# backend/app/telemetry/collector.py
import random
import time
from datetime import datetime

def collect_telemetry(device, config):
    """
    Simulates collecting telemetry data from a network device.
    In a real implementation, this would connect to the device using SNMP/NETCONF/etc.
    """
    metrics = json.loads(config.metrics) if config.metrics else []
    results = []
    
    # Map of available metrics and their collection functions
    metric_collectors = {
        'cpu_utilization': collect_cpu_utilization,
        'memory_utilization': collect_memory_utilization,
        'interface_throughput': collect_interface_throughput,
        'packet_loss': collect_packet_loss,
        'temperature': collect_temperature
    }
    
    # Collect each configured metric
    for metric in metrics:
        if metric in metric_collectors:
            # Simulate a small delay for each metric collection
            time.sleep(0.2)
            
            try:
                # Call the appropriate collector function
                metric_data = metric_collectors[metric](device)
                results.extend(metric_data)
            except Exception as e:
                # Log error but continue with other metrics
                print(f"Error collecting {metric} for device {device.name}: {str(e)}")
    
    return results

def collect_cpu_utilization(device):
    """Simulates collecting CPU utilization data."""
    return [{
        'metric': 'cpu_utilization',
        'value': random.uniform(5, 80),
        'unit': '%'
    }]

def collect_memory_utilization(device):
    """Simulates collecting memory utilization data."""
    return [{
        'metric': 'memory_utilization',
        'value': random.uniform(20, 90),
        'unit': '%'
    }]

def collect_interface_throughput(device):
    """Simulates collecting interface throughput data."""
    results = []
    
    for port in device.ports:
        if port.status == 'up':
            results.append({
                'metric': f'interface_throughput_in_{port.name}',
                'value': random.uniform(0, 1000),
                'unit': 'Mbps'
            })
            results.append({
                'metric': f'interface_throughput_out_{port.name}',
                'value': random.uniform(0, 1000),
                'unit': 'Mbps'
            })
    
    return results

def collect_packet_loss(device):
    """Simulates collecting packet loss data."""
    return [{
        'metric': 'packet_loss',
        'value': random.uniform(0, 2),
        'unit': '%'
    }]

def collect_temperature(device):
    """Simulates collecting temperature data."""
    return [{
        'metric': 'temperature',
        'value': random.uniform(30, 70),
        'unit': '°C'
    }]