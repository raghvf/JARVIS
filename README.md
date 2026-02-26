# JARVIS - AI Voice Assistant

## Project Overview
Developed a comprehensive voice-activated AI assistant application that integrates natural language processing, real-time web search, system automation, and conversational AI capabilities. The system processes voice commands through a multi-layered decision-making architecture to intelligently route queries and execute tasks.

## Key Features & Technical Implementation

### Core Architecture
- **Multi-threaded Application**: Implemented concurrent processing with separate threads for voice recognition and GUI rendering to ensure responsive user experience
- **Decision-Making Model**: Built a first-layer classification system using Cohere API to categorize user queries into general conversation, real-time information requests, or automation tasks
- **Modular Backend Design**: Structured codebase with separate modules for speech processing, chatbot logic, automation, and search functionality

### Voice Recognition & Speech Processing
- Integrated Selenium WebDriver with Chrome headless browser to access browser-based Web Speech API for real-time voice recognition
- Implemented multi-language support with automatic translation using mtranslate library
- Developed text-to-speech functionality using Microsoft Edge TTS API with customizable voice parameters and intelligent response truncation for long-form content

### AI Chatbot & Natural Language Understanding
- Leveraged Groq API with Llama 3.1 and Llama 3.3 models for conversational AI responses
- Implemented persistent chat history management using JSON-based storage with conversation context preservation
- Designed system prompts with real-time date/time context injection for accurate temporal responses

### Real-Time Information Retrieval
- Built a real-time search engine that integrates Google Search API to fetch current information from the web
- Implemented web scraping with BeautifulSoup to extract and parse search results
- Combined search results with LLM processing to generate contextually relevant, up-to-date answers

### System Automation & Task Execution
- Developed automation framework supporting application management (open/close), media playback, and system controls
- Integrated AppOpener library for intelligent application detection and launching
- Implemented YouTube integration for video search and playback using pywhatkit
- Created system control functions for volume management using keyboard automation
- Built AI-powered content generation system that creates documents (letters, applications, essays) and automatically opens them in Notepad

### Image Generation
- Integrated Hugging Face Stable Diffusion XL API for AI-powered image generation from text prompts
- Implemented asynchronous image processing with automatic file management and display

### User Interface
- Designed modern PyQt5-based graphical interface with animated GIFs, real-time status updates, and chat visualization
- Implemented responsive UI components with dynamic status indicators for microphone, assistant state, and task execution
- Created seamless integration between voice input, text display, and audio output

## Technical Stack
- **Languages**: Python 3.x
- **AI/ML APIs**: Groq (Llama models), Cohere (classification), Hugging Face (image generation)
- **Libraries**: PyQt5, Selenium, BeautifulSoup, Edge TTS, pygame, AppOpener, pywhatkit
- **Architecture**: Multi-threaded, modular design with async/await patterns
- **Data Storage**: JSON-based chat logs, file-based configuration management

## Technical Achievements
- Successfully integrated multiple third-party APIs (Groq, Cohere, Hugging Face, Google Search) with error handling and fallback mechanisms
- Implemented intelligent query routing system that automatically determines the appropriate processing method based on query type
- Designed scalable architecture supporting concurrent voice recognition, GUI updates, and background task execution
- Created robust error handling and logging system for production-ready deployment

## Impact & Results
- Delivered a fully functional voice assistant capable of handling diverse user queries ranging from conversational interactions to system automation
- Demonstrated proficiency in API integration, natural language processing, and multi-threaded application development
- Showcased ability to combine multiple technologies (speech recognition, AI models, web scraping, automation) into a cohesive user experience

