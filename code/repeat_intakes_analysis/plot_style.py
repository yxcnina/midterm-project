import matplotlib.pyplot as plt
import seaborn as sns

MAIN_COLOR = "#0173B2"
SECONDARY_COLOR = "#DE8F05"
ACCENT_COLOR = "#029E73"
WARNING_COLOR = "#D55E00"
NEUTRAL_COLOR = "#949494"

CATEGORY_PALETTE = [
    "#0173B2",
    "#DE8F05",
    "#029E73",
    "#D55E00",
    "#CC78BC",
    "#CA9161",
    "#56B4E9",
    "#949494",
]

def set_plot_style():
    sns.set_theme(
        style="whitegrid",
        context="talk",
        palette="colorblind",
    )

    plt.rcParams.update(
        {
            "figure.figsize": (10, 6),
            "figure.dpi": 120,
            "savefig.dpi": 300,
            "axes.titleweight": "bold",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "legend.frameon": False,
        }
    )