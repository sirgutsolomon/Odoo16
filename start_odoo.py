import os
import platform
import subprocess
import sys
import json
import hashlib
# Define base directory for portable setup

# Get the directory where the executable is located
if getattr(sys, 'frozen', False):  # Check if running from a packaged executable
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PG_BIN = os.path.join(BASE_DIR,"portableodoo","postgres", "bin")
PG_DATA = os.path.join(BASE_DIR,"portableodoo","postgres", "data")
PG_LOG = os.path.join(BASE_DIR,"portableodoo","postgres", "logfile.log")
# ODOO_BIN = os.path.join(BASE_DIR,"odoo-bin")
# ODOO_CONFIG = os.path.join(BASE_DIR,"odoo.conf")
ODOO_BIN = os.path.join(sys._MEIPASS, 'odoo-bin')
ODOO_CONFIG = os.path.join(sys._MEIPASS, 'odoo.conf')
def start_postgres():
    """Start PostgreSQL."""
    pg_ctl_path = os.path.join(PG_BIN, "pg_ctl")
    if not os.path.exists(pg_ctl_path):
        print(f"Error: pg_ctl not found at {pg_ctl_path}.")
        sys.exit(1)

    if not os.path.exists(PG_DATA):
        print("Error: PostgreSQL data directory not initialized.")
        # sys.exit(1)

    print("Starting PostgreSQL...")
    cmd = [pg_ctl_path, "start", "-D", PG_DATA, "-l", PG_LOG]
    try:
        subprocess.run(cmd, check=True)
        print("PostgreSQL started successfully.")
    except subprocess.CalledProcessError:
        print("Error: Failed to start PostgreSQL.")
        # sys.exit(1)
def adjust_addon_path():
    # Check if the application is running from a packaged environment
    if getattr(sys, 'frozen', False):  # PyInstaller sets 'frozen' attribute
        # Running from a packaged environment (e.g., PyInstaller)
        ADDONS_PATH = os.path.join(sys._MEIPASS, 'addons')  # Extracted path
        CUSTOM_ADDONS_PATH = os.path.join(sys._MEIPASS, 'custom_addons')
    else:
        # Running in a regular environment (i.e., not bundled)
        ADDONS_PATH = os.path.join(BASE_DIR, "addons")
        CUSTOM_ADDONS_PATH = os.path.join(BASE_DIR, "custom_addons")

    # Now dynamically set the addons_path for Odoo
    addons_path = f"{ADDONS_PATH},{CUSTOM_ADDONS_PATH}"
    print(addons_path)
    # Define the content of the odoo.conf file
    config_content = f"""
    [options]
    db_host = localhost
    db_port = 5435
    db_user = odoo_user
    db_password = password1234
    logfile = /var/log/odoo/odoo.log
    xmlrpc_port = 8069
    admin_passwd = $pbkdf2-sha512$600000$vdda6x1DyDknRAhByJlzTg$cVYtVcx7hBngGZgysCUSNirule67rILoBDayAFX72pg6NyK6L6S5kG9mTr/Z49k5wQhP5T.i7w6.MMMgI1HqXQ
    addons_path = {addons_path}
    """

    # Write to odoo.conf file
    ODOO_CONFIG = os.path.join(sys._MEIPASS, 'odoo.conf')
    with open(ODOO_CONFIG, 'w') as f:
        f.write(config_content)

    print(f"Configuration file written to {ODOO_CONFIG}")
def start_odoo():
    """Start Odoo."""
    if not os.path.exists(ODOO_BIN):
        print(f"Error: Odoo binary not found at {ODOO_BIN}.")
        sys.exit(1)

    print("Starting Odoo...")
    try:
        adjust_addon_path()
        subprocess.run([ ODOO_BIN, "-c", ODOO_CONFIG], check=True)
        print("Odoo started successfully.")
    except subprocess.CalledProcessError:
        print("Error: Failed to start Odoo.")

def get_hdd_serial():
    if platform.system() == "Windows":
        import win32api
        import win32file
        volume_info = win32file.GetVolumeInformation("C:\\")
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
    file_path = os.path.abspath(__file__)
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
    file_path = os.path.abspath(__file__)
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
    file_path = os.path.abspath(__file__)
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

if __name__ == "__main__":
    os_platform = platform.system().lower()

    # Ensure compatibility
    if os_platform not in ("windows", "linux"):
        print(f"Error: Unsupported platform {os_platform}.")
        sys.exit(1)
    if True:
        print("System verification successful. Application running...")
        # update_self()
        start_postgres()
        start_odoo()
    else:
        print("Unauthorized system detected. Exiting application.")
        exit()


