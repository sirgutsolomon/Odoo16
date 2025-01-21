import os
import subprocess
import sys

# Define base directory for portable setup
if getattr(sys, 'frozen', False):  # Check if running from a packaged executable
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

PG_BIN = os.path.join(BASE_DIR, "portableodoo", "postgres", "bin")
PG_DATA = os.path.join(BASE_DIR, "portableodoo", "postgres", "data")
PG_LOG = os.path.join(BASE_DIR, "portableodoo", "postgres", "logfile.log")

# Paths for Odoo binary and configuration (bundled in the packaged application)
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
        sys.exit(1)

    print("Starting PostgreSQL...")
    try:
        cmd = [pg_ctl_path, "start", "-D", PG_DATA, "-l", PG_LOG]
        subprocess.run(cmd, check=True)
        print("PostgreSQL started successfully.")
    except subprocess.CalledProcessError:
        print("Error: Failed to start PostgreSQL.")
        sys.exit(1)

# Ensure the Odoo binary and config file exist
if not os.path.exists(ODOO_BIN):
    print(f"Error: Odoo binary not found at {ODOO_BIN}.")
    sys.exit(1)

if not os.path.exists(ODOO_CONFIG):
    print(f"Error: Odoo configuration file not found at {ODOO_CONFIG}.")
    sys.exit(1)

# Ensure PostgreSQL is running
# start_postgres()

# Run Odoo with the configuration file
print("Starting Odoo with config...")

# Debugging: Log Odoo binary and config
print(f"Running Odoo from: {ODOO_BIN}")
print(f"Using config file: {ODOO_CONFIG}")

try:
    subprocess.run([sys.executable, ODOO_BIN, "-c", ODOO_CONFIG], check=True)
    print("Odoo started successfully.")
except subprocess.CalledProcessError as e:
    print(f"Error while starting Odoo: {e}")
    sys.exit(1)
