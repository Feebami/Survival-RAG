# 🌲 Survival RAG Oracle

**A completely offline, local AI survival assistant.**

The **Survival RAG Oracle** is a standalone chatbot designed to run on a standard gaming PC without any internet connection. It combines the reasoning power of modern AI (Llama 3.1) with a curated library of survival manuals, effectively acting as an interactive expert that you can carry in your pocket.

### 🎯 Project Goal
To provide a resilient, "knowledge-in-a-box" tool. Whether you are prepping for emergencies, camping off-grid, or just want a private AI assistant, this tool allows you to:
*   **Chat with a survival expert:** Ask questions like *"How do I start a fire with wet wood?"* or *"What plants are edible in North America?"*
*   **Zero Data Leakage:** Everything runs locally on your machine. No data is sent to the cloud.
*   **Portable:** Can be configured to run directly from a high-speed USB flash drive.

## 🛠️ System Requirements
*   **OS:** Windows 10 or 11
*   **Hardware:** A PC with a dedicated GPU (NVIDIA GTX/RTX or AMD Radeon) recommended for speed. (at least 12 GB VRAM recommended)
    *   *Can run on CPU-only, but responses will be very slow.*
*   **Space:** ~8 GB free space (mostly for the AI models).

## 🚀 Installation & Setup

Follow these steps once to set up the system. After setup, no internet is required.

### 1. Download this Repository
Click the green **Code** button above -> **Download ZIP**. Extract the folder to a location on your computer (e.g., `Documents\Survival_RAG` or your Flash Drive).

### 2. The "Side Quest": Install Ollama 🦙
This tool uses **Ollama** as its engine. Since Ollama is a separate program and too large to include in this repository, you need to add it to this folder manually.

1.  **Download Ollama** for Windows from [ollama.com](https://ollama.com/download/windows).
2.  Run the installer to install it on your PC.
3.  **Navigate to the install folder:**
    *   Press `Win + R`, paste this, and hit Enter: `%LOCALAPPDATA%\Programs\Ollama`
    *   Alternatively, you can find it in `C:\Users\<YourUsername>\AppData\Local\Programs\Ollama`
4.  **Copy EVERYTHING** in that folder (you should see `ollama.exe`, `lib`, etc.).
5.  **Paste it** into the `ollama` folder inside this project (`Survival_RAG\ollama\`).
    *   *Note: You can uninstall Ollama from your PC after copying the files. This isn't necessary and having Ollama installed locally can be useful. Copying the files to this project ensures portability.*

### 3. Run the Auto-Setup
A script is included to download the necessary AI brains and Python libraries for you.

1.  Double-click **`setup.bat`**.
2.  Wait for it to finish. It will:
    *   Check for the Ollama executable you just copied into the project.
    *   Install Python libraries (Chainlit, LangChain, etc.).
    *   Download the **Llama 3.1** AI model.
    *   Download the **bge-m3** embedding model.
    *   *This step requires an internet connection.*

## 💻 How to Use

### Start the Oracle (RAG Mode)
This is the main mode. The AI will answer questions using the survival manuals in its database.

1.  Double-click **`run.bat`**.
2.  Wait for the console to say "System ready!".
3.  A browser window should open automatically to `http://localhost:8000`.
4.  Start chatting!

### Chat with Llama 3.1 (Pure LLM Mode)
If you just want to talk to the raw AI model without the survival manual context retrieval in the terminal window, follow these steps:

1.  Open the ollama folder in Terminal:
    *   Right-click the `ollama` folder while holding `Shift` -> **Open in Terminal**.
2.  Run these commands:
    *   `$env:OLLAMA_MODELS = "$PWD\models"`
    *   `.\ollama.exe serve`
3.  Keep the terminal open and open another terminal from the ollama folder.
4.  Run this command to chat:
    *   `.\ollama.exe run llama3.1`

## ⚠️ Troubleshooting

**"The system cannot find the path specified..."**
*   Ensure you extracted the ZIP file. Do not run `.bat` files directly from inside the ZIP.
*   Ensure you copied the **contents** of the Ollama folder, not the folder itself (e.g., `Survival_RAG\ollama\ollama.exe` should exist).

**"Torch not compiled with CUDA enabled" / Slow Performance**
*   The system is running on your CPU. This happens if you don't have a dedicated GPU or if drivers are missing. It will still work, but answers will take a LONG time.

**Browser doesn't open**
*   Manually open your browser and go to: `http://localhost:8000`

## 📂 Project Structure

*   `data/`: Contains the Vector Database (`chroma_db`), original text chunks, and the cleaned text used for vectorization.
*   `ollama/`: The AI engine binaries and model files (models stored in `ollama/models`).
*   `python-312/`: A portable, self-contained Python runtime.
*   `chat.py`: The main application code using Chainlit and LangChain.
*   `vectorize.py`: Code to create the vector database from text files.
*   `setup.bat`: The setup script to download models and install dependencies.
*   `run.bat`: The script to start the chat application.
*   `other .py files`: Scripts for text processing and testing. Some cleaning and preparation of the corpus was done by hand, so results may vary.

## 🐧 For Linux & Power Users

If you are comfortable with the command line (Linux/macOS) and already have Python 3.11+ and Ollama installed, you don't need the bundled Windows executables.

### Prerequisites

*   Python 3.11+ installed
*   Ollama installed and set up
*   This repository cloned/downloaded

### Quick Setup

```bash
# Install Dependencies
pip install -r requirements.txt
# Pull Models
ollama pull llama3.1
ollama pull bge-m3
```

### Run the Application

```bash
# Start Ollama (if not running as a service)
ollama serve &
# Run the chat application
chainlit run chat.py -w
```

### Please Note:

*If intending to use this on a portable drive, the Linux system will require python, it's dependencies, Ollama, and the models installed on the host machine. Windows instructions and portability are provided above and intended for use on sufficiently powerful Windows machines e.g. Gaming PCs.*

*The limitations described here can be mitigated by installing the prerequisites into the project folder as done with the Windows instructions, but results may vary given different Linux system configurations.*

## 🙏 End Notes

Thanks for checking out the Survival RAG Oracle! This is a personal project born from my interest in survival skills and AI technology. It has a lot of room for improvement (improved corpus, prompt engineering, agentic RAG), so feel free to fork it and make your own enhancements. Stay safe out there!

## 📜 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.