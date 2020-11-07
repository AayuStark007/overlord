from imutils.video import VideoStream
import imagezmq
import socket
import time
import cv2
import sys


def pushFrames():
    try:
        print("Attempting to connect to imageHub")
        sender = imagezmq.ImageSender(connect_to="tcp://127.0.0.1:5555")
        print("Connected to image hub")

        rpiName = socket.gethostname()

        print("Starting video stream")
        vs = VideoStream(src=0, resolution=(320, 240)).start()
        # vs = VideoStream(usePiCamera=True).start()
        time.sleep(2.0)

        print("Begin sending frames")
        while True:
            frame = vs.read()
            sender.send_image(rpiName, frame)
    except:
        print("error:")
        raise


if __name__ == "__main__":
    pushFrames()