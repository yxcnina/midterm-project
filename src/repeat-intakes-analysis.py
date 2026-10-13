import os

import matplotlib.pyplot as plt
import pandas as pd

from plot_style import (
    CATEGORY_PALETTE,
    MAIN_COLOR,
    NEUTRAL_COLOR,
    ACCENT_COLOR,
    SECONDARY_COLOR,
    set_plot_style,
)


DATA_PATH = os.path.join(
    "data",
    "processed",
    "aac_in-out-episodes_2024.csv",
)

FIGURE_DIR = os.path.join(
    "artifacts",
    "figures",
)

os.makedirs(
    FIGURE_DIR,
    exist_ok=True,
)

Analysis = pd.read_csv(
    DATA_PATH,
    parse_dates=[
        "Intake_DateTime",
        "Outcome_DateTime",
    ],
)

# Connect each intake with the preceding outcome
Analysis["Previous Outcome Type"] = (
    Analysis.groupby("Animal ID")[
        "Outcome Type"
    ].shift(1)
)

Analysis["Previous Outcome_DateTime"] = (
    Analysis.groupby("Animal ID")[
        "Outcome_DateTime"
    ].shift(1)
)

Analysis["Days to Return"] = (
    (
        Analysis["Intake_DateTime"]
        - Analysis["Previous Outcome_DateTime"]
    ).dt.total_seconds()
    / 86400
).round(2)

# Identify repeat-intake episodes
QUALIFYING_OUTCOMES = {
    "Adoption",
    "Return to Owner",
    "Rto-Adopt",
}

is_repeat_intake = (
    (Analysis["Intake Event Number"] > 1)
    & Analysis["Previous Outcome Type"].isin(
        QUALIFYING_OUTCOMES
    )
)

repeat_intakes = Analysis.loc[
    is_repeat_intake
].copy()


repeat_animal_ids = (
    repeat_intakes["Animal ID"]
    .drop_duplicates()
)

repeat_animal_episodes = Analysis.loc[
    Analysis["Animal ID"].isin(
        repeat_animal_ids
    )
].copy()

# Summary Statistic
total_intake_episodes = len(Analysis)

total_animals = (
    Analysis["Animal ID"].nunique()
)

repeat_episode_count = len(
    repeat_intakes
)

repeat_animal_count = (
    repeat_intakes["Animal ID"]
    .nunique()
)

repeat_episode_share = (
    repeat_episode_count
    / total_intake_episodes
    * 100
)

repeat_animal_share = (
    repeat_animal_count
    / total_animals
    * 100
)

median_return_days = (
    repeat_intakes["Days to Return"]
    .median()
)

within_90_days = (
    repeat_intakes["Days to Return"]
    .le(90)
    .mean()
    * 100
)

set_plot_style()
# Figure 1: Share of repeat-intake episodes

figure_1 = pd.Series(
    {
        "Repeat intakes":
            repeat_episode_count,
        "Other intakes":
            total_intake_episodes
            - repeat_episode_count,
    }
).plot(kind="pie",
    autopct="%1.1f%%",
    colors=[
        MAIN_COLOR,
        NEUTRAL_COLOR,
    ],
    ylabel="",
    title="Share of Repeat Intakes in 2024",)

plt.savefig(
    os.path.join(
        FIGURE_DIR,
        "01_repeat_intake_share.png",
    )
)

plt.close()


# Figure 2: Repeat-intake scale
figure_2 = pd.Series(
    {
        "Repeat-intake episodes":
            repeat_episode_count,
        "Animals involved":
            repeat_animal_count,
    }
).plot(
    kind="bar",
    color=[
        MAIN_COLOR,
        SECONDARY_COLOR,
    ],
    xlabel="Measure",
    ylabel="Count",
    title="Repeat Intakes at Austin Animal Center in 2024",
    rot=0,
)

figure_2.bar_label(
    figure_2.containers[0],
    fmt="%d",
)

plt.savefig(
    os.path.join(
        FIGURE_DIR,
        "02_repeat_intake_scale.png",
    )
)

plt.close()

#Figure 3: Return-time distribution
return_time_labels = [
    "0-7 days",
    "8-30 days",
    "31-90 days",
    "More than 90 days",
]

repeat_intakes["Return Time Group"] = pd.cut(
    repeat_intakes["Days to Return"],
    bins=[
        0,
        7,
        30,
        90,
        float("inf"),
    ],
    labels=return_time_labels,
    include_lowest=True,
)

return_time_distribution = (
    repeat_intakes["Return Time Group"]
    .value_counts(normalize=True)
    .reindex(return_time_labels)
    .mul(100)
)

figure_3 = return_time_distribution.plot(
    kind="bar",
    color=MAIN_COLOR,
    xlabel="Time until return",
    ylabel="Percent of repeat intakes",
    title="Time Between Outcome and Repeat Intake",
    rot=0,
)

figure_3.bar_label(
    figure_3.containers[0],
    fmt="%.1f%%",
)

plt.savefig(
    os.path.join(
        FIGURE_DIR,
        "03_return_time_distribution.png",
    )
)

plt.close()

#Figure 4: Return pathways
repeat_intakes["Return Pathway"] = (
    repeat_intakes["Previous Outcome Type"]
    + " → "
    + repeat_intakes["Intake Type"]
)

pathway_percent = (
    repeat_intakes["Return Pathway"]
    .value_counts(normalize=True)
    .mul(100)
)

top_pathways = pathway_percent.head(6)
other_percent = 100 - top_pathways.sum()
return_pathway_distribution = pd.concat(
    [
        top_pathways,
        pd.Series(
            {
                "Other": other_percent,
            }
        ),
    ]
)

legend_labels = [
    f"{pathway} ({percent:.1f}%)"
    for pathway, percent
    in return_pathway_distribution.items()
]

figure_4 = return_pathway_distribution.plot(
    kind="pie",
    labels=[
        ""
        for _ in return_pathway_distribution
    ],
    autopct=lambda percent: (
        f"{percent:.1f}%"
        if percent >= 5
        else ""
    ),
    colors=CATEGORY_PALETTE[
        :len(return_pathway_distribution)
    ],
    startangle=90,
    counterclock=False,
    ylabel="",
    title="Most Common Pathways Back to the Shelter",
    textprops={
        "fontsize": 10,
    },
)

figure_4.legend(
    figure_4.patches,
    return_pathway_distribution.index,
    title="Return pathway",
    loc="center left",
    bbox_to_anchor=(1, 0.5),
    fontsize=10,
)

plt.savefig(
    os.path.join(
        FIGURE_DIR,
        "04_return_pathways.png",
    ),
    bbox_inches="tight",
)

plt.close()

#Figure 5: Outcomes after repeat intake
outcome_distribution = (
    repeat_intakes["Outcome Type"]
    .fillna("No recorded outcome")
    .value_counts(normalize=True)
    .mul(100)
    .sort_values()
)

figure_5 = outcome_distribution.plot(
    kind="barh",
    color=ACCENT_COLOR,
    xlabel="Percent of repeat intakes",
    ylabel="Outcome type",
    title="Outcomes After a Repeat Intake",
)

figure_5.bar_label(
    figure_5.containers[0],
    fmt="%.1f%%",
)

plt.savefig(
    os.path.join(
        FIGURE_DIR,
        "05_outcomes_after_repeat_intake.png",
    ),
    bbox_inches="tight"
)

plt.close()

#Figure 6: Intake-frequency distribution
intake_frequency = (
    repeat_animal_episodes
    .groupby("Animal ID")
    .size()
    .value_counts()
    .sort_index()
)

figure_6 = intake_frequency.plot(
    kind="bar",
    color=MAIN_COLOR,
    xlabel="Total intakes per animal in 2024",
    ylabel="Number of animals",
    title="Number of Intakes Among Repeat-Intake Animals",
    rot=0,
)

figure_6.bar_label(
    figure_6.containers[0],
    fmt="%d",
)

plt.savefig(
    os.path.join(
        FIGURE_DIR,
        "06_repeat_intake_frequency.png",
    ),
    bbox_inches="tight",
)

plt.close()
