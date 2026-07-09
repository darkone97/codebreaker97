# Changelog

All notable changes to the Codebreaker97 project will be documented in this file.

## [v1.4.0] - Native Audio Integration
* **Added:** `music_engine.py` plugin.
* **Changed:** Replaced Spotify API calls with native `mswindowsmusic:` URI for universal Windows default player support.
* **Added:** PyWhatKit dependency for YouTube autoplay bypassing.

## [v1.3.0] - Presentation Matrix
* **Added:** `ppt_engine.py` plugin leveraging `python-pptx`.
* **Changed:** Implemented Master Template Injection. The AI now injects text directly into `template.pptx` instead of generating unformatted white slides.

## [v1.2.0] - Autonomous Graphics Department
* **Added:** `image_engine.py` bridging the terminal with Gradio/Stable Diffusion.
* **Changed:** Added auto-boot sequence utilizing `subprocess` to launch `webui-user.bat` if the API is detected as offline.

## [v1.1.0] - Cortex Pipeline
* **Added:** Direct link model downloading architecture.
* **Note:** Setup `models/Stable-diffusion` directory for direct `.safetensors` injections (e.g., GhostMix, Juggernaut Reborn).

## [v1.0.0] - Initial Commit
* **Added:** `main.py` base loop.
* **Added:** Local Ollama Llama 3 integration.
