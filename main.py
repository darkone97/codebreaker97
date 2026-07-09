import os
import time
import ctypes
import json
import cv2
import psutil
import pyperclip
import webbrowser
import urllib.parse
from datetime import datetime
import pyautogui
import screen_brightness_control as sbc
import shutil
import threading
import queue
import requests
from bs4 import BeautifulSoup
import re
from PIL import Image
import speech_recognition as sr
import pyttsx3
import customtkinter as ctk
from customtkinter import filedialog
import fitz
import easyocr
import socket
import platform
import io

try:
    import ollama
except ImportError:
    pass

try:
    from translatepy import Translator  # type: ignore
except ImportError:
    Translator = None

# --- 1. SYSTEM INITIALIZATION & GLOBALS ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CONTACTS_FILE = "contacts.json"
MEMORY_FILE = "memory.json"
SCREENSHOT_DIR = "screenshots"
SECURITY_DIR = "security_logs"

def load_contacts():
    if os.path.exists(CONTACTS_FILE):
        try:
            with open(CONTACTS_FILE, "r") as f: return json.load(f)
        except Exception: return {}
    return {"contact_name": "+910000000000"}

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f: return json.load(f)
        except Exception: return {}
    return {}

def save_memory(data):
    try:
        with open(MEMORY_FILE, "w") as f: json.dump(data, f)
    except Exception: pass

CONTACTS = load_contacts()
MEMORY = load_memory()
active_timers = []

def load_chat_history():
    if os.path.exists("chat_history.json"):
        try:
            with open("chat_history.json", "r") as f: return json.load(f)
        except Exception: pass
    return []

chat_history = load_chat_history()
tts_queue = queue.Queue()
screenshot_counter = 0

if not os.path.exists(SCREENSHOT_DIR): os.makedirs(SCREENSHOT_DIR) 
if not os.path.exists(SECURITY_DIR): os.makedirs(SECURITY_DIR) 

def tts_worker():
    import pythoncom 
    pythoncom.CoInitialize() 
    engine = pyttsx3.init()
    engine.setProperty('rate', 160)
    while True:
        text = tts_queue.get()
        if text is None: break
        engine.say(text)
        engine.runAndWait()
        tts_queue.task_done()

threading.Thread(target=tts_worker, daemon=True).start()
def speak_async(text): tts_queue.put(str(text)[:500])

# --- 2. ADVANCED UTILITY FUNCTIONS ---
def take_screenshot():
    global screenshot_counter
    screenshot_counter += 1
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{SCREENSHOT_DIR}/screenshot_{timestamp}_{screenshot_counter}.png"
    try:
        img = pyautogui.screenshot()
        img.save(filename)
        return f"Screenshot saved: {filename}"
    except Exception as e:
        return f"Screenshot failed: {e}"

def get_system_info():
    info = {
        "CPU": f"{psutil.cpu_percent()}%",
        "RAM": f"{psutil.virtual_memory().percent}%",
        "Disk": f"{psutil.disk_usage('/').percent}%",
        "Battery": psutil.sensors_battery().percent if hasattr(psutil, "sensors_battery") and psutil.sensors_battery() else "Desktop",
        "OS": platform.system(),
        "Hostname": socket.gethostname()
    }
    return info

def list_files(directory="."):
    try:
        files = os.listdir(directory)
        return ", ".join(files[:20])
    except Exception as e:
        return f"Error listing files: {e}"

def get_clipboard():
    try:
        return pyperclip.paste()
    except Exception:
        return "Could not access clipboard"

def set_clipboard(text):
    try:
        pyperclip.copy(text)
        return "Text copied to clipboard"
    except Exception:
        return "Could not write to clipboard"

def translate_text(text, target_lang="es"):
    try:
        if Translator is None:
            return f"Translation not available. Install: pip install translatepy"
        translator = Translator()
        result = translator.translate(text, target_lang)
        return str(result)
    except Exception:
        return f"Translation not available. Install: pip install translatepy"

def calculate_expression(expr):
    try:
        expr = expr.replace("^", "**")
        result = eval(expr, {"__builtins__": None}, {})
        return f"Result: {result}"
    except Exception as e:
        return f"Calculation error: {e}"

def fetch_live_web_data(query):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(f"https://www.google.com/search?q={query}", headers=headers)
        return BeautifulSoup(res.text, "html.parser").find("div", class_="BNeawe").text
    except Exception: return "Unable to pull live web intelligence right now."

def read_local_pdf(pdf_name, ocr_engine=None):
    user_home = os.path.expanduser("~")
    desktop_path = os.path.join(user_home, "OneDrive", "Desktop") if os.path.exists(os.path.join(user_home, "OneDrive", "Desktop")) else os.path.join(user_home, "Desktop")
    transfer_dir = os.path.join(desktop_path, "Gemini_Transfers")
    target_file = next((p for p in [os.path.join(transfer_dir, pdf_name), os.path.join(transfer_dir, pdf_name + ".pdf"), pdf_name] if os.path.exists(p) and os.path.isfile(p)), None)
    
    if not target_file: return "I couldn't locate that document in your transfer folder."
    try:
        doc = fitz.open(target_file)
        text = "".join([page.get_text() for page in doc[:5]]) 
        
        if len(text.strip()) < 10 and ocr_engine is not None:
            print("[SYSTEM] Scanned PDF detected. Engaging OCR Vision fallback...")
            text = ""
            for page in doc[:2]: 
                pix = page.get_pixmap()
                pix.save("temp_pdf_page.png")
                text += " ".join(ocr_engine.readtext("temp_pdf_page.png", detail=0)) + "\n"
            if os.path.exists("temp_pdf_page.png"): os.remove("temp_pdf_page.png")
            
        return text[:3000]
    except Exception as e: return f"Error parsing document: {e}"

def read_workspace_file(filename):
    """Silently reads raw code files into the AI's context buffer."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"File Error: {e}"

# --- 3. MAIN GUI CLASS ---
class CodebreakerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("codebreaker97 Operating System - Dual Brain Build")
        self.geometry("1300x850")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.grid_columnconfigure(0, weight=0, minsize=260)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0, minsize=320)
        self.grid_rowconfigure(0, weight=1)

        self.is_voice_mode = False
        self.cap = None 
        self.latest_camera_frame = None
        
        self.ocr_reader = None 
        self.yolo_model = None
        self.yolo_active = False 

        # --- THE PLUGIN LOADER ---
        self.plugins = []
        self.load_plugins()
        # -------------------------

        self.build_left_sidebar()
        self.build_center_workspace()
        self.build_right_dashboard()

        threading.Thread(target=self.camera_worker, daemon=True).start()
        threading.Thread(target=self.load_ocr_engine, daemon=True).start()
        threading.Thread(target=self.capture_boot_photo, daemon=True).start() 
        
        self.update_ui_feed()
        self.update_system_metrics()
        self.speak_async = speak_async

    def capture_boot_photo(self):
        try:
            temp_cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            import time
            time.sleep(0.5)
            for _ in range(15): temp_cap.read() 
            ret, frame = temp_cap.read()
            temp_cap.release()
            
            if ret:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                log_path = os.path.join(SECURITY_DIR, f"boot_log_{ts}.jpg")
                cv2.imwrite(log_path, frame)
                print(f"[SECURITY] Boot frame captured to {log_path}")
        except Exception as e:
            print(f"[SECURITY] Boot capture failed: {e}")

    def load_ocr_engine(self):
        self.ocr_reader = easyocr.Reader(['en'], gpu=True) 

    def load_yolo_engine(self):
        try:
            from ultralytics import YOLO
            self.yolo_model = YOLO('yolov8s-world.pt')
            self.yolo_model.set_classes([
                "person", "book", "cup", "bottle", "cell phone", "laptop", "keyboard", "mouse"
            ])
            self.yolo_active = True
            self.safe_append_chat("SYSTEM", "YOLO-World Vision Tracking is now ACTIVE.")
            speak_async("Vision tracking initialized and active.")
        except Exception as e:
            self.safe_append_chat("ERROR", f"Failed to load vision tracking: {e}")

    def load_plugins(self):
        import importlib.util
        import glob
        if not os.path.exists("plugins"): os.makedirs("plugins")
        
        for plugin_file in glob.glob("plugins/*.py"):
            name = os.path.basename(plugin_file)[:-3]
            try:
                spec = importlib.util.spec_from_file_location(name, plugin_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                # Ensure the plugin has our standard hook
                if hasattr(module, "handle_query"):
                    self.plugins.append(module)
                    print(f"[SYSTEM] Plugin Loaded: {name}")
            except Exception as e:
                print(f"[ERROR] Failed to load plugin '{name}': {e}")

    def build_left_sidebar(self):
        self.left_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#1e1e24")
        self.left_frame.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        ctk.CTkLabel(self.left_frame, text="Second Brain & Memory", font=ctk.CTkFont(size=16, weight="bold")).pack(padx=20, pady=(20, 10))
        self.history_scroll = ctk.CTkScrollableFrame(self.left_frame, fg_color="transparent")
        self.history_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        self.note_btn = ctk.CTkButton(self.left_frame, text="View Notes.txt", font=ctk.CTkFont(weight="bold"), fg_color="#3b3b4a", hover_color="#525266", command=lambda: os.startfile("notes.txt") if os.path.exists("notes.txt") else None)
        self.note_btn.pack(pady=20, padx=20, fill="x")

    def build_center_workspace(self):
        self.center_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.center_frame.grid(row=0, column=1, padx=5, pady=10, sticky="nsew")
        self.center_frame.grid_columnconfigure(0, weight=1) 
        self.center_frame.grid_rowconfigure(0, weight=1)
        self.center_frame.grid_rowconfigure(1, weight=0)

        self.chat_display = ctk.CTkTextbox(self.center_frame, font=ctk.CTkFont(family="Consolas", size=15), wrap="word", fg_color="#121214", border_color="#3b3b4a", border_width=1)
        self.chat_display.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        self.chat_display.configure(state="disabled")
        self.safe_append_chat("SYSTEM", "codebreaker97 Core Online. All systems unlocked and ready.")

        self.input_frame = ctk.CTkFrame(self.center_frame, height=60, corner_radius=10, fg_color="#1e1e24")
        self.input_frame.grid(row=1, column=0, sticky="ew")
        self.input_frame.grid_columnconfigure(2, weight=1) 

        self.upload_btn = ctk.CTkButton(self.input_frame, text="📎", width=40, height=40, font=ctk.CTkFont(size=20), fg_color="#3b3b4a", hover_color="#525266", command=self.on_upload_click)
        self.upload_btn.grid(row=0, column=0, padx=(10, 0), pady=10)

        self.mic_btn = ctk.CTkButton(self.input_frame, text="🎤 Voice", width=60, height=40, font=ctk.CTkFont(size=14, weight="bold"), fg_color="#d64933", hover_color="#ed614c", command=self.toggle_voice_mode)
        self.mic_btn.grid(row=0, column=1, padx=(10, 5), pady=10)

        self.text_input = ctk.CTkEntry(self.input_frame, placeholder_text="Type command or upload a file...", height=40, border_width=0)
        self.text_input.grid(row=0, column=2, padx=5, pady=10, sticky="ew")
        self.text_input.bind("<Return>", self.on_send_click)

        self.send_btn = ctk.CTkButton(self.input_frame, text="Send", width=80, height=40, font=ctk.CTkFont(weight="bold"), command=self.on_send_click)
        self.send_btn.grid(row=0, column=3, padx=(5, 10), pady=10)

    def build_right_dashboard(self):
        self.right_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.right_frame.grid(row=0, column=2, padx=(5, 10), pady=10, sticky="nsew")
        self.right_frame.grid_rowconfigure(0, weight=1) 
        self.right_frame.grid_rowconfigure(1, weight=1)

        self.vision_frame = ctk.CTkFrame(self.right_frame, corner_radius=10, fg_color="#1e1e24")
        self.vision_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        ctk.CTkLabel(self.vision_frame, text="LIVE VISION FEED", font=ctk.CTkFont(size=14, weight="bold"), text_color="#00ffcc").pack(pady=(10, 0))
        self.video_label = ctk.CTkLabel(self.vision_frame, text="Loading Camera...")
        self.video_label.pack(expand=True, padx=10, pady=10)

        self.stats_frame = ctk.CTkFrame(self.right_frame, corner_radius=10, fg_color="#1e1e24")
        self.stats_frame.grid(row=1, column=0, sticky="nsew", pady=(5, 0))
        ctk.CTkLabel(self.stats_frame, text="SYSTEM METRICS", font=ctk.CTkFont(size=14, weight="bold"), text_color="#ffcc00").pack(pady=(15, 10))
        self.cpu_label = ctk.CTkLabel(self.stats_frame, text="CPU Load: --%", font=ctk.CTkFont(size=14))
        self.cpu_label.pack(anchor="w", padx=20, pady=10)
        self.ram_label = ctk.CTkLabel(self.stats_frame, text="RAM Usage: --%", font=ctk.CTkFont(size=14))
        self.ram_label.pack(anchor="w", padx=20, pady=10)
        self.battery_label = ctk.CTkLabel(self.stats_frame, text="Battery: --%", font=ctk.CTkFont(size=14))
        self.battery_label.pack(anchor="w", padx=20, pady=10)

    def safe_append_chat(self, speaker, text):
        self.after(0, self._do_append_chat, speaker, text)

    def _do_append_chat(self, speaker, text):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"[{datetime.now().strftime('%H:%M')}] {speaker}:\n{text}\n\n")
        self.chat_display.yview("end")
        self.chat_display.configure(state="disabled")

    def safe_add_history(self, command):
        self.after(0, self._do_add_history, command)

    def _do_add_history(self, command):
        short_cmd = (command[:25] + '...') if len(command) > 25 else command
        btn = ctk.CTkButton(self.history_scroll, text=f"💬 {short_cmd}", fg_color="#2b2b36", hover_color="#3b3b4a", anchor="w")
        btn.pack(fill="x", pady=4)

    def update_chat_memory(self, query, reply):
        global chat_history
        chat_history.extend([{'role': 'user', 'content': query}, {'role': 'assistant', 'content': reply}])
        # Keep the last 15 interactions so the JSON doesn't become 10,000 lines long
        if len(chat_history) > 15: chat_history = chat_history[-15:] 
        try:
            with open("chat_history.json", "w") as f: json.dump(chat_history, f)
        except Exception: pass

    def on_upload_click(self):
        file_path = filedialog.askopenfilename(filetypes=[("Documents & Images", "*.pdf;*.png;*.jpg;*.jpeg")])
        if file_path:
            filename = os.path.basename(file_path)
            user_home = os.path.expanduser("~")
            desk_path = os.path.join(user_home, "OneDrive", "Desktop") if os.path.exists(os.path.join(user_home, "OneDrive", "Desktop")) else os.path.join(user_home, "Desktop")
            transfer_dir = os.path.join(desk_path, "Gemini_Transfers")
            if not os.path.exists(transfer_dir): os.makedirs(transfer_dir)
            
            shutil.copy2(file_path, os.path.join(transfer_dir, filename))
            self.safe_append_chat("SYSTEM", f"File '{filename}' uploaded securely.")
            
            self.text_input.delete(0, "end")
            if filename.lower().endswith('.pdf'):
                self.text_input.insert(0, f"read the file {filename} and summarize it")
            else:
                self.text_input.insert(0, f"read the image {filename} and extract the text")

    def on_send_click(self, event=None):
        if self.is_voice_mode: self.disable_voice_mode() 
        query = self.text_input.get().strip()
        if not query: return
        self.text_input.delete(0, "end")
        self.safe_append_chat("Arpit", query)
        self.safe_add_history(query)
        threading.Thread(target=self.process_query, args=(query,), daemon=True).start()

    def toggle_voice_mode(self):
        if not self.is_voice_mode:
            self.is_voice_mode = True
            self.mic_btn.configure(fg_color="#00ffcc", text_color="black", text="🎙️ Active")
            self.text_input.configure(placeholder_text="Listening continuously. Type to cancel...")
            threading.Thread(target=self.continuous_voice_worker, daemon=True).start()
        else:
            self.disable_voice_mode()

    def disable_voice_mode(self):
        self.is_voice_mode = False
        self.mic_btn.configure(fg_color="#d64933", text_color="white", text="🎤 Voice")
        self.text_input.configure(placeholder_text="Type command or upload a file...")

    def continuous_voice_worker(self):
        try:
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                self.safe_append_chat("SYSTEM", "🎙️ Listening...")
                while self.is_voice_mode:
                    try:
                        audio = recognizer.listen(source, timeout=1, phrase_time_limit=10)
                        query = recognizer.recognize_google(audio)
                        if query:
                            self.safe_append_chat("Arpit (Voice)", query)
                            self.safe_add_history(query)
                            self.process_query(query)
                    except sr.WaitTimeoutError: continue 
                    except sr.UnknownValueError: continue
                    except sr.RequestError as e: self.safe_append_chat("ERROR", f"Google API error: {e}")
                    except Exception as e: self.safe_append_chat("ERROR", f"Voice error: {e}")
        except Exception as e:
            self.safe_append_chat("ERROR", f"Microphone Hardware Error: {e}. Ensure PyAudio is installed.") 
            self.after(0, self.disable_voice_mode)

    # ---- CORE AI & LOGIC PROCESSOR ----
    def process_query(self, query):
        query_clean = query.lower()
        
        # --- DYNAMIC PLUGIN ROUTER ---
        for plugin in self.plugins:
            try:
                # We pass 'self' so the plugin can use the chat, TTS, and camera!
                if plugin.handle_query(query_clean, self): 
                    return # Stop processing if a plugin takes the command
            except Exception as e:
                self.safe_append_chat("ERROR", f"Plugin fault: {e}")
        # -----------------------------

        # 1. ON-DEMAND CAMERA & YOLO VISION
        if "start vision" in query_clean:
            if self.cap is None:
                self.cap = cv2.VideoCapture(0)
            if self.yolo_model is None:
                self.safe_append_chat("SYSTEM", "Starting Camera and Loading YOLO-World...")
                speak_async("Activating camera and warming up vision engines.")
                threading.Thread(target=self.load_yolo_engine, daemon=True).start()
            else:
                self.yolo_active = True
                self.safe_append_chat("SYSTEM", "Camera and YOLO Vision Online.")
                speak_async("Vision tracking is now online.")
            return

        if "stop vision" in query_clean:
            self.yolo_active = False
            if self.cap is not None:
                self.cap.release() 
                self.cap = None
            self.latest_camera_frame = None 
            self.safe_append_chat("SYSTEM", "Camera and YOLO Vision Offline.")
            speak_async("Camera and vision tracking disabled.")
            return
# 6. WINDOWS PHONE LINK (CALLING)
        if query_clean.startswith("call "):
            target_name = query_clean.replace("call ", "").strip()
            number = None
            
            # Search contacts file (case-insensitive)
            for name, phone in CONTACTS.items():
                if name.lower() == target_name:
                    number = phone
                    break
            
            if number:
                self.safe_append_chat("SYSTEM", f"Initiating secure line to {target_name} ({number})...")
                speak_async(f"Calling {target_name}.")
                try:
                    # The 'tel:' protocol triggers Windows Phone Link
                    os.startfile(f"tel:{number}")
                except AttributeError:
                    # Fallback for Mac/Linux if OS module fails
                    webbrowser.open(f"tel:{number}")
                except Exception as e:
                    self.safe_append_chat("ERROR", f"Dialer failed: {e}")
            else:
                self.safe_append_chat("ERROR", f"Target '{target_name}' not found in contacts.json.")
                speak_async(f"I don't have a number for {target_name}.")
            return
        # 2. REAL-TIME VISION QUERIES (True LLaVA Multimodal)
        vision_keywords = ["what am i", "what am i doing", "what am i holding", "describe me", "what do you see", "analyze", "look at me", "what colour", "what color"]
        if any(k in query_clean for k in vision_keywords):
            if self.latest_camera_frame is None:
                self.safe_append_chat("ERROR", "Camera is offline. Say 'start vision' first.")
                return
            
            self.safe_append_chat("SYSTEM", "Capturing frame for LLaVA Multimodal Analysis...")
            speak_async("Processing visual data.")

            def vision_task():
                try:
                    img = Image.fromarray(self.latest_camera_frame)
                    buffered = io.BytesIO()
                    img.save(buffered, format="JPEG")
                    img_bytes = buffered.getvalue()

                    res = ollama.chat(model='llava', messages=[{'role': 'user', 'content': query, 'images': [img_bytes]}])
                    reply = res['message']['content']
                    self.safe_append_chat("codebreaker97", reply)
                    speak_async(reply)
                except Exception as e:
                    self.safe_append_chat("ERROR", f"LLaVA Error: {e}")

            threading.Thread(target=vision_task, daemon=True).start()
            return

        # 4. FILE MANAGEMENT & CLIPBOARD
        if "list files" in query_clean:
            self.safe_append_chat("SYSTEM", f"Files: {list_files('.')}")
            return
            
        if "copy to clipboard" in query_clean:
            text = query_clean.replace("copy to clipboard", "").strip()
            self.safe_append_chat("SYSTEM", set_clipboard(text))
            return
        # 7. LOCAL IMAGE GENERATION (STABLE DIFFUSION)
        if query_clean.startswith("generate image "):
            prompt_text = query_clean.replace("generate image ", "").strip()
            self.safe_append_chat("SYSTEM", f"Engaging Diffusion Engine... Prompt: '{prompt_text}'")
            speak_async("Generating image. Please wait.")

            def generate_task():
                payload = {
                    "prompt": prompt_text,
                    "steps": 20,
                    "width": 512,
                    "height": 512
                }
                try:

                    # Pointing to your local Automatic1111 API instance
                    response = requests.post(url='http://127.0.0.1:7860/sdapi/v1/txt2img', json=payload, timeout=60)
                    r = response.json()
                    
                    import base64
                    for i in r['images']:
                        image_data = base64.b64decode(i.split(",", 1)[0])
                        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                        out_path = f"generated_{ts}.png"
                        
                        with open(out_path, 'wb') as f:
                            f.write(image_data)
                            
                        self.safe_append_chat("SYSTEM", f"Image successfully compiled and saved to {out_path}")
                        speak_async("Image generation complete.")
                        
                        # Open the image automatically in Windows
                        os.startfile(out_path)
                except Exception as e:
                    self.safe_append_chat("ERROR", f"Diffusion Engine failed: {e}. Make sure your local WebUI API is running.")

            threading.Thread(target=generate_task, daemon=True).start()
            return
        # 5. HARDWARE MEDIA CONTROLS
        if "play music" in query_clean:
            # Pure hardware trigger to use Windows default media, bypassing protocol errors
            ctypes.windll.user32.keybd_event(0xB3, 0, 0, 0)
            self.safe_append_chat("SYSTEM", "Default media playback toggled.")
            speak_async("Music toggled.")
            return

        if any(k in query_clean for k in ["pause music", "forward", "next track", "skip", "volume up", "volume down"]):
            if "pause" in query_clean: ctypes.windll.user32.keybd_event(0xB3, 0, 0, 0)
            if "forward" in query_clean or "next" in query_clean or "skip" in query_clean: ctypes.windll.user32.keybd_event(0xB0, 0, 0, 0)
            if "volume up" in query_clean: [ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0) for _ in range(5)]
            if "volume down" in query_clean: [ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0) for _ in range(5)]
            self.safe_append_chat("SYSTEM", "Media control executed.")
            return

        # 14/15. READ IMAGES AND PDFS (OCR)
        if "read the image" in query_clean or "extract text" in query_clean or "read the file" in query_clean:
            filename = query_clean.replace("read the image", "").replace("extract text from", "").replace("read the file", "").split(" and ")[0].strip()
            user_home = os.path.expanduser("~")
            desk_path = os.path.join(user_home, "OneDrive", "Desktop") if os.path.exists(os.path.join(user_home, "OneDrive", "Desktop")) else os.path.join(user_home, "Desktop")
            target = os.path.join(desk_path, "Gemini_Transfers", filename)
            
            if os.path.exists(target):
                try:
                    if self.ocr_reader is None: self.ocr_reader = easyocr.Reader(['en'], gpu=True)
                    if filename.endswith(".pdf"):
                        extracted_text = read_local_pdf(filename, self.ocr_reader)
                    else:
                        extracted_text = " ".join(self.ocr_reader.readtext(target, detail=0))
                        
                    if not extracted_text: return self.safe_append_chat("SYSTEM", "No readable text found.")
                        
                    res = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': f"Here is the text:\n\n'{extracted_text}'\n\nFulfill request: {query}"}])
                    self.safe_append_chat("codebreaker97", res['message']['content'])
                except Exception as e: self.safe_append_chat("ERROR", f"OCR Failed: {e}")
            return

        # =========================================================================
        # 16. THE DUAL-BRAIN AUTO-ROUTER (LLAMA3 vs QWEN-CODER)
        # =========================================================================
        coding_keywords = ["code", "script", "debug", "python", "html", "css", "javascript", "function", "build a", "write a", "analyze"]
        is_coding_task = any(k in query_clean for k in coding_keywords)

        # SET YOUR TARGET CODER MODEL HERE (qwen2.5-coder:3b or qwen3-coder:4b)
        coder_model = "qwen2.5-coder:3b" 
        
        target_model = coder_model if is_coding_task else "llama3"
        brain_name = "Architect Mode" if is_coding_task else "Core"

        # Auto-File Sniffer: Detects if you mentioned a file name in your prompt
        file_match = re.search(r'\b([\w-]+\.(?:py|json|txt|md|html|js|css))\b', query_clean)
        code_context = ""
        
        if file_match and os.path.exists(file_match.group(1)):
            filename = file_match.group(1)
            self.safe_append_chat("SYSTEM", f"[Brain Swapped to {brain_name} - Reading {filename}...]")
            code_content = read_workspace_file(filename)
            code_context = f"\n\nContext - {filename}:\n```\n{code_content}\n```\n"
        else:
            self.safe_append_chat("SYSTEM", f"[Routing to {brain_name} ({target_model})...]")

        # Dynamic System Personas
        if is_coding_task:
            system_message = {'role': 'system', 'content': f"You are codebreaker97's Elite Architect Mode. Be a precise, expert AI developer. Provide functional code snippets only when necessary."}
        else:
            live_context = f" Live Web Context: {fetch_live_web_data(query)}" if any(k in query_clean for k in ["who is", "what is the price"]) else ""
            system_message = {'role': 'system', 'content': f"You are codebreaker97. Current Time: {datetime.now().strftime('%I:%M %p')}.{live_context} Be brief and helpful."}

        global chat_history
        try:
            # We silently append the read file context directly to your query so the LLM can see it!
            final_query = query + code_context
            response = ollama.chat(model=target_model, messages=[system_message] + chat_history + [{'role': 'user', 'content': final_query}])
            reply = response['message']['content']
            
            self.safe_append_chat(f"codebreaker97 ({brain_name})", reply)
            if not is_coding_task: # Don't read out massive blocks of Python out loud
                speak_async(reply)
            else:
                speak_async("Coding task complete.")

            # Append to persistent JSON memory
            self.update_chat_memory(query, reply)
        except Exception as e:
            self.safe_append_chat("ERROR", f"LLM Error with {target_model}: {e}. Ensure it is installed via ollama pull.")


    # ---- BACKGROUND PROCESSES ----
    def _run_timer(self, minutes):
        time.sleep(minutes * 60)
        self.safe_append_chat("SYSTEM", f"Timer complete! {minutes} minutes have passed.")
        speak_async("Timer complete.")

    def camera_worker(self):
        while True:
            if self.cap is not None and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    frame = cv2.flip(frame, 1)
                    if self.yolo_active and self.yolo_model is not None:
                        for r in self.yolo_model(frame, stream=True, verbose=False):
                            for box in r.boxes:
                                if int(box.conf[0] * 100) > 15:
                                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                                    cv2.putText(frame, self.yolo_model.names[int(box.cls[0])], (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                    self.latest_camera_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else: self.latest_camera_frame = None
            time.sleep(0.05) 

    def update_ui_feed(self):
        if self.latest_camera_frame is not None:
            img = Image.fromarray(self.latest_camera_frame)
            self.video_label.configure(image=ctk.CTkImage(light_image=img, dark_image=img, size=(300, 225)), text="")
        else: self.video_label.configure(image=None, text="Camera Offline\n(Say 'Start Vision')")
        self.after(40, self.update_ui_feed)

    def update_system_metrics(self):
        self.cpu_label.configure(text=f"CPU Load: {psutil.cpu_percent()}%")
        self.ram_label.configure(text=f"RAM Usage: {psutil.virtual_memory().percent}%")
        batt = psutil.sensors_battery() if hasattr(psutil, 'sensors_battery') else None
        self.battery_label.configure(text=f"Battery: {batt.percent}%" if batt else "Battery: Desktop / Not Found")
        self.after(2000, self.update_system_metrics)

    def on_closing(self):
        self.is_voice_mode = False 
        if hasattr(self, 'cap') and self.cap is not None: self.cap.release()
        self.destroy()

if __name__ == "__main__":
    app = CodebreakerGUI()
    app.mainloop()
