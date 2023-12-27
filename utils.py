import os
import pandas as pd
from autots import AutoTS
forecastDataPath = os.environ.get("FORECAST_DATA_PATH")


def fetch_data(input_file_path, date_col, value_col):
    df = pd.read_csv(input_file_path)
    df = df[[date_col, value_col]]
    df[date_col] = pd.to_datetime(df.Date)
    return df


def calculate_forecast_data(
    data_df, forecast_length, date_col, value_col
):
    """
    This function is used to calculate the forecast data.
    Add forecast model here. For example:

    model = AutoTS(
        forecast_length=forecast_length, 
        frequency='infer', 
        ensemble='simple', 
        drop_data_older_than_periods=200
    )
    model = model.fit(
        data_df, 
        date_col=date_col, 
        value_col=value_col, 
        id_col=None
    )
    prediction = model.predict()
    forecast = prediction.forecast
    """
    # Currently we are sending some dummy forecast data.
    forecast = [
        {
            date_col: "2021-01-01",
            value_col: 100
        },
        {
            date_col: "2021-02-01",
            value_col: 120
        },
        {
            date_col: "2021-03-01",
            value_col: 135
        },
        {
            date_col: "2021-03-01",
            value_col: 125
        }
    ]

    forecast = pd.DataFrame(
        forecast, 
        columns=[date_col, value_col]
    )
    forecast.to_csv(forecastDataPath, index=False)
