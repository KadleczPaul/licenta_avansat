import math
import mysql.connector
from scipy.spatial import KDTree
import logging
import time
import random


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class FastNetworkGenerator:
    def __init__(self, db_config, k_neighbors=12, road_factor=1.06):
        """
        k_neighbors=12: Permite nodurilor mari să aibă mai multe conexiuni (scurtături).
        road_factor=1.06: Adaugă doar 6% peste distanța aeriană (foarte realist pentru RO).
        """
        self.db_config = db_config
        self.k_neighbors = k_neighbors
        self.road_factor = road_factor

    def calculate_haversine(self, lat1, lon1, lat2, lon2):
        """Calculează distanța aeriană exactă între două coordonate."""
        R = 6371.0088
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)
        a = (math.sin(d_lat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(d_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def run(self):
        start_time = time.time()
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor(dictionary=True)


            logging.info("Extrag locațiile din baza de date...")
            cursor.execute("SELECT location_id, latitude, longitude FROM locations")
            locs = cursor.fetchall()

            if not locs:
                logging.error("Tabelul 'locations' este gol!")
                return


            points = [(float(l['latitude']), float(l['longitude'])) for l in locs]
            tree = KDTree(points)

            routes_data = []
            logging.info(f"Generez rețeaua optimizată pentru {len(locs)} locații...")

            for i, origin in enumerate(locs):

                distances, indexes = tree.query(points[i], k=self.k_neighbors + 1)


                target_k = random.randint(3, self.k_neighbors)

                for j in range(1, target_k + 1):
                    if j >= len(indexes): break

                    dest = locs[indexes[j]]
                    hav_km = self.calculate_haversine(
                        points[i][0], points[i][1],
                        points[indexes[j]][0], points[indexes[j]][1]
                    )


                    if hav_km > 100 and j > 2:
                        continue


                    road_km = round(hav_km * self.road_factor, 2)


                    routes_data.append((
                        origin['location_id'],
                        dest['location_id'],
                        road_km,
                        round(hav_km, 2)
                    ))


            logging.info(f"Salvez {len(routes_data)} rute... (Resetare tabel 'routes')")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            cursor.execute("TRUNCATE TABLE routes;")


            sql = """
                INSERT INTO routes (origin_id, destination_id, distance_km, distance_haversine_km, is_active, distance_source)
                VALUES (%s, %s, %s, %s, TRUE, 'dynamic')
            """


            for batch_idx in range(0, len(routes_data), 5000):
                cursor.executemany(sql, routes_data[batch_idx:batch_idx + 5000])
                conn.commit()
                logging.info(f"Progres: {min(batch_idx + 5000, len(routes_data))} rute salvate...")

            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

            logging.info(f"SUCCES! Rețeaua a fost generată în {round(time.time() - start_time, 2)} secunde.")

        except mysql.connector.Error as err:
            logging.error(f"Eroare MySQL: {err}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()


if __name__ == "__main__":

    MY_DB_CONFIG = {
        "host": "localhost",
        "user": "root",
        "password": "cinema",
        "database": "transport_management"
    }

    generator = FastNetworkGenerator(MY_DB_CONFIG)
    generator.run()