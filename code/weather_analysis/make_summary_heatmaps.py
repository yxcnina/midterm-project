
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm



PROJECT_ROOT = Path(__file__).resolve().parents[2]

TABLE_DIR = PROJECT_ROOT / "artifacts" / "weather_analysis" / "tables"

OUTPUT_DIR = (
    PROJECT_ROOT
    / "artifacts"
    / "weather_analysis"
    / "figures"
    / "summary_heatmaps"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)



WEATHER_COMPARISONS = [
    ("Rainfall", "rainfall"),
    ("Extreme Heat", "heat"),
    ("Cold Weather", "cold"),
    ("Freezing Sensitivity", "freezing_sensitivity"),
]




ANALYSES = [
    {
        "question": "Q5",
        "title": "Intake Type",
        "category_column": "intake_type",
        "prefixes": [
            "q5_intake_type",
            "q5b_heat",
            "q5c_cold",
            "q5c_freezing_sensitivity",
        ],
        "filename": "q5_intake_type_summary_heatmap.png",
    },
    {
        "question": "Q7",
        "title": "Outcome Type",
        "category_column": "outcome_type",
        "prefixes": [
            "q7a_rainfall",
            "q7b_heat",
            "q7c_cold",
            "q7c_freezing_sensitivity",
        ],
        "filename": "q7_outcome_type_summary_heatmap.png",
    },
    {
        "question": "Q6",
        "title": "Intake Condition",
        "category_column": "intake_condition",
        "prefixes": [
            "q6a_rainfall",
            "q6b_heat",
            "q6c_cold",
            "q6c_freezing_sensitivity",
        ],
        "filename": "q6_intake_condition_summary_heatmap.png",
    },
]



def find_difference_column(df):
    """
    Find the percentage-point difference column.

    Different questions use different column names.
    """

    possible_columns = [
        "difference_pp",
        "wet_minus_dry_pp",
        "hot_minus_nonhot_pp",
        "cold_minus_noncold_pp",
        "freezing_minus_nonfreezing_pp",
    ]

    for column in possible_columns:
        if column in df.columns:
            return column

    
    candidates = [
        column
        for column in df.columns
        if column.endswith("_pp")
        and "proportion" not in column
        and "reference" not in column
        and "exposed" not in column
    ]

    if len(candidates) == 1:
        return candidates[0]

    raise ValueError(
        "Cannot identify a percentage-point difference column. "
        f"Available columns: {df.columns.tolist()}"
    )



def load_heatmap_data(config):

    category_column = config["category_column"]

    combined = None

    for (weather_label, _), prefix in zip(
        WEATHER_COMPARISONS,
        config["prefixes"],
    ):

        filename = f"{prefix}_differences.csv"
        path = TABLE_DIR / filename

        if not path.exists():
            raise FileNotFoundError(
                f"Required CSV file not found: {path}"
            )

        df = pd.read_csv(path)

        if category_column not in df.columns:
            raise ValueError(
                f"Missing category column '{category_column}' "
                f"in {filename}. "
                f"Available columns: {df.columns.tolist()}"
            )

        difference_column = find_difference_column(df)

        current = df[
            [category_column, difference_column]
        ].copy()

        current = current.rename(
            columns={
                difference_column: weather_label
            }
        )

        if current[category_column].duplicated().any():
            raise ValueError(
                f"Duplicate categories found in {filename}"
            )

        if combined is None:
            combined = current
        else:
            combined = combined.merge(
                current,
                on=category_column,
                how="outer",
                validate="one_to_one",
            )

    combined = combined.set_index(category_column)

    weather_columns = [
        label for label, _ in WEATHER_COMPARISONS
    ]

    combined = combined[weather_columns]

    if combined.isna().any().any():
        missing = combined[
            combined.isna().any(axis=1)
        ].index.tolist()

        raise ValueError(
            "Some categories are missing from one or more "
            f"weather comparisons: {missing}"
        )

    combined = combined.astype(float)

    row_order = (
        combined.abs()
        .max(axis=1)
        .sort_values(ascending=False)
        .index
    )

    return combined.loc[row_order]



def create_heatmap(data, config):

    question = config["question"]
    title = config["title"]

    number_of_categories = len(data)

    figure_height = max(
        5.5,
        number_of_categories * 0.46 + 2.0,
    )

    fig, ax = plt.subplots(
        figsize=(11, figure_height)
    )

    values = data.to_numpy()

    max_absolute_value = max(
        float(abs(values).max()),
        0.1,
    )

    norm = TwoSlopeNorm(
        vmin=-max_absolute_value,
        vcenter=0,
        vmax=max_absolute_value,
    )

    image = ax.imshow(
        values,
        cmap="RdBu_r",
        norm=norm,
        aspect="auto",
    )

    ax.set_xticks(range(len(data.columns)))
    ax.set_xticklabels(
        data.columns,
        fontsize=10,
    )

    ax.set_yticks(range(len(data.index)))
    ax.set_yticklabels(
        data.index,
        fontsize=9,
    )

    ax.set_xlabel(
        "Weather Comparison",
        fontsize=11,
        labelpad=12,
    )

    ax.set_ylabel(
        title,
        fontsize=11,
        labelpad=12,
    )

    ax.set_title(
        f"{question}: {title} Composition Across Weather Conditions",
        fontsize=14,
        fontweight="bold",
        pad=18,
    )


    for row in range(values.shape[0]):
        for column in range(values.shape[1]):

            value = values[row, column]

            text_color = (
                "white"
                if abs(value) > max_absolute_value * 0.6
                else "black"
            )

            ax.text(
                column,
                row,
                f"{value:+.2f}",
                ha="center",
                va="center",
                fontsize=9,
                color=text_color,
            )

    colorbar = fig.colorbar(
        image,
        ax=ax,
        fraction=0.035,
        pad=0.035,
    )

    colorbar.set_label(
        "Difference in Percentage Points",
        fontsize=10,
    )

    ax.set_xticks(
        [x - 0.5 for x in range(1, len(data.columns))],
        minor=True,
    )

    ax.set_yticks(
        [y - 0.5 for y in range(1, len(data.index))],
        minor=True,
    )

    ax.grid(
        which="minor",
        color="white",
        linewidth=1.2,
    )

    ax.tick_params(
        which="minor",
        bottom=False,
        left=False,
    )

    fig.text(
        0.5,
        0.015,
        (
            "Values are exposed-group minus reference-group "
            "percentage-point differences. "
            "Descriptive associations only."
        ),
        ha="center",
        fontsize=9,
        color="dimgray",
    )

    fig.tight_layout(
        rect=[0, 0.045, 1, 1]
    )

    output_path = OUTPUT_DIR / config["filename"]

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)

    return output_path



def main():

    for config in ANALYSES:

        print(
            f"\n=== {config['question']} "
            f"{config['title']} Summary Heatmap ==="
        )

        data = load_heatmap_data(config)

        print("\nHeatmap data:")
        print(data.round(4).to_string())

        output_path = create_heatmap(
            data,
            config,
        )

        print(f"\nSaved: {output_path}")

    print("\n=== All Summary Heatmaps Complete ===")
    print("Three summary heatmaps generated successfully.")


if __name__ == "__main__":
    main()
