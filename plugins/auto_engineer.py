import threading
import time
try:
    import ollama
except ImportError:
    pass

def handle_query(query, app):
    # The Trigger Command
    if not query.startswith("auto engineer "):
        return False

    task = query.replace("auto engineer ", "", 1).strip()
    app.safe_append_chat("SYSTEM", "[Agent Loop] Initializing Strike Team (Llama3 & Qwen)...")
    app.speak_async("Initializing multi-agent strike team.")

    def agent_loop_worker():
        max_loops = 3 # Hard limit to save your hardware
        
        # 1. Llama 3 writes the Master Plan
        app.safe_append_chat("SYSTEM", "[Llama 3] Drafting architecture plan...")
        plan_prompt = f"You are the Senior Architect. Break this task into clear, logical steps for a junior Python developer: {task}. Keep it brief."
        try:
            plan = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': plan_prompt}])['message']['content']
        except Exception as e:
            app.safe_append_chat("ERROR", f"Llama Plan Failed: {e}")
            return

        current_code = ""

        # 2. The Multi-Agent Cycle
        for i in range(max_loops):
            app.safe_append_chat("SYSTEM", f"--- CYCLE {i+1} ---")
            
            # --- QWEN CODER PHASE ---
            app.safe_append_chat("SYSTEM", "[Qwen Coder] Writing code based on plan/feedback...")
            qwen_prompt = f"Task Plan: {plan}\n\nPrevious Code (if any): {current_code}\n\nWrite or fix the Python code. Output ONLY valid Python code inside ```python tags. Do not explain yourself."
            
            try:
                qwen_response = ollama.chat(model='qwen2.5-coder:3b', messages=[{'role': 'user', 'content': qwen_prompt}])['message']['content']
                current_code = qwen_response
            except Exception as e:
                app.safe_append_chat("ERROR", f"Qwen Build Failed: {e}")
                break

            # --- LLAMA 3 REVIEW PHASE ---
            app.safe_append_chat("SYSTEM", "[Llama 3] Reviewing Qwen's code...")
            llama_review_prompt = f"You are a strict Code Reviewer. Review this code for the task: '{task}'.\n\nCode:\n{current_code}\n\nIf the code is perfect, reply with ONLY the exact word 'APPROVED'. If it has errors, list them briefly so the developer can fix it."
            
            try:
                review = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': llama_review_prompt}])['message']['content']
            except Exception as e:
                app.safe_append_chat("ERROR", f"Llama Review Failed: {e}")
                break

            # The Early Exit Trigger
            if "APPROVED" in review.upper():
                app.safe_append_chat("SYSTEM", f"[Llama 3] Code approved on cycle {i+1}!")
                break
            else:
                app.safe_append_chat("SYSTEM", f"[Llama 3 Feedback] {review[:100]}...")
                plan = f"Fix these issues: {review}" # Feed the errors back into the next loop

        # 3. Deliver the Final Product
        app.safe_append_chat("codebreaker97 (Agent Loop)", f"Here is the final verified code for: {task}\n\n{current_code}")
        app.speak_async("Engineering task complete. Code is ready for review.")
        
        # Save to short-term memory
        app.update_chat_memory(query, f"Generated verified code for: {task}")

    # Run entirely in the background
    threading.Thread(target=agent_loop_worker, daemon=True).start()
    return True