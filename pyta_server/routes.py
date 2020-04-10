import os
import secrets
import psycopg2
from flask import request
from pyta_server import app, db
from pyta_server.models import Submissions, Uploads

@app.route('/', methods=['POST'])
def receive():
    rand_hex = secrets.token_hex(8)
    src_f = request.files
    cfg_f = request.files.get('config')
    ident = request.form.get('id')
    f_paths = []
    if src_f is not None and cfg_f is not None:
        for f in list(src_f.values())[:-1]: # Last value is cfg, handled separately
            _, src_ext = os.path.splitext(f.filename)
            src_n = rand_hex + src_ext
            src_path = os.path.join(app.root_path, 'static', 'source', src_n)
            f_paths.append(src_path)
            f.save(src_path)
            rand_hex = secrets.token_hex(8)

        _, cfg_ext = os.path.splitext(cfg_f.filename)
        cfg_n = rand_hex + cfg_ext
        cfg_path = os.path.join(app.root_path, 'static', 'config', cfg_n)
        cfg_f.save(cfg_path)

        submission = Submissions(identifier=ident, config=cfg_path)
        for path in f_paths:
            upload = Uploads(source=path, submission=submission)
            try:
                db.session.add(upload)
                db.session.commit()

            except (Exception, psycopg2.Error) as error:
                print("Error while connecting to PostgreSQL", error)

        return "files successfully received"

    return "bad request"
