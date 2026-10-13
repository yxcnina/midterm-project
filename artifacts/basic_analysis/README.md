# Basic Analysis

Six descriptive questions about Austin Animal Center records in 2024.
Figures use simple Matplotlib/Pandas plots and are saved as PNG only.

## Guide and data

| Theme | Question | Figures |
| --- | --- | --- |
| 01_intake_profile | Who comes through the shelter's doors? | [Age, sex, and breed](figures/01_intake_profile/) |
| 02_intake_timing | When are intake records most frequent? | [Monthly counts and cat ages](figures/02_intake_timing/) |
| 03_intake_context | How do animals enter, and in what condition? | [Intake types and conditions](figures/03_intake_context/) |
| 04_outcome_profile | What outcomes are recorded? | [Outcome composition](figures/04_outcome_profile/) |
| 05_trait_comparisons | How do adoption shares vary across recorded traits? | [Age, sex, breed, and color](figures/05_trait_comparisons/) |
| 06_intake_locations | What do mapped concentrations represent? | [Location maps and an address sensitivity check](figures/06_intake_locations/) |

Each theme has a same-named script in [code/basic_analysis](../../code/basic_analysis/README.md).
Summary tables follow the same six-folder structure under [tables](tables/).

| Source | All animal records | Cat records | Dog records |
| --- | ---: | ---: | ---: |
| [Full cleaned intakes](../../data/processed/aac_intakes_clean.csv) | 11,815 | 6,046 | 5,188 |
| [Full cleaned outcomes](../../data/processed/aac_outcomes_clean.csv) | 11,822 | 6,011 | 5,233 |
| [Geocoded intakes](../../data/processed/aac_intakes_clean_geocoded.csv) | 7,545 | 4,113 | 3,036 |

The observation is an **intake or outcome event**, not necessarily a unique
animal. The 2024 intake and outcome files are analyzed separately; they are
not a matched cohort. Non-spatial intake figures use the full intake file,
not the smaller geocoded subset. The six themes focus on cats and dogs.

## 1. Who comes through the shelter's doors?

![Age distribution](figures/01_intake_profile/age_distribution.png)

Cats have a younger intake profile: **61.4%** of cat records report an age
below six months, compared with **31.5%** of dog records. Dogs' largest age
group is **1 to under 3 years (33.2%)**.

![Sex distribution](figures/01_intake_profile/sex_distribution.png)

Female and male shares are similar for both species. Sex is recorded as
`Unknown` in **6.5%** of cat records and **0.9%** of dog records. These records
remain in the denominator.

![Recorded breed distribution](figures/01_intake_profile/breed_distribution.png)

`Domestic Shorthair` accounts for **82.6%** of cat records. The most frequent
individual dog label, `Pit Bull`, accounts for **8.4%**. The top five labels
cover **97.7%** of cat records and **32.8%** of dog records, so the gray bars
retain all remaining labels. These are recorded breed labels, not verified
genetic ancestry; `Mix` and compound labels remain separate.

The summary also separates sex from sterilization status. At intake,
**12.4%** of cat records and **24.1%** of dog records are coded spayed/neutered.
These shares use all records of each species, including unknown status.

[Counts and percentages](tables/01_intake_profile/intake_profile.csv)

## 2. When are intake records most frequent?

![Monthly cat and dog intakes](figures/02_intake_timing/monthly_intakes.png)

Cat intakes peak in **May: 887 records**, or **14.7%** of the year's cat
records. Dog intakes peak in **April and May**, tied at **512 records** each.
The two panels use the same count scale.

![Monthly cat ages](figures/02_intake_timing/monthly_cat_ages.png)

In May, **653 of 887 cat records (73.6%)** report ages below six months.
Another 228 are six months or older, and six are recorded as `0 years`.
The age breakdown helps show which records account for the monthly peak.

These are monthly totals, not daily rates; month lengths differ. One year
describes the pattern in 2024 and cannot establish a recurring seasonal
pattern by itself.

[Monthly species counts](tables/02_intake_timing/monthly_intakes.csv) ·
[Monthly cat-age counts](tables/02_intake_timing/monthly_cat_ages.csv)

## 3. How do animals enter, and in what condition?

![Intake types](figures/03_intake_context/intake_type.png)

`Stray` accounts for **81.8%** of cat intake records and **60.8%** of dog
records. `Owner Surrender` accounts for **14.3%** and **22.8%**, respectively.
Dogs also have a larger `Public Assist` share: **11.4%**, versus **1.6%** for cats.

![Intake conditions](figures/03_intake_context/intake_condition.png)

Most records are coded `Normal`: **76.3%** for cats and **78.7%** for dogs.
Cats have a larger `Neonatal` share (**8.8%** versus **1.7%**); dogs have a
larger `Injured` share (**9.2%** versus **6.8%**).

Each bar totals 100% of the species' intake records. All original categories
are retained, including very small segments. Labels appear only on segments
of at least 5%; the CSVs provide every count and percentage. Recorded intake
condition is an administrative category, not a standardized health score.

[Intake types](tables/03_intake_context/intake_type.csv) ·
[Intake conditions](tables/03_intake_context/intake_condition.csv)

## 4. What outcomes are recorded?

![Recorded outcomes](figures/04_outcome_profile/outcome_distribution.png)

| Recorded outcome | Cats, n = 6,011 | Dogs, n = 5,233 |
| --- | ---: | ---: |
| Adoption | 3,819 (63.5%) | 3,460 (66.1%) |
| Transfer | 1,729 (28.8%) | 822 (15.7%) |
| Return to Owner | 153 (2.5%) | 676 (12.9%) |

The adoption shares are relatively close, but cats have a larger transfer
share and dogs have a larger return-to-owner share.

All other outcome categories remain in the chart and table. `Rto-Adopt`
is kept separate from `Adoption`. Two cat and seven dog records have blank
outcome types and are labeled `Not recorded`; the literal category
`Missing` remains distinct. The denominator includes all outcome events
for that species.

These percentages describe the composition of the 2024 outcome file. They
do not show what ultimately happened to the animals admitted during 2024.

[All outcome counts and percentages](tables/04_outcome_profile/outcome_distribution.csv)

## 5. How do adoption shares vary across recorded traits?

For this section:

**Adoption share = records coded exactly `Adoption` / all outcome records
in the same species and trait group.**

Blank outcome types stay in the denominator. Age and sex are measured
**at outcome**, not at intake. Each point shows its group size, `n`.
The comparisons are descriptive and unadjusted.

![Adoption shares by age](figures/05_trait_comparisons/adoption_by_age.png)

Among the five age bands with interpretable boundaries, the **6 to under
12 months** group has the largest adoption share: **77.0%** for cats
(265/344) and **83.9%** for dogs (433/516). At seven years or older, the
shares are **46.0%** and **45.2%**.

The `0 years` groups are retained separately, but should not guide conclusions:
the cat group has 12 records and the dog group only two. Their 0% and 100%
shares reflect very small, imprecisely aged groups.

![Adoption shares by sex](figures/05_trait_comparisons/adoption_by_sex.png)

Cat female and male shares are close (**67.7%** and **68.2%**). For dogs,
the corresponding shares are **69.7%** and **64.0%**. The `Unknown` groups
are shown for completeness; their low adoption shares may reflect recording
or case-composition differences and are not a biological-sex comparison.
Sterilization labels describe status at outcome and cannot establish what
caused adoption.

![Adoption shares by breed](figures/05_trait_comparisons/adoption_by_breed.png)

For each species, the five labels are selected by **number of outcome
records**, not adoption share. Among the displayed dog labels,
`Labrador Retriever Mix` has a **78.0%** share and `Pit Bull Mix` has a
**58.6%** share. These raw comparisons do not isolate a breed effect.

![Adoption shares by color](figures/05_trait_comparisons/adoption_by_color.png)

Color labels are also selected by outcome frequency and kept in their original
form. Among the displayed cat labels, `Brown Tabby/White` has a **70.7%**
adoption share and `Black` has a **59.8%** share. The groups may differ in age,
breed, condition, timing, and other characteristics; this does not establish
a color preference or a causal effect.

The age differences give a clear descriptive pattern in these records.
Interpreting breed and color differences would require comparisons within
more similar groups, such as the same species and age band. No statistical
significance tests or causal models are used here.

[All trait groups, sample sizes, adoption counts, and chart-selection flags](tables/05_trait_comparisons/adoption_by_trait.csv)

## 6. What do mapped concentrations represent?

![All geocoded cat and dog intakes](figures/06_intake_locations/intake_locations_all_records.png)

| Species | Geocoded records | Full intake records | Geocoding coverage |
| --- | ---: | ---: | ---: |
| Cats | 4,113 | 6,046 | 68.0% |
| Dogs | 3,036 | 5,188 | 58.5% |

These are coordinate maps of recorded `Found Location` values, with no
street basemap. Each hexagon counts intake events. Both species and both map
versions use identical extents, bins, and a logarithmic color scale. All
geocoded cat/dog records are within the displayed extent; no outliers are
silently cropped.

The shelter marker identifies **7201 Levander Loop**, the address listed by
[City of Austin Animal Services](https://www.austintexas.gov/animal-services/contact).
The marker coordinates come from existing geocodes for the matching shelter
address in this dataset; the script does not call a geocoding service.

![Maps excluding shelter-address records](figures/06_intake_locations/intake_locations_without_shelter_address.png)

The second figure excludes **58 cat and 112 dog records** whose recorded
address matches the shelter's street number and name, including observed
spelling variants. It does not remove every point near the shelter. The
largest dog-bin count falls from **123 to 93**; the largest cat-bin count
remains **105**. These counts depend on the chosen grid.

A concentration at the shelter address may reflect a reporting or delivery
location. It should not automatically be read as a concentration of animals
found or abandoned at that exact site.

Coverage is also selective: across all animal types, **75.2%** of `Stray`
records are geocoded, compared with **13.1%** of `Owner Surrender` records.
Thus the maps describe the geocoded records, not all intake events or the
distribution of animals living in Austin.

Of all 7,545 geocoded records, **71.4%** are address points, **18.9%** are
interpolated street addresses, and **9.7%** are street intersections.
Coordinates are geocoded reference locations, not GPS observations, owner
residences, adoption destinations, or measures of neighborhood risk.

[Coverage by species](tables/06_intake_locations/coverage_by_species.csv) ·
[Coverage by intake type](tables/06_intake_locations/coverage_by_intake_type.csv) ·
[Location precision](tables/06_intake_locations/location_precision.csv) ·
[Shelter reference](tables/06_intake_locations/shelter_reference.csv) ·
[Map counts and exclusions](tables/06_intake_locations/spatial_audit.csv)

## Definitions and reproduction

- Intake composition percentages use all intake records of the species.
  Monthly species percentages use the annual species total; monthly cat-age
  percentages use that month's cat total.
- Outcome composition percentages use all outcome records of the species.
  Trait adoption percentages use all outcome records in the specific group.
  Displayed percentages are rounded and may not sum to exactly 100%.
- Approximate ages use 12 months per recorded year, 1 per recorded month,
  84/365.25 per recorded week, and 12/365.25 per recorded day. Cutoffs are 6,
  12, 36, and 84 months, with each lower boundary included. These are analytical
  intervals, not standardized biological life stages.
- `0 years` remains separate because its age precision is unclear. Blank
  values are retained as `Not recorded` when present. Literal `Unknown`
  categories remain separate from blanks.
- Female combines `Intact Female` and `Spayed Female`; male combines
  `Intact Male` and `Neutered Male`. Sterilization is a separate attribute.
  Original breed and color labels, including `Mix` and compound labels,
  are not collapsed.
- The spatial script matches records with Animal ID, Intake Date, Intake Time,
  and Intake Type; it verifies unique event keys and agreement in the shared
  source fields.
- This analysis does not match intake and outcome events, calculate length of
  stay, analyze repeat intakes, or estimate causal effects.

Use the [six scripts and run instructions](../../code/basic_analysis/README.md)
to reproduce the figures and CSVs. The existing input files are not modified.
