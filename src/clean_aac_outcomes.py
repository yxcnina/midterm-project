import os
import pandas as pd

IN_PATH = os.path.join(
    "data",
    "raw",
    "Austin_Animal_Center_Outcomes.csv",
)

OUTPUT_DIR = os.path.join("data", "processed")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "aac_outcomes_clean.csv")

outcomes = pd.read_csv(IN_PATH)

start_date = "2024-01-01"
end_date = "2025-01-01"

def convert_datetime(outcomes):
    outcomes = outcomes.copy()
    outcomes["DateTime"] = pd.to_datetime(
        outcomes["DateTime"]
        .astype("string")
        .str[:19],
        format="%Y-%m-%dT%H:%M:%S",
        errors= "coerce")
    return outcomes


def filter_2024(outcomes):
    is_2024 = (
        (outcomes["DateTime"] >= start_date)
        & (outcomes["DateTime"] < end_date)
    )
    return outcomes.loc[is_2024].copy()

def remove_duplicates(outcomes):
    event_key = [
        "Animal ID",
        "Date of Birth",
        "DateTime",
        "Outcome Type",
        "Outcome Subtype"
    ]

    outcomes = outcomes.sort_values(
            event_key,
            kind="mergesort",
        )

    return outcomes.drop_duplicates(
            subset=event_key,
            keep="first",
        ).copy()


def split_datetime(outcomes):
    outcomes = outcomes.copy()
    outcomes["Outcome Date"] = (
        outcomes["DateTime"]
        .dt.strftime("%Y-%m-%d")
    )
    outcomes["Outcome Time"] = (
        outcomes["DateTime"]
        .dt.strftime("%H:%M:%S")
    )
    return outcomes    

if __name__ == "__main__":
    outcomes = convert_datetime(outcomes)
    outcomes = outcomes.sort_values(
            by = ["DateTime"],
            ascending= True
        )
    outcomes_2024 = filter_2024(outcomes)
    outcomes_2024 = remove_duplicates(outcomes_2024)
    # delete useless columns
    outcomes_2024 = outcomes_2024.drop(
        columns=["Name", "MonthYear"],
    ).copy()
    outcomes_2024 = split_datetime(outcomes_2024)

    outcomes_2024.to_csv(
        OUTPUT_PATH,
        index = False,
        date_format="%Y-%m-%d %H:%M:%S"
    )

