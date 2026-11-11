"""One small client for every model. Returns parsed JSON, retries once."""
import json
import os
import re

from . import config


def _client(provider: str):
    from openai import OpenAI  # imported here so "fake" works without the package
    if provider == "openrouter":
        return OpenAI(
            api_key=os.environ["OPENROUTER_API_KEY"],
            base_url="https://openrouter.ai/api/v1",
        )
    raise ValueError(f"unknown provider: {provider}")


def _extract_json(text: str):
    """Models sometimes wrap JSON in ```json fences or add a sentence. Strip that."""
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if fenced:
        text = fenced.group(1)
    start = min([i for i in (text.find("{"), text.find("[")) if i != -1], default=-1)
    if start == -1:
        raise ValueError("no JSON found in reply")
    obj, _ = json.JSONDecoder().raw_decode(text[start:])  # ignores text after the JSON
    return obj


def _request_args(model: str, model_id: str, prompt: str) -> dict:
    """Build the API call, sending only the options this model accepts."""
    args = {"model": model_id, "messages": [{"role": "user", "content": prompt}]}
    temperature = config.temperature_for(model)
    if temperature is not None:
        args["temperature"] = temperature
    if config.SUPPORTS[model]["json_mode"]:
        args["response_format"] = {"type": "json_object"}
    return args


def ask(model: str, prompt: str, stage: str) -> tuple[str, dict]:
    """Send one prompt. Returns (raw reply, parsed JSON). Raises if still bad after retry."""
    provider, model_id = config.MODELS[model]
    if provider == "fake":
        raw = _fake_reply(stage)
        return raw, _extract_json(raw)

    client = _client(provider)
    last_error = None
    for _ in range(config.MAX_RETRIES + 1):
        resp = client.chat.completions.create(**_request_args(model, model_id, prompt))
        raw = resp.choices[0].message.content or ""
        try:
            return raw, _extract_json(raw)
        except (ValueError, json.JSONDecodeError) as e:
            last_error = e
    raise ValueError(f"{stage}: reply was not valid JSON after retry ({last_error})")


def _fake_reply(stage: str) -> str:
    """Canned answers shaped like the real ones, for offline testing."""
    fakes = {
        "b1": {"requirements": [
            {"text": "The ADS shall detect pedestrians crossing outside crosswalks."},
            {"text": "The ADS shall alert the operator when braking is suppressed."}]},
        "s1_extract": {
            "tgrl": "grl Fake { actor ADS { goal DetectObjects; goal PlanSafePath; } "
                    "actor Pedestrian { goal CrossSafely; } }",
            "goals": [
                {"id": "g1", "actor": "ADS", "text": "Detect objects around the vehicle"},
                {"id": "g2", "actor": "ADS", "text": "Plan a safe path"},
                {"id": "g3", "actor": "Pedestrian", "text": "Cross the road safely"}]},
        "s2_obstacles": {"obstacles": [
            {"id": "o1", "goal_id": "g1", "guide_word": "omission",
             "text": "Object class changes and its track history is lost",
             "violated_premise": "A detected object keeps one identity over time"},
            {"id": "o2", "goal_id": "g3", "guide_word": "omission",
             "text": "Pedestrian crosses midblock, which the ADS does not expect",
             "violated_premise": "Pedestrians only cross at crosswalks"}]},
        "s3_resolve": {"requirements": [
            {"obstacle_id": "o1", "text": "The ADS shall keep an object's track history when its class changes."},
            {"obstacle_id": "o2", "text": "The ADS shall predict paths for pedestrians crossing outside crosswalks."}]},
    }
    return json.dumps(fakes[stage])
