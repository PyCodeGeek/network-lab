# # backend/app/inventory/models.py
# from app import db
# from datetime import datetime

# class Inventory(db.Model):
#     __tablename__ = 'inventory'
    
#     id = db.Column(db.Integer, primary_key=True)
#     device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
#     hardware_model = db.Column(db.String(100))
#     serial_number = db.Column(db.String(100), unique=True)
#     os_version = db.Column(db.String(50))
#     last_inventory_update = db.Column(db.DateTime, default=datetime.utcnow)
    
#     # Relationships
#     device = db.relationship('Device', backref='inventory_items', lazy=True)
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'device_id': self.device_id,
#             'device_name': self.device.name if self.device else None,
#             'hardware_model': self.hardware_model,
#             'serial_number': self.serial_number,
#             'os_version': self.os_version,
#             'last_inventory_update': self.last_inventory_update.isoformat()
#         }

# class InterfaceInventory(db.Model):
#     __tablename__ = 'interface_inventory'
    
#     id = db.Column(db.Integer, primary_key=True)
#     inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
#     port_id = db.Column(db.Integer, db.ForeignKey('ports.id'), nullable=False)
#     mac_address = db.Column(db.String(17))
#     speed = db.Column(db.String(20))
#     duplex = db.Column(db.String(10))
#     mtu = db.Column(db.Integer)
    
#     # Relationships
#     inventory = db.relationship('Inventory', backref='interfaces', lazy=True)
#     port = db.relationship('Port', backref='inventory_details', lazy=True)
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'inventory_id': self.inventory_id,
#             'port_id': self.port_id,
#             'port_name': self.port.name if self.port else None,
#             'mac_address': self.mac_address,
#             'speed': self.speed,
#             'duplex': self.duplex,
#             'mtu': self.mtu
#         }

# # backend/app/inventory/routes.py
# from flask import Blueprint, request, jsonify
# from flask_jwt_extended import jwt_required
# from app import db
# from app.inventory.models import Inventory, InterfaceInventory
# from app.devices.models import Device, Port
# from datetime import datetime

# inventory_bp = Blueprint('inventory', __name__)

# @inventory_bp.route('/', methods=['GET'])
# @jwt_required()
# def get_inventory():
#     inventory_items = Inventory.query.all()
#     return jsonify([item.to_dict() for item in inventory_items]), 200

# @inventory_bp.route('/<int:device_id>', methods=['GET'])
# @jwt_required()
# def get_device_inventory(device_id):
#     device = Device.query.get_or_404(device_id)
#     inventory = Inventory.query.filter_by(device_id=device_id).first()
    
#     if not inventory:
#         return jsonify(message="No inventory data available for this device"), 404
    
#     inventory_data = inventory.to_dict()
#     interfaces = [interface.to_dict() for interface in inventory.interfaces]
#     inventory_data['interfaces'] = interfaces
    
#     return jsonify(inventory_data), 200

# @inventory_bp.route('/<int:device_id>', methods=['POST'])
# @jwt_required()
# def update_device_inventory(device_id):
#     device = Device.query.get_or_404(device_id)
#     data = request.get_json()
    
#     # Check if inventory exists
#     inventory = Inventory.query.filter_by(device_id=device_id).first()
#     if not inventory:
#         # Create new inventory
#         inventory = Inventory(
#             device_id=device_id,
#             hardware_model=data.get('hardware_model'),
#             serial_number=data.get('serial_number'),
#             os_version=data.get('os_version'),
#             last_inventory_update=datetime.utcnow()
#         )
#         db.session.add(inventory)
#     else:
#         # Update existing inventory
#         inventory.hardware_model = data.get('hardware_model', inventory.hardware_model)
#         inventory.serial_number = data.get('serial_number', inventory.serial_number)
#         inventory.os_version = data.get('os_version', inventory.os_version)
#         inventory.last_inventory_update = datetime.utcnow()
    
#     db.session.commit()
    
#     # Process interface inventory data if provided
#     if 'interfaces' in data:
#         for interface_data in data['interfaces']:
#             port_name = interface_data.get('port_name')
#             port = Port.query.filter_by(device_id=device_id, name=port_name).first()
            
#             if port:
#                 # Check if interface inventory exists
#                 interface_inv = InterfaceInventory.query.filter_by(
#                     inventory_id=inventory.id, 
#                     port_id=port.id
#                 ).first()
                
#                 if not interface_inv:
#                     # Create new interface inventory
#                     interface_inv = InterfaceInventory(
#                         inventory_id=inventory.id,
#                         port_id=port.id,
#                         mac_address=interface_data.get('mac_address'),
#                         speed=interface_data.get('speed'),
#                         duplex=interface_data.get('duplex'),
#                         mtu=interface_data.get('mtu')
#                     )
#                     db.session.add(interface_inv)
#                 else:
#                     # Update existing interface inventory
#                     interface_inv.mac_address = interface_data.get('mac_address', interface_inv.mac_address)
#                     interface_inv.speed = interface_data.get('speed', interface_inv.speed)
#                     interface_inv.duplex = interface_data.get('duplex', interface_inv.duplex)
#                     interface_inv.mtu = interface_data.get('mtu', interface_inv.mtu)
    
#     db.session.commit()
    
#     return jsonify(message="Inventory updated successfully"), 200

# @inventory_bp.route('/scan/<int:device_id>', methods=['POST'])
# @jwt_required()
# def scan_device_inventory(device_id):
#     from app.inventory.scanner import scan_device
    
#     device = Device.query.get_or_404(device_id)
    
#     # In a real implementation, this would connect to the device
#     # For now, simulate inventory scanning
#     inventory_data = scan_device(device)
    
#     return jsonify(inventory_data), 200

# # backend/app/inventory/scanner.py
# import random
# from datetime import datetime

# def scan_device(device):
#     """
#     Simulates scanning a network device to get inventory information.
#     In a real implementation, this would connect to the device using SSH/NETCONF/etc.
#     """
#     # Simulated data based on device type
#     if device.device_type == 'router':
#         hardware_model = 'CISCO2901/K9'
#         os_version = 'IOS XE 16.9.3'
#     elif device.device_type == 'switch':
#         hardware_model = 'CISCO3850-48T'
#         os_version = 'IOS 15.2'
#     else:
#         hardware_model = 'Generic Device'
#         os_version = 'Unknown OS'
    
#     # Generate a random serial number
#     serial_number = f"FTX{random.randint(1000000, 9999999)}"
    
#     # Gather interface data
#     interfaces = []
#     for port in device.ports:
#         mac_octets = [random.randint(0, 255) for _ in range(6)]
#         mac_address = ':'.join([f"{octet:02x}" for octet in mac_octets])
        
#         interface_data = {
#             'port_name': port.name,
#             'mac_address': mac_address,
#             'speed': '1000MB/s',
#             'duplex': 'full',
#             'mtu': 1500
#         }
#         interfaces.append(interface_data)
    
#     # Compose response
#     inventory_data = {
#         'hardware_model': hardware_model,
#         'serial_number': serial_number,
#         'os_version': os_version,
#         'interfaces': interfaces,
#         'timestamp': datetime.utcnow().isoformat()
#     }
    
#     return inventory_data

# # backend/app/provisioning/models.py
# from app import db
# from datetime import datetime
# import json

# class ConfigTemplate(db.Model):
#     __tablename__ = 'config_templates'
    
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     device_type = db.Column(db.String(50), nullable=False)
#     content = db.Column(db.Text, nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'name': self.name,
#             'device_type': self.device_type,
#             'content': self.content,
#             'created_at': self.created_at.isoformat(),
#             'updated_at': self.updated_at.isoformat()
#         }

# class ProvisioningTask(db.Model):
#     __tablename__ = 'provisioning_tasks'
    
#     id = db.Column(db.Integer, primary_key=True)
#     device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
#     template_id = db.Column(db.Integer, db.ForeignKey('config_templates.id'), nullable=True)
#     status = db.Column(db.String(20), default='pending') # pending, running, completed, failed
#     config_data = db.Column(db.Text) # JSON data for template variables
#     result = db.Column(db.Text)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     completed_at = db.Column(db.DateTime)
    
#     # Relationships
#     device = db.relationship('Device', backref='provisioning_tasks', lazy=True)
#     template = db.relationship('ConfigTemplate', backref='tasks', lazy=True)
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'device_id': self.device_id,
#             'device_name': self.device.name if self.device else None,
#             'template_id': self.template_id,
#             'template_name': self.template.name if self.template else None,
#             'status': self.status,
#             'config_data': json.loads(self.config_data) if self.config_data else None,
#             'result': self.result,
#             'created_at': self.created_at.isoformat(),
#             'completed_at': self.completed_at.isoformat() if self.completed_at else None
#         }

# # backend/app/provisioning/routes.py
# from flask import Blueprint, request, jsonify
# from flask_jwt_extended import jwt_required
# from app import db
# from app.provisioning.models import ConfigTemplate, ProvisioningTask
# from app.devices.models import Device
# from app.provisioning.provisioner import provision_device
# from datetime import datetime
# import json

# provisioning_bp = Blueprint('provisioning', __name__)

# @provisioning_bp.route('/templates', methods=['GET'])
# @jwt_required()
# def get_templates():
#     templates = ConfigTemplate.query.all()
#     return jsonify([template.to_dict() for template in templates]), 200

# @provisioning_bp.route('/templates/<int:id>', methods=['GET'])
# @jwt_required()
# def get_template(id):
#     template = ConfigTemplate.query.get_or_404(id)
#     return jsonify(template.to_dict()), 200

# @provisioning_bp.route('/templates', methods=['POST'])
# @jwt_required()
# def create_template():
#     data = request.get_json()
    
#     template = ConfigTemplate(
#         name=data['name'],
#         device_type=data['device_type'],
#         content=data['content']
#     )
    
#     db.session.add(template)
#     db.session.commit()
    
#     return jsonify(template.to_dict()), 201

# @provisioning_bp.route('/templates/<int:id>', methods=['PUT'])
# @jwt_required()
# def update_template(id):
#     template = ConfigTemplate.query.get_or_404(id)
#     data = request.get_json()
    
#     template.name = data.get('name', template.name)
#     template.device_type = data.get('device_type', template.device_type)
#     template.content = data.get('content', template.content)
    
#     db.session.commit()
    
#     return jsonify(template.to_dict()), 200

# @provisioning_bp.route('/templates/<int:id>', methods=['DELETE'])
# @jwt_required()
# def delete_template(id):
#     template = ConfigTemplate.query.get_or_404(id)
#     db.session.delete(template)
#     db.session.commit()
    
#     return jsonify(message="Template deleted"), 200

# @provisioning_bp.route('/tasks', methods=['GET'])
# @jwt_required()
# def get_tasks():
#     tasks = ProvisioningTask.query.all()
#     return jsonify([task.to_dict() for task in tasks]), 200

# @provisioning_bp.route('/tasks/<int:id>', methods=['GET'])
# @jwt_required()
# def get_task(id):
#     task = ProvisioningTask.query.get_or_404(id)
#     return jsonify(task.to_dict()), 200

# @provisioning_bp.route('/tasks', methods=['POST'])
# @jwt_required()
# def create_task():
#     data = request.get_json()
#     device_id = data['device_id']
#     template_id = data.get('template_id')
#     config_data = data.get('config_data', {})
    
#     device = Device.query.get_or_404(device_id)
    
#     if template_id:
#         template = ConfigTemplate.query.get_or_404(template_id)
    
#     task = ProvisioningTask(
#         device_id=device_id,
#         template_id=template_id,
#         config_data=json.dumps(config_data),
#         status='pending'
#     )
    
#     db.session.add(task)
#     db.session.commit()
    
#     # In a real-world application, this would be handled by a background task queue
#     # For simplicity, we'll execute it directly
#     provision_result = provision_device(task)
    
#     task.status = 'completed' if provision_result['success'] else 'failed'
#     task.result = json.dumps(provision_result)
#     task.completed_at = datetime.utcnow()
    
#     db.session.commit()
    
#     return jsonify(task.to_dict()), 201

# @provisioning_bp.route('/execute/<int:task_id>', methods=['POST'])
# @jwt_required()
# def execute_task(task_id):
#     task = ProvisioningTask.query.get_or_404(task_id)
    
#     if task.status not in ['pending', 'failed']:
#         return jsonify(message=f"Task is already {task.status}"), 400
    
#     task.status = 'running'
#     db.session.commit()
    
#     # Execute provisioning
#     provision_result = provision_device(task)
    
#     task.status = 'completed' if provision_result['success'] else 'failed'
#     task.result = json.dumps(provision_result)
#     task.completed_at = datetime.utcnow()
    
#     db.session.commit()
    
#     return jsonify(task.to_dict()), 200

# # backend/app/provisioning/provisioner.py
# import json
# import time
# from jinja2 import Template
# import random

# def provision_device(task):
#     """
#     Simulates provisioning a network device based on a template and configuration data.
#     In a real implementation, this would connect to the device using SSH/NETCONF/etc.
#     """
#     device = task.device
#     config_data = json.loads(task.config_data) if task.config_data else {}
    
#     # If using a template, render it with the provided data
#     if task.template:
#         template_content = task.template.content
#         try:
#             template = Template(template_content)
#             rendered_config = template.render(**config_data)
#         except Exception as e:
#             return {
#                 'success': False,
#                 'message': f"Failed to render template: {str(e)}",
#                 'device_id': device.id,
#                 'device_name': device.name
#             }
#     else:
#         # Direct configuration commands (if not using a template)
#         rendered_config = config_data.get('commands', '')
    
#     # Simulate connection and configuration of the device
#     try:
#         # Simulate a connection delay
#         time.sleep(1)
        
#         # Simulate success or failure (90% success rate)
#         if random.random() < 0.9:
#             result = {
#                 'success': True,
#                 'message': f"Device {device.name} successfully provisioned",
#                 'device_id': device.id,
#                 'device_name': device.name,
#                 'configuration': rendered_config,
#                 'output': simulate_device_output(device.device_type)
#             }
            
#             # Update device status
#             device.status = 'active'
#         else:
#             result = {
#                 'success': False,
#                 'message': f"Failed to provision device {device.name}",
#                 'device_id': device.id,
#                 'device_name': device.name,
#                 'error': "Connection timeout"
#             }
#     except Exception as e:
#         result = {
#             'success': False,
#             'message': f"Exception occurred: {str(e)}",
#             'device_id': device.id,
#             'device_name': device.name
#         }
    
#     return result

# def simulate_device_output(device_type):
#     """Generates simulated output from a device after configuration."""
#     if device_type == 'router':
#         return """
#         Router#show ip interface brief
#         Interface                  IP-Address      OK? Method Status                Protocol
#         GigabitEthernet0/0         192.168.1.1     YES NVRAM  up                    up      
#         GigabitEthernet0/1         10.0.0.1        YES NVRAM  up                    up      
#         GigabitEthernet0/2         unassigned      YES NVRAM  administratively down down    
#         GigabitEthernet0/3         unassigned      YES NVRAM  administratively down down    
#         Router#show version
#         Cisco IOS Software, 2900 Software (C2900-UNIVERSALK9-M), Version 15.7(3)M8
#         """
#     elif device_type == 'switch':
#         return """
#         Switch#show interfaces status
#         Port      Name               Status       Vlan       Duplex  Speed Type
#         Gi1/0/1                      connected    1          a-full  a-100 10/100/1000BaseTX
#         Gi1/0/2                      connected    1          a-full a-1000 10/100/1000BaseTX
#         Gi1/0/3                      notconnect   1            auto   auto 10/100/1000BaseTX
#         """
#     else:
#         return "Configuration applied successfully."



# backend/app/inventory/models.py
from app import db
from datetime import datetime
import json

class Inventory(db.Model):
    __tablename__ = 'inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    hardware_model = db.Column(db.String(100))
    serial_number = db.Column(db.String(100), unique=True)
    os_version = db.Column(db.String(50))
    firmware_version = db.Column(db.String(50))
    cpu_info = db.Column(db.Text)  # JSON string
    memory_info = db.Column(db.Text)  # JSON string
    storage_info = db.Column(db.Text)  # JSON string
    last_inventory_update = db.Column(db.DateTime, default=datetime.utcnow)
    scan_status = db.Column(db.String(20), default='pending')  # pending, scanning, completed, failed
    
    # Relationships
    interfaces = db.relationship('InterfaceInventory', backref='inventory', lazy=True, cascade="all, delete-orphan")
    modules = db.relationship('ModuleInventory', backref='inventory', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'device_name': self.device.name if self.device else None,
            'hardware_model': self.hardware_model,
            'serial_number': self.serial_number,
            'os_version': self.os_version,
            'firmware_version': self.firmware_version,
            'cpu_info': json.loads(self.cpu_info) if self.cpu_info else None,
            'memory_info': json.loads(self.memory_info) if self.memory_info else None,
            'storage_info': json.loads(self.storage_info) if self.storage_info else None,
            'last_inventory_update': self.last_inventory_update.isoformat(),
            'scan_status': self.scan_status,
            'interfaces': [interface.to_dict() for interface in self.interfaces],
            'modules': [module.to_dict() for module in self.modules]
        }

class InterfaceInventory(db.Model):
    __tablename__ = 'interface_inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    port_id = db.Column(db.Integer, db.ForeignKey('ports.id'), nullable=True)
    interface_name = db.Column(db.String(50), nullable=False)
    mac_address = db.Column(db.String(17))
    speed = db.Column(db.String(20))
    duplex = db.Column(db.String(10))
    mtu = db.Column(db.Integer)
    ip_address = db.Column(db.String(15))
    subnet_mask = db.Column(db.String(15))
    status = db.Column(db.String(20))
    description = db.Column(db.String(255))
    
    # Relationships
    port = db.relationship('Port', backref='inventory_details', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'inventory_id': self.inventory_id,
            'port_id': self.port_id,
            'interface_name': self.interface_name,
            'port_name': self.port.name if self.port else None,
            'mac_address': self.mac_address,
            'speed': self.speed,
            'duplex': self.duplex,
            'mtu': self.mtu,
            'ip_address': self.ip_address,
            'subnet_mask': self.subnet_mask,
            'status': self.status,
            'description': self.description
        }

class ModuleInventory(db.Model):
    __tablename__ = 'module_inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    slot_number = db.Column(db.Integer)
    module_type = db.Column(db.String(50))
    part_number = db.Column(db.String(50))
    serial_number = db.Column(db.String(50))
    description = db.Column(db.String(255))
    status = db.Column(db.String(20))
    
    def to_dict(self):
        return {
            'id': self.id,
            'inventory_id': self.inventory_id,
            'slot_number': self.slot_number,
            'module_type': self.module_type,
            'part_number': self.part_number,
            'serial_number': self.serial_number,
            'description': self.description,
            'status': self.status
        }
