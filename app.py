#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, Response, render_template, abort, request, redirect
from mimetypes import guess_type as guess_mime
from werkzeug.utils import secure_filename
import sys, os, time, markdown, lib

app = Flask(__name__)
app.url_map.strict_slashes = False
root = os.path.realpath(__file__)[:-len("/app.py")]

# エラーを除きデフォルトログを無効化する
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.after_request
def log_access(response):
        sys.stdout.write("[{0}] {1} - {2} - {3} {4}\n".format(
                time.strftime("%y/%m/%d %H:%M:%S"),
                lib.get_ip(),
                response.status,
                request.method,
                request.path
        ))
        sys.stdout.flush()
        return response

@app.errorhandler(404)
def handle_404(error):
        response = Response("404 ファイルが見つかりませんでした", 404)
        return response

@app.route("/")
def route_index():
        html = """%s""" % ("".join([x*80 for x in list("0123456789")]))
        html = render_template("base.html.jinja", data = {
                "content" : html
                })
        return html

@app.route("/<path:path>")
def catch_all(path):
        path = path.split("/")
        if len(path) >= 2:
                if path[0] in ["css", "js"]:
                        return get_resource("/".join(path))
        abort(404)

def get_resource(resource):
        path = root + "/static/" + lib.safe_path(resource)
        if os.path.exists(path):
                response = Response("", 200)
                response.set_data(lib.read_file(path))
                response.headers["Content-Type"] = "%s; charset=UTF-8" % lib.guess_mime(path)
                return response
        abort(404)

if __name__ == '__main__':
    app.run()