import mysql.connector

def massive_import(file_path):
    config = {
        "host": "localhost",
        "user": "root",
        "password": "cinema",
        "database": "transport_management"
    }

    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    print("--- RESETARE TABEL ---")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("TRUNCATE TABLE locations")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

    sql = "INSERT INTO locations (name, latitude, longitude) VALUES (%s, %s, %s)"

    buffer = []
    count = 0
    skipped = 0


    accepted_codes = {
        "PPL",
        "PPLA",
        "PPLA2",
        "PPLA3",
        "PPLA4",
        "PPLC",
        "PPLL",
        "PPLX"
    }

    print(f"Incep importul din {file_path}...")

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            try:
                row = line.rstrip("\n").split("\t")

                if len(row) < 8:
                    skipped += 1
                    continue

                feature_class = row[6]
                feature_code = row[7]


                if feature_class == "P" and feature_code in accepted_codes:
                    name = row[1].strip()
                    lat = float(row[4])
                    lon = float(row[5])

                    buffer.append((name, lat, lon))
                    count += 1

                if len(buffer) >= 1000:
                    cursor.executemany(sql, buffer)
                    conn.commit()
                    print(f"Am procesat {count} localitati...")
                    buffer = []

            except Exception:
                skipped += 1
                continue

    if buffer:
        cursor.executemany(sql, buffer)
        conn.commit()

    print("\n--- GATA! ---")
    print(f"Total localitati importate: {count}")
    print(f"Linii sarite: {skipped}")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    massive_import("RO.txt")