## A Simple API for Forecasting using Flask

A simple API to get the future forecast for time series data using Flask.


### Steps of Code Execution (Development)

  1. Install `Python 3.9`.
  2. Clone repository and go inside this directory.
  3. Create a Python `virtualenv` and enter inside the `virtuallenv`.
  4. Run the following command.
  ```bash
    python app.py
  ```
  5. The API server will be run on  `http://127.0.0.1:5000`.
  6. To stop the server press `CTRL + C`.


### Steps of Code Execution (Production)

  1. Install `Docker` and `Docker Compose`.
  2. Clone repository and go inside this directory
  3. Run
  ```bash
    docker-compose up --build [-d]
  ```
  4. The API server will be run on  `http://127.0.0.1:5000`.
  5. To stop the server run:
  ```bash
    docker-compose down
  ```
