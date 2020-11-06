from flask import (
    Flask,
    flash,
    render_template,
    redirect,
    url_for,
    session,
    request,
    send_from_directory,
    abort,
)
from flask import Response, Blueprint
from werkzeug.serving import run_simple

import threading
import datetime
import imutils
import time

import cv2
import numpy as np
import imagezmq


class ReverseProxied(object):
    def __init__(self, app, script_name=None, scheme=None, server=None):
        self.app = app
        self.script_name = script_name
        self.scheme = scheme
        self.server = server

    def __call__(self, environ, start_response):
        script_name = environ.get("HTTP_X_SCRIPT_NAME", "") or self.script_name
        if script_name:
            environ["SCRIPT_NAME"] = script_name
            path_info = environ["PATH_INFO"]
            if path_info.startswith(script_name):
                environ["PATH_INFO"] = path_info[len(script_name) :]
        scheme = environ.get("HTTP_X_SCHEME", "") or self.scheme
        if scheme:
            environ["wsgi.url_scheme"] = scheme
        server = environ.get("HTTP_X_FORWARDED_SERVER", "") or self.server
        if server:
            environ["HTTP_HOST"] = server
        return self.app(environ, start_response)


outFrame = None
lock = threading.Lock()

app = Flask(__name__)
# app.wsgi_app = ReverseProxied(app.wsgi_app, script_name="/overlord")

imageHub = imagezmq.ImageHub()


@app.route("/")
def index():
    return render_template("index.html")


def process_feed():
    global imageHub, outFrame, lock

    while True:
        (rpiName, image) = imageHub.recv_image()
        imageHub.send_reply(b"OK")

        timestamp = datetime.datetime.now()
        cv2.putText(
            image,
            timestamp.strftime("%A %d %B %Y %I:%M:%S%p"),
            (10, image.shape[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.35,
            (0, 0, 255),
            1,
        )

        with lock:
            outFrame = image.copy()


def generate():
    global outFrame, lock

    while True:
        with lock:
            if outFrame is None:
                outFrame = get_blank_image()

            (flag, encodedImage) = cv2.imencode(".jpg", outFrame)

            if not flag:
                continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + bytearray(encodedImage) + b"\r\n"
            )


def get_blank_image():
    blank_image = np.zeros((400, 400, 3), np.uint8)
    timestamp = datetime.datetime.now()
    cv2.putText(
        blank_image,
        timestamp.strftime("%A %d %B %Y %I:%M:%S%p"),
        (10, blank_image.shape[0] - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.35,
        (0, 0, 255),
        1,
    )

    return blank_image


@app.route("/video_feed")
def video_feed():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    t = threading.Thread(target=process_feed)
    t.daemon = True
    t.start()

    app.run(host="0.0.0.0", port=9000, debug=True, threaded=True, use_reloader=False)