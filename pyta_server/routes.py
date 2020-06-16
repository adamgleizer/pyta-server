import os
import secrets
import psycopg2
import json
from flask import request
from pyta_server import app, db
from pyta_server.models import Devices, Uploads, Files, Errors


def update_db(entry):
    """Save the entry to the database."""
    try:
        db.session.add(entry)
        db.session.commit()
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)


def commit_errors(error_info, upload, file=None):
    """Make an Errors tuple and save it to the database."""
    error = Errors(upload=upload,
                   file=file,
                   msg_id=error_info.get('msg_id'),
                   msg=error_info.get('msg'),
                   symbol=error_info.get('symbol'),
                   category=error_info.get('category'),
                   line=error_info.get('line'))
    update_db(error)


@app.route('/', methods=['POST'])
def receive():
    """Receive POST request sent from user running PyTA."""
    if isinstance(request.files, dict):
        upload_time = request.form.get('time')  # Replace ':' with "-" because : is not a valid directory character
        time_stamp = upload_time.replace(":", "-")
        unique_id = request.form.get('id')
        version = request.form.get('version')
        errors = json.loads(request.form.get('errors'))

        if db.session.query(Devices).get(unique_id):  # Check if device already exists in database
            device = db.session.query(Devices).get(unique_id)
        else:
            device = Devices(device_uuid=unique_id, version=version)
            update_db(device)

        src_f = {k: v for k, v in request.files.items() if k != 'config'}  # Exclude potential config file
        cfg_f = request.files.get('config')
        f_paths = []
        cfg_loc = None  # initialized at None for when default config was used
        for f in list(src_f.values()):  # Saving files
            src_path = os.path.join(app.root_path, 'static', 'source', unique_id, time_stamp)
            if not os.path.exists(src_path):
                os.makedirs(src_path)
            file_loc = os.path.join(src_path, f.filename)
            f_paths.append(file_loc)
            f.save(file_loc)
        if cfg_f:  # Saving if non-default config file was used
            rand_hex = secrets.token_hex(8)
            _, cfg_ext = os.path.splitext(cfg_f.filename)
            cfg_n = rand_hex + cfg_ext
            cfg_path = os.path.join(app.root_path, 'static', 'config', unique_id, time_stamp)
            if not os.path.exists(cfg_path):
                os.makedirs(cfg_path)
            cfg_loc = os.path.join(cfg_path, cfg_n)
            cfg_f.save(cfg_loc)

        upload = Uploads(upload_time=upload_time, config=cfg_loc, device=device)
        if f_paths:  # User uploaded files along with errors
            for path in f_paths:
                file = Files(upload=upload, path=path)
                update_db(file)
                for error_codes in errors.values():
                    for error_info in error_codes:
                        # Matching errors to files they were present in
                        if (error_info.get('module') + '.py') == os.path.basename(os.path.normpath(path)):
                            commit_errors(error_info=error_info, upload=upload, file=file)
        else:  # User uploaded just errors
            for error_list in errors.values():
                for error_info in error_list:
                    commit_errors(error_info=error_info, upload=upload)

        return "files successfully received"

    return "bad request"
