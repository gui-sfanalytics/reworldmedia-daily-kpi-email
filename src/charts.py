import os
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


PURPLE = "#76206f"
ORANGE = "#ff7f2a"
GREY = "#cfcfcf"
GRID = "#dddddd"


def format_thousands(x, pos):
    return f"{int(x):,}".replace(",", " ")


def create_subscription_charts(
    output_path,
    months,
    sliding_year,
    sliding_year_n1,
    objectifs,
    consolidated,
    consolidated_n1,
    consolidated_obj,
    months_ytd
):

    fig = plt.figure(figsize=(7.2, 7.4), dpi=100)

    # fond global (comme le body email)
    fig.patch.set_facecolor("#f2f2f2")

    # ajout d'une "card"
    from matplotlib.patches import FancyBboxPatch

    card = FancyBboxPatch(
        (0.01, 0.02),
        0.98,
        0.96,
        boxstyle="round,pad=0.015,rounding_size=0.03",
        linewidth=0,
        facecolor="white",
        transform=fig.transFigure,
        zorder=-10
    )
    fig.add_artist(card)


    # -----------------------------
    # CHART 1
    # -----------------------------
    ax1 = fig.add_axes([0.08, 0.60, 0.84, 0.25])

    ax1.plot(months, objectifs, color=ORANGE, linewidth=1.4, linestyle=(0, (2, 2)), label="Objectifs")
    ax1.plot(months, sliding_year_n1, color=GREY, linewidth=1.8, label="Année glissante N-1")
    ax1.plot(months, sliding_year, color=PURPLE, linewidth=2.2, label="Année glissante")

    ax1.set_title("Nombre d'abonnements sur 12 mois glissants", loc="left", fontsize=10, pad=30)
    ax1.axhline(ax1.get_ylim()[1], color="#cfcfcf", linewidth=0.8)

    ax1.grid(axis="y", color=GRID, linestyle=(0, (3, 4)), linewidth=0.7)
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.spines["left"].set_color("#dddddd")
    ax1.spines["bottom"].set_color("#dddddd")
    ax1.tick_params(axis="x", labelsize=9, length=0, pad=10)
    ax1.tick_params(axis="y", labelsize=8)
    ax1.yaxis.set_major_formatter(FuncFormatter(format_thousands))
  
  
    max_y_1 = max(
        max(sliding_year),
        max(sliding_year_n1),
        max(objectifs)
    )

    ax1.set_ylim(0, max_y_1 * 1.18)

    for i, value in enumerate(sliding_year):
        ax1.text(i, value + max_y_1 * 0.03, f"{value}", color=PURPLE, fontsize=8, ha="center")

    ax1.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.18),
        ncol=3,
        frameon=False,
        fontsize=8,
        handlelength=1.8,
        prop={"weight": "bold", "size": 8}
    )

    # -----------------------------
    # CHART 2
    # -----------------------------
    ax2 = fig.add_axes([0.08, 0.18, 0.84, 0.25])

    ax2.plot(months_ytd, consolidated_obj, color=ORANGE, linewidth=1.4, linestyle=(0, (2, 2)), label="Objectifs")
    ax2.plot(months_ytd, consolidated_n1, color=GREY, linewidth=1.8, label="Année cumulée N-1")
    ax2.plot(months_ytd, consolidated, color=PURPLE, linewidth=2.2, label="Année cumulée")

    ax2.set_title("Nombre d'abonnements cumulés", loc="left", fontsize=10, pad=30)
    ax2.axhline(ax2.get_ylim()[1], color="#cfcfcf", linewidth=0.8)

    ax2.grid(axis="y", color=GRID, linestyle=(0, (3, 4)), linewidth=0.7)
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.spines["left"].set_color("#dddddd")
    ax2.spines["bottom"].set_color("#dddddd")
    ax2.tick_params(axis="x", labelsize=9, length=0, pad=10)
    ax2.tick_params(axis="y", labelsize=8)
    ax2.yaxis.set_major_formatter(FuncFormatter(format_thousands))

    max_y_2 = max(
        max(consolidated),
        max(consolidated_n1),
        max(consolidated_obj)
    )

    ax2.set_ylim(0, max_y_2 * 1.15)

    for i, value in enumerate(consolidated):
        ax2.text(i, value + max_y_2 * 0.03, f"{value}", color=PURPLE, fontsize=8, ha="center")

    ax2.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.18),
        ncol=3,
        frameon=False,
        fontsize=8,
        handlelength=1.8,
        prop={"weight": "bold", "size": 8}
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, facecolor=fig.get_facecolor())
    plt.close()