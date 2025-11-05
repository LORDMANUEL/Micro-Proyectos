from flask import Flask, render_template, request, make_response
from jinja2 import Environment, FileSystemLoader
import os

app = Flask(__name__)

# Set up Jinja2 environment to load templates from a 'scripts' directory
script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')
jinja_env = Environment(loader=FileSystemLoader(script_dir))

# A dictionary to define the templates and their required parameters
SCRIPT_TEMPLATES = {
    'create_folder': {
        'name': 'Create Folder',
        'template': 'create_folder.bat.jinja',
        'params': ['folder_name']
    },
    'map_drive': {
        'name': 'Map Network Drive',
        'template': 'map_network_drive.bat.jinja',
        'params': ['drive_letter', 'network_path']
    },
    'set_static_ip': {
        'name': 'Set Static IP Address',
        'template': 'set_static_ip.bat.jinja',
        'params': ['interface_name', 'ip_address', 'subnet_mask', 'gateway']
    }
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        script_key = request.form.get('script_selection')
        if script_key in SCRIPT_TEMPLATES:
            template_info = SCRIPT_TEMPLATES[script_key]
            template = jinja_env.get_template(template_info['template'])

            # Collect parameters from the form
            context = {param: request.form.get(param) for param in template_info['params']}

            # Render the script
            generated_script = template.render(context)

            return render_template('ws_result.html', script=generated_script, filename=f"{script_key}.bat")

    return render_template('ws_index.html', scripts=SCRIPT_TEMPLATES)

@app.route('/download/<filename>')
def download_script(filename):
    script_content = request.args.get('content')
    response = make_response(script_content)
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-Type"] = "text/plain"
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009, debug=True)
