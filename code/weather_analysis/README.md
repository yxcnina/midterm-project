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


## Research Question 5: Rainfall and Animal Intake Type Composition

### Research Objective

Research Question 2 (Q2) found that stray intake events accounted for a slightly higher proportion of all animal intake events on wet days than on dry days. However, the binary comparison between stray and non-stray intakes does not reveal how the remaining intake categories contribute to the overall composition.

To extend Q2, this analysis examines the complete distribution of animal intake types across rainfall conditions.

The research question is:

**Does the composition of animal intake types differ between wet and dry days?**

Specifically, we compare the proportions of six intake categories to identify which types account for larger or smaller shares of recorded intake events under different rainfall conditions.

### Data and Methodology

This analysis uses the same cleaned 2024 Austin Animal Center (AAC) intake dataset and processed Austin daily weather dataset used in Q1, Q2, and Q4.

The input datasets are:

- `data/processed/aac_intakes_clean.csv`
- `data/processed/austin_weather_2024.csv`

Each intake event is matched to the weather observation for its intake date using a many-to-one merge.

Rainfall conditions are classified as follows:

- **Dry day:** Daily precipitation equals 0 mm (`wet_day = 0`).
- **Wet day:** Daily precipitation is greater than 0 mm (`wet_day = 1`).

The analysis includes all **11,815 recorded intake events** from 2024:

- **9,543 events** occurred on dry days.
- **2,272 events** occurred on wet days.

All events were successfully matched to weather observations. No intake records were excluded due to missing intake types or unmatched weather dates.

The dataset contains six distinct intake classifications:

1. Stray
2. Owner Surrender
3. Public Assist
4. Abandoned
5. Wildlife
6. Euthanasia Request

All six categories are retained, including rare categories, to preserve the complete observed intake distribution.

For each weather category, we calculate:

1. The number of recorded events belonging to each intake type.
2. The proportion of that intake type among all intake events recorded under the same weather condition.
3. The wet-minus-dry difference in percentage points.

The intake type proportion is defined as:

**Intake Type Proportion (%) = (Events in a Specific Intake Type / Total Intake Events in the Weather Group) × 100**

The difference in proportions is calculated as:

**Wet − Dry Difference (pp) = Wet-Day Proportion (%) − Dry-Day Proportion (%)**

The proportions within each weather group sum to 100%.

This is an event-level descriptive analysis. The objective is to examine differences in recorded intake composition rather than estimate causal effects.

### Findings

#### Intake Type Composition by Weather Condition

The following table presents the number and proportion of intake events in each category under dry and wet conditions.

| Intake Type | Dry Events | Dry Share | Wet Events | Wet Share | Wet − Dry (pp) |
|---|---:|---:|---:|---:|---:|
| Stray | 6,575 | 68.90% | 1,636 | 72.01% | +3.11 |
| Owner Surrender | 1,728 | 18.11% | 400 | 17.61% | -0.50 |
| Public Assist | 590 | 6.18% | 120 | 5.28% | -0.90 |
| Abandoned | 342 | 3.58% | 62 | 2.73% | -0.85 |
| Wildlife | 306 | 3.21% | 54 | 2.38% | -0.83 |
| Euthanasia Request | 2 | 0.02% | 0 | 0.00% | -0.02 |
| **Total** | **9,543** | **100.00%** | **2,272** | **100.00%** | **0.00** |

*Note: Individual percentages are rounded to two decimal places, so their displayed sums may differ slightly from 100%.*

The largest observed difference is associated with the **Stray** category.

Stray intakes accounted for approximately **68.90% of all intake events on dry days**, compared with **72.01% on wet days**, representing a wet-minus-dry difference of approximately **+3.11 percentage points**.

This result is consistent with the original Q2 analysis and confirms that the higher stray intake share on wet days remains evident when all intake categories are examined separately.

In contrast, each of the other five intake categories represented a slightly smaller proportion of recorded intake events on wet days.

Among the non-stray categories, the largest percentage-point differences were:

- **Public Assist:** -0.90 percentage points.
- **Abandoned:** -0.85 percentage points.
- **Wildlife:** -0.83 percentage points.

Owner Surrender showed a smaller difference of approximately -0.50 percentage points.

Euthanasia Request accounted for only two events in the full dataset, both recorded on dry days. Because this category is extremely rare, its percentage difference should not be interpreted as evidence of a meaningful weather-related pattern.

#### Figure 5a. Animal Intake Type Composition on Dry and Wet Days (2024)

![Animal Intake Type Composition on Dry and Wet Days](../../artifacts/weather_analysis/figures/05_intake_type/q5_intake_type_composition.png)

Figure 5a presents a 100% stacked bar chart comparing the relative shares of all six intake types on dry and wet days.

Stray intake events account for the largest share in both weather categories. Their share is slightly larger on wet days, while Owner Surrender, Public Assist, Abandoned, and Wildlife account for correspondingly smaller portions of the total.

Although the overall composition is broadly similar across rainfall conditions, the chart shows a modest shift toward a greater relative share of stray intake events on wet days.

#### Figure 5b. Wet-Minus-Dry Differences in Intake Type Shares (2024)

![Wet-Minus-Dry Intake Type Share Differences](../../artifacts/weather_analysis/figures/05_intake_type/q5_intake_type_differences.png)

Figure 5b displays the wet-minus-dry percentage-point difference for each intake classification.

Positive values indicate that an intake type accounts for a larger share of recorded events on wet days, while negative values indicate a smaller share.

The figure highlights the approximately **+3.11 percentage-point difference for Stray**, compared with smaller negative differences for the other five categories.

Because the intake categories collectively account for all recorded intake events, their percentage-point differences necessarily sum to zero, apart from rounding.

Consequently, a higher share for one category must be accompanied by lower combined shares for other categories.

### Overall Interpretation

Q5 provides a more detailed explanation of the descriptive pattern identified in Q2.

The earlier analysis showed that the proportion of stray intake events was higher on wet days than on dry days. By examining all six intake categories, Q5 shows that the higher stray share is accompanied by slightly smaller shares of Owner Surrender, Public Assist, Abandoned, Wildlife, and Euthanasia Request.

The most notable difference is concentrated in the Stray category, while the individual differences across the remaining categories are each less than one percentage point in magnitude.

These findings suggest that the composition of recorded AAC intake events varies modestly between wet and dry days.

However, changes in intake proportions do not necessarily imply corresponding changes in absolute daily event counts. Because the analysis compares event shares within each weather category, a smaller share of an intake type does not by itself establish that rainfall reduces the number of events belonging to that category.

Overall, Q5 complements Q1 and Q2 by distinguishing three related but different measures:

- **Q1:** Total daily intake volume.
- **Q2:** The proportion of stray intake events.
- **Q5:** The complete composition of intake types.

Together, these analyses provide a more comprehensive descriptive view of shelter intake patterns under different rainfall conditions.

### Limitations

Several limitations should be considered when interpreting these results.

**First, the analysis is descriptive rather than causal.** Differences in intake type composition cannot establish that rainfall causes changes in animal intake classifications.

**Second, the data describe recorded intake events rather than unique animals.** An individual animal may contribute multiple records, meaning that event counts should not be interpreted as counts of distinct animals.

**Third, the analysis does not adjust for seasonality or other potential confounding factors.** Intake composition may vary with weekdays, holidays, shelter operating procedures, animal characteristics, and other environmental or institutional conditions.

**Fourth, the wet-day indicator does not distinguish rainfall intensity or duration.** Light precipitation and heavy rainfall are placed in the same category, even though their associations with animal shelter activity could differ.

**Fifth, sample sizes differ between the two weather groups.** The dataset contains substantially more intake events on dry days than on wet days. This imbalance should be considered when comparing categories with small event counts.

**Sixth, rare intake classifications provide limited information.** In particular, only two Euthanasia Request intake events appear in the dataset. No meaningful conclusions about its relationship with rainfall can be drawn from such a small number of observations.

Finally, the analysis does not include formal statistical significance testing. The reported differences are observed descriptive differences and should not be interpreted as statistically significant effects.

### Possible Extensions

Future research could explore whether rainfall-associated differences in intake composition vary across animal types, especially dogs and cats.

Further analysis could also examine the relationship between weather conditions and specific intake classifications within different seasons or months.

Using multiple years of intake and weather data would increase the number of observed wet days and provide additional information about whether the patterns are persistent.

Another extension would be to investigate how different intake classifications are associated with subsequent shelter outcomes, including adoption, transfer, and return to owner.

Such analyses would provide a more detailed understanding of the relationship between weather conditions, shelter intake pathways, and subsequent animal outcomes.

### Reproducibility

Q5 is implemented in the following Python script:

`code/weather_analysis/analyze_intake_type_composition.py`

The script uses the cleaned intake dataset and the processed daily weather dataset.

From the project root directory, run:

```bash
python3 code/weather_analysis/analyze_intake_type_composition.py
```

The script performs the following operations:

1. Loads the cleaned intake and daily weather datasets.
2. Validates the number of observations and intake classifications.
3. Matches each intake event to the corresponding daily weather observation.
4. Calculates event counts and proportions for all six intake types.
5. Computes wet-minus-dry percentage-point differences.
6. Validates the event totals and consistency with Q2.
7. Saves summary statistics and generates the two visualizations.

The generated summary tables are:

- `artifacts/weather_analysis/tables/q5_intake_type_composition.csv`
- `artifacts/weather_analysis/tables/q5_intake_type_differences.csv`

The generated figures are:

- `artifacts/weather_analysis/figures/05_intake_type/q5_intake_type_composition.png`
- `artifacts/weather_analysis/figures/05_intake_type/q5_intake_type_differences.png`

The script uses project-relative file paths and produces the results programmatically without requiring manual modifications to the datasets.

Required Python packages are listed in the project's root `requirements.txt` file.


### Additional Temperature Analyses: Extreme Heat and Cold Weather

In addition to rainfall, we extend Research Question 5 to examine whether the composition of recorded animal intake types varies across temperature conditions.

The extensions address two additional questions:

- **Q5b:** Does the composition of animal intake types differ between hot and non-hot days?
- **Q5c:** Does the composition of animal intake types differ between cold and non-cold days?

We also conduct a supplementary sensitivity analysis using a stricter freezing-day definition.

These analyses use the same six intake categories and the same 11,815 intake events as the rainfall analysis in Q5a. Each temperature comparison is conducted separately, and all findings are descriptive rather than causal.

### Q5b: Extreme Heat and Intake Type Composition

#### Research Objective

The objective of Q5b is to investigate whether the distribution of animal intake classifications differs between days with extreme heat and days without extreme heat.

Unlike Q5a, which focuses on precipitation, this analysis considers daily maximum temperature.

#### Data and Methodology

We use the cleaned 2024 Austin Animal Center intake dataset and processed daily weather data.

Each intake event is matched to the temperature recorded on its intake date.

Consistent with Q3 and Q4c, weather conditions are classified as:

- **Hot day:** Daily maximum temperature is at least 35°C (`hot_day = 1`).
- **Non-hot day:** Daily maximum temperature is below 35°C (`hot_day = 0`).

The dataset contains:

- **101 hot days**, with 3,230 recorded intake events.
- **265 non-hot days**, including 264 days with recorded intake events and 8,585 intake events.

December 25, 2024, has no recorded intake events and therefore does not contribute to the event-level proportions.

All 11,815 intake events are included.

For each temperature group, we calculate the number and percentage of intake events belonging to each of the six intake categories.

The hot-minus-non-hot difference is measured in percentage points:

**Difference (pp) = Hot-Day Share (%) − Non-Hot-Day Share (%)**

#### Findings

| Intake Type | Non-Hot Events | Non-Hot Share | Hot Events | Hot Share | Difference (pp) |
|---|---:|---:|---:|---:|---:|
| Stray | 5,966 | 69.49% | 2,245 | 69.50% | +0.01 |
| Owner Surrender | 1,601 | 18.65% | 527 | 16.32% | -2.33 |
| Public Assist | 494 | 5.75% | 216 | 6.69% | +0.93 |
| Abandoned | 283 | 3.30% | 121 | 3.75% | +0.45 |
| Wildlife | 239 | 2.78% | 121 | 3.75% | +0.96 |
| Euthanasia Request | 2 | 0.02% | 0 | 0.00% | -0.02 |
| **Total** | **8,585** | **100.00%** | **3,230** | **100.00%** | **0.00** |

*Note: Percentages and percentage-point differences are rounded to two decimal places.*

The proportion of Stray intake events was almost identical between hot and non-hot days: approximately 69.49% and 69.50%, respectively.

The hot-minus-non-hot difference was only +0.01 percentage points, indicating virtually no observed difference in the relative share of stray intakes across the two temperature categories.

In contrast, Owner Surrender accounted for a smaller share of intake events on hot days, decreasing from approximately 18.65% on non-hot days to 16.32% on hot days, a difference of -2.33 percentage points.

Public Assist and Wildlife represented slightly larger shares on hot days, increasing by approximately 0.93 and 0.96 percentage points, respectively.

Abandoned intake events also accounted for a somewhat larger share on hot days, with a difference of +0.45 percentage points.

Euthanasia Request is too rare to support meaningful interpretation.

#### Figure 5c. Intake Type Composition on Hot and Non-Hot Days (2024)

![Extreme Heat and Intake Type Composition](../../artifacts/weather_analysis/figures/05_intake_type/q5b_heat_composition.png)

Figure 5c presents the complete intake type distribution under hot and non-hot conditions.

The Stray category accounts for nearly the same proportion of intake events in both groups, while relatively modest differences appear in the other categories.

#### Figure 5d. Hot-Minus-Non-Hot Differences in Intake Type Shares (2024)

![Extreme Heat Intake Type Share Differences](../../artifacts/weather_analysis/figures/05_intake_type/q5b_heat_differences.png)

Figure 5d shows the percentage-point differences between hot and non-hot days.

The largest difference is the lower Owner Surrender share on hot days, while the differences for Public Assist and Wildlife are positive but smaller.

#### Interpretation

Q5b suggests that extreme heat is associated with relatively modest differences in the composition of recorded animal intake events.

The near-identical Stray shares are particularly noteworthy when compared with Q5a, where wet days exhibited a higher stray intake proportion than dry days.

However, the absence of a substantial difference in the Stray share does not establish that extreme heat has no effect on the absolute number of stray intake events.

Similarly, the lower Owner Surrender share on hot days does not by itself imply that extreme heat reduces owner surrender activity.

The findings describe the relative composition of recorded events and may reflect seasonal, operational, or animal-related differences that are not controlled for in this analysis.

### Q5c: Cold Weather and Intake Type Composition

#### Research Objective

Q5c examines whether intake type composition differs between cold and non-cold days.

Because freezing conditions are relatively uncommon in Austin, we use a broader cold-day definition for the main analysis and examine freezing conditions separately as a sensitivity check.

#### Data and Methodology

Each intake event is matched to the daily minimum temperature on its intake date.

For the main analysis, the weather categories are:

- **Cold day:** Daily minimum temperature is at or below 5°C.
- **Non-cold day:** Daily minimum temperature is above 5°C.

This threshold identifies relatively cold days while retaining more observations than the stricter freezing-day definition.

The sample contains:

- **29 cold days**, with 708 recorded intake events.
- **337 non-cold days**, including 336 days with recorded intake events and 11,107 intake events.

The comparison includes all 11,815 intake events.

As in Q5a and Q5b, we calculate event counts, within-group percentages, and percentage-point differences for all six intake classifications.

The cold-minus-non-cold difference is:

**Difference (pp) = Cold-Day Share (%) − Non-Cold-Day Share (%)**

The 5°C threshold is an exploratory classification rather than an externally validated behavioral cutoff. It was selected after reviewing temperature coverage and sample sizes, but before examining the intake type composition results.

#### Findings

| Intake Type | Non-Cold Events | Non-Cold Share | Cold Events | Cold Share | Difference (pp) |
|---|---:|---:|---:|---:|---:|
| Stray | 7,793 | 70.16% | 418 | 59.04% | -11.12 |
| Owner Surrender | 1,957 | 17.62% | 171 | 24.15% | +6.53 |
| Public Assist | 646 | 5.82% | 64 | 9.04% | +3.22 |
| Abandoned | 366 | 3.30% | 38 | 5.37% | +2.07 |
| Wildlife | 343 | 3.09% | 17 | 2.40% | -0.69 |
| Euthanasia Request | 2 | 0.02% | 0 | 0.00% | -0.02 |
| **Total** | **11,107** | **100.00%** | **708** | **100.00%** | **0.00** |

*Note: Percentages and percentage-point differences are rounded to two decimal places.*

The most notable difference is observed in the Stray category.

Stray intake events accounted for approximately 70.16% of intake events on non-cold days, compared with 59.04% on cold days.

The cold-minus-non-cold difference was approximately **-11.12 percentage points**.

In contrast, Owner Surrender accounted for 24.15% of intake events on cold days, compared with 17.62% on non-cold days, an increase of approximately **6.53 percentage points**.

Public Assist also represented a larger share on cold days, increasing from 5.82% to 9.04%, a difference of approximately **3.22 percentage points**.

Abandoned intake events increased in relative share by approximately **2.07 percentage points**.

Wildlife represented a slightly smaller share on cold days, while Euthanasia Request remained extremely rare.

These descriptive differences are larger than many of the differences observed in the rainfall and extreme heat comparisons.

However, the cold-day sample contains only 29 days and 708 intake events, so the results require cautious interpretation.

#### Figure 5e. Intake Type Composition on Cold and Non-Cold Days (2024)

![Cold Weather and Intake Type Composition](../../artifacts/weather_analysis/figures/05_intake_type/q5c_cold_composition.png)

Figure 5e illustrates the complete intake type composition under the main 5°C cold-day definition.

The cold-day distribution has a smaller Stray share and relatively larger Owner Surrender, Public Assist, and Abandoned shares.

#### Figure 5f. Cold-Minus-Non-Cold Differences in Intake Type Shares (2024)

![Cold Weather Intake Type Share Differences](../../artifacts/weather_analysis/figures/05_intake_type/q5c_cold_differences.png)

Figure 5f shows the percentage-point differences across the six intake categories.

The largest negative difference is observed for Stray, while the largest positive difference is observed for Owner Surrender.

#### Interpretation

The cold-weather comparison reveals a more pronounced descriptive shift in intake composition than the extreme heat comparison.

On cold days, Stray accounts for a substantially smaller proportion of recorded intake events, while Owner Surrender, Public Assist, and Abandoned account for larger proportions.

One possible avenue for future research is whether cold weather is associated with changes in the types of animals brought to shelters or the circumstances under which animals enter shelters.

However, the present evidence does not identify the mechanisms behind the observed differences.

In particular, the larger shares of Owner Surrender and Public Assist should not be interpreted as evidence that cold weather causes these events to increase.

The comparisons may reflect seasonal differences, shelter operations, animal characteristics, or other factors unrelated to the direct effects of temperature.

### Q5c Sensitivity Analysis: Freezing Days

#### Objective and Methodology

To evaluate how sensitive the main cold-weather findings are to the temperature threshold, we repeat the composition analysis using the existing `freezing_day` indicator.

The categories are:

- **Freezing day:** Daily minimum temperature is at or below 0°C.
- **Non-freezing day:** Daily minimum temperature is above 0°C.

The 2024 dataset contains:

- **7 freezing days**, with 180 recorded intake events.
- **359 non-freezing days**, including 358 days with recorded intake events and 11,635 intake events.

Because there are only seven freezing days, this analysis should be treated as exploratory.

#### Findings

| Intake Type | Non-Freezing Events | Non-Freezing Share | Freezing Events | Freezing Share | Difference (pp) |
|---|---:|---:|---:|---:|---:|
| Stray | 8,093 | 69.56% | 118 | 65.56% | -4.00 |
| Owner Surrender | 2,091 | 17.97% | 37 | 20.56% | +2.58 |
| Public Assist | 695 | 5.97% | 15 | 8.33% | +2.36 |
| Abandoned | 400 | 3.44% | 4 | 2.22% | -1.22 |
| Wildlife | 354 | 3.04% | 6 | 3.33% | +0.29 |
| Euthanasia Request | 2 | 0.02% | 0 | 0.00% | -0.02 |
| **Total** | **11,635** | **100.00%** | **180** | **100.00%** | **0.00** |

*Note: Percentages and percentage-point differences are rounded to two decimal places.*

The freezing-day comparison shows a smaller Stray share than the non-freezing-day comparison, with a difference of approximately -4.00 percentage points.

Owner Surrender and Public Assist also account for larger shares on freezing days, with differences of approximately +2.58 and +2.36 percentage points.

These three categories exhibit the same directions of difference as in the 5°C main analysis, although the magnitudes differ.

However, Abandoned and Wildlife do not exhibit the same directional patterns under the two temperature thresholds.

Therefore, the cold-weather findings cannot be considered fully robust to the choice of temperature threshold.

#### Figure 5g. Intake Type Composition on Freezing and Non-Freezing Days (2024)

![Freezing Weather Intake Type Composition](../../artifacts/weather_analysis/figures/05_intake_type/q5c_freezing_sensitivity_composition.png)

Figure 5g shows the intake type composition using the stricter freezing-day definition.

#### Figure 5h. Freezing-Minus-Non-Freezing Differences in Intake Type Shares (2024)

![Freezing Weather Intake Type Share Differences](../../artifacts/weather_analysis/figures/05_intake_type/q5c_freezing_sensitivity_differences.png)

Figure 5h displays the percentage-point differences for the freezing-day sensitivity analysis.

#### Sensitivity Analysis Interpretation

The Stray, Owner Surrender, and Public Assist categories retain the same directions of difference under the 5°C and 0°C temperature thresholds.

Nevertheless, the magnitude of the differences changes substantially, and the signs of the differences for Abandoned and Wildlife are not consistent.

The freezing-day group contains only 180 events across seven days. As a result, relatively small changes in the number of recorded events can have noticeable effects on the estimated proportions.

The findings therefore provide limited descriptive support for the directional consistency of selected categories, but do not establish overall robustness.

### Overall Interpretation of the Q5 Temperature Extensions

The temperature analyses reveal different patterns in the composition of recorded animal intake events.

Under extreme heat, the Stray share remains almost unchanged, while Owner Surrender accounts for a somewhat smaller proportion of events.

Under the broader cold-weather definition, Stray accounts for a substantially smaller share, while Owner Surrender and Public Assist account for larger shares.

The freezing-day sensitivity analysis provides partial directional consistency for these categories, but the results depend on the chosen threshold.

Taken together with Q5a, these findings suggest that intake composition is not uniformly associated with all weather conditions.

Rainfall, extreme heat, and cold weather are associated with different descriptive patterns across intake types.

However, the weather classifications are not mutually exclusive, and differences between comparisons should not be interpreted as direct comparisons of causal effects.

### Limitations of the Temperature Analyses

Several important limitations apply.

First, these analyses are descriptive and cannot identify causal effects of temperature on animal intake activity.

Second, cold and hot days are concentrated in particular seasons. Seasonal animal behavior, breeding cycles, shelter operations, holidays, and other factors may explain part of the observed differences.

Third, the two temperature indicators use binary thresholds and do not capture the duration or severity of heat and cold exposure.

Fourth, the cold-day threshold of 5°C is exploratory and was selected after considering sample coverage. Results may change when different thresholds are applied.

Fifth, the freezing-day sample is particularly limited, with only seven calendar days and 180 recorded events.

Sixth, some intake types have very few observations. The Euthanasia Request category contains only two events across the full sample.

Seventh, the data represent recorded intake events rather than unique animals. Animals with repeated intake histories may contribute multiple observations.

Finally, these analyses do not use formal statistical tests or account for potential dependence among events occurring on the same date.

The magnitude of a descriptive percentage-point difference should therefore not be interpreted as evidence of statistical significance.

### Possible Extensions of the Temperature Analyses

Future work could examine whether the observed temperature-related composition differences persist after accounting for seasonality, weekdays, holidays, and shelter operating conditions.

An analysis using multiple years of daily weather and intake data would provide more observations of rare freezing conditions.

Temperature could also be modeled as a continuous measure or grouped into multiple prespecified categories, rather than using only binary thresholds.

Additional research could investigate whether intake type composition differs jointly by temperature and animal type, especially between dogs and cats.

Finally, examining longer-term animal-level intake and outcome histories could help distinguish changes in intake composition from changes in the circumstances and outcomes of individual animals.

### Reproducibility of Q5b and Q5c

The temperature extensions are implemented in the same Python script as Q5a:

`code/weather_analysis/analyze_intake_type_composition.py`

From the project root directory, run:

```bash
python3 code/weather_analysis/analyze_intake_type_composition.py
```

The script reads:

- `data/processed/aac_intakes_clean.csv`
- `data/processed/austin_weather_2024.csv`

The weather indicators are:

- `wet_day`: Daily precipitation greater than 0 mm.
- `hot_day`: Daily maximum temperature at least 35°C.
- `cold_day`: Daily minimum temperature at or below 5°C, constructed during the analysis.
- `freezing_day`: Daily minimum temperature at or below 0°C.

The additional summary tables are:

- `artifacts/weather_analysis/tables/q5b_heat_composition.csv`
- `artifacts/weather_analysis/tables/q5b_heat_differences.csv`
- `artifacts/weather_analysis/tables/q5c_cold_composition.csv`
- `artifacts/weather_analysis/tables/q5c_cold_differences.csv`
- `artifacts/weather_analysis/tables/q5c_freezing_sensitivity_composition.csv`
- `artifacts/weather_analysis/tables/q5c_freezing_sensitivity_differences.csv`

The additional figures are:

- `artifacts/weather_analysis/figures/05_intake_type/q5b_heat_composition.png`
- `artifacts/weather_analysis/figures/05_intake_type/q5b_heat_differences.png`
- `artifacts/weather_analysis/figures/05_intake_type/q5c_cold_composition.png`
- `artifacts/weather_analysis/figures/05_intake_type/q5c_cold_differences.png`
- `artifacts/weather_analysis/figures/05_intake_type/q5c_freezing_sensitivity_composition.png`
- `artifacts/weather_analysis/figures/05_intake_type/q5c_freezing_sensitivity_differences.png`

All statistics and visualizations are generated programmatically from the cleaned datasets using project-relative paths.

The script preserves all six original intake type categories, verifies event totals, and calculates within-group shares and percentage-point differences without manually changing the data.
