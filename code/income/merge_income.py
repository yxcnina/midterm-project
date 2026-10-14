import pandas as pd
import geopandas as gpd

pets=pd.read_csv(
    "data/processed/aac_intakes_clean_geocoded.csv")

income=pd.read_csv(
    "data/processed/census_tract_income_2024.csv",
    dtype={"tract_geoid": str})

tracts=gpd.read_file(
    "data/raw/tl_2024_48_tract.zip")

print("Pets:", len(pets))
print("Income:", len(income))
print("Tracts:", len(tracts))

print("Pet columns:")
print(pets.columns.tolist())

print("Tract data:")
print(tracts[["GEOID", "NAME"]].head())

print("Coordinate system:", tracts.crs)

points=gpd.GeoDataFrame(
    pets,
    geometry=gpd.points_from_xy(pets["longitude"], pets["latitude"]),
    crs="EPSG:4326")

points=points.to_crs(tracts.crs)

tracts=tracts[["GEOID", "geometry"]]

matched=gpd.sjoin(
    points,
    tracts,
    how="left",
    predicate="within")

matched=matched.rename(columns={"GEOID": "tract_geoid"})

print("Original pets:", len(pets))
print("After matching:", len(matched))
print("Matched tracts:", matched["tract_geoid"].notna().sum())
print("Missing tracts:", matched["tract_geoid"].isna().sum())

print(matched[["Animal ID", "tract_geoid"]].head())

matched=pd.merge(
    matched,
    income[["tract_geoid", "median_income", "income_status"]],
    on="tract_geoid",
    how="left",
    validate="many_to_one")

print("After income merge:", len(matched))

print("Valid incomes:", matched["median_income"].notna().sum())

print(matched["income_status"].value_counts(dropna=False))

print(
    matched[["Animal ID", "tract_geoid", "median_income"]].head())

intakes = pd.read_csv(
    "data/processed/aac_intakes_clean.csv")

keys=[
    "Animal ID",
    "Intake Date",
    "Intake Time",
    "Intake Type"]

income_data=matched[
    keys + ["tract_geoid", "median_income", "income_status"]]

print("Duplicate events:", income_data.duplicated(subset=keys).sum())

complete=pd.merge(
    intakes,
    income_data,
    on=keys,
    how="left",
    validate="one_to_one")

print("Original intakes:", len(intakes))
print("Final records:", len(complete))

print("Matched tracts:", complete["tract_geoid"].notna().sum())
print("Valid incomes:", complete["median_income"].notna().sum())

complete.to_csv(
    "data/processed/aac_intakes_with_income_2024.csv",
    index=False)

print("Income dataset saved successfully!")

episodes=pd.read_csv(
    "data/processed/aac_in-out-episodes_2024.csv")

income_info=complete[
    keys + ["tract_geoid", "median_income", "income_status"]]

final_data=pd.merge(
    episodes,
    income_info,
    on=keys,
    how="left",
    validate="one_to_one")

print("Original episodes:", len(episodes))
print("Final episodes:", len(final_data))
print("Valid incomes:", final_data["median_income"].notna().sum())

final_data.to_csv(
    "data/processed/aac_intake_outcomes_with_income_2024.csv",
    index=False)

print("Final dataset saved successfully!")