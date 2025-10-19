# 🎬 VidyAI Vizuara - Wikipedia Comic Video Generator

A powerful AI-driven application that transforms Wikipedia articles into engaging comic video stories with professional narration using advanced language models, image generation technology, and text-to-speech. This project combines Wikipedia content extraction, AI-powered story generation, automated comic panel creation, intelligent narration generation, voice synthesis, and video editing to produce educational and entertaining visual narratives.

## 🎯 Project Overview

VidyAI Vizuara is an innovative tool that creates complete video stories from Wikipedia articles:
- 🔍 Extracts content from Wikipedia articles in multiple languages
- 📖 Uses AI to generate compelling comic book storylines
- 🎬 Creates detailed scene prompts for visual storytelling
- 🎨 Generates high-quality comic panel images using free AI models
- 🎙️ Generates professional scene-by-scene narration
- 🔊 Converts narrations to high-quality voiceovers using Edge TTS
- 🎥 Assembles everything into a final video with transitions and audio
- 💾 Saves all content in organized files for reuse
- 🖥️ Provides beautiful, modern web UI with step-by-step workflow

## ✨ Latest Updates & Fixes

### Version 3.0 - Major Improvements
1. **✅ Fixed Voice Generation**: Audio now generates automatically for all scenes with proper error handling
2. **✅ Fixed Image Generation**: Now uses free Stable Diffusion models by default with better fallback handling
3. **✅ Fixed Video Generation**: Improved workflow ensures video assembly works seamlessly
4. **✅ Redesigned UI**: Beautiful modern interface with:
   - Gradient backgrounds and card-based layout
   - Step-by-step progress indicator
   - Organized settings in collapsible sections
   - Better visual feedback and status messages
   - Professional styling with hover effects and animations

### Key Improvements
- 🎵 **Automatic TTS**: Narrations automatically convert to MP3 using Microsoft Edge TTS
- 🖼️ **Free Models**: Uses Stable Diffusion 2.1 by default (no payment required)
- 🔄 **Better Error Handling**: Improved retry logic and fallback mechanisms
- 📊 **Progress Tracking**: Real-time status updates during generation
- 🎨 **Modern Design**: Completely redesigned UI with gradient themes and professional styling

## 🚀 Features

### Core Functionality
- **Multi-language Wikipedia Support**: Extract content from Wikipedia in 9 different languages
- **AI-Powered Story Generation**: Transform factual content into engaging comic narratives
- **Intelligent Scene Creation**: Generate detailed visual prompts for comic panels
- **Multiple Art Styles**: Support for various comic art styles (manga, superhero, noir, etc.)
- **Free Image Generation**: Uses Stable Diffusion models (no payment required)
- **Professional Voice Synthesis**: High-quality TTS using Microsoft Edge voices
- **Automatic Video Assembly**: Seamless video creation with transitions and audio sync
- **🎙️ Professional Narration**: Generate scene-by-scene narration with multiple styles and tones
- **📁 Text File Management**: Automatically save all generated content in organized text files
- **🔄 Content Reusability**: Use saved text files as input for other LLMs and applications

### User Interface
- **Streamlit Web App**: Interactive web interface for easy use
- **Flask API**: RESTful API for programmatic access
- **Real-time Progress**: Live updates during generation process
- **Download Options**: Export storylines and generated images

## 🏗️ Architecture

### Project Structure
```
genai/
├── README.md
├── vidai.ipynb
└── wiki_streamlit/
    ├── final.py                 # Main Streamlit application
    ├── app.py                   # Flask API server
    ├── requirements.txt         # Python dependencies
    ├── wiki_comic_generator.log # Application logs
    ├── .env_example             # Environment variables template
    ├── .gitignore               # Git ignore file
    ├── wikipedia_extractor.py   # Wikipedia content extraction module
    ├── story_generator.py       # AI story generation module
    ├── comic_image_generator.py # Image generation module
    ├── narration_generator.py   # NEW: Narration generation module
    ├── data/                    # Generated content storage
    │   ├── images/             # Generated comic panels
    │   │   ├── Ramayana/
    │   │   ├── Shivaji/
    │   │   ├── World War II/
    │   │   └── FIFA World Cup/
    │   ├── text/               # NEW: Text content storage
    │   │   └── [Topic Name]/
    │   │       ├── [Topic]_storyline.txt
    │   │       ├── [Topic]_scene_prompts.txt
    │   │       ├── [Topic]_page_info.json
    │   │       └── [Topic]_combined.txt
    │   ├── narration/          # NEW: Narration files
    │   │   └── [Topic Name]/
    │   │       ├── scene_1_narration.txt
    │   │       ├── scene_2_narration.txt
    │   │       ├── [Topic]_complete_narration.txt
    │   │       └── [Topic]_narrations.json
    │   └── *_data.json         # Extracted Wikipedia data
    └── test/                    # Test files and documentation
        ├── info.txt
        ├── proposal.txt
        └── test1.txt
```

### System Components

#### 1. Wikipedia Content Extraction (`WikipediaExtractor`)
- **Purpose**: Fetches and processes Wikipedia articles
- **Features**:
  - Multi-language support (EN, ES, FR, DE, IT, PT, RU, JA, ZH)
  - Disambiguation handling
  - Content sanitization and formatting
  - Automatic retry with exponential backoff
  - Data persistence to JSON files

#### 2. AI Story Generation (`StoryGenerator`)
- **Purpose**: Converts Wikipedia content into comic storylines
- **AI Model**: Groq's LLaMA 3.1 8B Instant
- **Features**:
  - Configurable story length (short/medium/long)
  - Character development and dialogue generation
  - Scene-by-scene narrative structure
  - Educational content integration
  - **NEW**: Automatic text file storage and organization
  - **NEW**: JSON export for programmatic access

#### 3. Scene Prompt Generation
- **Purpose**: Creates detailed visual descriptions for image generation
- **Features**:
  - Style-specific guidance (manga, superhero, noir, etc.)
  - Age-appropriate content filtering
  - Education level customization
  - Character consistency maintenance

#### 4. Image Generation (`ComicImageGenerator`)
- **Purpose**: Generates comic panel images from text prompts
- **Primary Model**: Black Forest Labs FLUX.1-dev
- **Fallback Model**: RunwayML Stable Diffusion v1.5
- **Features**:
  - Automatic fallback on API failures
  - Payment error handling
  - Placeholder image generation
  - Batch processing capabilities

#### 5. Narration Generation (`NarrationGenerator`) - NEW!
- **Purpose**: Generates professional scene-by-scene narration
- **AI Model**: Groq's LLaMA 3.1 8B Instant
- **Features**:
  - Multiple narration styles (dramatic, educational, storytelling, documentary)
  - Various voice tones (engaging, serious, playful, informative)
  - Scene-specific narration generation
  - Automatic text file organization
  - JSON export for programmatic access
  - Voice-over ready formatting

## 🤖 AI Models Used

### 1. Groq LLaMA 3.1 8B Instant
- **Provider**: Groq
- **Purpose**: Text generation for storylines and scene prompts
- **Capabilities**:
  - Fast inference (up to 500+ tokens/second)
  - High-quality text generation
  - Context understanding up to 8K tokens
  - Optimized for creative writing tasks

**Usage in Project**:
- Generates comic storylines from Wikipedia content
- Creates detailed scene descriptions for image generation
- Handles character dialogue and narrative structure
- **NEW**: Generates professional scene-by-scene narration
- **NEW**: Creates voice-over ready text content

### 2. Black Forest Labs FLUX.1-dev
- **Provider**: Hugging Face Inference API
- **Purpose**: Primary image generation model
- **Capabilities**:
  - State-of-the-art text-to-image generation
  - High-resolution output (1024x1024)
  - Excellent prompt following
  - Photorealistic and artistic styles

**Usage in Project**:
- Generates comic panel images from scene prompts
- Supports various art styles and visual themes
- Produces high-quality visual content

### 3. RunwayML Stable Diffusion v1.5
- **Provider**: Hugging Face Inference API
- **Purpose**: Fallback image generation model
- **Capabilities**:
  - Reliable text-to-image generation
  - Good prompt understanding
  - Free tier availability
  - Consistent output quality

**Usage in Project**:
- Serves as backup when primary model fails
- Handles payment/quota issues gracefully
- Ensures project reliability

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Internet connection for API access

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd genai/wiki_streamlit
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Set Up API Keys
Create a `.env` file in the `wiki_streamlit` directory:
```env
GROQ_API_KEY=your_groq_api_key_here
HF_API_TOKEN=your_huggingface_token_here
```

**API Key Setup**:
1. **Groq API Key**: 
   - Visit [console.groq.com](https://console.groq.com)
   - Sign up/login and generate an API key
   - Free tier includes generous usage limits

2. **Hugging Face Token**:
   - Visit [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
   - Create a new token with read permissions
   - Free tier available for most models

### Step 4: Run the Application

#### Option A: Streamlit Web App (Recommended)
```bash
streamlit run final.py
```
Access the app at `http://localhost:8501`

#### Option B: Flask API Server
```bash
python app.py
```
API available at `http://localhost:5000`

## 📖 Complete Usage Guide

### Web Interface (Streamlit) - Step-by-Step

The new interface guides you through 6 clear steps:

#### **Step 1: Search Wikipedia** 🔍
   - Enter your search query (e.g., "Albert Einstein", "Moon Landing")
   - Select Wikipedia language from sidebar (9 languages supported)
   - Click "🔎 Search" button
   - Select a topic from the results grid

#### **Step 2: Generate Storyline** 📖
   - Review the article summary (optional)
   - Configure story settings in sidebar:
     - Story length (short/medium/long)
     - Comic art style
     - Number of scenes (3-15)
   - Click "✨ Generate Comic Storyline"
   - Wait 1-2 minutes for AI processing
   - Review and download the generated storyline

#### **Step 3: Generate Scene Prompts** 🎬
   - Click "🎭 Generate Scene Prompts"
   - AI creates detailed visual descriptions for each scene
   - Preview all scene prompts in the expandable section
   - Story content automatically saved to text files

#### **Step 4: Generate Comic Images** 🎨
   - Click "🎨 Generate All Comic Images"
   - Images generate using free Stable Diffusion models
   - Progress updates shown in real-time
   - Takes 5-15 minutes depending on number of scenes
   - View generated comic panels in beautiful grid layout

#### **Step 5: Generate Narration & Audio** 🎙️
   - Configure narration settings in sidebar:
     - Narration style (dramatic/educational/storytelling/documentary)
     - Voice tone (engaging/serious/playful/informative)
     - Voice selection (5 English voices available)
     - Speech rate and volume
   - Click "🎙️ Generate All Scene Narrations"
   - Review generated narrations
   - Click "🔊 Generate Audio for All Scenes"
   - Audio files automatically created using Microsoft Edge TTS
   - Preview audio for each scene

#### **Step 6: Generate Final Video** 🎥
   - Configure video settings in sidebar:
     - Resolution (720p or 1080p)
     - Frame rate (24/25/30 fps)
     - Minimum scene duration
   - Click "🎬 Generate Final Video"
   - Video assembles with:
     - Scene transitions (crossfade effects)
     - Synchronized voiceovers
     - Professional timing
   - Preview and download the final MP4 video

### Quick Tips
- ✅ Use the sidebar to access all settings
- ✅ Each step must complete before moving to the next
- ✅ All generated content is automatically saved
- ✅ You can restart anytime using "🔄 Start Over" button
- ✅ Download your final video and all intermediate files

### API Usage (Flask)

#### Search Wikipedia
```bash
curl "http://localhost:5000/search?query=Albert%20Einstein&lang=en"
```

#### Generate Complete Comic
```bash
curl -X GET "http://localhost:5000/page_info?title=Albert%20Einstein&lang=en" \
  -H "Groq-Api-Key: your_groq_key" \
  -H "Hf-Api-Key: your_hf_token"
```

## ⚙️ Configuration Options

### Story Generation
- **Length**: Short (500 words), Medium (1000 words), Long (2000 words)
- **Style**: Manga, Superhero, Noir, Cartoon, European, Indie, Retro
- **Audience**: Kids, Teens, General, Adult
- **Education Level**: Basic, Standard, Advanced

### Narration Generation (NEW!)
- **Style**: Dramatic, Educational, Storytelling, Documentary
- **Voice Tone**: Engaging, Serious, Playful, Informative
- **Length**: 2-4 sentences per scene (50-100 words)
- **Format**: Voice-over ready text

### Image Generation
- **Scenes**: 3-15 panels per comic
- **Resolution**: High-quality output (1024x1024)
- **Style Consistency**: Maintained across all panels
- **Fallback Handling**: Automatic model switching on failures

### Language Support
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Russian (ru)
- Japanese (ja)
- Chinese (zh)

## 🔧 Technical Details

### Error Handling
- **Network Issues**: Automatic retry with exponential backoff
- **API Failures**: Graceful fallback to alternative models
- **Content Issues**: Disambiguation and suggestion handling
- **Rate Limiting**: Built-in delay and retry mechanisms

### Performance Optimization
- **Caching**: Wikipedia content saved locally
- **Batch Processing**: Efficient image generation pipeline
- **Memory Management**: Optimized for large content processing
- **Logging**: Comprehensive error tracking and debugging

### Data Management
- **Storage**: Organized file structure for generated content
- **Persistence**: JSON files for Wikipedia data
- **Cleanup**: Automatic directory creation and management
- **Backup**: Generated content preserved for reuse
- **NEW**: Text file storage for all generated content
- **NEW**: Narration files with multiple formats (TXT, JSON)
- **NEW**: Content reusability for other LLMs and applications

## 📁 Text File Management & Content Reusability

### Automatic Content Storage
The application now automatically saves all generated content in organized text files:

#### Story Content (`data/text/[Topic]/`)
- **`[Topic]_storyline.txt`**: Complete comic storyline
- **`[Topic]_scene_prompts.txt`**: All scene prompts for image generation
- **`[Topic]_page_info.json`**: Wikipedia page data in JSON format
- **`[Topic]_combined.txt`**: All content combined in one file

#### Narration Content (`data/narration/[Topic]/`)
- **`scene_1_narration.txt`**: Individual scene narrations
- **`[Topic]_complete_narration.txt`**: All narrations in one file
- **`[Topic]_narrations.json`**: Structured narration data

### Content Reusability
These text files can be used as input for:
- **Other LLMs**: Use the saved text as prompts for different AI models
- **Text-to-Speech**: Convert narrations to audio files
- **Video Creation**: Use content for video script generation
- **Further Processing**: Modify and enhance the generated content
- **API Integration**: Use JSON files for programmatic access

### Narration Features
- **Multiple Styles**: Dramatic, Educational, Storytelling, Documentary
- **Voice Tones**: Engaging, Serious, Playful, Informative
- **Scene-Specific**: Each narration tailored to its scene
- **Voice-Over Ready**: Formatted for smooth spoken delivery
- **Downloadable**: Complete narrations available for download

## 📊 Example Outputs

The application has generated successful comic strips for various topics:

- **Historical Events**: World War II, Ancient Civilizations
- **Cultural Topics**: Ramayana, Diwali celebrations
- **Sports**: FIFA World Cup
- **Historical Figures**: Shivaji Maharaj
- **Scientific Topics**: Space exploration, Physics

Each comic includes:
- 10 high-quality panels
- Consistent character design
- Educational narrative
- Appropriate visual style
- Downloadable content
- **NEW**: Professional scene-by-scene narration
- **NEW**: Organized text files for further processing
- **NEW**: Multiple narration styles and voice tones

## 🚨 Troubleshooting

### Common Issues

1. **API Key Errors**:
   - Verify keys in `.env` file
   - Check API key validity
   - Ensure sufficient quota

2. **Image Generation Failures**:
   - Check Hugging Face token
   - Verify model availability
   - Try fallback model

3. **Wikipedia Access Issues**:
   - Check internet connection
   - Verify language settings
   - Try different search terms

4. **Memory Issues**:
   - Reduce number of scenes
   - Process shorter articles
   - Restart application

### Debug Mode
Enable detailed logging by modifying the logging level in `final.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 🔮 Future Enhancements

### Planned Features
- **Voice Narration**: Audio generation for comic strips (Partially implemented!)
- **Video Export**: Animated comic sequences
- **Custom Characters**: User-defined character designs
- **Collaborative Editing**: Multi-user comic creation
- **Advanced Styling**: More art style options
- **Mobile App**: Native mobile application
- **Text-to-Speech**: Convert narrations to audio files
- **Advanced Narration**: Multi-language narration support

### Technical Improvements
- **Caching System**: Redis-based content caching
- **Database Integration**: PostgreSQL for data management
- **Microservices**: Containerized service architecture
- **CDN Integration**: Fast content delivery
- **Analytics**: Usage tracking and optimization

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Setup
```bash
git clone <repository-url>
cd genai/wiki_streamlit
pip install -r requirements.txt
python -m pytest tests/
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Wikipedia**: For providing comprehensive content
- **Groq**: For fast and reliable AI text generation
- **Hugging Face**: For image generation models and infrastructure
- **Streamlit**: For the excellent web framework
- **Open Source Community**: For various supporting libraries

## 📞 Support

For support, questions, or feature requests:
- Create an issue in the repository
- Contact the development team
- Check the documentation wiki

## 📈 Project Status

- **Version**: 3.0.0
- **Status**: Production Ready
- **Last Updated**: October 2024
- **Maintainer**: Airavat
- **Major Updates**: 
  - ✅ Complete video generation pipeline
  - ✅ Free image generation (Stable Diffusion)
  - ✅ Automatic voice synthesis (Edge TTS)
  - ✅ Modern, intuitive UI redesign
  - ✅ Improved error handling and reliability

## 🎯 What Makes This Special

### Complete End-to-End Solution
Unlike other tools that only generate images or text, VidyAI Vizuara creates complete educational videos:
- 📚 Research (Wikipedia extraction)
- ✍️ Writing (AI story generation)
- 🎨 Illustration (AI image generation)
- 🎙️ Narration (AI text generation + TTS)
- 🎬 Production (Video assembly)

### Free & Accessible
- Uses free Stable Diffusion models (no payment required)
- Uses Microsoft Edge TTS (completely free)
- Only requires free API keys from Groq and Hugging Face
- Open source and fully customizable

### Professional Quality
- High-resolution images (1024x1024)
- Natural-sounding voiceovers
- Smooth video transitions
- Synchronized audio and visuals
- Downloadable in multiple formats

---

**Made with ❤️ by Airavat | VidyAI Vizuara Team**
