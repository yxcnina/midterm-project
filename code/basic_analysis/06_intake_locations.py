"""Map recorded intake locations and summarize selective geocoding coverage."""

from math import cos, radians
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import LogNorm

ANIMALS = ["Cat", "Dog"]
EVENT_KEY = ["Animal ID", "Intake Date", "Intake Time", "Intake Type"]
SHELTER_ADDRESS = "7201 Levander Loop Bldg. A"
SHELTER_SOURCE = "https://www.austintexas.gov/animal-services/contact"


def read_intakes(data_folder):
    """Read full/geocoded intake CSVs; return verified event-level DataFrames."""
    intakes = pd.read_csv(
        data_folder / "aac_intakes_clean.csv", dtype=str, keep_default_na=False
    )
    locations = pd.read_csv(
        data_folder / "aac_intakes_clean_geocoded.csv",
        dtype=str,
        keep_default_na=False,
    )
    dates = pd.to_datetime(intakes["Intake Date"], format="%Y-%m-%d")
    if not dates.dt.year.eq(2024).all():
        raise ValueError("This analysis expects the cleaned 2024 intake file.")
    if intakes.duplicated(EVENT_KEY).any() or locations.duplicated(EVENT_KEY).any():
        raise ValueError("The intake event keys must be unique in both files.")

    matched = locations.merge(
        intakes,
        on=EVENT_KEY,
        how="left",
        suffixes=("_geo", "_full"),
        indicator=True,
        validate="one_to_one",
    )
    if not matched["_merge"].eq("both").all():
        raise ValueError("Some geocoded events are absent from the full intake file.")
    shared_columns = (set(intakes.columns) & set(locations.columns)) - set(EVENT_KEY)
    for column in shared_columns:
        if not matched[f"{column}_geo"].eq(matched[f"{column}_full"]).all():
            raise ValueError(f"The input files disagree on {column}.")

    locations["longitude"] = pd.to_numeric(locations["longitude"])
    locations["latitude"] = pd.to_numeric(locations["latitude"])
    valid_longitude = locations["longitude"].between(-180, 180)
    valid_latitude = locations["latitude"].between(-90, 90)
    if not (valid_longitude & valid_latitude).all():
        raise ValueError("The geocoded file contains invalid coordinates.")
    return intakes, locations


def shelter_address_mask(data):
    """Return rows with the shelter's street number/name, including known typos."""
    return data["Found Location"].str.match(
        r"^7201 (?:Levander|Levadner|Levender)(?:\s|$)", case=False
    )


def shelter_coordinates(locations):
    """Return the unique geocode of the exact shelter address, or raise."""
    exact_address = locations["Found Location"].eq("7201 Levander Loop in Austin (TX)")
    shelter = locations.loc[exact_address, ["longitude", "latitude"]].drop_duplicates()
    if len(shelter) != 1:
        raise ValueError("Check the shelter reference geocode before plotting.")
    return tuple(shelter.iloc[0])


def summarize_locations(intakes, locations, table_folder):
    """Save aggregate coverage/precision tables; return the shelter coordinates."""
    coverage_rows = []
    intake_type_rows = []
    precision_rows = []
    for animal in ["All animals", *ANIMALS]:
        full = intakes
        mapped = locations
        if animal != "All animals":
            full = intakes.loc[intakes["Animal Type"].eq(animal)]
            mapped = locations.loc[locations["Animal Type"].eq(animal)]
        coverage_rows.append(
            {
                "animal_type": animal,
                "intake_records": len(full),
                "geocoded_records": len(mapped),
                "not_geocoded_records": len(full) - len(mapped),
                "coverage_percent": 100 * len(mapped) / len(full),
            }
        )
        for intake_type, group in full.groupby("Intake Type"):
            mapped_count = mapped["Intake Type"].eq(intake_type).sum()
            intake_type_rows.append(
                {
                    "animal_type": animal,
                    "intake_type": intake_type,
                    "intake_records": len(group),
                    "geocoded_records": mapped_count,
                    "coverage_percent": 100 * mapped_count / len(group),
                }
            )
        for precision, group in mapped.groupby("location_precision"):
            precision_rows.append(
                {
                    "animal_type": animal,
                    "location_precision": precision,
                    "geocoded_records": len(group),
                    "geocoded_denominator": len(mapped),
                    "percent": 100 * len(group) / len(mapped),
                }
            )

    tables = {
        "coverage_by_species.csv": coverage_rows,
        "coverage_by_intake_type.csv": intake_type_rows,
        "location_precision.csv": precision_rows,
    }
    for filename, rows in tables.items():
        pd.DataFrame(rows).to_csv(table_folder / filename, index=False)

    # Use the existing geocodes of the exact address, not a guessed GPS location.
    longitude, latitude = shelter_coordinates(locations)
    reference = pd.DataFrame(
        [
            {
                "address": SHELTER_ADDRESS,
                "longitude": longitude,
                "latitude": latitude,
                "address_source": SHELTER_SOURCE,
                "coordinate_source": "Existing geocodes of the exact shelter address",
            }
        ]
    )
    reference.to_csv(table_folder / "shelter_reference.csv", index=False)
    return longitude, latitude


def plot_locations(intakes, locations, shelter, figure_folder, table_folder):
    """Save two paired hexbin maps and their aggregate spatial audit table."""
    pets = locations.loc[locations["Animal Type"].isin(ANIMALS)].copy()
    pets["Shelter address"] = shelter_address_mask(pets)
    extent = (
        pets["longitude"].min() - 0.02,
        pets["longitude"].max() + 0.02,
        pets["latitude"].min() - 0.02,
        pets["latitude"].max() + 0.02,
    )
    aspect = 1 / cos(radians(pets["latitude"].mean()))
    figures = []
    collections = []
    audit_rows = []
    variants = {
        "all_records": "Recorded found locations in 2024",
        "without_shelter_address": (
            "Recorded locations excluding shelter-address labels"
        ),
    }
    for variant, title in variants.items():
        figure, axes = plt.subplots(1, 2, figsize=(11, 6.8), sharex=True, sharey=True)
        for axis, animal in zip(axes, ANIMALS):
            mapped = pets.loc[pets["Animal Type"].eq(animal)]
            total = intakes["Animal Type"].eq(animal).sum()
            plotted = mapped
            if variant == "without_shelter_address":
                plotted = mapped.loc[~mapped["Shelter address"]]
            collection = axis.hexbin(
                plotted["longitude"],
                plotted["latitude"],
                gridsize=40,
                extent=extent,
                mincnt=1,
                cmap="YlOrRd",
                linewidths=0.2,
            )
            collections.append(collection)
            axis.scatter(
                *shelter,
                marker="*",
                s=110,
                color="royalblue",
                edgecolor="black",
                linewidth=0.5,
                label="Austin Animal Center",
                zorder=3,
            )
            axis.set_title(
                f"{animal}s: {len(plotted):,} records shown\n"
                f"Geocoded: {len(mapped):,}/{total:,} ({len(mapped) / total:.1%})"
            )
            axis.set_xlabel("Longitude")
            axis.set_ylabel("Latitude")
            axis.set_xlim(extent[:2])
            axis.set_ylim(extent[2:])
            axis.set_aspect(aspect)
            axis.ticklabel_format(useOffset=False)
            audit_rows.append(
                {
                    "map_variant": variant,
                    "animal_type": animal,
                    "geocoded_records": len(mapped),
                    "plotted_records": len(plotted),
                    "excluded_shelter_address_records": len(mapped) - len(plotted),
                    "shelter_address_records": int(mapped["Shelter address"].sum()),
                    "omitted_outside_extent": 0,
                    "minimum_longitude": mapped["longitude"].min(),
                    "maximum_longitude": mapped["longitude"].max(),
                    "minimum_latitude": mapped["latitude"].min(),
                    "maximum_latitude": mapped["latitude"].max(),
                    "largest_hexagon_count": int(collection.get_array().max()),
                }
            )
            if int(collection.get_array().sum()) != len(plotted):
                raise ValueError("The map bins do not include every plotted record.")
        figure.suptitle(title, fontsize=14)
        figure.legend(
            *axes[0].get_legend_handles_labels(),
            loc="upper center",
            bbox_to_anchor=(0.5, 0.93),
            frameon=False,
        )
        figure.subplots_adjust(left=0.07, right=0.85, top=0.85, bottom=0.19, wspace=0.2)
        figures.append((variant, figure, collection))

    maximum = max(collection.get_array().max() for collection in collections)
    for collection in collections:
        collection.set_norm(LogNorm(vmin=1, vmax=maximum))
    for variant, figure, collection in figures:
        colorbar_axis = figure.add_axes([0.88, 0.24, 0.02, 0.55])
        colorbar = figure.colorbar(collection, cax=colorbar_axis)
        ticks = [value for value in [1, 3, 10, 30, 100] if value <= maximum]
        colorbar.set_ticks(ticks)
        colorbar.set_ticklabels([str(value) for value in ticks])
        colorbar.set_label("Records per hexagon (log scale)")
        figure.text(
            0.07,
            0.105,
            "Coordinate density maps; no basemap. Same extent, bins and count scale. "
            "No points outside the extent.",
            fontsize=9,
        )
        figure.text(
            0.07,
            0.072,
            "Locations represent recorded Found Location text, not owner addresses, "
            "outcome destinations or GPS observations.",
            fontsize=9,
        )
        note = "Only geocoded records are shown; coverage differs by intake type."
        if variant == "without_shelter_address":
            excluded = int(pets["Shelter address"].sum())
            excluded_cats = int(
                (pets["Shelter address"] & pets["Animal Type"].eq("Cat")).sum()
            )
            excluded_dogs = excluded - excluded_cats
            note = (
                f"Excluded {excluded} shelter-address records "
                f"({excluded_cats} cats; {excluded_dogs} dogs). "
                "All other geocoded records remain."
            )
        figure.text(0.07, 0.039, note, fontsize=9)
        filename = f"intake_locations_{variant}.png"
        figure.savefig(figure_folder / filename, dpi=150)
        plt.close(figure)
    pd.DataFrame(audit_rows).to_csv(table_folder / "spatial_audit.csv", index=False)


def main():
    """Read existing intake files and write theme 06 aggregate tables and PNGs."""
    root = Path(__file__).resolve().parents[2]
    output = root / "artifacts" / "basic_analysis"
    figure_folder = output / "figures" / "06_intake_locations"
    table_folder = output / "tables" / "06_intake_locations"
    figure_folder.mkdir(parents=True, exist_ok=True)
    table_folder.mkdir(parents=True, exist_ok=True)

    intakes, locations = read_intakes(root / "data" / "processed")
    shelter = summarize_locations(intakes, locations, table_folder)
    plot_locations(intakes, locations, shelter, figure_folder, table_folder)
    print(f"Geocoded intake records: {len(locations):,}/{len(intakes):,}")
    print("Saved theme 06 coordinate maps and aggregate tables.")


if __name__ == "__main__":
    main()
