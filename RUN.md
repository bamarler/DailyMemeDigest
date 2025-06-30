# AI Meme Factory - Running Modes

## Overview

The AI Meme Factory can run in two modes:
- **Cloud Mode (Default)**: Uses OpenAI API for meme generation - slower but higher quality
- **Local Mode**: Uses Stable Diffusion locally - faster but requires good hardware

## How to Run

### Python Environment Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Cloud Mode (Default)
```bash
python meme.py
```

### Local Mode
```bash
python meme.py local
```

### With Custom Port
```bash
python meme.py cloud 8080
python meme.py local 8080
```

### Help
```bash
python meme.py --help
```

## Required API Keys

### Both Modes Need:
- **NEWS_API_KEY** - Get FREE key at https://newsapi.org/
- **GEMINI_API_KEY** - Get FREE key at https://aistudio.google.com/apikey

### Cloud Mode Also Needs:
- **OPENAI_API_KEY** - Get PAID key at https://platform.openai.com/settings/organization/api-keys

### Local Mode Setup:
First time setup for local mode:
```bash
pip install -r requirements-local.txt
```

For GPU support (recommended):
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install diffusers transformers accelerate pillow google-generativeai xformers
```

## Performance Comparison

| Feature | Cloud Mode (OpenAI) | Local Mode (SD) |
|---------|-------------------|-----------------|
| Setup Complexity | Easy | Moderate |
| Cost | Pay per image (see below) | Free (local hardware) |
| Speed | Slow | Fast |
| Quality | Excellent | Good |
| GPU Required | No | Recommended |
| Internet Required | Yes | Yes (for news) |

### Cloud Mode Token Costs (Square 1024x1024)
- **Low Quality**: 272 tokens
- **Medium Quality**: 1056 tokens  
- **High Quality**: 4160 tokens

## Environment Variables

Create a `.env` file with your API keys:

```bash
# Always required
NEWS_API_KEY=your-news-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here

# For cloud mode
OPENAI_API_KEY=your-openai-key-here

# Optional
SAVE_MEMES_TO_DISK=true  # Save memes locally (local mode only)
```

## Troubleshooting

### Check if GPU is available (for local mode)
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

### Missing Dependencies
The app will tell you exactly what to install if dependencies are missing when running in local mode.

### Slow Generation on CPU
CPU generation can take 30+ seconds per image. Consider using cloud mode or getting a GPU for local mode.