import subprocess
import logging
from flask import Flask, jsonify

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

FIRESTICK_IP = "192.168.1.99"
FIRESTICK_PORT = 5555
ADB_TARGET = f"{FIRESTICK_IP}:{FIRESTICK_PORT}"

def run_adb_reboot():
    """Connect to Firestick via ADB, trigger reboot, then disconnect."""
    commands = [
        ["adb", "connect", ADB_TARGET],
        ["adb", "-s", ADB_TARGET, "shell", "setprop", "sys.powerctl", "reboot"],
        ["adb", "disconnect", ADB_TARGET],
    ]
    for cmd in commands:
        logging.info(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        logging.info(f"stdout: {result.stdout.strip()}")
        if result.returncode != 0:
            logging.error(f"Command failed: {result.stderr.strip()}")
            return False, result.stderr.strip()
    return True, "Reboot triggered successfully"

@app.route("/reboot", methods=["POST"])
def reboot():
    success, message = run_adb_reboot()
    status_code = 200 if success else 500
    return jsonify({"success": success, "message": message}), status_code

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8765)