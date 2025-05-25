from flask import Blueprint, request, jsonify
from api.database import *

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/measurements', methods=['GET'])
def list_measurements():
    data = get_all_measurements()
    return jsonify(data), 200

@api_bp.route('/measurements/<int:id>', methods=['GET'])
def get_measurement_by_id(id):
    data = get_measurement(id)
    if data:
        return jsonify(data), 200
    return jsonify({'error': 'Not found'}), 404

@api_bp.route('/measurements', methods=['POST'])
def create_measurement():
    data = request.get_json()
    try:
        add_measurement(data['city'], data['temperature'], data['wind_speed'], data['power_output'])
        return jsonify({'message': 'Measurement added'}), 201
    except:
        return jsonify({'error': 'Invalid data'}), 400

@api_bp.route('/measurements/<int:id>', methods=['PUT'])
def update_measurement_by_id(id):
    data = request.get_json()
    update_measurement(id, data['temperature'], data['wind_speed'], data['power_output'])
    return jsonify({'message': 'Measurement updated'}), 200

@api_bp.route('/measurements/<int:id>', methods=['DELETE'])
def delete_measurement_by_id(id):
    delete_measurement(id)
    return jsonify({'message': 'Measurement deleted'}), 200

@api_bp.route('/measurements', methods=['DELETE'])
def delete_all_measurements():
    delete_all()  # funcție din database.py
    return jsonify({'message': 'All measurements deleted'}), 200

