#!flask/bin/python
from flask import Flask, request, jsonify, abort, make_response
from flask_cors import CORS
import os
from routefinder import RouteFinder

app = Flask(__name__)
CORS(app)
rf = RouteFinder()


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


# On IBM Cloud Cloud Foundry, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8000))

# curl -i "http://0.0.0.0:8000/route?origin=Exit_4&destination=C3-1"
# curl -i "https://dr-watson.us-south.cf.appdomain.cloud/route?origin=Exit_4&destination=C3-1"
# output: {'route': ['Exit_4', 'C1-2', 'E-1', 'E-2', 'E-3', 'C3-1']}
@app.route('/route', methods=['GET'])
def get_optimal_route():
    origin = request.args.get('origin', None)
    destination = request.args.get('destination')
    route = []

    if origin is None and destination is None:
        abort(404)
    elif origin is None:
        route = rf.optimal_entry_route(destination)
    elif destination is None:
        route = rf.optimal_exit_route(origin)
    else:
        route = rf.optimal_route(origin, destination)

    return jsonify({'route': route})


# curl -X PATCH "http://localhost:8000/compromised?zones[]=C2-1&zones[]=C3-1"
# curl -X PATCH "http://localhost:8000/compromised?zones[]=C2-1"
# curl -X PATCH "https://dr-watson.us-south.cf.appdomain.cloud/compromised?zones[]=C2-1&zones[]=C3-1"
@app.route('/compromised', methods=['PATCH'])
def remove_compromised_zones():
    zones = request.args.getlist('zones[]', None)
    if zones is None:
        abort(404)

    rf.remove_node(zones)
    removed = {}
    for zone in zones:
        removed[zone] = not rf.G.has_node(zone)

    return jsonify({'removed': removed})


# curl -i "http://localhost:8000/refresh"
# curl -i "https://dr-watson.us-south.cf.appdomain.cloud/refresh"
@app.route('/refresh', methods=['GET'])
def refresh():
    rf.reset_graph()

    return jsonify({'reset': True})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=False)
