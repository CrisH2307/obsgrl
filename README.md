# ObsGRL experiment runner

Runs the three conditions from our proposal on the NTSB cases and saves every LLM call as JSON.

| Condition | What it does | Items the raters score |
| --- | --- | --- |
| `b1` | One prompt: "list missing requirements" | requirements |
| `b2` | Stage 1 only: build a GRL model | goals |
| `obsgrl` | Stage 1 goals, stage 2 obstacles, stage 3 new requirements | requirements, each with its obstacle and premise |

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then add OPENROUTER_API_KEY
```

Both models (`gpt-6-luna`, `gpt-oss-120b`) go through OpenRouter with the same client.
GPT-6 Luna takes no temperature setting, so its runs record `temperature: null`.
Model names and per-model options live in `src/config.py`.

## Run

```bash
python -m src.runner --all --model fake --runs 2                      # offline test, no key
python -m src.runner --condition obsgrl --case uber_2018 --model gpt-oss-120b --runs 1   # pilot
python -m src.runner --all --model gpt-oss-120b                       # 45 runs
python -m src.runner --all --model gpt-6-luna                         # 45 runs
python analysis/metrics.py                                            # TGRL validity, run stability
```

Output: `runs/<condition>/<case>/<model>/run_<n>.json`. Finished runs are skipped,
so you can stop and restart safely. Failed runs are saved with `"ok": false` and retried next time.

## Status

Prompts are frozen (`PROMPT_VERSION = "v1"`, git tag `prompts-v1`). Every condition returns at most 10 items.
All 90 runs are done and archived in `runs/`. Do not change prompts or cases after this point.
Still open: ground truth (`ground_truth/`), blind rating sheet, recall, kappa and the Wilcoxon test.
