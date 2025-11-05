from flask import Flask, render_template, request
import subprocess

app = Flask(__name__)

def run_ping_test(host='8.8.8.8'):
    """Runs a simple ping test."""
    try:
        result = subprocess.check_output(['ping', '-c', '4', host], universal_newlines=True, stderr=subprocess.STDOUT)
        return f"Ping test to {host} successful:\n\n{result}"
    except subprocess.CalledProcessError as e:
        return f"Ping test to {host} failed:\n\n{e.output}"
    except FileNotFoundError:
        return "Error: 'ping' command not found. This tool is intended for Windows, but can run on Linux/macOS."


def run_tracert_test(host='8.8.8.8'):
    """Runs a traceroute test."""
    command = ['tracert', host] if os.name == 'nt' else ['traceroute', host]
    try:
        result = subprocess.check_output(command, universal_newlines=True, stderr=subprocess.STDOUT)
        return f"Traceroute to {host} successful:\n\n{result}"
    except subprocess.CalledProcessError as e:
        return f"Traceroute to {host} failed:\n\n{e.output}"
    except FileNotFoundError:
        return f"Error: '{command[0]}' command not found. This tool is intended for Windows."

def run_sfc_scan():
    """Runs the System File Checker (requires admin rights)."""
    if os.name != 'nt':
        return "SFC /scannow is a Windows-specific command and requires Administrator privileges."
    try:
        result = subprocess.check_output(['sfc', '/scannow'], universal_newlines=True, stderr=subprocess.STDOUT)
        return f"System File Checker results:\n\n{result}"
    except subprocess.CalledProcessError as e:
        return f"SFC /scannow failed. It must be run with Administrator privileges.\n\n{e.output}"

def run_chkdsk(drive='C:'):
    """Runs Check Disk in read-only mode (requires admin rights)."""
    if os.name != 'nt':
        return "CHKDSK is a Windows-specific command and requires Administrator privileges."
    try:
        result = subprocess.check_output(['chkdsk', drive], universal_newlines=True, stderr=subprocess.STDOUT)
        return f"Check Disk results for drive {drive}:\n\n{result}"
    except subprocess.CalledProcessError as e:
        return f"CHKDSK failed. It must be run with Administrator privileges.\n\n{e.output}"

TESTS = {
    'ping': {'name': 'Ping Google DNS', 'function': run_ping_test},
    'tracert': {'name': 'Traceroute to Google DNS', 'function': run_tracert_test},
    'sfc': {'name': 'System File Checker (Admin Required)', 'function': run_sfc_scan},
    'chkdsk': {'name': 'Check Disk (Read-Only, Admin Required)', 'function': run_chkdsk}
}

@app.route('/', methods=['GET'])
def index():
    return render_template('wt_index.html', tests=TESTS)

@app.route('/run_test', methods=['POST'])
def run_test():
    test_key = request.form.get('test')
    if test_key in TESTS:
        test_info = TESTS[test_key]
        test_function = test_info['function']
        result_output = test_function()
        return render_template('wt_results.html', test_name=test_info['name'], result=result_output)
    return redirect(url_for('index'))

if __name__ == '__main__':
    import os
    app.run(host='0.0.0.0', port=5010, debug=True)
