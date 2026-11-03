"""Light TGRL check. Not a full parser: enough to catch broken output.

TGRL looks like:  grl Name { actor A { goal G; softGoal S; } }
"""
import re


def check(tgrl: str) -> tuple[bool, str]:
    text = tgrl.strip()
    if not re.match(r"^grl\s+\w+\s*\{", text):
        return False, "must start with: grl <Name> {"
    depth = 0
    for ch in text:
        depth += ch == "{"
        depth -= ch == "}"
        if depth < 0:
            return False, "a '}' closes nothing"
    if depth != 0:
        return False, "braces do not balance"
    if "actor" not in text:
        return False, "no actor found"
    return True, ""
