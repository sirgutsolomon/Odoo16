import os
import location
import platform
import subprocess
import sys
import ctypes
# Get the directory where the executable is located
if getattr(sys, 'frozen', False):  # Check if running from a packaged executable
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# C:\Users\User\OneDrive\Desktop\odoo\Odoo16\dist\pgsql\bin
# PG_BIN = "C:\\Users\\User\OneDrive\Desktop\main\Odoo16\dist\database\\bin\pg_ctl.exe"
PG_BIN = os.path.join(BASE_DIR, "pgsql","bin","pg_ctl.exe")

PG_DATA = os.path.join(BASE_DIR, "data","pgsql","data")
PG_LOG = os.path.join(BASE_DIR,  "data","pgsql", "logfile.log")
# ODOO_BIN = os.path.join(BASE_DIR,"odoo-bin")
# ODOO_CONFIG = os.path.join(BASE_DIR,"odoo.conf")
ODOO_BIN = os.path.join(sys._MEIPASS, 'odoo-bin')
ODOO_CONFIG = os.path.join(sys._MEIPASS, 'odoo.conf')
def start_postgres():
    """Start PostgreSQL."""
    pg_ctl_path = PG_BIN
    if not os.path.exists(pg_ctl_path):
        print(f"Error: pg_ctl not found at {pg_ctl_path}.")
        sys.exit(1)

    if not os.path.exists(PG_DATA):
        print("Error: PostgreSQL data directory not initialized.")

    print("Starting PostgreSQL...")
    cmd = [pg_ctl_path, "start", "-D", PG_DATA, "-l", PG_LOG]
    try:
        subprocess.run(cmd, check=True)
        print("PostgreSQL started successfully.")
    except subprocess.CalledProcessError:
        print("Error: Failed to start PostgreSQL.")

def adjust_addon_path():
    if getattr(sys, 'frozen', False):

        ADDONS_PATH = os.path.join(sys._MEIPASS, 'addons')
        CUSTOM_ADDONS_PATH = os.path.join(sys._MEIPASS, 'custom_addons')
    else:

        ADDONS_PATH = os.path.join(BASE_DIR, "addons")
        CUSTOM_ADDONS_PATH = os.path.join(BASE_DIR, "custom_addons")

    addons_path = f"{ADDONS_PATH},{CUSTOM_ADDONS_PATH}"
    config_content = f"""
    [options]
    db_host = localhost
    db_port = 5432
    db_user = odoo_user
    db_password = password1234
    logfile = \\var\\log\\odoo\\odoo.log
    xmlrpc_port = 8069
    admin_passwd = $pbkdf2-sha512$600000$vdda6x1DyDknRAhByJlzTg$cVYtVcx7hBngGZgysCUSNirule67rILoBDayAFX72pg6NyK6L6S5kG9mTr/Z49k5wQhP5T.i7w6.MMMgI1HqXQ
    addons_path = {addons_path}
    """

    ODOO_CONFIG = os.path.join(sys._MEIPASS, 'odoo.conf')
    with open(ODOO_CONFIG, 'w') as f:
        f.write(config_content)

    print(f"Configuration file written to {ODOO_CONFIG}")
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def start_odoo():
    if not is_admin():
        print("Requesting admin privileges...")
        # Restart the script with admin privileges
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()
    """Start Odoo."""
    if not os.path.exists(ODOO_BIN):
        print(f"Error: Odoo binary not found at {ODOO_BIN}.")
        sys.exit(1)

    print("Starting Odoo...")
    try:
        adjust_addon_path()
        # python_exe = os.path.join(os.path.dirname(sys.executable), 'python.exe')
        subprocess.run(["python", ODOO_BIN, "-c", ODOO_CONFIG], check=True)
        print("Odoo started successfully.")

    except subprocess.CalledProcessError:
        print("Error: Failed to start Odoo.")


def open_browser():
    """Open the default browser to localhost:8069."""
    if platform.system().lower() == "linux":
        subprocess.run(["xdg-open", "http://localhost:8069"])
    elif platform.system().lower() == "windows":
        subprocess.run(["start", "http://localhost:8069"], shell=True)
if __name__ == "__main__":
    os_platform = platform.system().lower()

    # Ensure compatibility
    if os_platform not in ("windows", "linux"):
        print(f"Error: Unsupported platform {os_platform}.")
        sys.exit(1)
    location.update_self()
    if location.verify_self:
        print("System verification successful. Application running...")
        start_postgres()
        open_browser()
        start_odoo()

    else:
        print("Unauthorized system detected. Exiting application.")
        exit()


# SYSTEM_HASH: ALLOW_FIRST_TIME
