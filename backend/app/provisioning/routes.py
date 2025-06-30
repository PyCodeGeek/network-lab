
# backend/app/provisioning/routes.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.provisioning.models import ConfigTemplate, ProvisioningTask, ProvisioningLog
from app.devices.models import Device
from app.auth.models import User
from app.provisioning.provisioner import ProvisioningEngine
from datetime import datetime
import json

provisioning_bp = Blueprint('provisioning', __name__)

# Template Management Routes
@provisioning_bp.route('/templates', methods=['GET'])
@jwt_required()
def get_templates():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        device_type = request.args.get('device_type')
        is_active = request.args.get('is_active', type=bool)
        include_content = request.args.get('include_content', False, type=bool)
        
        # Build query
        query = ConfigTemplate.query
        
        if device_type:
            query = query.filter(ConfigTemplate.device_type == device_type)
        
        if is_active is not None:
            query = query.filter(ConfigTemplate.is_active == is_active)
        
        # Paginate
        templates = query.order_by(ConfigTemplate.updated_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'templates': [template.to_dict(include_content=include_content) for template in templates.items],
            'total': templates.total,
            'pages': templates.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get templates error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@provisioning_bp.route('/templates/<int:id>', methods=['GET'])
@jwt_required()
def get_template(id):
    try:
        template = ConfigTemplate.query.get_or_404(id)
        return jsonify(template.to_dict(include_content=True)), 200
        
    except Exception as e:
        current_app.logger.error(f"Get template error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@provisioning_bp.route('/templates', methods=['POST'])
@jwt_required()
def create_template():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        # Required fields
        required_fields = ['name', 'device_type', 'content']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400
        
        # Validate device type
        valid_types = ['router', 'switch', 'server', 'wireless', 'firewall']
        if data['device_type'] not in valid_types:
            return jsonify({'message': f'Invalid device type. Must be one of: {", ".join(valid_types)}'}), 400
        
        # Check if template name already exists
        if ConfigTemplate.query.filter_by(name=data['name']).first():
            return jsonify({'message': 'Template with this name already exists'}), 409
        
        # Validate template variables if provided
        variables = data.get('variables', [])
        if variables and not isinstance(variables, list):
            return jsonify({'message': 'Variables must be a list'}), 400
        
        # Create template
        template = ConfigTemplate(
            name=data['name'],
            device_type=data['device_type'],
            content=data['content'],
            variables=json.dumps(variables) if variables else None,
            description=data.get('description'),
            version=data.get('version', '1.0'),
            created_by=current_user_id
        )
        
        db.session.add(template)
        db.session.commit()
        
        return jsonify(template.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Create template error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@provisioning_bp.route('/templates/<int:id>', methods=['PUT'])
@jwt_required()
def update_template(id):
    try:
        template = ConfigTemplate.query.get_or_404(id)
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        # Update allowed fields
        updateable_fields = ['name', 'device_type', 'content', 'variables', 'description', 'version', 'is_active']
        
        for field in updateable_fields:
            if field in data:
                if field == 'name' and data[field] != template.name:
                    # Check name uniqueness
                    if ConfigTemplate.query.filter(ConfigTemplate.name == data[field], ConfigTemplate.id != id).first():
                        return jsonify({'message': 'Template with this name already exists'}), 409
                
                if field == 'variables':
                    # Validate and convert variables to JSON
                    variables = data[field]
                    if variables and not isinstance(variables, list):
                        return jsonify({'message': 'Variables must be a list'}), 400
                    setattr(template, field, json.dumps(variables) if variables else None)
                else:
                    setattr(template, field, data[field])
        
        template.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(template.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Update template error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@provisioning_bp.route('/templates/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_template(id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        template = ConfigTemplate.query.get_or_404(id)
        
        # Check permissions (admin or creator can delete)
        if user.role != 'admin' and template.created_by != current_user_id:
            return jsonify({'message': 'Permission denied'}), 403
        
        # Check if template is being used by active tasks
        active_tasks = ProvisioningTask.query.filter_by(
            template_id=id, 
            status='running'
        ).count()
        
        if active_tasks > 0:
            return jsonify({'message': 'Cannot delete template with active provisioning tasks'}), 409
        
        db.session.delete(template)
        db.session.commit()
        
        return jsonify({'message': 'Template deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Delete template error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

# Task Management Routes
@provisioning_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        status = request.args.get('status')
        device_id = request.args.get('device_id', type=int)
        include_configs = request.args.get('include_configs', False, type=bool)
        
        # Build query
        query = ProvisioningTask.query
        
        if status:
            query = query.filter(ProvisioningTask.status == status)
        
        if device_id:
            query = query.filter(ProvisioningTask.device_id == device_id)
        
        # Paginate
        tasks = query.order_by(ProvisioningTask.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'tasks': [task.to_dict(include_configs=include_configs) for task in tasks.items],
            'total': tasks.total,
            'pages': tasks.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get tasks error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@provisioning_bp.route('/tasks/<int:id>', methods=['GET'])
@jwt_required()
def get_task(id):
    try:
        task = ProvisioningTask.query.get_or_404(id)
        include_configs = request.args.get('include_configs', True, type=bool)
        
        result = task.to_dict(include_configs=include_configs)
        
        # Include logs if requested
        if request.args.get('include_logs', False, type=bool):
            result['logs'] = [log.to_dict() for log in task.logs]
        
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f"Get task error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@provisioning_bp.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        # Required fields
        device_id = data.get('device_id')
        name = data.get('name')
        
        if not device_id or not name:
            return jsonify({'message': 'device_id and name are required'}), 400
        
        # Verify device exists
        device = Device.query.get_or_404(device_id)
        
        # Get template if specified
        template_id = data.get('template_id')
        template = None
        if template_id:
            template = ConfigTemplate.query.get_or_404(template_id)
            if not template.is_active:
                return jsonify({'message': 'Template is not active'}), 400
        
        # Create task
        task = ProvisioningTask(
            device_id=device_id,
            template_id=template_id,
            name=name,
            config_data=json.dumps(data.get('config_data', {})),
            created_by=current_user_id,
            status='pending'
        )
        
        db.session.add(task)
        db.session.commit()
        
        # Execute task asynchronously if requested
        if data.get('execute_immediately', False):
            try:
                engine = ProvisioningEngine()
                engine.execute_task_async(task.id)
                return jsonify({
                    'message': 'Task created and execution started',
                    'task': task.to_dict()
                }), 201
            except Exception as e:
                current_app.logger.error(f"Failed to start task execution: {str(e)}")
                return jsonify({
                    'message': 'Task created but failed to start execution',
                    'task': task.to_dict(),
                    'execution_error': str(e)
                }), 201
        
        return jsonify(task.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Create task error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@provisioning_bp.route('/tasks/<int:id>/execute', methods=['POST'])
@jwt_required()
def execute_task(id):
    try:
        task = ProvisioningTask.query.get_or_404(id)
        
        if task.status not in ['pending', 'failed']:
            return jsonify({'message': f'Task is already {task.status}'}), 400
        
        # Reset task status
        task.status = 'pending'
        task.error_message = None
        task.progress = 0
        db.session.commit()
        
        # Execute task
        engine = ProvisioningEngine()
        engine.execute_task_async(task.id)
        
        return jsonify({
            'message': 'Task execution started',
            'task': task.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Execute task error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@provisioning_bp.route('/tasks/<int:id>/cancel', methods=['POST'])
@jwt_required()
def cancel_task(id):
    try:
        task = ProvisioningTask.query.get_or_404(id)
        
        if task.status not in ['pending', 'running']:
            return jsonify({'message': f'Cannot cancel task with status {task.status}'}), 400
        
        # Update task status
        task.status = 'cancelled'
        task.completed_at = datetime.utcnow()
        task.error_message = 'Task cancelled by user'
        
        # Add log entry
        log_entry = ProvisioningLog(
            task_id=task.id,
            level='INFO',
            message='Task cancelled by user'
        )
        db.session.add(log_entry)
        db.session.commit()
        
        return jsonify({
            'message': 'Task cancelled successfully',
            'task': task.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Cancel task error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@provisioning_bp.route('/tasks/<int:id>/rollback', methods=['POST'])
@jwt_required()
def rollback_task(id):
    try:
        task = ProvisioningTask.query.get_or_404(id)
        
        if task.status != 'completed':
            return jsonify({'message': 'Can only rollback completed tasks'}), 400
        
        if not task.rollback_config:
            return jsonify({'message': 'No rollback configuration available'}), 400
        
        # Create a new rollback task
        rollback_task = ProvisioningTask(
            device_id=task.device_id,
            template_id=None,
            name=f"Rollback: {task.name}",
            config_data=json.dumps({'rollback_from_task': task.id}),
            rendered_config=task.rollback_config,
            created_by=get_jwt_identity(),
            status='pending'
        )
        
        db.session.add(rollback_task)
        db.session.commit()
        
        # Execute rollback task
        engine = ProvisioningEngine()
        engine.execute_task_async(rollback_task.id)
        
        return jsonify({
            'message': 'Rollback task created and started',
            'rollback_task': rollback_task.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Rollback task error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@provisioning_bp.route('/tasks/<int:id>/logs', methods=['GET'])
@jwt_required()
def get_task_logs(id):
    try:
        task = ProvisioningTask.query.get_or_404(id)
        
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 100, type=int), 500)
        level = request.args.get('level')
        
        # Build query
        query = ProvisioningLog.query.filter_by(task_id=id)
        
        if level:
            query = query.filter(ProvisioningLog.level == level.upper())
        
        # Paginate
        logs = query.order_by(ProvisioningLog.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'logs': [log.to_dict() for log in logs.items],
            'total': logs.total,
            'pages': logs.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get task logs error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@provisioning_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_provisioning_summary():
    try:
        # Get task statistics
        total_tasks = ProvisioningTask.query.count()
        completed_tasks = ProvisioningTask.query.filter_by(status='completed').count()
        failed_tasks = ProvisioningTask.query.filter_by(status='failed').count()
        running_tasks = ProvisioningTask.query.filter_by(status='running').count()
        pending_tasks = ProvisioningTask.query.filter_by(status='pending').count()
        
        # Get template statistics
        total_templates = ConfigTemplate.query.count()
        active_templates = ConfigTemplate.query.filter_by(is_active=True).count()
        
        # Get recent tasks
        recent_tasks = ProvisioningTask.query.order_by(
            ProvisioningTask.created_at.desc()
        ).limit(10).all()
        
        # Success rate
        success_rate = round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2)
        
        return jsonify({
            'summary': {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'failed_tasks': failed_tasks,
                'running_tasks': running_tasks,
                'pending_tasks': pending_tasks,
                'success_rate': success_rate,
                'total_templates': total_templates,
                'active_templates': active_templates
            },
            'recent_tasks': [task.to_dict() for task in recent_tasks]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get provisioning summary error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500