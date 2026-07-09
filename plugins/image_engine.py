import urllib.request
import urllib.error
import json
import base64
import os
import threading
import subprocess
import time

def is_engine_online():
    """Pings the local server to see if Stable Diffusion is awake."""
    try:
        urllib.request.urlopen("http://127.0.0.1:7860/", timeout=2)
        return True
    except Exception:
        return False

def handle_query(query, app):
    if not query.startswith("generate image "):
        return False

    prompt = query.replace("generate image ", "", 1).strip()
    
    def render_worker():
        try:
            # --- Auto-Boot Sequence ---
            if not is_engine_online():
                app.safe_append_chat("SYSTEM", "[Image Engine] Stable Diffusion is offline. Booting the Graphics Department...")
                app.speak_async("Starting the visual rendering engine. This will take a moment.")
                
                # Launch the .bat file in a separate console window
                bat_path = r"D:\coding\stable-diffusion-webui\webui-user.bat"
                working_dir = r"D:\coding\stable-diffusion-webui"
                subprocess.Popen(bat_path, cwd=working_dir, creationflags=subprocess.CREATE_NEW_CONSOLE)
                
                # Wait for the engine to fully load (checking every 3 seconds)
                ready = False
                for _ in range(60): # Max wait time: 3 minutes
                    if is_engine_online():
                        ready = True
                        break
                    time.sleep(3)
                    
                if not ready:
                    app.safe_append_chat("ERROR", "[Image Engine] Startup timeout. The engine took too long to boot.")
                    return
                
                app.safe_append_chat("SYSTEM", "[Image Engine] Engine Online. Initiating render matrix...")
            else:
                app.safe_append_chat("SYSTEM", "[Image Engine] Engine already active. Routing prompt...")
                app.speak_async("Rendering image.")

            # --- Render Sequence ---
            url = "http://127.0.0.1:7860/sdapi/v1/txt2img"
            payload = {
                "prompt": prompt,
                "negative_prompt": "ugly, blurry, deformed, low quality, worst quality",
                "steps": 20,
                "width": 512,
                "height": 512
            }
            
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode('utf-8'))
            
            img_data = base64.b64decode(res_data['images'][0])
            filename = f"render_{threading.get_ident()}.png"
            
            with open(filename, "wb") as f:
                f.write(img_data)
            
            app.safe_append_chat("SYSTEM", f"Render complete! Saved locally as {filename}.")
            app.speak_async("Visual render complete.")
            os.startfile(filename) 

        except Exception as e:
            app.safe_append_chat("ERROR", f"Image Matrix Failure: {e}")

    threading.Thread(target=render_worker, daemon=True).start()
    return True