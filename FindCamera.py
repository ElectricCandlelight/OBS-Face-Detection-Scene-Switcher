import threading
import time
import cv2

class FindCamera:

    def __init__(self):
        self.timer = 0
        self.stopped = False
        self.available_ports, self. working_ports = self.list_ports()
        self.seleceted = 0


    def show_camera(self):
        for self.camera in self.working_ports:
            self.stream = cv2.VideoCapture(self.camera, cv2.CAP_DSHOW)
            self.time_elapsed = 0
            self.timer = time.time()
            current = 5
            while not self.stopped:
                self.grabbed, self.frame = self.stream.read()
                timer = current - int(self.time_elapsed)
                if self.grabbed:
                    cv2.rectangle(self.frame, (10,0),(490,100), (0,0,0), -1)
                    cv2.putText(self.frame, "Press any key to select/exit", (20,30), cv2.FONT_HERSHEY_DUPLEX, 1, 255, 1)
                    cv2.putText(self.frame, "Camera " + str(self.camera), (20,60), cv2.FONT_HERSHEY_DUPLEX, 1, 255, 1)
                    cv2.putText(self.frame, "Next camera in " + str(timer), (20,90), cv2.FONT_HERSHEY_DUPLEX, 1, 255, 1)
                    cv2.imshow("Searching For Cameras", self.frame)
                    if cv2.waitKey(1) > -1:
                        self.seleceted = self.camera
                        self.stopped = True
                        break
                    if  self.time_elapsed > 4 :
                        self.timer = time.time()
                        break
                    self.time_elapsed = time.time() - self.timer
            self.stream.release()
        cv2.destroyWindow("Searching For Cameras")

    def stop(self):
        self.stopped = True

    def list_ports(self):
        is_working = True
        dev_port = 0
        working_ports = []
        available_ports = []
        while is_working:
            camera = cv2.VideoCapture(dev_port, cv2.CAP_DSHOW)
            if not camera.isOpened():
                is_working = False
            else:
                is_reading, img = camera.read()
                if is_reading:
                    working_ports.append(dev_port)
                else:
                    available_ports.append(dev_port)
            camera.release()
            dev_port +=1
        return available_ports,working_ports

    def start(self):
        self.thread = threading.Thread(target=self.show_camera, args=(), daemon=True)
        self.thread.start()
        return self