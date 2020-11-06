from imutils.video import VideoStream
import imagezmq
import socket
import time
import cv2

sender = imagezmq.ImageSender(connect_to="tcp://127.0.0.1:5555")

rpiName = socket.gethostname()
vs = VideoStream(src=0, resolution=(320, 240)).start()
time.sleep(2.0)

while True:
    frame = vs.read()
    sender.send_image(rpiName, frame)