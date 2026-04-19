from datetime import datetime


class User:

    def __init__(self, user_id=None, username=None, password_hash=None, role='dispatcher', **kwargs):
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash
        self.role = role.lower().strip() if role else 'dispatcher'
        self.is_active = kwargs.get('is_active', 1)

    def is_admin(self):
        return self.role == "admin"

class Driver:
    def __init__(self, driver_id, first_name, last_name, license_number, phone_number=None, experience_years=0, **kwargs):
        self.driver_id = driver_id
        self.first_name = first_name
        self.last_name = last_name
        self.license_number = license_number
        self.phone_number = phone_number
        self.experience_years = int(experience_years or 0)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Vehicle:
    def __init__(self, vehicle_id, license_plate, brand, capacity_tons, fuel_consumption_l_per_100km, **kwargs):
        self.vehicle_id = vehicle_id
        self.license_plate = license_plate
        self.brand = brand
        self.capacity_tons = float(capacity_tons or 0)
        self.fuel_consumption = float(fuel_consumption_l_per_100km or 0)

    def can_carry(self, weight):
        return self.capacity_tons >= float(weight)

class Client:
    def __init__(self, client_id, name, email=None, phone=None, address=None, **kwargs):
        self.client_id = client_id
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address

class Location:
    def __init__(self, location_id, name, latitude, longitude, **kwargs):
        self.location_id = location_id
        self.name = name
        self.latitude = float(latitude)
        self.longitude = float(longitude)

class Route:
    def __init__(self, route_id, origin_id, destination_id, distance_km, is_active=1, **kwargs):
        self.route_id = route_id
        self.origin_id = origin_id
        self.destination_id = destination_id
        self.distance_km = float(distance_km)
        self.is_active = is_active

class Trip:
    def __init__(self, trip_id, vehicle_id, driver_id, client_id, origin_id, destination_id, total_distance_km, status="planned", **kwargs):
        self.trip_id = trip_id
        self.vehicle_id = vehicle_id
        self.driver_id = driver_id
        self.client_id = client_id
        self.origin_id = origin_id
        self.destination_id = destination_id
        self.total_distance = float(total_distance_km or 0)
        self.status = status
        self.cargo_weight = float(kwargs.get('cargo_weight_tons', 0))
        self.departure_datetime = kwargs.get('departure_datetime', datetime.now())