# backend/app/inventory/scanner.py
import random
import time
from datetime import datetime
import paramiko
import socket
from contextlib import contextmanager

def scan_device_inventory(device):
    """
    Scans a network device to collect inventory information.
    This is a simulation for the demo. In production, this would use real protocols
    like SSH, SNMP, NETCONF, or REST APIs depending on the device type.
    """
    
    # Simulate connection delay
    time.sleep(random.uniform(1, 3))
    
    # Try to determine if we can actually connect (for simulation)
    can_connect = simulate_connection_check(device)
    
    if not can_connect:
        raise Exception(f"Cannot connect to device {device.name} at {device.ip_address}")
    
    # Generate inventory data based on device type
    inventory_data = generate_simulated_inventory(device)
    
    return inventory_data

def simulate_connection_check(device):
    """
    Simulates checking if we can connect to a device.
    In production, this would be a real connection test.
    """
    # 85% success rate for simulation
    return random.random() < 0.85

def generate_simulated_inventory(device):
    """
    Generates simulated inventory data based on device type.
    """
    device_configs = {
        'router': {
            'hardware_models': ['CISCO2901/K9', 'CISCO1941/K9', 'CISCO3925/K9'],
            'os_versions': ['IOS XE 16.9.3', 'IOS 15.7.3', 'IOS XE 17.3.1'],
            'cpu_cores': [1, 2, 4],
            'memory_gb': [1, 2, 4, 8],
            'storage_gb': [256, 512, 1024]
        },
        'switch': {
            'hardware_models': ['CISCO3850-48T', 'CISCO2960X-48T', 'CISCO9300-48T'],
            'os_versions': ['IOS 15.2.7', 'IOS XE 16.12.4', 'IOS XE 17.6.1'],
            'cpu_cores': [1, 2],
            'memory_gb': [2, 4, 8],
            'storage_gb': [128, 256, 512]
        },
        'server': {
            'hardware_models': ['Dell PowerEdge R740', 'HP ProLiant DL380', 'Supermicro SYS-6029P'],
            'os_versions': ['Ubuntu 20.04.3', 'CentOS 8.4', 'Windows Server 2019'],
            'cpu_cores': [8, 16, 32, 64],
            'memory_gb': [16, 32, 64, 128, 256],
            'storage_gb': [500, 1000, 2000, 4000]
        },
        'wireless': {
            'hardware_models': ['CISCO-AIR-AP3802I', 'CISCO-AIR-AP2802I', 'CISCO-AIR-AP4800'],
            'os_versions': ['AireOS 8.10.151.0', 'AireOS 8.8.130.0', 'IOS XE 17.3.4'],
            'cpu_cores': [1, 2],
            'memory_gb': [1, 2],
            'storage_gb': [64, 128]
        },
        'firewall': {
            'hardware_models': ['ASA5525-X', 'ASA5545-X', 'FTD4112'],
            'os_versions': ['ASA 9.16.1', 'FTD 7.0.1', 'ASA 9.14.3'],
            'cpu_cores': [4, 8, 16],
            'memory_gb': [8, 16, 32],
            'storage_gb': [256, 512, 1024]
        }
    }
    
    config = device_configs.get(device.device_type, device_configs['router'])
    
    # Generate base inventory
    inventory = {
        'hardware_model': random.choice(config['hardware_models']),
        'serial_number': generate_serial_number(),
        'os_version': random.choice(config['os_versions']),
        'firmware_version': f"v{random.randint(1,5)}.{random.randint(0,9)}.{random.randint(0,9)}",
        'cpu_info': {
            'model': f"Intel Xeon E5-{random.randint(2600, 2699)}",
            'cores': random.choice(config['cpu_cores']),
            'frequency': f"{random.uniform(2.0, 3.5):.1f} GHz",
            'utilization': round(random.uniform(5, 75), 2)
        },
        'memory_info': {
            'total_gb': random.choice(config['memory_gb']),
            'available_gb': 0,
            'type': 'DDR4',
            'speed': f"{random.choice([2133, 2400, 2666, 3200])} MHz"
        },
        'storage_info': {
            'total_gb': random.choice(config['storage_gb']),
            'available_gb': 0,
            'type': random.choice(['SSD', 'HDD', 'NVME']),
            'filesystem': random.choice(['ext4', 'NTFS', 'flash'])
        },
        'interfaces': [],
        'modules': []
    }
    
    # Calculate available memory and storage
    inventory['memory_info']['available_gb'] = round(
        inventory['memory_info']['total_gb'] * random.uniform(0.3, 0.8), 2
    )
    inventory['storage_info']['available_gb'] = round(
        inventory['storage_info']['total_gb'] * random.uniform(0.4, 0.9), 2
    )
    
    # Generate interface inventory
    for port in device.ports:
        interface_data = {
            'interface_name': port.name,
            'mac_address': generate_mac_address(),
            'speed': port.speed or random.choice(['100', '1000', '10000']),
            'duplex': port.duplex or random.choice(['full', 'half']),
            'mtu': port.mtu or 1500,
            'ip_address': generate_ip_address() if random.random() < 0.7 else None,
            'subnet_mask': '255.255.255.0' if random.random() < 0.7 else None,
            'status': random.choice(['up', 'down', 'admin-down']),
            'description': f"Interface {port.name} on {device.name}"
        }
        inventory['interfaces'].append(interface_data)
    
    # Generate module inventory for applicable device types
    if device.device_type in ['router', 'switch']:
        num_modules = random.randint(1, 4)
        for i in range(num_modules):
            module_data = {
                'slot_number': i,
                'module_type': random.choice(['Line Card', 'Power Supply', 'Fan Module', 'Supervisor']),
                'part_number': f"WS-X{random.randint(6500, 6800)}-{random.randint(10, 99)}G",
                'serial_number': generate_serial_number(),
                'description': f"Module in slot {i}",
                'status': random.choice(['ok', 'failed', 'not-present'])
            }
            inventory['modules'].append(module_data)
    
    return inventory

def generate_serial_number():
    """Generate a realistic serial number"""
    prefixes = ['FTX', 'FCH', 'FOC', 'JAE', 'CAT']
    return f"{random.choice(prefixes)}{random.randint(1000000, 9999999)}"

def generate_mac_address():
    """Generate a realistic MAC address"""
    # Use Cisco OUI (00:1B:D5) for realism
    oui = "00:1B:D5"
    nic = ":".join([f"{random.randint(0, 255):02x}" for _ in range(3)])
    return f"{oui}:{nic}".upper()

def generate_ip_address():
    """Generate a realistic private IP address"""
    networks = [
        "192.168.{}.{}",
        "10.{}.{}.{}",
        "172.{}.{}.{}"
    ]
    
    network = random.choice(networks)
    
    if "192.168" in network:
        return network.format(random.randint(1, 254), random.randint(1, 254))
    elif "10." in network:
        return network.format(random.randint(0, 255), random.randint(0, 255), random.randint(1, 254))
    else:  # 172.x
        return network.format(random.randint(16, 31), random.randint(0, 255), random.randint(1, 254))

@contextmanager
def ssh_connection(device):
    """
    Context manager for SSH connections.
    In production, this would establish real SSH connections.
    """
    # This is a placeholder for real SSH connection logic
    # In production, you would use paramiko or netmiko
    
    client = None
    try:
        # Simulate connection setup
        time.sleep(0.5)
        
        # For demonstration, we'll just yield a mock client
        class MockSSHClient:
            def exec_command(self, command):
                # Return simulated command output
                return None, type('', (), {'read': lambda: b'simulated output'})(), None
        
        client = MockSSHClient()
        yield client
        
    except Exception as e:
        raise Exception(f"SSH connection failed: {str(e)}")
    finally:
        if client:
            # In production, close the real connection
            pass

def real_ssh_inventory_scan(device):
    """
    Example of how real SSH-based inventory scanning would work.
    This is commented out since it requires actual network devices.
    """
    try:
        with ssh_connection(device) as ssh:
            commands = {
                'cisco_ios': [
                    'show version',
                    'show inventory',
                    'show interfaces',
                    'show ip interface brief',
                    'show running-config | include hostname'
                ],
                'linux': [
                    'uname -a',
                    'lscpu',
                    'free -h',
                    'df -h',
                    'ip addr show'
                ]
            }
            
            # Determine device OS and execute appropriate commands
            # Parse output and return structured data
            pass
            
    except Exception as e:
        raise Exception(f"Real inventory scan failed: {str(e)}")

def snmp_inventory_scan(device):
    """
    Example of SNMP-based inventory scanning.
    This would use libraries like pysnmp in production.
    """
    try:
        # SNMP OIDs for common inventory data
        oids = {
            'sysDescr': '1.3.6.1.2.1.1.1.0',
            'sysUpTime': '1.3.6.1.2.1.1.3.0',
            'sysName': '1.3.6.1.2.1.1.5.0',
            'ifDescr': '1.3.6.1.2.1.2.2.1.2',
            'ifType': '1.3.6.1.2.1.2.2.1.3',
            'ifMtu': '1.3.6.1.2.1.2.2.1.4',
            'ifSpeed': '1.3.6.1.2.1.2.2.1.5',
            'ifPhysAddress': '1.3.6.1.2.1.2.2.1.6',
            'ifAdminStatus': '1.3.6.1.2.1.2.2.1.7',
            'ifOperStatus': '1.3.6.1.2.1.2.2.1.8'
        }
        
        # In production, use SNMP library to query these OIDs
        # from pysnmp.hlapi import *
        # ... SNMP query logic ...
        
        pass
        
    except Exception as e:
        raise Exception(f"SNMP inventory scan failed: {str(e)}")