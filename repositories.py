from datetime import datetime
from db_manager import Database
from models import User, Driver, Vehicle, Location, Route, Trip, Client

class UserRepository:
    def get_all(self):
        with Database() as cursor:
            cursor.execute("SELECT user_id, username, password_hash, role FROM users ORDER BY username ASC")
            rows = cursor.fetchall()
            return [User(**row) for row in rows]

    def find_by_username(self, username):
        with Database() as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            row = cursor.fetchone()
            return User(**row) if row else None

    def save(self, user):
        sql = "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)"
        with Database() as cursor:
            cursor.execute(sql, (user.username, user.password_hash, user.role))
            return cursor.lastrowid

    def delete(self, user_id):
        with Database() as cursor:
            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))


class DriverRepository:
    def get_all(self):
        with Database() as cursor:
            cursor.execute("SELECT * FROM drivers")
            rows = cursor.fetchall()
            return [Driver(**row) for row in rows]

    def find_by_id(self, driver_id):
        with Database() as cursor:
            cursor.execute("SELECT * FROM drivers WHERE driver_id = %s", (driver_id,))
            row = cursor.fetchone()
            return Driver(**row) if row else None

    def add_driver(self, data):
        sql = """
            INSERT INTO drivers (first_name, last_name, license_number, phone_number, experience_years) 
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (data.get('first_name'), data.get('last_name'),
                  data.get('license'), data.get('phone'), data.get('exp', 0))
        with Database() as cursor:
            cursor.execute(sql, params)

    def delete(self, driver_id):
        with Database() as cursor:
            cursor.execute("DELETE FROM drivers WHERE driver_id = %s", (driver_id,))


class VehicleRepository:
    def get_all(self):
        with Database() as cursor:
            cursor.execute("SELECT * FROM vehicles")
            rows = cursor.fetchall()
            return [Vehicle(**row) for row in rows]

    def find_by_id(self, vehicle_id):
        with Database() as cursor:
            cursor.execute("SELECT * FROM vehicles WHERE vehicle_id = %s", (vehicle_id,))
            row = cursor.fetchone()
            return Vehicle(**row) if row else None

    def add_vehicle(self, data):
        sql = """
            INSERT INTO vehicles (license_plate, brand, capacity_tons, fuel_consumption_l_per_100km) 
            VALUES (%s, %s, %s, %s)
        """
        params = (data.get('plate'), data.get('brand'),
                  data.get('capacity'), data.get('fuel'))
        with Database() as cursor:
            cursor.execute(sql, params)

    def delete(self, vehicle_id):
        with Database() as cursor:
            cursor.execute("DELETE FROM vehicles WHERE vehicle_id = %s", (vehicle_id,))


class LocationRepository:
    def get_all(self):
        with Database() as cursor:
            cursor.execute("SELECT * FROM locations ORDER BY name ASC")
            rows = cursor.fetchall()
            return [Location(**row) for row in rows]

    def find_by_id(self, loc_id):
        with Database() as cursor:
            cursor.execute("SELECT * FROM locations WHERE location_id = %s", (loc_id,))
            row = cursor.fetchone()
            return Location(**row) if row else None

    def search_by_name(self, query):
        with Database() as cursor:
            cursor.execute("SELECT location_id, name FROM locations WHERE name LIKE %s LIMIT 10", (query + '%',))
            return cursor.fetchall()

    def get_all_coordinates(self):
        with Database() as cursor:
            cursor.execute("SELECT location_id, latitude, longitude FROM locations")
            rows = cursor.fetchall()
            return {r['location_id']: (float(r['latitude']), float(r['longitude'])) for r in rows}

    def add_location(self, data):
        sql = "INSERT INTO locations (name, latitude, longitude) VALUES (%s, %s, %s)"
        with Database() as cursor:
            cursor.execute(sql, (data.get('name'), data.get('latitude'), data.get('longitude')))

    def delete(self, loc_id):
        with Database() as cursor:
            cursor.execute("DELETE FROM locations WHERE location_id = %s", (loc_id,))


class RouteRepository:
    def get_all(self):
        with Database() as cursor:
            cursor.execute("SELECT * FROM routes")
            return cursor.fetchall()

    def get_graph_data(self):
        with Database() as cursor:
            cursor.execute("SELECT origin_id, destination_id, distance_km FROM routes")
            rows = cursor.fetchall()
            graph = {}
            for row in rows:
                u, v, w = row['origin_id'], row['destination_id'], float(row['distance_km'])
                if u not in graph: graph[u] = {}
                graph[u][v] = w
            return graph


class TripRepository:
    def get_all(self):
        with Database() as cursor:
            cursor.execute("SELECT * FROM trips")
            return cursor.fetchall()

    def get_all_with_names(self):
        sql = """
            SELECT t.*, d.first_name, d.last_name, v.license_plate, v.brand, 
                   l1.name AS origin_city, l2.name AS dest_city
            FROM trips t
            JOIN drivers d ON t.driver_id = d.driver_id
            JOIN vehicles v ON t.vehicle_id = v.vehicle_id
            JOIN locations l1 ON t.origin_id = l1.location_id
            JOIN locations l2 ON t.destination_id = l2.location_id
            ORDER BY t.departure_datetime DESC
        """
        with Database() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def save(self, trip):
        sql = """
            INSERT INTO trips (vehicle_id, driver_id, client_id, origin_id, destination_id, 
                               total_distance_km, status, cargo_weight_tons, departure_datetime)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (trip.vehicle_id, trip.driver_id, trip.client_id, trip.origin_id,
                  trip.destination_id, trip.total_distance, trip.status,
                  trip.cargo_weight, trip.departure_datetime)
        with Database() as cursor:
            cursor.execute(sql, params)
            return cursor.lastrowid

    def update_status(self, trip_id, new_status):
        with Database() as cursor:
            if new_status == 'finished' or new_status == 'delivered':

                sql = "UPDATE trips SET status = %s, arrival_datetime = %s WHERE trip_id = %s"
                cursor.execute(sql, ('delivered', datetime.now(), trip_id))
            else:
                sql = "UPDATE trips SET status = %s WHERE trip_id = %s"
                cursor.execute(sql, (new_status, trip_id))
            return True

class ClientRepository:
    def get_all(self):
        with Database() as cursor:
            cursor.execute("SELECT * FROM clients ORDER BY name ASC")
            return cursor.fetchall()

    def add(self, name):
        with Database() as cursor:
            cursor.execute("INSERT INTO clients (name) VALUES (%s)", (name,))
            return cursor.lastrowid