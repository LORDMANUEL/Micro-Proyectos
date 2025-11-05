import os
from flask import Flask, request, redirect, url_for, send_from_directory, render_template_string

UPLOAD_FOLDER = 'uploads'

app = Flask(__name__, static_folder=UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), UPLOAD_FOLDER)

# HTML Template as a string
HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Local File Sharer</title>
  <style>
    body { font-family: Arial, sans-serif; background-color: #f4f4f9; color: #333; text-align: center; padding: 50px; }
    h1 { color: #444; }
    .container { background-color: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); display: inline-block; }
    form { margin-bottom: 20px; }
    input[type=file] { border: 1px solid #ddd; padding: 10px; border-radius: 4px; }
    input[type=submit] { background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
    input[type=submit]:hover { background-color: #0056b3; }
    .share-link { margin-top: 20px; }
    #shareLink { padding: 10px; width: 300px; border: 1px solid #ccc; border-radius: 4px; }
    button { background-color: #28a745; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; margin-left: 5px; }
    button:hover { background-color: #218838; }
  </style>
</head>
<body>
  <div class="container">
    <h1>Upload a File to Share Locally</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    {% if link %}
    <div class="share-link">
      <h2>Share this link:</h2>
      <input type="text" value="{{ link }}" id="shareLink" size="50" readonly>
      <button onclick="copyLink()">Copy Link</button>
    </div>
    <script>
    function copyLink() {
      var copyText = document.getElementById("shareLink");
      copyText.select();
      copyText.setSelectionRange(0, 99999); /* For mobile devices */
      document.execCommand("copy");
      alert("Link copied to clipboard!");
    }
    </script>
    {% endif %}
  </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            share_link = url_for('uploaded_file', filename=filename, _external=True)
            return render_template_string(HTML_TEMPLATE, link=share_link)

    return render_template_string(HTML_TEMPLATE, link=None)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(host='0.0.0.0', port=5006, debug=True)
