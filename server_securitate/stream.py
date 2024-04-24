
from datetime import datetime, timedelta, timezone, tzinfo
from Crypto.PublicKey import RSA
from .rsa import *
import cv2
import zmq
import base64
import numpy as np
import threading
import random
from django.views.decorators import gzip
from django.http import StreamingHttpResponse

class Stream:
    def __init__(self, port, uid):
        self.port = port
        self.uid = uid
        self.stream_active = False
        self.image = None
    
    def start_stream(self):
        self.stream_active = True
        print("apel")
        x = threading.Thread(target = self.stream_aux, args=(self.port, self.uid))
        x.start()
        
    def stop_stream(self):
        self.stream_active = False
        
    def get_image(self):
        if self.image is None:
            return None
        _, jpeg = cv2.imencode('.jpg', self.image)
        return jpeg.tobytes()
    
    def stream_aux(self, port, uid):
        context = zmq.Context()
        footage_socket = context.socket(zmq.SUB)
        footage_socket.bind('tcp://*:'+str(port))
        footage_socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode_(''))

        print("am pornit thread")
        while self.stream_active:
            try:
                frame = footage_socket.recv_string()
                img = base64.b64decode(frame)
                
                #img e bytearray
                #aici s-ar putea insera decriptia
                
                npimg = np.fromstring(img, dtype=np.uint8)
                source = cv2.imdecode(npimg, 1)
                #cv2.imshow("Stream", source)
                #cv2.waitKey(1)
                self.image=source   

            except KeyboardInterrupt:
                #cv2.destroyAllWindows()
                break
        print("am oprit thread")
        
    def gen(self):
        while True:
            frame = self.get_image()
            yield(b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
