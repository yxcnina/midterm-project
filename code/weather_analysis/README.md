# Weather and Animal Intake/Outcome Descriptive Analysis

## Research Overview

This analysis examines descriptive associations between weather conditions and animal intake and outcome events recorded by the Austin Animal Center in 2024.

Three research questions are considered:

1. Do wet days have different average daily animal intake counts compared with dry days?
2. Does the proportion of stray intake events differ between wet and dry days?
3. Does the proportion of adoption outcomes differ between hot and non-hot days?

The analyses focus on observed differences in daily event counts and event-type proportions. They do not attempt to establish causal relationships.

## Research Question 1: Rainfall and Daily Animal Intake Counts

### Data and Methodology

We use the cleaned Austin Animal Center intake dataset for 2024, containing 11,815 intake records, together with daily precipitation data from NOAA.

Individual intake events are aggregated by calendar date to construct daily intake counts. These counts are merged with the daily weather dataset by date. Wet days are defined as days with precipitation greater than 0 mm, while dry days are defined as days with zero precipitation.

The main analysis compares the mean, median, and standard deviation of daily intake counts between wet and dry days.

The cleaned intake dataset contains recorded events on 365 of the 366 calendar days in 2024. December 25 has no recorded intake events and is excluded from the main analysis because an absence of records does not necessarily indicate zero actual intakes. A sensitivity analysis treats this date as a zero-intake day.

### Findings

The main analysis includes 293 dry days and 72 wet days.

| Statistic | Dry Days | Wet Days |
|---|---:|---:|
| Number of days | 293 | 72 |
| Total intake events | 9,543 | 2,272 |
| Mean daily intakes | 32.57 | 31.56 |
| Median daily intakes | 32 | 33 |
| Standard deviation | 16.42 | 14.78 |

The average daily intake count is approximately 1.01 events lower on wet days than on dry days. However, the difference is small compared with the day-to-day variation observed within each group.

The median daily intake count is slightly higher on wet days, suggesting that the two groups have broadly similar typical daily intake volumes.

**Figure 1. Average Daily Animal Intakes on Dry and Wet Days (2024)**

![Average Daily Animal Intakes on Dry and Wet Days](../../artifacts/weather_analysis/figures/01_daily_intakes/wet_vs_dry_daily_intakes.png)

The figure compares the average number of recorded daily animal intakes
between dry and wet days. The vertical axis begins at zero to avoid
visually exaggerating the small difference between the two groups. 

**Figure 2. Distribution of Daily Animal Intake Counts on Dry and Wet Days (2024)**

![Daily Animal Intake Distribution on Dry and Wet Days](../../artifacts/weather_analysis/figures/01_daily_intakes/wet_vs_dry_daily_intakes_boxplot.png)

To complement the comparison of group means, the boxplot examines the distribution of daily intake counts across dry and wet days. The boxes represent the interquartile ranges (IQRs), the horizontal lines inside the boxes indicate the medians, and the diamond markers represent the means. Points beyond the whiskers indicate potential outliers under the 1.5 × IQR rule.

The two distributions overlap substantially. The median daily intake count is 32 on dry days and 33 on wet days, suggesting that typical daily intake volumes are similar across the two weather categories.

Dry days exhibit slightly greater overall variability, with a standard deviation of 16.42 compared with 14.78 on wet days. Several unusually high daily intake counts appear as outliers on dry days, whereas no similarly high outliers are identified on wet days.

Overall, the boxplot supports the interpretation of the original mean comparison: recorded daily intake volumes do not exhibit a pronounced descriptive difference between wet and dry days. However, these comparisons do not establish that precipitation has no effect on animal intake activity.

The boxplot uses the same 365 recorded intake days as the main analysis (293 dry days and 72 wet days), excluding December 25, 2024, because no intake records are available for that date. 

### Sensitivity Analysis

When December 25 is treated as a day with zero intake events, the number of wet days increases from 72 to 73, and the wet-day mean decreases from 31.56 to 31.12. The dry-day mean remains unchanged at 32.57.

The wet-minus-dry mean difference therefore changes from approximately −1.01 to −1.45 daily intake events.

The direction of the descriptive comparison remains unchanged under this alternative assumption.

### Limitations

This analysis is descriptive and cannot establish that rainfall causes changes in animal intake counts.

Differences in seasonality, weekdays, holidays, and shelter operations may influence recorded intake patterns. The absence of intake records on December 25 cannot be interpreted with certainty as zero actual events.

Furthermore, the binary wet-day indicator does not distinguish between light precipitation and heavy rainfall. Weather measurements also reflect conditions at the selected Austin weather station rather than every location where animals were found.

### Possible Extensions

Future research could examine precipitation intensity, account for seasonal and weekday differences, and investigate whether associations vary by animal type or intake category.

### Reproducibility

Run the analysis from the project root directory:

```bash
python3 code/weather_analysis/analyze_daily_intakes.py
```

This script reproduces the Q1 descriptive statistics, sensitivity analysis, and figure using the cleaned intake and processed weather data.

The generated outputs are:

- `artifacts/weather_analysis/figures/01_daily_intakes/wet_vs_dry_daily_intakes.png`
- `artifacts/weather_analysis/tables/q1_daily_intakes_summary.csv`

The required Python packages are listed in the project's root `requirements.txt` file. 


## Research Question 2: Rainfall and Stray Intake Proportions

### Data and Methodology 

This analysis examines whether the proportion of stray animal intake events differs between wet and dry days in Austin during 2024.

We use the cleaned Austin Animal Center intake dataset, containing 11,815 intake events, together with the daily weather dataset derived from NOAA observations.

Unlike Research Question 1, which aggregates intake events into daily counts, this analysis uses individual intake events as the unit of observation.

Each intake event is matched to its corresponding daily weather record using the intake date. The matching procedure uses a many-to-one relationship because multiple intake events can occur on the same calendar date, while each date has a single weather record.

Wet days are defined as days with precipitation greater than 0 mm, and dry days are defined as days with zero precipitation.

A binary indicator, `is_stray`, is created:

- `is_stray = 1` if the intake event is classified as `Stray`.
- `is_stray = 0` for all other intake types.

For each weather category, the stray intake proportion is calculated by dividing the number of stray intake events by the total number of intake events in that category.

All 11,815 intake events were successfully matched to weather records. No unmatched intake dates or duplicate weather dates were detected.

### Findings

The event-level analysis produces the following results:

| Statistic | Dry Days | Wet Days |
|---|---:|---:|
| Total intake events | 9,543 | 2,272 |
| Stray intake events | 6,575 | 1,636 |
| Non-stray intake events | 2,968 | 636 |
| Stray intake proportion | 68.90% | 72.01% |

The proportion of stray intake events was approximately **68.90% on dry days**, compared with **72.01% on wet days**.

The wet-minus-dry difference was approximately **3.11 percentage points**.

Thus, among recorded intake events, stray intakes accounted for a slightly larger share on wet days than on dry days.

**Figure 2. Stray Intake Proportions on Dry and Wet Days (2024)**

![Stray Intake Proportions on Dry and Wet Days](../../artifacts/weather_analysis/figures/02_stray_intakes/stray_proportion_wet_vs_dry.png)

The figure compares the percentage of intake events classified as stray under the two weather conditions. Both proportions are calculated at the event level, and the vertical axis ranges from 0% to 100%.

### Interpretation Across Research Questions 1 and 2

The findings from Research Questions 1 and 2 provide complementary descriptions of animal intake patterns.

Research Question 1 shows that the average daily intake count was slightly lower on wet days than on dry days (31.56 versus 32.57).

Research Question 2 shows that the proportion of intake events classified as stray was slightly higher on wet days than on dry days (72.01% versus 68.90%).

Together, these results suggest that the overall number of recorded intake events and the composition of those events do not necessarily move in the same direction across weather conditions.

However, these comparisons describe observed associations and do not establish that rainfall caused changes in intake volume or composition.

### Limitations

This analysis is descriptive and does not establish a causal relationship between rainfall and stray intake proportions.

Differences in seasonality, weekdays, holidays, shelter operations, and other factors may influence the types of intake events recorded under different weather conditions.

The analysis uses a binary wet-day indicator and does not distinguish between light and heavy precipitation.

Daily precipitation measurements are based on weather observations from a selected Austin station and may not represent conditions at every animal intake location.

In addition, event-level observations may be clustered within calendar dates, and the analysis does not adjust for such dependence. No statistical significance test is performed.

Finally, the analysis describes the composition of recorded intake events rather than changes in the underlying stray animal population.

### Possible Extensions

Future research could investigate whether stray intake proportions vary with precipitation intensity, animal type, or season.

A more detailed analysis could also account for calendar-related factors and examine daily stray intake counts alongside event-level proportions.

These extensions may help distinguish variation in total intake activity from variation in the composition of intake events.

### Reproducibility

Run the Q2 analysis from the project root directory:

```bash
python3 code/weather_analysis/analyze_stray_intakes.py
```

The script validates the intake and weather date matching, calculates stray intake proportions, and generates the following outputs:

- `artifacts/weather_analysis/tables/q2_stray_intakes_summary.csv`
- `artifacts/weather_analysis/figures/02_stray_intakes/stray_proportion_wet_vs_dry.png`

The analysis uses cleaned intake data from `data/processed/aac_intakes_clean.csv` and daily weather data from `data/processed/austin_weather_2024.csv`.

Python package dependencies are listed in the project's root `requirements.txt` file. 


## Research Question 3: Extreme Heat and Adoption Outcome Proportions

### Data and Methodology

This analysis examines whether the proportion of adoption outcomes differs between hot and non-hot days in Austin during 2024.

We use the cleaned Austin Animal Center outcome dataset together with the daily weather dataset constructed from NOAA and Open-Meteo data. Daily maximum temperature is measured using NOAA observations.

The analysis uses individual outcome events as the unit of observation. Each event is matched to the corresponding daily weather record using its outcome date. Because multiple outcome events may occur on the same day, a many-to-one merge is used.

Hot days are defined as days when the daily maximum temperature is at least 35°C. Non-hot days are defined as days when the maximum temperature is below 35°C.

A binary indicator, `is_adoption`, is created:

- `is_adoption = 1` when `Outcome Type` is `Adoption`.
- `is_adoption = 0` for other known outcome types.

The `Rto-Adopt` category is treated separately from `Adoption` and is classified as non-adoption in the main analysis.

The cleaned dataset contains 11,822 outcome events. All events were successfully matched to weather records, and no invalid outcome dates or duplicate weather dates were identified.

Ten records with missing `Outcome Type` were excluded because their adoption status could not be determined. This leaves **11,812 valid outcome events**, including 7,431 adoption events.

For each weather category, the adoption outcome proportion is calculated by dividing the number of adoption events by the total number of outcome events with a known outcome type.

### Findings

The event-level descriptive analysis produces the following results:

| Statistic | Non-Hot Days | Hot Days |
|---|---:|---:|
| Total outcome events | 8,221 | 3,591 |
| Adoption outcomes | 5,093 | 2,338 |
| Non-adoption outcomes | 3,128 | 1,253 |
| Adoption proportion | 61.95% | 65.11% |

The adoption outcome proportion was approximately **61.95% on non-hot days** and **65.11% on hot days**.

The hot-minus-non-hot difference was approximately **3.16 percentage points**.

Thus, adoption accounted for a slightly larger share of recorded outcome events on hot days than on non-hot days.

**Figure 3. Adoption Outcome Proportions on Non-Hot and Hot Days (2024)**

![Adoption Outcome Proportions on Non-Hot and Hot Days](../../artifacts/weather_analysis/figures/03_adoption_outcomes/adoption_proportion_hot_vs_nonhot.png)

The figure compares the percentage of recorded outcome events classified as adoption under the two weather conditions. The vertical axis ranges from 0% to 100%, and the comparison is conducted at the event level.

### Interpretation

The observed difference indicates that the composition of recorded outcome events varied across temperature categories in 2024.

However, the adoption outcome proportion measures the share of adoption events among recorded outcomes. It does not represent the probability that an individual animal entering the shelter will eventually be adopted.

The results are descriptive and do not establish that extreme heat increases adoption activity or causes changes in adoption outcomes.

### Limitations

This analysis is descriptive and cannot establish a causal relationship between temperature and adoption outcomes.

Seasonality may be particularly important because hot days are concentrated in warmer months, when shelter intake and adoption patterns may differ for reasons unrelated to temperature.

Weekdays, holidays, shelter operations, and animal characteristics may also influence observed outcome patterns.

The binary hot-day indicator does not distinguish between moderately hot days and periods of prolonged extreme heat. Weather measurements from a selected Austin station may not represent conditions at every location relevant to animal intake or adoption.

The analysis treats outcome events as observations rather than tracking individual animals from intake to final outcome. Consequently, the adoption proportion should not be interpreted as an animal-level adoption success rate.

In addition, outcome events occurring on the same date may be correlated, and the analysis does not adjust for this dependence or perform statistical significance testing.

Finally, the primary analysis excludes ten records with missing outcome types and treats `Rto-Adopt` as distinct from `Adoption`. Alternative classification choices could slightly change the reported proportions.

### Possible Extensions

Future research could examine temperature intensity rather than only a binary hot-day classification.

Additional analyses could account for seasonal patterns, weekdays, animal characteristics, and shelter operations.

Linking individual intake and outcome records could also support an investigation of adoption probabilities or time to adoption, rather than only the composition of recorded outcome events.

### Reproducibility

Run the Q3 analysis from the project root directory:

```bash
python3 code/weather_analysis/analyze_adoption_outcomes.py
```

The script loads the cleaned outcome and processed weather datasets, validates date matching, excludes records with missing outcome types, and calculates adoption proportions for hot and non-hot days.

The generated outputs are:

- `artifacts/weather_analysis/tables/q3_adoption_outcomes_summary.csv`
- `artifacts/weather_analysis/figures/03_adoption_outcomes/adoption_proportion_hot_vs_nonhot.png`

The input datasets are:

- `data/processed/aac_outcomes_clean.csv`
- `data/processed/austin_weather_2024.csv`

Required Python packages are listed in the project's root `requirements.txt` file. 


## Research Question 4: Animal Type Heterogeneity in Weather-Related Intake and Outcome Patterns

### Research Objectives

The preceding analyses compare shelter intake and outcome patterns across weather conditions using all recorded animal types. However, aggregate comparisons may conceal differences between animal groups.

To investigate this possibility, we focus on dogs and cats and examine three related questions:

- **Q4a:** Do average daily intake counts on wet and dry days differ between dogs and cats?
- **Q4b:** Do stray intake proportions on wet and dry days differ between dogs and cats?
- **Q4c:** Do adoption outcome proportions on hot and non-hot days differ between dogs and cats?

These analyses extend Q1–Q3 by examining whether the observed weather-related patterns vary across animal types.

### Data and Methodology

We use the same cleaned Austin Animal Center (AAC) intake and outcome datasets and the processed 2024 Austin weather dataset used in the preceding analyses.

The analysis focuses on two categories in the `Animal Type` variable: `Dog` and `Cat`.

The 2024 intake dataset contains 5,188 dog intake events and 6,046 cat intake events, for a combined total of 11,234 events. The outcome dataset contains 5,233 dog outcome events and 6,011 cat outcome events, totaling 11,244 events.

Dogs and cats represent approximately 95% of the intake and outcome events in the cleaned datasets. Other animal types, including birds, livestock, and records classified as other animals, are excluded from this heterogeneity analysis but remain included in the original Q1–Q3 analyses.

**Q4a — Daily Intake Counts by Animal Type**

Individual intake events are grouped by intake date and animal type to calculate the number of dog and cat intake events recorded each day.

These daily counts are then merged with weather observations. We distinguish wet days, defined as days with precipitation greater than 0 mm, from dry days, defined as days with no recorded precipitation.

To ensure consistency with Q1, December 25, 2024, is excluded because no intake records are available for that date. On other dates with recorded AAC intake activity, an animal type with no recorded intake events is assigned a daily count of zero.

Both dogs and cats are therefore analyzed using the same 365 dates: 293 dry days and 72 wet days.

For each animal type and weather group, we calculate the total intake events, mean daily intake count, median daily intake count, and standard deviation.

**Q4b — Stray Intake Proportions by Animal Type**

Individual dog and cat intake events are matched to daily precipitation observations using their intake dates.

An event is classified as a stray intake when `Intake Type` equals `Stray`.

Within each animal type and rainfall category, the stray intake proportion is calculated as:

Stray intake proportion = (Stray intake events / Total intake events in the group) × 100%.

All 11,234 dog and cat intake events are included in this calculation.

**Q4c — Adoption Outcome Proportions by Animal Type**

Individual dog and cat outcome events are matched to daily maximum temperature observations using their outcome dates.

A hot day is defined as a day with maximum temperature at or above 35°C. Other days are classified as non-hot days.

Consistent with Q3, an adoption is defined strictly as an event whose `Outcome Type` equals `Adoption`. The `Rto-Adopt` category is not counted as an adoption.

Of the 11,244 dog and cat outcome events, nine records have missing outcome classifications and are excluded. The remaining 11,235 events are used to calculate adoption outcome proportions within each animal type and temperature category:

Adoption outcome proportion = (Adoption outcome events / Outcome events with known types in the group) × 100%.

All comparisons are descriptive and do not estimate causal effects.

### Findings

#### Q4a: Rainfall and Daily Intake Counts by Animal Type

| Animal Type | Weather | Days | Total Intakes | Mean Daily Intakes | Median | Standard Deviation |
|---|---|---:|---:|---:|---:|---:|
| Dog | Dry | 293 | 4,194 | 14.31 | 13.0 | 7.64 |
| Dog | Wet | 72 | 994 | 13.81 | 14.0 | 6.86 |
| Cat | Dry | 293 | 4,863 | 16.60 | 15.0 | 11.41 |
| Cat | Wet | 72 | 1,183 | 16.43 | 14.5 | 10.08 |

The mean daily dog intake count was 14.31 on dry days and 13.81 on wet days, a wet-minus-dry difference of approximately **−0.50 events per day**.

For cats, the corresponding means were 16.60 and 16.43, a difference of approximately **−0.17 events per day**.

Thus, both animal types had slightly lower mean daily intake counts on wet days. The descriptive difference was somewhat larger for dogs than for cats.

Cat intake counts also exhibited greater day-to-day variability than dog intake counts across both weather categories.

**Figure 4a. Average Daily Dog and Cat Intakes on Dry and Wet Days (2024)**

![Average Daily Dog and Cat Intakes](../../artifacts/weather_analysis/figures/04_animal_type/q4a_daily_intakes_by_animal_type.png)

These comparisons suggest that the relatively small overall wet-versus-dry difference identified in Q1 is also reflected in the two principal animal categories, although the magnitude varies somewhat by animal type.

#### Q4b: Rainfall and Stray Intake Proportions by Animal Type

| Animal Type | Weather | Total Intakes | Stray Intakes | Non-Stray Intakes | Stray Proportion |
|---|---|---:|---:|---:|---:|
| Dog | Dry | 4,194 | 2,517 | 1,677 | 60.01% |
| Dog | Wet | 994 | 638 | 356 | 64.19% |
| Cat | Dry | 4,863 | 3,974 | 889 | 81.72% |
| Cat | Wet | 1,183 | 974 | 209 | 82.33% |

Among dog intake events, the stray proportion increased from 60.01% on dry days to 64.19% on wet days, a difference of approximately **+4.18 percentage points**.

Among cat intake events, the stray proportion increased from 81.72% to 82.33%, a smaller difference of approximately **+0.61 percentage points**.

Cats consistently had a higher share of stray intake events than dogs under both weather conditions. However, the wet-versus-dry difference in the stray intake proportion was larger among dogs.

**Figure 4b. Stray Intake Proportions by Animal Type and Rainfall (2024)**

![Stray Intake Proportions by Animal Type](../../artifacts/weather_analysis/figures/04_animal_type/q4b_stray_proportions_by_animal_type.png)

This result adds an important distinction to Q2. Although the overall stray intake proportion was higher on wet days, that difference was not uniform across animal types.

The difference between the wet-minus-dry changes for dogs and cats was approximately 3.57 percentage points. This is a descriptive comparison of group differences, not evidence of a statistically significant interaction or a causal effect.

#### Q4c: Extreme Heat and Adoption Outcome Proportions by Animal Type

| Animal Type | Weather | Valid Outcomes | Adoptions | Non-Adoptions | Adoption Proportion |
|---|---|---:|---:|---:|---:|
| Dog | Non-Hot | 3,863 | 2,543 | 1,320 | 65.83% |
| Dog | Hot | 1,363 | 917 | 446 | 67.28% |
| Cat | Non-Hot | 3,948 | 2,434 | 1,514 | 61.65% |
| Cat | Hot | 2,061 | 1,385 | 676 | 67.20% |

Among dog outcome events, the adoption proportion was 65.83% on non-hot days and 67.28% on hot days, a difference of approximately **+1.45 percentage points**.

Among cat outcome events, the adoption proportion was 61.65% on non-hot days and 67.20% on hot days, a larger difference of approximately **+5.55 percentage points**.

Thus, adoption represented a larger share of recorded outcome events on hot days for both animal types, but the descriptive difference was substantially larger among cats.

**Figure 4c. Adoption Outcome Proportions by Animal Type and Heat (2024)**

![Adoption Outcome Proportions by Animal Type](../../artifacts/weather_analysis/figures/04_animal_type/q4c_adoption_proportions_by_animal_type.png)

The difference between the hot-minus-non-hot changes for cats and dogs was approximately 4.10 percentage points.

This pattern helps qualify the aggregate finding from Q3. The higher overall adoption outcome proportion on hot days may reflect different patterns across animal categories rather than a uniform relationship for all animal types.

Importantly, the outcome proportion measures the composition of recorded shelter exits. It does not measure the probability that an individual dog or cat entering the shelter will ultimately be adopted.

### Overall Interpretation

The three analyses show that weather-related shelter event patterns vary both by animal type and by the activity being examined.

For daily intake volume, dogs and cats both exhibited slightly lower mean counts on wet days, although the differences were modest.

For stray intake composition, dogs showed a larger wet-versus-dry increase in the stray intake proportion than cats.

For adoption outcome composition, cats showed a larger hot-versus-non-hot increase in the adoption proportion than dogs.

These findings demonstrate that aggregate descriptive comparisons can obscure differences across animal groups.

However, the direction and magnitude of the differences depend on the specific outcome. The results do not establish that one animal type is universally more responsive to weather conditions.

### Limitations

Several limitations apply to this heterogeneity analysis.

First, comparisons are based on recorded shelter events rather than unique animals. An animal may contribute more than one event, and the resulting observations may not be statistically independent.

Second, animal types differ in their underlying intake and outcome compositions. These differences may reflect factors other than weather, including animal characteristics, shelter practices, adoption availability, and seasonal patterns.

Third, the analyses do not control for potential confounding variables such as weekdays, holidays, seasonal changes, shelter staffing, or changes in shelter capacity.

Fourth, although dogs and cats represent most recorded events, the results do not necessarily apply to other animal categories.

Fifth, Q4a measures average daily intake counts, whereas Q4b and Q4c measure event-level proportions. These quantities have different denominators and should not be interpreted interchangeably.

Sixth, the hot-day and wet-day indicators simplify continuous weather conditions into binary categories. Differences in rainfall intensity, temperature, and duration of weather events are not directly examined.

Finally, the observed group differences have not been subjected to formal statistical significance testing or causal identification. Differences in descriptive percentages should not be treated as evidence of statistically significant weather effects.

### Possible Extensions

Future analysis could investigate whether the observed differences remain after accounting for seasonality, weekdays, holidays, and shelter operational factors.

Additional animal-level information, including age, health condition, and prior shelter histories, could help explain variation in intake and outcome patterns.

Longer time series covering multiple years would provide a larger sample for evaluating whether these patterns are persistent.

More detailed weather measures could also support analyses of rainfall intensity, heat duration, and lagged weather conditions.

Finally, linked intake and outcome histories would allow future research to examine individual animal-level adoption probabilities and time to adoption, rather than relying solely on the composition of outcome events.

### Reproducibility

All Q4 analyses are implemented in:

`code/weather_analysis/analyze_animal_type_heterogeneity.py`

From the project root directory, run:

```bash
python3 code/weather_analysis/analyze_animal_type_heterogeneity.py
```

The script reads the following processed datasets:

- `data/processed/aac_intakes_clean.csv`
- `data/processed/aac_outcomes_clean.csv`
- `data/processed/austin_weather_2024.csv`

It produces three summary tables:

- `artifacts/weather_analysis/tables/q4a_daily_intakes_by_animal_type.csv`
- `artifacts/weather_analysis/tables/q4b_stray_proportions_by_animal_type.csv`
- `artifacts/weather_analysis/tables/q4c_adoption_proportions_by_animal_type.csv`

It also produces three figures:

- `artifacts/weather_analysis/figures/04_animal_type/q4a_daily_intakes_by_animal_type.png`
- `artifacts/weather_analysis/figures/04_animal_type/q4b_stray_proportions_by_animal_type.png`
- `artifacts/weather_analysis/figures/04_animal_type/q4c_adoption_proportions_by_animal_type.png`

The script uses project-relative paths, checks weather-date matching, verifies key event totals, and generates all statistics and figures programmatically.

Required Python packages are listed in the project's root `requirements.txt` file.