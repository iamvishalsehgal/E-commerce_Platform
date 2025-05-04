import os

from flask import Flask, request
#from flask_cors import CORS

from db import Base, engine
from resources.tracking import Tracking

app = Flask(__name__)
app.config["DEBUG"] = True
Base.metadata.create_all(engine)
#CORS(app)

@app.route("/tracking/register", methods=["POST"])
def register_tracking():
    req_data = request.get_json()
    return Tracking.create(req_data)

@app.route("/tracking/<tracking_id>", methods=["GET"])
def get_tracking_status(tracking_id):
    return Tracking.get(tracking_id)

@app.route("/tracking/<tracking_id>", methods=["PUT"])
def update_tracking_status(tracking_id):
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    return Tracking.put(tracking_id, latitude, longitude)

if __name__ == '__main__':
    app.run(port=int(os.environ.get("PORT", 5003)), host='0.0.0.0', debug=True)
    #app.run(port=int(os.environ.get("PORT", 5003)), host='0.0.0.0', debug=True, use_reloader=False)