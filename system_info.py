import psutil
import socket
import platform
import json
import logging

def get_system_info():
    # Get system information
    system_info = {
        "hostname": socket.gethostname(),
        "operating_system": platform.system(),
        "cpu_count": psutil.cpu_count(),
        "cpu_usage": psutil.cpu_percent(),
        "memory_total": psutil.virtual_memory().total,
        "memory_used": psutil.virtual_memory().used,
        "disk_total": psutil.disk_usage('/').total,
        "disk_used": psutil.disk_usage('/').used,
    }
    return system_info

def get_utilization_info():
    # Get utilization information
    disk_io = psutil.disk_io_counters()
    net_io = psutil.net_io_counters()
    utilization_info = {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_read_bytes": disk_io.read_bytes,
        "disk_write_bytes": disk_io.write_bytes,
        "network_io_sent": net_io.bytes_sent,
        "network_io_recv": net_io.bytes_recv,
    }
    return utilization_info

def get_error_logs():
    # Get recent error logs
    error_logs = []
    try:
        with open('error_logs.txt', 'r') as f:
            for line in f.readlines():
                error_logs.append(line)
    except FileNotFoundError:
        logging.error("Error log file not found.")
    return error_logs

def store_information():
    # Store system information, utilization information, and error logs to a file
    with open('system_info.json', 'w') as f:
        json.dump(get_system_info(), f, indent=4)

    with open('utilization_info.json', 'w') as f:
        json.dump(get_utilization_info(), f, indent=4)

    with open('error_logs.txt', 'w') as f:
        f.writelines(get_error_logs())

if __name__ == '__main__':
    store_information()
