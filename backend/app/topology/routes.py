
# backend/app/topology/routes.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.topology.models import TopologyLayout
from app.devices.models import Device, Port
import json

topology_bp = Blueprint('topology', __name__)

@topology_bp.route('/layouts', methods=['GET'])
@jwt_required()
def get_layouts():
    try:
        layouts = TopologyLayout.query.order_by(TopologyLayout.updated_at.desc()).all()
        
        return jsonify({
            'layouts': [layout.to_dict() for layout in layouts]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get topology layouts error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@topology_bp.route('/layouts/<int:id>', methods=['GET'])
@jwt_required()
def get_layout(id):
    try:
        layout = TopologyLayout.query.get_or_404(id)
        return jsonify(layout.to_dict()), 200
        
    except Exception as e:
        current_app.logger.error(f"Get topology layout error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@topology_bp.route('/layouts', methods=['POST'])
@jwt_required()
def create_layout():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        # Required fields
        if not data.get('name'):
            return jsonify({'message': 'Name is required'}), 400
        
        # Check if name already exists
        if TopologyLayout.query.filter_by(name=data['name']).first():
            return jsonify({'message': 'Layout with this name already exists'}), 409
        
        layout = TopologyLayout(
            name=data['name'],
            description=data.get('description'),
            layout_data=json.dumps(data.get('layout_data', {})),
            is_default=data.get('is_default', False),
            created_by=current_user_id
        )
        
        # If this is set as default, unset other defaults
        if layout.is_default:
            TopologyLayout.query.filter_by(is_default=True).update({'is_default': False})
        
        db.session.add(layout)
        db.session.commit()
        
        return jsonify(layout.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Create topology layout error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@topology_bp.route('/current', methods=['GET'])
@jwt_required()
def get_current_topology():
    try:
        # Get all devices and their connections
        devices = Device.query.all()
        
        # Get default layout or create basic layout
        layout = TopologyLayout.query.filter_by(is_default=True).first()
        layout_data = json.loads(layout.layout_data) if layout and layout.layout_data else {}
        
        # Build topology data
        topology_devices = []
        connections = []
        
        for device in devices:
            # Get device position from layout or generate default
            device_layout = layout_data.get('devices', {}).get(str(device.id), {})
            
            topology_device = {
                'id': device.id,
                'name': device.name,
                'type': device.device_type,
                'x': device_layout.get('x', 100),
                'y': device_layout.get('y', 100),
                'status': device.status,
                'ip_address': device.ip_address,
                'ports': [port.to_dict() for port in device.ports]
            }
            topology_devices.append(topology_device)
            
            # Collect connections
            for port in device.ports:
                if port.connected_to_port_id:
                    connected_port = Port.query.get(port.connected_to_port_id)
                    if connected_port and connected_port.device_id > device.id:  # Avoid duplicates
                        connection = {
                            'id': f"{port.id}-{connected_port.id}",
                            'from_device': device.id,
                            'to_device': connected_port.device_id,
                            'from_port': port.id,
                            'to_port': connected_port.id,
                            'status': port.status
                        }
                        connections.append(connection)
        
        return jsonify({
            'devices': topology_devices,
            'connections': connections,
            'layout_id': layout.id if layout else None
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get current topology error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@topology_bp.route('/save', methods=['POST'])
@jwt_required()
def save_topology():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        layout_name = data.get('name', 'Current Layout')
        layout_data = {
            'devices': data.get('devices', {}),
            'connections': data.get('connections', []),
            'canvas_settings': data.get('canvas_settings', {})
        }
        
        # Check if updating existing layout
        layout_id = data.get('layout_id')
        if layout_id:
            layout = TopologyLayout.query.get(layout_id)
            if layout:
                layout.layout_data = json.dumps(layout_data)
                layout.updated_at = datetime.utcnow()
            else:
                return jsonify({'message': 'Layout not found'}), 404
        else:
            # Create new layout
            layout = TopologyLayout(
                name=layout_name,
                description=data.get('description', 'Saved topology layout'),
                layout_data=json.dumps(layout_data),
                created_by=current_user_id
            )
            db.session.add(layout)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Topology saved successfully',
            'layout': layout.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Save topology error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500