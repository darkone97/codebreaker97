# Codebreaker97 🧠💻

Codebreaker97 is an autonomous, fully local AI operating system. Built on a modular architecture, it uses a local Large Language Model as the central "CEO" to interpret natural language commands and seamlessly route them to specialized background matrixes (plugins) to execute complex tasks across the host machine.

## 🚀 Overview
Instead of just chatting, Codebreaker97 takes physical action. By bridging terminal-based text prediction with local system execution, this OS can autonomously render graphics, compile presentations, and control native media without the user ever leaving the command line.

## 🧩 Core Architecture
* **The Core (LLM):** Powered by Llama 3 via Ollama, ensuring 100% offline, uncensored, and private reasoning.
* **The Plugin Matrix:** A hot-swappable `plugins/` directory allows for infinite expansion of the AI's capabilities without altering the main event loop.
* **The Sensory Cortex:** Built-in hooks for voice synthesis, microphone transcription, and real-time computer vision tracking.

## 📚 Documentation
For detailed information on setting up, configuring, and utilizing Codebreaker97, refer to the following documents:
* [**QUICKSTART.md**](QUICKSTART.md) - Step-by-step installation instructions and first-run guide.
* [**FEATURES.md**](FEATURES.md) - Deep dive into the active subsystems and exact command triggers.
* [**CHANGELOG.md**](CHANGELOG.md) - Version history, feature updates, and patch notes.

## ⚙️ Active Subsystems
* **Stable Diffusion Bridge:** Autonomously boots and commands a local Automatic1111 WebUI to generate high-res images using custom hardware checkpoints.
* **Presentation Generator:** Brainstorms topics and injects Llama 3's formatted text directly into custom `.pptx` master templates.
* **Native Media Controller:** Intercepts audio commands to wake up native Windows media or bypass local storage to stream specific tracks directly from the web.

---
*Built for the terminal. No cloud required.*
