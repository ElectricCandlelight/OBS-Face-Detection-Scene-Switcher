import threading
import time
import cv2
from obswebsocket import obsws, requests

class FaceDetect:

    def __init__(self, obs_ws, cam_src, on_detect, perv_scene, loss_none, off_detect, poll_rate, output, name):
        self.obs_ws = obs_ws
        self.stream = cv2.VideoCapture(cam_src)
        self.grabbed, self.frame = self.stream.read()
        self.on_detect = on_detect
        self.perv_scene = perv_scene
        self.loss_none = loss_none
        self.off_detect = off_detect
        self.frame_rate = poll_rate
        self.frame_rate = int(poll_rate)
        self.stopped = False
        self.faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        self.timer = 0
        self.source_vis = True
        self.output = output
        self.name = name

        
    def face_detect(self):
        while not self.stopped:
        # Capture frame-by-frame
            self.time_elapsed = time.time() - self.timer

            self.grabbed, self.frame = self.stream.read()

            if  self.time_elapsed > 1./self.frame_rate:

                self.timer = time.time()
                self.gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
                self.faces = self.faceCascade.detectMultiScale(self.gray, scaleFactor=1.6, minNeighbors=4, minSize=(150, 150))

        # Draw a rectangle around the faces
                if self.output:
                    for (x, y, w, h) in self.faces:
                        cv2.rectangle(self.frame, (x, y), (x+w, y+h), (0, 255, 0), 1)

                if  type( self.faces) == tuple:
                    if not self.source_vis:
                        if self.perv_scene:
                            self.obs_ws.call(requests.SetCurrentScene(current_scene))
                        elif self.loss_none:
                            pass
                        else:
                            self.obs_ws.call(requests.SetCurrentScene(self.off_detect))
                        self.source_vis = True
                else:
                    if self.source_vis:
                        scene = self.obs_ws.call(requests.GetCurrentScene())
                        current_scene = scene.getName()
                        self.source_vis = False
                        self.obs_ws.call(requests.SetCurrentScene(self.on_detect))
                # Display the resulting frame
                if self.output:
                    cv2.imshow("Detector " + self.name, self.frame)

                if cv2.waitKey(1) > 0:
                    break
        print("stopping")
        self.stream.release()
        if self.output:
            cv2.destroyWindow("Detector " + self.name)

    def stop(self):
        self.stopped = True

    def start(self):
        self.thread1 = threading.Thread(target=self.face_detect, args=(), daemon=True)
        self.thread1.start()
        return self
