import os
import secrets
import psycopg2
import json
import datetime
import re

from flask import request
from pyta_server import app, db
from pyta_server.models import Devices, Uploads, Files, Errors
from typing import Dict, List, Any

INIT_SRC_PATH = os.path.join(app.root_path, 'static', 'source')
INIT_CFG_PATH = os.path.join(app.root_path, 'static', 'config')


@app.route('/', methods=['POST'])
def receive():
    """Receive POST request sent from user running PyTA."""
    upload_time = str(datetime.datetime.utcnow())
    time_stamp = upload_time.replace(":", "-")  # Replace ':' with "-" because : is not a valid directory character
    unique_id = request.form.get('id')
    version = request.form.get('version')

    if db.session.query(Devices).get(unique_id):  # Check if device already exists in database
        device = db.session.query(Devices).get(unique_id)
    else:
        device = Devices(device_uuid=unique_id, version=version)
        update_db(device)

    src_files = request.files.values()
    payload = json.loads(request.form.get('payload'))
    errors = payload.get('errors')
    cfg = payload.get('cfg')
    cfg_loc = None  # initialized at None for when default config was used
    f_paths = save_files(src_files, unique_id, time_stamp)
    if cfg:
        cfg_loc = save_cfg_as_json(cfg, unique_id, time_stamp)

    upload = Uploads(upload_time=upload_time, config=cfg_loc, device=device)
    if f_paths:  # User uploaded files
        for path in f_paths:
            file = Files(upload=upload, path=path)
            update_db(file)
            # 'errors' is an empty dict if the User only uploaded files
            for error_codes in errors.values():
                for error_info in error_codes:
                    # Matching errors to files they were present in
                    if (error_info.get('module') + '.py') == os.path.basename(os.path.normpath(path)):
                        commit_errors(error_info=error_info, upload=upload, file=file)
    else:  # User uploaded just errors
        for error_list in errors.values():
            for error_info in error_list:
                commit_errors(error_info=error_info, upload=upload)

    return "Data submission successfully received"


def update_db(entry) -> None:
    """Save the entry to the database."""
    try:
        db.session.add(entry)
        db.session.commit()
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)


def commit_errors(error_info: Dict[str, str], upload, file=None) -> None:
    """Make an Errors tuple and save it to the database."""
    error = Errors(upload=upload,
                   file=file,
                   msg_id=error_info.get('msg_id'),
                   msg=error_info.get('msg'),
                   symbol=error_info.get('symbol'),
                   category=error_info.get('category'),
                   line=error_info.get('line'))
    update_db(error)


def enumerate_file_name(filename: str) -> str:
    """Enumerates filenames to avoid over-writes when the user
    uploads files with the same name."""
    pattern = re.compile("(\d+)")
    # Counter is the '(n)' portion of an enumerated filename
    f_name, counter = filename[:-3], filename[-3:]
    if pattern.match(counter):
        curr_count = int(counter[1])
        new_enum = " (" + str(curr_count + 1) + ").py"
        return f_name + new_enum
    else:
        return f_name + " (1).py"


def save_files(src_files, unique_id: str, time_stamp: str) -> List[str]:
    """Saves the files from the POST request and returns a list of
    the paths they were saved at."""
    f_paths = []
    for f in src_files:
        src_path = os.path.join(INIT_SRC_PATH, unique_id, time_stamp)
        if not os.path.exists(src_path):
            os.makedirs(src_path)
        curr_name = f.filename
        file_loc = os.path.join(src_path, curr_name)
        while os.path.exists(file_loc):
            file_loc = os.path.join(src_path, enumerate_file_name(curr_name))
        f_paths.append(file_loc)
        f.save(file_loc)
    return f_paths


def save_cfg_as_json(cfg, unique_id: str, time_stamp: str) -> str:
    """Saves the configuration file in a JSON format and returns
    the path it was saved at."""
    rand_hex = secrets.token_hex(8)
    cfg_n = rand_hex + '.json'
    cfg_path = os.path.join(INIT_CFG_PATH, unique_id, time_stamp)
    if not os.path.exists(cfg_path):
        os.makedirs(cfg_path)
    cfg_loc = os.path.join(cfg_path, cfg_n)
    cfg_f = open(cfg_loc, 'w')
    json.dump(cfg, cfg_f, indent=4)
    cfg_f.close()
    return cfg_loc
