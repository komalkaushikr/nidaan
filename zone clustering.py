import numpy as np

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
    R = 6371
    lat1, lon1 = np.radians(p1)
    lat2, lon2 = np.radians(p2)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))

def kmeans(points, k, iters=100, seed=0):
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(points), size=k, replace=False)
    centroids = points[idx].copy()
    for _ in range(iters):
        dists = np.array([[haversine(p, c) for c in centroids] for p in points])
        labels = np.argmin(dists, axis=1)
        new_centroids = np.array([
            points[labels == j].mean(axis=0) if np.any(labels == j) else centroids[j]
            for j in range(k)
        ])
        if np.allclose(new_centroids, centroids):
            break
        centroids = new_centroids
    return labels, centroids

names = list(BINS.keys())
coords = np.array([BINS[i][1:] for i in names])

# Baseline: single hub serving everyone (today's de facto model)
global_centroid = coords.mean(axis=0)
baseline_avg_dist = np.mean([haversine(p, global_centroid) for p in coords])

# k=3 territories via k-means
K = 3
labels, centroids = kmeans(coords, K, seed=0)
zoned_avg_dist = np.mean([haversine(coords[i], centroids[labels[i]]) for i in range(len(coords))])

reduction_pct = (1 - zoned_avg_dist / baseline_avg_dist) * 100

print(f"Single-hub model   -> avg distance from bin to hub: {baseline_avg_dist:.2f} km")
print(f"3-zone k-means model -> avg distance from bin to zone center: {zoned_avg_dist:.2f} km")
print(f"Reduction in avg travel distance per bin: {reduction_pct:.1f}%")
print()
print("Zone assignments:")
for j in range(K):
    members = [BINS[names[i]][0] for i in range(len(names)) if labels[i] == j]
    print(f"  Zone {j+1} (center {centroids[j][0]:.4f}, {centroids[j][1]:.4f}): {members}")