
# Austin Weather Data Collection

## Overview

This module retrieves historical daily weather data for Austin, Texas, covering January 1 through December 31, 2024.

Weather data are collected from two sources:

1. NOAA NCEI Daily Summaries
2. Open-Meteo Historical Weather API

The datasets will be cleaned and merged by date in the subsequent data-processing stage.

## Data Sources

### NOAA

- Provider: National Oceanic and Atmospheric Administration (NOAA)
- Dataset: NCEI Daily Summaries
- Station: Austin Camp Mabry
- Station ID: USW00013958
- Period: January 1–December 31, 2024
- API: https://www.ncei.noaa.gov/access/services/data/v1

Variables:

| Variable | Description | Unit |
| --- | --- | --- |
| TMAX | Daily maximum temperature | °C |
| TMIN | Daily minimum temperature | °C |
| PRCP | Daily precipitation total | mm |

### Open-Meteo

- Provider: Open-Meteo
- Dataset: Historical Weather API
- Latitude: 30.3208
- Longitude: -97.7603
- Timezone: America/Chicago
- Period: January 1–December 31, 2024
- API: https://archive-api.open-meteo.com/v1/archive

Variables:

| Variable | Description | Unit |
| --- | --- | --- |
| relative_humidity_2m_mean | Daily mean relative humidity at 2 meters | % |
| cloud_cover_mean | Daily mean cloud cover | % |
| wind_speed_10m_max | Daily maximum wind speed at 10 meters | km/h |

## Reproducing the Data Collection

From the project root directory, run:

```bash
python3 code/weather/fetch_noaa.py
python3 code/weather/fetch_open_meteo.py
```

The scripts use Python's standard library and do not require additional packages.

## Raw Data Outputs

The scripts save their results to:

- `data/raw/noaa_austin_2024.json`
- `data/raw/open_meteo_austin_2024.json`

## Initial Validation

Both sources returned 366 daily observations for 2024.

The initial checks reported:

- No missing calendar dates
- No duplicate dates
- No missing requested weather fields or values

Further numerical and logical validation will be performed during data processing.

## Data Limitations

NOAA provides station-based weather observations, whereas Open-Meteo provides historical gridded weather estimates for the requested coordinates.

The two sources may differ in spatial coverage and daily measurement conventions.

Daily records should therefore be interpreted with attention to differences in observation windows and local time definitions.

The data collection stage preserves raw source values. Cleaning, harmonization, date merging, and derived variables are handled separately.


## Weather Data Processing

The script `process_weather.py` processes and combines daily
weather observations for Austin, Texas, in 2024.

### Processing Workflow

1. Load NOAA daily weather data from `data/raw/noaa_austin_2024.json`.
2. Load Open-Meteo daily weather data from `data/raw/open_meteo_austin_2024.json`.
3. Standardize column names and convert dates and weather variables to appropriate data types.
4. Merge both datasets using calendar dates with one-to-one validation.
5. Create three binary weather indicators.
6. Validate data completeness and logical consistency.
7. Export the processed dataset to `data/processed/austin_weather_2024.csv`.

### Processed Weather Variables

| Variable | Description |
| --- | --- |
| `date` | Calendar date (YYYY-MM-DD) |
| `temp_max_c` | Daily maximum temperature (°C) |
| `temp_min_c` | Daily minimum temperature (°C) |
| `precipitation_mm` | Daily precipitation (mm) |
| `humidity_mean_pct` | Daily mean relative humidity (%) |
| `cloud_cover_mean_pct` | Daily mean cloud cover (%) |
| `wind_speed_max_kmh` | Daily maximum wind speed (km/h) |
| `hot_day` | 1 if maximum temperature is at least 35°C; otherwise 0 |
| `freezing_day` | 1 if minimum temperature is at most 0°C; otherwise 0 |
| `wet_day` | 1 if daily precipitation is greater than 0 mm; otherwise 0 |

### Validation

The processed dataset contains 366 rows and 10 columns,
covering January 1 through December 31, 2024.

Validation checks confirm:

- All 366 calendar dates are present.
- No duplicated dates or missing values.
- Maximum temperature is not lower than minimum temperature.
- Precipitation and wind speed are nonnegative.
- Relative humidity and cloud cover are within 0–100%.
- Binary indicators are consistent with their definitions.

Weather indicator frequencies for 2024:

- Hot days: 101
- Freezing days: 7
- Wet days: 73

### Run the Processing Script

From the project root directory:

```bash
python3 code/weather/process_weather.py
```

The script validates the dataset before exporting the final CSV.

### Use in Event-Level Analysis

The processed weather dataset contains one observation per date.

It can be merged with cleaned animal intake and outcome event
datasets using their respective intake or outcome dates.

Because multiple animal events can occur on the same day,
these merges should use a many-to-one relationship.

Weather variables describe daily conditions associated with
event dates and should not be interpreted as proof of causation.
