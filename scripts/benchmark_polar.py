import math
import os
import statistics
import time

import weatherrouting

POLAR_PATH = os.path.join(
                          os.path.dirname(__file__), "../tests/data/bavaria38.pol"
        )

def run_once(polar, samples, iterations, bisect):
    start = time.perf_counter()

    total = 0.0
    for _ in range(iterations):
        for tws, twa in samples:
            total += polar.get_speed(tws, twa, bisect)


    elapsed = time.perf_counter() - start
    return elapsed, total

def main():
    polar = weatherrouting.Polar(POLAR_PATH)
    samples = [
        (33.8, math.radians(164)),
        (7.6, math.radians(5)),
        (1.3, math.radians(28)),
        (43.5, math.radians(95)),
        (11.9, math.radians(155)),
        (53.7, math.radians(88)),
    ]

    iterations = 50_000
    repeats = 7

    times_old = []
    checksum_old = None

    times_new = []
    checksum_new = None

    for _ in range(repeats):
        elapsed, total = run_once(polar, samples, iterations, False)
        times_old.append(elapsed)
        checksum_old = total

        elapsed, total = run_once(polar, samples, iterations, True)
        times_new.append(elapsed)
        checksum_new = total


    median_old = statistics.median(times_old)
    median_new = statistics.median(times_new)
    speedup = median_old / median_new
    time_reduction = (1 - median_new / median_old) * 100
    checksum_diff = checksum_new - checksum_old

    print(f"iterations: {iterations}")
    print(f"samples: {len(samples)}")
    print(f"repeats: {repeats}")

    print("\n------ OLD ------")
    print(f"min: {min(times_old):.6f}s")
    print(f"median: {median_old:.6f}s")
    print(f"checksum: {checksum_old:.17g}")

    print("\n------ NEW ------")
    print(f"min: {min(times_new):.6f}s")
    print(f"median: {median_new:.6f}s")
    print(f"checksum: {checksum_new:.17g}")

    print("\n------ COMPARISON ------")
    print(f"median speedup: {speedup:.3f}x")
    print(f"time reduction: {time_reduction:.2f}%")
    print(f"checksum difference: {checksum_diff:.17e}")

if __name__ == "__main__":
    main()
