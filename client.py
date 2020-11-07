from imagezmq.imagezmq import ImageSender
from imutils.video import VideoStream
import imagezmq
import socket
import time
import cv2
import sys

from functools import wraps
import argparse
import errno
import os
import signal


class TimeoutError(Exception):
    pass


def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator


def pushFrames(args):
    try:
        print("Attempting to connect to imageHub")
        sender = imagezmq.ImageSender(
            connect_to="tcp://{}:{}".format(args.ip, args.port)
        )
        print("Connected to image hub")

        rpiName = socket.gethostname()

        print("Starting video stream")
        if args.use_pi:
            vs = VideoStream(usePiCamera=True).start()
        else:
            vs = VideoStream(src=0, resolution=(320, 240)).start()
        time.sleep(2.0)

        print("Begin sending frames")
        while True:
            try:
                readAndSend(rpiName, vs, sender)
            except TimeoutError as err:
                print("Timed Out sending frame to remote", err)
                vs.stop()
                sender.close()
                print("Waiting for 5s before reconnecting...")
                time.sleep(5.0)
                print("Attempt reconnect")
                pushFrames()
    except:
        print("error: ", sys.exc_info()[0])
        raise


@timeout(5)
def readAndSend(hostName: str, vs: VideoStream, sender: ImageSender):
    frame = vs.read()
    sender.send_image(hostName, frame)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--use_pi",
        action="store_true",
        help="Whether to use Pi camera or system camera",
    )
    ap.add_argument(
        "-i", "--ip", type=str, required=True, help="ip adddress of remote host"
    )
    ap.add_argument(
        "-p", "--port", type=int, default=5555, help="receiver port of remote host"
    )
    args = ap.parse_args()

    pushFrames(args)