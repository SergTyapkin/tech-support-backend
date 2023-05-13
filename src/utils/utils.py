import datetime
import json
import os

from flask import jsonify, make_response, current_app
from flask_mail import Mail, Message

from src.constants import HTTP_OK


def str_between(string: (str, bytes), start: (str, bytes), end: (str, bytes), replace_to: (str, bytes) = None):
    end_idx = start_idx = string.find(start) + len(start)
    if isinstance(end, list):
        while end_idx < len(string) and string[end_idx] not in end:
            end_idx += 1
    else:
        end_idx = string.find(end)

    if replace_to is None:
        return string[start_idx: end_idx], start_idx, end_idx
    return string[:start_idx] + replace_to + string[end_idx:]


def read_config(filepath: str) -> dict:
    try:
        file = open(filepath, "r")
        config = json.load(file)
        file.close()

        if "db_password" not in config:
            config["db_password"] = os.environ["DATABASE_PASSWORD"]

        if "mail_password" not in config:
            config["mail_password"] = os.environ["MAIL_PASSWORD"]

        return config
    except Exception as e:
        print("Can't open and serialize json:", filepath)
        print(e)
        exit()


def read_app_config(filepath: str) -> dict:
    config = read_config(filepath)

    if config['save_images_to_db'] is False:
        if not os.path.isdir(config['save_images_folder']):
            print("Folder to saving images doesn't exists:", config['save_images_folder'])
            exit()

    return config


def count_lines(filename, chunk_size=4096) -> int:
    with open(filename) as file:
        return sum(chunk.count('\n') for chunk in iter(lambda: file.read(chunk_size), ''))


def html_prettify(headers: list, body: list, multilines: bool = False, row_onclick=None) -> str:
    if multilines:
        value_foo = lambda val: str(val).replace('\n', '<br>')
    else:
        value_foo = lambda val: str(val)

    thead = "<thead>\n"
    tbody = "<tbody>\n"
    for header in headers:
        thead += "<tr>\n"
        tbody += "<th>" + header + "</th>"
    thead += "</tr>\n"

    for row in body:
        tbody += "<tr" + ((" onclick=" + row_onclick(row[0]) + " style=\"cursor: pointer\"") if row_onclick else "") + ">\n"
        for value in row:
            tbody += "<td>" + value_foo(value) + "</td>"
        tbody += "</tr>\n"
    thead += "</thead>\n"
    tbody += "</tbody>\n"

    return "<table>\n" + thead + tbody + "</table>"

    # flex
    '''tbody = "<div class=\"grid-rows\">\n"
    trow = "<div class=\"grid-columns\">\n"
    for header in headers:
        trow += "<div>" + header + "</div>\n"
    trow += "</div>\n"
    tbody += trow

    for row in body:
        trow = "<div class=\"grid-columns\"" + ((" onclick=" + row_onclick(row[0]) + " style=\"cursor: pointer\"") if row_onclick else "") + ">\n"
        for value in row:
            trow += "<div>" + value_foo(value) + "</div>"
        trow += "</div>\n"
        tbody += trow

    return tbody + "</div>"'''


def jsonResponse(resp: dict or str, code: int = HTTP_OK):
    if isinstance(resp, str):
        resp = {"info": resp}

    return make_response(jsonify(resp), code)


def send_email(email, title, htmlBody):
    with current_app.app_context():
        mail = Mail()
        msg = Message(title, recipients=[email],
                      sender=(current_app.config['MAIL_DEFAULT_SENDER'], current_app.config['MAIL_DEFAULT_SENDER']))
        msg.html = htmlBody
        mail.send(msg)


def times_to_str(object):
    for key in object.keys():
        if type(object[key]) is datetime.time:
            object[key] = object[key].isoformat()
        if type(object[key]) is datetime.date:
            object[key] = object[key].isoformat()


def list_times_to_str(listWithTimedelta):
    for el in listWithTimedelta:
        times_to_str(el)
