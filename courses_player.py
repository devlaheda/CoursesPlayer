import json
import os
import subprocess
import sys
import time
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import vlc
import sqlite3
import threading
from natsort import natsorted
import ctypes

config_path = 'config.json'
defaul_config = {
    "db_file": "default.db",
    "root_dir": "D:\\COURS",
    "scanned": True,
    "playback_speed": 1,
    "selected_item" : None
}
title = "Video Tutorial Player"
class VideoPlayerApp:
    def __init__(self, root):
        self.root = root
        self.hidden_fscreen = False
        self.selected_item = None
        self.current_video_path = None  
        self.root.title(title)
        self.root.geometry("1600x900")  
        self.is_slider_moving = False
        self.lock = threading.Lock()
        self.window_attributes = {
            "geometry": self.root.geometry(),
            "title": self.root.title()
        }
        self.vlc_instance = vlc.Instance()
        self.media_player = self.vlc_instance.media_player_new()
        self.event_manager = self.media_player.event_manager()
        self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.on_video_end)
        try:
            config = self.load_config(config_path)
            self.db_file = config.get('db_file', 'default.db')
            self.root_dir = config.get('root_dir', '')
            self.scanned = config.get('scanned', False)
            self.playback_speed = config.get('playback_speed', 1)
            self.media_player.set_rate(self.playback_speed)
            self.selected_item = config.get('selected_item',None)            
        except json.JSONDecodeError as je:
            messagebox.showerror("JSON ERROR ", f" Config file has JSON error unabale to deserialze it \n {je}")
        if not os.path.exists(self.db_file):
            replay = messagebox.askyesno("Database Error", "Database file not found Do you want to create it?")
            if replay:
                self.scanned = False
            else:
                exit()
        if not os.path.exists(self.root_dir):
            messagebox.showerror("Courses Folder",f"Course folder not found please check your config file {self.root_dir}")
            exit()
        self.create_db_tables()  
        self.create_widgets() 
        self.set_up_bindings()       
        self.check_playback()
        self.speed.config(text=f"Speed: x{self.playback_speed}")
    def load_config(self,file_path):
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                config = json.load(file)
                return config
        else:
            with open(config_path, 'w') as json_file:
                json.dump(defaul_config, json_file, indent=4)
            self.load_config(file_path)  
    def get_connection(self):
        return sqlite3.connect(self.db_file)
    def create_db_tables(self):
        conn = self.get_connection()
        cursor= conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_progress (                
                course_id INTEGER ,
                video_path TEXT PRIMARY KEY ,
                video_length INTEGER ,
                progress INTEGER ,
                FOREIGN KEY (course_id) REFERENCES course_progress (course_id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS course_progress (
                course_id INTEGER PRIMARY KEY AUTOINCREMENT ,
                course_name TEXT UNIQUE ,
                total_length INTEGER ,
                total_progress INTEGER
            )
        ''')
        conn.commit()
        conn.close()
    def set_up_bindings(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.tree.bind("<Double-1>", self.on_video_select)
        self.tree.bind("<Button-3>", self.show_rescan_menu)
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<space>", self.toggle_play_pause)
        self.tree.bind('<Left>', lambda e: self.skip_backward())
        self.tree.bind('<Right>', lambda e: self.skip_forward())
        self.tree.bind('<Up>', lambda e: self.volumeUP() )
        self.tree.bind('<Down>', lambda e: self.volumeDOWN())
        self.root.bind("<Escape>", self.toggle_fullscreen)
        self.root.bind("<Key-d>", self.increase_speed)
        self.root.bind("<Key-D>", self.increase_speed)
        self.root.bind("<Key-s>", self.decrease_speed)
        self.root.bind("<Key-S>", self.decrease_speed)  
        self.root.bind_all('<Up>', self.volumeUP)
        self.root.bind_all('<Down>', self.volumeDOWN)
        self.root.bind("f", self.next_video)
        self.root.bind("q", self.previous_video)
        self.root.bind("x", self.stop_video)
        self.root.bind("h", self.hideTreeView)
        self.slider.bind("<ButtonPress-1>", self.on_slider_move)  
        self.slider.bind("<ButtonRelease-1>", self.on_slider_release)  
    
    def create_widgets(self):
        self.tree_frame = ttk.Frame(self.root, width=400)
        self.tree_frame.grid(row=0, column=0, sticky='nsw')
        self.video_frame = ttk.Frame(self.root) 
        self.video_frame.grid(row=0, column=1, sticky='nsew') 
        self.root.grid_columnconfigure(0, weight=0)  
        self.root.grid_columnconfigure(1, weight=1)  
        self.root.grid_rowconfigure(0, weight=1) 
        self.tree = ttk.Treeview(self.tree_frame, columns=("progress",))
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.heading("#0", text="Video Files", anchor=tk.W)
        self.tree.heading("progress", text="%", anchor=tk.W)
        self.tree.column("progress", width=50, anchor=tk.W, stretch=False)  
        self.tree.column("#0", anchor=tk.W, stretch=True)  
        self.player_handle = self.video_frame.winfo_id()
        self.media_player.set_hwnd(self.player_handle)
        self.video_status_label = ttk.Label(self.root, text="No video playing", font=("Arial", 10))
        self.video_status_label.grid(row=1, column=0, columnspan=2)
        self.slider_frame = ttk.Frame(self.root) 
        self.slider_frame.grid(row=2, column=0, sticky="ew", padx=10, columnspan=2)
        self.time_label = ttk.Label(self.slider_frame, text="00:00 / 00:00", style="TLabel")
        self.time_label.grid(row=0, column=1, sticky=tk.E, padx=10) 
        self.volume = ttk.Label(self.slider_frame, text="Volume: 100%", style="TLabel")
        self.volume.grid(row=0, column=2, sticky=tk.E, padx=10)  
        self.speed = ttk.Label(self.slider_frame, text="Speed: x1.0", style="TLabel")
        self.speed.grid(row=0, column=3, sticky=tk.E, padx=10)  
        self.slider = ttk.Scale(self.slider_frame, from_=0, to=100, orient=tk.HORIZONTAL, style="TScale")
        self.slider.grid(row=0, column=0, sticky="ew")
        self.slider_frame.grid_columnconfigure(0, weight=1)
        self.slider_frame.grid_columnconfigure(1, weight=0)
        self.scan_course_folder()
        self.load_last_video_played()
    
    def change_scale_state(self, state='disabled'):
        self.slider.config(state=state)
    
    def load_videos(self, course_item, course_dir):
        conn = self.get_connection()
        cursor= conn.cursor()
        for item in (natsorted(os.listdir(course_dir))):
            item_path = os.path.join(course_dir, item)
            if os.path.isdir(item_path):
                    subfolder_item = self.tree.insert(course_item, 'end', text=item,tags=(None,), open=False)
                    self.load_videos(subfolder_item, item_path)  

            elif item.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')):
                cursor.execute("SELECT progress, video_length FROM video_progress WHERE video_path=?", (item_path,))
                row = cursor.fetchone()

                if row:
                    progress, video_length = row
                    progress_percentage = (progress / video_length) * 100 if video_length else 0
                else:
                    progress_percentage = 0
                self.tree.insert(course_item, 'end', text=item, values=(f"{progress_percentage:.1f}%"), tags=(item_path,))
        conn.close()
    
    def load_courses(self,dir):
        if self.tree.get_children():
            self.tree.delete(*self.tree.get_children())      
        conn = self.get_connection()
        cursor= conn.cursor()
        for provider_name in os.listdir(dir):
            provider_dir = os.path.join(dir, provider_name)
            if os.path.isdir(provider_dir):
                provider_item = self.tree.insert('', 'end', text=f"{provider_name}",tags=(None,), open=False)
                for course_name in os.listdir(provider_dir):
                    course_dir = os.path.join(provider_dir, course_name)
                    if os.path.isdir(course_dir):
                        cursor.execute("SELECT total_progress, total_length FROM course_progress WHERE course_name=?", (course_name,))
                        row = cursor.fetchone()
                        if row:
                            total_progress, total_length = row
                            total_percentage = (total_progress / total_length) * 100 if total_length else 0
                        else:
                            total_percentage = 0                        
                        course_item = self.tree.insert(provider_item, 'end', text=f"{course_name}", values=(f"{total_percentage:.1f}%"),tags=(None,), open=False)
                        self.load_videos(course_item, course_dir)
        conn.close()                    
        Tooltip(self.tree, delay=800)
    
    def create_tooltips(self):
        for course_item in self.tree.get_children():
            for video_item in self.tree.get_children(course_item):
                video_name = self.tree.item(video_item, 'text')
                Tooltip(self.tree, video_item, video_name)
    
    def on_video_select(self, event):
        self.selected_item = self.tree.selection()
        if self.selected_item:
            video_path = self.tree.item(self.selected_item, 'tags')[0]
            self.load_video(video_path)
    
    def load_video(self, video_path):
        conn = self.get_connection()
        cursor= conn.cursor()
        if os.path.exists(video_path):
            self.video_status_label.config(text=f"{os.path.basename(video_path)}")
            media = self.vlc_instance.media_new(video_path)
            self.media_player.set_media(media)
            cursor.execute("SELECT progress , video_length FROM video_progress WHERE video_path=?", (video_path,))
            row = cursor.fetchone()
            if row:
                progress  = row[0]
                video_length = row[1]
                percentage = (progress / video_length) * 100 if video_length else 0
                if percentage > 99 :
                    replay = messagebox.askyesno("Video Completed", "This video has been completed before. Do you want to replay it?")
                    if replay:
                        progress = 0
                    else:
                        self.next_video()
            else:
                progress = 0
            self.current_video_path = video_path
            self.play_video()
            time.sleep(0.5)
            if progress > 0:
                self.media_player.set_time(progress)
        else:
            self.video_status_label.config(text="Video file does not exist")
        conn.close()
    
    def play_video(self):
        if self.selected_item:
            self.media_player.play()
            self.root.after(0, lambda: self.change_scale_state('normal'))
    
    def pause_video(self):
        if self.media_player:
            self.media_player.pause()
    
    def stop_video(self,event=None):
        self.save_progress()
        if self.media_player:
            self.root.after(0, lambda: self.change_scale_state('disabled'))
            self.media_player.stop()            
            self.video_status_label.config(text="No video playing")
    
    def save_progress(self):
        with self.lock:
            conn = self.get_connection()
            cursor= conn.cursor()
            if self.current_video_path:
                length = self.media_player.get_length()
                position = self.media_player.get_time() if self.media_player.get_time() < length else length
                selected_item = self.tree.selection()
                item_id = self.selected_item[0]
                new_percentage = (position / length) * 100 if length else 0
                self.tree.item(item_id, values=(f"{new_percentage:.1f}%",))    
                cursor.execute("UPDATE video_progress SET progress=? WHERE video_path=?", (position, self.current_video_path))
                conn.commit()
                cursor.execute("SELECT SUM(progress) FROM video_progress WHERE course_id = (SELECT course_id FROM video_progress WHERE video_path = ?)", (self.current_video_path,))
                sum = cursor.fetchone()
                cursor.execute("UPDATE course_progress SET total_progress=? WHERE  course_id = (SELECT course_id FROM video_progress WHERE video_path = ?)", (sum[0], self.current_video_path))
                conn.commit()
                conn.close()
    
    def on_closing(self):
        self.update_json_value(config_path,'selected_item',self.selected_item) 
        self.stop_video(self)
        if self.media_player:
            self.media_player.stop()
            del self.media_player
        self.root.destroy()
    
    def on_video_end(self,event):
        try:
            print("Video ended, saving progress.")
            self.save_progress()
            print("Video ended, next ....")
            self.root.after(0, self.next_video)
        except Exception as e:
            print(f"An error occurred: {e}")
    
    def check_playback(self):
        if self.media_player.is_playing():
            self.save_progress()
        self.root.after(10000, self.check_playback)
    
    def toggle_fullscreen(self,event=None):
        if not hasattr(self, 'is_fullscreen'):
            self.is_fullscreen = False
        if not self.is_fullscreen:
            self.root.attributes("-fullscreen", True)
            self.is_fullscreen = True
        else:
            self.root.attributes("-fullscreen", False)
            self.is_fullscreen = False   
        if self.tree_frame.winfo_ismapped():
            self.tree_frame.grid_forget()
        else:
            self.tree_frame.grid(row=0, column=0, sticky='nsw')
    
    def hideTreeView(self ,event = None):
        if self.tree_frame.winfo_ismapped():
            self.tree_frame.grid_forget()
        else:
            self.tree_frame.grid(row=0, column=0, sticky='nsw')
        if self.hidden_fscreen:
            self.hide_title_bar()
        if not self.hidden_fscreen:
            self.show_title_bar()
        print(self.hidden_fscreen)
    
    def toggle_play_pause(self, event=None):
        if self.media_player.is_playing():
            self.media_player.pause()
        else:
            self.media_player.play()
    
    def increase_speed(self, event=None):
        current_speed = self.media_player.get_rate()
        new_speed = round(current_speed + 0.1,2)
        self.media_player.set_rate(new_speed)
        self.speed.config(text=f"Speed: x{new_speed}")
        self.update_json_value(config_path,'playback_speed',new_speed)
    
    def decrease_speed(self, event=None):
        current_speed = self.media_player.get_rate()
        new_speed = round(current_speed - 0.1,2) 
        if new_speed >= 0.1:
            self.media_player.set_rate(new_speed)
            self.speed.config(text=f"Speed: x{new_speed}")
            self.update_json_value(config_path,'playback_speed',new_speed) 
    
    def next_video(self, event=None):
        selected_item = self.tree.selection()
        if self.selected_item:
            parent_item = self.tree.parent(self.selected_item)
            if parent_item:
                next_index = self.tree.index(self.selected_item) + 1
                chilrens = self.tree.get_children(parent_item)
                if next_index < len(chilrens):
                    next_item = chilrens[next_index]
                    self.tree.selection_set(next_item)
                    self.on_video_select(None)
    
    def previous_video(self, event=None):
        selected_item = self.tree.selection()
        if self.selected_item:
            parent_item = self.tree.parent(self.selected_item)
            if parent_item:
                previous_index = self.tree.index(self.selected_item) - 1
                if previous_index >= 0:
                    previous_item = self.tree.get_children(parent_item)[previous_index]
                    self.tree.selection_set(previous_item)
                    self.on_video_select(event)
    
    def scan_videos_in_background(self,thread_cursor,thread_conn,course_dir, course_id):            
            total_length = 0
            for inner_cours in os.listdir(course_dir):
                inner_cours_dir = os.path.join(course_dir,inner_cours)
                if os.path.isdir(inner_cours_dir):
                    print('\t|---',inner_cours)
                    total_length += self.scan_videos_in_background(thread_cursor,thread_conn,inner_cours_dir,course_id)
                if inner_cours.endswith(('.mp4', '.mkv', '.avi', '.mov')):
                    video_file = inner_cours
                    video_path = os.path.join(course_dir, video_file)
                    media = self.vlc_instance.media_new(video_path)
                    media.parse()
                    length = media.get_duration()
                    if length != -1:
                        total_length += length
                        thread_cursor.execute("INSERT OR REPLACE INTO video_progress (course_id,video_path, video_length, progress) VALUES (?,?, ?, ?)",
                                    (course_id[0],video_path, length, 0))
                        thread_conn.commit()
                    else:
                        print(f"Could not get length for: {video_file}")            
            return total_length
    
    def scan_courses_in_background(self):
        thread_conn = sqlite3.connect(self.db_file)
        thread_cursor = thread_conn.cursor()
        for provider_name in os.listdir(self.root_dir):
            provider_dir = os.path.join(self.root_dir, provider_name)
            if os.path.isdir(provider_dir):
                for course_name in os.listdir(provider_dir):
                    thread_cursor.execute("INSERT OR IGNORE INTO course_progress (course_name, total_length, total_progress) VALUES (?, ?, ?)",
                                            (course_name, 0, 0))                        
                    thread_conn.commit()
                    thread_cursor.execute("SELECT course_id FROM course_progress WHERE course_name = ?", (course_name,))
                    course_id = thread_cursor.fetchone()
                    course_dir = os.path.join(provider_dir, course_name)
                    if os.path.isdir(course_dir):
                        print("|--",course_name)
                        total_length = self.scan_videos_in_background(thread_cursor,thread_conn,course_dir,course_id)
                        thread_cursor.execute("UPDATE course_progress SET total_length=? WHERE course_id=?",
                                            (total_length, course_id[0]))                        
                        thread_conn.commit()                    
        self.update_json_value(config_path,'scanned',True)
        thread_conn.close()
    
    def show_rescan_menu(self, event=None):
        popup = tk.Toplevel(self.root)
        popup.title("Menu")
        popup.geometry("100x80")
        label = tk.Label(popup, text="Rescan Course Folder ?")
        label.pack(pady=5)

        rescan_button = tk.Button(popup, text="Scan", command=self.scan_course_folder)
        rescan_button.pack(pady=5)
    
    def scan_course_folder(self):
        if not self.scanned :
            self.scan_thread = threading.Thread(target=self.scan_courses_in_background, daemon=True)
            self.scan_thread.start()
        self.load_courses(self.root_dir)
    
    def load_last_video_played(self):        
        if(self.selected_item):
            parent = self.tree.parent(self.selected_item)
            while parent:
                self.tree.item(parent, open=True)
                parent = self.tree.parent(parent)
            self.tree.selection_set(self.selected_item)
            video_path = self.tree.item(self.selected_item, 'tags')[0]
            self.load_video(video_path)
        self.root.after(0, lambda: self.change_scale_state(self.media_player.is_playing()))
        self.update_time_slider()      
    
    def update_json_value(self,json_file_path,prop,value):
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)
        data[prop] = value
        with open(json_file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
    
    def skip_forward(self,event=None):
        current_time = self.media_player.get_time()
        self.media_player.set_time(current_time + 10000)
        return'break'
    
    def skip_backward(self,event=None):
        current_time = self.media_player.get_time()
        self.media_player.set_time(max(0, current_time - 10000))
        return'break'
    
    def on_slider_move(self, event):
        self.is_slider_moving = True  
    
    def on_slider_release(self, event):
        self.is_slider_moving = False
        total_time = self.media_player.get_length()
        new_time = self.slider.get() * total_time / 100
        self.media_player.set_time(int(new_time))
        self.check_playback()
    
    def update_time_slider(self):
        if self.media_player.get_state() in [vlc.State.Playing, vlc.State.Paused] and not self.is_slider_moving:
            current_time = self.media_player.get_time()
            total_time = self.media_player.get_length()
            if total_time > 0:
                self.slider.set(current_time * 100 / total_time)
                current_minutes, current_seconds = divmod(current_time // 1000, 60)
                total_minutes, total_seconds = divmod(total_time // 1000, 60)
                self.time_label.config(text=f"{int(current_minutes):02}:{int(current_seconds):02} / {int(total_minutes):02}:{int(total_seconds):02}")
        root.after(500, self.update_time_slider)
    
    def volumeUP(self, event=None):
        current_volume = self.media_player.audio_get_volume()
        new_volume = min(current_volume + 10, 150)
        self.volume.config(text=f"Volume: {new_volume}%")
        self.media_player.audio_set_volume(new_volume)
        return'break'
    
    def volumeDOWN(self, event=None):
        current_volume = self.media_player.audio_get_volume()
        new_volume = max(current_volume - 10, 0)
        self.volume.config(text=f"Volume: {new_volume}%")
        self.media_player.audio_set_volume(new_volume)
        return'break'
    
    def show_title_bar(self):
        self.root.overrideredirect(False)
        self.root.iconify()  
        self.root.deiconify()  
        self.hidden_fscreen = False
    
    def hide_title_bar(self):        
        self.window_attributes["geometry"] = self.root.geometry()
        self.root.overrideredirect(True)
        self.hidden_fscreen = True
        

class Tooltip:
    def __init__(self, widget, delay=5000):
        self.widget = widget
        self.tooltip_window = None
        self.delay = delay  
        self.after_id = None  
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<Motion>", self.on_motion)

    def on_enter(self, event=None):
        self.schedule_tooltip(event)

    def on_leave(self, event=None):
        self.hide_tooltip()
        if self.after_id:
            self.widget.after_cancel(self.after_id)  

    def on_motion(self, event):
        item = self.widget.identify_row(event.y)  
        if item:
            video_name = self.widget.item(item, "text")  
            if self.after_id:
                self.widget.after_cancel(self.after_id)  
            self.schedule_tooltip(event, video_name)

    def schedule_tooltip(self, event, text=None):
        if text:
            self.after_id = self.widget.after(self.delay, lambda: self.show_tooltip(event, text))

    def show_tooltip(self, event, text):
        if self.tooltip_window:
            self.tooltip_window.destroy()

        x, y, _, _ = self.widget.bbox(self.widget.identify_row(event.y))
        x = self.widget.winfo_rootx() + event.x + 20  
        y = self.widget.winfo_rooty() + event.y + 20  

        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(tw, text=text, background="yellow", borderwidth=1, relief="solid")
        label.pack()

    def hide_tooltip(self):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

def set_dark_theme(root):
    
    root.configure(bg='#2e2e2e')  
    style = ttk.Style()
    style.theme_use('clam') 
    style.configure('Treeview',
                    background='#2e2e2e',  
                    foreground='white',     
                    fieldbackground='#2e2e2e',  
                    bordercolor='#1e1e1e',  
                    font=('Helvetica', 10))                       
    style.configure('Treeview.Heading',
                    background='#1e1e1e',  
                    foreground='white',     
                    font=('Helvetica', 11, 'bold'))    
    style.configure('TButton', 
                    background='#3e3e3e',   
                    foreground='white',     
                    font=('Helvetica', 10))    
    style.configure("TScale", 
                    background="#555",  
                    troughcolor="black",  
                    sliderrelief="flat",  
                    sliderlength=1,      
                    sliderthickness=1,    
                    troughthickness=1) 
    style.configure('TLabel', 
                    background='#2e2e2e',   
                    foreground='white',     
                    font=('Helvetica', 10))    
    style.configure('TFrame', background='#2e2e2e')  

required_packages = [
    'python-vlc',
    'tkinter',
    'sqlite3',
    'natsort'
]

def install(package):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def check_and_install_packages():
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"{package} is not installed. Installing now...")
            install(package)
            print(f"{package} installed successfully.")

if __name__ == "__main__":
    check_and_install_packages()
    root = tk.Tk()
    set_dark_theme(root)
    app = VideoPlayerApp(root)
    root.mainloop()
