
# backend/app/devices/utils.py
import ipaddress
import subprocess
import platform
from datetime import datetime
import socket
import paramiko
from flask import current_app

def validate_ip_address(ip_str):
    """Validate IP address format"""
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False

def ping_device(ip_address, timeout=5):
    """Ping a device to test connectivity"""
    try:
        # Determine ping command based on OS
        if platform.system().lower() == 'windows':
            cmd = ['ping', '-n', '1', '-w', str(timeout * 1000), ip_address]
        else:
            cmd = ['ping', '-c', '1', '-W', str(timeout), ip_address]
        
        start_time = datetime.now()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 2)
        end_time = datetime.now()
        
        response_time = (end_time - start_time).total_seconds() * 1000
        
        return {
            'success': result.returncode == 0,
            'time': response_time,
            'output': result.stdout
        }
        
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': 'Timeout'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def test_ssh_connection(ip_address, username, password, port=22, timeout=10):
    """Test SSH connectivity to a device"""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        ssh.connect(
            hostname=ip_address,
            port=port,
            username=username,
            password=password,
            timeout=timeout
        )
        
        # Test with a simple command
        stdin, stdout, stderr = ssh.exec_command('echo "SSH connection successful"')
        output = stdout.read().decode().strip()
        
        ssh.close()
        
        return {
            'success': True,
            'output': output
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def get_device_info(ip_address, username, password, port=22):
    """Get basic device information via SSH"""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        ssh.connect(
            hostname=ip_address,
            port=port,
            username=username,
            password=password,
            timeout=30
        )
        
        # Try different commands to get device info
        commands = [
            'show version',  # Cisco
            'uname -a',      # Linux/Unix
            'hostname',      # Generic
        ]
        
        info = {}
        
        for cmd in commands:
            try:
                stdin, stdout, stderr = ssh.exec_command(cmd)
                output = stdout.read().decode().strip()
                if output:
                    info[cmd] = output
                    break
            except:
                continue
        
        ssh.close()
        
        return {
            'success': True,
            'info': info
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }