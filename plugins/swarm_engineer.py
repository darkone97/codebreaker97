import threading
import time
try:
    import ollama
except ImportError:
    pass

def handle_query(query, app):
    # The Trigger Command
    if not query.startswith("swarm engineer "):
        return False

    task = query.replace("swarm engineer ", "", 1).strip()
    app.safe_append_chat("SYSTEM", "[Swarm Protocol] Activating Multi-Agent Pipeline...")
    app.speak_async("Activating swarm architecture.")

    def swarm_worker():
        try:
            # --- AGENT 1: The Architect (Llama 3) ---
            app.safe_append_chat("SYSTEM", "[Agent 1: Llama3 Architect] Drafting blueprint...")
            plan_prompt = f"You are the Lead System Architect. Create a highly detailed, step-by-step logic plan to build this: '{task}'. Do not write code, only write the architecture plan."
            plan = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': plan_prompt}])['message']['content']

            # --- AGENT 2: The Junior Dev (Qwen) ---
            app.safe_append_chat("SYSTEM", "[Agent 2: Qwen Junior] Writing initial draft...")
            draft_prompt = f"You are a Junior Python Developer. Follow this plan strictly and write the initial code draft:\n\n{plan}\n\nOutput ONLY Python code inside ```python tags."
            draft = ollama.chat(model='qwen2.5-coder:3b', messages=[{'role': 'user', 'content': draft_prompt}])['message']['content']

            # --- AGENT 3: The Senior Dev (Qwen) ---
            app.safe_append_chat("SYSTEM", "[Agent 3: Qwen Senior] Refactoring and optimizing...")
            refine_prompt = f"You are a Senior Python Developer. Take this junior's code and refactor it to be clean, efficient, and professional. Add necessary imports and comments.\n\nCode:\n{draft}\n\nOutput ONLY the improved Python code inside ```python tags."
            refined = ollama.chat(model='qwen2.5-coder:3b', messages=[{'role': 'user', 'content': refine_prompt}])['message']['content']

            # --- AGENT 4: The QA Tester (Qwen) ---
            app.safe_append_chat("SYSTEM", "[Agent 4: Qwen QA] Hunting for bugs and fixing errors...")
            qa_prompt = f"You are an aggressive Quality Assurance AI. Look at this code. Find any potential errors, missing variables, or logic flaws, and fix them permanently. \n\nCode:\n{refined}\n\nOutput ONLY the final, flawless Python code inside ```python tags."
            final_code = ollama.chat(model='qwen2.5-coder:3b', messages=[{'role': 'user', 'content': qa_prompt}])['message']['content']

            # --- AGENT 5: The Reviewer (Llama 3) ---
            app.safe_append_chat("SYSTEM", "[Agent 5: Llama3 Reviewer] Final sign-off...")
            summary_prompt = f"The dev team just finished this code for the task: '{task}'. Write a 2-sentence summary of what this code does for the user.\n\nCode:\n{final_code}"
            summary = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': summary_prompt}])['message']['content']

            # --- DELIVERY ---
            app.safe_append_chat("codebreaker97 (Swarm Mode)", f"{summary}\n\n{final_code}")
            app.speak_async("Swarm engineering complete. Code is ready.")
            
            # Save to memory
            app.update_chat_memory(query, f"Swarm generated code for: {task}")

        except Exception as e:
            app.safe_append_chat("ERROR", f"Swarm Pipeline Failed: {e}")

    # Run silently in the background so the UI doesn't freeze
    threading.Thread(target=swarm_worker, daemon=True).start()
    return True