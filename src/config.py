"""All experiment settings in one place. Change here, not in code."""

# Short name -> (provider, model id). Both providers speak the OpenAI API.
MODELS = {
    "gpt-4o": ("openai", "gpt-4o-2024-08-06"),
    "llama-3.1-70b": ("openrouter", "meta-llama/llama-3.1-70b-instruct"),
    "fake": ("fake", "fake"),  # offline testing, no API key needed
}

CONDITIONS = ["b1", "b2", "obsgrl"]
CASES = ["uber_2018", "williston_2016", "mountainview_2018"]

TEMPERATURE = 0.7   # >0 so the 5 runs can differ (RQ3 measures that)
RUNS_PER_CELL = 5
MAX_RETRIES = 1     # retry once if the reply is not valid JSON / TGRL

PROMPT_VERSION = "v0-draft"  # bump to "v1" when you freeze prompts (task 11)
