import numpy as np

bins = [
    ("Miranda House College", 2.6), ("Lady Shri Ram College", 2.2), ("Gargi College", 3.0),
    ("Jesus & Mary College", 1.9), ("IP College for Women", 2.4), ("Sarojini Nagar Hostel", 1.8),
    ("Lajpat Nagar Community Center", 0.8), ("Karol Bagh Hostel Block B", 1.5),
    ("Dwarka Sector 10 SHG Center", 0.6), ("Rohini Women's Hostel", 1.7),
]
HOURS = 14 * 24
ROLL_WINDOW = 6

def simulate(demand_pads, demand_inc, eta_sequence, lookahead_hr):
    fill, history, overflow, trips, lead_times, eta_idx = 10.0, [], 0, 0, [], 0
    reset_rng = np.random.default_rng(123)
    for h in range(HOURS):
        fill += demand_pads[h] * demand_inc[h]
        history.append(fill)
        if len(history) > ROLL_WINDOW: history.pop(0)
        fire = fill >= 80
        if not fire and len(history) >= ROLL_WINDOW:
            x = np.arange(len(history))
            slope, _ = np.polyfit(x, history, 1)
            if slope > 0:
                hrs_to_80 = (80 - fill) / slope
                if 0 <= hrs_to_80 <= lookahead_hr:
                    fire = True
                    lead_times.append(hrs_to_80)
        if fire:
            eta = eta_sequence[eta_idx % len(eta_sequence)]; eta_idx += 1
            t = h
            while t < h + eta and t < HOURS - 1:
                t += 1
                fill += demand_pads[t] * demand_inc[t]
            if fill >= 100: overflow += 1
            trips += 1
            fill = reset_rng.uniform(3, 8)
    return overflow, trips, lead_times

rng_eta = np.random.default_rng(7)
eta_pool = [max(0.25, rng_eta.normal(0.6, 0.25)) for _ in range(5000)]

# baseline reactive trip count (lookahead=0 == pure reactive)
rng_main = np.random.default_rng(42)
demands = [(rng_main.poisson(lam, HOURS), rng_main.uniform(0.8, 1.5, HOURS)) for _, lam in bins]
_, base_trips, _ = 0, 0, None
total_base_trips = 0
for dp, di in demands:
    _, t, _ = simulate(dp, di, eta_pool, lookahead_hr=0)
    total_base_trips += t

print(f"{'Lookahead (hr)':>15} | {'Early-catch %':>13} | {'Avg lead (min)':>14} | {'Trip cost %':>11}")
print("-"*65)
for lookahead in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
    total_trips, all_lead = 0, []
    for dp, di in demands:
        _, t, lt = simulate(dp, di, eta_pool, lookahead_hr=lookahead)
        total_trips += t
        all_lead.extend(lt)
    early_pct = len(all_lead) / total_trips * 100
    avg_lead_min = np.mean(all_lead) * 60 if all_lead else 0
    trip_cost_pct = (total_trips / total_base_trips - 1) * 100
    print(f"{lookahead:>15.1f} | {early_pct:>12.0f}% | {avg_lead_min:>13.0f}m | {trip_cost_pct:>10.1f}%")