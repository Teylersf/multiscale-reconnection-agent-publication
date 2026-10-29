"""Independently verify v1.2 paired resampling from compact records only.

No raw histories, downloads, source-function rerun, or prior-result rewrites.
Resample multiplicities and separate full/FP arithmetic intentionally differ
from the primary implementation's indexed difference calculation.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import csv
import hashlib
import json
import math
import re
import numpy as np

if not __debug__:
    raise RuntimeError("Python -O is forbidden: verification assertions must remain enabled.")

ROOT = Path(__file__).resolve().parents[1]
METHODS = ("left", "symmetric", "right")
BATCHES = ("inter_energy", "high_energy")
TOL = 1e-12


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "results/full-source-bootstrap-independent-v1.2.0.json")
    args = parser.parse_args()
    boot_path = ROOT / "results/paired-history-bootstrap-v1.2.0.json"
    full_path = ROOT / "results/full-source-validation-v1.2.0.json"
    boot = json.loads(boot_path.read_text())
    full = json.loads(full_path.read_text())
    assert boot["status"] == full["status"] == "pass"
    assert boot["script"] == full["script"]
    assert sha(ROOT / boot["script"]["path"]) == boot["script"]["sha256"]
    for item in boot["inputs"] + full["inputs"]:
        assert sha(ROOT / item["path"]) == item["sha256"]
    for key in ["replicate_output", "range_table_output"]:
        item = boot[key]
        assert sha(ROOT / "results" / item["filename"]) == item["sha256"]
    with np.load(ROOT / "results/public-batch-per-particle.npz", allow_pickle=False) as source:
        keys = [key.split("__", 1)[1] for key in source.files if key.startswith(BATCHES[0] + "__")]
        data = {key: np.concatenate([source[batch + "__" + key] for batch in BATCHES]) for key in keys}
    assert len(data["tag"]) == len(np.unique(data["tag"])) == 1003
    assert np.array_equal(data["total_net_gain"], data["final_gamma"].astype(float) - data["initial_gamma"].astype(float))
    count, seed = boot["replicates"], boot["seed"]
    assert count == 20000 and seed == 20261029 and boot["bit_generator"] == "PCG64"
    assert boot["quantile_method"] == "NumPy linear"
    ranges = {}
    with (ROOT / "results" / boot["range_table_output"]["filename"]).open(newline="") as f:
        for row in csv.DictReader(f):
            key = (row["band"], row["method"], row["estimand"])
            assert key not in ranges
            ranges[key] = row
    results = {}
    max_replicate_error = 0.0
    max_summary_error = 0.0
    with np.load(ROOT / "results" / boot["replicate_output"]["filename"], allow_pickle=False) as stored:
        for index, (band, mask) in enumerate([
            ("intermediate", (data["final_gamma"] > 5.77) & (data["final_gamma"] < 16.40)),
            ("high", data["final_gamma"] > 16.40),
        ]):
            n = int(np.sum(mask))
            assert n == {"intermediate": 667, "high": 84}[band]
            assert np.array_equal(stored[band + "__selected_tags"], data["tag"][mask])
            a = data["total_net_gain"][mask]
            assert np.isfinite(a).all() and (a > 0).all()
            fp = data["first_passage"][mask, 1]
            complete = np.column_stack([data[method][mask, 3] for method in METHODS])
            fp_fraction = fp / a
            complete_fraction = complete / a[:, None]
            mean = np.empty((count, 3))
            share = np.empty_like(mean)
            rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence(seed, spawn_key=(index,))))
            # One multinomial multiplicity vector represents the same selected
            # history IDs for all methods and both estimator numerator/denominator
            # pairs. These are bootstrap counts, not physical sampling weights.
            for k in range(count):
                ids = rng.integers(0, n, size=n, dtype=np.int64)
                weights = np.bincount(ids, minlength=n)
                mean[k] = (weights @ complete_fraction - weights @ fp_fraction) / n
                share[k] = (weights @ complete - weights @ fp) / (weights @ a)
            expected = {"mean_particle_fraction_change": mean, "total_net_gain_share_change": share}
            stored_names = {"mean_particle_fraction_change": "mean_fraction_change",
                            "total_net_gain_share_change": "total_net_gain_share_change"}
            report = {}
            for estimand, values in expected.items():
                published_values = stored[band + "__" + stored_names[estimand]]
                assert values.shape == published_values.shape == (count, 3)
                error = float(np.max(np.abs(values - published_values)))
                max_replicate_error = max(max_replicate_error, error)
                assert error < TOL
                for j, method in enumerate(METHODS):
                    primary = boot["bands"][band]["methods"][method][estimand]
                    point = (
                        math.fsum(map(float, complete_fraction[:, j])) / n
                        - math.fsum(map(float, fp_fraction)) / n
                        if estimand.startswith("mean")
                        else (math.fsum(map(float, complete[:, j])) - math.fsum(map(float, fp))) / math.fsum(map(float, a))
                    )
                    quantiles = np.quantile(values[:, j], [0.025, 0.5, 0.975], method="linear")
                    assert primary["conditional_empirical_percentile_probabilities"] == [0.025, 0.5, 0.975]
                    deltas = [
                        abs(point - primary["point_fraction"]),
                        float(np.max(np.abs(quantiles - primary["conditional_empirical_percentile_fractions"]))),
                        abs(float(values[:, j].std(ddof=1)) - primary["bootstrap_replicate_standard_deviation_fraction"]),
                    ]
                    max_summary_error = max(max_summary_error, *deltas)
                    assert max(deltas) < TOL
                    row = ranges[(band, method, estimand)]
                    assert int(row["histories"]) == n and int(row["replicates"]) == count
                    csv_numbers = np.array([float(row[key]) for key in [
                        "point_percentage_points", "conditional_p2_5_percentage_points",
                        "conditional_p50_percentage_points", "conditional_p97_5_percentage_points"]])
                    assert np.max(np.abs(csv_numbers - 100 * np.r_[point, quantiles])) < 1e-9
                    report[method + "/" + estimand] = {
                        "point_fraction": point,
                        "conditional_iid_empirical_percentile_fractions": quantiles.tolist(),
                        "maximum_summary_absolute_error": max(deltas),
                    }
            results[band] = {"histories": n, "replicates": count, "summaries": report}
            print(band + ": independent multiplicity verification passed")
    assert len(ranges) == 12
    source = full["execution"]
    assert source["source_function_executed_once_on_all_1003_inputs"]
    assert source["input_histories"] == 1003 and source["input_samples_per_history"] == 40764
    assert source["selected_output_histories"] == 751
    for band, n in [("intermediate", 667), ("high", 84)]:
        assert source["bands"][band]["selected_histories"] == n
        assert source["bands"][band]["source_indices_exact"]
        assert source["bands"][band]["all_three_returned_arrays_exact"]
        assert all(c["mismatching_values"] == 0 and c["maximum_absolute_difference"] == 0 for c in source["bands"][band]["channels"])
    manifest = json.loads((ROOT / "data/upstream-cc0/released-cohort-inventory.json").read_text())
    expected_raw = {entry["id"]: entry for entry in manifest["files"]}
    assert len(full["raw_input_bindings"]) == len(expected_raw) == 32
    for item in full["raw_input_bindings"]:
        target = expected_raw[item["id"]]
        assert item["sha256"] == target["sha256"] and item["bytes"] == target["size"]
        assert item["hash_verified_before_read"] and item["metadata_unchanged_after_read"]
    interpretation = boot["interpretation"]
    assert "NOT population confidence intervals" in interpretation
    assert any("correlated" in text for text in boot["limitations"])
    assert any("probabilities are unknown" in text for text in boot["limitations"])
    inputs = []
    for name in ["experiments/validate_full_source_and_bootstrap.py",
                 "results/full-source-validation-v1.2.0.json",
                 "results/paired-history-bootstrap-v1.2.0.json",
                 "results/paired-history-bootstrap-v1.2.0.npz",
                 "results/paired-history-bootstrap-ranges-v1.2.0.csv",
                 "results/public-batch-per-particle.npz",
                 "data/upstream-cc0/first_passage_function.py",
                 "data/upstream-cc0/released-cohort-inventory.json"]:
        inputs.append({"path": name, "sha256": sha(ROOT / name)})
    result = {
        "schema_version": 1, "status": "pass",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "verifier": {"path": "experiments/verify_source_bootstrap_compact.py", "sha256": sha(__file__)},
        "inputs": inputs, "replicate_absolute_tolerance": TOL,
        "independent_algorithm": "PCG64 seeded whole-history draws converted to multiplicities; full and FP estimator numerators are computed separately, then differenced. No primary bootstrap function was imported.",
        "all_240000_stored_shift_values_numerically_reproduced": True,
        "maximum_replicate_absolute_error": max_replicate_error,
        "maximum_point_quantile_SD_absolute_error": max_summary_error,
        "all_12_CSV_and_JSON_range_records_verified": True,
        "source_execution_review": {
            "complete_pinned_function_execution_path_reviewed": True,
            "all_six_returned_arrays_and_two_index_lists_reported_exact": True,
            "all_32_raw_input_hash_bindings_match_public_inventory": True,
            "independent_second_raw_read_or_source_rerun": False,
            "scope": "The primary execution receipt and source path were reviewed and bound; only the paired bootstrap is independently recomputed here from compact records.",
        },
        "results": results,
        "interpretation": "Conditional iid empirical resampling diagnostics only. No representative source-population confidence interval, physical uncertainty bound, significance test or direction of full-cohort bias is established.",
        "limitations": [
            "Selected histories come from one simulation and may be correlated.",
            "Archive inclusion probabilities and unposted cohort composition are unknown.",
            "No independent-run or physical-cluster resampling is invented.",
            "Resampling does not resolve temporal/mask cadence or continuous-work ambiguity.",
        ],
        "old_outputs_modified": False, "raw_downloads": 0,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "pass", "max_replicate_error": max_replicate_error,
                      "receipt_sha256": sha(args.output)}, indent=2))


if __name__ == "__main__":
    main()
