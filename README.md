# Austin Animal Center Intakes in 2024
## Research Goal
This project studies stray-animal intakes at the Austin Animal Center (AAC) during 2024 by examining animal characteristics and shelter outcomes, repeat-intake patterns, neighborhood income and crime conditions, and weather-related intake patterns.


## Table of Contents
- [1. Research Questions and Analysis Modules](#1-research-questions-and-analysis-modules)
- [2. Data Resource](#2-data-resource)
- [3. Methodology](#3-methodology)
- [4. Main Findings](#4-main-findings)
- [5. Limitations](#5-limitations)
- [6. Extensions](#6-extensions)
- [7. Reproducing the Project](#7-reproducing-the-project)

## 1. Research Questions and Analysis Modules

This project examines stray-animal intakes at the Austin Animal Center in 2024 from five complementary perspectives. Each analysis module focuses on a different part of the intake process or the broader environment in which stray animals are found.

| Analysis Module | Main Research Question | Detailed Analysis |
|---|---|---|
| **Repeat Intakes** | How common are repeat intakes, how quickly do animals return, what are the most common return pathways, and what happens after they return? | [Repeat Intake Analysis](artifacts/README/README-repeat-intake-analysis.md) |
| **Animal Characteristics** | How are animal characteristics such as age, color, animal type, sex, breed, and intake condition associated with shelter outcomes? | [Animal Characteristics Analysis](artifacts/README/README-basic-analysis.md) |
| **Income & Found Location** | How do stray-animal intake patterns vary across areas with different income levels, and are animals found in different socioeconomic areas associated with different intake or outcome patterns? | [Income and Location Analysis](artifacts/README/README-income-analysis.md) |
| **Weather** | How are precipitation and temperature associated with AAC intake volume, intake and outcome composition, and differences between dogs and cats? | [Weather Analysis](artifacts/README/README-weather-analysis.md) |
| **Crime & Found Location** | Do areas with higher reported crime counts also tend to have more stray-animal intakes, and does this relationship remain after accounting for geographic and monthly differences? | [Crime and Location Analysis](artifacts/README/README-crime.md) |
## 2. Data Resource
<table>
<thead>
<tr>
<th>Analysis Module</th>
<th>Data Source</th>
<th>Source</th>
<th>Important Fields</th>
</tr>
</thead>
<tbody>
<tr>
<td rowspan="2"><strong>Repeat Intakes</strong></td>
<td>Austin Animal Center Intakes</td>
<td><a href="https://data.austintexas.gov/Health-and-Community-Services/Austin-Animal-Center-Intakes-10-01-2013-to-05-05-2/wter-evkm/about_data">City of Austin Open Data</a></td>
<td><code>Animal ID</code>, <code>DateTime</code>, <code>Intake Type</code>, <code>Intake Condition</code>, <code>Animal Type</code>, <code>Age upon Intake</code></td>
</tr>
<tr>
<td>Austin Animal Center Outcomes</td>
<td><a href="https://data.austintexas.gov/Health-and-Community-Services/Austin-Animal-Center-Outcomes-10-01-2013-to-05-05-/9t4d-g238/about_data">City of Austin Open Data</a></td>
<td><code>Animal ID</code>, <code>DateTime</code>, <code>Outcome Type</code>, <code>Outcome Subtype</code></td>
</tr>
<tr>
<td rowspan="2"><strong><mark>Animal Characteristics</mark></strong></td>
<td>Austin Animal Center Intakes</td>
<td><a href="https://data.austintexas.gov/Health-and-Community-Services/Austin-Animal-Center-Intakes-10-01-2013-to-05-05-2/wter-evkm/about_data">City of Austin Open Data</a></td>
<td><code>Animal ID</code>, <code>Animal Type</code>, <code>Age upon Intake</code>, <code>Color</code>, <code>Breed</code>, <code>Sex upon Intake</code>, <code>Intake Condition</code></td>
</tr>
<tr>
<td>Austin Animal Center Outcomes</td>
<td><a href="https://data.austintexas.gov/Health-and-Community-Services/Austin-Animal-Center-Outcomes-10-01-2013-to-05-05-/9t4d-g238/about_data">City of Austin Open Data</a></td>
<td><code>Animal ID</code>, <code>DateTime</code>, <code>Outcome Type</code>, <code>Outcome Subtype</code></td>
</tr>
<tr>
<td rowspan="3"><strong><mark>Income &amp; Found Location</strong></td>
<td>Austin Animal Center Intakes</td>
<td><a href="https://data.austintexas.gov/Health-and-Community-Services/Austin-Animal-Center-Intakes-10-01-2013-to-05-05-2/wter-evkm/about_data">City of Austin Open Data</a></td>
<td><code>Animal ID</code>, <code>Found Location</code>, <code>DateTime</code>, <code>Intake Type</code></td>
</tr>
<tr>
<td>U.S. Census Geocoder</td>
<td><a href="https://geocoding.geo.census.gov/geocoder/">U.S. Census Bureau</a></td>
<td><code>Latitude</code>, <code>Longitude</code>, <code>Census Tract</code>, <code>Census Block Group</code></td>
</tr>
<tr>
<td>American Community Survey (ACS)</td>
<td><a href="https://api.census.gov/data/2024/acs/acs5">U.S. Census Bureau ACS API</a></td>
<td><code>Population</code>, <code>Median Household Income</code>, Census geographic identifiers, and other socioeconomic variables used in the analysis</td>
</tr>
<tr>
<td rowspan="4"><strong>Weather</strong></td>
<td>Austin Animal Center Intakes</td>
<td><a href="https://data.austintexas.gov/Health-and-Community-Services/Austin-Animal-Center-Intakes-10-01-2013-to-05-05-2/wter-evkm/about_data">City of Austin Open Data</a></td>
<td><code>Animal ID</code>, <code>DateTime</code>, <code>Intake Type</code>, <code>Intake Condition</code>, <code>Animal Type</code></td>
</tr>
<tr>
<td>Austin Animal Center Outcomes</td>
<td><a href="https://data.austintexas.gov/Health-and-Community-Services/Austin-Animal-Center-Outcomes-10-01-2013-to-05-05-/9t4d-g238/about_data">City of Austin Open Data</a></td>
<td><code>Animal ID</code>, <code>DateTime</code>, <code>Outcome Type</code>, <code>Animal Type</code></td>
</tr>
<tr>
<td>NOAA Daily Weather Observations</td>
<td><a href="https://www.ncei.noaa.gov/support/access-data-service-api-user-documentation">NOAA NCEI Daily Summaries API</a></td>
<td><code>TMAX</code> (daily maximum temperature), <code>TMIN</code> (daily minimum temperature), <code>PRCP</code> (daily precipitation)</td>
</tr>
<tr>
<td>Open-Meteo Historical Weather Data</td>
<td><a href="https://open-meteo.com/en/docs/historical-weather-api">Open-Meteo Historical Weather API</a></td>
<td><code>relative_humidity_2m_mean</code>, <code>cloud_cover_mean</code>, <code>wind_speed_10m_max</code></td>
</tr>
<tr>
<td rowspan="3"><strong>Crime &amp; Found Location</strong></td>
<td>Austin Animal Center Intakes</td>
<td><a href="https://data.austintexas.gov/Health-and-Community-Services/Austin-Animal-Center-Intakes-10-01-2013-to-05-05-2/wter-evkm/about_data">City of Austin Open Data</a></td>
<td><code>Animal ID</code>, <code>Found Location</code>, <code>DateTime</code>, <code>Intake Type</code></td>
</tr>
<tr>
<td>Austin Crime Reports</td>
<td><a href="https://data.austintexas.gov/Public-Safety/Crime-Reports/fdj4-gpfu/about_data">City of Austin Open Data</a></td>
<td><code>Report Date</code>, <code>Offense</code>, <code>Census Block Group</code>, and other geographic or crime-category fields used in the analysis</td>
</tr>
<tr>
<td>American Community Survey (ACS)</td>
<td><a href="https://api.census.gov/data/2024/acs/acs5">U.S. Census Bureau ACS API</a></td>
<td><code>Population</code> and Census geographic identifiers used to construct population-adjusted crime measures</td>
</tr>
</tbody>
</table>

## 3. Methodology

### 3.1 Repeat-Intake Analysis
The repeat-intake analysis combines the cleaned 2024 AAC intake and outcome records into an episode-level dataset.

For each animal, intake events are ordered chronologically and assigned unique intake-event identifiers. Outcomes are then matched to the most recent preceding intake using `pandas.merge_asof()`. If multiple outcomes are matched to the same intake episode, only the earliest outcome is retained. Intake episodes without a matched outcome are kept in the dataset.

A repeat intake is defined as a new intake that occurs after the animal previously left AAC through one of the following outcome types:

- `Adoption`
- `Return to Owner`
- `Rto-Adopt`

Returns following `Transfer` or other outcome types are excluded from the main repeat-intake definition because those records may represent movement between organizations rather than a return from the community.

The analysis measures the share of repeat-intake episodes, time until return, return pathways, outcomes after return, and the number of observed intake episodes per animal.

[Read the full Repeat Intake Methodology →](artifacts/README/README-repeat-intake-analysis.md)
### <mark>3.2 Basic</mark>
### 3.3 Crime
The crime analysis combines 2024 Austin crime reports with geocoded AAC stray-intake records at the council-district level.

Reported crime incidents are obtained through the City of Austin Socrata API, while official council-district boundaries are downloaded through the City of Austin ArcGIS REST API. AAC records are restricted to `Stray` intakes, and observations referring to the shelter's own `7201 Levander` address are removed.

Each geocoded AAC intake is spatially matched to one official council-district polygon. Crime incidents and matched stray intakes are then counted separately by district and month, producing a complete dataset of 10 council districts × 12 months.

The analysis compares crime and stray-intake counts using:

- annual across-district correlations,
- unadjusted district-month regressions,
- regressions controlling for district and month differences,
- monthly daily-average trends.

These results are interpreted as descriptive associations rather than causal effects.

[Read the full Crime Analysis Methodology →](artifacts/README/README-crime.md)
### <mark>3.4 Income-Level
### <mark>3.5 Weather
The weather analysis combines cleaned 2024 Austin Animal Center (AAC) intake and outcome records with daily Austin weather observations from NOAA and Open-Meteo. NOAA provides daily maximum temperature, minimum temperature, and precipitation observations from station `USW00013958`, while Open-Meteo provides daily mean relative humidity, mean cloud cover, and maximum wind speed for the selected Austin coordinates.

The two weather datasets are standardized and merged one-to-one by calendar date to construct `austin_weather_2024.csv`. The processed dataset is validated for complete 2024 date coverage, duplicate dates, missing values, and consistency of weather measurements and indicators. AAC intake and outcome events are subsequently matched to the corresponding daily weather observations using their event dates.

Weather conditions are classified using daily precipitation and temperature:

- **Wet days:** Daily precipitation greater than 0 mm; dry days have zero precipitation.
- **Hot days:** Daily maximum temperature at least 35°C.
- **Cold days:** Daily minimum temperature at most 5°C.
- **Freezing days:** Daily minimum temperature at most 0°C.

Days not meeting each temperature threshold form the corresponding reference group.

The analysis uses four complementary approaches:

1. **Daily intake volume (Q1).** Intake events are aggregated into daily counts, and mean daily intakes are compared between wet and dry days. The main comparison includes 365 days with recorded intake activity, excluding December 25, 2024, for which no intake records are available. A sensitivity analysis additionally treats this missing date as a zero-intake day.

2. **Selected intake and outcome proportions (Q2–Q3).** The proportion of `Stray` intakes is compared between wet and dry days, while the proportion of `Adoption` outcomes is compared between hot and non-hot days. Both proportions are calculated from event counts within each weather group.

3. **Animal-type heterogeneity (Q4).** The daily intake, stray intake, and adoption outcome comparisons are repeated separately for dogs and cats. For daily counts, both animal types are evaluated over the same 365 recorded intake dates, assigning zero to an animal type on dates when AAC recorded intakes but none for that type. Stray and adoption proportions are calculated separately within each animal-type and weather group.

4. **Full event composition (Q5–Q7).** The analysis compares all six recorded intake types, all 16 intake conditions, and all nine non-missing outcome types across rainfall, extreme heat, cold weather, and freezing-day conditions. For each category, its share is calculated relative to all eligible intake or outcome events in the corresponding weather group.

Differences in category shares are reported in **percentage points**, calculated as the weather-exposed group's percentage minus the reference group's percentage. The extended composition analyses produce category-level summary tables and visualizations, including three heatmaps consolidating the four weather comparisons.

All weather-event matches are validated, and the analyses distinguish daily intake counts from event-level proportions. The results describe observed associations rather than causal effects, since weather conditions may coincide with seasonal variation, shelter operations, and other factors affecting recorded shelter activity.

[Read the full Weather Analysis Methodology →](code/weather_analysis/README.md)

## 4. Main Findings
### 4.1 Repeat Intakes

Repeat intakes were relatively uncommon in the 2024 AAC data. Repeat-intake episodes accounted for about **4.4% of all intake episodes**, while about **4.1% of unique animals** experienced at least one qualifying repeat intake.

![Scale of repeat intakes](artifacts/repeat-intake-analysis/figures/01_repeat_intake_share.png)

Most observed returns happened relatively quickly. About **86.9% of qualifying repeat intakes occurred within 90 days** of the previous outcome, and more than **72% occurred within the first 30 days**.

![Time until return](artifacts/repeat-intake-analysis/figures/02_return_time_distribution.png)

The most common return pathway was **Adoption → Owner Surrender**, which accounted for approximately **71.0% of qualifying repeat-intake episodes**. After a repeat intake, **70.6%** of episodes were followed by another adoption.

Most repeat-intake animals returned only once during 2024: about **89%** had exactly two observed intake episodes.

[Read the full Repeat Intake Findings →](artifacts/README/README-repeat-intake-analysis.md)
### <mark>4.2 Basic
### 4.3 Crime
Across Austin's 10 council districts, districts with higher annual reported crime counts also tended to have more matched stray-animal intakes. The annual Pearson correlation between crime counts and stray-intake counts was **r = 0.6183**.

![Annual crime and stray-intake relationship](artifacts/crime/analysis/annual_district_scatter.png)

In the unadjusted district-month regression, an additional **100 reported crimes** was associated with approximately **6.09 additional geocoded stray intakes**.

However, the relationship became substantially weaker after controlling for persistent differences across districts and common monthly patterns. The adjusted estimate fell to approximately **3.54 additional stray intakes per 100 crimes**, with a district-clustered **p-value of 0.4029** and an approximate 95% confidence interval of **[-5.58, 12.66]**.

![Adjusted crime and stray-intake relationship](artifacts/crime/analysis/adjusted_within_district_month.png)

Overall, the raw data show a positive relationship between crime counts and stray-animal intakes across districts, but the evidence becomes much weaker after accounting for district and month differences. The results therefore do not support a causal interpretation that crime increases stray-animal intake.
### <mark>4.4 Income-Level
### <mark>4.5 Weather
The weather analysis reveals several descriptive differences in Austin Animal Center (AAC) intake and outcome patterns across rainfall and temperature conditions during 2024. The findings cover daily intake volume, stray intake and adoption outcome proportions, differences between dogs and cats, and the broader composition of intake and outcome events.

**Rainfall and Daily Intake Volume (Q1).** Average daily intake counts were **32.57 on dry days** and **31.56 on wet days**, a difference of approximately **1.01 fewer intake events per day on wet days**. The difference was relatively small compared with the variation in daily intake counts within each group. Treating the one date without recorded intakes as a zero-intake day did not change the direction of this comparison.

**Rainfall and Stray Intake Proportions (Q2).** Stray intakes represented **68.90% of intake events on dry days**, compared with **72.01% on wet days**, a **3.11-percentage-point increase**. Thus, although the average daily intake count was slightly lower on wet days, stray animals accounted for a larger share of recorded intakes.

**Extreme Heat and Adoption Outcome Proportions (Q3).** Adoptions represented **61.95% of valid outcome events on non-hot days** and **65.11% on hot days**, a **3.16-percentage-point increase**. This measures the composition of recorded shelter outcomes, not the probability that an individual animal entering AAC will eventually be adopted.

**Animal-Type Heterogeneity (Q4).** Separate comparisons for dogs and cats reveal that the aggregate weather-related patterns are not uniform across animal types.

- **Daily intake volume (Q4a):** Average daily dog intakes decreased from **14.31 on dry days to 13.81 on wet days**, while average daily cat intakes decreased from **16.60 to 16.43**. Both differences were modest.
- **Stray intake proportions (Q4b):** The stray share increased from **60.01% to 64.19% for dogs** (**+4.18 percentage points**) but from **81.72% to 82.33% for cats** (**+0.61 percentage points**). The wet-day increase was therefore more pronounced among dogs, although cats had a higher stray intake share under both weather conditions.
- **Adoption outcome proportions (Q4c):** The adoption share increased from **65.83% to 67.28% for dogs** (**+1.45 percentage points**) and from **61.65% to 67.20% for cats** (**+5.55 percentage points**) between non-hot and hot days. The hot-day difference was substantially larger among cats.

![Adoption outcome proportions for dogs and cats](artifacts/weather_analysis/figures/04_animal_type/q4c_adoption_proportions_by_animal_type.png)

These findings suggest that aggregate weather comparisons can conceal meaningful descriptive differences between animal groups.

**Intake Type Composition (Q5).** Extending the analysis to all six intake types reveals differences across rainfall, heat, cold, and freezing conditions. The `Stray` share was **3.11 percentage points higher on wet days** but **11.12 percentage points lower on cold days**. On cold days, `Owner Surrender` and `Public Assist` represented larger shares of intake events, increasing by **6.53** and **3.22 percentage points**, respectively. In contrast, the stray intake share was nearly identical between hot and non-hot days.

![Weather-related differences in intake type composition](artifacts/weather_analysis/figures/summary_heatmaps/q5_intake_type_summary_heatmap.png)

**Intake Condition Composition (Q6).** The distribution of recorded intake conditions was broadly similar between wet and dry days, but more noticeable differences appeared under extreme heat. On hot days, the share of intakes classified as `Normal` was **6.12 percentage points lower**, while the shares classified as `Sick` and `Neonatal` were **2.54** and **2.30 percentage points higher**, respectively, compared with non-hot days.

![Weather-related differences in intake condition composition](artifacts/weather_analysis/figures/summary_heatmaps/q6_intake_condition_summary_heatmap.png)

**Outcome Type Composition (Q7).** Across the nine non-missing outcome categories, the adoption share was higher in the weather-exposed group in all four comparisons: **+1.21 percentage points on wet days**, **+3.16 on hot days**, **+4.02 on cold days**, and **+6.38 on freezing days**, relative to their respective reference groups. On cold days, the `Transfer` share was also **5.63 percentage points lower** than on non-cold days. The freezing-day results require particular caution because they are based on only **185 valid outcome events**.

![Weather-related differences in outcome type composition](artifacts/weather_analysis/figures/summary_heatmaps/q7_outcome_type_summary_heatmap.png)

**Overall Interpretation.** Weather conditions are associated with differences in AAC intake volume, intake composition, recorded intake conditions, and outcome composition. These relationships vary across weather indicators and animal types. Rainfall-related differences in daily intake volume were modest, while some temperature-related differences in event composition were more pronounced.

All findings are **descriptive rather than causal**. Seasonal variation, shelter operations, differences in weather-group sample sizes, and other unobserved factors may contribute to the observed patterns.

[Read the full Weather Analysis Findings →](code/weather_analysis/README.md)

## 5. Limitations
This project has several important limitations.
1. The main analysis is limited to 2024.
   Events occurring before or after the study period may not be captured. For example, an animal may have entered AAC before 2024 or had an outcome after 2024.
2. AAC data do not represent all stray animals in Austin.
   The datasets include animals that entered the Austin Animal Center system. Animals handled by other organizations, reunited with owners without entering AAC, or remaining outside the shelter system are not observed.
3. Some important behavioral information is unavailable.
   The datasets generally do not include detailed owner identity, reasons for surrender or return, or the motivations behind adoption decisions.
4. Found-location data are incomplete or imprecise for some animals.
   Some Found Location records cannot be reliably mapped to a specific Census geography, reducing the sample available for neighborhood-level analysis.
5. Neighborhood-level relationships are descriptive.
   Associations between income, crime, weather, and animal intake patterns should not be interpreted as causal effects.
## 6. Extensions
This project could be extended in several directions:
1. Use multiple years of AAC intake and outcome data.
   A longer time period would provide more complete animal histories and allow long-term trends to be studied.
2. Improve geographic matching.
   Better address cleaning or alternative geocoding methods could increase the share of Found Location records matched to Census geography.
3. Include additional socioeconomic variables.
   Future work could consider renter share, poverty rates, housing characteristics, or other neighborhood variables in addition to income.
4. Use richer animal-history data.
   More detailed owner information, surrender reasons, or adoption-history information would allow stronger interpretation of repeat-intake patterns.
5. Include animals outside the AAC system.
   Data from other shelters or animal-service organizations could provide a more complete picture of stray animals in the Austin area.
6. Study changes over time.
   Multi-year data could be used to examine whether intake patterns, neighborhood relationships, or repeat-intake rates have changed.
## 7. Reproducing the Project
### 7.1 Create and Activate a Virtual Environment
On macOS/Linux:
```
python3 -m venv .venv
source .venv/bin/activate
```
### 7.2 Install Dependencies
```
python -m pip install -r requirements.txt
```
### 7.3 Obtain the Raw Data
The raw CSV files of intakes and outcomes are placed in data/raw folder, and the websites for downloading the raw data are listed below:
* Austin Animal Center Intakes: https://data.austintexas.gov/Health-and-Community-Services/Austin-Animal-Center-Intakes-10-01-2013-to-05-05-2/wter-evkm/about_data
* Austin Animal Center Outcomes: https://data.austintexas.gov/Health-and-Community-Services/Austin-Animal-Center-Outcomes-10-01-2013-to-05-05-/9t4d-g238/about_data
### <mark>7.4 Clean the AAC Data and 
Run the two cleaning scripts:
``` 
python code/data_cleaning/clean_aac_intake.py
python code/data_cleaning/clean_aac_outcomes.py
```
These scripts create:
``` 
data/processed/aac_intakes_clean.csv
data/processed/aac_outcomes_clean.csv
```
### 7.5 Run the Analysis Modules
Repeat Intake Analysis
```
python code/repeat_intakes_analysis/aac_in-out-episodes_2024.py
python code/repeat_intakes_analysis/repeat-intakes-analysis.py
```
Detailed instructions:
[Repeat Intake README](artifacts/README/README-repeat-intake-analysis.md)
