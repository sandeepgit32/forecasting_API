import os, utils
from flask import Flask, jsonify, request 
from dotenv import load_dotenv
load_dotenv(".env", verbose=True)


app = Flask(__name__) 


@app.route("/forecast", methods = ["GET", "POST"]) 
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
    - Performs AutoTS forecasting using the provided input data.
    - Returns the forecast data path if successful.
    - Returns a 400 error if the input is invalid.
    - Returns a 500 error if there is an error in forecasting.
    """
    forecastDataPath = os.environ.get("FORECAST_DATA_PATH")
    if(request.method == "GET"):
        if os.path.exists(forecastDataPath):
            return jsonify({
                "status": "True",
                "dataPath": forecastDataPath
            }), 200
        else:
            return jsonify({
                "status": "False",
                "message": "No forecast data found"
            }), 404

    elif(request.method == "POST"): 
        input_data = request.get_json()

        input_file_path = input_data.get("filePath")
        forecast_length = input_data.get("forecastLength")
        date_col = input_data.get("dateCol")
        value_col = input_data.get("valueCol")
        forecast_type = input_data.get("forecastType") # "monthly"/"weekly"
        period_of_seasonality = input_data.get("periodOfSeasonality")
        if (
            (input_file_path is None)
            or (forecast_length is None)
            or (date_col is None)
            or (value_col is None)
            or (forecast_type not in ("monthly", "weekly"))
            or (period_of_seasonality is None)
        ):
            return jsonify({
                "status": "False",
                "message": "Invalid input"
            }), 400
        try:
            data_df = utils.fetch_data(
                input_file_path, date_col, value_col
            )
            if type(data_df) is dict:
                return jsonify({
                    "status": "False",
                    "message": data_df["message"]
                }), 400
            utils.calculate_forecast_data(
                data_df, 
                forecast_length, 
                date_col, 
                value_col, 
                forecast_type, 
                period_of_seasonality
            )
            return jsonify({
                "status": "True",
                "dataPath": forecastDataPath
            }), 200
        except:
            return jsonify({
                "status": "False",
                "message": "Error in forecasting"
            }), 500


# main function 
if __name__ == "__main__": 
    app.run(host="0.0.0.0", port=5000, debug = True)
