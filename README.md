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

### API Call (POST request)

  - Request: Send the HTTP POST request on endpoint `/forecast` with a body having the following format:
  ```
    {
        "filePath": "<input_filename_with_path>",
        "forecastLength": <Integer>,
        "dateCol": "<date_column>",
        "valueCol": "<value_column>",
        "forecastType": "monthly" / "weekly",
        "periodOfSeasonality": <Integer>
    }
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