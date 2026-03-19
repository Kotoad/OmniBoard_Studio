import os
import sys
import platform
import subprocess
import time

def perform_update(save_path):
    if platform.system() == "Windows":
        # Removed STARTUPINFO hidden window flags to allow UAC/Error prompts to appear
        
        # Switched /VERYSILENT to /SILENT. 
        # /SILENT shows the progress bar and errors, but clicks "Next" automatically.
        cmd = [
            save_path, 
            '/SILENT', 
            '/NOCANCEL', 
            '/NORESTART', 
            '/CLOSEAPPLICATIONS', 
            f'/LOG={os.path.join(os.path.dirname(save_path), "update_install.log")}'
        ]
        
        # Launch normally so the UI can appear
        subprocess.Popen(cmd)
        
        time.sleep(1) 
    else:
        # Linux remains background-safe
        app_path = sys.executable
        app_dir = os.path.dirname(os.path.abspath(app_path))
        script = f"sleep 2 && tar -xzf '{save_path}' -C '{app_dir}' && '{app_path}' &"
        subprocess.Popen(['bash', '-c', script])