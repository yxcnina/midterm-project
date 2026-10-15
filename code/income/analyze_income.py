import argparse

from income_sample import OUTPUT_DIR


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage",
        choices=["all", "sample", "intakes", "composition", "outcomes"],
        default="all",
        help="Default: all. Individual stages are useful while developing the code.",
    )
    stage=parser.parse_args().stage
    if stage in ["all", "sample"]:
        from income_sample import main as run_sample
        run_sample()
    if stage in ["all", "intakes"]:
        from income_intakes import main as run_intakes
        run_intakes()
    if stage in ["all", "composition"]:
        from income_composition import main as run_composition
        run_composition()
    if stage in ["all", "outcomes"]:
        from income_outcomes import main as run_outcomes
        run_outcomes()
    print("\nFinished. Tables and figures are in:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
