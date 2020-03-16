import os
import secrets
import psycopg2
from flask import request
from pyta_server import app, db
from pyta_server.models import Uploads

@app.route('/', methods=['POST'])
def receive():
    rand_hex = secrets.token_hex(8)
    src_f = request.files['source']
    cfg_f = request.files['config']
    _, src_ext = os.path.splitext(src_f.filename)
    _, cfg_ext = os.path.splitext(cfg_f.filename)
    src_n = rand_hex + src_ext
    cfg_n = rand_hex + cfg_ext
    src_path = os.path.join(app.root_path, 'static', 'source', src_n)
    cfg_path = os.path.join(app.root_path, 'static', 'config', cfg_n)
    src_f.save(src_path)
    cfg_f.save(cfg_path)

    upload= Uploads(source=src_path, config =cfg_path, identifier="create unique on install")
    try:
        db.session.add(upload)
        db.session.commit()

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)

    return "files successfully received"
