import os
import secrets
import psycopg2
import json
from flask import request
from pyta_server import app, db
from pyta_server.models import Devices, Uploads, Errors


def update_db(entry):
    try:
        db.session.add(entry)
        db.session.commit()
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)


def commit_errors(error_info, upload=None):
    error = Errors(file=upload,
                   msg_id=error_info.get('msg_id'),
                   symbol=error_info.get('symbol'),
                   msg=error_info.get('msg'),
                   category=error_info.get('category'),
                   line=error_info.get('line'))
    update_db(error)


@app.route('/', methods=['POST'])
def receive():
    if isinstance(request.files, dict):
        upload_time = request.form.get('time')  # Replace ':' with "-" because : is not a valid directory key
        time_stamp = upload_time.replace(":", "-")
        unique_id = request.form.get('id')
        version = request.form.get('version')
        errors = json.loads(request.form.get('errors'))
        if db.session.query(Devices).get(unique_id):
            device = db.session.query(Devices).get(unique_id)
        else:
            device = Devices(device_uuid=unique_id, version=version)
            update_db(device)
        src_f = {k: v for k, v in request.files.items() if k != 'config'}  # Excluding potential config file
        cfg_f = request.files.get('config')
        f_paths = []
        for f in list(src_f.values()):
            src_path = os.path.join(app.root_path, 'static', 'source', unique_id, time_stamp)
            if not os.path.exists(src_path):
                os.makedirs(src_path)
            file_loc = os.path.join(src_path, f.filename)
            f_paths.append(file_loc)
            f.save(file_loc)
        if cfg_f: # Non-default config file
            rand_hex = secrets.token_hex(8)
            _, cfg_ext = os.path.splitext(cfg_f.filename)
            cfg_n = rand_hex + cfg_ext
            cfg_path = os.path.join(app.root_path, 'static', 'config', unique_id, time_stamp)
            if not os.path.exists(cfg_path):
                os.makedirs(cfg_path)
            cfg_loc = os.path.join(cfg_path, cfg_n)
            cfg_f.save(cfg_loc)

            for path in f_paths:
                upload = Uploads(upload_time=upload_time, source=path, config=cfg_path, device=device)
                update_db(upload)
                for error_info in errors.values():
                    if (error_info.get('module') + '.py') == os.path.basename(os.path.normpath(path)):
                        commit_errors(error_info, upload)
        else:  # Default config was used
            for path in f_paths:
                upload = Uploads(upload_time=upload_time, source=path, device=device)
                update_db(upload)
                for error_list in errors.values():
                    for error_info in error_list:
                        if (error_info.get('module') + '.py') == os.path.basename(os.path.normpath(path)):
                            commit_errors(error_info, upload)
        return "files successfully received"

    return "bad request"
