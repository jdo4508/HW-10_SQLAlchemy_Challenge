import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


################
# Database Setup
################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# create sessionfrom Python to the DB
session = Session(engine)

#############
# Flask Setup
#############
app = Flask(__name__)


##############
# Flask Routes
##############

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year"""
    #Calculate the date 1 year ago from the last data point in the database
    last_point = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_date = dt.date(2017,8,23) - dt.timedelta(days=365)
    
    #Perform a query to retrieve the data and precipitation scores
    climate_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_date).all()
   
    #Create dictionary with date as the key and prcp as the value
    precip = {date: prcp for date, prcp in climate_data}

    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    results = session.query(Station.station).all()

    #Add results and convert to a list
    stations = list(np.ravel(results))

    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Return the temperature observations (tobs) for previous year."""

    #Calculate the date 1 year ago from the last data point in the database
    last_point = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_date = dt.date(2017,8,23) - dt.timedelta(days=365)
    
    #Query the primary station for tobs
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= year_date).all()

    #Add results and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        #Calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        #Add results and convert to a list
        temps = list(np.ravel(results))
        return jsonify(temps)

    #Calculate TMIN, TAVG, TMAX with start and stop
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    #Add results and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps)


if __name__ == '__main__':
    app.run(debug=True)