import psutil
import os
import signal

def close_application_by_path(app_path):
    # Normalize the path (replace environment variables like %windir%)
    app_path = os.path.expandvars(app_path)

    # Iterate through all running processes
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            # Check if process executable path matches
            if proc.info['exe'] and app_path.lower() == proc.info['exe'].lower():
                # Kill the parent process and its children
                parent_proc = psutil.Process(proc.info['pid'])
                for child_proc in parent_proc.children(recursive=True):
                    child_proc.terminate()  # Terminate child processes
                parent_proc.terminate()  # Terminate parent process
                print(f"Closed application: {proc.info['name']} (PID: {proc.info['pid']})")
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    print(f"Application with path '{app_path}' not found.")
    return False

def close_application_by_name(app_name):
    app_name_lower = app_name.lower()
    found = False
    
    # Iterate through all running processes
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # Check if process name matches (case-insensitive)
            if app_name_lower in proc.info['name'].lower():
                # Kill the parent process and its children
                parent_proc = psutil.Process(proc.info['pid'])
                for child_proc in parent_proc.children(recursive=True):
                    child_proc.terminate()  # Terminate child processes
                parent_proc.terminate()  # Terminate parent process
                print(f"Closed application: {proc.info['name']} (PID: {proc.info['pid']})")
                found = True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    if not found:
        print(f"Application with name '{app_name}' not found.")
    return found
