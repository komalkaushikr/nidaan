import numpy as np
from itertools import permutations

# bin coords (lat, lng) from app.py, plus a recycling hub (central Delhi NCR point)
HUB = (28.6315, 77.2167)
BINS = {
    1: ("Miranda House College", 28.6878, 77.2150),
    2: ("Lady Shri Ram College", 28.6563, 77.2436),
    3: ("Gargi College", 28.5535, 77.1889),
    4: ("Jesus & Mary College", 28.5972, 77.1714),
    5: ("IP College for Women", 28.6741, 77.2291),
    6: ("Sarojini Nagar Hostel", 28.5770, 77.1955),
    7: ("Lajpat Nagar Community Center", 28.5677, 77.2433),
    8: ("Karol Bagh Hostel Block B", 28.6514, 77.1907),
    9: ("Dwarka Sector 10 SHG Center", 28.5823, 77.0490),
    10: ("Rohini Women's Hostel", 28.7041, 77.1025),
}

def haversine(p1, p2):
    R = 6371  # km
    lat1, lon1 = np.radians(p1)
    lat2, lon2 = np.radians(p2)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))

def route_distance(stops, order):
    pts = [HUB] + [stops[i][1:] for i in order] + [HUB]
    return sum(haversine(pts[i], pts[i+1]) for i in range(len(pts)-1))

def nearest_neighbor_order(stops):
    remaining = list(range(len(stops)))
    order = []
    current = HUB
    while remaining:
        dists = [haversine(current, stops[i][1:]) for i in remaining]
        nxt = remaining[int(np.argmin(dists))]
        order.append(nxt)
        current = stops[nxt][1:]
        remaining.remove(nxt)
    return order

rng = np.random.default_rng(42)
bin_ids = list(BINS.keys())
naive_total, opt_total = [], []

TRIALS = 500
for _ in range(TRIALS):
    k = rng.integers(3, 6)  # 3-5 bins flagged at once, realistic batch size
    chosen = rng.choice(bin_ids, size=k, replace=False)
    stops = [BINS[i] for i in chosen]

    naive_order = list(range(len(stops)))  # dispatch in the order alerts came in
    naive_dist = route_distance(stops, naive_order)

    opt_order = nearest_neighbor_order(stops)
    opt_dist = route_distance(stops, opt_order)

    naive_total.append(naive_dist)
    opt_total.append(opt_dist)

naive_avg = np.mean(naive_total)
opt_avg = np.mean(opt_total)
savings_pct = (1 - opt_avg/naive_avg) * 100

print(f"Trials: {TRIALS} (batches of 3-5 simultaneously-flagged bins)")
print(f"Avg naive (alert-order) round-trip distance: {naive_avg:.2f} km")
print(f"Avg nearest-neighbor round-trip distance:     {opt_avg:.2f} km")
print(f"Avg distance saved per multi-bin trip: {savings_pct:.1f}%")
print(f"Total distance saved across {TRIALS} trips: {sum(naive_total)-sum(opt_total):.1f} km")