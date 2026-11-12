"""Run-level metrics that need no human ratings: TGRL validity and run stability.

Usage: python analysis/metrics.py
Reads runs/<condition>/<case>/<model>/run_<n>.json, prints a table, writes analysis/run_metrics.csv.

Stability = mean pairwise Jaccard between the 5 runs of one cell (condition, case, model).
Items are free text, so two items count as the same when their word overlap
(token Jaccard) is at least MATCH_THRESHOLD. Each item can match only once.
This is a rough, automatic proxy. Report it with the threshold, and check a sample by hand.
"""
import csv, glob, itertools, json, re, statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MATCH_THRESHOLD = 0.35
STOP = {"the", "a", "an", "of", "to", "and", "or", "in", "on", "for", "shall", "system", "be", "is", "that", "with", "by", "as", "when", "are"}


def tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]+", text.lower()) if w not in STOP and len(w) > 2}


def sim(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if a | b else 0.0


def run_jaccard(a: list[str], b: list[str]) -> float:
    """Greedy one-to-one matching of items, then Jaccard on the matched count."""
    ta, tb = [tokens(x) for x in a], [tokens(x) for x in b]
    pairs = sorted(((sim(x, y), i, j) for i, x in enumerate(ta) for j, y in enumerate(tb)), reverse=True)
    used_a, used_b, matched = set(), set(), 0
    for s, i, j in pairs:
        if s < MATCH_THRESHOLD:
            break
        if i in used_a or j in used_b:
            continue
        used_a.add(i); used_b.add(j); matched += 1
    union = len(a) + len(b) - matched
    return matched / union if union else 0.0


def load():
    cells = defaultdict(list)
    for f in sorted(glob.glob(str(ROOT / "runs/*/*/*/run_*.json"))):
        d = json.load(open(f))
        cells[(d["condition"], d["case"], d["model"])].append(d)
    return cells


def main():
    rows = []
    for (cond, case, model), runs in sorted(load().items()):
        texts = [[i["text"] for i in r["items"]] for r in runs]
        jac = [run_jaccard(a, b) for a, b in itertools.combinations(texts, 2)]
        checked = [r["tgrl_valid"] for r in runs if r["tgrl_valid"] is not None]
        rows.append({
            "condition": cond, "case": case, "model": model, "runs": len(runs),
            "ok_rate": sum(r["ok"] for r in runs) / len(runs),
            "tgrl_valid_rate": (sum(checked) / len(checked)) if checked else "",
            "mean_items": statistics.mean(len(t) for t in texts),
            "jaccard_mean": statistics.mean(jac) if jac else "",
        })
    out = ROOT / "analysis/run_metrics.csv"
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

    print(f"{'cond':7}{'case':20}{'model':14}{'valid':>7}{'items':>7}{'jaccard':>9}")
    for r in rows:
        v = f"{r['tgrl_valid_rate']:.2f}" if r["tgrl_valid_rate"] != "" else "-"
        print(f"{r['condition']:7}{r['case']:20}{r['model']:14}{v:>7}{r['mean_items']:>7.1f}{r['jaccard_mean']:>9.2f}")
    print("\nMean Jaccard by condition and model")
    agg = defaultdict(list)
    for r in rows:
        agg[(r["condition"], r["model"])].append(r["jaccard_mean"])
    for k, v in sorted(agg.items()):
        print(f"  {k[0]:7}{k[1]:14}{statistics.mean(v):.2f}")
    print(f"\nwritten: {out}  (match threshold {MATCH_THRESHOLD})")


if __name__ == "__main__":
    main()
