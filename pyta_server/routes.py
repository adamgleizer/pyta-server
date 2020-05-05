import os
import secrets
import psycopg2
from flask import request
from pyta_server import app, db
from pyta_server.models import Submissions, Uploads

def commit_upload(upload):
        try:
            db.session.add(upload)
            db.session.commit()
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)

@app.route('/', methods=['POST'])
def receive():
    if isinstance(request.files, dict):
        uuid = request.form.get('id')
        submission = Submissions(device_uuid=uuid, version='current') #Not sure how to find current version from __init__, ask David
        src_f = {k:v for k,v in request.files.items() if k != 'config'} #Excluding potential config file
        cfg_f = request.files.get('config')
        f_paths = []
        for f in list(src_f.values()):
            rand_hex = secrets.token_hex(8)
            _, src_ext = os.path.splitext(f.filename)
            src_n = rand_hex + src_ext
            src_path = os.path.join(app.root_path, 'static', 'source', src_n)
            f_paths.append(src_path)
            f.save(src_path)
        if cfg_f: # Non-default config file
            rand_hex = secrets.token_hex(8)
            _, cfg_ext = os.path.splitext(cfg_f.filename)
            cfg_n = rand_hex + cfg_ext
            cfg_path = os.path.join(app.root_path, 'static', 'config', cfg_n)
            cfg_f.save(cfg_path)
            for path in f_paths:
                upload = Uploads(source=path, config=cfg_path, submission=submission)
                commit_upload(upload)
        else: #Default config was used
            for path in f_paths:
                upload = Uploads(source=path, submission=submission)
                commit_upload(upload)

        return "files successfully received"

    return "bad request"
