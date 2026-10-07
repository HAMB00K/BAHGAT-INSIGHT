# -*- coding: utf-8 -*-
"""
Génère schema_etoile.png — schéma en étoile de l'entrepôt Bahgat Insight,
dans la charte graphique de la plateforme (fond #F9F9F7, cartes arrondies).

Usage :  python make_star_schema.py
Sortie : schema_etoile.png (300 dpi) dans le même dossier, à copier dans le
         dossier d'assets Overleaf pour la figure \\ref{fig:etoile}.
"""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

OUT = Path(__file__).with_name("schema_etoile.png")

# ---- charte -----------------------------------------------------------------
PAGE = "#F9F9F7"
CARD = "#FCFCFB"
BORDER = "#D8D6CE"
INK = "#0B0B0B"
MUT = "#52514E"
MUT2 = "#898781"
LINE = "#B9B7AF"
NAVY = "#1C5CAB"
BLUE = "#2A78D6"
GREEN = "#159A6B"
AMBER = "#D28F00"
VIOLET = "#4A3AA7"
GOLD = "#B45309"

plt.rcParams["font.family"] = ["Segoe UI", "DejaVu Sans"]

fig, ax = plt.subplots(figsize=(12.4, 8.2), dpi=300)
fig.patch.set_facecolor(PAGE)
ax.set_facecolor(PAGE)
ax.set_xlim(0, 100)
ax.set_ylim(0, 70)
ax.axis("off")


def table_card(x, y, w, h, title, subtitle, color, rows, title_size=11.5):
    """Carte de table : bandeau coloré + liste de colonnes taguées PK/FK."""
    # ombre douce
    ax.add_patch(FancyBboxPatch((x + 0.35, y - 0.45), w, h, zorder=2,
                                boxstyle="round,pad=0,rounding_size=1.1",
                                fc="#000000", ec="none", alpha=0.06))
    # corps
    ax.add_patch(FancyBboxPatch((x, y), w, h, zorder=3,
                                boxstyle="round,pad=0,rounding_size=1.1",
                                fc=CARD, ec=BORDER, lw=1.1))
    # bandeau titre (arrondi haut, carré bas)
    bh = 6.2 if subtitle else 4.6
    ax.add_patch(FancyBboxPatch((x, y + h - bh), w, bh, zorder=4,
                                boxstyle="round,pad=0,rounding_size=1.1",
                                fc=color, ec="none"))
    ax.add_patch(Rectangle((x, y + h - bh), w, bh / 2, zorder=4, fc=color, ec="none"))
    ax.text(x + 1.6, y + h - (2.1 if subtitle else 2.45), title, zorder=6,
            fontsize=title_size, fontweight="bold", color="white", va="center")
    if subtitle:
        ax.text(x + 1.6, y + h - 4.7, subtitle, zorder=6, fontsize=7.2,
                color="white", alpha=0.92, va="center")
    # colonnes
    step = (h - bh - 1.6) / max(len(rows), 1)
    for i, (tag, name, desc) in enumerate(rows):
        ry = y + h - bh - 1.6 - i * step
        tx = x + 1.6
        if tag:
            ax.text(tx, ry, tag, zorder=6, fontsize=7.3, fontweight="bold",
                    color=GOLD if tag == "PK" else BLUE, va="center")
            tx += 3.4
        ax.text(tx, ry, name, zorder=6, fontsize=8.2, color=INK,
                va="center", fontweight="semibold" if tag == "PK" else "normal")
        if desc:
            ax.text(x + w - 1.6, ry, desc, zorder=6, fontsize=7.0,
                    color=MUT2, va="center", ha="right")


def link(x1, y1, x2, y2):
    """Relation plusieurs-à-un : ∗ côté fait, 1 côté dimension."""
    ax.plot([x1, x2], [y1, y2], color=LINE, lw=1.6, zorder=1,
            solid_capstyle="round")
    fx, fy = x1 + (x2 - x1) * 0.22, y1 + (y2 - y1) * 0.22
    dx, dy = x1 + (x2 - x1) * 0.78, y1 + (y2 - y1) * 0.78
    for px, py, t in ((fx, fy, "∗"), (dx, dy, "1")):
        ax.text(px, py, t, fontsize=9, fontweight="bold", color=MUT,
                ha="center", va="center", zorder=5,
                bbox=dict(boxstyle="circle,pad=0.22", fc=PAGE, ec=LINE, lw=1.0))


# ---- titre ------------------------------------------------------------------
ax.text(3, 67.2, "Entrepôt de données — schéma en étoile (Kimball)",
        fontsize=15.5, fontweight="bold", color=INK)
ax.text(3, 64.6, "Table de faits centrale au grain « ligne de ticket », "
                 "dimensions descriptives partagées · SQLite, ≈ 1,3 M de lignes au total",
        fontsize=9, color=MUT)

# ---- fait central -----------------------------------------------------------
FX, FY, FW, FH = 36.5, 17.5, 27, 33
table_card(FX, FY, FW, FH, "FACT_SALES",
           "grain : 1 ligne de ticket  ·  ≈ 1 030 000 lignes",
           NAVY, [
               ("PK", "transaction_id", ""),
               ("FK", "date_key", "→ dim_date"),
               ("FK", "store_id", "→ dim_store"),
               ("FK", "product_id", "→ dim_product"),
               ("FK", "customer_id", "→ dim_customer"),
               ("", "quantity · unit_price", "mesures"),
               ("", "discount_pct · discount_amount", ""),
               ("", "gross / net_amount", ""),
               ("", "cost / margin_amount", ""),
               ("", "payment_method", ""),
               ("", "sales_channel", "In-Store / Online"),
           ], title_size=13)

# ---- dimensions -------------------------------------------------------------
table_card(4, 41.5, 24, 20.5, "DIM_DATE", "1 096 jours · calendrier enrichi", BLUE, [
    ("PK", "date_key", ""),
    ("", "date · year · month · quarter", ""),
    ("", "day_name · is_weekend", ""),
    ("", "is_ramadan · is_eid", "Hijri"),
    ("", "retail_event", "DSF, White Friday…"),
])
table_card(72, 41.5, 24, 20.5, "DIM_STORE", "18 magasins · 3 pays", GREEN, [
    ("PK", "store_id", ""),
    ("", "store_name · city · country", ""),
    ("", "store_type", "flagship, mall…"),
    ("", "sqm · opened_date", ""),
])
table_card(4, 4.5, 24, 20.5, "DIM_CUSTOMER", "40 000 clients fidélité", VIOLET, [
    ("PK", "customer_id", ""),
    ("", "first / last_name · gender", ""),
    ("", "birth_year · age_band", ""),
    ("", "city · join_date · email", ""),
])
table_card(72, 4.5, 24, 20.5, "DIM_PRODUCT", "320 produits · 8 catégories", AMBER, [
    ("PK", "product_id", ""),
    ("", "product_name · brand", ""),
    ("", "category · subcategory", ""),
    ("", "unit_price · unit_cost", ""),
    ("FK", "supplier_id", "→ dim_supplier"),
])

# ---- relations (ancrées sur les BORDS des cartes) ---------------------------
link(FX, FY + FH - 5, 28, 49.5)                    # fact -> dim_date
link(FX + FW, FY + FH - 5, 72, 49.5)               # fact -> dim_store
link(FX, FY + 5, 28, 17)                           # fact -> dim_customer
link(FX + FW, FY + 5, 72, 17)                      # fact -> dim_product

# ---- note de bas de schéma --------------------------------------------------
ax.add_patch(FancyBboxPatch((30, 6.2), 40, 6.6, zorder=3,
                            boxstyle="round,pad=0,rounding_size=1.0",
                            fc="#F0EFEC", ec=BORDER, lw=1.0))
ax.text(50, 10.4, "Le même modèle porte aussi :", fontsize=8, color=MUT,
        ha="center", zorder=5, fontweight="bold")
ax.text(50, 8.0, "fact_returns · fact_marketing · fact_web_traffic · fact_inventory "
                 "(mêmes dimensions)\ndim_supplier · tables d'agrégats · sorties ML "
                 "(prévisions, anomalies, segments)",
        fontsize=7.4, color=MUT, ha="center", va="center", zorder=5)

fig.savefig(OUT, bbox_inches="tight", facecolor=PAGE, pad_inches=0.25)
print(f"OK -> {OUT}")
