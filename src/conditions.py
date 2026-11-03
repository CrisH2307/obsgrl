"""The three conditions. Each takes a case text and fills a RunRecord."""
import json
from pathlib import Path

from . import llm, tgrl
from .schema import Item, RunRecord, StageLog

PROMPTS = Path(__file__).resolve().parent.parent / "prompts"


def _prompt(name: str, **fill: str) -> str:
    text = (PROMPTS / name).read_text()
    for key, value in fill.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def _call(rec: RunRecord, stage: str, prompt: str) -> dict:
    raw, parsed = llm.ask(rec.model, prompt, stage)
    rec.stages.append(StageLog(stage=stage, prompt=prompt, raw_response=raw, parsed=parsed))
    return parsed


def run_b1(rec: RunRecord, case: str) -> None:
    out = _call(rec, "b1", _prompt("b1_plain.txt", CASE=case))
    rec.items = [Item(id=f"r{i}", kind="requirement", text=r["text"])
                 for i, r in enumerate(out["requirements"], 1)]


def _extract(rec: RunRecord, case: str, file: str) -> list[dict]:
    out = _call(rec, "s1_extract", _prompt(file, CASE=case))
    rec.tgrl = out.get("tgrl", "")
    rec.tgrl_valid, problem = tgrl.check(rec.tgrl)
    if problem:
        rec.stages[-1].error = f"TGRL: {problem}"
    return out["goals"]


def run_b2(rec: RunRecord, case: str) -> None:
    goals = _extract(rec, case, "b2_extract.txt")
    rec.items = [Item(id=g["id"], kind="goal", text=f'{g["actor"]}: {g["text"]}') for g in goals]


def run_obsgrl(rec: RunRecord, case: str) -> None:
    goals = _extract(rec, case, "obsgrl/s1_extract.txt")
    obstacles = _call(rec, "s2_obstacles", _prompt(
        "obsgrl/s2_obstacles.txt", CASE=case, GOALS=json.dumps(goals, indent=2)))["obstacles"]
    reqs = _call(rec, "s3_resolve", _prompt(
        "obsgrl/s3_resolve.txt", CASE=case, OBSTACLES=json.dumps(obstacles, indent=2)))["requirements"]

    by_id = {o["id"]: o for o in obstacles}
    for i, r in enumerate(reqs, 1):
        o = by_id.get(r.get("obstacle_id"), {})
        context = f'Obstacle: {o.get("text", "?")} | Premise: {o.get("violated_premise", "?")}'
        rec.items.append(Item(id=f"r{i}", kind="requirement", text=r["text"], context=context))


RUNNERS = {"b1": run_b1, "b2": run_b2, "obsgrl": run_obsgrl}
