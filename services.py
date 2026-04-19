from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import Trip, User
from router import Router


class TransportService:
    def __init__(self, loc_repo, route_repo, vehicle_repo, driver_repo, trip_repo, client_repo):
        self.loc_repo = loc_repo
        self.route_repo = route_repo
        self.vehicle_repo = vehicle_repo
        self.driver_repo = driver_repo
        self.trip_repo = trip_repo
        self.client_repo = client_repo

    def get_dashboard_stats(self):
        return {
            "loc_count": len(self.loc_repo.get_all()),
            "route_count": len(self.route_repo.get_all()),
            "trips_count": len(self.trip_repo.get_all())
        }

    def get_planner_resources(self):
        return {
            "clients": self.client_repo.get_all(),
            "drivers": self.driver_repo.get_all(),
            "vehicles": self.vehicle_repo.get_all()
        }

    def calculate_route(self, start_id, end_id, algorithm_type="astar"):
        if not start_id or not end_id or start_id == end_id:
            return {"success": False, "error": "Invalid origin or destination."}
        graph = self.route_repo.get_graph_data()
        coords = self.loc_repo.get_all_coordinates()
        engine = Router(graph, coords)
        result = engine.get_route(int(start_id), int(end_id), algorithm=algorithm_type)
        if result["success"]:
            result["cities"] = [self.loc_repo.find_by_id(node_id).name for node_id in result["path"]]
        return result

    def schedule_trip(self, form_data):
        try:

            new_trip = Trip(
                trip_id=None,
                vehicle_id=int(form_data.get('vehicle_id')),
                driver_id=int(form_data.get('driver_id')),
                client_id=int(form_data.get('client_id')),
                origin_id=int(form_data.get('origin_id')),
                destination_id=int(form_data.get('destination_id')),
                total_distance_km=float(form_data.get('total_distance', 0)),
                cargo_weight_tons=float(form_data.get('cargo_weight', 0)),
                status="planned",
                departure_datetime=datetime.now()
            )


            vehicle = self.vehicle_repo.find_by_id(new_trip.vehicle_id)
            if not vehicle.can_carry(new_trip.cargo_weight):
                return False, f"Capacitate depășită pentru {vehicle.license_plate}!"


            trip_id = self.trip_repo.save(new_trip)
            return True, f"Trip #{trip_id} successfully created!"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def update_trip_status(self, trip_id, status):
        """Actualizează statusul și returnează obligatoriu DOUĂ valori."""
        try:
            self.trip_repo.update_status(trip_id, status)
            return True, f"Trip updated to {status}."
        except Exception as e:
            return False, f"Failed to update: {str(e)}"

    def get_all_trips_view(self):
        return self.trip_repo.get_all_with_names()

class UserService:
    def __init__(self, user_repo):
        self.user_repo = user_repo

    def authenticate(self, username, password):
        user = self.user_repo.find_by_username(username)
        if user and check_password_hash(user.password_hash, password):
            return user
        return None

    def create_new_user(self, username, password, role):
        try:
            hashed_pw = generate_password_hash(password)
            new_user = User(None, username, hashed_pw, role)
            self.user_repo.save(new_user)
            return True, f"User {username} created."
        except Exception as e:
            return False, str(e)