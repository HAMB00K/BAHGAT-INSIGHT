# -*- coding: utf-8 -*-
"""
Génère les planches PNG du dictionnaire de données (annexe B du rapport),
dans la charte graphique de la plateforme.

Usage :  python make_data_dictionary.py
Sortie : dico_sources.png, dico_entrepot.png, dico_ml.png (300 dpi)
"""
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = Path(__file__).parent

PAGE = "#F9F9F7"
CARD = "#FCFCFB"
HEAD = "#F0EFEC"
BORDER = "#D8D6CE"
GRID = "#E1E0D9"
INK = "#0B0B0B"
MUT = "#52514E"
MUT2 = "#898781"
CHIP = {
    "DIM":     "#2A78D6",
    "FAIT":    "#1C5CAB",
    "AGRÉGAT": "#159A6B",
    "ML":      "#4A3AA7",
    "OPS":     "#D28F00",
    "CSV":     "#52514E",
}

plt.rcParams["font.family"] = ["Segoe UI", "DejaVu Sans"]

LINE_H = 1.55          # hauteur d'une ligne de texte (unités internes)
PAD = 1.05             # marge verticale dans une rangée


def render_table(filename, title, subtitle, columns, rows, note=None):
    """columns: [(label, x, width, align)] ; rows: [dict col->text, 'chip'->str]"""
    # --- pré-calcul des hauteurs (wrap de la colonne 'wrap') -----------------
    wrapped = []
    for row in rows:
        cell_lines = {}
        for label, x, w, align, wrap_chars in columns:
            txt = row.get(label, "")
            lines = textwrap.wrap(txt, wrap_chars) if wrap_chars else [txt]
            cell_lines[label] = lines or [""]
        n = max(len(v) for v in cell_lines.values())
        wrapped.append((cell_lines, n))

    header_h = 2.6
    title_h = 6.2
    note_h = 3.2 if note else 0.8
    total_h = title_h + header_h + sum(n * LINE_H + 2 * PAD for _, n in wrapped) + note_h + 2.5

    fig_w = 12.4
    fig, ax = plt.subplots(figsize=(fig_w, total_h * 0.118), dpi=300)
    fig.patch.set_facecolor(PAGE)
    ax.set_facecolor(PAGE)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, total_h)
    ax.axis("off")

    y = total_h - 2.0
    ax.text(2.5, y, title, fontsize=14.5, fontweight="bold", color=INK, va="top")
    ax.text(2.5, y - 2.9, subtitle, fontsize=8.5, color=MUT, va="top")
    y -= title_h

    # --- carte englobante ----------------------------------------------------
    table_top = y
    table_h = header_h + sum(n * LINE_H + 2 * PAD for _, n in wrapped)
    ax.add_patch(FancyBboxPatch((2.5, table_top - table_h), 95, table_h, zorder=2,
                                boxstyle="round,pad=0,rounding_size=0.9",
                                fc=CARD, ec=BORDER, lw=1.1))

    # --- en-têtes ------------------------------------------------------------
    ax.add_patch(FancyBboxPatch((2.5, table_top - header_h), 95, header_h, zorder=3,
                                boxstyle="round,pad=0,rounding_size=0.9",
                                fc=HEAD, ec="none"))
    ax.add_patch(plt.Rectangle((2.5, table_top - header_h), 95, header_h / 2,
                               zorder=3, fc=HEAD, ec="none"))
    for label, x, w, align, _ in columns:
        tx = x + w - 0.8 if align == "right" else x
        ax.text(tx, table_top - header_h / 2, label.upper(), zorder=5,
                fontsize=7.2, fontweight="bold", color=MUT,
                ha="right" if align == "right" else "left", va="center")

    # --- rangées -------------------------------------------------------------
    ry = table_top - header_h
    for i, (cell_lines, n) in enumerate(wrapped):
        rh = n * LINE_H + 2 * PAD
        if i > 0:
            ax.plot([3.3, 96.7], [ry, ry], color=GRID, lw=0.8, zorder=4)
        chip = rows[i].get("chip")
        for label, x, w, align, _ in columns:
            lines = cell_lines[label]
            first_y = ry - PAD - LINE_H / 2
            if label == "type" and chip:
                col = CHIP.get(chip, MUT)
                cw = min(1.3 * len(chip) + 2.0, 8.6)   # ne pas déborder sur la colonne suivante
                ax.add_patch(FancyBboxPatch((x, first_y - 0.85), cw, 1.9, zorder=5,
                                            boxstyle="round,pad=0,rounding_size=0.55",
                                            fc=col, ec="none"))
                ax.text(x + cw / 2, first_y + 0.08, chip, zorder=6, fontsize=6.4,
                        fontweight="bold", color="white", ha="center", va="center")
                continue
            bold = (label == columns[0][0])
            for j, ln in enumerate(lines):
                tx = x + w - 0.8 if align == "right" else x
                ax.text(tx, first_y - j * LINE_H, ln, zorder=5,
                        fontsize=7.6 if bold else 7.3,
                        fontweight="bold" if bold else "normal",
                        color=INK if bold else MUT,
                        ha="right" if align == "right" else "left", va="center")
        ry -= rh

    if note:
        ax.text(2.5, ry - 2.4, note, fontsize=7.2, color=MUT2, va="top", style="italic")

    out = HERE / filename
    fig.savefig(out, bbox_inches="tight", facecolor=PAGE, pad_inches=0.22)
    plt.close(fig)
    print(f"OK -> {out}")


# ============================================================================
# B.1 — extractions sources
# ============================================================================
cols = [("fichier", 4.5, 22, "left", None),
        ("type", 27.5, 6, "left", None),
        ("≈ lignes", 34, 8.5, "right", None),
        ("contenu", 45, 52, "left", 64)]
render_table(
    "dico_sources.png",
    "Annexe B.1 — Extractions sources (data/raw)",
    "Neuf fichiers CSV simulant les systèmes sources · fenêtre 2023-07-01 → 2026-06-30 · montants en AED",
    cols,
    [
        {"fichier": "sales_transactions.csv", "chip": "CSV", "≈ lignes": "1 032 000",
         "contenu": "Lignes de ticket POS / e-commerce — contient les défauts injectés : doublons d'export, "
                    "dates ISO et JJ/MM/AAAA mélangées, IDs client manquants, quantités négatives, prix nuls, "
                    "libellés de paiement incohérents"},
        {"fichier": "returns.csv", "chip": "CSV", "≈ lignes": "38 000",
         "contenu": "Retours produits avec motif, dont une rafale frauduleuse injectée (janv. 2026)"},
        {"fichier": "customers.csv", "chip": "CSV", "≈ lignes": "40 000",
         "contenu": "Clients fidélité — casse des villes incohérente, e-mails dupliqués"},
        {"fichier": "products.csv", "chip": "CSV", "≈ lignes": "320",
         "contenu": "Référentiel produits : catégorie, marque, prix et coût unitaires"},
        {"fichier": "stores.csv", "chip": "CSV", "≈ lignes": "18",
         "contenu": "16 magasins physiques (EAU, KSA, Bahreïn) + 2 sites e-commerce"},
        {"fichier": "suppliers.csv", "chip": "CSV", "≈ lignes": "40",
         "contenu": "Fournisseurs : pays, délai de livraison, score de fiabilité"},
        {"fichier": "marketing_spend.csv", "chip": "CSV", "≈ lignes": "5 480",
         "contenu": "Dépense quotidienne par canal et campagne (Ramadan Nights, DSF, White Friday…)"},
        {"fichier": "web_traffic.csv", "chip": "CSV", "≈ lignes": "1 096",
         "contenu": "Sessions, visiteurs, taux de rebond et de conversion du canal e-commerce"},
        {"fichier": "inventory_snapshots.csv", "chip": "CSV", "≈ lignes": "167 000",
         "contenu": "Stock mensuel par magasin × produit, jours de rupture (crise injectée oct. 2025)"},
    ],
    note="Les volumes exacts varient légèrement d'une génération à l'autre (tirages aléatoires) ; "
         "la graine fixée rend chaque exécution reproductible à l'identique.")

# ============================================================================
# B.2 — entrepôt
# ============================================================================
cols = [("table", 4.5, 20, "left", None),
        ("type", 25, 9, "left", None),
        ("clé / grain", 35, 17, "left", 22),
        ("colonnes principales", 53, 36, "left", 46),
        ("≈ lignes", 89.5, 7.5, "right", None)]
render_table(
    "dico_entrepot.png",
    "Annexe B.2 — Entrepôt : dimensions, faits et agrégats",
    "Schéma en étoile (Kimball) chargé dans SQLite par le pipeline ETL · index sur toutes les clés de jointure",
    cols,
    [
        {"table": "dim_date", "chip": "DIM", "clé / grain": "date_key (jour)",
         "colonnes principales": "date, year, month, quarter, day_name, is_weekend, is_ramadan, is_eid, retail_event",
         "≈ lignes": "1 096"},
        {"table": "dim_store", "chip": "DIM", "clé / grain": "store_id",
         "colonnes principales": "store_name, city, country, store_type, sqm, opened_date",
         "≈ lignes": "18"},
        {"table": "dim_product", "chip": "DIM", "clé / grain": "product_id",
         "colonnes principales": "product_name, category, subcategory, brand, unit_price, unit_cost, margin_pct, supplier_id",
         "≈ lignes": "320"},
        {"table": "dim_customer", "chip": "DIM", "clé / grain": "customer_id",
         "colonnes principales": "first/last_name, gender, birth_year, age_band, city, join_date, email, dup_email_flag",
         "≈ lignes": "40 000"},
        {"table": "dim_supplier", "chip": "DIM", "clé / grain": "supplier_id",
         "colonnes principales": "supplier_name, country, lead_time_days, reliability_score",
         "≈ lignes": "40"},
        {"table": "fact_sales", "chip": "FAIT", "clé / grain": "transaction_id (ligne de ticket)",
         "colonnes principales": "4 FK dimensions, quantity, unit_price, discount_pct, gross/discount/net/cost/margin_amount, "
                                 "payment_method, sales_channel",
         "≈ lignes": "1,03 M"},
        {"table": "fact_returns", "chip": "FAIT", "clé / grain": "return_id (retour)",
         "colonnes principales": "transaction_id, date_key, store/product/customer_id, qty_returned, refund_amount, reason",
         "≈ lignes": "38 000"},
        {"table": "fact_marketing", "chip": "FAIT", "clé / grain": "jour × canal",
         "colonnes principales": "channel, campaign, spend_aed, impressions, clicks",
         "≈ lignes": "5 480"},
        {"table": "fact_web_traffic", "chip": "FAIT", "clé / grain": "jour",
         "colonnes principales": "sessions, unique_visitors, bounce_rate, avg_session_sec, online_orders, conversion_rate",
         "≈ lignes": "1 096"},
        {"table": "fact_inventory", "chip": "FAIT", "clé / grain": "mois × magasin × produit",
         "colonnes principales": "units_sold_month, units_on_hand, stockout_days",
         "≈ lignes": "167 000"},
        {"table": "agg_daily_* (4 tables)", "chip": "AGRÉGAT", "clé / grain": "jour (× magasin / catégorie)",
         "colonnes principales": "orders, units, gross/net_revenue, margin, refunds, marketing_spend — pré-calculées "
                                 "pour des tableaux de bord < 100 ms",
         "≈ lignes": "44 000"},
    ])

# ============================================================================
# B.3 — sorties ML & exploitation
# ============================================================================
render_table(
    "dico_ml.png",
    "Annexe B.3 — Sorties machine learning et tables d'exploitation",
    "Résultats des trois modules ML réinjectés dans l'entrepôt, consommés par l'application Flask et Power BI",
    cols,
    [
        {"table": "forecast_daily", "chip": "ML", "clé / grain": "jour × périmètre",
         "colonnes principales": "actual, forecast, lo, hi (intervalle 95 %), model, kind (history/forecast) — "
                                 "périmètres : compagnie + 8 catégories",
         "≈ lignes": "2 430"},
        {"table": "forecast_metrics", "chip": "ML", "clé / grain": "modèle × périmètre",
         "colonnes principales": "mape, rmse, is_champion (backtest 60 jours de holdout)",
         "≈ lignes": "10"},
        {"table": "anomalies", "chip": "ML", "clé / grain": "anomaly_id (alerte)",
         "colonnes principales": "date_key, store_id, metric, method, value, expected, score, severity, description",
         "≈ lignes": "variable"},
        {"table": "anomaly_ground_truth / _validation", "chip": "ML", "clé / grain": "incident injecté",
         "colonnes principales": "label, fenêtre start/end, stores, detected, n_alerts, methods — mesure du rappel",
         "≈ lignes": "7"},
        {"table": "customer_segments", "chip": "ML", "clé / grain": "customer_id",
         "colonnes principales": "recency, frequency, monetary, tenure_days, segment, churn_risk (0-1), clv_annual",
         "≈ lignes": "37 000"},
        {"table": "segment_profiles", "chip": "ML", "clé / grain": "segment",
         "colonnes principales": "customers, moyennes R/F/M, total_revenue, revenue_share_pct, avg_churn_risk, avg_clv",
         "≈ lignes": "5"},
        {"table": "dq_log", "chip": "OPS", "clé / grain": "correction qualité",
         "colonnes principales": "issue, rows_affected, action — le rapport de fiabilisation affiché dans l'application",
         "≈ lignes": "10"},
        {"table": "pipeline_runs", "chip": "OPS", "clé / grain": "étape d'exécution",
         "colonnes principales": "stage (EXTRACT/TRANSFORM/LOAD/TOTAL), seconds, rows_out, run_at",
         "≈ lignes": "4"},
    ],
    note="Grain, clés et mesures détaillés colonne par colonne dans docs/data_dictionary.md du dépôt.")
