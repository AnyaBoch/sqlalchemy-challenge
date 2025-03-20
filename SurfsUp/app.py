# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
from flask import Flask, jsonify

# SQLAlchemy dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


#################################################
# Database Setup
#################################################
#creating engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
# Initialize Flask app
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """Hawaii Climate Analysis API"""
    return (
        f"<h1>Hawaii Climate API</h1>"
        f"<h3>Available Routes:</h3>"
        f"<ul>"
        f"<li>/api/v1.0/precipitation - Last year's precipitation data</li>"
        f"<li>/api/v1.0/stations - List of all stations</li>"
        f"<li>/api/v1.0/tobs - Temperature observations for the most active station</li>"
        f"<li>/api/v1.0/<start>- enter any date in #yyyy-mm-dd# format - Min, Max, Avg temperatures from start date</li>"
        f"<li>/api/v1.0/v1.0/<start>/<end> - enter any code in #yyyy-mm-dd/yyyy-mm-dd# - Min, Max, Avg temperatures for date range</li>"
        f"</ul>"
        f"Observed period of time is 2010-01-01 till 2017-08-23 / enter format yyyy-mm-dd"

    )

#####################route - precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    #create our session (link) from Python to the DB
    session = Session(engine)
    # Find the most recent date
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    query_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Query precipitation data
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= query_date).all()
    
    session.close()

    # Convert to dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    
    return jsonify(precipitation_dict)

####################route - stations
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all stations as JSON."""
    session = Session(engine)

    # Query all stations
    stations = session.query(Station.station).all()
    session.close()

    # Convert list of tuples into normal list
    stations_list = [station[0] for station in stations]

    return jsonify(stations_list)

####################route - tobs
@app.route("/api/v1.0/tobs")
def tobs():
    """Return the temperature observations for the most active station for the last year."""
    session = Session(engine)

    # Finding the most active station
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]

    # Finding the most recent date
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    query_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Query temperature data
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= query_date).all()

    session.close()

    # Convert to dictionary
    temperature_list = [{date: tobs} for date, tobs in temperature_data]

    return jsonify(temperature_list)

######################route - <start>
@app.route("/api/v1.0/<start>")

def start(start):
    """Return min, avg, and max temperature for most active station for a specified start or start-end range"""
    session = Session(engine)


    # Query temperature statistics
    results = session.query(func.min(Measurement.tobs),
                            func.avg(Measurement.tobs),
                            func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).all()

    session.close()

    temp_stat = []
    for min, avg,max in results:
        tobs_dict = {}
        tobs_dict["Tmin"] = min
        tobs_dict["Tavg"] = avg
        tobs_dict ["Tmax"] = max
        temp_stat.append(tobs_dict)

    return jsonify(temp_stat)

##########################route - <start>/<end>
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)

    # Query temperature statistics
    results = session.query(func.min(Measurement.tobs),
                            func.avg(Measurement.tobs),
                            func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).\
              filter(Measurement.date <= end).all()

    session.close()

    # Convert results into a dictionary
    temp_stats = []

    for min, avg,max in results:
        tobs_dict = {}
        tobs_dict["Tmin"] = min
        tobs_dict["Tavg"] = avg
        tobs_dict ["Tmax"] = max
        temp_stats.append(tobs_dict)

    return jsonify(temp_stats)

# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True)