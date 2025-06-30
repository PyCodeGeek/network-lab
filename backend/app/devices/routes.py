# # backend/app/devices/routes.py
# from flask import Blueprint, request, jsonify, current_app
# from flask_jwt_extended import jwt_required, get_jwt_identity
# from app import db
# from app.devices.models import Device, Port
# from app.auth.models import User
# from sqlalchemy import or_

# devices_bp = Blueprint('devices', __name__)

# @devices_bp.route('/', methods=['GET'])
# @jwt_required()
# def get_devices():
#     try:
#         # Query parameters
#         page = request.args.get('page', 1, type=int)
#         per_page = min(request.args.get('per_page', 50, type=int), 100)
#         device_type = request.args.get('type')
#         status = request.args.get('status')
#         search = request.args.get('search')
        
#         # Build query
#         query = Device.query
        
#         if device_type:
#             query = query.filter(Device.device_type == device_type)
        
#         if status:
#             query = query.filter(Device.status == status)
        
#         if search:
#             query = query.filter(
#                 or_(
#                     Device.name.ilike(f'%{search}%'),
#                     Device.ip_address.ilike(f'%{search}%'),
#                     Device.description.ilike(f'%{search}%')
#                 )
#             )
        
#         # Paginate
#         devices = query.order_by(Device.created_at.desc()).paginate(
#             page=page, per_page=per_page, error_out=False
#         )
        
#         return jsonify({
#             'devices': [device.to_dict() for device in devices.items],
#             'total': devices.total,
#             'pages': devices.pages,
#             'current_page': page
#         }), 200
        
#     except Exception as e:
#         current_app.logger.error(f"Get devices error: {str(e)}")
#         return jsonify({'message': 'Internal server error'}), 500

# @devices_bp.route('/<int:id>', methods=['GET'])
# @jwt_required()
# def get_device(id):
#     try:
#         device = Device.query.get_or_404(id)
        
#         # Check if user can view sensitive data
#         current_user_id = get_jwt_identity()
#         user = User.query.get(current_user_id)
#         include_sensitive = user and user.role == 'admin'
        
#         return jsonify(device.to_dict(include_sensitive=include_sensitive)), 200
        
#     except Exception as e:
#         current_app.logger.error(f"Get device error: {str(e)}")
#         return jsonify({'message': 'Internal server error'}), 500

# @devices_bp.route('/', methods=['POST'])
# @jwt_required()
# def create_device():
#     try:
#         data = request.get_json()
        
#         if not data:
#             return jsonify({'message': 'No data provided'}), 400
        
#         # Required fields
#         required_fields = ['name', 'device_type', 'ip_address']
#         for field in required_fields:
#             if not data.get(field):
#                 return jsonify({'message': f'{field} is required'}), 400
        
#         # Validate device type
#         valid_types = ['router', 'switch', 'server', 'wireless', 'firewall']
#         if data['device_type'] not in valid_types:
#             return jsonify({'message': f'Invalid device type. Must be one of: {", ".join(valid_types)}'}), 400
        
#         # Check if device with same name or IP exists
#         if Device.query.filter_by(name=data['name']).first():
#             return jsonify({'message': 'Device with this name already exists'}), 409
        
#         if Device.query.filter_by(ip_address=data['ip_address']).first():
#             return jsonify({'message': 'Device with this IP address already exists'}), 409
        
#         # Create device
#         device = Device(
#             name=data['name'],
#             device_type=data['device_type'],
#             ip_address=data['ip_address'],
#             username=data.get('username'),
#             password=data.get('password'),  # Should be encrypted in production
#             ssh_port=data.get('ssh_port', 22),
#             snmp_community=data.get('snmp_community', 'public'),
#             snmp_port=data.get('snmp_port', 161),
#             location=data.get('location'),
#             description=data.get('description'),
#             status='inactive'
#         )
        
#         db.session.add(device)
#         db.session.flush()  # Get the ID
        
#         # Create default ports based on device type
#         default_ports = get_default_ports(device.device_type)
#         for port_data in default_ports:
#             port = Port(
#                 device_id=device.id,
#                 name=port_data['name'],
#                 port_type=port_data['type'],
#                 speed=port_data.get('speed'),
#                 description=f"Default {port_data['type']} port"
#             )
#             db.session.add(port)
        
#         db.session.commit()
        
#         return jsonify(device.to_dict()), 201
        
#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.error(f"Create device error: {str(e)}")
#         return jsonify({'message': 'Internal server error'}), 500

# def get_default_ports(device_type):
#     """Get default ports for a device type"""
#     port_configs = {
#         'router': [
#             {'name': 'GigabitEthernet0/0', 'type': 'ethernet', 'speed': '1000'},
#             {'name': 'GigabitEthernet0/1', 'type': 'ethernet', 'speed': '1000'},
#             {'name': 'Serial0/0/0', 'type': 'serial'},
#             {'name': 'Serial0/0/1', 'type': 'serial'}
#         ],
#         'switch': [
#             {'name': f'FastEthernet0/{i}', 'type': 'ethernet', 'speed': '100'}
#             for i in range(1, 25)
#         ] + [
#             {'name': 'GigabitEthernet0/1', 'type': 'ethernet', 'speed': '1000'},
#             {'name': 'GigabitEthernet0/2', 'type': 'ethernet', 'speed': '1000'}
#         ],
#         'server': [
#             {'name': 'eth0', 'type': 'ethernet', 'speed': '1000'},
#             {'name': 'eth1', 'type': 'ethernet', 'speed': '1000'}
#         ],
#         'wireless': [
#             {'name': 'radio0', 'type': 'wireless'},
#             {'name': 'ethernet0', 'type': 'ethernet', 'speed': '1000'}
#         ],
#         'firewall': [
#             {'name': 'inside', 'type': 'ethernet', 'speed': '1000'},
#             {'name': 'outside', 'type': 'ethernet', 'speed': '1000'},
#             {'name': 'dmz', 'type': 'ethernet', 'speed': '1000'}
#         ]
#     }
    
#     return port_configs.get(device_type, [
#         {'name': 'port0', 'type': 'ethernet', 'speed': '1000'}
#     ])

# @devices_bp.route('/<int:id>', methods=['PUT'])
# @jwt_required()
# def update_device(id):
#     try:
#         device = Device.query.get_or_404(id)
#         data = request.get_json()
        
#         if not data:
#             return jsonify({'message': 'No data provided'}), 400
        
#         # Update allowed fields
#         updateable_fields = ['name', 'device_type', 'ip_address', 'username', 'password', 
#                            'ssh_port', 'snmp_community', 'snmp_port', 'location', 'description', 'status']
        
#         for field in updateable_fields:
#             if field in data:
#                 if field == 'name' and data[field] != device.name:
#                     # Check name uniqueness
#                     if Device.query.filter(Device.name == data[field], Device.id != id).first():
#                         return jsonify({'message': 'Device with this name already exists'}), 409
                
#                 if field == 'ip_address' and data[field] != device.ip_address:
#                     # Check IP uniqueness
#                     if Device.query.filter(Device.ip_address == data[field], Device.id != id).first():
#                         return jsonify({'message': 'Device with this IP address already exists'}), 409
                
#                 setattr(device, field, data[field])
        
#         device.updated_at = datetime.utcnow()
#         db.session.commit()
        
#         return jsonify(device.to_dict()), 200
        
#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.error(f"Update device error: {str(e)}")
#         return jsonify({'message': 'Internal server error'}), 500

# @devices_bp.route('/<int:id>', methods=['DELETE'])
# @jwt_required()
# def delete_device(id):
#     try:
#         current_user_id = get_jwt_identity()
#         user = User.query.get(current_user_id)
        
#         if not user or user.role != 'admin':
#             return jsonify({'message': 'Admin access required'}), 403
        
#         device = Device.query.get_or_404(id)
        
#         # Check if device has active connections
#         active_connections = Port.query.filter_by(device_id=id).filter(Port.connected_to_port_id.isnot(None)).count()
#         if active_connections > 0:
#             return jsonify({'message': 'Cannot delete device with active port connections'}), 409
        
#         db.session.delete(device)
#         db.session.commit()
        
#         return jsonify({'message': 'Device deleted successfully'}), 200
        
#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.error(f"Delete device error: {str(e)}")
#         return jsonify({'message': 'Internal server error'}), 500

# @devices_bp.route('/<int:device_id>/ports', methods=['GET'])
# @jwt_required()
# def get_device_ports(device_id):
#     try:
#         device = Device.query.get_or_404(device_id)
#         return jsonify([port.to_dict() for port in device.ports]), 200
        
#     except Exception as e:
#         current_app.logger.error(f"Get device ports error: {str(e)}")
#         return jsonify({'message': 'Internal server error'}), 500

# @devices_bp.route('/<int:device_id>/ports', methods=['POST'])
# @jwt_required()
# def create_port(device_id):
#     try:
#         device = Device.query.get_or_404(device_id)
#         data = request.get_json()
        
#         if not data:
#             return jsonify({'message': 'No data provided'}), 400
        
#         required_fields = ['name', 'port_type']
#         for field in required_fields:
#             if not data.get(field):
#                 return jsonify({'message': f'{field} is required'}), 400
        
#         # Check if port name already exists on this device
#         if Port.query.filter_by(device_id=device_id, name=data['name']).first():
#             return jsonify({'message': 'Port with this name already exists on this device'}), 409
        
#         port = Port(
#             device_id=device_id,
#             name=data['name'],
#             port_type=data['port_type'],
#             speed=data.get('speed'),
#             duplex=data.get('duplex'),
#             mtu=data.get('mtu', 1500),
#             description=data.get('description'),
#             admin_status=data.get('admin_status', 'up'),
#             status='down'
#         )
        
#         db.session.add(port)
#         db.session.commit()
        
#         return jsonify(port.to_dict()), 201
        
#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.error(f"Create port error: {str(e)}")
#         return jsonify({'message': 'Internal server error'}), 500

# @devices_bp.route('/ports/<int:port_id>/connect', methods=['POST'])
# @jwt_required()
# def connect_ports(port_id):
#     try:
#         data = request.get_json()
#         target_port_id = data.get('target_port_id')
        
#         if not target_port_id:
#             return jsonify({'message': 'target_port_id is required'}), 400
        
#         port = Port.query.get_or_404(port_id)
#         target_port = Port.query.get_or_404(target_port_id)
        
#         # Check if ports are already connected
#         if port.connected_to_port_id or target_port.connected_to_port_id:
#             return jsonify({'message': 'One or both ports are already connected'}), 409
        
#         # Check if trying to connect port to itself
#         if port_id == target_port_id:
#             return jsonify({'message': 'Cannot connect port to itself'}), 400
        
#         # Check if both ports belong to the same device
#         if port.device_id == target_port.device_id:
#             return jsonify({'message': 'Cannot connect ports on the same device'}), 400
        
#         # Create bidirectional connection
#         port.connected_to_port_id = target_port_id
#         target_port.connected_to_port_id = port_id
        
#         # Update port status
#         port.status = 'up'
#         target_port.status = 'up'
        
#         db.session.commit()
        
#         return jsonify({'message': 'Ports connected successfully'}), 200
        
#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.error(f"Connect ports error: {str(e)}")
#         return jsonify({'message': 'Internal server error'}), 500

# @devices_bp.route('/ports/<int:port_id>/disconnect', methods=['POST'])
# @jwt_required()
# def disconnect_ports(port_id):
#     try:
#         port = Port.query.get_or_404(port_id)
        
#         if not port.connected_to_port_id:
#             return jsonify({'message': 'Port is not connected'}), 400
        
#         # Get the connected port
#         target_port = Port.query.get(port.connected_to_port_id)
        
#         # Remove bidirectional connection
#         port.connected_to_port_id = None
#         port.status = 'down'
        
#         if target_port:
#             target_port.connected_to_port_id = None
#             target_port.status = 'down'
        
#         db.session.commit()
        
#         return jsonify({'message': 'Port disconnected successfully'}), 200
        
#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.error(f"Disconnect ports error: {str(e)}")
#         return jsonify({'message': 'Internal server error'}), 500

# @devices_bp.route('/types', methods=['GET'])
# @jwt_required()
# def get_device_types():
#     """Get available device types and their statistics"""
#     try:
#         device_types = ['router', 'switch', 'server', 'wireless', 'firewall']
        
#         stats = {}
#         for device_type in device_types:
#             count = Device.query.filter_by(device_type=device_type).count()
#             active_count = Device.query.filter_by(device_type=device_type, status='active').count()
#             stats[device_type] = {
#                 'total': count,
#                 'active': active_count,
#                 'inactive': count - active_count
#             }
        
#         return jsonify({
#             'device_types': device_types,
#             'statistics': stats
#         }), 200
        
#     except Exception as e:
#         current_app.logger.error(f"Get device types error: {str(e)}")
#         return jsonify({'message': 'Internal server error'}), 500




# backend/app/devices/routes.py
# from flask import Blueprint,request, jsonify, current_app
# from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
# from app import db
# # from app.devices import bp
# from app.models import Device, Port
# from app.auth.decorators import role_required, operator_required
# from app.devices.utils import validate_ip_address, ping_device, get_device_info
# from datetime import datetime
# import ipaddress

# devices_bp = Blueprint('devices', __name__)

# # @bp.route('', methods=['GET'])
# @devices_bp.route('/', methods=['GET'])
# @jwt_required()
# def get_devices():
#     """Get all devices with filtering and pagination"""
#     try:
#         # Query parameters
#         page = request.args.get('page', 1, type=int)
#         per_page = min(request.args.get('per_page', 20, type=int), 100)
#         device_type = request.args.get('type')
#         status = request.args.get('status')
#         search = request.args.get('search', '').strip()
        
#         # Build query
#         query = Device.query
        
#         # Apply filters
#         if device_type:
#             query = query.filter(Device.device_type == device_type)
        
#         if status:
#             query = query.filter(Device.status == status)
        
#         if search:
#             search_pattern = f'%{search}%'
#             query = query.filter(
#                 db.or_(
#                     Device.name.ilike(search_pattern),
#                     Device.ip_address.ilike(search_pattern),
#                     Device.description.ilike(search_pattern)
#                 )
#             )
        
#         # Order by name
#         query = query.order_by(Device.name)
        
#         # Paginate
#         devices = query.paginate(
#             page=page,
#             per_page=per_page,
#             error_out=False
#         )
        
#         return jsonify({
#             'devices': [device.to_dict() for device in devices.items],
#             'total': devices.total,
#             'pages': devices.pages,
#             'current_page': page,
#             'per_page': per_page,
#             'has_next': devices.has_next,
#             'has_prev': devices.has_prev
#         }), 200
        
#     except Exception as e:
#         current_app.logger.error(f"Get devices error: {str(e)}")
#         return jsonify({'error': 'Failed to retrieve devices'}), 500

# # @bp.route('/<int:device_id>', methods=['GET'])
# @devices_bp.route('/<int:device_id>', methods=['GET'])
# @jwt_required()
# def get_device(device_id):
#     """Get single device by ID"""
#     try:
#         device = Device.query.get_or_404(device_id)
        
#         # Include credentials for operators and admins
#         claims = get_jwt()
#         include_credentials = claims.get('role') in ['admin', 'operator']
        
#         return jsonify(device.to_dict(include_credentials=include_credentials)), 200
        
#     except Exception as e:
#         current_app.logger.error(f"Get device error: {str(e)}")
#         return jsonify({'error': 'Device not found'}), 404

# # @bp.route('', methods=['POST'])
# @devices_bp.route('/', methods=['POST'])
# @operator_required
# def create_device():
#     """Create a new device"""
#     try:
#         data = request.get_json()
#         if not data:
#             return jsonify({'error': 'Request must be JSON'}), 400
        
#         # Validate required fields
#         required_fields = ['name', 'device_type', 'ip_address']
#         errors = []
        
#         for field in required_fields:
#             if not data.get(field):
#                 errors.append(f'{field} is required')
        
#         # Validate IP address
#         ip_address = data.get('ip_address', '').strip()
#         if ip_address and not validate_ip_address(ip_address):
#             errors.append('Invalid IP address format')
        
#         # Validate device type
#         valid_types = ['router', 'switch', 'server', 'wireless', 'firewall']
#         if data.get('device_type') not in valid_types:
#             errors.append(f'Device type must be one of: {", ".join(valid_types)}')
        
#         # Check for duplicate IP
#         if ip_address:
#             existing_device = Device.query.filter_by(ip_address=ip_address).first()
#             if existing_device:
#                 errors.append('IP address already exists')
        
#         # Check for duplicate name
#         name = data.get('name', '').strip()
#         if name:
#             existing_device = Device.query.filter_by(name=name).first()
#             if existing_device:
#                 errors.append('Device name already exists')
        
#         if errors:
#             return jsonify({'error': 'Validation failed', 'details': errors}), 400
        
#         # Create device
#         device = Device(
#             name=name,
#             device_type=data['device_type'],
#             ip_address=ip_address,
#             username=data.get('username', '').strip(),
#             password=data.get('password', ''),  # Should be encrypted in production
#             ssh_port=data.get('ssh_port', 22),
#             snmp_community=data.get('snmp_community', 'public'),
#             snmp_version=data.get('snmp_version', '2c'),
#             location=data.get('location', '').strip(),
#             description=data.get('description', '').strip()
#         )
        
#         db.session.add(device)
#         db.session.flush()  # Get the device ID
        
#         # Create default ports based on device type
#         create_default_ports(device)
        
#         db.session.commit()
        
#         current_app.logger.info(f"Device created: {device.name} ({device.ip_address})")
        
#         return jsonify({
#             'message': 'Device created successfully',
#             'device': device.to_dict()
#         }), 201
        
#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.error(f"Create device error: {str(e)}")
#         return jsonify({'error': 'Failed to create device'}), 500

# # @bp.route('/<int:device_id>', methods=['PUT'])
# @devices_bp.route('/<int:device_id>', methods=['PUT'])
# @operator_required
# def update_device(device_id):
#     """Update device"""
#     try:
#         device = Device.query.get_or_404(device_id)
        
#         data = request.get_json()
#         if not data:
#             return jsonify({'error': 'Request must be JSON'}), 400
        
#         errors = []
        
#         # Validate IP address if provided
#         if 'ip_address' in data:
#             ip_address = data['ip_address'].strip()
#             if not validate_ip_address(ip_address):
#                 errors.append('Invalid IP address format')
#             else:
#                 # Check for duplicate IP (excluding current device)
#                 existing_device = Device.query.filter(
#                     Device.ip_address == ip_address,
#                     Device.id != device_id
#                 ).first()
#                 if existing_device:
#                     errors.append('IP address already exists')
        
#         # Validate device type if provided
#         if 'device_type' in data:
#             valid_types = ['router', 'switch', 'server', 'wireless', 'firewall']
#             if data['device_type'] not in valid_types:
#                 errors.append(f'Device type must be one of: {", ".join(valid_types)}')
        
#         # Check for duplicate name if provided
#         if 'name' in data:
#             name = data['name'].strip()
#             if name:
#                 existing_device = Device.query.filter(
#                     Device.name == name,
#                     Device.id != device_id
#                 ).first()
#                 if existing_device:
#                     errors.append('Device name already exists')
        
#         if errors:
#             return jsonify({'error': 'Validation failed', 'details': errors}), 400
        
#         # Update fields
#         updatable_fields = [
#             'name', 'device_type', 'ip_address', 'username', 'password',
#             'ssh_port', 'snmp_community', 'snmp_version', 'location', 'description'
#         ]
        
#         for field in updatable_fields:
#             if field in data:
#                 if field in ['name', 'username', 'location', 'description']:
#                     setattr(device, field, data[field].strip())
#                 else:
#                     setattr(device, field, data[field])
        
#         device.updated_at = datetime.utcnow()
#         db.session.commit()
        
#         current_app.logger.info(f"Device updated: {device.name} ({device.ip_address})")
        
#         return jsonify({
#             'message': 'Device updated successfully',
#             'device': device.to_dict()
#         }), 200
        
#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.error(f"Update device error: {str(e)}")
#         return jsonify({'error': 'Failed to update device'}), 500

# # @bp.route('/<int:device_id>', methods=['DELETE'])
# @devices_bp.route('/<int:device_id>', methods=['DELETE'])
# @operator_required
# def delete_device(device_id):
#     """Delete device"""
#     try:
#         device = Device.query.get_or_404(device_id)
#         device_name = device.name
        
#         db.session.delete(device)
#         db.session.commit()
        
#         current_app.logger.info(f"Device deleted: {device_name}")
        
#         return jsonify({'message': 'Device deleted successfully'}), 200
        
#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.error(f"Delete device error: {str(e)}")
#         return jsonify({'error': 'Failed to delete device'}), 500

# # @bp.route('/<int:device_id>/test-connection', methods=['POST'])
# @devices_bp.route('/<int:device_id>/test-connection', methods=['POST'])
# @operator_required
# def test_device_connection(device_id):
#     """Test connection to device"""
#     try:
#         device = Device.query.get_or_404(device_id)
        
#         # Ping test
#         ping_result = ping_device(device.ip_address)
        
#         result = {
#             'device_id': device_id,
#             'device_name': device.name,
#             'ip_address': device.ip_address,
#             'ping_success': ping_result['success'],
#             'ping_time': ping_result.get('time'),
#             'timestamp': datetime.utcnow().isoformat()
#         }
        
#         # Update device status based on ping result
#         if ping_result['success']:
#             device.status = 'active'
#             device.last_seen = datetime.utcnow()
#         else:
#             device.status = 'inactive'
        
#         db.session.commit()
        
#         return jsonify(result), 200
        
#     except Exception as e:
#         current_app.logger.error(f"Test connection error: {str(e)}")
#         return jsonify({'error': 'Failed to test connection'}), 500

# # @bp.route('/<int:device_id>/ports', methods=['GET'])
# @devices_bp.route('/<int:device_id>/ports', methods=['GET'])
# @jwt_required()
# def get_device_ports(device_id):
#     """Get device ports"""
#     try:
#         device = Device.query.get_or_404(device_id)
        
#         return jsonify({
#             'device_id': device_id,
#             'device_name': device.name,
#             'ports': [port.to_dict() for port in device.ports]
#         }), 200
        
#     except Exception as e:
#         current_app.logger.error(f"Get device ports error: {str(e)}")
#         return jsonify({'error': 'Failed to get device ports'}), 500

# # @bp.route('/<int:device_id>/ports', methods=['POST'])
# @devices_bp.route('/<int:device_id>/ports', methods=['POST'])
# @operator_required
# def create_port(device_id):
#     """Create a new port for device"""
#     try:
#         device = Device.query.get_or_404(device_id)
        
#         data = request.get_json()
#         if not data:
#             return jsonify({'error': 'Request must be JSON'}), 400
        
#         # Validate required fields
#         if not data.get('name'):
#             return jsonify({'error': 'Port name is required'}), 400
        
#         # Check for duplicate port name on this device
#         existing_port = Port.query.filter_by(
#             device_id=device_id,
#             name=data['name']
#         ).first()
#         if existing_port:
#             return jsonify({'error': 'Port name already exists on this device'}), 400
        
#         port = Port(
#             device_id=device_id,
#             name=data['name'].strip(),
#             port_type=data.get('port_type', 'ethernet'),
#             description=data.get('description', '').strip(),
#             vlan_id=data.get('vlan_id'),
#             mtu=data.get('mtu', 1500)
#         )
        
#         db.session.add(port)
#         db.session.commit()
        
#         current_app.logger.info(f"Port created: {port.name} on device {device.name}")
        
#         return jsonify({
#             'message': 'Port created successfully',
#             'port': port.to_dict()
#         }), 201
        
#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.error(f"Create port error: {str(e)}")
#         return jsonify({'error': 'Failed to create port'}), 500

# # @bp.route('/ports/<int:port_id>/connect', methods=['POST'])
# @devices_bp.route('/ports/<int:port_id>/connect', methods=['POST'])
# @operator_required
# def connect_ports(port_id):
#     """Connect two ports"""
#     try:
#         data = request.get_json()
#         if not data or 'target_port_id' not in data:
#             return jsonify({'error': 'target_port_id is required'}), 400
        
#         target_port_id = data['target_port_id']
        
#         port1 = Port.query.get_or_404(port_id)
#         port2 = Port.query.get_or_404(target_port_id)
        
#         # Validate connection
#         if port1.device_id == port2.device_id:
#             return jsonify({'error': 'Cannot connect ports on the same device'}), 400
        
#         if port1.connected_to_port_id:
#             return jsonify({'error': f'Port {port1.name} is already connected'}), 400
        
#         if port2.connected_to_port_id:
#             return jsonify({'error': f'Port {port2.name} is already connected'}), 400
        
#         # Create bidirectional connection
#         port1.connected_to_port_id = port2.id
#         port2.connected_to_port_id = port1.id
        
#         # Update status
#         port1.status = 'up'
#         port2.status = 'up'
        
#         db.session.commit()
        
#         current_app.logger.info(f"Ports connected: {port1.name} <-> {port2.name}")
        
#         return jsonify({
#             'message': 'Ports connected successfully',
#             'connection': {
#                 'port1': port1.to_dict(),
#                 'port2': port2.to_dict()
#             }
#         }), 200
        
#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.error(f"Connect ports error: {str(e)}")
#         return jsonify({'error': 'Failed to connect ports'}), 500

# # @bp.route('/ports/<int:port_id>/disconnect', methods=['POST'])
# @devices_bp.route('/ports/<int:port_id>/disconnect', methods=['POST'])
# @operator_required
# def disconnect_port(port_id):
#     """Disconnect a port"""
#     try:
#         port = Port.query.get_or_404(port_id)
        
#         if not port.connected_to_port_id:
#             return jsonify({'error': 'Port is not connected'}), 400
        
#         # Get connected port
#         connected_port = Port.query.get(port.connected_to_port_id)
        
#         # Remove bidirectional connection
#         port.connected_to_port_id = None
#         port.status = 'down'
        
#         if connected_port:
#             connected_port.connected_to_port_id = None
#             connected_port.status = 'down'
        
#         db.session.commit()
        
#         current_app.logger.info(f"Port disconnected: {port.name}")
        
#         return jsonify({
#             'message': 'Port disconnected successfully',
#             'port': port.to_dict()
#         }), 200
        
#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.error(f"Disconnect port error: {str(e)}")
#         return jsonify({'error': 'Failed to disconnect port'}), 500

# # @bp.route('/types', methods=['GET'])
# @devices_bp.route('/types', methods=['GET'])
# @jwt_required()
# def get_device_types():
#     """Get available device types"""
#     device_types = [
#         {
#             'value': 'router',
#             'label': 'Router',
#             'description': 'Network router for routing traffic between networks'
#         },
#         {
#             'value': 'switch',
#             'label': 'Switch',
#             'description': 'Network switch for connecting devices in a LAN'
#         },
#         {
#             'value': 'server',
#             'label': 'Server',
#             'description': 'Server providing network services'
#         },
#         {
#             'value': 'wireless',
#             'label': 'Wireless AP',
#             'description': 'Wireless access point for WiFi connectivity'
#         },
#         {
#             'value': 'firewall',
#             'label': 'Firewall',
#             'description': 'Security device for network protection'
#         }
#     ]
    
#     return jsonify(device_types), 200

# # @bp.route('/bulk', methods=['POST'])
# @devices_bp.route('/bulk', methods=['POST'])
# @role_required(['admin', 'operator'])
# def bulk_operations():
#     """Perform bulk operations on devices"""
#     try:
#         data = request.get_json()
#         if not data:
#             return jsonify({'error': 'Request must be JSON'}), 400
        
#         operation = data.get('operation')
#         device_ids = data.get('device_ids', [])
        
#         if not operation or not device_ids:
#             return jsonify({'error': 'Operation and device_ids are required'}), 400
        
#         if operation == 'delete':
#             devices = Device.query.filter(Device.id.in_(device_ids)).all()
#             for device in devices:
#                 db.session.delete(device)
            
#             db.session.commit()
            
#             return jsonify({
#                 'message': f'{len(devices)} devices deleted successfully',
#                 'deleted_count': len(devices)
#             }), 200
        
#         elif operation == 'update_status':
#             new_status = data.get('status')
#             if not new_status:
#                 return jsonify({'error': 'Status is required for update_status operation'}), 400
            
#             devices = Device.query.filter(Device.id.in_(device_ids)).all()
#             for device in devices:
#                 device.status = new_status
#                 device.updated_at = datetime.utcnow()
            
#             db.session.commit()
            
#             return jsonify({
#                 'message': f'{len(devices)} devices updated successfully',
#                 'updated_count': len(devices)
#             }), 200
        
#         else:
#             return jsonify({'error': 'Unknown operation'}), 400
        
#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.error(f"Bulk operations error: {str(e)}")
#         return jsonify({'error': 'Bulk operation failed'}), 500

# # Helper functions
# def create_default_ports(device):
#     """Create default ports based on device type"""
#     port_configs = {
#         'router': [
#             {'name': 'GigabitEthernet0/0', 'type': 'ethernet'},
#             {'name': 'GigabitEthernet0/1', 'type': 'ethernet'},
#             {'name': 'GigabitEthernet0/2', 'type': 'ethernet'},
#             {'name': 'GigabitEthernet0/3', 'type': 'ethernet'},
#         ],
#         'switch': [
#             {'name': f'FastEthernet0/{i}', 'type': 'ethernet'} 
#             for i in range(1, 25)  # 24 ports
#         ],
#         'server': [
#             {'name': 'eth0', 'type': 'ethernet'},
#             {'name': 'eth1', 'type': 'ethernet'},
#         ],
#         'wireless': [
#             {'name': 'wlan0', 'type': 'wireless'},
#         ],
#         'firewall': [
#             {'name': 'inside', 'type': 'ethernet'},
#             {'name': 'outside', 'type': 'ethernet'},
#             {'name': 'dmz', 'type': 'ethernet'},
#             {'name': 'management', 'type': 'ethernet'},
#         ]
#     }
    
#     ports_config = port_configs.get(device.device_type, [])
    
#     for port_config in ports_config:
#         port = Port(
#             device_id=device.id,
#             name=port_config['name'],
#             port_type=port_config['type']
#         )
#         db.session.add(port)









from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models import Device, Port

devices_bp = Blueprint('devices', __name__)

@devices_bp.route('/', methods=['GET'])
@jwt_required()
def get_devices():
    """Get all devices"""
    try:
        devices = Device.query.all()
        return jsonify([device.to_dict() for device in devices])
    except Exception as e:
        return jsonify(message=f"Error fetching devices: {str(e)}"), 500

@devices_bp.route('/<int:device_id>', methods=['GET'])
@jwt_required()
def get_device(device_id):
    """Get specific device"""
    try:
        device = Device.query.get_or_404(device_id)
        return jsonify(device.to_dict())
    except Exception as e:
        return jsonify(message=f"Error fetching device: {str(e)}"), 500

@devices_bp.route('/', methods=['POST'])
@jwt_required()
def create_device():
    """Create new device"""
    try:
        data = request.get_json() or {}
        
        required_fields = ['name', 'device_type', 'ip_address']
        for field in required_fields:
            if not data.get(field):
                return jsonify(message=f"Field '{field}' is required"), 400
        
        device = Device(
            name=data['name'],
            device_type=data['device_type'],
            ip_address=data['ip_address'],
            username=data.get('username', ''),
            password=data.get('password', ''),
            ssh_port=data.get('ssh_port', 22),
            description=data.get('description', '')
        )
        
        db.session.add(device)
        db.session.commit()
        
        return jsonify(device.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify(message=f"Error creating device: {str(e)}"), 500

@devices_bp.route('/<int:device_id>', methods=['PUT'])
@jwt_required()
def update_device(device_id):
    """Update device"""
    try:
        device = Device.query.get_or_404(device_id)
        data = request.get_json() or {}
        
        # Update fields
        for field in ['name', 'device_type', 'ip_address', 'username', 'password', 'ssh_port', 'status', 'description']:
            if field in data:
                setattr(device, field, data[field])
        
        db.session.commit()
        return jsonify(device.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify(message=f"Error updating device: {str(e)}"), 500

@devices_bp.route('/<int:device_id>', methods=['DELETE'])
@jwt_required()
def delete_device(device_id):
    """Delete device"""
    try:
        device = Device.query.get_or_404(device_id)
        db.session.delete(device)
        db.session.commit()
        
        return jsonify(message="Device deleted successfully")
        
    except Exception as e:
        db.session.rollback()
        return jsonify(message=f"Error deleting device: {str(e)}"), 500