"""
Synthetic data generator for the Bahgat Insight Platform.

Simulates 3 years of operations of "Al Noor Retail Group", a fictional
omni-channel retailer operating in the GCC (UAE, KSA, Bahrain):

    - 18 stores (flagships, malls, street stores, 2 e-commerce sites)
    - 320 products across 8 categories
    - 40,000 loyalty customers
    - ~1,000,000 sales line items with realistic seasonality:
      Ramadan / Eid, Dubai Shopping Festival, White Friday,
      back-to-school, weekends, growth trend, promotions
    - Injected operational anomalies (POS outage, flood, pricing bug,
      returns-fraud burst...) that the ML layer must detect
    - Injected data-quality issues (duplicates, mixed date formats,
      missing IDs, bad values) that the ETL layer must fix

Everything is deterministic (fixed random seed) so results are
reproducible for the demo.

Run from the project root:
    python -m src.data_generation.generate_data
"""
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.config import (
    RAW_DIR, LOG_DIR, SIM_START, SIM_END, RANDOM_SEED,
)

rng = np.random.default_rng(RANDOM_SEED)

# ===========================================================================
# 1. Reference data
# ===========================================================================

STORES = [
    # store_id, name, city, country, store_type, sqm, base_orders_per_day
    ("S01", "Dubai Mall Flagship",      "Dubai",          "UAE",     "Flagship", 2600, 32),
    ("S02", "Mall of the Emirates",     "Dubai",          "UAE",     "Mall",     1400, 17),
    ("S03", "Deira City Centre",        "Dubai",          "UAE",     "Mall",     1150, 15),
    ("S04", "Dubai Marina Walk",        "Dubai",          "UAE",     "Street",    620,  9),
    ("S05", "Jumeirah Road",            "Dubai",          "UAE",     "Street",    540,  8),
    ("S06", "Yas Mall",                 "Abu Dhabi",      "UAE",     "Mall",     1300, 16),
    ("S07", "Abu Dhabi Corniche",       "Abu Dhabi",      "UAE",     "Street",    580,  9),
    ("S08", "Al Wahda Mall",            "Abu Dhabi",      "UAE",     "Mall",     1050, 14),
    ("S09", "Sahara Centre",            "Sharjah",        "UAE",     "Mall",      980, 13),
    ("S10", "Al Majaz Waterfront",      "Sharjah",        "UAE",     "Street",    460,  8),
    ("S11", "Manar Mall",               "Ras Al Khaimah", "UAE",     "Mall",      760, 10),
    ("S12", "Riyadh Park Flagship",     "Riyadh",         "KSA",     "Flagship", 2400, 30),
    ("S13", "Kingdom Centre",           "Riyadh",         "KSA",     "Mall",     1200, 15),
    ("S14", "Red Sea Mall",             "Jeddah",         "KSA",     "Mall",     1100, 14),
    ("S15", "Tahlia Street",            "Jeddah",         "KSA",     "Street",    600,  9),
    ("S16", "Manama City Centre",       "Manama",         "Bahrain", "Mall",      900, 12),
    ("S17", "Online Store UAE",         "Dubai",          "UAE",     "Online",      0, 42),
    ("S18", "Online Store KSA",         "Riyadh",         "KSA",     "Online",      0, 28),
]

CATEGORIES = [
    # name, base demand share, margin, price_low, price_high, n_products
    ("Electronics",          0.18, 0.22,   89, 4999, 55),
    ("Fashion",              0.22, 0.55,   49,  899, 60),
    ("Home & Living",        0.10, 0.45,   29, 2499, 45),
    ("Beauty & Fragrance",   0.12, 0.60,   39,  699, 40),
    ("Gourmet Grocery",      0.16, 0.35,   15,  199, 35),
    ("Sports & Outdoor",     0.08, 0.42,   59, 1299, 35),
    ("Kids & Toys",          0.08, 0.48,   19,  499, 30),
    ("Jewellery & Watches",  0.06, 0.52,  299, 9999, 20),
]

SUBCATEGORIES = {
    "Electronics":         ["Smartphones", "Laptops", "Audio", "Wearables", "Accessories"],
    "Fashion":             ["Menswear", "Womenswear", "Footwear", "Bags & Accessories"],
    "Home & Living":       ["Furniture", "Decor", "Kitchen & Dining"],
    "Beauty & Fragrance":  ["Skincare", "Makeup", "Perfume"],
    "Gourmet Grocery":     ["Coffee & Tea", "Chocolate & Confectionery", "Organic Pantry"],
    "Sports & Outdoor":    ["Fitness Equipment", "Outdoor Gear", "Sportswear"],
    "Kids & Toys":         ["Toys & Games", "Baby Essentials", "School Supplies"],
    "Jewellery & Watches": ["Watches", "Fine Jewellery"],
}

BRANDS = {
    "Electronics":         ["Novatek", "Aurion", "PulseWave", "Zenora", "Voltix"],
    "Fashion":             ["Maison Layl", "Urban Dune", "Sable & Co", "Nomad Thread", "Lujain"],
    "Home & Living":       ["Casa Amara", "Dar Living", "Oasis Home", "Mishkal"],
    "Beauty & Fragrance":  ["Oud Royale", "Lumiere", "Bahar Beauty", "Velvet Rose"],
    "Gourmet Grocery":     ["Al Dhahab Foods", "Terra Verde", "Safwa Select", "Kanz Gourmet"],
    "Sports & Outdoor":    ["Falcon Athletics", "DuneTrail", "CoreFit", "Sahara Peak"],
    "Kids & Toys":         ["Little Wonders", "PlayNest", "Farah Kids"],
    "Jewellery & Watches": ["Al Zain Heritage", "Meridian Time", "Noor Jewels"],
}

PRODUCT_NOUNS = {
    "Smartphones": ["Smartphone X", "Smartphone Pro", "Smartphone Lite", "Foldable Phone"],
    "Laptops": ["Ultrabook 14", "Notebook 15", "Gaming Laptop 16", "Convertible 13"],
    "Audio": ["Wireless Earbuds", "Noise-Cancelling Headphones", "Bluetooth Speaker", "Soundbar"],
    "Wearables": ["Smartwatch", "Fitness Band", "Smart Ring"],
    "Accessories": ["Power Bank", "Wireless Charger", "USB-C Hub", "Phone Case", "Screen Protector"],
    "Menswear": ["Linen Shirt", "Slim Chinos", "Blazer", "Polo Shirt", "Kandura Classic"],
    "Womenswear": ["Silk Abaya", "Maxi Dress", "Blouse", "Tailored Trousers", "Kimono Wrap"],
    "Footwear": ["Leather Sneakers", "Loafers", "Sandals", "Ankle Boots"],
    "Bags & Accessories": ["Tote Bag", "Crossbody Bag", "Leather Belt", "Silk Scarf"],
    "Furniture": ["Accent Chair", "Coffee Table", "Bookshelf", "Console Table"],
    "Decor": ["Ceramic Vase", "Wall Art", "Scented Candle Set", "Table Lamp"],
    "Kitchen & Dining": ["Dinnerware Set", "Chef Knife Set", "Espresso Maker", "Serving Tray"],
    "Skincare": ["Vitamin C Serum", "Hydrating Cream", "Night Repair Oil", "Sunscreen SPF50"],
    "Makeup": ["Matte Lipstick", "Eyeshadow Palette", "Foundation", "Mascara"],
    "Perfume": ["Oud Intense EDP", "Amber Musk EDP", "Rose Saffron EDP", "Citrus Vetiver EDT"],
    "Coffee & Tea": ["Specialty Arabica Beans", "Karak Chai Blend", "Matcha Set", "Turkish Coffee"],
    "Chocolate & Confectionery": ["Date Chocolate Box", "Pistachio Pralines", "Baklava Selection"],
    "Organic Pantry": ["Organic Honey", "Cold-Pressed Olive Oil", "Za'atar Blend", "Quinoa Pack"],
    "Fitness Equipment": ["Adjustable Dumbbells", "Yoga Mat Pro", "Resistance Bands", "Kettlebell"],
    "Outdoor Gear": ["Camping Tent", "Hiking Backpack", "Cooler Box", "Trekking Poles"],
    "Sportswear": ["Running Shoes", "Training Tee", "Compression Leggings", "Track Jacket"],
    "Toys & Games": ["Building Blocks Set", "RC Car", "Board Game Classic", "Plush Falcon"],
    "Baby Essentials": ["Baby Carrier", "Stroller Compact", "Feeding Set"],
    "School Supplies": ["Ergonomic Backpack", "Stationery Bundle", "Lunchbox Set"],
    "Watches": ["Chronograph Steel", "Minimalist Leather", "Diver Automatic", "Rose Gold Classic"],
    "Fine Jewellery": ["Diamond Pendant", "Gold Bangle", "Pearl Earrings", "Sapphire Ring"],
}

FIRST_NAMES = [
    "Ahmed", "Mohammed", "Omar", "Youssef", "Khalid", "Hassan", "Ali", "Tariq", "Rashid", "Salem",
    "Fatima", "Aisha", "Mariam", "Layla", "Noor", "Huda", "Sara", "Reem", "Dana", "Amal",
    "Zayed", "Hamdan", "Majid", "Saeed", "Sultan", "Nasser", "Faisal", "Abdullah", "Ibrahim", "Karim",
    "Hessa", "Latifa", "Shamma", "Moza", "Alia", "Salama", "Noura", "Jawaher", "Maha", "Lina",
    "John", "Michael", "David", "James", "Robert", "Priya", "Ananya", "Ravi", "Arjun", "Deepa",
    "Maria", "Elena", "Sophie", "Anna", "Chen", "Wei", "Yuki", "Olga", "Ivan", "Carlos",
]

LAST_NAMES = [
    "Al Maktoum", "Al Nahyan", "Al Qasimi", "Al Falasi", "Al Suwaidi", "Al Marri", "Al Mansoori",
    "Al Hammadi", "Al Shamsi", "Al Zaabi", "Al Ketbi", "Al Ameri", "Al Dhaheri", "Al Mazrouei",
    "Khan", "Sharma", "Patel", "Kumar", "Singh", "Nair", "Menon", "Iyer",
    "Smith", "Johnson", "Brown", "Garcia", "Martinez", "Silva", "Santos", "Ivanov",
    "Haddad", "Nasser", "Aoun", "Khalil", "Saleh", "Mansour", "Farah", "Najjar", "Sabbagh", "Attar",
]

CITY_WEIGHTS = {
    "Dubai": 0.34, "Abu Dhabi": 0.18, "Sharjah": 0.12, "Ras Al Khaimah": 0.05,
    "Riyadh": 0.16, "Jeddah": 0.10, "Manama": 0.05,
}

SUPPLIER_COUNTRIES = ["UAE", "KSA", "China", "India", "Turkey", "Italy", "Germany", "France", "Japan", "Vietnam"]

PAYMENT_PHYSICAL = (["Card", "Cash", "Apple Pay", "Tabby"], [0.55, 0.18, 0.17, 0.10])
PAYMENT_ONLINE = (["Card", "Apple Pay", "Tabby", "PayPal"], [0.45, 0.25, 0.20, 0.10])

RETURN_REASONS = ["Size issue", "Defective", "Changed mind", "Wrong item delivered", "Damaged in delivery", "Other"]

MARKETING_CHANNELS = [
    # channel, base daily spend AED
    ("Social Media", 5500),
    ("Search Ads", 4200),
    ("Email", 800),
    ("Influencer", 2500),
    ("Offline & Mall Media", 3800),
]

# ===========================================================================
# 2. Calendar effects
# ===========================================================================

RAMADAN = [("2024-03-11", "2024-04-08"), ("2025-03-01", "2025-03-29"), ("2026-02-18", "2026-03-18")]
EID = [("2024-04-09", "2024-04-12"), ("2025-03-30", "2025-04-02"), ("2026-03-19", "2026-03-22")]
DSF = [("2023-12-08", "2024-01-12"), ("2024-12-08", "2025-01-12"), ("2025-12-08", "2026-01-12")]
WHITE_FRIDAY = [("2023-11-24", "2023-11-27"), ("2024-11-29", "2024-12-02"), ("2025-11-28", "2025-12-01")]
BACK_TO_SCHOOL = [("2023-08-20", "2023-09-05"), ("2024-08-20", "2024-09-05"), ("2025-08-20", "2025-09-05")]
NATIONAL_DAY = [("2023-12-01", "2023-12-03"), ("2024-12-01", "2024-12-03"), ("2025-12-01", "2025-12-03")]
FLASH_SALE_DAYS = ["2024-06-16", "2025-06-15"]

# Operational anomalies injected on purpose (ground truth for the demo)
ANOMALY_EVENTS = [
    {"label": "POS system outage - Deira City Centre", "start": "2024-05-14", "end": "2024-05-14",
     "stores": ["S03"], "multiplier": 0.10},
    {"label": "Power outage - Riyadh Park Flagship", "start": "2024-09-17", "end": "2024-09-17",
     "stores": ["S12"], "multiplier": 0.25},
    {"label": "Warehouse flood - Sharjah stores", "start": "2025-02-10", "end": "2025-02-12",
     "stores": ["S09", "S10"], "multiplier": 0.35},
    {"label": "Mega flash sale (all stores)", "start": "2025-06-15", "end": "2025-06-15",
     "stores": "ALL", "multiplier": 1.75},
    {"label": "White Friday online surge", "start": "2025-11-28", "end": "2025-11-29",
     "stores": ["S17", "S18"], "multiplier": 2.10},
]
PRICING_BUG_DAY = "2025-09-03"        # Electronics sold at -50% by mistake
FRAUD_RETURN_WINDOW = ("2026-01-08", "2026-01-14")   # returns-abuse burst at S09
FRAUD_RETURN_STORE = "S09"


def _in_ranges(dates: pd.DatetimeIndex, ranges) -> np.ndarray:
    mask = np.zeros(len(dates), dtype=bool)
    for start, end in ranges:
        mask |= (dates >= pd.Timestamp(start)) & (dates <= pd.Timestamp(end))
    return mask


# ===========================================================================
# 3. Dimension generators
# ===========================================================================

def gen_stores() -> pd.DataFrame:
    df = pd.DataFrame(STORES, columns=["store_id", "store_name", "city", "country", "store_type", "sqm", "base_orders"])
    df["opened_date"] = [
        "2015-03-01", "2016-09-15", "2015-11-20", "2019-04-10", "2020-02-01",
        "2017-06-05", "2018-10-12", "2018-03-22", "2019-08-30", "2021-01-15",
        "2020-11-05", "2017-02-14", "2018-07-19", "2019-05-25", "2021-09-01",
        "2020-06-18", "2021-03-01", "2022-05-01",
    ]
    return df


def gen_products() -> pd.DataFrame:
    rows = []
    pid = 1
    for cat, share, margin, p_low, p_high, n_prod in CATEGORIES:
        subs = SUBCATEGORIES[cat]
        brands = BRANDS[cat]
        for i in range(n_prod):
            sub = subs[i % len(subs)]
            brand = brands[rng.integers(0, len(brands))]
            noun = PRODUCT_NOUNS[sub][rng.integers(0, len(PRODUCT_NOUNS[sub]))]
            # log-uniform price inside the category range, rounded to a retail price
            price = float(np.exp(rng.uniform(np.log(p_low), np.log(p_high))))
            price = round(price / 5) * 5 - 0.01
            price = max(price, p_low)
            cost = round(price * (1 - margin) * rng.uniform(0.9, 1.1), 2)
            rows.append({
                "product_id": f"P{pid:04d}",
                "product_name": f"{brand} {noun}",
                "category": cat,
                "subcategory": sub,
                "brand": brand,
                "unit_price": round(price, 2),
                "unit_cost": cost,
                "launch_date": str(pd.Timestamp("2020-01-01") + pd.Timedelta(days=int(rng.integers(0, 1200)))).split(" ")[0],
            })
            pid += 1
    return pd.DataFrame(rows)


def gen_customers(n=40_000) -> pd.DataFrame:
    cities = list(CITY_WEIGHTS.keys())
    probs = np.array(list(CITY_WEIGHTS.values()))
    probs = probs / probs.sum()
    first = rng.choice(FIRST_NAMES, size=n)
    last = rng.choice(LAST_NAMES, size=n)
    city = rng.choice(cities, size=n, p=probs)
    birth_year = rng.integers(1958, 2006, size=n)
    join_offset = rng.integers(0, 1500, size=n)  # joined during the ~4 years before sim end
    join_date = pd.Timestamp("2022-06-01") + pd.to_timedelta(join_offset, unit="D")
    gender = rng.choice(["M", "F"], size=n, p=[0.52, 0.48])
    df = pd.DataFrame({
        "customer_id": [f"C{i:06d}" for i in range(1, n + 1)],
        "first_name": first,
        "last_name": last,
        "gender": gender,
        "birth_year": birth_year,
        "city": city,
        "join_date": join_date.strftime("%Y-%m-%d"),
        "email": [f"{f.lower().replace(' ', '')}.{l.lower().replace(' ', '')}{i}@example.com"
                  for i, (f, l) in enumerate(zip(first, last))],
    })
    # spending propensity (lognormal) drives who shops often -> creates real RFM structure
    df["_propensity"] = rng.lognormal(mean=0.0, sigma=1.0, size=n)

    # --- injected quality issues: inconsistent city casing + a few duplicate emails
    idx = rng.choice(n, size=int(n * 0.04), replace=False)
    df.loc[idx[: len(idx) // 2], "city"] = df.loc[idx[: len(idx) // 2], "city"].str.upper()
    df.loc[idx[len(idx) // 2:], "city"] = df.loc[idx[len(idx) // 2:], "city"].str.lower()
    dup_idx = rng.choice(n, size=60, replace=False)
    df.loc[dup_idx, "email"] = "duplicate.account@example.com"
    return df


def gen_suppliers(products: pd.DataFrame):
    n_sup = 40
    suppliers = pd.DataFrame({
        "supplier_id": [f"SUP{i:03d}" for i in range(1, n_sup + 1)],
        "supplier_name": [f"{rng.choice(['Global', 'Prime', 'Emirates', 'Falcon', 'Atlas', 'Orient', 'Delta', 'Crown'])} "
                          f"{rng.choice(['Trading', 'Distribution', 'Imports', 'Supply Co', 'Logistics', 'Group'])} {i}"
                          for i in range(1, n_sup + 1)],
        "country": rng.choice(SUPPLIER_COUNTRIES, size=n_sup),
        "lead_time_days": rng.integers(3, 45, size=n_sup),
        "reliability_score": np.round(rng.uniform(0.72, 0.99, size=n_sup), 2),
    })
    products = products.copy()
    products["supplier_id"] = rng.choice(suppliers["supplier_id"].values, size=len(products))
    return suppliers, products


# ===========================================================================
# 4. Sales engine
# ===========================================================================

def build_day_effects(dates: pd.DatetimeIndex):
    """Returns (day_mult, discount_intensity, category_probs[day, cat])."""
    n = len(dates)
    day_mult = np.ones(n)
    disc = np.full(n, 0.10)

    ramadan = _in_ranges(dates, RAMADAN)
    eid = _in_ranges(dates, EID)
    dsf = _in_ranges(dates, DSF)
    wf = _in_ranges(dates, WHITE_FRIDAY)
    bts = _in_ranges(dates, BACK_TO_SCHOOL)
    nat = _in_ranges(dates, NATIONAL_DAY)
    flash = dates.isin(pd.to_datetime(FLASH_SALE_DAYS))
    summer = np.isin(dates.month, [7, 8])

    day_mult[ramadan] *= 1.15
    day_mult[eid] *= 1.45
    day_mult[dsf] *= 1.25
    day_mult[wf] *= 1.60
    day_mult[bts] *= 1.15
    day_mult[nat] *= 1.20
    day_mult[flash] *= 1.00      # store-level anomaly multiplier handles the surge
    day_mult[summer] *= 1.05
    day_mult *= rng.normal(1.0, 0.05, size=n).clip(0.8, 1.2)

    disc[ramadan] = 0.25
    disc[eid] = 0.35
    disc[dsf] = 0.45
    disc[bts] = 0.30
    disc[wf] = 0.85
    disc[flash] = 0.90

    # category demand shares per day
    cat_names = [c[0] for c in CATEGORIES]
    base = np.array([c[1] for c in CATEGORIES])
    probs = np.tile(base, (n, 1)).astype(float)

    def boost(mask, cat, factor):
        probs[mask, cat_names.index(cat)] *= factor

    boost(ramadan, "Fashion", 1.5); boost(ramadan, "Gourmet Grocery", 1.6)
    boost(ramadan, "Jewellery & Watches", 1.5); boost(ramadan, "Beauty & Fragrance", 1.3)
    boost(eid, "Fashion", 1.8); boost(eid, "Jewellery & Watches", 2.0)
    boost(eid, "Kids & Toys", 1.6); boost(eid, "Beauty & Fragrance", 1.5)
    boost(wf, "Electronics", 2.6); boost(wf, "Sports & Outdoor", 1.4)
    boost(dsf, "Electronics", 1.5); boost(dsf, "Fashion", 1.4); boost(dsf, "Home & Living", 1.2)
    boost(bts, "Kids & Toys", 2.0); boost(bts, "Fashion", 1.3)
    bug = dates == pd.Timestamp(PRICING_BUG_DAY)
    boost(bug, "Electronics", 2.6)

    probs = probs / probs.sum(axis=1, keepdims=True)
    return day_mult, disc, probs


def gen_sales(stores: pd.DataFrame, products: pd.DataFrame, customers: pd.DataFrame):
    dates = pd.date_range(SIM_START, SIM_END, freq="D")
    n_days, n_stores = len(dates), len(stores)
    day_mult, disc_intensity, cat_probs = build_day_effects(dates)

    # ---- weekday patterns by store type
    wd_physical = np.array([0.92, 0.90, 0.95, 1.05, 1.15, 1.18, 1.00])  # Mon..Sun
    wd_online = np.array([1.00, 0.98, 1.00, 1.02, 1.05, 1.05, 1.02])
    dow = dates.dayofweek.values

    # ---- growth trend (online grows much faster)
    t_years = (np.arange(n_days) / 365.25)
    growth_physical = 1.09 ** t_years
    growth_online = 1.27 ** t_years

    # ---- anomaly multiplier matrix A[day, store]
    A = np.ones((n_days, n_stores))
    sid_list = stores["store_id"].tolist()
    for ev in ANOMALY_EVENTS:
        dmask = (dates >= pd.Timestamp(ev["start"])) & (dates <= pd.Timestamp(ev["end"]))
        targets = range(n_stores) if ev["stores"] == "ALL" else [sid_list.index(s) for s in ev["stores"]]
        for si in targets:
            A[dmask, si] *= ev["multiplier"]

    # ---- expected orders matrix -> Poisson
    lam = np.zeros((n_days, n_stores))
    for si, row in stores.iterrows():
        online = row["store_type"] == "Online"
        wd = wd_online if online else wd_physical
        growth = growth_online if online else growth_physical
        lam[:, si] = row["base_orders"] * growth * wd[dow] * day_mult * A[:, si]
    orders_per = rng.poisson(lam)

    n_orders = int(orders_per.sum())
    print(f"  Generating {n_orders:,} orders...")

    # ---- explode matrix into one row per order
    flat = orders_per.flatten()  # day-major: [d0s0, d0s1, ..., d0s17, d1s0, ...]
    order_day = np.repeat(np.repeat(np.arange(n_days), n_stores), flat)
    order_store = np.repeat(np.tile(np.arange(n_stores), n_days), flat)

    # ---- assign customers per store (city affinity + propensity weights)
    cust_city = customers["city"].str.strip().str.title().values
    propensity = customers["_propensity"].values
    order_customer = np.full(n_orders, -1, dtype=np.int64)   # -1 = guest / walk-in
    for si, srow in stores.iterrows():
        mask = order_store == si
        cnt = int(mask.sum())
        if cnt == 0:
            continue
        if srow["store_type"] == "Online":
            pool = np.arange(len(customers))
            member_rate = 0.88
        else:
            pool = np.where(cust_city == srow["city"])[0]
            if len(pool) < 100:
                pool = np.arange(len(customers))
            member_rate = 0.72
        w = propensity[pool]
        w = w / w.sum()
        chosen = rng.choice(pool, size=cnt, p=w)
        is_member = rng.random(cnt) < member_rate
        chosen = np.where(is_member, chosen, -1)
        order_customer[mask] = chosen

    # ---- order timestamps (evening-heavy)
    hour_p = np.array([0.4, 0.2, 0.1, 0.1, 0.1, 0.2, 0.5, 1.0, 1.5, 2.5, 3.5, 4.5,
                       5.0, 4.8, 4.5, 4.6, 5.0, 6.0, 7.5, 8.5, 8.0, 6.5, 4.0, 2.0])
    hour_p = hour_p / hour_p.sum()
    order_hour = rng.choice(24, size=n_orders, p=hour_p)
    order_minute = rng.integers(0, 60, size=n_orders)

    # ---- payment method per order
    order_payment = np.empty(n_orders, dtype=object)
    online_mask = np.isin(order_store, [sid_list.index("S17"), sid_list.index("S18")])
    m_names, m_probs = PAYMENT_PHYSICAL
    o_names, o_probs = PAYMENT_ONLINE
    order_payment[~online_mask] = rng.choice(m_names, size=int((~online_mask).sum()), p=m_probs)
    order_payment[online_mask] = rng.choice(o_names, size=int(online_mask.sum()), p=o_probs)

    # ---- explode orders into line items
    lines_per_order = rng.choice([1, 2, 3, 4, 5, 6], size=n_orders,
                                 p=[0.35, 0.28, 0.17, 0.10, 0.06, 0.04])
    n_lines = int(lines_per_order.sum())
    print(f"  Generating {n_lines:,} line items...")
    line_order = np.repeat(np.arange(n_orders), lines_per_order)
    line_day = order_day[line_order]
    line_store = order_store[line_order]

    # ---- pick category per line (day-dependent), then product within category
    cat_names = [c[0] for c in CATEGORIES]
    line_cat = np.empty(n_lines, dtype=np.int8)
    for d in range(n_days):
        m = line_day == d
        c = int(m.sum())
        if c:
            line_cat[m] = rng.choice(len(cat_names), size=c, p=cat_probs[d])

    prod_cat = products["category"].values
    prod_price = products["unit_price"].values
    line_product = np.empty(n_lines, dtype=np.int32)
    for ci, cat in enumerate(cat_names):
        pidx = np.where(prod_cat == cat)[0]
        # price-aware Zipf popularity: cheapest items sell most (realistic),
        # which also keeps store-level daily revenue from being dominated by
        # rare big-ticket sales (heavy tails would drown anomaly signals)
        pidx = pidx[np.argsort(prod_price[pidx])]
        ranks = np.arange(1, len(pidx) + 1)
        w = 1.0 / ranks ** 1.0
        w = w / w.sum()
        m = line_cat == ci
        line_product[m] = rng.choice(pidx, size=int(m.sum()), p=w)

    # ---- quantity
    qty = rng.choice([1, 2, 3], size=n_lines, p=[0.72, 0.20, 0.08])
    grocery_ci = cat_names.index("Gourmet Grocery")
    gmask = line_cat == grocery_ci
    qty[gmask] = rng.choice([1, 2, 3, 4, 5, 6], size=int(gmask.sum()),
                            p=[0.30, 0.25, 0.18, 0.12, 0.09, 0.06])
    jw_ci = cat_names.index("Jewellery & Watches")
    qty[line_cat == jw_ci] = 1

    # ---- discount per line
    r = rng.random(n_lines)
    intensity = disc_intensity[line_day]
    discount = np.zeros(n_lines)
    promo = r < intensity
    discount[promo] = rng.choice([5, 10, 15, 20, 25, 30], size=int(promo.sum()),
                                 p=[0.20, 0.25, 0.20, 0.15, 0.10, 0.10])
    # pricing bug: all Electronics at -50% on that day (margin destruction)
    bug_mask = (line_day == int(np.where(dates == pd.Timestamp(PRICING_BUG_DAY))[0][0])) & \
               (line_cat == cat_names.index("Electronics"))
    discount[bug_mask] = 50

    # ---- assemble dataframe
    unit_price = products["unit_price"].values[line_product]
    sales = pd.DataFrame({
        "transaction_id": [f"T{i:08d}" for i in range(1, n_lines + 1)],
        "order_id": np.char.add("ORD-", np.char.zfill(line_order.astype(str), 8)),
        "order_date": dates[line_day].strftime("%Y-%m-%d"),
        "order_time": [f"{h:02d}:{m:02d}" for h, m in
                       zip(order_hour[line_order], order_minute[line_order])],
        "store_id": stores["store_id"].values[line_store],
        "customer_id": np.where(order_customer[line_order] >= 0,
                                customers["customer_id"].values[order_customer[line_order].clip(0)],
                                ""),
        "product_id": products["product_id"].values[line_product],
        "quantity": qty,
        "unit_price": unit_price,
        "discount_pct": discount.astype(int),
        "payment_method": order_payment[line_order],
        "sales_channel": np.where(np.isin(line_store,
                                          [sid_list.index("S17"), sid_list.index("S18")]),
                                  "Online", "In-Store"),
    })
    return sales, dates


def inject_quality_issues(sales: pd.DataFrame):
    """Deliberately corrupt the raw extract; returns (df, ground_truth_counts)."""
    n = len(sales)
    issues = {}

    # 1. duplicated rows (double POS export) ~0.25%
    dup_idx = rng.choice(n, size=int(n * 0.0025), replace=False)
    dups = sales.iloc[dup_idx].copy()
    issues["duplicate_rows"] = len(dups)

    # 2. mixed date formats on ~6% of rows (DD/MM/YYYY)
    fmt_idx = rng.choice(n, size=int(n * 0.06), replace=False)
    d = pd.to_datetime(sales.loc[fmt_idx, "order_date"])
    sales.loc[fmt_idx, "order_date"] = d.dt.strftime("%d/%m/%Y")
    issues["mixed_date_formats"] = len(fmt_idx)

    # 3. extra missing customer ids on member rows (~1.5%)
    member_rows = sales.index[sales["customer_id"] != ""]
    miss_idx = rng.choice(member_rows, size=int(len(member_rows) * 0.015), replace=False)
    sales.loc[miss_idx, "customer_id"] = ""
    issues["missing_customer_id_injected"] = len(miss_idx)

    # 4. impossible values: negative quantities / zero prices
    neg_idx = rng.choice(n, size=180, replace=False)
    sales.loc[neg_idx, "quantity"] = -sales.loc[neg_idx, "quantity"]
    zero_idx = rng.choice(n, size=150, replace=False)
    sales.loc[zero_idx, "unit_price"] = 0.0
    issues["negative_quantity"] = 180
    issues["zero_price"] = 150

    # 5. messy payment method casing/whitespace ~4%
    messy_idx = rng.choice(n, size=int(n * 0.04), replace=False)
    third = len(messy_idx) // 3
    sales.loc[messy_idx[:third], "payment_method"] = \
        sales.loc[messy_idx[:third], "payment_method"].str.upper()
    sales.loc[messy_idx[third:2 * third], "payment_method"] = \
        sales.loc[messy_idx[third:2 * third], "payment_method"].str.lower()
    sales.loc[messy_idx[2 * third:], "payment_method"] = \
        " " + sales.loc[messy_idx[2 * third:], "payment_method"] + " "
    issues["messy_payment_labels"] = len(messy_idx)

    sales = pd.concat([sales, dups], ignore_index=True)
    # shuffle a small window so duplicates are not trivially adjacent
    sales = sales.sample(frac=1.0, random_state=RANDOM_SEED).sort_values("order_date", kind="stable").reset_index(drop=True)
    return sales, issues


def gen_returns(sales: pd.DataFrame, products: pd.DataFrame):
    cat_by_pid = dict(zip(products["product_id"], products["category"]))
    base_p = {"Fashion": 0.060, "Electronics": 0.045, "Home & Living": 0.020,
              "Beauty & Fragrance": 0.020, "Gourmet Grocery": 0.008,
              "Sports & Outdoor": 0.020, "Kids & Toys": 0.020, "Jewellery & Watches": 0.010}
    cats = sales["product_id"].map(cat_by_pid)
    p = cats.map(base_p).fillna(0.02).values
    p = p * np.where(sales["sales_channel"].values == "Online", 1.6, 1.0)
    take = rng.random(len(sales)) < p

    ret = sales.loc[take, ["transaction_id", "order_date", "quantity"]].copy()
    # parse both date formats to compute the return date
    od = pd.to_datetime(ret["order_date"], format="%Y-%m-%d", errors="coerce")
    od = od.fillna(pd.to_datetime(ret["order_date"], format="%d/%m/%Y", errors="coerce"))
    delay = rng.integers(1, 30, size=len(ret))
    ret["return_date"] = (od + pd.to_timedelta(delay, unit="D")).dt.strftime("%Y-%m-%d")
    ret["qty_returned"] = np.abs(ret["quantity"].values)
    ret["reason"] = rng.choice(RETURN_REASONS, size=len(ret), p=[0.28, 0.22, 0.24, 0.12, 0.10, 0.04])

    # fraud burst: abnormal share of returns at one store during one week
    f_start, f_end = FRAUD_RETURN_WINDOW
    win = sales[(sales["store_id"] == FRAUD_RETURN_STORE)]
    od_all = pd.to_datetime(win["order_date"], format="%Y-%m-%d", errors="coerce")
    od_all = od_all.fillna(pd.to_datetime(win["order_date"], format="%d/%m/%Y", errors="coerce"))
    recent = win[(od_all >= pd.Timestamp(f_start) - pd.Timedelta(days=21)) & (od_all <= pd.Timestamp(f_end))]
    fraud_take = recent.sample(frac=0.45, random_state=RANDOM_SEED)
    fr = fraud_take[["transaction_id", "order_date", "quantity"]].copy()
    fr_dates = pd.to_datetime(rng.choice(pd.date_range(f_start, f_end).astype(str), size=len(fr)))
    fr["return_date"] = fr_dates.strftime("%Y-%m-%d")
    fr["qty_returned"] = np.abs(fr["quantity"].values)
    fr["reason"] = "Other"
    ret = pd.concat([ret, fr], ignore_index=True)

    ret.insert(0, "return_id", [f"R{i:07d}" for i in range(1, len(ret) + 1)])
    return ret.drop(columns=["quantity"])


def gen_marketing(dates: pd.DatetimeIndex, day_mult: np.ndarray):
    rows = []
    ramadan = _in_ranges(dates, RAMADAN)
    dsf = _in_ranges(dates, DSF)
    wf = _in_ranges(dates, WHITE_FRIDAY)
    bts = _in_ranges(dates, BACK_TO_SCHOOL)
    campaign = np.full(len(dates), "Always-On", dtype=object)
    campaign[bts] = "Back to School"
    campaign[ramadan] = "Ramadan Nights"
    campaign[dsf] = "Dubai Shopping Festival"
    campaign[wf] = "White Friday"
    boost = 1 + 1.4 * (day_mult - 1).clip(0)
    boost[wf] *= 1.8
    for ch, base in MARKETING_CHANNELS:
        spend = base * boost * rng.normal(1.0, 0.12, size=len(dates)).clip(0.6, 1.5)
        impressions = spend * rng.uniform(38, 55)
        clicks = impressions * rng.uniform(0.012, 0.03, size=len(dates))
        for i, dt in enumerate(dates):
            rows.append((dt.strftime("%Y-%m-%d"), ch, campaign[i], round(float(spend[i]), 2),
                         int(impressions[i]), int(clicks[i])))
    df = pd.DataFrame(rows, columns=["date", "channel", "campaign", "spend_aed", "impressions", "clicks"])
    return df


def gen_web_traffic(dates: pd.DatetimeIndex, sales: pd.DataFrame):
    od = pd.to_datetime(sales["order_date"], format="%Y-%m-%d", errors="coerce")
    od = od.fillna(pd.to_datetime(sales["order_date"], format="%d/%m/%Y", errors="coerce"))
    online = sales[sales["sales_channel"] == "Online"].copy()
    online["_d"] = od[online.index].dt.strftime("%Y-%m-%d")
    daily_orders = online.groupby("_d")["order_id"].nunique()

    rows = []
    for dt in dates:
        key = dt.strftime("%Y-%m-%d")
        orders = int(daily_orders.get(key, 0))
        cr = rng.normal(0.031, 0.0025)
        cr = min(max(cr, 0.02), 0.045)
        sessions = int(orders / cr) if orders else int(rng.uniform(1500, 2500))
        rows.append({
            "date": key,
            "sessions": sessions,
            "unique_visitors": int(sessions * rng.uniform(0.72, 0.85)),
            "new_visitor_pct": round(float(rng.uniform(0.28, 0.44)), 3),
            "bounce_rate": round(float(rng.normal(0.38, 0.04)), 3),
            "avg_session_sec": int(rng.normal(215, 35)),
            "online_orders": orders,
            "conversion_rate": round(orders / sessions, 4) if sessions else 0.0,
        })
    return pd.DataFrame(rows)


def gen_inventory(sales: pd.DataFrame, stores: pd.DataFrame, products: pd.DataFrame):
    od = pd.to_datetime(sales["order_date"], format="%Y-%m-%d", errors="coerce")
    od = od.fillna(pd.to_datetime(sales["order_date"], format="%d/%m/%Y", errors="coerce"))
    tmp = sales[["store_id", "product_id", "quantity"]].copy()
    tmp["month"] = od.dt.to_period("M").astype(str)
    tmp = tmp[tmp["quantity"] > 0]
    monthly = tmp.groupby(["month", "store_id", "product_id"], as_index=False)["quantity"].sum()
    monthly = monthly.rename(columns={"quantity": "units_sold_month"})
    cover = rng.uniform(1.1, 2.8, size=len(monthly))
    monthly["units_on_hand"] = np.ceil(monthly["units_sold_month"] * cover).astype(int)
    monthly["stockout_days"] = rng.choice([0, 0, 0, 0, 0, 1, 2, 3], size=len(monthly))
    # stockout crisis: Electronics at the flagship, Oct 2025
    elec = set(products.loc[products["category"] == "Electronics", "product_id"])
    crisis = (monthly["month"] == "2025-10") & (monthly["store_id"] == "S01") & \
             (monthly["product_id"].isin(elec))
    monthly.loc[crisis, "units_on_hand"] = 0
    monthly.loc[crisis, "stockout_days"] = rng.integers(8, 20, size=int(crisis.sum()))
    return monthly.rename(columns={"month": "snapshot_month"})


# ===========================================================================
# 5. Main
# ===========================================================================

def main():
    t0 = time.time()
    print("=" * 60)
    print("Bahgat Insight Platform - Synthetic Data Generator")
    print("=" * 60)

    print("[1/8] Dimensions: stores, products, customers, suppliers")
    stores = gen_stores()
    products = gen_products()
    customers = gen_customers()
    suppliers, products = gen_suppliers(products)

    print("[2/8] Sales transactions (this is the heavy step)")
    sales, dates = gen_sales(stores, products, customers)
    day_mult, _, _ = build_day_effects(dates)

    print("[3/8] Injecting data-quality issues into the raw extract")
    sales, issues = inject_quality_issues(sales)

    print("[4/8] Returns (incl. fraud burst)")
    returns = gen_returns(sales, products)

    print("[5/8] Marketing spend")
    marketing = gen_marketing(dates, day_mult)

    print("[6/8] Web traffic")
    web = gen_web_traffic(dates, sales)

    print("[7/8] Inventory snapshots")
    inventory = gen_inventory(sales, stores, products)

    print("[8/8] Writing CSV files to data/raw/")
    customers_out = customers.drop(columns=["_propensity"])
    files = {
        "stores.csv": stores.drop(columns=["base_orders"]),
        "products.csv": products,
        "customers.csv": customers_out,
        "suppliers.csv": suppliers,
        "sales_transactions.csv": sales,
        "returns.csv": returns,
        "marketing_spend.csv": marketing,
        "web_traffic.csv": web,
        "inventory_snapshots.csv": inventory,
    }
    manifest = {"generated_at": datetime.now().isoformat(timespec="seconds"),
                "simulation_window": [SIM_START, SIM_END],
                "random_seed": RANDOM_SEED,
                "injected_quality_issues": issues,
                "injected_anomalies": [e["label"] for e in ANOMALY_EVENTS] + [
                    f"Pricing bug (Electronics -50%) on {PRICING_BUG_DAY}",
                    f"Returns-abuse burst at {FRAUD_RETURN_STORE} {FRAUD_RETURN_WINDOW[0]} to {FRAUD_RETURN_WINDOW[1]}",
                    "Electronics stockout at S01 during 2025-10",
                ],
                "files": {}}
    for name, df in files.items():
        path = RAW_DIR / name
        df.to_csv(path, index=False)
        manifest["files"][name] = {"rows": int(len(df)), "size_mb": round(path.stat().st_size / 1e6, 2)}
        print(f"    {name:28s} {len(df):>10,} rows  ({manifest['files'][name]['size_mb']} MB)")

    with open(LOG_DIR / "generation_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nDone in {time.time() - t0:.1f}s. Manifest -> logs/generation_manifest.json")


if __name__ == "__main__":
    main()
