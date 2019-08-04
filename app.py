#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, Response, render_template, abort, request, redirect
from mimetypes import guess_type as guess_mime
from werkzeug.utils import secure_filename
import sys, os, time, lib

app = Flask(__name__)
app.url_map.strict_slashes = False
lib.root = os.path.realpath(__file__)[:-len("/app.py")]

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
        posts = lib.recent_posts()
        html = render_template("post.html.jinja", data = posts)
        return html

@app.route("/<path:path>")
def catch_all(path):
        if len(path.split("/")) >= 2:
                head = path.split("/")[0]
                if head in ["css", "js"]:
                        path = lib.root + "/static/" + lib.safe_path(path)
                        if os.path.exists(path):
                                response = Response("", 200)
                                response.set_data(lib.read_file(path))
                                response.headers["Content-Type"] = "%s; charset=UTF-8" % lib.guess_mime(path)
                                return response
                elif head == "post":
                        path = lib.root + "/content/" + lib.safe_path(path[5:])
                        if os.path.exists(path):
                                response = Response("", 200)
                                extension = path.split(".")[-1]
                                if extension in ["md", "markdown"]:
                                        post = lib.read_post(path)
                                        response.set_data(render_template("post.html.jinja", data = post))
                                        response.headers["Content-Type"] = "text/html; charset=UTF-8"
                                elif extension in ["png", "jpg", "pdf", "mp3", "mp4"]:
                                        response.set_data(lib.read_file(path))
                                        response.headers["Content-Type"] = "%s; charset=UTF-8" % lib.guess_mime(path)
                                else:
                                        abort(404)
                                return response
        abort(404)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000")