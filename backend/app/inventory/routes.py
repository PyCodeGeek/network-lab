
# backend/app/inventory/routes.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.inventory.models import Inventory, InterfaceInventory, ModuleInventory
from app.devices.models import Device, Port
from app.inventory.scanner import scan_device_inventory
from datetime import datetime
import json

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/', methods=['GET'])
@jwt_required()
def get_inventory():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        device_type = request.args.get('device_type')
        scan_status = request.args.get('scan_status')
        
        # Build query
        query = db.session.query(Inventory).join(Device)
        
        if device_type:
            query = query.filter(Device.device_type == device_type)
        
        if scan_status:
            query = query.filter(Inventory.scan_status == scan_status)
        
        # Paginate
        inventory_items = query.order_by(Inventory.last_inventory_update.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'inventory': [item.to_dict() for item in inventory_items.items],
            'total': inventory_items.total,
            'pages': inventory_items.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get inventory error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@inventory_bp.route('/<int:device_id>', methods=['GET'])
@jwt_required()
def get_device_inventory(device_id):
    try:
        device = Device.query.get_or_404(device_id)
        inventory = Inventory.query.filter_by(device_id=device_id).first()
        
        if not inventory:
            return jsonify({
                'message': 'No inventory data available for this device',
                'device': device.to_dict()
            }), 404
        
        return jsonify(inventory.to_dict()), 200
        
    except Exception as e:
        current_app.logger.error(f"Get device inventory error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@inventory_bp.route('/<int:device_id>', methods=['POST'])
@jwt_required()
def update_device_inventory(device_id):
    try:
        device = Device.query.get_or_404(device_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        # Check if inventory exists
        inventory = Inventory.query.filter_by(device_id=device_id).first()
        if not inventory:
            # Create new inventory
            inventory = Inventory(device_id=device_id)
            db.session.add(inventory)
        
        # Update inventory fields
        updateable_fields = [
            'hardware_model', 'serial_number', 'os_version', 'firmware_version',
            'cpu_info', 'memory_info', 'storage_info', 'scan_status'
        ]
        
        for field in updateable_fields:
            if field in data:
                if field in ['cpu_info', 'memory_info', 'storage_info']:
                    # Convert dict to JSON string
                    if isinstance(data[field], dict):
                        setattr(inventory, field, json.dumps(data[field]))
                    else:
                        setattr(inventory, field, data[field])
                else:
                    setattr(inventory, field, data[field])
        
        inventory.last_inventory_update = datetime.utcnow()
        db.session.flush()  # Get the inventory ID
        
        # Process interface inventory data if provided
        if 'interfaces' in data:
            # Clear existing interface inventory
            InterfaceInventory.query.filter_by(inventory_id=inventory.id).delete()
            
            for interface_data in data['interfaces']:
                # Find matching port
                port = None
                if 'port_name' in interface_data:
                    port = Port.query.filter_by(
                        device_id=device_id, 
                        name=interface_data['port_name']
                    ).first()
                
                interface_inv = InterfaceInventory(
                    inventory_id=inventory.id,
                    port_id=port.id if port else None,
                    interface_name=interface_data.get('interface_name', ''),
                    mac_address=interface_data.get('mac_address'),
                    speed=interface_data.get('speed'),
                    duplex=interface_data.get('duplex'),
                    mtu=interface_data.get('mtu'),
                    ip_address=interface_data.get('ip_address'),
                    subnet_mask=interface_data.get('subnet_mask'),
                    status=interface_data.get('status'),
                    description=interface_data.get('description')
                )
                db.session.add(interface_inv)
        
        # Process module inventory data if provided
        if 'modules' in data:
            # Clear existing module inventory
            ModuleInventory.query.filter_by(inventory_id=inventory.id).delete()
            
            for module_data in data['modules']:
                module_inv = ModuleInventory(
                    inventory_id=inventory.id,
                    slot_number=module_data.get('slot_number'),
                    module_type=module_data.get('module_type'),
                    part_number=module_data.get('part_number'),
                    serial_number=module_data.get('serial_number'),
                    description=module_data.get('description'),
                    status=module_data.get('status')
                )
                db.session.add(module_inv)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Inventory updated successfully',
            'inventory': inventory.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Update inventory error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@inventory_bp.route('/scan/<int:device_id>', methods=['POST'])
@jwt_required()
def scan_device(device_id):
    try:
        device = Device.query.get_or_404(device_id)
        
        # Update or create inventory record with scanning status
        inventory = Inventory.query.filter_by(device_id=device_id).first()
        if not inventory:
            inventory = Inventory(device_id=device_id)
            db.session.add(inventory)
        
        inventory.scan_status = 'scanning'
        inventory.last_inventory_update = datetime.utcnow()
        db.session.commit()
        
        # Perform the scan
        try:
            inventory_data = scan_device_inventory(device)
            
            # Update inventory with scanned data
            inventory.hardware_model = inventory_data.get('hardware_model')
            inventory.serial_number = inventory_data.get('serial_number')
            inventory.os_version = inventory_data.get('os_version')
            inventory.firmware_version = inventory_data.get('firmware_version')
            
            if inventory_data.get('cpu_info'):
                inventory.cpu_info = json.dumps(inventory_data['cpu_info'])
            if inventory_data.get('memory_info'):
                inventory.memory_info = json.dumps(inventory_data['memory_info'])
            if inventory_data.get('storage_info'):
                inventory.storage_info = json.dumps(inventory_data['storage_info'])
            
            inventory.scan_status = 'completed'
            
            # Clear and update interface inventory
            InterfaceInventory.query.filter_by(inventory_id=inventory.id).delete()
            for interface_data in inventory_data.get('interfaces', []):
                port = Port.query.filter_by(
                    device_id=device_id, 
                    name=interface_data.get('interface_name')
                ).first()
                
                interface_inv = InterfaceInventory(
                    inventory_id=inventory.id,
                    port_id=port.id if port else None,
                    interface_name=interface_data.get('interface_name', ''),
                    mac_address=interface_data.get('mac_address'),
                    speed=interface_data.get('speed'),
                    duplex=interface_data.get('duplex'),
                    mtu=interface_data.get('mtu'),
                    ip_address=interface_data.get('ip_address'),
                    subnet_mask=interface_data.get('subnet_mask'),
                    status=interface_data.get('status'),
                    description=interface_data.get('description')
                )
                db.session.add(interface_inv)
            
            # Clear and update module inventory
            ModuleInventory.query.filter_by(inventory_id=inventory.id).delete()
            for module_data in inventory_data.get('modules', []):
                module_inv = ModuleInventory(
                    inventory_id=inventory.id,
                    slot_number=module_data.get('slot_number'),
                    module_type=module_data.get('module_type'),
                    part_number=module_data.get('part_number'),
                    serial_number=module_data.get('serial_number'),
                    description=module_data.get('description'),
                    status=module_data.get('status')
                )
                db.session.add(module_inv)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Device scan completed successfully',
                'inventory': inventory.to_dict()
            }), 200
            
        except Exception as scan_error:
            # Update status to failed
            inventory.scan_status = 'failed'
            db.session.commit()
            
            current_app.logger.error(f"Device scan failed: {str(scan_error)}")
            return jsonify({
                'message': f'Device scan failed: {str(scan_error)}',
                'inventory': inventory.to_dict()
            }), 500
        
    except Exception as e:
        current_app.logger.error(f"Scan device error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@inventory_bp.route('/scan/all', methods=['POST'])
@jwt_required()
def scan_all_devices():
    try:
        # Get all active devices
        devices = Device.query.filter_by(status='active').all()
        
        scan_results = {
            'total_devices': len(devices),
            'scanned': 0,
            'failed': 0,
            'results': []
        }
        
        for device in devices:
            try:
                # Update or create inventory record
                inventory = Inventory.query.filter_by(device_id=device.id).first()
                if not inventory:
                    inventory = Inventory(device_id=device.id)
                    db.session.add(inventory)
                
                inventory.scan_status = 'scanning'
                inventory.last_inventory_update = datetime.utcnow()
                db.session.commit()
                
                # Perform scan
                inventory_data = scan_device_inventory(device)
                
                # Update inventory (similar to single device scan)
                inventory.hardware_model = inventory_data.get('hardware_model')
                inventory.serial_number = inventory_data.get('serial_number')
                inventory.os_version = inventory_data.get('os_version')
                inventory.firmware_version = inventory_data.get('firmware_version')
                inventory.scan_status = 'completed'
                
                db.session.commit()
                
                scan_results['scanned'] += 1
                scan_results['results'].append({
                    'device_id': device.id,
                    'device_name': device.name,
                    'status': 'success'
                })
                
            except Exception as device_error:
                scan_results['failed'] += 1
                scan_results['results'].append({
                    'device_id': device.id,
                    'device_name': device.name,
                    'status': 'failed',
                    'error': str(device_error)
                })
                
                # Update inventory status to failed
                if 'inventory' in locals():
                    inventory.scan_status = 'failed'
                    db.session.commit()
        
        return jsonify({
            'message': f'Bulk scan completed. {scan_results["scanned"]} successful, {scan_results["failed"]} failed.',
            'results': scan_results
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Scan all devices error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@inventory_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_inventory_summary():
    try:
        # Get inventory statistics
        total_devices = Device.query.count()
        scanned_devices = Inventory.query.filter_by(scan_status='completed').count()
        pending_scans = Inventory.query.filter_by(scan_status='pending').count()
        failed_scans = Inventory.query.filter_by(scan_status='failed').count()
        
        # Get device type breakdown
        device_types = db.session.query(
            Device.device_type,
            db.func.count(Device.id).label('count')
        ).group_by(Device.device_type).all()
        
        type_breakdown = {device_type: count for device_type, count in device_types}
        
        # Get recent scans
        recent_scans = db.session.query(Inventory, Device).join(Device).order_by(
            Inventory.last_inventory_update.desc()
        ).limit(10).all()
        
        recent_scans_data = []
        for inventory, device in recent_scans:
            recent_scans_data.append({
                'device_id': device.id,
                'device_name': device.name,
                'device_type': device.device_type,
                'scan_status': inventory.scan_status,
                'last_scan': inventory.last_inventory_update.isoformat()
            })
        
        return jsonify({
            'summary': {
                'total_devices': total_devices,
                'scanned_devices': scanned_devices,
                'pending_scans': pending_scans,
                'failed_scans': failed_scans,
                'scan_coverage': round((scanned_devices / total_devices * 100) if total_devices > 0 else 0, 2)
            },
            'device_type_breakdown': type_breakdown,
            'recent_scans': recent_scans_data
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get inventory summary error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@inventory_bp.route('/search', methods=['GET'])
@jwt_required()
def search_inventory():
    try:
        query_param = request.args.get('q', '').strip()
        
        if not query_param:
            return jsonify({'message': 'Search query is required'}), 400
        
        # Search in inventory and device data
        results = db.session.query(Inventory, Device).join(Device).filter(
            db.or_(
                Device.name.ilike(f'%{query_param}%'),
                Device.ip_address.ilike(f'%{query_param}%'),
                Inventory.hardware_model.ilike(f'%{query_param}%'),
                Inventory.serial_number.ilike(f'%{query_param}%'),
                Inventory.os_version.ilike(f'%{query_param}%')
            )
        ).limit(50).all()
        
        search_results = []
        for inventory, device in results:
            result_data = inventory.to_dict()
            result_data['device'] = device.to_dict()
            search_results.append(result_data)
        
        return jsonify({
            'query': query_param,
            'total_results': len(search_results),
            'results': search_results
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Search inventory error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500



