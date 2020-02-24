import os
import secrets
from flask import redirect, url_for, request
from pyta_server import app

#Current directories for storing source and config files
dirs = \
    {
    'source': os.path.join(app.root_path, 'static/source'),
    'config': os.path.join(app.root_path, 'static/config')
    }

@app.route('/', methods=['GET', 'POST'])
def receive():
    if request.method == 'POST':
        for f_type in request.files.keys():
            user_f = request.files[f_type]
            rand_hex = secrets.token_hex(8)
            _, f1_ext = os.path.splitext(user_f.filename)
            fn = rand_hex + f1_ext
            f_path = os.path.join(dirs[f_type], fn)
            user_f.save(f_path)

        return redirect((url_for('receive')))
    else:
        return ""