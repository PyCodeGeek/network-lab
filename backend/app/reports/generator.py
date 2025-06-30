
# # backend/app/reports/generator.py
# import json
# from datetime import datetime
# from app.devices.models import Device, Port
# from app.inventory.models import Inventory
# from app.telemetry.models import TelemetryData
# from jinja2 import Template

# def generate_report(report):
#     """
#     Generates a report based on the specified type and parameters.
#     """
#     report_type = report.report_type
#     parameters = json.loads(report.parameters) if report.parameters else {}
    
#     # Select the appropriate report generation function
#     if report_type == 'inventory':
#         return generate_inventory_report(parameters)
#     elif report_type == 'performance':
#         return generate_performance_report(parameters)
#     elif report_type == 'connectivity':
#         return generate_connectivity_report(parameters)
#     elif report_type == 'provisioning':
#         return generate_provisioning_report(parameters)
#     else:
#         raise ValueError(f"Unknown report type: {report_type}")

# def generate_inventory_report(parameters):
#     """Generates an inventory report."""
#     # Get all devices or filter by device_ids if provided
#     device_ids = parameters.get('device_ids', [])
    
#     if device_ids:
#         devices = Device.query.filter(Device.id.in_(device_ids)).all()
#     else:
#         devices = Device.query.all()
    
#     # Collect inventory data
#     inventory_data = []
#     for device in devices:
#         inventory = Inventory.query.filter_by(device_id=device.id).first()
        
#         device_data = {
#             'id': device.id,
#             'name': device.name,
#             'device_type': device.device_type,
#             'ip_address': device.ip_address,
#             'status': device.status,
#             'ports': [port.to_dict() for port in device.ports],
#             'inventory': inventory.to_dict() if inventory else None
#         }
        
#         inventory_data.append(device_data)
    
#     # Generate HTML report
#     template_str = """
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <title>Network Inventory Report</title>
#         <style>
#             body { font-family: Arial, sans-serif; margin: 20px; }
#             h1 { color: #333366; }
#             table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
#             th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
#             th { background-color: #f2f2f2; }
#             tr:nth-child(even) { background-color: #f9f9f9; }
#             .section { margin-bottom: 30px; }
#         </style>
#     </head>
#     <body>
#         <h1>Network Inventory Report</h1>
#         <p>Generated: {{ generated_at }}</p>
        
#         <div class="section">
#             <h2>Device Summary</h2>
#             <table>
#                 <tr>
#                     <th>ID</th>
#                     <th>Name</th>
#                     <th>Type</th>
#                     <th>IP Address</th>
#                     <th>Status</th>
#                 </tr>
#                 {% for device in devices %}
#                 <tr>
#                     <td>{{ device.id }}</td>
#                     <td>{{ device.name }}</td>
#                     <td>{{ device.device_type }}</td>
#                     <td>{{ device.ip_address }}</td>
#                     <td>{{ device.status }}</td>
#                 </tr>
#                 {% endfor %}
#             </table>
#         </div>
        
#         {% for device in devices %}
#         <div class="section">
#             <h2>{{ device.name }} Details</h2>
            
#             {% if device.inventory %}
#             <h3>Hardware Information</h3>
#             <table>
#                 <tr>
#                     <th>Hardware Model</th>
#                     <td>{{ device.inventory.hardware_model }}</td>
#                 </tr>
#                 <tr>
#                     <th>Serial Number</th>
#                     <td>{{ device.inventory.serial_number }}</td>
#                 </tr>
#                 <tr>
#                     <th>OS Version</th>
#                     <td>{{ device.inventory.os_version }}</td>
#                 </tr>
#                 <tr>
#                     <th>Last Updated</th>
#                     <td>{{ device.inventory.last_inventory_update }}</td>
#                 </tr>
#             </table>
#             {% else %}
#             <p>No inventory data available for this device.</p>
#             {% endif %}
            
#             <h3>Ports</h3>
#             <table>
#                 <tr>
#                     <th>Name</th>
#                     <th>Type</th>
#                     <th>Status</th>
#                     <th>Connected To</th>
#                 </tr>
#                 {% for port in device.ports %}
#                 <tr>
#                     <td>{{ port.name }}</td>
#                     <td>{{ port.port_type }}</td>
#                     <td>{{ port.status }}</td>
#                     <td>{{ port.connected_to_port_id }}</td>
#                 </tr>
#                 {% endfor %}
#             </table>
#         </div>
#         {% endfor %}
#     </body>
#     </html>
#     """
    
#     template = Template(template_str)
#     report_html = template.render(
#         devices=inventory_data,
#         generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
#     )
    
#     return report_html

# def generate_performance_report(parameters):
#     """Generates a performance report based on telemetry data."""
#     # Implementation would be similar to the inventory report but with telemetry data
#     # For brevity, returning a placeholder
#     return "<html><body><h1>Performance Report</h1><p>This is a placeholder for the performance report.</p></body></html>"

# def generate_connectivity_report(parameters):
#     """Generates a report on network connectivity."""
#     # Implementation would analyze the connections between devices
#     # For brevity, returning a placeholder
#     return "<html><body><h1>Connectivity Report</h1><p>This is a placeholder for the connectivity report.</p></body></html>"

# def generate_provisioning_report(parameters):
#     """Generates a report on provisioning tasks."""
#     # Implementation would analyze provisioning tasks and their outcomes
#     # For brevity, returning a placeholder
#     return "<html><body><h1>Provisioning Report</h1><p>This is a placeholder for the provisioning report.</p></body></html>"


















# backend/app/reports/generator.py
import json
import os
import threading
from datetime import datetime, timedelta
from jinja2 import Template, Environment, DictLoader
from app import db
from app.reports.models import Report
from app.devices.models import Device, Port
from app.inventory.models import Inventory
from app.provisioning.models import ProvisioningTask
from app.telemetry.models import TelemetryData, TelemetryAlert
from sqlalchemy import func, and_

class ReportGenerator:
    def __init__(self):
        self.template_env = self._setup_template_environment()
    
    def _setup_template_environment(self):
        """Setup Jinja2 template environment with custom templates"""
        templates = {
            'base_html': self._get_base_html_template(),
            'inventory_report': self._get_inventory_template(),
            'performance_report': self._get_performance_template(),
            'connectivity_report': self._get_connectivity_template(),
            'provisioning_report': self._get_provisioning_template()
        }
        
        return Environment(loader=DictLoader(templates))
    
    def generate_report_async(self, report_id):
        """Generate a report asynchronously"""
        thread = threading.Thread(target=self.generate_report, args=(report_id,))
        thread.daemon = True
        thread.start()
        return thread
    
    def generate_report(self, report_id):
        """Generate a report"""
        report = None
        try:
            # Get report from database
            report = Report.query.get(report_id)
            if not report:
                raise Exception(f"Report {report_id} not found")
            
            # Update status
            report.status = 'generating'
            report.progress = 0
            db.session.commit()
            
            # Generate report based on type
            if report.report_type == 'inventory':
                content = self.generate_inventory_report(report)
            elif report.report_type == 'performance':
                content = self.generate_performance_report(report)
            elif report.report_type == 'connectivity':
                content = self.generate_connectivity_report(report)
            elif report.report_type == 'provisioning':
                content = self.generate_provisioning_report(report)
            elif report.report_type == 'telemetry':
                content = self.generate_telemetry_report(report)
            elif report.report_type == 'security':
                content = self.generate_security_report(report)
            else:
                raise Exception(f"Unknown report type: {report.report_type}")
            
            # Save report content
            report.result = content
            report.file_size = len(content.encode('utf-8')) if content else 0
            report.status = 'completed'
            report.progress = 100
            report.generated_at = datetime.utcnow()
            
            db.session.commit()
            
        except Exception as e:
            error_msg = str(e)
            if report:
                report.status = 'failed'
                report.error_message = error_msg
                report.progress = 0
                db.session.commit()
            
            from flask import current_app
            current_app.logger.error(f"Report generation failed for report {report_id}: {error_msg}")
    
    def generate_inventory_report(self, report):
        """Generate inventory report"""
        parameters = json.loads(report.parameters) if report.parameters else {}
        
        # Get devices based on parameters
        query = Device.query
        
        if parameters.get('device_ids'):
            query = query.filter(Device.id.in_(parameters['device_ids']))
        
        if parameters.get('device_types'):
            query = query.filter(Device.device_type.in_(parameters['device_types']))
        
        devices = query.all()
        
        # Collect inventory data
        inventory_data = []
        total_devices = len(devices)
        
        for i, device in enumerate(devices):
            # Update progress
            progress = int((i / total_devices) * 90)  # Reserve 10% for template rendering
            report.progress = progress
            db.session.commit()
            
            inventory = Inventory.query.filter_by(device_id=device.id).first()
            
            device_data = {
                'device': device.to_dict(),
                'inventory': inventory.to_dict() if inventory else None,
                'ports': [port.to_dict() for port in device.ports]
            }
            
            inventory_data.append(device_data)
        
        # Generate report content
        template = self.template_env.get_template('inventory_report')
        content = template.render(
            report=report.to_dict(),
            devices=inventory_data,
            generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            total_devices=total_devices,
            parameters=parameters
        )
        
        return content
    
    def generate_performance_report(self, report):
        """Generate performance report"""
        parameters = json.loads(report.parameters) if report.parameters else {}
        
        # Parse time range
        time_range = parameters.get('time_range', '1d')
        if time_range == '1h':
            start_time = datetime.utcnow() - timedelta(hours=1)
        elif time_range == '1d':
            start_time = datetime.utcnow() - timedelta(days=1)
        elif time_range == '1w':
            start_time = datetime.utcnow() - timedelta(weeks=1)
        elif time_range == '1m':
            start_time = datetime.utcnow() - timedelta(days=30)
        else:
            start_time = datetime.utcnow() - timedelta(days=1)
        
        # Get telemetry data
        query = TelemetryData.query.filter(TelemetryData.timestamp >= start_time)
        
        if parameters.get('device_ids'):
            query = query.filter(TelemetryData.device_id.in_(parameters['device_ids']))
        
        if parameters.get('metrics'):
            query = query.filter(TelemetryData.metric.in_(parameters['metrics']))
        
        telemetry_data = query.all()
        
        # Process data for report
        performance_data = self._process_performance_data(telemetry_data, parameters)
        
        template = self.template_env.get_template('performance_report')
        content = template.render(
            report=report.to_dict(),
            performance_data=performance_data,
            generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            time_range=time_range,
            parameters=parameters
        )
        
        return content
    
    def generate_connectivity_report(self, report):
        """Generate connectivity report"""
        parameters = json.loads(report.parameters) if report.parameters else {}
        
        # Get all devices and their connections
        devices = Device.query.all()
        connections = []
        
        for device in devices:
            for port in device.ports:
                if port.connected_to_port_id:
                    connected_port = Port.query.get(port.connected_to_port_id)
                    if connected_port:
                        connections.append({
                            'from_device': device.name,
                            'from_port': port.name,
                            'to_device': connected_port.device.name,
                            'to_port': connected_port.name,
                            'status': port.status
                        })
        
        # Generate topology data
        topology_data = {
            'devices': [device.to_dict() for device in devices],
            'connections': connections,
            'total_devices': len(devices),
            'total_connections': len(connections),
            'active_connections': len([c for c in connections if c['status'] == 'up'])
        }
        
        template = self.template_env.get_template('connectivity_report')
        content = template.render(
            report=report.to_dict(),
            topology=topology_data,
            generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            parameters=parameters
        )
        
        return content
    
    def generate_provisioning_report(self, report):
        """Generate provisioning report"""
        parameters = json.loads(report.parameters) if report.parameters else {}
        
        # Parse time range
        time_range = parameters.get('time_range', '1w')
        if time_range == '1d':
            start_time = datetime.utcnow() - timedelta(days=1)
        elif time_range == '1w':
            start_time = datetime.utcnow() - timedelta(weeks=1)
        elif time_range == '1m':
            start_time = datetime.utcnow() - timedelta(days=30)
        else:
            start_time = datetime.utcnow() - timedelta(weeks=1)
        
        # Get provisioning tasks
        query = ProvisioningTask.query.filter(ProvisioningTask.created_at >= start_time)
        
        if parameters.get('status_filter'):
            query = query.filter(ProvisioningTask.status.in_(parameters['status_filter']))
        
        tasks = query.order_by(ProvisioningTask.created_at.desc()).all()
        
        # Calculate statistics
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status == 'completed'])
        failed_tasks = len([t for t in tasks if t.status == 'failed'])
        success_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        provisioning_data = {
            'tasks': [task.to_dict() for task in tasks],
            'statistics': {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'failed_tasks': failed_tasks,
                'success_rate': round(success_rate, 2)
            }
        }
        
        template = self.template_env.get_template('provisioning_report')
        content = template.render(
            report=report.to_dict(),
            provisioning_data=provisioning_data,
            generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            time_range=time_range,
            parameters=parameters
        )
        
        return content
    
    def generate_telemetry_report(self, report):
        """Generate telemetry report"""
        # Placeholder for telemetry report
        return "<html><body><h1>Telemetry Report</h1><p>Coming soon...</p></body></html>"
    
    def generate_security_report(self, report):
        """Generate security report"""
        # Placeholder for security report
        return "<html><body><h1>Security Report</h1><p>Coming soon...</p></body></html>"
    
    def _process_performance_data(self, telemetry_data, parameters):
        """Process telemetry data for performance reporting"""
        # Group data by device and metric
        grouped_data = {}
        
        for data_point in telemetry_data:
            device_id = data_point.device_id
            metric = data_point.metric
            
            if device_id not in grouped_data:
                grouped_data[device_id] = {}
            
            if metric not in grouped_data[device_id]:
                grouped_data[device_id][metric] = []
            
            grouped_data[device_id][metric].append({
                'value': data_point.value,
                'timestamp': data_point.timestamp.isoformat(),
                'unit': data_point.unit
            })
        
        # Calculate statistics for each metric
        processed_data = {}
        
        for device_id, metrics in grouped_data.items():
            device = Device.query.get(device_id)
            processed_data[device_id] = {
                'device_name': device.name if device else f'Device {device_id}',
                'metrics': {}
            }
            
            for metric, values in metrics.items():
                if values:
                    numeric_values = [v['value'] for v in values if v['value'] is not None]
                    if numeric_values:
                        processed_data[device_id]['metrics'][metric] = {
                            'min': min(numeric_values),
                            'max': max(numeric_values),
                            'avg': sum(numeric_values) / len(numeric_values),
                            'count': len(numeric_values),
                            'unit': values[0]['unit'],
                            'values': values[-10:]  # Last 10 values for trending
                        }
        
        return processed_data
    
    def _get_base_html_template(self):
        """Base HTML template for reports"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ report.name }} - Network Lab Report</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            border-bottom: 2px solid #2563eb;
            margin-bottom: 30px;
            padding-bottom: 20px;
        }
        .title {
            color: #2563eb;
            margin: 0;
        }
        .subtitle {
            color: #64748b;
            margin: 5px 0 0;
        }
        .meta-info {
            background: #f8fafc;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .content {
            margin: 20px 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }
        th {
            background: #f1f5f9;
            font-weight: 600;
            color: #475569;
        }
        tr:hover {
            background: #f8fafc;
        }
        .stat-card {
            background: #fff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 20px;
            margin: 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            color: #2563eb;
        }
        .stat-label {
            color: #64748b;
            font-size: 0.875rem;
        }
        .status-active { color: #10b981; }
        .status-inactive { color: #ef4444; }
        .status-warning { color: #f59e0b; }
        @media print {
            body { font-size: 12px; }
            .no-print { display: none; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1 class="title">{{ report.name }}</h1>
        <p class="subtitle">{{ report.description or report.report_type.title() + " Report" }}</p>
    </div>
    
    <div class="meta-info">
        <strong>Generated:</strong> {{ generated_at }}<br>
        <strong>Report Type:</strong> {{ report.report_type.title() }}<br>
        <strong>Created By:</strong> {{ report.created_by or "System" }}
    </div>
    
    <div class="content">
        {% block content %}{% endblock %}
    </div>
    
    <div class="footer" style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e2e8f0; color: #64748b; font-size: 0.875rem;">
        <p>Generated by Network Lab Automation Framework</p>
    </div>
</body>
</html>
        """
    
    def _get_inventory_template(self):
        """Inventory report template"""
        return """
{% extends "base_html" %}
{% block content %}
    <div style="display: flex; flex-wrap: wrap; margin: -10px;">
        <div class="stat-card">
            <div class="stat-value">{{ total_devices }}</div>
            <div class="stat-label">Total Devices</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{{ devices|selectattr('device.status', 'equalto', 'active')|list|length }}</div>
            <div class="stat-label">Active Devices</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{{ devices|selectattr('inventory')|list|length }}</div>
            <div class="stat-label">Scanned Devices</div>
        </div>
    </div>

    <h2>Device Inventory</h2>
    <table>
        <thead>
            <tr>
                <th>Device Name</th>
                <th>Type</th>
                <th>IP Address</th>
                <th>Status</th>
                <th>Hardware Model</th>
                <th>OS Version</th>
                <th>Serial Number</th>
            </tr>
        </thead>
        <tbody>
            {% for item in devices %}
            <tr>
                <td>{{ item.device.name }}</td>
                <td>{{ item.device.device_type.title() }}</td>
                <td>{{ item.device.ip_address }}</td>
                <td class="status-{{ item.device.status }}">{{ item.device.status.title() }}</td>
                <td>{{ item.inventory.hardware_model if item.inventory else 'N/A' }}</td>
                <td>{{ item.inventory.os_version if item.inventory else 'N/A' }}</td>
                <td>{{ item.inventory.serial_number if item.inventory else 'N/A' }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    {% for item in devices %}
    {% if item.inventory %}
    <h3>{{ item.device.name }} - Detailed Information</h3>
    <div style="background: #f8fafc; padding: 15px; border-radius: 8px; margin: 10px 0;">
        <h4>Hardware Details</h4>
        <p><strong>Model:</strong> {{ item.inventory.hardware_model }}</p>
        <p><strong>Serial Number:</strong> {{ item.inventory.serial_number }}</p>
        <p><strong>OS Version:</strong> {{ item.inventory.os_version }}</p>
        {% if item.inventory.cpu_info %}
        <p><strong>CPU:</strong> {{ item.inventory.cpu_info.model }} ({{ item.inventory.cpu_info.cores }} cores)</p>
        {% endif %}
        {% if item.inventory.memory_info %}
        <p><strong>Memory:</strong> {{ item.inventory.memory_info.total_gb }}GB</p>
        {% endif %}
        
        {% if item.ports %}
        <h4>Ports ({{ item.ports|length }})</h4>
        <table style="font-size: 0.875rem;">
            <thead>
                <tr>
                    <th>Port Name</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Speed</th>
                    <th>Connected To</th>
                </tr>
            </thead>
            <tbody>
                {% for port in item.ports %}
                <tr>
                    <td>{{ port.name }}</td>
                    <td>{{ port.port_type }}</td>
                    <td class="status-{{ 'active' if port.status == 'up' else 'inactive' }}">{{ port.status }}</td>
                    <td>{{ port.speed or 'N/A' }}</td>
                    <td>{{ 'Connected' if port.connected_to_port_id else 'Not Connected' }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% endif %}
    </div>
    {% endif %}
    {% endfor %}
{% endblock %}
        """
    
    def _get_performance_template(self):
        """Performance report template"""
        return """
{% extends "base_html" %}
{% block content %}
    <h2>Performance Summary</h2>
    <p><strong>Analysis Period:</strong> {{ time_range }}</p>
    
    {% for device_id, device_data in performance_data.items() %}
    <h3>{{ device_data.device_name }}</h3>
    <div style="background: #f8fafc; padding: 15px; border-radius: 8px; margin: 10px 0;">
        {% for metric, stats in device_data.metrics.items() %}
        <h4>{{ metric.replace('_', ' ').title() }}</h4>
        <div style="display: flex; gap: 20px; margin: 10px 0;">
            <div class="stat-card" style="margin: 0; flex: 1;">
                <div class="stat-value" style="font-size: 1.5rem;">{{ "%.2f"|format(stats.min) }}</div>
                <div class="stat-label">Minimum {{ stats.unit }}</div>
            </div>
            <div class="stat-card" style="margin: 0; flex: 1;">
                <div class="stat-value" style="font-size: 1.5rem;">{{ "%.2f"|format(stats.avg) }}</div>
                <div class="stat-label">Average {{ stats.unit }}</div>
            </div>
            <div class="stat-card" style="margin: 0; flex: 1;">
                <div class="stat-value" style="font-size: 1.5rem;">{{ "%.2f"|format(stats.max) }}</div>
                <div class="stat-label">Maximum {{ stats.unit }}</div>
            </div>
            <div class="stat-card" style="margin: 0; flex: 1;">
                <div class="stat-value" style="font-size: 1.5rem;">{{ stats.count }}</div>
                <div class="stat-label">Data Points</div>
            </div>
        </div>
        {% endfor %}
    </div>
    {% endfor %}
{% endblock %}
        """
    
    def _get_connectivity_template(self):
        """Connectivity report template"""
        return """
{% extends "base_html" %}
{% block content %}
    <div style="display: flex; flex-wrap: wrap; margin: -10px;">
        <div class="stat-card">
            <div class="stat-value">{{ topology.total_devices }}</div>
            <div class="stat-label">Total Devices</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{{ topology.total_connections }}</div>
            <div class="stat-label">Total Connections</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{{ topology.active_connections }}</div>
            <div class="stat-label">Active Connections</div>
        </div>
    </div>

    <h2>Network Topology</h2>
    <table>
        <thead>
            <tr>
                <th>Source Device</th>
                <th>Source Port</th>
                <th>Target Device</th>
                <th>Target Port</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            {% for connection in topology.connections %}
            <tr>
                <td>{{ connection.from_device }}</td>
                <td>{{ connection.from_port }}</td>
                <td>{{ connection.to_device }}</td>
                <td>{{ connection.to_port }}</td>
                <td class="status-{{ 'active' if connection.status == 'up' else 'inactive' }}">{{ connection.status.title() }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <h2>Device Details</h2>
    {% for device in topology.devices %}
    <h3>{{ device.name }}</h3>
    <div style="background: #f8fafc; padding: 15px; border-radius: 8px; margin: 10px 0;">
        <p><strong>Type:</strong> {{ device.device_type.title() }}</p>
        <p><strong>IP Address:</strong> {{ device.ip_address }}</p>
        <p><strong>Status:</strong> <span class="status-{{ device.status }}">{{ device.status.title() }}</span></p>
        <p><strong>Ports:</strong> {{ device.ports|length }}</p>
        <p><strong>Connected Ports:</strong> {{ device.ports|selectattr('connected_to_port_id')|list|length }}</p>
    </div>
    {% endfor %}
{% endblock %}
        """
    
    def _get_provisioning_template(self):
        """Provisioning report template"""
        return """
{% extends "base_html" %}
{% block content %}
    <div style="display: flex; flex-wrap: wrap; margin: -10px;">
        <div class="stat-card">
            <div class="stat-value">{{ provisioning_data.statistics.total_tasks }}</div>
            <div class="stat-label">Total Tasks</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{{ provisioning_data.statistics.completed_tasks }}</div>
            <div class="stat-label">Completed</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{{ provisioning_data.statistics.failed_tasks }}</div>
            <div class="stat-label">Failed</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{{ provisioning_data.statistics.success_rate }}%</div>
            <div class="stat-label">Success Rate</div>
        </div>
    </div>

    <h2>Provisioning Tasks</h2>
    <table>
        <thead>
            <tr>
                <th>Task Name</th>
                <th>Device</th>
                <th>Template</th>
                <th>Status</th>
                <th>Created</th>
                <th>Duration</th>
            </tr>
        </thead>
        <tbody>
            {% for task in provisioning_data.tasks %}
            <tr>
                <td>{{ task.name }}</td>
                <td>{{ task.device_name }}</td>
                <td>{{ task.template_name or 'Custom' }}</td>
                <td class="status-{{ 'active' if task.status == 'completed' else ('warning' if task.status == 'running' else 'inactive') }}">{{ task.status.title() }}</td>
                <td>{{ task.created_at[:19] }}</td>
                <td>{{ task.duration or 'N/A' }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
{% endblock %}
        """