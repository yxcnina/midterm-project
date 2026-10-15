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