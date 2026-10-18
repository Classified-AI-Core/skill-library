#!/usr/bin/env python3
"""Tests for hf_run.py. No network, no credentials, no charges.

The HTTP layer is stubbed rather than mocked over a socket: the branches worth
pinning are terminal-state handling, the cost guard, the spend ledger, and the
output-shape parsing, none of which are about sockets.

Run: python3 Skills/higgsfield-run/scripts/test_hf_run.py
"""

import argparse
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hf_run  # noqa: E402


def fake_download(url, dest):
    with open(dest, "wb") as fh:
        fh.write(b"x" * 10)
    return 10


def gen_args(**over):
    base = dict(prompt="a test prompt", prompt_file=None, model=None, video=True,
                slug="t", variants=1, duration=None, aspect=None, resolution=None,
                start_frame=None, param=None, max_cost=hf_run.DEFAULT_MAX_COST,
                timeout=30, dry_run=False)
    base.update(over)
    return argparse.Namespace(**base)


class Sandbox(unittest.TestCase):
    """Redirect every write off the real workspace before any test runs."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.media = os.path.join(self.tmp.name, "media")
        self.ledger = os.path.join(self.tmp.name, "spend.jsonl")
        self.p1 = mock.patch.object(hf_run, "MEDIA_ROOT", self.media)
        self.p2 = mock.patch.object(hf_run, "LEDGER_PATH", self.ledger)
        self.p3 = mock.patch.object(hf_run, "credentials", lambda: ("kid", "ksec"))
        for p in (self.p1, self.p2, self.p3):
            p.start()
        self.addCleanup(self.tmp.cleanup)
        for p in (self.p1, self.p2, self.p3):
            self.addCleanup(p.stop)

    def ledger_rows(self):
        if not os.path.exists(self.ledger):
            return []
        with open(self.ledger, encoding="utf-8") as fh:
            return [json.loads(line) for line in fh if line.strip()]

    def run_generate(self, statuses, args=None, submit=None, sleepless=True):
        """Drive cmd_generate with a scripted sequence of status bodies."""
        submit = submit if submit is not None else (
            200, {"status": "queued", "request_id": "r1",
                  "status_url": "https://api.higgsfield.ai/requests/r1/status"})
        seq = list(statuses)

        def fake_request(url, headers, method="GET", payload=None, timeout=60):
            if method == "POST":
                return submit
            return seq.pop(0) if seq else (200, {"status": "in_progress"})

        with mock.patch.object(hf_run, "request_json", side_effect=fake_request), \
             mock.patch.object(hf_run, "download", side_effect=fake_download), \
             mock.patch.object(hf_run, "time") as t:
            t.monotonic.side_effect = ([0] * 400 if sleepless
                                       else [0, 1, 2, 3] + [10_000] * 400)
            t.sleep.return_value = None
            return hf_run.cmd_generate(args or gen_args())


class TestCostGuard(Sandbox):
    def test_refuses_above_cap(self):
        args = gen_args(duration=10, variants=4, dry_run=True)
        with self.assertRaises(SystemExit) as cm:
            hf_run.cmd_generate(args)
        self.assertIn("REFUSED", str(cm.exception))

    def test_variants_multiply_the_estimate(self):
        reg = hf_run.load_registry()
        spec = reg["models"]["kling3-turbo-t2v"]
        one = hf_run.estimate_cost(spec, 5, 1)
        four = hf_run.estimate_cost(spec, 5, 4)
        self.assertAlmostEqual(four, one * 4, places=6)
        self.assertAlmostEqual(one, 0.56, places=4)

    def test_image_rate_ignores_duration(self):
        spec = hf_run.load_registry()["models"]["soul"]
        self.assertEqual(hf_run.estimate_cost(spec, 30, 1),
                         hf_run.estimate_cost(spec, 5, 1))

    def test_dry_run_sends_nothing_and_writes_no_ledger(self):
        with mock.patch.object(hf_run, "request_json") as rq:
            rc = hf_run.cmd_generate(gen_args(dry_run=True))
        self.assertEqual(rc, 0)
        rq.assert_not_called()
        self.assertEqual(self.ledger_rows(), [])


class TestTerminalStates(Sandbox):
    def test_completed_downloads_and_settles(self):
        rc = self.run_generate([(200, {"status": "in_progress"}),
                                (200, {"status": "completed",
                                       "video": {"url": "https://cdn/x.mp4"}})])
        self.assertEqual(rc, 0)
        rows = self.ledger_rows()
        self.assertEqual([r["kind"] for r in rows], ["intent", "settled"])
        self.assertEqual(rows[1]["status"], "completed")
        self.assertFalse(rows[1]["refund_expected"])

    def test_failed_marks_refund_expected(self):
        rc = self.run_generate([(200, {"status": "failed", "error": "content policy"})])
        self.assertEqual(rc, 1)
        settled = self.ledger_rows()[-1]
        self.assertEqual(settled["status"], "failed")
        self.assertTrue(settled["refund_expected"])

    def test_nsfw_is_terminal_not_a_poll_forever(self):
        rc = self.run_generate([(200, {"status": "nsfw"})])
        self.assertEqual(rc, 1)
        self.assertEqual(self.ledger_rows()[-1]["status"], "nsfw")

    def test_completed_with_no_media_is_a_failure_not_a_success(self):
        rc = self.run_generate([(200, {"status": "completed"})])
        self.assertEqual(rc, 1)

    def test_submit_rejection_writes_no_intent(self):
        """A request the API refused was never billable, so no intent row."""
        rc = self.run_generate([], submit=(404, {"detail": "Model not found"}))
        self.assertEqual(rc, 1)
        kinds = [r["kind"] for r in self.ledger_rows()]
        self.assertEqual(kinds, ["submit_rejected"])
        self.assertNotIn("intent", kinds)

    def test_local_timeout_still_settles_the_intent(self):
        """The charge is real even when we stop waiting, so it must be recorded."""
        rc = self.run_generate([(200, {"status": "in_progress"})] * 3, sleepless=False)
        self.assertEqual(rc, 1)
        rows = self.ledger_rows()
        self.assertEqual([r["kind"] for r in rows], ["intent", "settled"])
        self.assertEqual(rows[1]["status"], "failed")
        self.assertIn("timeout", rows[1]["error"])

    def test_401_while_polling_stops_immediately(self):
        rc = self.run_generate([(401, {"detail": "Invalid credentials"})])
        self.assertEqual(rc, 1)
        self.assertIn("401", self.ledger_rows()[-1]["error"])


class TestVariants(Sandbox):
    def test_each_variant_gets_its_own_intent_and_settlement(self):
        rc = self.run_generate(
            [(200, {"status": "completed", "video": {"url": "https://cdn/a.mp4"}})] * 3,
            args=gen_args(variants=3))
        self.assertEqual(rc, 0)
        rows = self.ledger_rows()
        self.assertEqual(len([r for r in rows if r["kind"] == "intent"]), 3)
        self.assertEqual(len([r for r in rows if r["kind"] == "settled"]), 3)
        self.assertEqual({r["variant"] for r in rows if r["kind"] == "intent"}, {1, 2, 3})
        self.assertEqual(len({r["batch"] for r in rows}), 1)

    def test_one_bad_variant_does_not_abort_the_others(self):
        rc = self.run_generate(
            [(200, {"status": "failed", "error": "boom"}),
             (200, {"status": "completed", "video": {"url": "https://cdn/b.mp4"}})],
            args=gen_args(variants=2))
        self.assertEqual(rc, 0)
        settled = [r for r in self.ledger_rows() if r["kind"] == "settled"]
        self.assertEqual([r["status"] for r in settled], ["failed", "completed"])


class TestOutputShapes(unittest.TestCase):
    """The response schema carries four media shapes; all four must be read."""

    def test_images_array(self):
        self.assertEqual(hf_run.media_urls({"images": [{"url": "a"}, {"url": "b"}]}), ["a", "b"])

    def test_singular_video_object(self):
        self.assertEqual(hf_run.media_urls({"video": {"url": "v"}}), ["v"])

    def test_audio_singular_and_plural(self):
        self.assertEqual(hf_run.media_urls({"audio": {"url": "a"}, "audios": [{"url": "b"}]}),
                         ["a", "b"])

    def test_empty_and_malformed_are_not_urls(self):
        self.assertEqual(hf_run.media_urls({}), [])
        self.assertEqual(hf_run.media_urls({"video": None, "images": [{}, {"url": ""}]}), [])


class TestPayloadShaping(Sandbox):
    def test_params_outside_the_model_schema_are_dropped(self):
        """soul declares only `prompt`. An aspect meant for a video model
        must not ride along into an image request."""
        captured = {}

        def fake_request(url, headers, method="GET", payload=None, timeout=60):
            if method == "POST":
                captured.update(payload)
                return 200, {"status": "queued", "request_id": "r1",
                             "status_url": "https://api.higgsfield.ai/requests/r1/status"}
            return 200, {"status": "completed", "images": [{"url": "https://cdn/i.jpg"}]}

        with mock.patch.object(hf_run, "request_json", side_effect=fake_request), \
             mock.patch.object(hf_run, "download", side_effect=fake_download), \
             mock.patch.object(hf_run, "time") as t:
            t.monotonic.return_value = 0
            t.sleep.return_value = None
            hf_run.cmd_generate(gen_args(model="soul", video=False, aspect="16:9",
                                         resolution="4k"))
        self.assertEqual(set(captured), {"prompt"})

    def test_start_frame_maps_to_each_model_own_param_name(self):
        """kling calls it image_url, wan calls it file_url."""
        for model, key in (("kling3-turbo-i2v", "image_url"), ("wan3-ref2v", "file_url")):
            captured = {}

            def fake_request(url, headers, method="GET", payload=None, timeout=60):
                if method == "POST":
                    captured.update(payload)
                    return 200, {"status": "queued", "request_id": "r1",
                                 "status_url": "https://api.higgsfield.ai/requests/r1/status"}
                return 200, {"status": "completed", "video": {"url": "https://cdn/v.mp4"}}

            with mock.patch.object(hf_run, "request_json", side_effect=fake_request), \
                 mock.patch.object(hf_run, "download", side_effect=fake_download), \
                 mock.patch.object(hf_run, "time") as t:
                t.monotonic.return_value = 0
                t.sleep.return_value = None
                hf_run.cmd_generate(gen_args(model=model, video=False,
                                             start_frame="https://cdn/in.jpg"))
            self.assertEqual(captured.get(key), "https://cdn/in.jpg", model)

    def test_start_frame_on_a_text_only_model_is_refused(self):
        with self.assertRaises(SystemExit) as cm:
            hf_run.cmd_generate(gen_args(model="kling3-turbo-t2v",
                                         start_frame="https://cdn/in.jpg", dry_run=True))
        self.assertIn("no start frame", str(cm.exception))


class TestPromptFile(unittest.TestCase):
    def test_longest_fenced_block_wins(self):
        """Saved prompt files carry a header and the prompt in a fence. A short
        example fence must not beat the real prompt."""
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
            fh.write("# Header\n\nnotes\n\n```\nshort\n```\n\n"
                     "```text\nMAIN SUBJECT\nthe real and much longer prompt body\n```\n")
            path = fh.name
        try:
            got = hf_run.read_prompt(argparse.Namespace(prompt_file=path, prompt=None))
            self.assertIn("MAIN SUBJECT", got)
            self.assertNotIn("# Header", got)
        finally:
            os.unlink(path)

    def test_plain_file_with_no_fence_is_used_whole(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
            fh.write("just a bare prompt\n")
            path = fh.name
        try:
            self.assertEqual(hf_run.read_prompt(
                argparse.Namespace(prompt_file=path, prompt=None)), "just a bare prompt")
        finally:
            os.unlink(path)


class TestCredentials(unittest.TestCase):
    def test_env_wins_over_the_secrets_file(self):
        with mock.patch.dict(os.environ, {"HIGGSFIELD_API_KEY_ID": "envid",
                                          "HIGGSFIELD_API_KEY_SECRET": "envsec"}), \
             mock.patch.dict(os.environ, {"HIGGSFIELD_API_KEY": ""}), \
             mock.patch.object(hf_run, "read_secrets_file",
                               return_value={"HIGGSFIELD_API_KEY_ID": "fileid",
                                             "HIGGSFIELD_API_KEY_SECRET": "filesec"}):
            self.assertEqual(hf_run.credentials(), ("envid", "envsec"))

    def test_single_console_key_is_split_on_first_colon(self):
        with mock.patch.dict(os.environ, {"HIGGSFIELD_API_KEY": "myid:my:sec"}):
            self.assertEqual(hf_run.credentials(), ("myid", "my:sec"))

    def test_falls_back_to_the_secrets_file(self):
        with mock.patch.dict(os.environ, {}, clear=True), \
             mock.patch.object(hf_run, "read_secrets_file",
                               return_value={"HIGGSFIELD_API_KEY_ID": "fid",
                                             "HIGGSFIELD_API_KEY_SECRET": "fsec"}):
            self.assertEqual(hf_run.credentials(), ("fid", "fsec"))

    def test_missing_credentials_name_the_fix(self):
        with mock.patch.dict(os.environ, {}, clear=True), \
             mock.patch.object(hf_run, "read_secrets_file", return_value={}):
            with self.assertRaises(SystemExit) as cm:
                hf_run.credentials()
        msg = str(cm.exception)
        self.assertIn("Settings > Advanced", msg)
        self.assertIn("HIGGSFIELD_API_KEY_ID", msg)

    def test_the_script_never_writes_the_secrets_file(self):
        """Guard on the standing rule. Reading is fine, writing is never fine."""
        with open(hf_run.__file__, encoding="utf-8") as fh:
            src = fh.read()
        for line in src.splitlines():
            if ".zo_secrets" in line or "SECRETS_FILE" in line:
                self.assertNotIn('"w"', line)
                self.assertNotIn('"a"', line)
        self.assertIn('open(SECRETS_FILE, encoding="utf-8")', src)


class TestRegistry(unittest.TestCase):
    def test_every_entry_is_complete_and_points_at_the_real_host(self):
        reg = hf_run.load_registry()
        for name, spec in reg["models"].items():
            for field in ("kind", "endpoint", "rate_usd", "rate_unit", "params", "verified"):
                self.assertIn(field, spec, f"{name} missing {field}")
            self.assertTrue(spec["endpoint"].startswith("https://api.higgsfield.ai/"), name)
            self.assertIn(spec["kind"], ("image", "video"))
            self.assertIn(spec["rate_unit"], ("per_image", "per_second"))
            self.assertIn("prompt", spec["params"], name)

    def test_defaults_resolve(self):
        reg = hf_run.load_registry()
        self.assertIn(reg["default_image"], reg["models"])
        self.assertIn(reg["default_video"], reg["models"])
        self.assertEqual(reg["models"][reg["default_video"]]["kind"], "video")
        self.assertEqual(reg["models"][reg["default_image"]]["kind"], "image")

    def test_declared_defaults_are_inside_declared_params(self):
        """A default the model does not accept would be silently dropped at
        submit time, which is a config error wearing a working disguise."""
        for name, spec in hf_run.load_registry()["models"].items():
            for k in (spec.get("defaults") or {}):
                self.assertIn(k, spec["params"], f"{name}: default '{k}' not in params")

    def test_start_frame_param_is_a_declared_param(self):
        for name, spec in hf_run.load_registry()["models"].items():
            sf = spec.get("start_frame_param")
            if sf:
                self.assertIn(sf, spec["params"], name)


class TestRedaction(unittest.TestCase):
    def test_the_secret_never_survives_into_an_error_string(self):
        self.assertNotIn("ksec", hf_run.redact("failed for key ksec here", "kid", "ksec"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
