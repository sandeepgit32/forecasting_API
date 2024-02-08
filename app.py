import os, utils, db
from functools import wraps
from flask_bcrypt import Bcrypt
from flask import Flask, jsonify, request, render_template, redirect, url_for, session, send_from_directory
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
load_dotenv(".env", verbose=True)


app = Flask(__name__)
app.secret_key = os.environ.get('APP_SECRET_KEY')
bcrypt_obj = Bcrypt(app)


def authentication_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs): 
        if session.get('logged_in'):
            return func(*args, **kwargs)
        else:
            return render_template('login.html')
    return wrapper


@app.route('/favicon.ico')
def favicon():
    '''
    Get the fabicon file without using html
    '''
    return send_from_directory(
        os.path.join(app.root_path, 'static'), 
        'images/icons/favicon.ico', \
        mimetype='image/vnd.microsoft.icon'
    )


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        if session.get('logged_in'):
            return redirect(url_for('index'))
        return render_template('register.html')
    else:
        if request.form['password'] != request.form['repassword']:
            return render_template('register.html', message="Passwords do not match!")
        # Hashing the password
        hashPassword = bcrypt_obj.generate_password_hash(request.form['password'])
        user_existance_flag = db.is_user_exist(request.form['username'])
        if not user_existance_flag:
            db.add_user_data(
                request.form['username'], 
                request.form['name'], 
                request.form['surname'],
                hashPassword
            )
            session['registration_message'] = "User created successfully! Please log in."
            return redirect(url_for('login'))
        else:
            return render_template('register.html', message="User Already Exists!")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if session.get('logged_in'):
            return redirect(url_for('index'))
        if session.get('registration_message'):
            message = session.get('registration_message')
            session['registration_message'] = None
            return render_template('login.html', message=message)
        else:
            return render_template('login.html')
    else:
        u = request.form['username']
        p = request.form['password']
        user_existance_flag = db.is_user_exist(u)
        if not user_existance_flag:
            return render_template('login.html', message="Incorrect Details!")
        user_data = db.get_user_data(u)
        if user_data is not None:
            # Password is checked
            hashPassword = db.retrieve_password_hash(u)
            if bcrypt_obj.check_password_hash(hashPassword, p):
                session['logged_in'] = "True"
                session['user'] = u # Store the username in session variable for display after redirection
                session['name'] = user_data["name"]
                session['surname'] = user_data["surname"]
                return redirect(url_for('index'))
        return render_template('login.html', message="Incorrect Details!")


@app.route('/logout', methods=['GET'])
def logout():
    session['logged_in'] = False
    session['user'] = None
    session['name'] = None
    session['surname'] = None
    return redirect(url_for('login'))


@app.route('/', methods=['GET'])
@authentication_required
def index():
    return render_template('index.html', 
        welcome_name=f'{session["name"]} {session["surname"]}',
        logged_in="True"
    )


@app.route("/forecast", methods=["GET"])
@authentication_required
def forecast():
    """
    Endpoint for performing forecasting.

    GET Method:
    - Returns the forecast data path if it exists.
    - Returns a 404 error if no forecast data is found.

    POST Method:
    - Accepts input data in JSON format.
    - The input data should have the following format:
        {
            "filePath": <string>
            "forecastLength": <integer>
        }
    - Performs forecasting using the provided input data.
    - Returns the forecast data path if successful.
    - Returns a 400 error if the input is invalid.
    - Returns a 500 error if there is an error in forecasting.
    """
    if request.method == "GET":
        try:
            input_file_path = os.environ.get("INPUT_DATA_PATH")
            forecast_length = int(request.args.get("forecastLength"))
            date_col = request.args.get("dateCol")
            value_col = request.args.get("valueCol")
            forecast_type = request.args.get("forecastType")
            period_of_seasonality = int(request.args.get("periodOfSeasonality"))
        except:
            return render_template(
                "forecast.html", status="False", message="Invalid URL"
            )
        if (
            (input_file_path is None)
            or (forecast_length is None)
            or (date_col is None)
            or (value_col is None)
            or (forecast_type is None)
            or (period_of_seasonality is None)
        ):
            return render_template(
                "forecast.html", status="False", message="Invalid URL"
            )
        if forecast_type not in ("monthly", "weekly"):
            return render_template(
                "forecast.html",
                status="False",
                message="Invalid forecast type (valid type: monthly/weekly)",
            )
        if forecast_type == "monthly":
            forecastDataPath = os.environ.get("FORECAST_DATA_PATH_MONTHLY")
        elif forecast_type == "weekly":
            forecastDataPath = os.environ.get("FORECAST_DATA_PATH_WEEKLY")
        try:
            data_df = utils.fetch_data(input_file_path, date_col, value_col)
            if type(data_df) is dict:
                return render_template(
                    "forecast.html", status="False", message=data_df["message"]
                )
            forecast = utils.calculate_forecast_data(
                data_df,
                forecast_length,
                date_col,
                value_col,
                forecast_type,
                period_of_seasonality,
            )
            forecast.to_csv(forecastDataPath, index=False)
            return render_template(
                "forecast.html", status="True", dataPath=forecastDataPath
            )
        except:
            return render_template(
                "forecast.html",
                status="False",
                message="The algorithm cannot forecast the data.",
            )


@app.route("/statistics", methods=["GET"])
@authentication_required
def statistics():
    if request.method == "GET":
        try:
            input_file_path = os.environ.get("INPUT_DATA_PATH")
            statisticsDataPath = os.environ.get("STATISTICS_DATA_PATH")
            data_df = utils.fetch_raw_data(input_file_path)
            if type(data_df) is dict:
                return render_template(
                    "statistics.html", status="False", message=data_df["message"]
                )
            describe_df = data_df.describe(include='all')
            describe_df.insert(0, 'Statistics', describe_df.index)
            describe_df.to_csv(statisticsDataPath, index=False)
            return render_template(
                "statistics.html", status="True", dataPath=statisticsDataPath
            )
        except:
            return render_template(
                "statistics.html", status="False", message="Internal server error"
            )


# main function
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)