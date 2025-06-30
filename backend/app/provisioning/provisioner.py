
# backend/app/provisioning/provisioner.py
import json
import time
import threading
from datetime import datetime
from jinja2 import Template, TemplateError
from app import db
from app.provisioning.models import ProvisioningTask, ProvisioningLog
from app.devices.models import Device
import paramiko
import socket

class ProvisioningEngine:
    def __init__(self):
        self.active_tasks = {}
    
    def execute_task_async(self, task_id):
        """Execute a provisioning task asynchronously"""
        thread = threading.Thread(target=self.execute_task, args=(task_id,))
        thread.daemon = True
        thread.start()
        self.active_tasks[task_id] = thread
        return thread
    
    def execute_task(self, task_id):
        """Execute a provisioning task"""
        task = None
        try:
            # Get task from database
            task = ProvisioningTask.query.get(task_id)
            if not task:
                raise Exception(f"Task {task_id} not found")
            
            # Update task status
            task.status = 'running'
            task.started_at = datetime.utcnow()
            task.progress = 0
            db.session.commit()
            
            self.log_message(task, 'INFO', f"Starting provisioning task: {task.name}")
            
            # Get device
            device = task.device
            if not device:
                raise Exception("Device not found")
            
            self.log_message(task, 'INFO', f"Target device: {device.name} ({device.ip_address})")
            
            # Render configuration
            config = self.render_configuration(task)
            task.rendered_config = config
            task.progress = 25
            db.session.commit()
            
            self.log_message(task, 'INFO', "Configuration rendered successfully")
            
            # Get current configuration for rollback
            current_config = self.get_current_configuration(device)
            if current_config:
                task.rollback_config = current_config
                db.session.commit()
                self.log_message(task, 'INFO', "Current configuration saved for rollback")
            
            task.progress = 50
            db.session.commit()
            
            # Apply configuration
            result = self.apply_configuration(device, config)
            task.result = json.dumps(result)
            task.progress = 90
            db.session.commit()
            
            self.log_message(task, 'INFO', "Configuration applied successfully")
            
            # Verify configuration
            if self.verify_configuration(device, config):
                task.status = 'completed'
                task.progress = 100
                self.log_message(task, 'INFO', "Configuration verified successfully")
            else:
                task.status = 'completed'
                task.progress = 100
                self.log_message(task, 'WARNING', "Configuration applied but verification failed")
            
            task.completed_at = datetime.utcnow()
            db.session.commit()
            
        except Exception as e:
            error_msg = str(e)
            if task:
                task.status = 'failed'
                task.error_message = error_msg
                task.completed_at = datetime.utcnow()
                task.progress = 0
                db.session.commit()
                self.log_message(task, 'ERROR', f"Task failed: {error_msg}")
            
            # Log to application logger as well
            from flask import current_app
            current_app.logger.error(f"Provisioning task {task_id} failed: {error_msg}")
        
        finally:
            # Remove from active tasks
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
    
    def render_configuration(self, task):
        """Render configuration template with provided variables"""
        try:
            if task.template:
                # Use template
                template_content = task.template.content
                config_data = json.loads(task.config_data) if task.config_data else {}
                
                # Add default variables
                config_data.update({
                    'device_name': task.device.name,
                    'device_ip': task.device.ip_address,
                    'device_type': task.device.device_type,
                    'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                })
                
                template = Template(template_content)
                rendered = template.render(**config_data)
                
                self.log_message(task, 'DEBUG', f"Template variables: {json.dumps(config_data, indent=2)}")
                
            else:
                # Direct configuration
                config_data = json.loads(task.config_data) if task.config_data else {}
                rendered = config_data.get('raw_config', task.rendered_config or '')
            
            if not rendered.strip():
                raise Exception("Rendered configuration is empty")
            
            return rendered
            
        except TemplateError as e:
            raise Exception(f"Template rendering error: {str(e)}")
        except Exception as e:
            raise Exception(f"Configuration rendering failed: {str(e)}")
    
    def get_current_configuration(self, device):
        """Get current device configuration for rollback purposes"""
        try:
            self.log_message(None, 'INFO', f"Retrieving current configuration from {device.name}")
            
            # This is a simulation. In production, use real device connections
            if device.device_type in ['router', 'switch']:
                return self.simulate_cisco_config_backup(device)
            elif device.device_type == 'server':
                return self.simulate_server_config_backup(device)
            else:
                return f"# Configuration backup for {device.name}\n# Type: {device.device_type}\n"
            
        except Exception as e:
            # Don't fail the task if backup fails, just log it
            self.log_message(None, 'WARNING', f"Failed to backup current configuration: {str(e)}")
            return None
    
    def apply_configuration(self, device, config):
        """Apply configuration to device"""
        try:
            self.log_message(None, 'INFO', f"Applying configuration to {device.name}")
            
            # Simulate configuration application based on device type
            if device.device_type in ['router', 'switch']:
                return self.apply_cisco_configuration(device, config)
            elif device.device_type == 'server':
                return self.apply_server_configuration(device, config)
            elif device.device_type == 'wireless':
                return self.apply_wireless_configuration(device, config)
            elif device.device_type == 'firewall':
                return self.apply_firewall_configuration(device, config)
            else:
                return self.apply_generic_configuration(device, config)
            
        except Exception as e:
            raise Exception(f"Configuration application failed: {str(e)}")
    
    def verify_configuration(self, device, config):
        """Verify that configuration was applied successfully"""
        try:
            self.log_message(None, 'INFO', f"Verifying configuration on {device.name}")
            
            # Simulate verification process
            time.sleep(1)  # Simulate verification delay
            
            # In production, this would check specific configuration items
            # For simulation, we'll have a 90% success rate
            import random
            success = random.random() < 0.9
            
            if success:
                self.log_message(None, 'INFO', "Configuration verification passed")
            else:
                self.log_message(None, 'WARNING', "Configuration verification failed")
            
            return success
            
        except Exception as e:
            self.log_message(None, 'ERROR', f"Configuration verification error: {str(e)}")
            return False
    
    def simulate_cisco_config_backup(self, device):
        """Simulate backing up Cisco device configuration"""
        time.sleep(2)  # Simulate network delay
        
        return f"""!
! Configuration backup for {device.name}
! Type: {device.device_type}
! Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
!
version 15.7
service timestamps debug datetime msec
service timestamps log datetime msec
no service password-encryption
!
hostname {device.name}
!
interface GigabitEthernet0/0
 ip address {device.ip_address} 255.255.255.0
 no shutdown
!
interface GigabitEthernet0/1
 no ip address
 shutdown
!
line con 0
line vty 0 4
 login
!
end"""
    
    def simulate_server_config_backup(self, device):
        """Simulate backing up server configuration"""
        time.sleep(1)  # Simulate backup delay
        
        return f"""# Configuration backup for {device.name}
# Type: {device.device_type}
# Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}

# Network configuration
DEVICE={device.name}
IPADDR={device.ip_address}
NETMASK=255.255.255.0

# System configuration
HOSTNAME={device.name}
TIMEZONE=UTC
"""
    
    def apply_cisco_configuration(self, device, config):
        """Simulate applying configuration to Cisco device"""
        time.sleep(3)  # Simulate configuration time
        
        # Simulate SSH connection and configuration
        self.log_message(None, 'INFO', f"Connecting to {device.ip_address} via SSH")
        self.log_message(None, 'INFO', "Entering configuration mode")
        self.log_message(None, 'INFO', "Applying configuration commands")
        
        # Count configuration lines for progress
        config_lines = [line.strip() for line in config.split('\n') if line.strip() and not line.strip().startswith('!')]
        total_lines = len(config_lines)
        
        result = {
            'success': True,
            'lines_applied': total_lines,
            'output': f"Configuration with {total_lines} commands applied successfully",
            'warnings': [],
            'errors': []
        }
        
        # Simulate some warnings for realism
        if total_lines > 10:
            result['warnings'].append("Large configuration detected, consider applying in smaller chunks")
        
        self.log_message(None, 'INFO', f"Applied {total_lines} configuration commands")
        return result
    
    def apply_server_configuration(self, device, config):
        """Simulate applying configuration to server"""
        time.sleep(2)  # Simulate configuration time
        
        self.log_message(None, 'INFO', f"Connecting to {device.ip_address} via SSH")
        self.log_message(None, 'INFO', "Applying server configuration")
        
        result = {
            'success': True,
            'config_files_updated': ['network', 'hostname', 'services'],
            'output': "Server configuration applied successfully",
            'services_restarted': ['networking', 'ssh'],
            'warnings': [],
            'errors': []
        }
        
        return result
    
    def apply_wireless_configuration(self, device, config):
        """Simulate applying configuration to wireless device"""
        time.sleep(2)
        
        result = {
            'success': True,
            'output': "Wireless configuration applied successfully",
            'radio_restarted': True,
            'warnings': [],
            'errors': []
        }
        
        return result
    
    def apply_firewall_configuration(self, device, config):
        """Simulate applying configuration to firewall"""
        time.sleep(3)
        
        result = {
            'success': True,
            'output': "Firewall configuration applied successfully",
            'rules_updated': True,
            'policy_compiled': True,
            'warnings': [],
            'errors': []
        }
        
        return result
    
    def apply_generic_configuration(self, device, config):
        """Simulate applying configuration to generic device"""
        time.sleep(2)
        
        result = {
            'success': True,
            'output': f"Configuration applied to {device.device_type} device",
            'warnings': [],
            'errors': []
        }
        
        return result
    
    def log_message(self, task, level, message):
        """Add log message to task"""
        if task:
            log_entry = ProvisioningLog(
                task_id=task.id,
                level=level,
                message=message
            )
            db.session.add(log_entry)
            db.session.commit()
        
        # Also log to application logger
        from flask import current_app
        if current_app:
            getattr(current_app.logger, level.lower(), current_app.logger.info)(f"Task {task.id if task else 'N/A'}: {message}")

# Real SSH connection example (commented out for simulation)
def real_ssh_provisioning(device, config):
    """
    Example of real SSH-based device provisioning.
    This would be used in production environments.
    """
    try:
        # Create SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to device
        ssh.connect(
            hostname=device.ip_address,
            port=device.ssh_port,
            username=device.username,
            password=device.password,
            timeout=30
        )
        
        # Execute configuration commands
        commands = config.split('\n')
        results = []
        
        for command in commands:
            command = command.strip()
            if command and not command.startswith('!'):
                stdin, stdout, stderr = ssh.exec_command(command)
                output = stdout.read().decode()
                error = stderr.read().decode()
                
                results.append({
                    'command': command,
                    'output': output,
                    'error': error
                })
        
        ssh.close()
        return {'success': True, 'results': results}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}