# Optimization of Taxi Service in New York City with Distributed Cloud Computing

This repository contains the code of the class project for [CS 5412 Cloud Computing, Spring 2019](http://www.cs.cornell.edu/courses/cs5412/2019sp/) at Cornell University.

## Authors

- Summer Li    jl3879@cornell.edu
- Bowen Mao    bm644@cornell.edu
- Haoran Yang  hy538@cornell.edu

## Components

Below are brief descriptions of all the components. For detail, please refer to the final report.

### Model

`model.ipynb` is an IPython Notebook. It pre-processes [New York City yellow taxi trip records](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page) in the Year 2017, builds the original mathematical model and evaluates the performance of the model.

### Front-end Web App

`cloud-frontend` (`nyc-taxi-cs/www/`) contains our static front-end web app. It is deployed as a submodule of the Azure Function `nyc-taxi-cs`.

`split.py` (`nyc-taxi-cs/www/data/split.py`) is a Python script which pre-processes GeoJSON files in order to show the taxi zones on the map.

### Sensor Simulation

`taxi-simulation` contains a Node.js program which simulates sensors and sends taxi trip records to the Azure IoT Hub.

`preprocess.ipynb` (`taxi-simulation/preprocess.ipynb`) converts CSV-format trip record files into JSON format and splits the records into smaller files organized by date and hour.

### Azure Functions

`nyc-taxi-cs2` contains a C# Script Azure Function, `IoTHubEventTrigger`. It is an IoT Hub event trigger which receives an IoT Hub event (i.e. an incoming IoT Hub message), pre-processes the input data and sends output to the cache (i.e.
Azure Cosmos DB).

`nyc-taxi-py` contains a Python Azure Function, `CalcCachedDataTimerTrigger`. It is a timer trigger firing hourly at HH:05 and performs model update.

`nyc-taxi-py2` contains two Python Azure Functions. `QueryHttpTrigger` is an HTTP trigger which return the expected income for all taxi zones as well as the zone IDs of the top three zones where the expected income is the highest. `UpdateFilesTimerTrigger` is a timer trigger firing hourly at HH:15 (10 minutes after the firing of `CalcCachedDataTimerTrigger`) to pull the latest model files.

`nyc-taxi-cs` contains a C# Script Azure Function, `StaticFileServer`, adopted from https://anthonychu.ca/post/azure-functions-static-file-server/. It is a static file server serving our front-end web application. 

### Stress Test

`locustfile.py` is a Python script performing stress tests on the Front-end Web App.
