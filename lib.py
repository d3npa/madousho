#!/usr/bin/env python3
from flask import request
from werkzeug.utils import secure_filename
from string import printable
from mimetypes import guess_type
import re, os, markdown, time

# https://stackoverflow.com/a/93029
control_chars = "".join(map(chr, list(range(0,32)) + list(range(127,160))))
re_no_cc = re.compile("[%s]" % re.escape(control_chars))

root = ""
keywords = {
        "HEADER_HEAD" : "START_HEADERS",
        "HEADER_TAIL" : "END_HEADERS"
}


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

def read_post(path):
        # ファイルパスから記事をパース、ヘッダーを辞書で返し内容をMarkdownとして返す。
        # 不正なパスの場合エラー吹きますので呼び出す前にチェックしましょう。
        headers = {}
        contents = ""
        with open(path, "r") as f:
                parse_headers = False
                line_index = 0
                data = [line[:-1] for line in f.readlines()]
                if data[line_index] == keywords["HEADER_HEAD"]:
                        parse_headers = True
                while parse_headers:
                        line_index += 1
                        line = data[line_index]
                        if line:
                                if line == keywords["HEADER_TAIL"]:
                                        parse_headers = False
                                        line_index += 1
                                        break
                                line = line.split(": ")
                                headers.update({line[0] : line[1]})
                contents = "\n".join(data[line_index:])
        # print(root, path)
        return [{
                "link" : path.replace(root + "/content/", "/post/"),
                "headers" : headers,
                "contents" : markdown.markdown(contents, extensions=['extra'])
        }]

def recent_posts(directory=""):
        files = []
        directory = root + "/content" + directory
        def discover_files(directory, files):
                for file in os.listdir(directory):
                        file = "/".join([directory, file])
                        if os.path.isfile(file) and file[-3:] == ".md":
                                files.append(file)
                        if os.path.isdir(file):
                                discover_files(file, files)
        def order_file(file):
                with open(file, "r") as f:
                        if f.readline()[:-1] == keywords["HEADER_HEAD"]:
                                post = read_post(file)[0]
                                if "headers" in post and "Date" in post["headers"]:
                                        try:
                                                return -time.mktime(time.strptime(post["headers"]["Date"], "%Y/%m/%d"))
                                        except ValueError:
                                                print("(%s)「Date」ヘッダーをパースできませんでした（形式の問題？）" % file)
                                                return 0
                        return 0
        discover_files(directory, files)
        files = sorted(files, key=order_file)
        posts = []
        for file in files[:5]:
                post = read_post(file)
                path = file[len(directory):-len(file.split("/")[-1])]                                           # ルートとファイル名を含めず
                post[0]["contents"] = post[0]["contents"].replace("src=\".res/", "src=\"/post%s.res/" % path)   # 画像リンクを修正する
                posts += post
        return posts