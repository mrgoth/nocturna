import math
import requests
import numpy as np
import webbrowser
from scipy.spatial import cKDTree
import os
import random
import time

# -----------------------------
# CONFIG

LAT = 34.665421
LON = -1.874938

RUNS = 60
MEMORY_FILE = "drakul_memory.txt"
MIN_DISTANCE = 300

SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter"
]

# -----------------------------
# INPUT

while True:
    try:
        RADIUS = int(input("Radius (500–10000m): "))
        if 500 <= RADIUS <= 10000:
            break
    except:
        pass

INTENTION = input("Mode (normal / paranormal): ").lower()

# -----------------------------
# MEMORY

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []
    pts = []
    with open(MEMORY_FILE, "r") as f:
        for line in f:
            try:
                lat, lon = map(float, line.strip().split(","))
                pts.append((lat, lon))
            except:
                continue
    return pts

def save_memory(pt):
    with open(MEMORY_FILE, "a") as f:
        f.write(f"{pt[0]},{pt[1]}\n")

def far_from_memory(pt, memory):
    for m in memory:
        if math.dist(pt, m) * 111000 < MIN_DISTANCE:
            return False
    return True

memory = load_memory()

# -----------------------------
# FETCH (FIXED)

def fetch_layers():
    for attempt in range(3):  # retry 3 times
        for s in SERVERS:
            try:
                query = f"""
                [out:json];
                (
                  way["highway"](around:{RADIUS},{LAT},{LON});
                  way["building"](around:{RADIUS},{LAT},{LON});
                  way["landuse"="forest"](around:{RADIUS},{LAT},{LON});
                  way["natural"="water"](around:{RADIUS},{LAT},{LON});
                  way["landuse"="industrial"](around:{RADIUS},{LAT},{LON});
                  way["railway"](around:{RADIUS},{LAT},{LON});
                  way["amenity"="graveyard"](around:{RADIUS},{LAT},{LON});
                );
                out geom;
                """

                r = requests.post(s, data=query, timeout=40)
                data = r.json()

                layers = {
                    "road": [],
                    "build": [],
                    "forest": [],
                    "industrial": [],
                    "rail": [],
                    "water": [],
                    "grave": []
                }

                for el in data.get("elements", []):
                    pts = [(p["lat"], p["lon"]) for p in el.get("geometry", [])]
                    tags = el.get("tags", {})

                    if "highway" in tags:
                        layers["road"].extend(pts)
                    elif "building" in tags:
                        layers["build"].extend(pts)
                    elif tags.get("landuse") == "forest":
                        layers["forest"].extend(pts)
                    elif tags.get("landuse") == "industrial":
                        layers["industrial"].extend(pts)
                    elif "railway" in tags:
                        layers["rail"].extend(pts)
                    elif tags.get("natural") == "water":
                        layers["water"].extend(pts)
                    elif tags.get("amenity") == "graveyard":
                        layers["grave"].extend(pts)

                # RETURN even if partial
                return {k: cKDTree(v) if v else None for k, v in layers.items()}

            except:
                continue

        time.sleep(2)

    print("⚠️ WARNING: USING LIMITED DATA")
    return {k: None for k in ["road","build","forest","industrial","rail","water","grave"]}

# -----------------------------
# METRICS

def dist(pt, tree):
    if tree is None:
        return 2000
    d, _ = tree.query([pt])
    return d[0] * 111000

def density(pt, tree, r=0.002):
    if tree is None:
        return 0
    return len(tree.query_ball_point(pt, r))

# -----------------------------
# ACCESS

def is_accessible(pt, t):
    d_road = dist(pt, t["road"])
    d_build = dist(pt, t["build"])

    return (
        d_road < 600 and
        d_build > 200
    )

# -----------------------------
# RANDOM

def rand_point():
    r = RADIUS * math.sqrt(np.random.random())
    t = np.random.uniform(0, 2 * math.pi)

    dx = r * math.cos(t)
    dy = r * math.sin(t)

    return (
        LAT + dy / 111300,
        LON + dx / (111300 * math.cos(math.radians(LAT)))
    )

# -----------------------------
# PARANORMAL SCORE

def score(pt, t):
    rd = dist(pt, t["road"])
    bd = dist(pt, t["build"])
    fd = dist(pt, t["forest"])
    wd = dist(pt, t["water"])
    gd = dist(pt, t["grave"])
    idd = dist(pt, t["industrial"])

    isolation = bd * 1.0 + rd * 0.5
    void = min(rd, bd, fd) * 1.2
    edge = abs(rd - bd) * 200

    anomaly = 0

    if wd < 150:
        anomaly += 5000
    if gd < 150:
        anomaly += 7000
    if idd < 250:
        anomaly += 4000

    rarity = 0
    if bd > 800:
        rarity += 6000
    if rd > 1000:
        rarity += 4000

    s = isolation + void + edge + anomaly + rarity

    if INTENTION == "paranormal":
        s *= 1.8

    s += random.uniform(-300, 300)

    return s

# -----------------------------
# SEARCH

def search_best(trees):
    best = None
    best_s = -1e9

    for _ in range(RUNS * 1000):
        p = rand_point()

        if not is_accessible(p, trees):
            continue

        if not far_from_memory(p, memory):
            continue

        s = score(p, trees)

        if s > best_s:
            best = p
            best_s = s

    if best is None:
        return (LAT, LON, -9999)

    return (best[0], best[1], best_s)

# -----------------------------
# MAIN

THRESHOLD = 100000  # 🔥 ONLY CHANGE ADDED

os.system("cls" if os.name == "nt" else "clear")

print("DR4KUL V4.5")
print("PARANORMAL ENGINE ACTIVE\n")

time.sleep(1)
print(">> CONTACTING DATA SOURCES...")
trees = fetch_layers()

time.sleep(1)
print(">> BREACHING VEIL...\n")

lat, lon, s = search_best(trees)

if s >= THRESHOLD:
    save_memory((lat, lon))

    link = f"https://www.google.com/maps?q={lat},{lon}"

    print(">> ANOMALY DETECTED\n")
    print(f"SCORE: {int(s)}\n")
    print(link)

    webbrowser.open_new_tab(link)
else:
    print(">> NO STRONG ANOMALY FOUND")
    print(f"SCORE TOO LOW: {int(s)}")

print("\nEND\n")