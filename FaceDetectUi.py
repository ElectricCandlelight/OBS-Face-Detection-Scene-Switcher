import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from configparser import ConfigParser
from obswebsocket import obsws, requests
from FaceDetect import FaceDetect
from FindCamera import FindCamera
import time

#======
#CONFIG 
#======
parser = ConfigParser()
parser.read("settings.ini")
saved_port = parser.get("obs", "port")
saved_passw = parser.get("obs", "password")
saved_auto_con = parser.get("obs", "auto_con")
saved_auto_con = int(saved_auto_con)

#===============
#OBS Settings UI
#===============
class ObsSettings:
    def __init__(self, master):
        self.master = master
        #OBS settings LBLF
        self.lblf_obs = tk.LabelFrame(self.master, text="OBS Settings", padx=10, pady=10)

        #Port LBL ENT
        self.lbl_port = tk.Label(self.lblf_obs, text="Port")
        self.ent_port = tk.Entry(self.lblf_obs, width=30)
        self.ent_port.insert(0, saved_port)

        self.lbl_port.grid(row=0, column=0, sticky=tk.E)
        self.ent_port.grid(row=0, column=1)

        #Password LBL ENT
        self.lbl_passw = tk.Label(self.lblf_obs, text="Password")
        self.ent_passw = tk.Entry(self.lblf_obs, width=30, show="*")
        self.ent_passw.insert(0, saved_passw)

        self.lbl_passw.grid(row=1,column=0, sticky=tk.E)
        self.ent_passw.grid(row=1,column=1)

        #Show password CHK
        self.var_show_passw = tk.IntVar()
        self.var_show_passw.set(0)
        self.chk_show_passw = tk.Checkbutton(self.lblf_obs, text="Show Password", variable=self.var_show_passw, command= self.toggle_show_passw)

        self.chk_show_passw.grid(row=2, column=1, sticky=tk.W)

        #Connect BTN
        self.btn_connect = tk.Button(self.lblf_obs, text="Connect", command=connect, padx=10, width=10)

        self.btn_connect.grid(row=0, column=2, rowspan=2, padx=10, pady=10)

        #Auto connect CHK
        self.var_auto_con = tk.IntVar()
        self.var_auto_con.set(saved_auto_con)
        self.chk_auto_con = tk.Checkbutton(self.lblf_obs, text="Auto Connect", variable=self.var_auto_con, command=self.toggle_auto_connect)

        self.chk_auto_con.grid(row=2, column=2)

    def toggle_show_passw(self):
        if self.var_show_passw.get():
            self.ent_passw.config(show="")
        else:
            self.ent_passw.config(show="*")

    def toggle_auto_connect(self):
        parser = ConfigParser()
        parser.read("settings.ini")
        if self.var_auto_con.get():
            parser.set("obs", "auto_con", "1")
        else:
            parser.set("obs", "auto_con", "0")
        with open("settings.ini", "w") as configfile:
            parser.write(configfile)

#==================
#Camera Settings UI
#==================
class CameraSettings:
    def __init__(self, master, name):
        self.test = 1
        self.name = name
        self.master = master
        #Camera settings LBLF
        self.lblf_cam = tk.LabelFrame(self.master, text="Detector " + self.name, padx=10, pady=10)

        #Camera LBL DRP BTN
        self.lbl_cam = tk.Label(self.lblf_cam, text="Select Camera")
        self.drp_cam = ttk.Combobox(self.lblf_cam, state="readonly", width=4)
        self.drp_cam.bind("<<ComboboxSelected>>", self.camera_selected)
        self.btn_cam = tk.Button(self.lblf_cam, text="Find Camera", command=self.find_camera, padx=10, width=10)

        self.lbl_cam.grid(row=0, column=0, sticky=tk.E, pady=5)
        self.drp_cam.grid(row=0, column=1, sticky=tk.W)
        self.btn_cam.grid(row=0, column=1, sticky=tk.E)

        #On detect LBL DRP
        self.lbl_on_detect = tk.Label(self.lblf_cam, text="On Detection")
        self.drp_on_detect= ttk.Combobox(self.lblf_cam, state="readonly", value = scenes_list, width=30)
        self.drp_on_detect.bind("<<ComboboxSelected>>", self.detect_selected)

        self.lbl_on_detect.grid(row=1, column=0, sticky=tk.E, pady=5)
        self.drp_on_detect.grid(row=1, column=1, sticky=tk.W)

        #Off detect LBL DRP
        self.lbl_off_detect = tk.Label(self.lblf_cam, text="Detection Loss")
        self.drp_off_detect= ttk.Combobox(self.lblf_cam, state="readonly", value = scenes_list, width=30)
        self.drp_off_detect.bind("<<ComboboxSelected>>", self.detect_selected)

        self.lbl_off_detect.grid(row=3, column=0, sticky=tk.E, pady=5)
        self.drp_off_detect.grid(row=2, column=1, sticky=tk.W)

        #Previous scene CHK
        self.var_prev_scene = tk.IntVar()
        self.chk_prev_scene = tk.Checkbutton(self.lblf_cam, text="Previous Scene", variable=self.var_prev_scene, command=self.toggle_prev_scene)

        self.chk_prev_scene.grid(row=3, column=1, sticky=tk.W)

        #None scene CHK
        self.var_loss_none = tk.IntVar()
        self.chk_loss_none = tk.Checkbutton(self.lblf_cam, text="Do Nothing", variable=self.var_loss_none, command=self.toggle_loss_none)

        self.chk_loss_none.grid(row=4, column=1, sticky=tk.W)

        #FPS LBL ENT
        self.var_fps = tk.StringVar()
        self.var_fps.trace("w", self.get_fps)
        self.lbl_fps = tk.Label(self.lblf_cam, text="Poll Rate")
        self.ent_fps = tk.Entry(self.lblf_cam, width=5, textvariable=self.var_fps)

        self.lbl_fps.grid(row=5, column=0, sticky=tk.E)
        self.ent_fps.grid(row=5, column=1, sticky=tk.W)

        #Output LBL CHK
        self.var_output = tk.IntVar()
        self.lbl_output = tk.Label(self.lblf_cam, text="Show Output")
        self.chk_output = tk.Checkbutton(self.lblf_cam,  variable=self.var_output, command=self.toggle_show_output)

        self.lbl_output.grid(row=6, column=0, sticky=tk.E)
        self.chk_output.grid(row=6, column=1, sticky=tk.W)

        #Start BTN
        self.btn_start = tk.Button(self.lblf_cam, text="Start", command=self.face_detect, padx=10, width=10)

        self.btn_start.grid(row=6, column=1, sticky=tk.E)

    def camera_selected(self, event):
        self.master.focus()
        parser = ConfigParser()
        parser.read("settings.ini")
        parser.set("cam" + self.name, "camera", self.drp_cam.get())
        with open("settings.ini", "w") as configfile:
            parser.write(configfile)

    def detect_selected(self, event):
        self.master.focus()
        parser = ConfigParser()
        parser.read("settings.ini")
        parser.set("cam" + self.name, "on_detect", self.drp_on_detect.get())
        parser.set("cam" + self.name, "off_detect", self.drp_off_detect.get())
        with open("settings.ini", "w") as configfile:
            parser.write(configfile)

    def toggle_prev_scene(self):
        parser = ConfigParser()
        parser.read("settings.ini")
        if self.var_prev_scene.get():
            self.drp_off_detect.config(state="disabled")
            self.chk_loss_none.config(state="disable")
            parser.set("cam"+ self.name, "prev_scene", "1")
        else:
            parser.set("cam" + self.name, "prev_scene", "0")
            self.drp_off_detect.config(state="readonly")
            self.chk_loss_none.config(state="normal")
        with open("settings.ini", "w") as configfile:
            parser.write(configfile)

    def toggle_loss_none(self):
        parser = ConfigParser()
        parser.read("settings.ini")
        if self.var_loss_none.get():
            self.drp_off_detect.config(state="disabled")
            self.chk_prev_scene.config(state="disable")
            parser.set("cam"+ self.name, "loss_none", "1")
        else:
            parser.set("cam" + self.name, "loss_none", "0")
            self.drp_off_detect.config(state="readonly")
            self.chk_prev_scene.config(state="normal")
        with open("settings.ini", "w") as configfile:
            parser.write(configfile)

    def get_fps(self, fps, index, mode):
        fps=self.var_fps.get()
        parser = ConfigParser()
        parser.read("settings.ini")
        parser.set("cam"+ self.name, "fps", fps)
        with open("settings.ini", "w") as configfile:
            parser.write(configfile)

    def toggle_show_output(self):
        parser = ConfigParser()
        parser.read("settings.ini")
        if self.var_output.get():
            parser.set("cam"+ self.name, "output", "1")
        else:
            parser.set("cam" + self.name, "output", "0")
        with open("settings.ini", "w") as configfile:
            parser.write(configfile)

    def face_detect(self):
        parser = ConfigParser()
        parser.read("settings.ini")
        saved_auto_connect = parser.get("obs", "auto_con")
        saved_auto_connect = int(saved_auto_connect)
        saved_camera = parser.get("cam" + self.name, "camera")
        saved_camera = int(saved_camera)
        saved_on_detect = parser.get("cam" + self.name, "on_detect")
        saved_off_detect = parser.get("cam"+ self.name, "off_detect")
        saved_prev_scene = parser.get("cam"+ self.name, "prev_scene")
        saved_loss_none = parser.get("cam"+ self.name, "loss_none")
        saved_output = parser.get("cam"+ self.name, "output")
        saved_prev_scene = int(saved_prev_scene)
        saved_loss_none = int(saved_loss_none)
        saved_output = int(saved_output)
        saved_fps = parser.get("cam1", "fps")
        self.btn_start.config(text="Stop", command=self.stop_face_detect)
        self.face_detect_obj = FaceDetect(ws, saved_camera, saved_on_detect, saved_prev_scene, saved_loss_none, saved_off_detect, saved_fps, saved_output, self.name).start()
        if saved_output:
            self.monitor(self.face_detect_obj.thread1)

    def stop_face_detect(self):
        self.btn_start.config(text="Start", command=self.face_detect)
        self.face_detect_obj.stop()

    def monitor(self, thread):
        if thread.is_alive():
            # check the thread every 100ms
            root.after(100, lambda: self.monitor(thread))
        else:
            self.btn_start.config(text="Start", command=self.face_detect)

    def find_camera(self):
        camera = FindCamera()
        working_ports = camera.working_ports
        camera.start()
        #camera =  FindCamera(3, "3").start()
        #available_ports, working_ports = list_ports()
        self.monitor_cam(camera.thread1, camera)
        for i in range(4):
            cam_list[i].drp_cam.config(value= working_ports)

    def monitor_cam(self, thread, camera):
        if thread.is_alive():
            # check the thread every 100ms
            root.after(100, lambda: self.monitor_cam(thread, camera))
        else:
            print("Selected")
            print(camera.seleceted)
            if not camera.seleceted == 0:
                self.drp_cam.current(camera.seleceted - 1)
                parser = ConfigParser()
                parser.read("settings.ini")
                parser.set("cam" + self.name, "camera", self.drp_cam.get())
                with open("settings.ini", "w") as configfile:
                    parser.write(configfile)

#==================
#Functions
#==================
def connect():
    global ws
    host = "localhost"
    port = obs_ui.ent_port.get()
    passw = obs_ui.ent_passw.get()

    ws = obsws(host, port, passw)
    try:
        ws.connect()
    except:
        messagebox.showerror("Connection Error", 
        "Unable to connect to OBS websocket server. \nCheck OBS is open. \nCheck port and password are correct.\nOBS Tools -> WebSocket Server Settings")
        time.sleep(1)
        ws.disconnect()
    else:
        parser = ConfigParser()
        parser.read("settings.ini")
        parser.set("obs", "port", port)
        parser.set("obs", "password", passw)
        with open("settings.ini", "w") as configfile:
            parser.write(configfile)
        obs_ui.btn_connect.config(text="Disconnect", command=disconnect)
        obs_get_scenes()
        for i in range(4):
            for child in cam_list[i].lblf_cam.winfo_children():
                child.configure(state='normal')
            #cam
            saved_camera = parser.get("cam"+str(i + 1), "camera")
            saved_camera = int(saved_camera)
            cam_list[i].drp_cam.config(value= saved_camera)
            cam_list[i].drp_cam.current(0)
            #detect
            saved_on_detect = parser.get("cam"+str(i + 1), "on_detect")
            cam_list[i].drp_on_detect.config(value= scenes_list)
            try:
                index = scenes_list.index(saved_on_detect)
            except:
                print("no scene")
            else:
                cam_list[i].drp_on_detect.current(index)
            saved_off_detect = parser.get("cam"+str(i + 1), "off_detect")
            cam_list[i].drp_off_detect.config(value= scenes_list)
            try:
                index = scenes_list.index(saved_off_detect)
            except:
                print("no scene")
            else:
                cam_list[i].drp_off_detect.current(index)
            #prev
            saved_prev_scene = parser.get("cam"+str(i + 1), "prev_scene")
            saved_prev_scene = int(saved_prev_scene)
            cam_list[i].var_prev_scene.set(saved_prev_scene)
            if saved_prev_scene:
                cam_list[i].drp_off_detect.config(state="disabled")
                cam_list[i].chk_loss_none.config(state="disable")
            #none
            saved_loss_none = parser.get("cam"+str(i + 1), "loss_none")
            saved_loss_none = int(saved_loss_none)
            cam_list[i].var_loss_none.set(saved_loss_none)
            if saved_loss_none:
                cam_list[i].drp_off_detect.config(state="disabled")
                cam_list[i].chk_prev_scene.config(state="disable")
            #fps
            saved_fps = parser.get("cam"+str(i + 1), "fps")
            cam_list[i].var_fps.set(saved_fps)
            #show output
            saved_output = parser.get("cam"+str(i + 1), "output")
            saved_output = int(saved_output)
            cam_list[i].var_output.set(saved_output)


def disconnect():
    ws.disconnect()
    obs_ui.btn_connect.config(text="Connect", command=connect)
    for i in range(4):
        for child in cam_list[i].lblf_cam.winfo_children():
            child.configure(state='disable')

scenes_list=[]

def obs_get_scenes():
    scenes_list.clear()
    scenes = ws.call(requests.GetSceneList())
    for s in scenes.getScenes():
        name = s['name']
        scenes_list.append(name)
    print(scenes_list)


def main(): 
    global root
    root = tk.Tk()
    root.title("Face Detection Scene Swither")
    global cam_list
    global obs_ui
    obs_ui = ObsSettings(root)
    cam1_ui = CameraSettings(root, "1")
    cam2_ui = CameraSettings(root, "2")
    cam3_ui = CameraSettings(root, "3")
    cam4_ui = CameraSettings(root, "4")
    cam_list = [cam1_ui, cam2_ui, cam3_ui, cam4_ui]
    obs_ui.lblf_obs.grid(row=0,column=0, columnspan=2, padx=10, pady=10, sticky=tk.W)
    cam1_ui.lblf_cam.grid(row=1, column=0, padx=10, pady=10,sticky=tk.W)
    cam2_ui.lblf_cam.grid(row=1, column=1,  padx=10, pady=10, sticky=tk.W)
    cam3_ui.lblf_cam.grid(row=2, column=0,  padx=10, pady=10, sticky=tk.W)
    cam4_ui.lblf_cam.grid(row=2, column=1,  padx=10, pady=10, sticky=tk.W)

    for i in range(4):
        for child in cam_list[i].lblf_cam.winfo_children():
            child.configure(state='disable')

    if saved_auto_con:
        connect()

    root.mainloop()


if __name__ == '__main__':
    main()