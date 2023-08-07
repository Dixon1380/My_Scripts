import psutil
# Basic script that allows me to see the process running on any machine.
def display_system_processes():
    print("System Processes:")
    print("{:<10} {:<40} {:<10} {:<10}".format("PID", "Name", "Status", "CPU Usage (%)"))

    for process in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent']):
        pid = process.info['pid']
        name = process.info['name']
        status = process.info['status']
        cpu_percent = process.info['cpu_percent']

        print("{:<10} {:<40} {:<10} {:<10.2f}".format(pid, name, status, cpu_percent))

if __name__ == "__main__":
    display_system_processes()
