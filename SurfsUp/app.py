# Import the dependencies.
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation amounts from the past 12 months: /api/v1.0/precipitation<br/>"
        f"List of stations: /api/v1.0/stations<br/>"
        f"Temperatures from the past 12 months from the most active station, USC00519281: /api/v1.0/tobs<br/>"
        f"Average, Minimum, & Maximum temperatures from a specified start date: /api/v1.0/yyyy-mm-dd <br/>"
        f"Average, Minimum, & Maximum temperatures from a specified start and end date (end date caps off the URL): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )
    
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Calculate the date one year from the last date in data set.
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    
    # Query the date and precipitation amount from past year and order by date ascending
    results = session.query(measurement.date,measurement.prcp).filter(measurement.date >= year_ago)\
    .order_by(measurement.date).all()
    
    # Close the session
    session.close()
    
    # Convert query results to a dictionary where date is key and precipitation amount is the value   
    prepcipitation_dict = {}
    for date, prcp in results:
        prepcipitation_dict[date] = prcp

    # Jsonify the dictionary
    return jsonify(prepcipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query the stations in the dataset
    active_stations = session.query(measurement.station).group_by(measurement.station).all()
    
    # Close the session
    session.close()
    
    # Convert query results to a list of stations
    all_stations = list(np.ravel(active_stations))
    
    # Jsonify the list
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Get the last year based on the most recent date and save it as a variable
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    
    # Query the temp and date from the most active station (USC00519281) from the past year
    most_active_station_stats_year = session.query(measurement.tobs, measurement.date).\
    filter(measurement.date >= year_ago).filter(measurement.station == 'USC00519281').all()
    
    # Close the session
    session.close()
    
    # Convert query results to a list of dates and their corresponding temperatures 
    most_active_stats_list = []
    for tobs, date in most_active_station_stats_year:
        most_active_stats_dict = {}
        most_active_stats_dict["tobs"] = tobs
        most_active_stats_dict["date"] = date
        most_active_stats_list.append(most_active_stats_dict)
     
     # Jsonify the list   
    return jsonify(most_active_stats_list)

@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query the minimum, maximum, and average temperatures from a specific start date
    start_date_stats = session.query(func.min(measurement.tobs),\
        func.max(measurement.tobs),func.avg(measurement.tobs)).\
            filter(measurement.date >= start).all()
    
    # Close the session
    session.close()
    
    # Convert query results to a list of minimum, maximum, and average temperatures
    start_date_list = []
    for tmin, tmax, tavg in start_date_stats:
        start_date_dict = {}
        start_date_dict["min"] = tmin
        start_date_dict["max"] = tmax
        start_date_dict["avg"] = tavg
        start_date_list.append(start_date_dict)
      
    # Jsonify the list    
    return jsonify(start_date_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query the minimum, maximum, and average temperatures within a specific start and end date
    start_end_date_stats = session.query(func.min(measurement.tobs),\
        func.max(measurement.tobs),func.avg(measurement.tobs)).\
            filter(measurement.date >= start).filter(measurement.date <= end).all()
    
    # Close the session
    session.close()
    
    # Convert query results to a list of minimum, maximum, and average temperatures
    start_end_date_list = []
    for tmin, tmax, tavg in start_end_date_stats:
        start_end_date_dict = {}
        start_end_date_dict["min"] = tmin
        start_end_date_dict["max"] = tmax
        start_end_date_dict["avg"] = tavg
        start_end_date_list.append(start_end_date_dict)
    
    # Jsonify the list    
    return jsonify(start_end_date_list)

# Ensure the server only runs when explicitly called by running the script as the main program   
if __name__ == '__main__':
    app.run(debug=True)