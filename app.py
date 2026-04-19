from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from config import Config
from db_manager import check_db_connection
from services import TransportService, UserService
from repositories import (LocationRepository, VehicleRepository,
                          DriverRepository, TripRepository,
                          UserRepository, ClientRepository, RouteRepository)

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY


loc_repo = LocationRepository()
veh_repo = VehicleRepository()
dr_repo = DriverRepository()
trip_repo = TripRepository()
user_repo = UserRepository()
client_repo = ClientRepository()
route_repo = RouteRepository()


transport_service = TransportService(loc_repo, route_repo, veh_repo, dr_repo, trip_repo, client_repo)
user_service = UserService(user_repo)



@app.route('/')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))


    stats = transport_service.get_dashboard_stats()
    return render_template('index.html', **stats)



@app.route('/planner', methods=['GET', 'POST'])
def planner():
    if 'user_id' not in session:
        return redirect(url_for('login'))


    resources = transport_service.get_planner_resources()

    result = None
    form_data = {}

    if request.method == 'POST':
        form_data = {
            "start_id": request.form.get('start_id'),
            "end_id": request.form.get('end_id'),
            "start_name": request.form.get('start_name_visible'),
            "end_name": request.form.get('end_name_visible'),
            "algorithm": request.form.get('algorithm')
        }


        result = transport_service.calculate_route(
            form_data["start_id"],
            form_data["end_id"],
            algorithm_type=form_data["algorithm"]
        )

        if not result["success"]:
            flash(result["error"])
            result = None

    return render_template('planner.html', result=result, form_data=form_data, **resources)




@app.route('/drivers', methods=['GET', 'POST'])
def manage_drivers():
    if 'user_id' not in session: return redirect(url_for('login'))

    if request.method == 'POST':

        dr_repo.add_driver(request.form)
        flash("Driver added successfully!")

    drivers = dr_repo.get_all()
    return render_template('drivers.html', drivers=drivers)


@app.route('/vehicles', methods=['GET', 'POST'])
def manage_vehicles():
    if 'user_id' not in session: return redirect(url_for('login'))

    if request.method == 'POST':
        veh_repo.add_vehicle(request.form)
        flash("Vehicle added to the fleet!")

    vehicles = veh_repo.get_all()
    return render_template('vehicles.html', vehicles=vehicles)


@app.route('/locations', methods=['GET', 'POST'])
def manage_locations():
    if 'user_id' not in session: return redirect(url_for('login'))

    search_q = request.args.get('search', '')

    if request.method == 'POST':
        loc_repo.add_location(request.form)
        flash("Location added to the network!")


    if search_q:
        locs = loc_repo.search_by_name(search_q)
    else:
        locs = loc_repo.get_all()

    return render_template('locations.html', locations=locs, search_query=search_q)




@app.route('/users', methods=['GET', 'POST'])
def manage_users():

    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Access Denied! Administrators only.")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        success, message = user_service.create_new_user(
            request.form.get('username'),
            request.form.get('password'),
            request.form.get('role')
        )
        flash(message)

    users = user_repo.get_all()
    return render_template('users.html', users=users)


@app.route('/delete_user/<int:id>')
def delete_user(id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('dashboard'))

    if id == session.get('user_id'):
        flash("Security Error: You cannot delete yourself!")
    else:
        user_repo.delete(id)
        flash("User removed.")

    return redirect(url_for('manage_users'))


@app.route('/save_trip', methods=['POST'])
def save_trip():
    if 'user_id' not in session:
        return redirect(url_for('login'))


    success, message = transport_service.schedule_trip(request.form)
    flash(message)

    return redirect(url_for('view_trips') if success else url_for('planner'))


@app.route('/trips')
def view_trips():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    trips = transport_service.get_all_trips_view()
    return render_template('trips.html', trips=trips)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = user_service.authenticate(
            request.form.get('username'),
            request.form.get('password')
        )
        if user:
            session.update({
                'user_id': user.user_id,
                'username': user.username,
                'role': user.role
            })
            return redirect(url_for('dashboard'))
        flash("Invalid username or password!")

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))



@app.route('/api/search')
def search_cities():

    query = request.args.get('q', '')

    results = loc_repo.search_by_name(query)
    return jsonify(results)


@app.route('/add_client_ajax', methods=['POST'])
def add_client_ajax():
    data = request.get_json()

    success, result = transport_service.add_client_quick(data.get('name'))
    return jsonify({"success": success, **result})


@app.route('/delete_driver/<int:id>')
def delete_driver(id):
    if 'user_id' not in session: return redirect(url_for('login'))
    try:
        dr_repo.delete(id)
        flash("Driver removed from the system.")
    except Exception as e:

        flash(f"System Error: {str(e)}")
    return redirect(url_for('manage_drivers'))

@app.route('/delete_vehicle/<int:id>')
def delete_vehicle(id):
    if 'user_id' not in session: return redirect(url_for('login'))
    try:
        veh_repo.delete(id)
        flash("Vehicle removed from fleet.")
    except Exception as e:
        flash("Cannot delete vehicle! It is linked to existing trip records.")
    return redirect(url_for('manage_vehicles'))

@app.route('/delete_location/<int:id>')
def delete_location(id):
    if 'user_id' not in session: return redirect(url_for('login'))
    try:
        loc_repo.delete(id)
        flash("Location removed from network.")
    except Exception as e:
        flash("Cannot delete location! It is part of an active route or trip.")
    return redirect(url_for('manage_locations'))




@app.route('/update_trip_status', methods=['POST'])
def update_trip_status():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    t_id = request.form.get('trip_id')
    stat = request.form.get('status')


    success, message = transport_service.update_trip_status(t_id, stat)

    flash(message)
    return redirect(url_for('view_trips'))


if __name__ == '__main__':
    if check_db_connection():
        app.run(debug=True, port=5000)