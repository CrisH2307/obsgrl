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
cp .env.example .env        # then paste your keys
```

GPT-4o goes through OpenAI. Llama 3.1 70B goes through OpenRouter, which uses the same client.
Model names and settings live in `src/config.py`.

## Run

```bash
python -m src.runner --all --model fake --runs 2                      # offline test, no keys
python -m src.runner --condition obsgrl --case uber_2018 --model gpt-4o --runs 1   # pilot
python -m src.runner --all --model gpt-4o                             # 45 runs
python -m src.runner --all --model llama-3.1-70b                      # 45 runs
```

Output: `runs/<condition>/<case>/<model>/run_<n>.json`. Finished runs are skipped,
so you can stop and restart safely. Failed runs are saved with `"ok": false` and retried next time.

## Before the real runs

1. Replace the placeholder files in `cases/` with the real descriptions (tasks 3-5).
2. Check the obstacle types in `prompts/obsgrl/s2_obstacles.txt` against van Lamsweerde & Letier [2].
3. Pilot on one case, fix prompts, then set `PROMPT_VERSION = "v1"` in `src/config.py`
   and run `git tag prompts-v1`. Do not change prompts after that.

## Layout

```
cases/         input descriptions (one .md per case)
ground_truth/  frozen premise lists; the runner never reads this
prompts/       all prompt text; edit here, not in code
src/           config, llm client, conditions, TGRL check, runner
runs/          output JSON
analysis/      metrics script (next step)
```
# obsgrl
