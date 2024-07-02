# Import the dependencies.
import numpy as np
import pandas as pd
import sqlalchemy
import datetime as dt

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Define what to do when the user hits the homepage
@app.route("/")
def homepage():
    return """ <h1> Welcome to the Honolulu, Hawaii Climate Analysis API! </h1>
    <style>body {background-image: url("https://a.cdn-hotels.com/gdcs/production186/d559/a82dee28-b6fd-417c-b51b-a535ddeb2f85.jpg");}</style>

    <h3> The available routes are: </h3>
        <ul>
            <li><a href = "/api/v1.0/precipitation"> Precipitation</a>: <strong>/api/v1.0/precipitation</strong></li>
            <li><a href = "/api/v1.0/stations"> Stations </a>: <strong>/api/v1.0/stations</strong></li>
            <li><a href = "/api/v1.0/tobs"> TOBS </a>: <strong>/api/v1.0/tobs</strong></li>
            <li>To print the minimum, average, and maximum temperatures for a specific start date,</li> 
            <li>press the link and replace the "start" on the URL for a date with the next format "MMDDYYYY"</li>
            <li><a href = "/api/v1.0/<start"> Start Date MIN, AVG and MAX Temperature </a>: <strong>/api/v1.0/start</strong></li>
            <li>To print the minimum, average, and maximum temperatures for a specific start/end date, press the link and replace</li> 
            <li>the "start/end" on the URL for start and end date with the next format "MMDDYYYY"</li>
            <li><a href = "/api/v1.0/<start>/<end>"> Start/End Date MIN, AVG and MAX Temperature </a>: <strong>/api/v1.0/start/end</strong></li>
        </ul>
    """

# Routing for precipitation for the past 12 months 
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    # Calculate the date one year from the last date in data set and Perform a query to retrieve the data and precipitation scores.
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>= prev_year)
    
    session.close()

    # Create a dictionary from the results 
    precip_data = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["precipitation"] = prcp
        precip_data.append(precip_dict)

    return (jsonify(precip_data))


# Routing for station list
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    # Perform a query to get the list the stations from the database
    stations_results = session.query(Station.station).all()

    session.close()

    # Create a dictionary from the results 
    station_data = []
    for station in stations_results:
        station_dict = {}
        station_dict["station name"] = tuple(station) #Added "tuple" to ensure that the station data is kept intact once it is added to the dictionary
        station_data.append(station_dict)

    print(station_data)
    return (jsonify(station_data))


# Routing for temperature observed for the past 12 months on the most active station USC00519281.
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    # Calculate the date one year from the last date in data set and perform a query to retrieve the data and temperature observation.
    prev_year = dt.date(2017, 8, 18) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.tobs).filter((Measurement.station == 'USC00519281')&(Measurement.date>= prev_year)).all()
    
    session.close()

    # Create a dictionary from the results 
    tobs_data = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_data.append(tobs_dict)

    return (jsonify(tobs_data))


# Routing to find a min, max and average temperature observed with a Start date selected by the user
@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine) 

    # Create query for minimum, average, and max tobs and filter by the Start date
    start_date_tobs_results = session.query(*[func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)]).\
        filter(Measurement.date >= start).all()
    
    session.close() 

    # Create a list of the values and appended to a dictionarie
    start_date =[]
    for min, avg, max in start_date_tobs_results:
        sdate_tobs_dict = {}
        sdate_tobs_dict["min"] = min
        sdate_tobs_dict["average"] = avg
        sdate_tobs_dict["max"] = max
        start_date.append(sdate_tobs_dict)
    
    return jsonify(start_date)


# Routing to find a min, max and average temperature observed with a Start/End date selected by the user 
@app.route("/api/v1.0/<start>/<end>")
def Start_end_date(start, end):
    session = Session(engine)
    
    # Create query for minimum, average, and max tobs and filter by the Start/End date
    st_end_date_tobs_results = session.query(*[func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()
  
    # Create a list of the values and appended to a dictionarie
    st_end_tobs_date = []
    for min, avg, max in st_end_date_tobs_results:
        st_end_tobs_date_dict = {}
        st_end_tobs_date_dict["min_temp"] = min
        st_end_tobs_date_dict["avg_temp"] = avg
        st_end_tobs_date_dict["max_temp"] = max
        st_end_tobs_date.append(st_end_tobs_date_dict) 
    
    return jsonify(st_end_tobs_date)
   
if __name__ == '__main__':
    app.run(debug=True) 