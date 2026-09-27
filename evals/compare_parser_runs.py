"""Compare frozen before/after scores; never refit or tune a model.

Example after saving both scores files (see docs/PROJECT-PARSER-FIX.md):
    python evals/compare_parser_runs.py before.parquet after.parquet
"""
import argparse
import json
from pathlib import Path

import calibration
import score

ROOT = Path(__file__).resolve().parents[1]


def compare(before, after, cohorts, published=None):
    """Use identical labels, capacity, scorer and row order for every saved score set."""
    paths = {"old_parser_same_environment": before, "corrected_parser": after}
    if published:
        paths = {"previous_saved_scores": published, **paths}
    frames = {name: calibration.load(cohorts, path) for name, path in paths.items()}
    result = {"runs": {name: calibration.compare_rankings(frame).reset_index().to_dict(orient="records")
                       for name, frame in frames.items()}}
    old = frames["old_parser_same_environment"]
    new = frames["corrected_parser"]
    assert old.donor_id.equals(new.donor_id)
    old_list = score._top_k_mask(old, old.expected_value.values, 0.1)
    new_list = score._top_k_mask(new, new.expected_value.values, 0.1)
    result["list_members_replaced_same_environment"] = int((old_list & ~new_list).sum())
    result["score_difference_same_environment"] = float(
        calibration.compare_rankings(new).loc["expected_value", "value_per_contact"]
        - calibration.compare_rankings(old).loc["expected_value", "value_per_contact"])
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("--cohorts", type=Path, default=ROOT / "data/processed/cohorts.parquet")
    parser.add_argument("--published", type=Path)
    parser.add_argument("--out", type=Path, default=ROOT / "evals/results/parser_fix_comparison.json")
    args = parser.parse_args()
    result = compare(args.before, args.after, args.cohorts, args.published)
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
