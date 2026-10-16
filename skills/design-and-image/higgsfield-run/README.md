# higgsfield-run

Runs a prompt through the Higgsfield REST API and brings the file back into the
workspace. The execution half of the prompt system: `video-prompt` and
`image-prompt` write the text, this runs it, `prompt-scoring` records the verdict.

## Structure

```
higgsfield-run/
├── SKILL.md                  workflow, money rules, image-first pattern
├── README.md                 this file
├── references/
│   └── api-notes.md          verified API facts, with where each came from
└── scripts/
    ├── hf_run.py             the runner: doctor, models, upload, generate, status
    ├── models.json           model registry: endpoints, rates, parameter schemas
    └── test_hf_run.py        31 tests, no network and no charges
```

## Usage

```bash
HF=/home/workspace/Skills/higgsfield-run/scripts/hf_run.py

python3 $HF doctor                        # verify credentials, spends nothing
python3 $HF models                        # registry with rates
python3 $HF generate --video --prompt "..." --duration 5 --dry-run
python3 $HF generate --model soul --variants 4 --slug hero \
  --prompt-file Content/image-prompts/hero-2026-09-20.md
python3 $HF upload Media/higgsfield/hero-2026-09-20/hero-01.jpg
python3 $HF status <request_id> --download
```

## Credentials

`HIGGSFIELD_API_KEY` (single console key, id:secret; the older `HIGGSFIELD_API_KEY_ID` + `HIGGSFIELD_API_KEY_SECRET` pair still works) from
`console.higgsfield.ai`, set in **Zo Settings > Advanced**. Registered in
`System/secrets-manifest.json`. Never written into `/root/.zo_secrets`, which is
rebuilt from Settings at every sandbox boot; a test enforces that the script
only ever opens that file for reading.

## Spend ledger

`Content/prompt-results/higgsfield-spend.jsonl`, two rows per generation:

- `intent` written **before** the request leaves, because that is the moment it
  becomes billable
- `settled` written when it reaches a terminal state, carrying
  `refund_expected` for anything that did not complete

An intent with no settlement is the state worth being able to find: something
died mid-poll and a charge may exist that nothing else recorded.

## Tests

```bash
python3 Skills/higgsfield-run/scripts/test_hf_run.py
```

31 tests, no network and no credentials. They cover the cost guard, all four
terminal states, local timeout, variant isolation, the four output media shapes,
per-model parameter mapping, prompt-file extraction, credential precedence, and
registry integrity. Six were mutation-tested: reintroducing the defect each one
describes makes it fail.
