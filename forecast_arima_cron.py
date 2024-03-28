import os
import itertools
import numpy as np
import pandas as pd
import statsmodels.api as sm

DATE_COL = "Order Date" # Provide the "date" column name here
VALUE_COL = "Sales" # Provide the "value" column name here
PRODUCT_FAMILY_COLUMN = "Category" # Provide the "product family" column name here
PRODUCT_NAME_COLUMN = "Product Name" # Provide the "product name" column name here
PERIOD_OF_SEASONALITY = 12 # Provide the period of seasonality here
FORECAST_TYPE = "monthly" # Provide the forecast type here ("monthly" or "weekly")
FORECAST_LENGTH = 6 # Provide the forecast length here
CONFIDENCE_LEVEL = 90
# Path variables
INPUT_DATA_PATH = os.path.join("files", "Superstore.xlsx")  # Provide the input file path here
ALL_FORECAST_RESULT_PATH = os.path.join("files", f"all_arima_forecast_result_{FORECAST_TYPE}.csv") # Provide the monthly/weekly forcast result file path here
ALL_FORECAST_ACCURACY_PATH = os.path.join("files", f"all_arima_forecast_accuracy_{FORECAST_TYPE}.csv") # Provide the monthly/weekly forcast accuracy file path here


def process_data(value_df, date_col, value_col, forecast_type):
    """
    This function will process the value_df containing the date-wise values
    by aggregating the into month-wise summary.
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


def fetch_data(file_path, date_col, value_col, product_family, product_name):
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
        df = df[[date_col, value_col, product_family, product_name]]
        df[date_col] = pd.to_datetime(df[date_col])
        return df
    except:
        return {
            "message": "The specified column(s) does not exist in the file."
        }


def filter_data_for_product_family_and_product_name(
    df, 
    date_col, 
    value_col,
    product_family_col,
    product_name_col,
    product_family,
    product_name
):
    if product_family == "All":
        if product_name != "All":
            df = df[df[product_name_col] == product_name]
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


def calculate_forecast_data(
    processed_value_df, 
    forecast_length, 
    date_col, 
    value_col, 
    forecast_type, 
    period_of_seasonality
):
    forecast_ci, mean_forecast = get_forecast_using_sarimax_model(
        processed_value_df, forecast_length, value_col, period_of_seasonality
    )
    forecast = pd.concat([forecast_ci, mean_forecast], axis=1)
    forecast[forecast < 0] = 0
    forecast[date_col] = forecast.index
    return forecast


def calculate_forecast_accuracy(
    processed_value_df, 
    forecast_length, 
    date_col, 
    value_col, 
    forecast_type, 
    period_of_seasonality
):
    forecast_ci, mean_forecast = get_forecast_using_sarimax_model(
        processed_value_df[:-forecast_length], forecast_length, value_col, period_of_seasonality
    )
    mean_forecast[mean_forecast < 0] = 0
    y_forecasted = mean_forecast
    y_truth = processed_value_df[-forecast_length:]
    print('--------y_truth-------->')
    print(y_truth)
    print('--------y_forecasted-------->')
    print(y_forecasted)
    mse = round(((y_forecasted - y_truth) ** 2).mean(), 2)
    # If an element of y_truth is zero, then the percentage error is undefined.
    # To avoid this, we skip the element if y_truth is zero and the corresponding element in y_forecasted is non-zero.
    non_zero_mask = (y_truth != 0)
    y_truth_non_zero = y_truth[non_zero_mask]
    y_forecasted_non_zero = y_forecasted[non_zero_mask]
    mape = round(np.mean(np.abs((y_truth_non_zero - y_forecasted_non_zero)/y_truth_non_zero))*100, 2)
    bias = round((np.sum(y_forecasted_non_zero - y_truth_non_zero)/np.sum(y_truth_non_zero))*100, 2)
    accuracy = round(100 - mape, 2)
    print("mse, mape, bias -------->", mse, mape, bias)
    return mse, mape, bias, accuracy


def main():
    invoice_df = fetch_data(
        INPUT_DATA_PATH, 
        DATE_COL, 
        VALUE_COL,
        PRODUCT_FAMILY_COLUMN,
        PRODUCT_NAME_COLUMN
    )
    product_family_list = invoice_df[PRODUCT_FAMILY_COLUMN].unique().tolist()
    product_name_list = invoice_df[PRODUCT_NAME_COLUMN].unique().tolist()
    product_family_list.append("All")
    product_name_list.append("All")
    accuracy_df = pd.DataFrame(columns=["Product Family", "Product Name", "MSE", "MAPE", "Bias", "Accuracy"])
    for product_family in product_family_list:
        for product_name in product_name_list:
            print(f"Processing forecast for {product_family} - {product_name}")
            data_df = filter_data_for_product_family_and_product_name(
                invoice_df,
                DATE_COL,
                VALUE_COL,
                PRODUCT_FAMILY_COLUMN,
                PRODUCT_NAME_COLUMN,
                product_family,
                product_name
            )
            if data_df.empty:
                continue
            processed_value_df = process_data(
                data_df, 
                DATE_COL,
                VALUE_COL,
                FORECAST_TYPE
            )
            try:
                forecast_df = calculate_forecast_data(
                    processed_value_df,
                    FORECAST_LENGTH,
                    DATE_COL,
                    VALUE_COL,
                    FORECAST_TYPE,
                    PERIOD_OF_SEASONALITY,
                )
            except:
                continue
            forecast_df["Product Family"] = product_family
            forecast_df["Product Name"] = product_name
            forecast_df.to_csv(
                ALL_FORECAST_RESULT_PATH, 
                index=False,
                mode='a', 
                header = not os.path.exists(ALL_FORECAST_RESULT_PATH))
            try:
                mse, mape, bias, accuracy = calculate_forecast_accuracy(
                    processed_value_df, 
                    FORECAST_LENGTH,
                    DATE_COL,
                    VALUE_COL,
                    FORECAST_TYPE,
                    PERIOD_OF_SEASONALITY
                )
            except:
                mse, mape, bias, accuracy = None, None, None, None
            # append data into accuracy_df dataframe
            df_dictionary = pd.DataFrame([{
                "Product Family": product_family,
                "Product Name": product_name,
                "MSE": mse,
                "MAPE": mape,
                "Bias": bias,
                "Accuracy": accuracy
            }])
            accuracy_df = pd.concat(
                [accuracy_df, df_dictionary], 
                ignore_index=True
            )
            accuracy_df.to_csv(
                ALL_FORECAST_ACCURACY_PATH, 
                index=False,
                mode='a', 
                header = not os.path.exists(ALL_FORECAST_ACCURACY_PATH))


if __name__ == "__main__":
    main()