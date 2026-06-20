import os
import subprocess
import threading

def run_command(command):
    """Runs a terminal command and returns the output silently."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except Exception as e:
        return str(e)

def handle_query(query, app):
    """
    The standard Plugin Hook. 
    'query' is the user's lowercase text. 
    'app' gives you full access to codebreaker97's UI and functions.
    """
    keywords = ["deploy codebase", "save my progress", "push to github", "commit code"]
    
    if any(k in query for k in keywords):
        app.safe_append_chat("SYSTEM", "[Git Developer] Analyzing codebase changes...")
        app.speak_async("Analyzing repository changes.")
        
        def git_worker():
            # 1. Check if git exists
            if not os.path.exists(".git"):
                app.safe_append_chat("SYSTEM", "[Git Developer] Initializing new Git repository...")
                run_command("git init")
                
            # 2. Stage all changes
            run_command("git add .")
            
            # 3. Get the raw diff to see exactly what you changed
            status_out = run_command("git status -s")
            if not status_out:
                app.safe_append_chat("SYSTEM", "[Git Developer] Workspace is clean. No changes to save.")
                app.speak_async("Workspace is clean.")
                return

            # 4. Use your Coder Brain to write the commit message!
            app.safe_append_chat("SYSTEM", "[Git Developer] Asking Architect Mode to write commit message...")
            prompt = f"I am committing code. Here is the raw git status output showing modified files:\n{status_out}\n\nWrite a short, professional, 1-sentence Git commit message describing this update. Do not wrap it in quotes."
            
            try:
                import ollama
                res = ollama.chat(model='qwen2.5-coder:3b', messages=[{'role': 'user', 'content': prompt}])
                commit_msg = res['message']['content'].strip()
            except Exception:
                commit_msg = "Automated codebase update via codebreaker97."

            # 5. Commit and Push
            run_command(f'git commit -m "{commit_msg}"')
            app.safe_append_chat("SYSTEM", f"[Git Developer] Committed with message: '{commit_msg}'")
            
            push_out = run_command("git push")
            if "fatal" in push_out.lower():
                app.safe_append_chat("ERROR", f"[Git Developer] Could not push to remote. Ensure GitHub is linked. Local commit saved.\n{push_out}")
                app.speak_async("Code saved locally, but remote push failed.")
            else:
                app.safe_append_chat("SYSTEM", "[Git Developer] Successfully deployed to remote repository.")
                app.speak_async("Codebase secured and deployed.")

        # Run in background so the UI doesn't freeze!
        threading.Thread(target=git_worker, daemon=True).start()
        
        return True # Tell main.py that this plugin handled the request

    return False # Tell main.py to keep looking
