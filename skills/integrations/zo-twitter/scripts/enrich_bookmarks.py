#!/usr/bin/env python3
"""
Enrich all X bookmark JSONs with full API v2 data (expanded URLs, media, metrics, articles).
This script:
1. Exports all bookmarks using bird CLI
2. Enriches each bookmark file with X API v2 data (metrics, media, expanded URLs)
3. Fetches full article text for X native articles
"""

import json, os, time, sys
from requests_oauthlib import OAuth1
import requests
import subprocess

BASE = "/home/workspace/Research/x_bookmarks"
API_KEY = os.environ.get("x_api_key")
API_SECRET = os.environ.get("x_api_secret")
ACCESS_TOKEN = os.environ.get("x_access_token")
ACCESS_SECRET = os.environ.get("x_access_token_secret")

if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET]):
    print("ERROR: Missing X API credentials in environment variables")
    sys.exit(1)

auth = OAuth1(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)

# Folder config
folders = {
    "read_later": "1892933668843307008",
    "crypto": "1890095095906619393",
    "dark_conspiracy": "1890095119235092481",
    "fascism": "1890095139640983552",
    "for_bbn_intel": "1890095158909644800",
    "for_sam": "1890095180250947584",
    "futurism": "1890095198110666752",
    "israel": "1890095220474867712",
    "politics": "1890095244650213376",
    "prediction_markets": "1890095282273562624",
    "products_to_use": "1890095301462044672",
    "aliens": "1861568583991541800",
}

def export_bookmarks():
    """Export all bookmarks using bird CLI"""
    print("📥 Exporting bookmarks with bird CLI...", flush=True)
    
    for folder_name, folder_id in folders.items():
        print(f"  Exporting {folder_name}...", flush=True)
        folder_path = f"{BASE}/{folder_name}"
        os.makedirs(folder_path, exist_ok=True)
        
        cmd = f"bird bookmarks --folder-id {folder_id} --all --json > {folder_path}/bookmarks.json"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"  ⚠️  Warning: {folder_name} export failed: {result.stderr}", flush=True)
        else:
            # Count bookmarks
            try:
                with open(f"{folder_path}/bookmarks.json") as f:
                    data = json.load(f)
                    print(f"  ✓ {folder_name}: {len(data)} bookmarks", flush=True)
            except:
                print(f"  ⚠️  Warning: Could not read {folder_name}/bookmarks.json", flush=True)
    
    # Also export all bookmarks to main file
    print(f"  Exporting all bookmarks to bookmarks_all.json...", flush=True)
    cmd = f"bird bookmarks --all --json > {BASE}/bookmarks_all.json"
    subprocess.run(cmd, shell=True, capture_output=True, text=True)

def enrich_with_api():
    """Enrich bookmarks with X API v2 data"""
    print("\n🔧 Enriching with X API v2 data...", flush=True)
    
    all_files = [f"{BASE}/bookmarks_all.json"] + [f"{BASE}/{f}/bookmarks.json" for f in folders.keys()]
    
    for path in all_files:
        if not os.path.exists(path):
            continue
            
        with open(path) as f:
            data = json.load(f)
        
        if not data:
            continue
        
        ids = [t["id"] for t in data if "id" in t]
        if not ids:
            continue
        
        # Batch API calls (100 tweets per call)
        enriched = {}
        for i in range(0, len(ids), 100):
            batch = ids[i:i+100]
            params = {
                "ids": ",".join(batch),
                "tweet.fields": "created_at,public_metrics,entities,referenced_tweets,note_tweet",
                "expansions": "attachments.media_keys,referenced_tweets.id,referenced_tweets.id.author_id",
                "media.fields": "url,preview_image_url,type,variants,alt_text"
            }
            
            r = requests.get("https://api.x.com/2/tweets", params=params, auth=auth)
            
            if r.status_code != 200:
                print(f"  ⚠️  API error: {r.status_code}", flush=True)
                continue
            
            result = r.json()
            
            # Build enrichment map
            media_map = {}
            if "includes" in result and "media" in result["includes"]:
                for m in result["includes"]["media"]:
                    media_map[m["media_key"]] = m
            
            for tweet in result.get("data", []):
                tid = tweet["id"]
                metrics = tweet.get("public_metrics", {})
                entities = tweet.get("entities", {})
                
                # Extract media
                media_list = []
                if "attachments" in tweet and "media_keys" in tweet["attachments"]:
                    for key in tweet["attachments"]["media_keys"]:
                        if key in media_map:
                            m = media_map[key]
                            media_obj = {"type": m["type"]}
                            
                            if m["type"] == "photo":
                                media_obj["url"] = m.get("url")
                            elif m["type"] in ["video", "animated_gif"]:
                                media_obj["preview_url"] = m.get("preview_image_url")
                                variants = m.get("variants", [])
                                mp4_variants = [v for v in variants if v.get("content_type") == "video/mp4"]
                                if mp4_variants:
                                    best = max(mp4_variants, key=lambda v: v.get("bit_rate", 0))
                                    media_obj["video_url"] = best.get("url")
                            
                            media_list.append(media_obj)
                
                # Extract links
                links = []
                for url_obj in entities.get("urls", []):
                    link = {
                        "url": url_obj.get("expanded_url") or url_obj.get("url"),
                        "title": url_obj.get("title"),
                        "description": url_obj.get("description")
                    }
                    links.append(link)
                
                # Handle quoted tweets
                quoted = None
                if tweet.get("referenced_tweets"):
                    for ref in tweet["referenced_tweets"]:
                        if ref["type"] == "quoted":
                            quoted = {"id": ref["id"]}
                
                enriched[tid] = {
                    "metrics": {
                        "likes": metrics.get("like_count", 0),
                        "retweets": metrics.get("retweet_count", 0),
                        "replies": metrics.get("reply_count", 0),
                        "bookmarks": metrics.get("bookmark_count", 0),
                        "impressions": metrics.get("impression_count", 0)
                    },
                    "media": media_list if media_list else None,
                    "links": links if links else None,
                    "quoted_tweet": quoted
                }
                
                # Add note_tweet text if present
                if "note_tweet" in tweet:
                    enriched[tid]["note_text"] = tweet["note_tweet"].get("text")
        
        # Apply enrichment to original data
        updated = 0
        for t in data:
            if t["id"] in enriched:
                t.update(enriched[t["id"]])
                updated += 1
        
        # Save
        with open(path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        rel = os.path.relpath(path, BASE)
        print(f"  ✓ {rel}: enriched {updated} tweets", flush=True)
    
    print(f"  API calls complete!", flush=True)

def fetch_articles():
    """Fetch X native article text"""
    print("\n📰 Fetching X native articles...", flush=True)
    
    all_files = [f"{BASE}/bookmarks_all.json"] + [f"{BASE}/{f}/bookmarks.json" for f in folders.keys()]
    
    for path in all_files:
        if not os.path.exists(path):
            continue
        
        with open(path) as f:
            data = json.load(f)
        
        # Find articles
        article_ids = []
        for t in data:
            if t.get("links"):
                for link in t["links"]:
                    if "/i/article/" in link.get("url", "") and not link.get("article_text"):
                        article_ids.append((t["id"], link["url"]))
        
        if not article_ids:
            continue
        
        # Fetch with bird
        updated = 0
        for tid, url in article_ids:
            article_id = url.split("/i/article/")[-1]
            result = subprocess.run(f"bird read {article_id}", shell=True, capture_output=True, text=True)
            
            if result.returncode == 0 and len(result.stdout.strip()) > 100:
                # Find tweet and add article text
                for t in data:
                    if t["id"] == tid:
                        for link in t.get("links", []):
                            if link["url"] == url:
                                link["article_text"] = result.stdout.strip()
                                updated += 1
        
        if updated > 0:
            with open(path, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            rel = os.path.relpath(path, BASE)
            print(f"  ✓ {rel}: {updated} articles", flush=True)

def main():
    print("=" * 60)
    print("X BOOKMARKS ENRICHMENT")
    print("=" * 60)
    
    export_bookmarks()
    enrich_with_api()
    fetch_articles()
    
    print("\n✅ All bookmarks enriched and updated!")
    print("=" * 60)

if __name__ == "__main__":
    main()
