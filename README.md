## A Simple API for Forecasting using Flask

A simple API to get the future forecast for time series data using Flask.


### Steps of Code Execution (Localhost)

  1. Install `Python 3.9`.
  2. Clone repository and go inside this directory.
  3. Create a Python `virtualenv` and run install the dependencies inside the `virtualenv`.
  ```bash
    pin install -r requirements.txt
  ```
  4. Run the following command.
  ```bash
    python app.py
  ```
  5. The API server will be run on `http://127.0.0.1:5000`.
  6. To stop the server press `CTRL + C`.


### Steps of Code Execution (Docker)

  1. Install `Docker` and `Docker Compose`.
  2. Clone repository and go inside this directory
  3. Run
  ```bash
    docker-compose up --build [-d]
  ```
  4. The API server will be run on `http://127.0.0.1:5000`.
  5. To stop the server run:
  ```bash
    docker-compose down
  ```

### API Call (GET request)

  - Request: Send the HTTP GET request on the following endpoint format:
  ```
    http://127.0.0.1:5000/forecast?forecastLength=<Integer>&dateCol=<date_column>&valueCol=<value_column>&forecastType=<monthly/weekly>&periodOfSeasonality=<Integer>&productFamilyCol=<product_family_column>&productNameCol=<product_name_column>&productFamily=<product_family>&productName=<product_name>
  ```
  For example:
  ```
    http://127.0.0.1:5000/forecast?forecastLength=6&dateCol=Order%20Date&valueCol=Sales&forecastType=monthly&periodOfSeasonality=12&productFamilyCol=Category&productNameCol=Product%20Name&productFamily=Office%20Supplies&productName=All
  ```
  - Success response: If the forecast is successful, the API will return a response in the following format:
  ```
    {
        "dataPath": "<output_filename_with_path_in_csv_format>",
        "status": "True"
    }
  ```
  - Failure response: If the forecast is unsuccessful, the API will return a response in the following format:
  ```
    {
        "dataPath": "<error_message>",
        "status": "False"
    }
  ```
  - HTTP call for **Missing value identification**
  ```
    http://127.0.0.1:5000/missing_value_identification?dateCol=Order%20Date&valueCol=Sales
  ```

  - HTTP call for **Missing data imputation**
  ```
    http://127.0.0.1:5000/missing_value_imputation?valueCol=Sales
  ```

  - HTTP call for **Outlier detection**
  ```
    http://127.0.0.1:5000/outlier_detection?dateCol=Order%20Date&valueCol=Sales
  ```