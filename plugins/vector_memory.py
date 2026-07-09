import os
import threading

try:
    import chromadb
    import ollama
except ImportError:
    chromadb = None

def handle_query(query, app):
    # Failsafe: If libraries aren't installed, let main.py handle the query normally
    if chromadb is None:
        return False

    # Initialize the local vector database silently
    client = chromadb.PersistentClient(path="./security_logs/vector_vault")
    collection = client.get_or_create_collection(name="long_term_memory")

    # --- ACTION 1: SAVE A MEMORY ---
    if query.startswith("remember "):
        fact = query.replace("remember ", "", 1).strip()
        app.safe_append_chat("SYSTEM", "[Vector Vault] Encrypting and storing memory...")
        app.speak_async("Securing memory in the vault.")
        
        def save_memory():
            try:
                # Convert the text into mathematics (Embeddings)
                embed = ollama.embeddings(model='nomic-embed-text', prompt=fact)['embedding']
                import time
                doc_id = f"mem_{int(time.time())}"
                
                # Store the math and the text in the local database
                collection.add(embeddings=[embed], documents=[fact], ids=[doc_id])
                app.safe_append_chat("SYSTEM", "[Vector Vault] Memory successfully encoded.")
            except Exception as e:
                app.safe_append_chat("ERROR", f"Vault Encoding Error: {e}")
        
        threading.Thread(target=save_memory, daemon=True).start()
        return True # Tell main.py we handled this

    # --- ACTION 2: PROACTIVE RECALL ---
    # Skip short queries or hardware commands to save processing time
    skip_words = ["play music", "stop", "volume", "screenshot", "time", "start vision"]
    if any(k in query for k in skip_words) or len(query) < 8:
        return False

    try:
        # Check the vault to see if the database is empty
        if collection.count() == 0:
            return False

        # Convert the user's question into math to search for meaning
        query_embed = ollama.embeddings(model='nomic-embed-text', prompt=query)['embedding']
        results = collection.query(query_embeddings=[query_embed], n_results=1)
        
        # If we find a highly relevant memory (distance < 1.0)
        if results['distances'] and results['distances'][0] and results['distances'][0][0] < 1.0:
            memory_context = results['documents'][0][0]
            app.safe_append_chat("SYSTEM", f"[Vector Vault] Accessing relevant memory: '{memory_context[:40]}...'")
            
            def answer_with_memory():
                prompt = f"Context from your past memory: '{memory_context}'\n\nUser Query: {query}\n\nAnswer the user utilizing the memory context provided."
                try:
                    res = ollama.chat(model='llama3', messages=[
                        {'role': 'system', 'content': 'You are codebreaker97. Be brief and helpful.'}, 
                        {'role': 'user', 'content': prompt}
                    ])
                    reply = res['message']['content']
                    
                    app.safe_append_chat("codebreaker97 (Augmented)", reply)
                    app.speak_async(reply)
                    
                    # Update persistent memory across threads
                    app.update_chat_memory(query, reply)
                except Exception as e:
                    app.safe_append_chat("ERROR", f"Augmented LLM Error: {e}")

            threading.Thread(target=answer_with_memory, daemon=True).start()
            return True # Take over the response!
            
    except Exception as e:
        pass # If the database search fails for any reason, fail silently and let main.py answer normally

    return False # No relevant memory found, pass control back to main.py