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
            self.stream = cv2.VideoCapture(self.camera)
            self.time_elapsed = 0
            self.timer = time.time()
            current = 5
            while not self.stopped:
                self.grabbed, self.frame = self.stream.read()
                timer = current - int(self.time_elapsed)
                if self.grabbed:
                    cv2.putText(self.frame, "Camera " + str(self.camera), (30,50), cv2.FONT_HERSHEY_DUPLEX, 1, 255, 1)
                    cv2.putText(self.frame, "Next camera in " + str(timer), (30,80), cv2.FONT_HERSHEY_DUPLEX, 1, 255, 1)
                    cv2.imshow("Searching For Cameras", self.frame)
                    if cv2.waitKey(1) > -1:
                        self.stopped = True
                        self.seleceted = self.camera
                        print(self.seleceted)
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
            camera = cv2.VideoCapture(dev_port)
            if not camera.isOpened():
                is_working = False
                print("Port %s is not working." %dev_port)
            else:
                is_reading, img = camera.read()
                w = camera.get(3)
                h = camera.get(4)
                if is_reading:
                    print("Port %s is working and reads images (%s x %s)" %(dev_port,h,w))
                    working_ports.append(dev_port)
                else:
                    print("Port %s for camera ( %s x %s) is present but does not reads." %(dev_port,h,w))
                    available_ports.append(dev_port)
            camera.release()
            print("released")
            dev_port +=1
        print(working_ports)
        return available_ports,working_ports

    def start(self):
        self.thread1 = threading.Thread(target=self.show_camera, args=(), daemon=True)
        self.thread1.start()
        return self