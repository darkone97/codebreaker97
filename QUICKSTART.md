# J.A.R.V.I.S. Quick Start Guide

## 🚀 Installation

### 1. Install Required Packages
```bash
pip install opencv-python customtkinter torch ultralytics easyocr ollama pyttsx3 pyperclip screen-brightness-control SpeechRecognition PyMuPDF requests beautifulsoup4 translatepy psutil pyautogui numpy
```

### 2. Start Ollama Server
```bash
ollama serve
```
*In another terminal window, ensure Ollama is running with Llama 3*

### 3. Launch J.A.R.V.I.S.
```bash
python main.py
```

---

## 💡 First Commands to Try

### 1. Help Menu
```
Type: "help" or "commands"
```
This displays all available commands with descriptions.

### 2. Activate Vision
```
Type: "start vision"
Speak/Type: "what am i doing?"
Type: "stop vision"
```
This activates the camera and analyzes what's visible.

### 3. System Status
```
Type: "system info"
```
Shows CPU, RAM, Disk, Battery, and system information.

### 4. Take Notes
```
Type: "take a note remember to call John"
Type: "show notes"
```
Persistent note-taking system.

### 5. Ask a Question
```
Type: "What is the capital of France?"
```
Full LLM reasoning with intelligent responses.

---

## 🎤 Voice Mode

### Enable Voice Recognition
1. Click **"🎤 Voice"** button OR type **"start listening"**
2. The button turns cyan and shows **"🎙️ Active"**
3. Speak your commands naturally
4. The system continuously listens and processes

### Disable Voice
- Type any text command, or
- Click the voice button again, or
- Say **"stop listening"**

---

## 📁 File Management

### Upload Documents
1. Click **"📎"** (paperclip icon)
2. Select a PDF or image file
3. The system auto-suggests a command
4. Press Enter or modify and submit

### Extract Text from Images
```
Type: "read the image filename.png"
```

### Extract Text from PDFs
```
Type: "read the file document.pdf and summarize it"
```

---

## 🔋 Battery-Saving Privacy Features

### Camera Management
- **Camera is OFF at boot** → No battery drain
- **"start vision"** → Physically powers on camera
- **"stop vision"** → Physically cuts power
- Green light only appears when camera is active

### Smart Model Loading
- YOLO loads only when you say "start vision"
- OCR loads once on startup
- LLM ready immediately

---

## 📚 Common Workflows

### Workflow 1: Document Analysis
```
1. Upload a PDF using paperclip icon
2. Type: "read the file [name] and analyze it"
3. Ask follow-up questions about the document
```

### Workflow 2: Real-Time Vision Analysis
```
1. Type: "start vision"
2. Point camera at something
3. Type: "what am i holding?"
4. Get instant AI analysis
5. Type: "stop vision"
```

### Workflow 3: Research & Summarization
```
1. Type: "search latest AI breakthroughs"
2. Type: "translate that to Spanish"
3. Type: "remember this information"
```

### Workflow 4: System Maintenance
```
1. Type: "screenshot"
2. Type: "system info"
3. Type: "brightness 50"
4. Type: "open notepad"
```

---

## 🎯 Pro Tips

### 1. Memory System
- **"remember [important info]"** - Persist data across sessions
- **"what do you remember"** - Recall stored memories
- Great for tracking personal data, preferences, schedules

### 2. Calculator
- Use for quick math: **"calculate 25 * 4 + 10"**
- Works with complex expressions including `^` for powers

### 3. Timer Function
- **"timer 5"** sets a 5-minute timer
- Timer runs in background, audio alert when complete
- Multiple timers can run simultaneously

### 4. Clipboard Integration
- **"copy to clipboard [text]"** - Quick copy
- **"read clipboard"** - Paste and analyze
- Great for text processing workflows

### 5. Translation
- **"translate hello world to Japanese"** - Instant translation
- Works with any ISO language code (es, fr, de, zh, ja, etc.)

### 6. Multi-Turn Conversations
- System maintains last 10 messages
- Ask follow-up questions naturally
- Context-aware responses

---

## ⚙️ Customization

### Adjust TTS Speed
Edit line 57 in main.py:
```python
engine.setProperty('rate', 150)  # Change 150 to desired WPM
```

### Change Camera Confidence Threshold
Edit YOLO process_query section:
```python
if conf > 0.25:  # Change 0.25 to desired confidence
```

### Modify Brightness Range
Windows brightness supports 0-100 range naturally.

---

## 🆘 Troubleshooting

### Ollama Not Found
- Ensure Ollama is running: `ollama serve`
- Check Ollama is on http://localhost:11434

### Microphone Not Working
- Check Windows Microphone permissions
- Test with Windows Sound settings first
- Ensure no other app is using microphone

### Camera Not Loading
- Try: **"start vision"** then wait 5 seconds
- Check if camera is already in use by another app
- Verify camera permissions in Windows

### GPU Not Accelerating
- For YOLO: Install CUDA and cuDNN
- For EasyOCR: Install torch with CUDA support
- `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`

### Brightness Control Fails
- Ensure monitor supports DDC-CI
- Check Windows driver support
- Some virtual machines don't support brightness control

---

## 🔒 Privacy Checklist

- ✅ Camera off until you activate it
- ✅ Local OCR processing (no cloud required)
- ✅ Local YOLO object detection
- ✅ Optional web search only when requested
- ✅ Notes and memories stored locally
- ✅ No telemetry or tracking
- ✅ All processing on your machine

---

## 📈 Performance Tips

1. **First run**: YOLO download takes ~1-2 minutes on first activation
2. **Subsequent runs**: Loads from cache instantly
3. **Voice recognition**: Takes 1-2 seconds to process
4. **OCR on images**: 5-15 seconds depending on image size
5. **Web searches**: 3-5 seconds depending on internet speed

---

## 🎓 Learning Resources

- Check **FEATURES.md** for complete command reference
- Type **"help"** anytime to see all available commands
- Try voice mode to experience natural interaction
- Experiment with combining features (e.g., screenshot + search)

---

## 📞 Support

If you encounter issues:
1. Check error message in the chat display
2. Verify all dependencies are installed
3. Ensure Ollama server is running
4. Check Python version is 3.9+
5. Review the FEATURES.md for detailed documentation

---

**Happy Assisting with J.A.R.V.I.S.! 🚀**

Current Version: 2.0 - Multimodal AI Edition
Last Updated: 2026-06-16
