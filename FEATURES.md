# Codebreaker97: System Features

Codebreaker97 is a fully modular, AI-driven local operating system. It acts as a central CEO, routing commands to specialized subsystems and background matrixes.

## Core Capabilities
* **Local LLM Cortex:** Powered by Llama 3 (via Ollama) for completely offline, private, and uncensored conversational processing.
* **Extensible Plugin Architecture:** Modular `plugins/` folder allows hot-swapping Python scripts without altering the main loop.

## Active Subsystems
* **Image Engine (Stable Diffusion Bridge):** 
  * Intercepts `generate image` commands.
  * Autonomously boots the Automatic1111 WebUI background process if it is offline.
  * Injects custom prompts, Negative Prompts, and rendering settings.
  * Auto-displays the final rendered `.png` directly on the host screen.
* **Presentation Engine:** 
  * Intercepts `create a ppt on` commands.
  * Brainstorms strict slide structures using Llama 3.
  * Injects the generated text into a custom master design shell (`template.pptx`).
  * Autonomously opens Microsoft PowerPoint with the finished deck.
* **Music Engine:** 
  * Intercepts `play music` to trigger native Windows media resume (`mswindowsmusic:` protocol).
  * Intercepts `play [song]` to bypass local storage, auto-search, and play specific tracks directly via YouTube using PyWhatKit.
* **Sensory Accessibility Engine:**
  * Real-time voice synthesis and auditory feedback (pyttsx3).
  * (In Development) Microphone transcription and webcam-based skeletal hand-tracking via MediaPipe.
