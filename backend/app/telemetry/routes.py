# backend/app/telemetry/routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.telemetry.models import TelemetryConfig, TelemetryData
from app.devices.models import Device
from app.telemetry.collector import collect_telemetry
from datetime import datetime, timedelta
import json

telemetry_bp = Blueprint('telemetry', __name__)

@telemetry_bp.route('/config', methods=['GET'])
@jwt_required()
def get_telemetry_configs():
    configs = TelemetryConfig.query.all()
    return jsonify([config.to_dict() for config in configs]), 200

@telemetry_bp.route('/config/<int:device_id>', methods=['GET'])
@jwt_required()
def get_device_telemetry_config(device_id):
    config = TelemetryConfig.query.filter_by(device_id=device_id).first()
    
    if not config:
        return jsonify(message="No telemetry configuration found for this device"), 404
    
    return jsonify(config.to_dict()), 200

@telemetry_bp.route('/config/<int:device_id>', methods=['POST'])
@jwt_required()
def configure_device_telemetry(device_id):
    device = Device.query.get_or_404(device_id)
    data = request.get_json()
    
    # Check if configuration exists
    config = TelemetryConfig.query.filter_by(device_id=device_id).first()
    
    if not config:
        # Create new configuration
        config = TelemetryConfig(
            device_id=device_id,
            metrics=json.dumps(data.get('metrics', [])),
            collection_interval=data.get('collection_interval', 60),
            enabled=data.get('enabled', True)
        )
        db.session.add(config)
    else:
        # Update existing configuration
        if 'metrics' in data:
            config.metrics = json.dumps(data['metrics'])
        if 'collection_interval' in data:
            config.collection_interval = data['collection_interval']
        if 'enabled' in data:
            config.enabled = data['enabled']
    
    db.session.commit()
    
    return jsonify(config.to_dict()), 200

@telemetry_bp.route('/data/<int:device_id>', methods=['GET'])
@jwt_required()
def get_device_telemetry_data(device_id):
    device = Device.query.get_or_404(device_id)
    
    # Parse query parameters
    metric = request.args.get('metric')
    start_time_str = request.args.get('start_time')
    end_time_str = request.args.get('end_time')
    limit = request.args.get('limit', 100, type=int)
    
    # Build query
    query = TelemetryData.query.filter_by(device_id=device_id)
    
    if metric:
        query = query.filter_by(metric=metric)
    
    if start_time_str:
        start_time = datetime.fromisoformat(start_time_str)
        query = query.filter(TelemetryData.timestamp >= start_time)
    
    if end_time_str:
        end_time = datetime.fromisoformat(end_time_str)
        query = query.filter(TelemetryData.timestamp <= end_time)
    
    # Order by timestamp descending and limit results
    telemetry_data = query.order_by(TelemetryData.timestamp.desc()).limit(limit).all()
    
    return jsonify([data.to_dict() for data in telemetry_data]), 200

@telemetry_bp.route('/collect/<int:device_id>', methods=['POST'])
@jwt_required()
def collect_device_telemetry(device_id):
    device = Device.query.get_or_404(device_id)
    config = TelemetryConfig.query.filter_by(device_id=device_id).first()
    
    if not config:
        return jsonify(message="Telemetry not configured for this device"), 400
    
    if not config.enabled:
        return jsonify(message="Telemetry collection is disabled for this device"), 400
    
    # In a real-world application, this would be handled by a background task scheduler
    # For simplicity, we'll execute it directly
    telemetry_results = collect_telemetry(device, config)
    
    # Store the collected data
    for result in telemetry_results:
        telemetry_data = TelemetryData(
            device_id=device_id,
            metric=result['metric'],
            value=result['value'],
            unit=result['unit'],
            timestamp=datetime.utcnow()
        )
        db.session.add(telemetry_data)
    
    db.session.commit()
    
    return jsonify({"message": "Telemetry data collected successfully", "count": len(telemetry_results)}), 200

@telemetry_bp.route('/summary/<int:device_id>', methods=['GET'])
@jwt_required()
def get_device_telemetry_summary(device_id):
    device = Device.query.get_or_404(device_id)
    
    # Get the last 24 hours of data
    start_time = datetime.utcnow() - timedelta(hours=24)
    
    # Get all metrics for this device
    metrics_query = db.session.query(TelemetryData.metric).filter_by(device_id=device_id).distinct()
    metrics = [row[0] for row in metrics_query.all()]
    
    summary = {}
    for metric in metrics:
        # Get the latest value
        latest = TelemetryData.query.filter_by(
            device_id=device_id, 
            metric=metric
        ).order_by(TelemetryData.timestamp.desc()).first()
        
        # Get min, max, avg for the last 24 hours
        data_points = TelemetryData.query.filter(
            TelemetryData.device_id == device_id,
            TelemetryData.metric == metric,
            TelemetryData.timestamp >= start_time
        ).all()
        
        values = [point.value for point in data_points if point.value is not None]
        
        if values:
            min_val = min(values)
            max_val = max(values)
            avg_val = sum(values) / len(values)
        else:
            min_val = max_val = avg_val = None
        
        summary[metric] = {
            'latest': latest.value if latest else None,
            'unit': latest.unit if latest else None,
            'timestamp': latest.timestamp.isoformat() if latest else None,
            'min': min_val,
            'max': max_val,
            'avg': avg_val,
            'count': len(values)
        }
    
    return jsonify(summary), 200