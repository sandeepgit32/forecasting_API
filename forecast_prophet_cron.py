import os
import itertools
import numpy as np
import pandas as pd
from prophet import Prophet

DATE_COL = "Order Date" # Provide the "date" column name here
VALUE_COL = "Sales" # Provide the "value" column name here
PRODUCT_FAMILY_COLUMN = "Category" # Provide the "product family" column name here
PRODUCT_NAME_COLUMN = "Product Name" # Provide the "product name" column name here
FORECAST_TYPE = "monthly" # Provide the forecast type here ("monthly" or "weekly")
FORECAST_LENGTH = 6 # Provide the forecast length here
CONFIDENCE_LEVEL = 90
# Path variables
INPUT_DATA_PATH = os.path.join("files", "Superstore.xlsx")  # Provide the input file path here
ALL_FORECAST_RESULT_PATH = os.path.join("files", f"all_prophet_forecast_result_{FORECAST_TYPE}.csv") # Provide the monthly/weekly forcast result file path here
ALL_FORECAST_ACCURACY_PATH = os.path.join("files", f"all_prophet_forecast_accuracy_{FORECAST_TYPE}.csv") # Provide the monthly/weekly forcast accuracy file path here


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


def calculate_prophet_forecast_data(
    processed_value_df, 
    forecast_length, 
    date_col, 
    value_col, 
    forecast_type, 
):
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
    return forecast


def calculate_forecast_accuracy(
    processed_value_df, 
    forecast_length, 
    date_col, 
    value_col, 
    forecast_type
):
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
    forecast = forecast[-2*forecast_length:-forecast_length]
    forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    # Eliminate the negative values from the forecast
    forecast['yhat'][forecast['yhat'] < 0] = 0
    forecast['yhat_lower'][forecast['yhat_lower'] < 0] = 0
    forecast.columns = [date_col, 'predicted_mean', 'lower Sales', 'upper Sales']
    # Make the date_col as index
    forecast.set_index(date_col, inplace=True)
    y_forecasted = forecast['predicted_mean']
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
    product_family_list = ["All"] + product_family_list
    product_name_list = ["All"] + product_name_list
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
                    FORECAST_TYPE
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
                    FORECAST_TYPE
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