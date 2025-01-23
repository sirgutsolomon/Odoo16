# SYSTEM_HASH: ALLOW_FIRST_TIME
import json
import hashlib
import os
import platform
import subprocess
import sys
import ctypes
# Check if running as a PyInstaller executable
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS  # Temp directory for bundled app
else:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

file_path = os.path.join(BASE_DIR, 'location.py')
def get_hdd_serial():
    if platform.system() == "Windows":
        import win32api
        import win32file
        volume_info = win32api.GetVolumeInformation("C:\\")
        return str(volume_info[1])
    elif platform.system() == "Linux":
        try:
            with open("/sys/class/dmi/id/board_serial", "r") as file:
                return file.read().strip()
        except FileNotFoundError:
            try:
                with open("/sys/class/dmi/id/product_uuid", "r") as file:
                    return file.read().strip()
            except FileNotFoundError:
                try:
                    with open("/var/lib/dbus/machine-id", "r") as file:
                        return file.read().strip()
                except FileNotFoundError:
                    return ""
    else:
        return ""

def get_machine_guid():
    if platform.system() == "Windows":
        try:
            import winreg
            registry = winreg.HKEY_LOCAL_MACHINE
            address = "SOFTWARE\\Microsoft\\Cryptography"
            key = winreg.OpenKey(registry, address, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
            value = winreg.QueryValueEx(key, "MachineGuid")[0]
            winreg.CloseKey(key)
            return value
        except Exception:
            return ""
    return ""

def get_mac_address():
    try:
        import netifaces
        for interface in netifaces.interfaces():
            if netifaces.AF_LINK in netifaces.ifaddresses(interface):
                return netifaces.ifaddresses(interface)[netifaces.AF_LINK][0]['addr']
    except ImportError:
        pass
    return ""

def get_system_info():
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "hdd_serial": get_hdd_serial(),
        "mac_address": get_mac_address(),
        "machine_guid": get_machine_guid(),
    }

def encrypt_data(data):
    serialized_data = json.dumps(data, sort_keys=True).encode()
    return hashlib.sha256(serialized_data).hexdigest()

def initialize_self():
    system_info = get_system_info()
    encrypted_info = encrypt_data(system_info)

    with open(file_path, 'r') as file:
        content = file.readlines()

    hash_placeholder = "# SYSTEM_HASH:"
    for line in content:
        if line.startswith(hash_placeholder):
            stored_hash = line[len(hash_placeholder):].strip()
            if hashlib.sha256(stored_hash.encode()).hexdigest() == hashlib.sha256("ALLOW_FIRST_TIME".encode()).hexdigest():
                update_self()  # Lock to this machine on first run
            return

    with open(file_path, 'a') as file:
        file.write(f"{hash_placeholder} {encrypted_info}\n")

def update_self():
    system_info = get_system_info()
    encrypted_info = encrypt_data(system_info)

    with open(file_path, 'r') as file:
        content = file.readlines()

    # Replace the placeholder for the hash if it exists
    new_content = []
    hash_placeholder = "# SYSTEM_HASH:"
    hash_updated = False

    for line in content:
        if line.startswith(hash_placeholder):
            new_content.append(f"{hash_placeholder} {encrypted_info}\n")
            hash_updated = True
        else:
            new_content.append(line)

    if not hash_updated:
        new_content.append(f"{hash_placeholder} {encrypted_info}\n")

    with open(file_path, 'w') as file:
        file.writelines(new_content)

def verify_self():
    system_info = get_system_info()
    current_hash = encrypt_data(system_info)

    with open(file_path, 'r') as file:
        content = file.readlines()

    hash_placeholder = "# SYSTEM_HASH:"
    for line in content:
        if line.startswith(hash_placeholder):
            stored_hash = line[len(hash_placeholder):].strip()
            return stored_hash == current_hash

    return False
def open_browser():
    """Open the default browser to localhost:8069."""
    if platform.system().lower() == "linux":
        subprocess.run(["xdg-open", "http://localhost:8069"])
    elif platform.system().lower() == "windows":
        subprocess.run(["start", "http://localhost:8069"], shell=True)