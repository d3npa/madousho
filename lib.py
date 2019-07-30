#!/usr/bin/env python3
from flask import request
from werkzeug.utils import secure_filename
from string import printable
from mimetypes import guess_type
import re

# https://stackoverflow.com/a/93029
control_chars = "".join(map(chr, list(range(0,32)) + list(range(127,160))))
re_no_cc = re.compile("[%s]" % re.escape(control_chars))

def get_ip():
        # クライアントのIPアドレスを返す。
        return request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr

def safe_path(path):
        # ファイルパスから不正文字を省く。
        path = re_no_cc.sub("", path)
        path = path.replace("/../", "/./").replace("/./", "/")
        return path

def guess_mime(path):
        # ファイルのMIMEタイプを推測する。
        extension = path.split(".")[-1]
        if extension in ["md", "markdown"]:
                return "text/html"
        else:
                return guess_type(path)[0]
                
def read_file(path):
        # ファイルを読み込もうとする。
        # 不正なパスの場合エラー吹きますので呼び出す前にチェックしましょう。
        with open(path, "rb") as f:
                return f.read()

