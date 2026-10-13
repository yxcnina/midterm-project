# Basic analysis code

Each of the six questions has one standalone script. Its filename matches its
figure folder under `artifacts/basic_analysis/figures/` and its table folder
under `artifacts/basic_analysis/tables/`.

| Script | Question | Input |
| --- | --- | --- |
| [01_intake_profile.py](01_intake_profile.py) | What are the age, sex, and breed profiles of cat and dog intakes? | Full cleaned intakes |
| [02_intake_timing.py](02_intake_timing.py) | When are intake records most frequent? | Full cleaned intakes |
| [03_intake_context.py](03_intake_context.py) | How do intake types and conditions differ? | Full cleaned intakes |
| [04_outcome_profile.py](04_outcome_profile.py) | What outcomes are recorded for cats and dogs? | Full cleaned outcomes |
| [05_trait_comparisons.py](05_trait_comparisons.py) | How does the adoption share of outcome records vary by recorded traits? | Full cleaned outcomes |
| [06_intake_locations.py](06_intake_locations.py) | What do mapped intake concentrations represent? | Full and geocoded intakes |

## Run the analysis

From the repository root, install the packages once:

```bash
python -m pip install -r requirements.txt
```

Run any theme independently, or run all six in this order:

```bash
python code/basic_analysis/01_intake_profile.py
python code/basic_analysis/02_intake_timing.py
python code/basic_analysis/03_intake_context.py
python code/basic_analysis/04_outcome_profile.py
python code/basic_analysis/05_trait_comparisons.py
python code/basic_analysis/06_intake_locations.py
```

The scripts read existing files in `data/processed/`. They create their own
output folders and save only PNG figures and CSV summary tables. Re-running a
script replaces its outputs. It does not rewrite the input files. The paths
are based on the script location, so no personal computer path is needed.

## Reading the code

Functions separate data preparation, summary calculations, and plotting.
Each function has a short docstring describing its input and output, and
`main()` connects the steps. Importing a script does not run the analysis.
Formatting follows Black's 88-character line limit and consistent double quotes.

All six scripts can be read separately. They use familiar Pandas and Matplotlib
operations rather than a custom plotting framework. Age conversion appears in
the relevant scripts so each theme remains self-contained.

The observation is a recorded event, not necessarily a unique animal. Intakes
and outcomes are not matched into a cohort. Age text recorded as `0 years` is
kept separate, and original breed/color labels are preserved. In theme 05,
adoption percentages describe outcome records and are not estimates of an
intake animal's eventual adoption probability.

See the [results, figures, and definitions](../../artifacts/basic_analysis/README.md)
for the findings and the denominator used in each theme.
