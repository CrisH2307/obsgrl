"""Data shapes shared by the runner, the rating sheet and the metrics script."""
from dataclasses import dataclass, field, asdict


@dataclass
class Item:
    """One thing a condition proposes. This is what raters see and score."""
    id: str            # e.g. "r3"
    kind: str          # "requirement" | "goal"
    text: str          # the proposal itself
    context: str = ""  # ObsGRL only: the obstacle and premise behind it


@dataclass
class StageLog:
    """One LLM call. Kept so every run can be audited and reproduced."""
    stage: str
    prompt: str
    raw_response: str
    parsed: dict | list | None = None
    error: str = ""


@dataclass
class RunRecord:
    condition: str
    case: str
    model: str
    model_id: str
    run: int
    temperature: float | None   # None = model does not accept one (e.g. GPT-6 Luna)
    prompt_version: str
    started_at: str
    items: list[Item] = field(default_factory=list)
    stages: list[StageLog] = field(default_factory=list)
    tgrl: str = ""          # B2 and ObsGRL only
    tgrl_valid: bool | None = None
    ok: bool = True

    def to_dict(self) -> dict:
        return asdict(self)