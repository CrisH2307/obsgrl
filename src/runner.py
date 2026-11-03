"""Run experiments from the command line.

  python -m src.runner --condition obsgrl --case uber_2018 --model gpt-4o --runs 1
  python -m src.runner --all --model fake          # every condition x case, offline
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import config
from .conditions import RUNNERS
from .schema import RunRecord, StageLog

ROOT = Path(__file__).resolve().parent.parent


def run_one(condition: str, case: str, model: str, run: int) -> Path:
    out = ROOT / "runs" / condition / case / model / f"run_{run}.json"
    if out.exists() and json.loads(out.read_text()).get("ok"):
        print(f"skip  {out.relative_to(ROOT)} (already done)")
        return out  # failed runs are not skipped, so rerunning retries them

    rec = RunRecord(
        condition=condition, case=case, model=model, model_id=config.MODELS[model][1],
        run=run, temperature=config.TEMPERATURE, prompt_version=config.PROMPT_VERSION,
        started_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )
    case_text = (ROOT / "cases" / f"{case}.md").read_text()
    try:
        RUNNERS[condition](rec, case_text)
    except Exception as e:  # keep going; the failed run is saved and marked
        rec.ok = False
        rec.stages.append(StageLog(stage="error", prompt="", raw_response="", error=repr(e)))
        print(f"FAIL  {condition}/{case}/{model}/run_{run}: {e}", file=sys.stderr)

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec.to_dict(), indent=2, ensure_ascii=False))
    print(f"{'ok   ' if rec.ok else 'saved'} {out.relative_to(ROOT)}  ({len(rec.items)} items)")
    return out


def main() -> None:
    p = argparse.ArgumentParser(description="Run ObsGRL experiment conditions.")
    p.add_argument("--condition", choices=config.CONDITIONS)
    p.add_argument("--case", choices=config.CASES)
    p.add_argument("--model", choices=list(config.MODELS), required=True)
    p.add_argument("--runs", type=int, default=config.RUNS_PER_CELL)
    p.add_argument("--all", action="store_true", help="every condition x case for this model")
    a = p.parse_args()

    if a.all:
        cells = [(c, k) for c in config.CONDITIONS for k in config.CASES]
    elif a.condition and a.case:
        cells = [(a.condition, a.case)]
    else:
        p.error("give --condition and --case, or --all")

    if config.MODELS[a.model][0] != "fake":
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")

    for condition, case in cells:
        for run in range(1, a.runs + 1):
            run_one(condition, case, a.model, run)


if __name__ == "__main__":
    main()
