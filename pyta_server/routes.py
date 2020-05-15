import os
import secrets
import psycopg2
from flask import request
from pyta_server import app, db
from pyta_server.models import Devices, Uploads

def commit_upload(upload):
        try:
            db.session.add(upload)
            db.session.commit()
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)

@app.route('/', methods=['POST'])
def receive():
    if isinstance(request.files, dict):
        unique_id = request.form.get('id')
        version = request.form.get('version')
        if db.session.query(Devices).get(unique_id):
            device = db.session.query(Devices).get(unique_id)
        else:
            device = Devices(device_uuid=unique_id, version=version)
        src_f = {k:v for k,v in request.files.items() if k != 'config'} #Excluding potential config file
        cfg_f = request.files.get('config')
        f_paths = []
        for f in list(src_f.values()):
            rand_hex = secrets.token_hex(8)
            _, src_ext = os.path.splitext(f.filename)
            src_n = rand_hex + src_ext
            src_path = os.path.join(app.root_path, 'static', 'source', unique_id)
            if not os.path.exists(src_path):
                os.makedirs(src_path)
            file_loc = os.path.join(src_path, src_n)
            f_paths.append(file_loc)
            f.save(file_loc)
        if cfg_f: # Non-default config file
            rand_hex = secrets.token_hex(8)
            _, cfg_ext = os.path.splitext(cfg_f.filename)
            cfg_n = rand_hex + cfg_ext
            cfg_path = os.path.join(app.root_path, 'static', 'config', unique_id)
            if not os.path.exists(cfg_path):
                os.makedirs(cfg_path)
            cfg_loc = os.path.join(cfg_path, cfg_n)
            cfg_f.save(cfg_loc)
            for path in f_paths:
                upload = Uploads(source=path, config=cfg_path, device=device)
                commit_upload(upload)
        else: #Default config was used
            for path in f_paths:
                upload = Uploads(source=path, device=device)
                commit_upload(upload)

        return "files successfully received"

    return "bad request"
