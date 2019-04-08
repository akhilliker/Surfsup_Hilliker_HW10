# 1. import Libraries
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# 2. Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)
# 2. Create an app, being sure to pass __name__
app = Flask(__name__)

# 3. Define what to do when a user hits the index route
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"<b><i>Welcome to Your Source for Hawaiian Weather Data! </i></b><br/><br/>"
        f"<b>Available Routes:</b><br/><br/>"
        f"<a href='/api/v1.0/precipitation'> Precipitation </a> <br/><br/>"
        f"<a href='/api/v1.0/stations'> Weather Stations </a> <br/><br/>"
        f"<a href='/api/v1.0/tobs'> Last Year's Temperatures </a> <br/><br/>"
        f"<b>Precipitation On Specified Date:</b> /api/v1.0/start_date  <br/>"
        f"Replace start_date in the URL with requested date in format %Y-%m-%d; example: 2010-11-12 <br/><br/>"
        f"<b>Precipitation Over Date Range: </b> /api/v1.0/start_date/end_date'  <br/>"
        f"Replace start_date and end_date in the URL with vacation date range in format %Y-%m-%d: example: 2010-11-07/2010-11-15 <br/>"
        f"You will be shown the minimum and maximum temp for that date range, as well as the average temp (inclusive of start and end dates). <br><br>"
        f"Range of dates in data set is 2010-01-01 to 2017-08-23"
    )

# 4. Define what to do when a user hits the other routes
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Perform a query to retrieve the data and precipitation from the table"""
    # Query precipitation data from the entire table
    results = session.query(Measurement.date, Measurement.prcp).all()
    # Create a dictionary from the row data and append to a list of all dates
    precip = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        precip.append(prcp_dict)
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    # Query all station names
    station_name = session.query(Station.station).all() 
    # Convert list of tuples into normal list
    all_station_names = list(np.ravel(station_name))
    return jsonify(all_station_names)

@app.route("/api/v1.0/tobs")
def tobs():
    # Query temp data from the past year
    lastyear = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > '2016-08-22').\
        order_by(Measurement.date).all()
    
    # Create a dictionary from the row data and append to a list of all dates
    temp_lastyear = []
    for date, tobs in lastyear:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        temp_lastyear.append(tobs_dict)
    return jsonify(temp_lastyear)

@app.route("/api/v1.0/<start_date>")
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
def calc_temps(start_date):
    return jsonify(session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all())

@app.route("/api/v1.0/<start_date>/<end_date>")
def calc_temps2(start_date, end_date):
    # When given the start and end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

    return jsonify(session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all())


if __name__ == "__main__":
    app.run(debug=False)