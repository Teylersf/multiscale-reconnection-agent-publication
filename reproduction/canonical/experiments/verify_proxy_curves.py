#!/usr/bin/env python3
"""Reconstruct published proxy curves from frozen primary data, without a PIC run.

Requirements: Python 3, NumPy, Matplotlib. No network, pickle loading, or original
figure redistribution. See data/proxy-reconstruction-provenance.json for hashes,
versions, licenses, and the numerical coordinate extraction.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def gaussian_reflect(values, sigma=1.5):
    """Gaussian filter with half-sample symmetric/reflect boundary, truncate=4."""
    radius = int(4 * sigma + 0.5)
    offsets = np.arange(-radius, radius + 1)
    weights = np.exp(-offsets**2 / (2 * sigma**2))
    weights /= weights.sum()
    return np.convolve(np.pad(values, radius, mode="symmetric"), weights, mode="valid")


def check_coordinates(actual, expected, tolerance):
    residual = np.asarray(expected) - np.asarray(actual)
    return {
        "points": int(len(actual)),
        "max_abs_x_pdf_points": float(np.max(np.abs(residual[:, 0]))),
        "max_abs_y_pdf_points": float(np.max(np.abs(residual[:, 1]))),
        "rms_coordinate_residual_pdf_points": float(np.sqrt(np.mean(residual**2))),
        "tolerance_pdf_points": tolerance,
        "passed": bool(np.max(np.abs(residual)) < tolerance),
    }


def energy_log_check(energies, raw_jdote, tau_a, actual_interval, published_count):
    steps = energies[:, 0]
    unique_steps, first, counts = np.unique(steps, return_index=True, return_counts=True)
    last = len(steps) - 1 - np.unique(steps[::-1], return_index=True)[1]
    # Both alternatives are checked; neither restart chronology is assumed.
    last = last[np.argsort(steps[last])]
    first_rows = energies[first]
    last_rows = energies[last]
    duplicates_identical = bool(np.array_equal(first_rows, last_rows))
    magnetic = first_rows[:, 4:7].sum(axis=1)
    electric = first_rows[:, 1:4].sum(axis=1)
    kinetic = first_rows[:, 7:].sum(axis=1)
    initial_m = magnetic[0]
    initial_total = initial_m + electric[0] + kinetic[0]
    snapshots = []
    for index in [published_count - 1, len(raw_jdote) - 1]:
        conditional_step = index * 409 * 5
        b = np.interp(conditional_step, unique_steps, magnetic)
        e = np.interp(conditional_step, unique_steps, electric)
        k = np.interp(conditional_step, unique_steps, kinetic)
        snapshots.append({
            "cumulative_array_index": index,
            "conditional_step": conditional_step,
            "conditional_t_over_tA_using_info_dt": float(index * actual_interval / tau_a),
            "minus_delta_M_over_M0": float((initial_m - b) / initial_m),
            "minus_delta_EM_over_M0": float((initial_m - b - e + electric[0]) / initial_m),
            "delta_K_over_M0": float((k - kinetic[0]) / initial_m),
            "raw_JdotE_integral_divided_by_25": float(raw_jdote[index] / 25),
            "raw_JdotE_integral_with_exact_info_dt": float(raw_jdote[index] * actual_interval / 4000),
            "total_energy_drift_over_M0": float((b + e + k - initial_total) / initial_m),
        })
    return {
        "status": "conditional consistency context, not a run-identity proof or De energy-conservation test",
        "raw_rows": int(len(energies)), "unique_steps": int(len(unique_steps)),
        "duplicate_rows": int(np.sum(counts - 1)),
        "restart_backwards_transitions": int(np.sum(np.diff(steps) < 0)),
        "all_duplicate_step_values_identical_at_reported_precision": duplicates_identical,
        "unique_step_range": [float(unique_steps[0]), float(unique_steps[-1])],
        "unique_step_spacing": [float(v) for v in np.unique(np.diff(unique_steps))],
        "initial_magnetic_energy": float(initial_m),
        "initial_kinetic_energy": float(kinetic[0]),
        "snapshots": snapshots,
        "limits": [
            "Shared L320 labels and matching header/info timestep do not prove a common executable/run revision.",
            "The diagnostic uses 50-step averages spaced by 2045 steps; the global log samples every 100 steps.",
            "An integral of the electron-frame proxy De is not identically the global change in magnetic or particle energy.",
            "No unaligned raw cumulative value is treated as evidence of incorrect published physics.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--report", type=Path)
    parser.add_argument("--figure", type=Path)
    args = parser.parse_args()
    study = args.study.resolve()
    report_path = args.report or study / "results/proxy-verification.json"
    figure_path = args.figure or study / "figures/proxy-reconstruction.png"
    provenance = json.loads((study / "data/proxy-reconstruction-provenance.json").read_text())
    fixture_hashes = []
    for item in provenance["fixtures"]:
        path = study / item["path"]
        actual = sha256(path)
        if actual != item["sha256"]:
            raise ValueError(f"Fixture hash mismatch: {item['path']}")
        fixture_hashes.append({"path": item["path"], "sha256": actual, "verified": True})
    with np.load(study / "data/upstream.npz", allow_pickle=False) as data:
        data = {key: data[key] for key in data.files}
    with np.load(study / "data/published-vector-coordinates.npz", allow_pickle=False) as coords:
        coords = {key: coords[key] for key in coords.files}
    tau_a = 4 * np.pi * 320 / (5 / np.sqrt(27))
    dt_wpe = 0.07809755
    actual_interval = 409 * 5 * dt_wpe
    raw_time = data["time_raw_320"]
    displayed_time = raw_time / 5
    regions = {
        "total": data["cumulative_320_total"],
        "ds": data["cumulative_320_ds"], "cs": data["cumulative_320_cs"],
        "is": data["cumulative_320_is1"] + data["cumulative_320_is2"],
        "tb": data["cumulative_320_tb"],
    }
    calibration = provenance["axis_calibration"]
    f3 = calibration["figure3"]
    f4 = calibration["figure4"]
    tol = calibration["tolerance_pdf_points"]
    count = len(coords["figure3_total"])
    checks = {}
    for key, raw_values in regions.items():
        displayed = raw_values[:count] / 25
        xy = np.column_stack([
            f3["x_at_0"] + (f3["x_at_5"] - f3["x_at_0"]) / 5 * displayed_time[:count],
            f3["top_y_at_0"] - (f3["top_y_at_0"] - f3["top_y_at_0_015"]) / 0.015 * displayed,
        ])
        checks[f"figure3_{key}"] = check_coordinates(coords[f"figure3_{key}"], xy, tol)
    inst = data["instantaneous_320_total"].astype(float)
    inst_count = len(coords["figure4_total"])
    # Empirically verified display reconstruction, not an assertion that the
    # deposited default-L40 script is the exact original plotting program.
    displayed_rate = gaussian_reflect(inst[:inst_count]) * tau_a
    rate_time = displayed_time[1:inst_count + 1]
    xy = np.column_stack([
        f4["x_at_0"] + (f4["x_at_4"] - f4["x_at_0"]) / 4 * rate_time,
        f4["top_y_at_0"] - (f4["top_y_at_0"] - f4["top_y_at_0_01"]) / 0.01 * displayed_rate,
    ])
    checks["figure4_total"] = check_coordinates(coords["figure4_total"], xy, tol)
    increment_residual = np.diff(regions["total"]) - inst * 4000
    denominator = regions["total"][count - 1]
    fractions = {key: float(value[count - 1] / denominator) for key, value in regions.items() if key != "total"}
    scaled_fractions = {
        key: float((value[count - 1] / 25) / (denominator / 25))
        for key, value in regions.items() if key != "total"
    }
    energy = energy_log_check(
        data["global_energies_320"], data["jdotE_cumulative_320"],
        tau_a, actual_interval, count
    )
    result = {
        "study": "arXiv:2511.15988v1 positive proxy-curve reconstruction",
        "fixture_hashes": fixture_hashes,
        "result": "published curves consistent with explicitly transformed deposited arrays",
        "all_coordinate_checks_passed": all(item["passed"] for item in checks.values()),
        "checks": checks,
        "display_transforms": {
            "time": "t_display = time_raw_320 / 5",
            "cumulative": "D_display = cumulative_raw / 25",
            "rate": "rate_display = tauA * GaussianReflect(instantaneous_raw[:115], sigma=1.5, truncate=4)",
            "tauA_in_plasma_time_units": float(tau_a),
            "published_cumulative_count": count,
            "published_cumulative_endpoint": {
                "time": float(displayed_time[count - 1]),
                "total": float(denominator / 25),
            },
            "published_rate_path_count": inst_count,
            "rate_plot_visible_xrange": [0, 4],
            "rate_path_caveat": "The stored vector path includes points clipped by the original x-axis limit at 4; the own plot uses the visible 0..4 interval.",
        },
        "raw_array_checks": {
            "raw_time_spacing": float(raw_time[1] - raw_time[0]),
            "raw_time_spacing_times_tauA": float((raw_time[1] - raw_time[0]) * tau_a),
            "max_abs_diff_cumulative_minus_4000_instantaneous": float(np.max(np.abs(increment_residual))),
            "regional_fractions_before_scaling": fractions,
            "regional_fractions_after_scaling": scaled_fractions,
            "fraction_max_abs_difference": float(max(abs(fractions[k] - scaled_fractions[k]) for k in fractions)),
        },
        "clock_context": {
            "info_dt_wpe": dt_wpe, "info_field_interval_steps": 409,
            "averaging_spacing_field_outputs": 5, "averaging_steps": 50,
            "physical_plasma_time_per_average_spacing": float(actual_interval),
            "display_nominal_plasma_time_per_average_spacing": 160.0,
            "nominal_over_actual": float(160 / actual_interval),
            "interpretation": "A 0.1819% nominal-versus-truncated-step clock difference remains; it is distinguished from the removed factors 5 and 25 and is not called an established paper error.",
        },
        "conditional_global_energy_context": energy,
        "scope": [
            "Checks displayed L320 proxy curves only, not a new PIC simulation or independent regional-mask validation.",
            "OSF project/file dates and renamed figure layout are later than arXiv-v1; exact run provenance remains bounded.",
            "This evidence positively rules out alleging a factor 25 error in the published v1 curves from the untransformed arrays.",
        ],
    }
    if not result["all_coordinate_checks_passed"]:
        raise AssertionError(json.dumps(result["checks"], indent=2))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(1, 2, figsize=(10.6, 3.8), constrained_layout=True)
    colors = {"total": "#222222", "ds": "#2455c3", "cs": "#dc8b12", "is": "#c53c45", "tb": "#15874a"}
    labels = {"total": "Total", "ds": "Downstream", "cs": "Primary current sheet", "is": "Islands", "tb": "Top / bottom"}
    for key, raw_values in regions.items():
        ax[0].plot(displayed_time[:count], raw_values[:count] / 25, color=colors[key], label=labels[key], lw=1.8)
    ax[0].set(xlabel=r"$t/t_A$ (raw time / 5)", ylabel=r"Cumulative $\mathcal{D}_i$ (raw / 25)",
              title="Cumulative proxy: published Fig. 3", xlim=(0, 4.5), ylim=(-0.0002, 0.015))
    ax[0].legend(loc="upper left", frameon=False, fontsize=8.5)
    ax[1].plot(rate_time, displayed_rate, color=colors["ds"], lw=1.8)
    ax[1].set(xlabel=r"$t/t_A$ (raw time / 5)", ylabel=r"$t_A \int D_e\,dV/M_0$",
              title="Smoothed rate: published Fig. 4", xlim=(0, 4), ylim=(-0.0002, 0.012))
    for axes in ax:
        axes.grid(alpha=0.18)
        axes.ticklabel_format(axis="y", style="plain", useOffset=False)
    figure_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(figure_path, dpi=180, metadata={"Author": "Taylor Kalin", "Description": "Independent reconstruction from OSF EPWTU CC0 arrays; attribution and source versions in companion provenance JSON."})
    plt.close(fig)
    result["generated_figure"] = {"path": figure_path.relative_to(study).as_posix(), "sha256": sha256(figure_path)}
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "all_coordinate_checks_passed": result["all_coordinate_checks_passed"],
        "max_coordinate_residual_pdf_points": max(max(v["max_abs_x_pdf_points"], v["max_abs_y_pdf_points"]) for v in checks.values()),
        "regional_fractions": fractions,
        "report": str(report_path), "figure": str(figure_path),
    }, indent=2))


if __name__ == "__main__":
    main()
