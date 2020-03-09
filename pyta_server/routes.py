import os
import secrets
import psycopg2
from flask import request
from pyta_server import app, db
from pyta_server.models import Uploads

@app.route('/', methods=['POST'])
def receive():
    if request.method == 'POST':
        dirs = {'source':'', 'config':''}
        rand_hex = secrets.token_hex(8)
        for f_type in request.files.keys():
            user_f = request.files[f_type]
            _, f1_ext = os.path.splitext(user_f.filename)
            fn = rand_hex + f1_ext
            f_path = os.path.join(app.root_path, f'static\{f_type}', fn)
            user_f.save(f_path)
            dirs[f_type] = f_path

        upload = Uploads(source=dirs['source'], config =dirs['config'])
        try:
            db.session.add(upload)
            db.session.commit()

        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)

        return "files successfully received"

    else:
        return "null"
