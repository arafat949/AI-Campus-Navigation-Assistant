"""
Fuzzy Logic - a small Mamdani-style fuzzy rule engine used to estimate how
CROWDED a corridor / classroom / route is likely to be, based on:
    - occupancy percentage (current headcount vs room capacity)
    - time of day (class-change / peak hours vs off-peak)

Why fuzzy logic fits here: "crowded" isn't a hard yes/no threshold - a room
at 55% occupancy during a peak hour "feels" more crowded than the same 55%
at 8pm. Fuzzy membership functions capture that gradual, human-like judgement
instead of a brittle if/else cutoff.

Steps: fuzzify inputs -> evaluate rules (min for AND) -> combine outputs
(weighted average, i.e. simplified centroid defuzzification).
"""


def tri(x, a, b, c):
    """Triangular membership function: 0 at/outside [a, c], peaks at 1 at b."""
    if x <= a or x >= c:
        return 0.0
    if x == b:
        return 1.0
    if x < b:
        return (x - a) / (b - a)
    return (c - x) / (c - b)


def fuzzify_occupancy(pct):
    return {
        "low": tri(pct, -1, 0, 50),
        "medium": tri(pct, 20, 50, 80),
        "high": tri(pct, 50, 100, 101),
    }


def fuzzify_time(hour):
    """Peaks roughly around class-change / lunch hours on a typical class day."""
    return {
        "off_peak": max(tri(hour, -1, 8, 10), tri(hour, 16, 19, 21)),
        "peak": max(tri(hour, 9, 11, 13), tri(hour, 13, 14.5, 16)),
    }


# Rule base: IF occupancy IS x AND time IS y THEN congestion IS z (0-100 crisp output)
RULES_OUTPUT = {
    ("low", "off_peak"): 10,
    ("low", "peak"): 30,
    ("medium", "off_peak"): 35,
    ("medium", "peak"): 65,
    ("high", "off_peak"): 60,
    ("high", "peak"): 95,
}


def estimate_congestion(current_count, capacity, hour):
    pct = min(100.0, max(0.0, (current_count / capacity) * 100)) if capacity else 0.0
    occ = fuzzify_occupancy(pct)
    tm = fuzzify_time(hour)

    fired = []
    numerator, denominator = 0.0, 0.0
    for (o_level, t_level), out_value in RULES_OUTPUT.items():
        strength = min(occ[o_level], tm[t_level])   # fuzzy AND = min
        if strength > 0:
            fired.append({
                "rule": f"IF occupancy is {o_level} AND time is {t_level} THEN congestion is {out_value}",
                "strength": round(strength, 2),
            })
            numerator += strength * out_value
            denominator += strength

    score = numerator / denominator if denominator else 0.0
    if score < 33:
        label = "Low"
    elif score < 66:
        label = "Medium"
    else:
        label = "High"

    return {
        "occupancy_pct": round(pct, 1),
        "congestion_score": round(score, 1),
        "congestion_label": label,
        "fired_rules": fired,
    }
