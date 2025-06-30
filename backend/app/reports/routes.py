# # backend/app/reports/routes.py
# from flask import Blueprint, request, jsonify, send_file
# from flask_jwt_extended import jwt_required
# from app import db
# from app.reports.models import Report
# from app.reports.generator import generate_report
# from datetime import datetime
# import json
# import io

# reports_bp = Blueprint('reports', __name__)

# @reports_bp.route('/', methods=['GET'])
# @jwt_required()
# def get_reports():
#     reports = Report.query.all()
#     return jsonify([report.to_dict() for report in reports]), 200

# @reports_bp.route('/<int:id>', methods=['GET'])
# @jwt_required()
# def get_report(id):
#     report = Report.query.get_or_404(id)
#     return jsonify(report.to_dict()), 200

# @reports_bp.route('/', methods=['POST'])
# @jwt_required()
# def create_report():
#     data = request.get_json()
    
#     report = Report(
#         name=data['name'],
#         report_type=data['report_type'],
#         parameters=json.dumps(data.get('parameters', {})),
#         status='pending'
#     )
    
#     db.session.add(report)
#     db.session.commit()
    
#     # In a real-world application, this would be handled by a background task queue
#     # For simplicity, we'll execute it directly
#     report.status = 'generating'
#     db.session.commit()
    
#     try:
#         result = generate_report(report)
#         report.result = result
#         report.status = 'completed'
#         report.generated_at = datetime.utcnow()
#     except Exception as e:
#         report.result = str(e)
#         report.status = 'failed'
    
#     db.session.commit()
    
#     return jsonify(report.to_dict()), 201

# @reports_bp.route('/types', methods=['GET'])
# @jwt_required()
# def get_report_types():
#     # List of available report types
#     report_types = [
#         {
#             'id': 'inventory',
#             'name': 'Inventory Report',
#             'description': 'Detailed inventory of network devices and their components'
#         },
#         {
#             'id': 'performance',
#             'name': 'Performance Report',
#             'description': 'Analysis of network performance metrics over time'
#         },
#         {
#             'id': 'connectivity',
#             'name': 'Connectivity Report',
#             'description': 'Overview of device connections and network topology'
#         },
#         {
#             'id': 'provisioning',
#             'name': 'Provisioning Report',
#             'description': 'History of device provisioning tasks and their outcomes'
#         }
#     ]
    
#     return jsonify(report_types), 200

# @reports_bp.route('/download/<int:id>', methods=['GET'])
# @jwt_required()
# def download_report(id):
#     report = Report.query.get_or_404(id)
    
#     if report.status != 'completed':
#         return jsonify(message=f"Report is not ready for download. Status: {report.status}"), 400
    
#     # Create in-memory file
#     file_data = io.BytesIO(report.result.encode())
#     file_data.seek(0)
    
#     # Determine file type based on report type
#     if report.report_type in ['inventory', 'performance', 'connectivity', 'provisioning']:
#         filename = f"{report.report_type}_report_{report.id}.html"
#         mimetype = 'text/html'
#     else:
#         filename = f"report_{report.id}.txt"
#         mimetype = 'text/plain'
    
#     return send_file(
#         file_data,
#         mimetype=mimetype,
#         as_attachment=True,
#         attachment_filename=filename
#     )





# backend/app/reports/routes.py
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.reports.models import Report
from app.reports.generator import ReportGenerator
from datetime import datetime
import json
import os
import threading

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/', methods=['GET'])
@jwt_required()
def get_reports():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        report_type = request.args.get('report_type')
        status = request.args.get('status')
        created_by = request.args.get('created_by')
        
        # Build query
        query = Report.query
        
        if report_type:
            query = query.filter(Report.report_type == report_type)
        
        if status:
            query = query.filter(Report.status == status)
        
        if created_by:
            query = query.filter(Report.created_by == created_by)
        
        # Paginate
        reports = query.order_by(Report.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'reports': [report.to_dict() for report in reports.items],
            'total': reports.total,
            'pages': reports.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get reports error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@reports_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_report(id):
    try:
        report = Report.query.get_or_404(id)
        include_content = request.args.get('include_content', False, type=bool)
        
        return jsonify(report.to_dict(include_content=include_content)), 200
        
    except Exception as e:
        current_app.logger.error(f"Get report error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@reports_bp.route('/', methods=['POST'])
@jwt_required()
def create_report():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        # Required fields
        required_fields = ['name', 'report_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400
        
        # Validate report type
        valid_types = ['inventory', 'performance', 'connectivity', 'provisioning', 'telemetry', 'security']
        if data['report_type'] not in valid_types:
            return jsonify({'message': f'Invalid report type. Must be one of: {", ".join(valid_types)}'}), 400
        
        # Create report
        report = Report(
            name=data['name'],
            report_type=data['report_type'],
            description=data.get('description'),
            parameters=json.dumps(data.get('parameters', {})),
            format=data.get('format', 'html'),
            created_by=current_user_id,
            status='pending'
        )
        
        db.session.add(report)
        db.session.commit()
        
        # Generate report asynchronously if requested
        if data.get('generate_immediately', True):
            try:
                generator = ReportGenerator()
                generator.generate_report_async(report.id)
                return jsonify({
                    'message': 'Report created and generation started',
                    'report': report.to_dict()
                }), 201
            except Exception as e:
                current_app.logger.error(f"Failed to start report generation: {str(e)}")
                return jsonify({
                    'message': 'Report created but failed to start generation',
                    'report': report.to_dict(),
                    'generation_error': str(e)
                }), 201
        
        return jsonify(report.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Create report error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@reports_bp.route('/<int:id>/generate', methods=['POST'])
@jwt_required()
def generate_report(id):
    try:
        report = Report.query.get_or_404(id)
        
        if report.status in ['generating']:
            return jsonify({'message': 'Report is already being generated'}), 400
        
        # Reset report status
        report.status = 'pending'
        report.progress = 0
        report.error_message = None
        db.session.commit()
        
        # Generate report
        generator = ReportGenerator()
        generator.generate_report_async(report.id)
        
        return jsonify({
            'message': 'Report generation started',
            'report': report.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Generate report error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@reports_bp.route('/<int:id>/download', methods=['GET'])
@jwt_required()
def download_report(id):
    try:
        report = Report.query.get_or_404(id)
        
        if report.status != 'completed':
            return jsonify({'message': f'Report is not ready for download. Status: {report.status}'}), 400
        
        if not report.result and not report.file_path:
            return jsonify({'message': 'Report content not available'}), 404
        
        # If file exists, serve it
        if report.file_path and os.path.exists(report.file_path):
            return send_file(
                report.file_path,
                as_attachment=True,
                download_name=f"{report.name}.{report.format}"
            )
        
        # Otherwise, serve content directly
        if report.result:
            from io import BytesIO
            
            content = report.result.encode('utf-8') if isinstance(report.result, str) else report.result
            file_data = BytesIO(content)
            file_data.seek(0)
            
            # Determine MIME type
            mime_types = {
                'html': 'text/html',
                'pdf': 'application/pdf',
                'csv': 'text/csv',
                'json': 'application/json'
            }
            
            return send_file(
                file_data,
                mimetype=mime_types.get(report.format, 'text/plain'),
                as_attachment=True,
                download_name=f"{report.name}.{report.format}"
            )
        
        return jsonify({'message': 'Report content not found'}), 404
        
    except Exception as e:
        current_app.logger.error(f"Download report error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@reports_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_report(id):
    try:
        current_user_id = get_jwt_identity()
        report = Report.query.get_or_404(id)
        
        # Check permissions (admin or creator can delete)
        from app.auth.models import User
        user = User.query.get(current_user_id)
        if user.role != 'admin' and report.created_by != current_user_id:
            return jsonify({'message': 'Permission denied'}), 403
        
        # Delete file if it exists
        if report.file_path and os.path.exists(report.file_path):
            try:
                os.remove(report.file_path)
            except OSError:
                pass  # File might be in use or already deleted
        
        db.session.delete(report)
        db.session.commit()
        
        return jsonify({'message': 'Report deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Delete report error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@reports_bp.route('/types', methods=['GET'])
@jwt_required()
def get_report_types():
    """Get available report types and their descriptions"""
    try:
        report_types = [
            {
                'id': 'inventory',
                'name': 'Inventory Report',
                'description': 'Detailed inventory of network devices and their components',
                'parameters': [
                    {'name': 'device_ids', 'type': 'array', 'description': 'Specific device IDs to include'},
                    {'name': 'device_types', 'type': 'array', 'description': 'Device types to include'},
                    {'name': 'include_hardware', 'type': 'boolean', 'description': 'Include hardware details'}
                ]
            },
            {
                'id': 'performance',
                'name': 'Performance Report',
                'description': 'Analysis of network performance metrics over time',
                'parameters': [
                    {'name': 'device_ids', 'type': 'array', 'description': 'Devices to analyze'},
                    {'name': 'metrics', 'type': 'array', 'description': 'Metrics to include'},
                    {'name': 'time_range', 'type': 'string', 'description': 'Time range (1h, 1d, 1w, 1m)'},
                    {'name': 'aggregation', 'type': 'string', 'description': 'Data aggregation method'}
                ]
            },
            {
                'id': 'connectivity',
                'name': 'Connectivity Report',
                'description': 'Overview of device connections and network topology',
                'parameters': [
                    {'name': 'include_physical', 'type': 'boolean', 'description': 'Include physical connections'},
                    {'name': 'include_logical', 'type': 'boolean', 'description': 'Include logical connections'},
                    {'name': 'format', 'type': 'string', 'description': 'Output format (table, diagram)'}
                ]
            },
            {
                'id': 'provisioning',
                'name': 'Provisioning Report',
                'description': 'History of device provisioning tasks and their outcomes',
                'parameters': [
                    {'name': 'time_range', 'type': 'string', 'description': 'Time range to analyze'},
                    {'name': 'status_filter', 'type': 'array', 'description': 'Task statuses to include'},
                    {'name': 'device_types', 'type': 'array', 'description': 'Device types to include'}
                ]
            },
            {
                'id': 'telemetry',
                'name': 'Telemetry Report',
                'description': 'Telemetry data analysis and trends',
                'parameters': [
                    {'name': 'metrics', 'type': 'array', 'description': 'Metrics to analyze'},
                    {'name': 'time_range', 'type': 'string', 'description': 'Analysis time range'},
                    {'name': 'include_alerts', 'type': 'boolean', 'description': 'Include alert analysis'}
                ]
            },
            {
                'id': 'security',
                'name': 'Security Report',
                'description': 'Security analysis and compliance status',
                'parameters': [
                    {'name': 'compliance_framework', 'type': 'string', 'description': 'Compliance framework'},
                    {'name': 'include_vulnerabilities', 'type': 'boolean', 'description': 'Include vulnerability scan'},
                    {'name': 'risk_assessment', 'type': 'boolean', 'description': 'Include risk assessment'}
                ]
            }
        ]
        
        return jsonify({
            'report_types': report_types
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get report types error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@reports_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_reports_summary():
    try:
        # Get report statistics
        total_reports = Report.query.count()
        completed_reports = Report.query.filter_by(status='completed').count()
        failed_reports = Report.query.filter_by(status='failed').count()
        generating_reports = Report.query.filter_by(status='generating').count()
        
        # Get reports by type
        type_stats = db.session.query(
            Report.report_type,
            db.func.count(Report.id).label('count')
        ).group_by(Report.report_type).all()
        
        type_breakdown = {report_type: count for report_type, count in type_stats}
        
        # Get recent reports
        recent_reports = Report.query.order_by(
            Report.created_at.desc()
        ).limit(10).all()
        
        return jsonify({
            'summary': {
                'total_reports': total_reports,
                'completed_reports': completed_reports,
                'failed_reports': failed_reports,
                'generating_reports': generating_reports,
                'success_rate': round((completed_reports / total_reports * 100) if total_reports > 0 else 0, 2)
            },
            'type_breakdown': type_breakdown,
            'recent_reports': [report.to_dict() for report in recent_reports]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get reports summary error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500
