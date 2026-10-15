import os
import pandas as pd

INTAKE_PATH = os.path.join(
    "data",
    "processed",
    "aac_intakes_clean.csv"
)

OUTCOME_PATH = os.path.join(
    "data",
    "processed",
    "aac_outcomes_clean.csv"
)

OUTPUT_PATH = os.path.join(
    "data",
    "processed",
    "aac_in-out-episodes_2024.csv"
)

start_date = "2024-01-01"
end_date = "2025-01-01"

QUALIFYING_OUTCOMES = {
    "Adoption",
    "Return to Owner",
    "Rto-Adopt",
}

intakes = pd.read_csv(INTAKE_PATH,parse_dates=["DateTime"])
outcomes = pd.read_csv(OUTCOME_PATH,parse_dates=["DateTime"])


intakes = intakes.rename(
    columns= {
        "DateTime": "Intake_DateTime",
    }
).copy()

intakes = intakes.sort_values(
    ["Animal ID","Intake_DateTime"],
    kind="mergesort",
).reset_index(drop=True)

intakes["Intake Event Number"] = (
    intakes.groupby("Animal ID").cumcount() + 1
)

intakes["Intake Event ID"] = (
    intakes["Animal ID"].astype(str)
    + "_"
    + intakes["Intake Event Number"].astype(str)
)

outcomes = outcomes.rename(
    columns ={
        "DateTime": "Outcome_DateTime",
        }
).copy()

def match_outcomes_to_intakes(intakes, outcomes):
    intakes_for_matching = intakes.sort_values(
        ["Intake_DateTime", "Animal ID"],
        kind="mergesort",
    )

    outcomes_for_matching = outcomes.sort_values(
        ["Outcome_DateTime", "Animal ID"],
        kind="mergesort",
    )

    matched_outcomes = pd.merge_asof(
    outcomes_for_matching,
    intakes_for_matching[
        [
            "Intake Event ID",
            "Animal ID",
            "Intake_DateTime",
        ]
    ],
    by="Animal ID",
    left_on="Outcome_DateTime",
    right_on="Intake_DateTime",
    direction="backward",
    allow_exact_matches=True,
)
    #Remove outcomes without a prior intake in 2024, since the intake may have occurred before 2024.
    matched_outcomes = matched_outcomes.dropna(
        subset=["Intake Event ID"]
    ).copy()
    
    #If one intake matches multiple outcomes, keep only the earliest outcome.
    matched_outcomes = matched_outcomes.sort_values(
    [
        "Intake Event ID",
        "Outcome_DateTime",
    ],
    kind="mergesort",
)
    matched_outcomes = matched_outcomes.drop_duplicates(
    subset=["Intake Event ID"],
    keep="first",
)

    matched_outcomes = matched_outcomes[
        [
            "Intake Event ID",
            "Outcome_DateTime",
            "Outcome Type",
            "Outcome Subtype",
            "Sex upon Outcome",
            "Age upon Outcome",
            "Outcome Date",
            "Outcome Time",
        ]
    ]

    Repeat_Intakes = intakes.merge(
        matched_outcomes,
        on="Intake Event ID",
        how="left",
    )

    Repeat_Intakes = Repeat_Intakes.sort_values(
        ["Animal ID", "Intake_DateTime"],
        kind="mergesort",
    ).reset_index(drop=True)

    columns = [
        "Intake Event ID",
        "Intake Event Number",
        "Animal ID",
        "Intake_DateTime",
        "Intake Date",
        "Intake Time",
        "Intake Type",
        "Found Location",
        "Intake Condition",
        "Animal Type",
        "Sex upon Intake",
        "Age upon Intake",
        "Breed",
        "Color",
        "Outcome_DateTime",
        "Outcome Date",
        "Outcome Time",
        "Outcome Type",
        "Outcome Subtype",
        "Sex upon Outcome",
        "Age upon Outcome",
    ]

    Repeat_Intakes = Repeat_Intakes[columns]

    Repeat_Intakes = Repeat_Intakes.sort_values(
        [
        "Animal ID",
        "Intake Event Number",
        ],
        kind="mergesort",
    ).reset_index(drop=True)

    Repeat_Intakes.to_csv(
        OUTPUT_PATH,
        index=False,
        date_format="%Y-%m-%d %H:%M:%S",
    )

if __name__ == "__main__":
    match_outcomes_to_intakes(
        intakes,
        outcomes,
    )