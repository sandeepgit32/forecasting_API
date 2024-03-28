import os
import itertools
import numpy as np
import pandas as pd
from prophet import Prophet
import statsmodels.api as sm
from dotenv import load_dotenv
load_dotenv(".env", verbose=True)
CONFIDENCE_LEVEL = float(os.environ.get("CONFIDENCE_LEVEL"))


def process_data(value_df, date_col, value_col, forecast_type):
    """
    This function will process the value_df containing the date-wise values
    by aggregating the into month-wise/week-wise summary.
    """
    value_df.set_index(date_col, inplace=True)
    if forecast_type == "monthly":
        value_ts = value_df[value_col].resample("MS").sum()
    elif forecast_type == "weekly":
        value_ts = value_df[value_col].resample("W-MON").sum()
    return value_ts


def get_forecast_using_sarimax_model(
    value_df, forecast_length, value_col, period_of_seasonality
):
    """
    This function returns the range of forecast in terms of a dataframe as well as the 
    mean forecast as pandas series format. Forecast range format:

                lower value 	upper value
    2022-02-01 	0.000000e+00 	6.157182e+05
    2022-03-01 	2.120170e+06 	3.861684e+06
    2022-04-01 	1.885155e+07 	2.098446e+07
    2022-05-01 	2.021819e+07 	2.268106e+07
    2022-06-01 	1.531324e+07 	1.806681e+07
    2022-07-01 	1.131891e+07 	1.433530e+07
    2022-08-01 	1.736294e+06 	4.994368e+06

    Forecast mean format:

    2022-02-01   -8.790682e-11
    2022-03-01    2.990927e+06
    2022-04-01    1.991800e+07
    2022-05-01    2.144963e+07
    2022-06-01    1.669003e+07
    2022-07-01    1.282710e+07
    2022-08-01    3.365331e+06
    2022-09-01    2.956771e+06
    2022-10-01    1.345307e+06
    2022-11-01    1.446777e+06
    Freq: MS, Name: predicted_mean, dtype: float64
    """
    try:
        pqd, seasonal_pqd = get_optimal_parameters_for_sarimax(
            value_df, value_col, forecast_length, period_of_seasonality
        )
        model_sarimax = sm.tsa.statespace.SARIMAX(
            value_df, order=pqd, seasonal_order=seasonal_pqd
        )
        results = model_sarimax.fit(disp=False)
        forcast = results.get_forecast(steps=forecast_length)
        req_prob = CONFIDENCE_LEVEL / 100
        forcast_ci = forcast.conf_int(alpha=1 - req_prob)
        # forcast_ci[forcast_ci < 0] = 0
        return forcast_ci, forcast.predicted_mean
    except:
        return None, None


def get_optimal_parameters_for_sarimax(
    value_df, value_col, forecast_length, period_of_seasonality
):
    # Define the p, d and q parameters to take any value between 0 and 2
    p = d = q = range(0, 2)
    # Generate all different combinations of p, q and q triplets
    pdq = list(itertools.product(p, d, q))
    # Generate all different combinations of seasonal p, q and q triplets
    m = period_of_seasonality
    seasonal_pdq = [(x[0], x[1], x[2], m) for x in list(itertools.product(p, d, q))]

    AIC_dict = {}
    pqd_dict = {}
    seasonal_pqd_dict = {}
    count = 0

    for param in pdq:
        for param_seasonal in seasonal_pdq:
            try:
                mod = sm.tsa.statespace.SARIMAX(
                    value_df, order=param, seasonal_order=param_seasonal
                )
                results = mod.fit(disp=False)
                AIC_dict[f"ARIMA{param}x{param_seasonal}"] = results.aic
                pqd_dict[f"ARIMA{param}x{param_seasonal}"] = param
                seasonal_pqd_dict[f"ARIMA{param}x{param_seasonal}"] = param_seasonal
                count += 1
                print('{}: ARIMA{}x{};  AIC:{:.4f}'.format(count, param, param_seasonal, results.aic))
            except:
                continue

    for _ in range(len(pqd_dict)):
        optimal_key = min(AIC_dict, key=AIC_dict.get)
        mod = sm.tsa.statespace.SARIMAX(
            value_df,
            order=pqd_dict[optimal_key],
            seasonal_order=seasonal_pqd_dict[optimal_key],
        )
        results = mod.fit(disp=False)
        # results.summary()
        forecast = results.get_forecast(steps=forecast_length)
        req_prob = CONFIDENCE_LEVEL / 100
        forecast_ci = forecast.conf_int(alpha=1 - req_prob)
        if True in forecast_ci[f"lower {value_col}"].isnull().tolist():
            del AIC_dict[optimal_key]
            continue
        else:
            break
    optimal_key = min(AIC_dict, key=AIC_dict.get)
    return pqd_dict[optimal_key], seasonal_pqd_dict[optimal_key]


def fetch_data(file_path, date_col, value_col):
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path)
        else:
            return {
                "message": "Invalid file format (Valid format: `.csv` and `.xlsx`)."
            }
    except:
        return {
            "message": "The file does not exist"
        }
    try:
        df = df[[date_col, value_col]]
        df[date_col] = pd.to_datetime(df[date_col])
        return df
    except:
        return {
            "message": "The specified column(s) does not exist in the file."
        }


def fetch_data_with_product_filter(
    file_path,
    date_col, 
    value_col,
    product_family_col,
    product_name_col,
    product_family,
    product_name
    ):
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path)
        else:
            return {
                "message": "Invalid file format (Valid format: `.csv` and `.xlsx`)."
            }
    except:
        return {
            "message": "The file does not exist"
        }
    try:
        df = df[[date_col, value_col, product_family_col, product_name_col]]
        if product_family == "All":
            df = df[[date_col, value_col]]
            df[date_col] = pd.to_datetime(df[date_col])
            return df
        else:
            if product_name == "All":
                df = df[df[product_family_col] == product_family]
            else:
                df = df[(df[product_family_col] == product_family) \
                    & (df[product_name_col] == product_name)]
            df = df[[date_col, value_col]]
            df[date_col] = pd.to_datetime(df[date_col])
            return df
    except:
        return {
            "message": "The specified column(s) does not exist in the file."
        }


def fetch_raw_data(file_path):
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path)
        else:
            return {
                "message": "Invalid file format (Valid format: `.csv` and `.xlsx`)."
            }
        return df
    except:
        return {
            "message": "The file does not exist"
        }


def calculate_forecast_data(
    data_df, 
    forecast_length, 
    date_col, 
    value_col, 
    forecast_type, 
    period_of_seasonality
):
    processed_value_df = process_data(
        data_df, date_col, value_col, forecast_type
    )
    forecast_ci, mean_forecast = get_forecast_using_sarimax_model(
        processed_value_df, forecast_length, value_col, period_of_seasonality
    )
    print('-------->', forecast_ci, mean_forecast)
    forecast = pd.concat([forecast_ci, mean_forecast], axis=1)
    # Eliminate the negative values from the forecast
    forecast[forecast < 0] = 0
    print('-------->')
    print(forecast)
    forecast[date_col] = forecast.index
    return forecast, processed_value_df


def calculate_prophet_forecast_data(
    data_df, 
    forecast_length, 
    date_col, 
    value_col, 
    forecast_type, 
):
    processed_value_df = process_data(
        data_df, date_col, value_col, forecast_type
    )
    # Move the index of the series processed_value_df to a column
    df = processed_value_df.copy()
    df = df.reset_index()
    df1 = pd.DataFrame()
    df1['ds'] = pd.to_datetime(df[date_col])
    df1['y'] = df[value_col]
    m = Prophet()
    m.fit(df1)
    # freq = 'M' for monthly and 'W' stands for weekly frequency.
    future = m.make_future_dataframe(
        periods=forecast_length,
        freq='M' if forecast_type == 'monthly' else 'W'
    )  
    forecast = m.predict(future)
    forecast = forecast[-forecast_length:]
    forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    # Eliminate the negative values from the forecast
    forecast['yhat'][forecast['yhat'] < 0] = 0
    forecast['yhat_lower'][forecast['yhat_lower'] < 0] = 0
    # Rename columns for the dataframe
    forecast.columns = [date_col, 'predicted_mean', 'lower Sales', 'upper Sales']
    # Advance the date by one day to make it compatible with ARIMA forecast
    forecast[date_col] = forecast[date_col] + pd.DateOffset(days=1)
    print('-------->', len(forecast))
    print(forecast)
    print('-------->', len(processed_value_df))
    print(processed_value_df)
    return forecast, processed_value_df