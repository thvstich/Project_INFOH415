import time
import psycopg2
import csv

DB = {
    "dbname": "landsat8",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5435"
}

SCALES = ["256", "64"]
REPEAT = 6

# Bounding box (EPSG:4326)
BBOX = "ST_MakeEnvelope(4.3, 50.8, 4.45, 50.9, 4326)"

conn = psycopg2.connect(**DB)
cur = conn.cursor()

rows = []

for scale in SCALES:
    b4 = f"landsat_{scale}_b4"
    b5 = f"landsat_{scale}_b5"

    queries = {
        "Q1_crop": f"""
            SELECT ST_Clip(rast, {BBOX})
            FROM {b4}
            WHERE ST_Intersects(rast, {BBOX});
        """,


        "Q2_ndvi": f"""
            SELECT AVG((stats).mean)
            FROM (
                SELECT ST_SummaryStats(
                    ST_MapAlgebraExpr(
                        b5.rast,
                        b4.rast,
                        '( [rast1] - [rast2] ) / ( [rast1] + [rast2] )',
                        '32BF'
                    )
                ) AS stats
                FROM {b4} b4
                JOIN {b5} b5
                  ON ST_Intersects(b4.rast, b5.rast)
                WHERE ST_Intersects(b4.rast, {BBOX})
            ) s;
        """,

        "Q3_filter": f"""
            SELECT ST_MapAlgebraExpr(
                rast,
                4,
                'CASE WHEN [rast] > 1000 THEN [rast] ELSE 0 END',
                '32BF'
                ) as filtered_rast
            FROM {b4};
        """
    }

    for qname, sql in queries.items():
        times = []

        for run_id in range(1, REPEAT + 1):
            start = time.perf_counter()
            cur.execute(sql)
            cur.fetchall()
            end = time.perf_counter()

            elapsed = end - start
            times.append(elapsed)

            # Save each run
            rows.append([
                "PostGIS",
                scale,
                qname,
                run_id,
                elapsed,
                ""
            ])

            print(f"PostGIS {scale} {qname} run {run_id}: {elapsed:.4f}s")

        avg_time = sum(times[1:]) / len(times[1:])


        # Save average
        rows.append([
            "PostGIS",
            scale,
            qname,
            "avg",
            "",
            avg_time
        ])

        print(f"PostGIS {scale} {qname} AVG: {avg_time:.4f}s")

conn.close()

# Write CSV
with open("benchmark/results/results_postgis.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "system",
        "scale",
        "query",
        "run_id",
        "time_seconds",
        "avg_time_seconds"
    ])
    writer.writerows(rows)
