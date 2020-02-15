#declarations
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
from flask import Flask, jsonify, request
import os

engine = create_engine('sqlite:///hawaii.sqlite', echo=False)

# Declare a Base using 'automap_base()'
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

#Create app
app = Flask(__name__)

#Homepage
@app.route("/")

def welcome():
   
     print("Server received request for 'Home' page...")
     return (
        f"Treating yourself to a vacation Hawaii?<br/>"
        f"We have the information you need!<br/>"
        f"What would you like to know about?<br/>"
        f"<br/>"
        f"/precipitation<br/>"
        f"/stations<br/>"
        f"/tobs<br/>"
    ) 

#Query for the dates and temperature observations from the last year
begin_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

@app.route("/api/v1.0/precipitation")

def precipitation():

    # Retrieve the last 12 months of precipitation data
    results_precip = session.query(Measurement.date, Measurement.prcp).\
                        filter(Measurement.date > begin_date).order_by(Measurement.date).all()
    
    # Create a dictionary from the row data and append to a list of for the precipitation data
    precip_d = []

    for prcp_data in results_precip:
        prcp_dict = {}
        prcp_dict["Date"] = prcp_data.date
        prcp_dict["Precipitation"] = prcp_data.prcp
        precip_d.append(prcp_dict)
        

    return jsonify(precip_d)

#Query and returns a json list of stations from the dataset    
@app.route("/api/v1.0/stations")

def stations():
    
    # Query all the stations
    results_stations = session.query(Station).all()

    # Create a dictionary from the row data and append to a list of stations.
    stations_complete = []

    for stations in results_stations:
        stations_dict = {}
        stations_dict["Station"] = stations.station
        stations_dict["Station Name"] = stations.name
        stations_dict["Latitude"] = stations.latitude
        stations_dict["Longitude"] = stations.longitude
        stations_dict["Elevation"] = stations.elevation
        stations_complete.append(stations_dict)
    
    return jsonify(stations_complete)


#Json list of Temperature Observations (tobs) for the previous year
@app.route("/api/v1.0/tobs")

def tobs():
    
    # Query all the stations and for the given date. 
    results_tobs = session.query(Measurement.station, Measurement.date, Measurement.tobs).group_by(Measurement.date).\
                    filter(Measurement.date > begin_date).order_by(Measurement.station).all()
                    
    # Create a dictionary from the row data and append to a list of for the temperature data.
    temp_data = []
    for tobs_data in results_tobs:
        tobs_dict = {}
        tobs_dict["Station"] = tobs_data.station
        tobs_dict["Date"] = tobs_data.date
        tobs_dict["Temperature"] = tobs_data.tobs
        temp_data.append(tobs_dict)
    
    return jsonify(temp_data)
#Json list of the minimum temperature, the average temperature, and the max temperature for a given start date
@app.route("/api/v1.0/temp/", methods=['get'])

def start_stats(start=None):
    
    start = request.args.get('start')
    
    # Query all the stations and for the given date. 
    results_temp = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
                    filter(Measurement.date >= start).all()

    # Create a dictionary from the row data and append to a list of for the temperature data.
    temp_hawaii = []
    
    for Tmin, Tmax, Tavg in results_temp:
        temp_hawaii_dict = {}
        temp_hawaii_dict["Minimum Temp"] = Tmin
        temp_hawaii_dict["Maximum Temp"] = Tmax
        temp_hawaii_dict["Average Temp"] = Tavg
        temp_hawaii.append(temp_hawaii_dict)
    
    return jsonify(temp_hawaii)


#Json list of the minimum temperature, the average temperature, and the max temperature for a given start-end date range
@app.route("/api/v1.0/temp-range/", methods=['get'])
def calc_stats(start=None, end=None):
    
    start = request.args.get('start')
    end   = request.args.get('end') 
    
    # Query all the stations and for the given range of dates. 
    results_range = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
                     filter(Measurement.date >= start).\
                         filter(Measurement.date <= end).all()

    # Create a dictionary from the row data and append to a list of for the temperature data.
    alpha_omega = []
    
    for Tmin, Tmax, Tavg in results_range:
        alpha_omega_dict = {}
        alpha_omega_dict["Minimum Temp"] = Tmin
        alpha_omega_dict["Maximum Temp"] = Tmax
        alpha_omega_dict["Average Temp"] = Tavg
        alpha_omega_dict['start']=start
        alpha_omega_dict['end']=end
        alpha_omega.append(alpha_omega_dict)
    
    return jsonify(alpha_omega)

if __name__ == "__main__":
    app.run(debug=True)


