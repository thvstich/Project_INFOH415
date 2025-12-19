import time
import csv
import os
import requests
from requests.auth import HTTPBasicAuth



# CONFIGURATION

WCPS_ENDPOINT = "http://localhost:8080/rasdaman/ows"
SCALES = ["256", "64"]
REPEAT = 6

# WCPS queries template

def q1_crop(scale):
    return f"""
for c in (landsat_tiles_{scale}_B4) 
return encode(c[E(600600:615900), N(5635400:5646900)],"csv")
"""


def q2_ndvi(scale):
    return f"""
for r in (landsat_tiles_{scale}_B4),
    n in (landsat_tiles_{scale}_B5)
return avg(
  (n[E(600600:615900), N(5635400:5646900)] - r[E(600600:615900), N(5635400:5646900)])
  /
  (n[E(600600:615900), N(5635400:5646900)] + r[E(600600:615900), N(5635400:5646900)])
)
"""


def q3_filter(scale):
    return f"""
for c in (landsat_tiles_{scale}_B4)
return avg(c*(c > 1000))
"""

QUERIES = {
    "Q1_crop": q1_crop,
    "Q2_ndvi": q2_ndvi,
    "Q3_filter": q3_filter,
}


# WCPS RUNNER

def run_wcps(query):
    params = {
        "service": "WCS",
        "version": "2.0.1",
        "request": "ProcessCoverages",
        "query": query,
    }

    response = requests.post(
        WCPS_ENDPOINT,
        data=params,
        auth=HTTPBasicAuth("rasadmin", "rasadmin")
        )

    if response.status_code != 200:
        raise RuntimeError(
            f"WCPS error {response.status_code}: {response.text[:200]}"
        )

# BENCHMARK

os.makedirs("benchmark/results", exist_ok=True)
rows = []

for scale in SCALES:
    for qname, qfunc in QUERIES.items():
        times = []

        query = qfunc(scale)


        for run_id in range(1, REPEAT + 1):
            start = time.perf_counter()
            run_wcps(query)
            end = time.perf_counter()

            elapsed = end - start
            times.append(elapsed)

            rows.append([
                "Rasdaman-WCPS",
                scale,
                qname,
                run_id,
                elapsed,
                ""
            ])

            print(f"WCPS {scale} {qname} run {run_id}: {elapsed:.4f}s")

        avg_time = sum(times[1:]) / len(times[1:])


        rows.append([
            "Rasdaman-WCPS",
            scale,
            qname,
            "avg",
            "",
            avg_time
        ])

        print(f"WCPS {scale} {qname} AVG: {avg_time:.4f}s")


# WRITE CSV

output_csv = "benchmark/results/results_rasdaman.csv"

with open(output_csv, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "system",
        "scale",
        "query",
        "run_id",
        "time_seconds",
        "avg_time_seconds",
    ])
    writer.writerows(rows)

print(f"\nWCPS benchmark finished. Results written to {output_csv}")
