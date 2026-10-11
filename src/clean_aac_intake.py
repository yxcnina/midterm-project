import os
import pandas as pd 

IN_PATH = os.path.join(
    "data",
    "raw",
    "Austin_Animal_Center_Intakes.csv",
)

OUTPUT_DIR = os.path.join("data", "processed")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "aac_intakes_clean.csv")

intakes = pd.read_csv(IN_PATH)

start_date = "2024-01-01"
end_date = "2025-01-01"

def convert_datetime(intakes):
    intakes = intakes.copy()
    intakes["DateTime"] = pd.to_datetime(
        intakes["DateTime"],
        format="%m/%d/%Y %I:%M:%S %p",
        errors= "coerce")
    return intakes

# check if there is NaT
# intakes = convert_datetime(intakes)
# print(intakes[intakes["DateTime"].isna()])

def filter_2024(intakes):
    is_2024 = (
        (intakes["DateTime"] >= start_date)
        & (intakes["DateTime"] < end_date)
    )
    return intakes.loc[is_2024].copy()

def remove_duplicates(intakes):
    event_key = [
        "Animal ID",
        "DateTime",
        "Intake Type",
    ]

    intakes = intakes.sort_values(
        event_key,
        kind="mergesort",
    )

    return intakes.drop_duplicates(
        subset=event_key,
        keep="first",
    ).copy()

def split_datetime(intakes):
    intakes = intakes.copy()
    intakes["Intake Date"] = (
        intakes["DateTime"]
        .dt.strftime("%Y-%m-%d")
    )
    intakes["Intake Time"] = (
        intakes["DateTime"]
        .dt.strftime("%H:%M:%S")
    )
    intakes = intakes.drop(
        columns=["DateTime"]
    )
    return intakes    

if __name__ == "__main__":
    intakes = convert_datetime(intakes)
    intakes = intakes.sort_values(
            by = ["DateTime"],
            ascending= True
        )
    intakes_2024 = filter_2024(intakes)
    intakes_2024 = remove_duplicates(intakes_2024)
    intakes_2024 = split_datetime(intakes_2024)
    # delete useless columns
    intakes_2024 = intakes_2024.drop(
        columns=["Name", "MonthYear"],
    ).copy()

    intakes_2024.to_csv(
        OUTPUT_PATH,
        index = False,
        date_format="%Y-%m-%d"
    )

