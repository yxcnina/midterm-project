import pandas as pd
import zipfile

zip_file=zipfile.ZipFile("data/raw/census_tract_income_2024.zip")

print(zip_file.namelist())

csv_file=zip_file.open("ACSDT5Y2024.B19013-Data.csv")
income=pd.read_csv(csv_file, skiprows=[1], dtype=str)

print(income.head())

print(income.shape)

income=income[["GEO_ID", "NAME", "B19013_001E", "B19013_001M"]]

income=income.drop_duplicates()

print("Rows after cleaning:", income.shape)

print("Unique Census tracts:", income["GEO_ID"].nunique())

print("Duplicate tract IDs:", income["GEO_ID"].duplicated().sum())

income["tract_geoid"]=income["GEO_ID"].str[-11:]

print(income[["GEO_ID", "tract_geoid"]].head())

income["income_raw"]=income["B19013_001E"]

income["median_income"]=pd.to_numeric(
    income["income_raw"].str.replace(",", "", regex=False),
    errors="coerce"
)

income.loc[income["median_income"] < 0, "median_income"] = float("nan")

income["income_status"]="numeric"

income.loc[
    income["median_income"].isna(),
    "income_status"
]="missing_or_special"

income.loc[
    income["income_raw"].str.endswith("+", na=False),
    "income_status"
]="above_upper_limit"

print(income["income_status"].value_counts())

income=income[
    ["tract_geoid", "NAME", "income_raw",
     "median_income", "B19013_001M", "income_status"]
]

income.to_csv(
    "data/processed/census_tract_income_2024.csv",
    index=False
)

print("Finished!")
print("Final rows:", len(income))

csv_file.close()
zip_file.close()

