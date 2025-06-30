# AI Meme Factory

An AI-powered newsletter generator that makes staying informed fun and accessible. In today's fast-paced world, where attention spans are shrinking and information overload is common, young people often struggle to keep up with important news and developments. AI Meme Factory bridges this gap by transforming complex news articles into engaging memes, making it easier for everyone to stay informed about the latest trends and events.

Using cutting-edge AI technologies, the project generates memes that capture the essence of trending topics, helping users stay up-to-date with the state of the art in various fields. Choose between cloud mode (using OpenAI API) or local mode (using Stable Diffusion) for meme generation.

## Features

- 📰 Automated news article collection using NewsAPI
- 🤖 AI-generated meme prompts based on trending topics
- 🎨 High-quality meme generation using either OpenAI or Stable Diffusion
- 📊 Real-time analytics and database tracking
- 🌐 Two operating modes: Cloud (OpenAI) or Local (Stable Diffusion)
- 🔄 Dynamic meme generation based on current news

## Getting Started

Detailed setup and running instructions are available in the [RUN.md](RUN.md) file.

## Requirements

### Common Requirements
- Python 3.8+
- NEWS_API_KEY (Free from https://newsapi.org/)
- GEMINI_API_KEY (Free from https://aistudio.google.com/apikey)

### Cloud Mode (Default)
- OPENAI_API_KEY (Paid from https://platform.openai.com/settings/organization/api-keys)

### Local Mode
- Stable Diffusion dependencies (see RUN.md)
- GPU recommended for better performance

## Project Structure

- `app.py` - Main Flask application
- `src/` - Core functionality
  - `news_aggregator.py` - News collection
  - `filter_top_k.py` - Article filtering
  - `prompt_generator.py` - Meme prompt generation
  - `meme_generator.py` - Cloud meme generation
  - `meme_generator_local.py` - Local meme generation
- `database/` - Data storage

## Running the Application

See [RUN.md](RUN.md) for detailed running instructions.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- NewsAPI for news aggregation
- OpenAI for cloud meme generation
- Stable Diffusion for local meme generation
- Google Gemini for AI assistance