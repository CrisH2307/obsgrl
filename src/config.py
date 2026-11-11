"""All experiment settings in one place. Change here, not in code."""

# Short name -> (provider, model id). Everything goes through OpenRouter (one API key).
MODELS = {
    "gpt-6-luna": ("openrouter", "openai/gpt-6-luna"),
    "gpt-4o": ("openrouter", "openai/gpt-4o-2024-08-06"),
    "gpt-oss-120b": ("openrouter", "openai/gpt-oss-120b"),  # open-weight model
    "llama-3.1-70b": ("openrouter", "meta-llama/llama-3.1-70b-instruct"),
    "fake": ("fake", "fake"),  # offline testing, no API key needed
}

# What each model accepts on OpenRouter (checked Nov 11, 2026).
# GPT-6 Luna is a reasoning model: it ignores temperature.
# Llama 3.1 70B has no JSON mode, so we ask for JSON in the prompt and parse it.
SUPPORTS = {
    "gpt-6-luna": {"temperature": False, "json_mode": True},
    "gpt-4o": {"temperature": True, "json_mode": True},
    "gpt-oss-120b": {"temperature": True, "json_mode": True},
    "llama-3.1-70b": {"temperature": True, "json_mode": False},
    "fake": {"temperature": True, "json_mode": True},
}

CONDITIONS = ["b1", "b2", "obsgrl"]
CASES = ["uber_2018", "williston_2016", "mountainview_2018"]

TEMPERATURE = 0.7   # >0 so the 5 runs can differ (RQ3); only sent where supported
RUNS_PER_CELL = 5
MAX_RETRIES = 1     # retry once if the reply is not valid JSON

PROMPT_VERSION = "v1"  # bump to "v1" when you freeze prompts (task 11)


def temperature_for(model: str) -> float | None:
    """The temperature actually sent, or None if the model does not take one."""
    return TEMPERATURE if SUPPORTS[model]["temperature"] else None
