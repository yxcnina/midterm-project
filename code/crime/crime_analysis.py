"""Analyze Austin 2024 council-district crime and stray-intake summaries.

Inputs (produced by crime_component.py):
    data/processed/crime_stray_district_month_2024.csv
    data/processed/crime_stray_district_2024.csv

Outputs (under artifacts/crime/analysis/):
    annual_district_scatter.png
    monthly_daily_averages.png
    adjusted_within_district_month.png
    crime_monthly_summary.csv
    crime_analysis_statistics.csv
    crime_regression_results.csv

Run from repository root: python code/crime/crime_analysis.py
"""

from calendar import monthrange
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
import statsmodels.formula.api as smf


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "processed"
OUTPUT_DIR = ROOT / "artifacts" / "crime" / "analysis"
MONTHLY_FILE = DATA_DIR / "crime_stray_district_month_2024.csv"
ANNUAL_FILE = DATA_DIR / "crime_stray_district_2024.csv"


def load_and_validate():
    """Return complete month and year tables after consistency checks."""
    for file in (MONTHLY_FILE, ANNUAL_FILE):
        if not file.is_file():
            raise FileNotFoundError(f"Missing input CSV: {file}")

    monthly = pd.read_csv(MONTHLY_FILE)
    annual = pd.read_csv(ANNUAL_FILE)
    keys = ["district", "month"]
    measurements = ["crime_count", "stray_intake_count"]

    if set(keys + measurements) != set(monthly.columns):
        raise ValueError("Monthly CSV must have district, month and two count columns")
    if set(["district"] + measurements) != set(annual.columns):
        raise ValueError("Annual CSV must have district and two count columns")
    if monthly.isna().any().any() or annual.isna().any().any():
        raise ValueError("Input files contain missing values")
    if monthly.duplicated(keys).any() or annual.duplicated("district").any():
        raise ValueError("Repeated geography/month combinations")

    # Reject malformed identifiers and fractional/non-numeric counts before
    # converting types: astype(int) alone would silently truncate values.
    for label, frame, columns in (
        ("Monthly", monthly, keys + measurements),
        ("Annual", annual, ["district"] + measurements),
    ):
        for column in columns:
            try:
                values = pd.to_numeric(frame[column], errors="raise")
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{label} {column} must be numeric") from exc
            if not np.isfinite(values.to_numpy(dtype=float)).all():
                raise ValueError(f"{label} {column} contains non-finite values")
            if not (values % 1 == 0).all():
                raise ValueError(f"{label} {column} must contain whole numbers")
            if column in measurements and (values < 0).any():
                raise ValueError("Counts cannot be negative")
            frame[column] = values.astype("int64")

    if not monthly["district"].between(1, 10).all():
        raise ValueError("Monthly districts must be from 1 through 10")
    if not monthly["month"].between(1, 12).all():
        raise ValueError("Monthly months must be from 1 through 12")
    if not annual["district"].between(1, 10).all():
        raise ValueError("Annual districts must be from 1 through 10")

    expected = pd.MultiIndex.from_product(
        [range(1, 11), range(1, 13)], names=keys
    )
    actual = pd.MultiIndex.from_frame(monthly[keys])
    if len(monthly) != 120 or set(actual) != set(expected):
        raise ValueError("Expected all 10 districts x all 12 months")

    recomputed = (
        monthly.groupby("district", as_index=False)[measurements]
        .sum()
        .sort_values("district")
        .reset_index(drop=True)
    )
    annual = annual.sort_values("district").reset_index(drop=True)
    if not recomputed.equals(annual):
        raise ValueError("Annual totals disagree with monthly CSV")
    monthly = monthly.sort_values(keys).reset_index(drop=True)
    return monthly, annual


def save_annual_chart(annual):
    """Visualize the cross-district (not causal) relationship."""
    fig, ax = plt.subplots(figsize=(8.2, 5.5))
    ax.scatter(annual["crime_count"], annual["stray_intake_count"], s=65)
    label_offsets = {6: (-20, 15), 10: (12, 2)}
    for row in annual.itertuples(index=False):
        ax.annotate(
            f"D{row.district}",
            (row.crime_count, row.stray_intake_count),
            xytext=label_offsets.get(row.district, (5, 5)),
            textcoords="offset points",
            fontsize=9,
        )
    corr = pearsonr(annual["crime_count"], annual["stray_intake_count"])
    ax.text(
        0.02, 0.97,
        f"Pearson r = {corr.statistic:.3f}; n = 10 districts",
        transform=ax.transAxes,
        va="top",
        fontsize=10,
    )
    ax.set_title("Austin 2024: Reported Crime vs. Geocoded Stray Intakes")
    ax.set_xlabel("Reported crime incidents (annual count)")
    ax.set_ylabel("Geocoded stray intake records (annual count)")
    ax.grid(alpha=0.22)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "annual_district_scatter.png", dpi=200)
    plt.close(fig)


def monthly_table_and_chart(monthly):
    """Normalize monthly counts to average per day to account for month length."""
    totals = monthly.groupby("month", as_index=False)[
        ["crime_count", "stray_intake_count"]
    ].sum()
    totals["days"] = totals["month"].map(lambda month: monthrange(2024, month)[1])
    totals["crime_per_day"] = totals["crime_count"] / totals["days"]
    totals["stray_per_day"] = totals["stray_intake_count"] / totals["days"]
    totals.to_csv(OUTPUT_DIR / "crime_monthly_summary.csv", index=False)

    fig, axes = plt.subplots(2, 1, figsize=(9, 6.5), sharex=True)
    axes[0].plot(totals["month"], totals["crime_per_day"], marker="o")
    axes[0].set_ylabel("Crime reports / day")
    axes[0].set_title("Reported Crime: Monthly Average per Day")
    axes[1].plot(totals["month"], totals["stray_per_day"], marker="o")
    axes[1].set_ylabel("Stray intakes / day")
    axes[1].set_title("Geocoded Stray Intakes: Monthly Average per Day")
    axes[1].set_xlabel("Month in 2024")
    axes[1].set_xticks(range(1, 13))
    for ax in axes:
        ax.grid(alpha=0.22)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "monthly_daily_averages.png", dpi=200)
    plt.close(fig)
    return totals


def save_adjusted_chart(monthly):
    """Plot deviations after removing district and month averages."""
    adj = monthly.copy()
    for field in ["crime_count", "stray_intake_count"]:
        adj[f"adjusted_{field}"] = (
            adj[field]
            - adj.groupby("district")[field].transform("mean")
            - adj.groupby("month")[field].transform("mean")
            + adj[field].mean()
        )

    x = adj["adjusted_crime_count"]
    y = adj["adjusted_stray_intake_count"]
    fig, ax = plt.subplots(figsize=(8.2, 5.5))
    ax.scatter(x, y, alpha=0.7)
    ax.axhline(0, linewidth=0.8)
    ax.axvline(0, linewidth=0.8)
    ax.set_title("Association after Removing District and Month Averages")
    ax.set_xlabel("Crime reports: adjusted difference from expected count")
    ax.set_ylabel("Stray intakes: adjusted difference from expected count")
    ax.text(
        0.02, 0.97,
        f"Adjusted Pearson r = {pearsonr(x, y).statistic:.3f}",
        transform=ax.transAxes,
        va="top",
    )
    ax.grid(alpha=0.18)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "adjusted_within_district_month.png", dpi=200)
    plt.close(fig)
    return adj


def correlation_table(monthly, annual, totals, adjusted):
    """Save descriptive Pearson/Spearman correlations with sample sizes."""
    configurations = [
        ("annual_districts", annual, "crime_count", "stray_intake_count"),
        ("pooled_district_months", monthly, "crime_count", "stray_intake_count"),
        ("aggregated_months", totals, "crime_count", "stray_intake_count"),
        (
            "district_and_month_adjusted",
            adjusted,
            "adjusted_crime_count",
            "adjusted_stray_intake_count",
        ),
    ]
    rows = []
    for label, frame, x, y in configurations:
        pearson = pearsonr(frame[x], frame[y])
        spearman = spearmanr(frame[x], frame[y])
        rows.append({
            "analysis": label,
            "observations": len(frame),
            "pearson_r": pearson.statistic,
            "pearson_naive_p": pearson.pvalue,
            "spearman_rho": spearman.statistic,
            "spearman_naive_p": spearman.pvalue,
        })
    result = pd.DataFrame(rows)
    result.to_csv(OUTPUT_DIR / "crime_analysis_statistics.csv", index=False)
    return result


def regression_table(monthly):
    """OLS sensitivity analysis, using district-clustered standard errors."""
    model_specs = [
        ("Unadjusted", "stray_intake_count ~ crime_count"),
        ("District controls", "stray_intake_count ~ crime_count + C(district)"),
        (
            "District and month controls",
            "stray_intake_count ~ crime_count + C(district) + C(month)",
        ),
    ]
    rows = []
    for name, formula in model_specs:
        model = smf.ols(formula, data=monthly).fit()
        robust = model.get_robustcov_results(
            cov_type="cluster", groups=monthly["district"]
        )
        index = model.model.exog_names.index("crime_count")
        confidence = robust.conf_int()[index]
        rows.append({
            "model": name,
            "observations": int(model.nobs),
            "district_clusters": int(monthly["district"].nunique()),
            "change_in_strays_per_100_crime_reports":
                100 * float(model.params["crime_count"]),
            "cluster_robust_p": float(robust.pvalues[index]),
            "ci_low_per_100": float(100 * confidence[0]),
            "ci_high_per_100": float(100 * confidence[1]),
            "r_squared": float(model.rsquared),
        })
    result = pd.DataFrame(rows)
    result.to_csv(OUTPUT_DIR / "crime_regression_results.csv", index=False)
    return result


def main():
    """Verify inputs, generate figures, save analysis and print key results."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    monthly, annual = load_and_validate()
    save_annual_chart(annual)
    totals = monthly_table_and_chart(monthly)
    adjusted = save_adjusted_chart(monthly)
    correlations = correlation_table(monthly, annual, totals, adjusted)
    regressions = regression_table(monthly)
    print("DATA VERIFIED: 10 districts x 12 months; annual totals agree.")
    print("TOTAL CRIME:", int(annual["crime_count"].sum()))
    print("TOTAL GEOCODED STRAY INTAKES:", int(annual["stray_intake_count"].sum()))
    print("\nCORRELATIONS\n", correlations.round(4).to_string(index=False))
    print("\nOLS WITH DISTRICT-CLUSTERED SE\n", regressions.round(4).to_string(index=False))
    print("\nResults saved to:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
