import os, utils
from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv
load_dotenv(".env", verbose=True)


app = Flask(__name__) 


@app.route("/forecast", methods = ["GET"]) 
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
        try:
            input_file_path = os.environ.get("INPUT_DATA_PATH") 
            forecast_length = int(request.args.get("forecastLength"))
            date_col = request.args.get("dateCol")
            value_col = request.args.get("valueCol")
            forecast_type = request.args.get("forecastType")
            period_of_seasonality = int(request.args.get("periodOfSeasonality"))
        except:
            return render_template(
                "render_page.html", 
                status="False",
                message="Invalid URL"
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
                "render_page.html", 
                status="False",
                message="Invalid URL"
            )
        if forecast_type not in ("monthly", "weekly"):
            return render_template(
                "render_page.html", 
                status="False",
                message="Invalid forecast type (valid type: monthly/weekly)"
            )
        try:
            data_df = utils.fetch_data(
                input_file_path, date_col, value_col
            )
            if type(data_df) is dict:
                return render_template(
                    "render_page.html", 
                    status="False",
                    message=data_df["message"]
                )
            utils.calculate_forecast_data(
                data_df, 
                forecast_length, 
                date_col, 
                value_col, 
                forecast_type, 
                period_of_seasonality
            )
            return render_template(
                "render_page.html", 
                status="True",
                dataPath=forecastDataPath
            )
        except:
            return render_template(
                "render_page.html", 
                status="False",
                message=data_df["message"]
            )


# main function 
if __name__ == "__main__": 
    app.run(host="0.0.0.0", port=5000, debug = True)
