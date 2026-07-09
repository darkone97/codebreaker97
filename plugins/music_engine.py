import threading
import os
import pyautogui
import webbrowser
import time
try:
    import pywhatkit
except ImportError:
    pass

def handle_query(query, app):
    # Trigger on any command that starts with "play "
    if not query.startswith("play "):
        return False

    # Extract what comes after "play "
    command = query.replace("play ", "", 1).strip()
    
    def music_worker():
        try:
            # SCENARIO 1: The Cold Start ("play music")
            if command == "music":
                app.safe_append_chat("SYSTEM", "[Music Engine] Sending global resume signal...")
                pyautogui.press('playpause')
                time.sleep(1)
                
                app.safe_append_chat("SYSTEM", "[Music Engine] Booting native Windows audio interface...")
                app.speak_async("Resuming media. Launching default music player.")
                
                # Force-launch the Default Windows Music Player natively using Windows URI
                try:
                    os.startfile("mswindowsmusic:")
                except Exception:
                    app.safe_append_chat("ERROR", "[Music Engine] Failed to launch the native Windows media player.")
                    
            # SCENARIO 2: Specific Song Request ("play [song name]")
            else:
                app.safe_append_chat("SYSTEM", f"[Music Engine] Bypassing local storage. Routing '{command}' to YouTube Matrix...")
                app.speak_async(f"Pulling up {command} on YouTube.")
                
                try:
                    # This searches YouTube and clicks the first video automatically
                    pywhatkit.playonyt(command)
                    app.safe_append_chat("SYSTEM", "[Music Engine] Target acquired and playing.")
                except Exception:
                    app.safe_append_chat("SYSTEM", "[Warning] Autoplay failed. Defaulting to manual search.")
                    query_string = command.replace(" ", "+")
                    webbrowser.open(f"https://www.youtube.com/results?search_query={query_string}")

        except Exception as e:
            app.safe_append_chat("ERROR", f"Audio Matrix Failure: {e}")

    threading.Thread(target=music_worker, daemon=True).start()
    return True