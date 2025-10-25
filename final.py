import streamlit as st
import os
import re
import glob
import json
import logging
from typing import Optional
from dotenv import load_dotenv
from wikipedia_extractor import WikipediaExtractor
from story_generator import StoryGenerator
from gemini_image_generator import GeminiImageGenerator
from narration_generator import NarrationGenerator
from tts_generator import generate_scene_audios, synthesize_to_mp3, estimate_tts_duration_seconds
from video_editor import build_video

# Load environment variables from .env if present
script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv()

# Default API keys (loaded from environment if available)
GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("wiki_comic_generator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("WikiComicGenerator")


# Streamlit UI
def main():
    st.set_page_config(
        page_title="VidyAI Vizuara - Comic Video Generator",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state variables
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    if 'selected_topic' not in st.session_state:
        st.session_state.selected_topic = None
    if 'page_info' not in st.session_state:
        st.session_state.page_info = None
    if 'storyline' not in st.session_state:
        st.session_state.storyline = None
    if 'scene_prompts' not in st.session_state:
        st.session_state.scene_prompts = None
    if 'comic_images' not in st.session_state:
        st.session_state.comic_images = None
    if 'story_saved' not in st.session_state:
        st.session_state.story_saved = False
    if 'narrations' not in st.session_state:
        st.session_state.narrations = None
    if 'narration_style' not in st.session_state:
        st.session_state.narration_style = "dramatic"
    if 'voice_tone' not in st.session_state:
        st.session_state.voice_tone = "engaging"
    if 'audio_paths' not in st.session_state:
        st.session_state.audio_paths = None
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    
    # Modern CSS styling
    st.markdown("""
        <style>
        /* Main styling */
        .main {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 0;
        }
        .main > div {
            background: white;
            padding: 2rem;
            border-radius: 20px;
            margin: 1rem auto;
            max-width: 1400px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        /* Header styling */
        .main-header {
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 0.5rem;
            padding: 1rem 0;
        }
        
        .subtitle {
            text-align: center;
            font-size: 1.2rem;
            color: #2c3e50;
            margin-bottom: 2rem;
            font-weight: 500;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }
        
        /* Step indicator */
        .step-container {
            display: flex;
            justify-content: space-between;
            align-items: stretch;
            margin: 2rem 0;
            padding: 1rem;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 15px;
            gap: 0.5rem;
        }
        
        .step {
            flex: 1;
            text-align: center;
            padding: 0.8rem 0.5rem;
            border-radius: 10px;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
            color: #555;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            min-height: 70px;
        }
        
        .step.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            transform: scale(1.05);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .step.completed {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }
        
        .step-number {
            font-size: 1.3rem;
            font-weight: bold;
            margin-bottom: 0.3rem;
        }
        
        .step-title {
            font-size: 0.85rem;
            font-weight: 600;
            line-height: 1.2;
        }
        
        /* Card styling */
        .info-card {
            background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
            padding: 1.2rem;
            border-radius: 12px;
            margin: 1rem 0;
            border-left: 5px solid #2196F3;
            box-shadow: 0 3px 12px rgba(0,0,0,0.08);
            color: #1565C0;
            font-weight: 500;
            font-size: 0.95rem;
            line-height: 1.6;
        }
        
        .success-card {
            background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
            padding: 1.2rem;
            border-radius: 12px;
            margin: 1rem 0;
            border-left: 5px solid #4CAF50;
            box-shadow: 0 3px 12px rgba(0,0,0,0.08);
            color: #2E7D32;
            font-weight: 500;
            font-size: 0.95rem;
            line-height: 1.6;
        }
        
        .warning-card {
            background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
            padding: 1.2rem;
            border-radius: 12px;
            margin: 1rem 0;
            border-left: 5px solid #FF9800;
            box-shadow: 0 3px 12px rgba(0,0,0,0.08);
            color: #E65100;
            font-weight: 500;
            font-size: 0.95rem;
            line-height: 1.6;
        }
        
        .error-card {
            background: linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%);
            padding: 1.2rem;
            border-radius: 12px;
            margin: 1rem 0;
            border-left: 5px solid #F44336;
            box-shadow: 0 3px 12px rgba(0,0,0,0.08);
            color: #C62828;
            font-weight: 500;
            font-size: 0.95rem;
            line-height: 1.6;
        }
        
        /* Section header */
        .section-header {
            font-size: 1.8rem;
            font-weight: 700;
            color: #4a5fc1;
            margin: 2.5rem 0 1.2rem 0;
            padding-bottom: 0.6rem;
            border-bottom: 3px solid #4a5fc1;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
            line-height: 1.3;
        }
        
        /* Comic panel styling */
        .comic-panel {
            margin: 0.8rem 0;
            padding: 1rem;
            border: 3px solid #667eea;
            border-radius: 12px;
            background: white;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
        }
        
        .comic-panel:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.12);
        }
        
        .comic-caption {
            font-size: 0.9rem;
            font-style: italic;
            margin-top: 0.6rem;
            text-align: center;
            color: #444;
            font-weight: 500;
        }
        
        /* Button styling */
        .stButton>button {
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.3s ease;
            padding: 0.6rem 1.5rem;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        /* Fix column gaps */
        div[data-testid="column"] {
            padding: 0 0.5rem;
        }
        
        /* Ensure proper text alignment in cards */
        .stMarkdown p {
            margin-bottom: 0.5rem;
        }
        
        /* Fix expander styling */
        .streamlit-expanderHeader {
            font-weight: 600;
            font-size: 1rem;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        }
        
        /* Progress indicator */
        .progress-container {
            background: #f0f2f6;
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        .progress-item {
            display: flex;
            align-items: center;
            padding: 0.5rem;
            margin: 0.3rem 0;
        }
        
        .progress-icon {
            margin-right: 0.8rem;
            font-size: 1.2rem;
        }
        
        /* Audio player custom styling */
        audio {
            width: 100%;
            border-radius: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # App header
    st.markdown('<div class="main-header">🎬 VidyAI Vizuara</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Transform Wikipedia Articles into Engaging Educational Videos - Perfect for Students!</div>', unsafe_allow_html=True)
    
    # Determine current step based on session state
    if st.session_state.comic_images and st.session_state.audio_paths:
        st.session_state.current_step = 6
    elif st.session_state.narrations:
        st.session_state.current_step = 5
    elif st.session_state.comic_images:
        st.session_state.current_step = 4
    elif st.session_state.scene_prompts:
        st.session_state.current_step = 3
    elif st.session_state.storyline:
        st.session_state.current_step = 2
    elif st.session_state.selected_topic:
        st.session_state.current_step = 1
    
    # Step indicator
    steps = [
        ("1", "Search"),
        ("2", "Storyline"),
        ("3", "Scenes"),
        ("4", "Images"),
        ("5", "Narration"),
        ("6", "Video")
    ]
    
    step_html = '<div class="step-container">'
    for i, (num, title) in enumerate(steps, 1):
        if i < st.session_state.current_step:
            step_class = "step completed"
            icon = "✓"
        elif i == st.session_state.current_step:
            step_class = "step active"
            icon = num
        else:
            step_class = "step"
            icon = num
        step_html += f'<div class="{step_class}"><div class="step-number">{icon}</div><div class="step-title">{title}</div></div>'
    step_html += '</div>'
    st.markdown(step_html, unsafe_allow_html=True)
    
    # Existing topics and assets reuse section
    st.markdown('---')
    st.markdown('<div class="section-header">📦 Reuse Existing Topics & Assets</div>', unsafe_allow_html=True)
    
    def _sanitize_title(name: str) -> str:
        return re.sub(r'[\\/*?:"<>|]', '_', name).strip()
    
    def _list_existing_topics(base_images_dir: str = os.path.join('data', 'images')):
        if not os.path.isdir(base_images_dir):
            return []
        try:
            return sorted([d for d in os.listdir(base_images_dir) if os.path.isdir(os.path.join(base_images_dir, d))])
        except Exception:
            return []
    
    def _load_existing_assets(topic: str):
        safe_title = _sanitize_title(topic)
        images_dir = os.path.join('data', 'images', safe_title)
        narr_base_dir = os.path.join('data', 'narration', safe_title)
        narration_dir = os.path.join(narr_base_dir, 'audio')
        text_dir = os.path.join('data', 'text', safe_title)
        
        # Images
        image_paths = sorted(glob.glob(os.path.join(images_dir, 'scene_*.jpg')),
                             key=lambda p: int(re.search(r'scene_(\d+)\.', os.path.basename(p)).group(1)) if re.search(r'scene_(\d+)\.', os.path.basename(p)) else 0)
        
        # Audio (mp3)
        audio_paths = {}
        if os.path.isdir(narration_dir):
            for mp3 in glob.glob(os.path.join(narration_dir, 'scene_*.mp3')):
                m = re.search(r'scene_(\d+)\.', os.path.basename(mp3))
                if m:
                    scene_num = int(m.group(1))
                    audio_paths[f'scene_{scene_num}'] = mp3
        
        # Optional: load narrations json
        narr_json = os.path.join(narr_base_dir, f'{safe_title}_narrations.json')
        narr_data = None
        if os.path.isfile(narr_json):
            try:
                with open(narr_json, 'r', encoding='utf-8') as f:
                    narr_data = json.load(f)
            except Exception:
                narr_data = None
        
        # Optional: storyline for context
        storyline_path = os.path.join(text_dir, f'{safe_title}_storyline.txt')
        storyline = None
        if os.path.isfile(storyline_path):
            try:
                with open(storyline_path, 'r', encoding='utf-8') as f:
                    storyline = f.read()
            except Exception:
                storyline = None
        
        return image_paths, audio_paths, narr_data, storyline
    
    existing_topics = _list_existing_topics()
    if existing_topics:
        colA, colB = st.columns([2, 1])
        with colA:
            reuse_topic = st.selectbox('Select an existing topic to reuse assets', options=existing_topics, index=0)
        with colB:
            if st.button('🔄 Refresh List'):
                st.rerun()
        
        if reuse_topic:
            imgs, auds, narr_meta, storyline = _load_existing_assets(reuse_topic)
            st.markdown(f"**Topic:** {reuse_topic}")
            st.markdown(f"- Images found: {len(imgs)}")
            st.markdown(f"- Audio files found: {len(auds)}")
            if narr_meta:
                st.markdown(f"- Narrations metadata detected")
            if storyline:
                with st.expander('📖 Preview Storyline (optional)', expanded=False):
                    st.text_area('Storyline', value=storyline[:4000], height=180, label_visibility='collapsed')
            
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button('📥 Load Images Only'):
                    if imgs:
                        st.session_state.comic_images = imgs
                        # set selected topic for video title
                        st.session_state.selected_topic = reuse_topic
                        st.session_state.page_info = {"title": reuse_topic}
                        st.markdown('<div class="success-card">✅ Loaded images from existing topic.</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="error-card">❌ No images found for this topic.</div>', unsafe_allow_html=True)
            with c2:
                if st.button('📥 Load Images + Audio'):
                    if imgs:
                        st.session_state.comic_images = imgs
                        st.session_state.selected_topic = reuse_topic
                        st.session_state.page_info = {"title": reuse_topic}
                        if auds:
                            st.session_state.audio_paths = {f"scene_{i}": auds.get(f"scene_{i}") for i in range(1, len(imgs) + 1) if auds.get(f"scene_{i}")}
                            st.markdown('<div class="success-card">✅ Loaded images and audio from existing topic.</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="warning-card">⚠️ No audio files found; you can still generate them in Step 5.</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="error-card">❌ No images found for this topic.</div>', unsafe_allow_html=True)
            with c3:
                if st.button('🎬 Generate Video Now (if audio loaded)'):
                    if st.session_state.get('comic_images') and st.session_state.get('audio_paths'):
                        w, h = (1920, 1080)
                        out_dir = os.path.join('data', 'videos')
                        os.makedirs(out_dir, exist_ok=True)
                        try:
                            result = build_video(
                                images=st.session_state.comic_images,
                                scene_audio=st.session_state.audio_paths,
                                out_dir=out_dir,
                                title=st.session_state.page_info.get('title', reuse_topic),
                                fps=30,
                                resolution=(w, h),
                                crossfade_sec=0.3,
                                min_scene_seconds=3.0,
                                head_pad=0.15,
                                tail_pad=0.15,
                                bg_music_path=None,
                                bg_music_volume=0.08
                            )
                            st.session_state.final_video = result["video_path"]
                            st.markdown('<div class="success-card">🎉 Video generated successfully from existing assets!</div>', unsafe_allow_html=True)
                            st.rerun()
                        except Exception as e:
                            st.markdown(f'<div class="error-card">❌ Error generating video: {str(e)}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="warning-card">⚠️ Please load images and audio first.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-card">No existing topics found yet. Generate some images to see them here.</div>', unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        # API keys section
        with st.expander("🔑 API Keys", expanded=False):
            groq_api_key = st.text_input(
                "Groq API Key", 
                type="password", 
                value=GROQ_API_KEY if GROQ_API_KEY else "", 
                help="Required for story and narration generation. Add to .env file to auto-load."
            )
            gemini_api_key = st.text_input(
                "Google Gemini API Key", 
                type="password", 
                value=GEMINI_API_KEY if GEMINI_API_KEY else "", 
                help="Required for image generation. Get free key from: https://aistudio.google.com/app/apikey. Add to .env file to auto-load."
            )
            
            # Show status
            if GROQ_API_KEY:
                st.success("✅ Groq API Key loaded from .env")
            if GEMINI_API_KEY:
                st.success("✅ Gemini API Key loaded from .env")
        
        st.markdown("---")
        
        # Wikipedia settings
        with st.expander("📚 Wikipedia Settings", expanded=False):
            wiki_lang = st.selectbox(
                "Language",
                options=["en", "es", "fr", "de", "it", "pt", "ru", "ja", "zh"],
                index=0,
                format_func=lambda x: {
                    "en": "🇬🇧 English", "es": "🇪🇸 Spanish", "fr": "🇫🇷 French", 
                    "de": "🇩🇪 German", "it": "🇮🇹 Italian", "pt": "🇵🇹 Portuguese",
                    "ru": "🇷🇺 Russian", "ja": "🇯🇵 Japanese", "zh": "🇨🇳 Chinese"
                }.get(x, x)
            )
        
        # Story settings
        with st.expander("📖 Story Settings", expanded=False):
            story_length = st.select_slider(
                "Story Length",
                options=["short", "medium", "long"],
                value="medium"
            )
            
            comic_style = st.selectbox(
                "Comic Art Style",
                options=[
                    "western comic", "manga", "comic book", "noir comic", 
                    "superhero comic", "indie comic", "cartoon", "graphic novel",
                    "golden age comic", "modern comic", "manhwa"
                ],
                index=0
            )
            
            num_scenes = st.slider(
                "Number of Scenes",
                min_value=3,
                max_value=15,
                value=10
            )
            
            st.markdown("**Advanced:**")
            max_content_chars = st.number_input(
                "Max Wikipedia Content (chars)",
                min_value=5000,
                max_value=30000,
                value=25000,
                step=5000,
                help="Maximum characters from Wikipedia to process. Keep at 25000 to avoid Groq token limits (12K TPM). Reduce if you get 'Request too large' errors."
            )
        
        # Narration settings
        with st.expander("🎙️ Narration Settings", expanded=False):
            narration_style = st.selectbox(
                "Narration Style",
                options=["dramatic", "educational", "storytelling", "documentary"],
                index=0
            )
            
            voice_tone = st.selectbox(
                "Voice Tone",
                options=["engaging", "serious", "playful", "informative"],
                index=0
            )
            
            tts_lang = st.selectbox(
                "Language",
                options=["en", "hi", "es", "fr", "de", "it", "pt", "ru", "ja", "zh-CN"],
                index=0,
                format_func=lambda x: {
                    "en": "English", "hi": "Hindi", "es": "Spanish", 
                    "fr": "French", "de": "German", "it": "Italian",
                    "pt": "Portuguese", "ru": "Russian", "ja": "Japanese", "zh-CN": "Chinese"
                }.get(x, x),
                help="Select language for text-to-speech"
            )
            
            tts_accent = st.selectbox(
                "Accent",
                options=[ "co.in","com", "co.uk", "com.au", "ca", "co.za"],
                index=0,
                format_func=lambda x: {
                    "co.in": "🇮🇳 India","com": "🇺🇸 US", "co.uk": "🇬🇧 UK", 
                    "com.au": "🇦🇺 Australia", "ca": "🇨🇦 Canada", "co.za": "🇿🇦 South Africa"
                }.get(x, x),
                help="Select accent/region for English (applies to English only)"
            )
            
            slow_speech = st.checkbox("Slower Speech Rate", value=False, help="Enable for clearer, slower narration")
        
        # Video settings
        with st.expander("🎥 Video Settings", expanded=False):
            min_scene_seconds = st.number_input("Min Scene Duration (s)", min_value=1, max_value=10, value=3)
            fps = st.selectbox("Frame Rate", options=[24, 25, 30], index=2)
            resolution = st.selectbox("Resolution", options=["1280x720", "1920x1080"], index=1)

        st.markdown("---")
        
        # Reset button
        if st.button("🔄 Start Over"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 💡 About")
        st.markdown("""
        **VidyAI Vizuara** transforms Wikipedia content into engaging educational videos using simple, student-friendly language.
        
        ✨ **New Updates:**
        - Simple, clear language for students
        - More engaging storytelling
        - Better UI with improved layout
        
        
        """)
    
    # Main content area
    # Step 1: Search Wikipedia
    st.markdown('<div class="section-header">🔍 Step 1: Search Wikipedia Topic</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        query = st.text_input("Search Wikipedia", placeholder="Enter a topic (e.g., Albert Einstein, Moon Landing, Ancient Rome)...", label_visibility="collapsed")
    with col2:
        search_button = st.button("🔎 Search", type="primary")
        
        if search_button and query:
            if not groq_api_key:
                st.markdown('<div class="error-card">⚠️ Please enter your Groq API key in the sidebar to continue.</div>', unsafe_allow_html=True)
            else:
                with st.spinner("🔍 Searching Wikipedia..."):
                    wiki_extractor = WikipediaExtractor(language=wiki_lang)
                    search_results = wiki_extractor.search_wikipedia(query)
                    
                    if isinstance(search_results, str):
                        st.markdown(f'<div class="warning-card">{search_results}</div>', unsafe_allow_html=True)
                    else:
                        st.session_state.search_results = search_results
                        st.session_state.selected_topic = None
                        st.session_state.page_info = None
                        st.session_state.storyline = None
                        st.session_state.scene_prompts = None
                        st.session_state.comic_images = None
                        st.markdown(f'<div class="success-card">✅ Found {len(search_results)} results for "{query}"</div>', unsafe_allow_html=True)
        
    # Display search results
    if st.session_state.search_results:
        st.markdown("#### 📋 Search Results - Select a topic:")
        
        # Display in a grid
        cols = st.columns(3)
        for i, result in enumerate(st.session_state.search_results):
            with cols[i % 3]:
                if st.button(f"📄 {result}", key=f"result_{i}"):
                    st.session_state.selected_topic = result
                    st.session_state.page_info = None
                    st.session_state.storyline = None
                    st.session_state.scene_prompts = None
                    st.session_state.comic_images = None
                    st.session_state.narrations = None
                    st.session_state.audio_paths = None
                    st.rerun()

        # Step 2: Generate storyline
        if st.session_state.selected_topic:
            st.markdown("---")
            st.markdown('<div class="section-header">📖 Step 2: Generate Comic Storyline</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-card"><strong>Selected Topic:</strong> {st.session_state.selected_topic}</div>', unsafe_allow_html=True)
            
            if st.session_state.page_info is None:
                with st.spinner(f"📚 Fetching information about '{st.session_state.selected_topic}'..."):
                    wiki_extractor = WikipediaExtractor(language=wiki_lang)
                    page_info = wiki_extractor.get_page_info(st.session_state.selected_topic)
                    st.session_state.page_info = page_info
            
            # Handle errors in page retrieval
            if "error" in st.session_state.page_info:
                st.markdown(f'<div class="error-card">{st.session_state.page_info["message"]}</div>', unsafe_allow_html=True)
                
                # Show disambiguation options if available
                if "options" in st.session_state.page_info:
                    st.markdown("#### 🔀 Multiple matches found. Please select one:")
                    cols = st.columns(3)
                    for i, option in enumerate(st.session_state.page_info["options"]):
                        with cols[i % 3]:
                            if st.button(f"📄 {option}", key=f"option_{i}"):
                                st.session_state.selected_topic = option
                                st.session_state.page_info = None
                                st.session_state.storyline = None
                                st.session_state.scene_prompts = None
                                st.session_state.comic_images = None
                                st.rerun()
            else:
                # Show page summary if available
                with st.expander("📄 View Article Summary", expanded=False):
                    summary_text = st.session_state.page_info.get("summary") if isinstance(st.session_state.page_info, dict) else None
                    if summary_text:
                        st.markdown(summary_text)
                    else:
                        st.markdown("No summary available for this topic.")
                
                # Generate storyline button
                if not st.session_state.storyline:
                    if st.button("✨ Generate Comic Storyline", type="primary"):
                        with st.spinner("🎨 Creating comic storyline..."):
                            story_generator = StoryGenerator(api_key=groq_api_key)
                            storyline = story_generator.generate_comic_storyline(
                                st.session_state.page_info["title"],
                                st.session_state.page_info["content"],
                                target_length=story_length,
                                max_chars=max_content_chars
                            )
                            st.session_state.storyline = storyline
                            st.session_state.scene_prompts = None
                            st.session_state.comic_images = None
                            st.session_state.story_saved = False
                            st.session_state.narrations = None
                            st.session_state.audio_paths = None
                            st.rerun()
    
        # Step 3: Generate scene prompts
        if st.session_state.storyline:
            st.markdown("---")
            st.markdown('<div class="section-header">🎬 Step 3: Generate Scene Prompts</div>', unsafe_allow_html=True)
            st.markdown('<div class="success-card">✅ Storyline generated successfully!</div>', unsafe_allow_html=True)
            
            with st.expander("📖 View Full Storyline", expanded=False):
                st.markdown(st.session_state.storyline)
            st.download_button(
                label="💾 Download Storyline",
                data=st.session_state.storyline,
                file_name=f"{st.session_state.page_info['title']}_storyline.md",
                mime="text/markdown"
            )
            
            # Generate scene prompts button
            if not st.session_state.scene_prompts:
                if st.button("🎭 Generate Scene Prompts", type="primary"):
                    with st.spinner(f"🎬 Generating {num_scenes} scene prompts..."):
                        story_generator = StoryGenerator(api_key=groq_api_key)
                        scene_prompts = story_generator.generate_scene_prompts(
                            st.session_state.page_info["title"],
                            st.session_state.storyline,
                            comic_style,
                            num_scenes=num_scenes
                        )
                        st.session_state.scene_prompts = scene_prompts
                        st.session_state.comic_images = None
                        
                        # Save story content to text files
                        file_paths = story_generator.save_story_content(
                            st.session_state.page_info["title"],
                            st.session_state.storyline,
                            scene_prompts,
                            st.session_state.page_info
                        )
                        st.session_state.story_saved = True
                        st.rerun()
        
        # Step 4: Generate images
        if st.session_state.scene_prompts:
            st.markdown("---")
            st.markdown('<div class="section-header">🖼️ Step 4: Generate Comic Images</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="success-card">✅ Generated {len(st.session_state.scene_prompts)} scene prompts!</div>', unsafe_allow_html=True)
            
            with st.expander(f"🎭 View Scene Prompts ({len(st.session_state.scene_prompts)} scenes)", expanded=False):
                for i, prompt in enumerate(st.session_state.scene_prompts, 1):
                    st.markdown(f"**Scene {i}:**")
                    st.text_area(f"Scene {i} Prompt", value=prompt, height=100, key=f"scene_prompt_view_{i}", label_visibility="collapsed")
            
            # Helper: extract sheets for consistency
            def _extract_character_sheet(story_text: str) -> str:
                try:
                    # Capture content under '## Main Characters' until next '##'
                    match = re.search(r"##\s*Main Characters.*?\n(.*?)(?:\n##\s|\Z)", story_text, re.DOTALL | re.IGNORECASE)
                    section = (match.group(1).strip() if match else "").strip()
                    # Compact excessive whitespace and limit size
                    section = re.sub(r"\n{2,}", "\n", section)
                    return section[:1200]
                except Exception:
                    return ""

            def _build_style_sheet(style_name: str) -> str:
                base = f"Maintain a consistent '{style_name}' comic style across all scenes."
                guidance = {
                    "manga": "Use black-and-white tones, clean linework, expressive faces, dynamic panels.",
                    "superhero comic": "Bold colors, strong outlines, dynamic poses, dramatic lighting.",
                    "noir comic": "High contrast lighting, moody shadows, restrained palette.",
                    "cartoon": "Simplified shapes, bold outlines, bright but balanced colors.",
                    "western comic": "Clear linework, saturated palette, cinematic framing."
                }
                tip = guidance.get(style_name.lower(), "Consistent palette, line weight, and framing throughout.")
                return base + " " + tip

            # Generate comic images button
            if not st.session_state.comic_images:
                if st.button("🎨 Generate All Comic Images", type="primary"):
                    if not gemini_api_key:
                        st.markdown('<div class="error-card">⚠️ Please enter your Google Gemini API key in the sidebar.</div>', unsafe_allow_html=True)
                    else:
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        with st.spinner(f"🎨 Generating {len(st.session_state.scene_prompts)} comic images with Gemini 2.5 Flash Image..."):
                            try:
                                image_generator = GeminiImageGenerator(api_key=gemini_api_key)
                                
                                # Update progress
                                status_text.text("Initializing Gemini image generation...")
                                
                                # Build sheets for image consistency
                                style_sheet = _build_style_sheet(comic_style)
                                character_sheet = _extract_character_sheet(st.session_state.storyline or "")
                                negative_concepts = [
                                    "text", "letters", "watermark", "logo", "caption", "speech bubble", "ui"
                                ]

                                image_paths = image_generator.generate_comic_strip(
                                    st.session_state.scene_prompts,
                                    "data/images",
                                    st.session_state.page_info["title"],
                                    style_sheet=style_sheet,
                                    character_sheet=character_sheet,
                                    negative_concepts=negative_concepts,
                                    aspect_ratio="16:9"
                                )
                                
                                progress_bar.progress(100)
                                st.session_state.comic_images = image_paths
                                
                                if image_paths:
                                    st.markdown(f'<div class="success-card">✅ Successfully generated {len(image_paths)} comic panels with Gemini!</div>', unsafe_allow_html=True)
                                else:
                                    st.markdown('<div class="error-card">❌ Failed to generate images. Check the logs.</div>', unsafe_allow_html=True)
                            except Exception as e:
                                st.markdown(f'<div class="error-card">❌ Error: {str(e)}</div>', unsafe_allow_html=True)
                                logger.error(f"Image generation error: {str(e)}")
                            st.rerun()
    
    # Display generated comic images
    if st.session_state.comic_images:
        st.markdown("---")
        st.markdown('<div class="section-header">🖼️ Your Generated Comic Panels</div>', unsafe_allow_html=True)
        
        # Display images in a grid
        cols_per_row = 3
        for i in range(0, len(st.session_state.comic_images), cols_per_row):
            cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                idx = i + j
                if idx < len(st.session_state.comic_images):
                    with cols[j]:
                        st.markdown(f'<div class="comic-panel">', unsafe_allow_html=True)
                        st.image(st.session_state.comic_images[idx], use_container_width=True)
                        st.markdown(f'<div class="comic-caption">Scene {idx+1}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
    
    # Step 5: Generate narration and audio
    if st.session_state.story_saved and st.session_state.comic_images:
        st.markdown("---")
        st.markdown('<div class="section-header">🎙️ Step 5: Generate Narration & Audio</div>', unsafe_allow_html=True)
        
        if not st.session_state.narrations:
            st.markdown('<div class="info-card">📝 Generate narrations for each scene to create voiceovers.</div>', unsafe_allow_html=True)
            
            if st.button("🎙️ Generate All Scene Narrations", type="primary"):
                with st.spinner(f"📝 Generating narrations for {len(st.session_state.scene_prompts)} scenes..."):
                    narration_generator = NarrationGenerator(api_key=groq_api_key)
                    narrations = narration_generator.generate_all_scene_narrations(
                        st.session_state.page_info["title"],
                        narration_style,
                        voice_tone
                    )
                    st.session_state.narrations = narrations
                    st.markdown('<div class="success-card">✅ Narrations generated successfully!</div>', unsafe_allow_html=True)
                    st.rerun()
        else:
            st.markdown(f'<div class="success-card">✅ Narrations ready for {len(st.session_state.narrations["narrations"])} scenes!</div>', unsafe_allow_html=True)
            
            # Show narrations
            with st.expander("📝 View All Narrations", expanded=False):
                for scene_key, scene_data in st.session_state.narrations['narrations'].items():
                    scene_num = scene_data['scene_number']
                    narration = scene_data['narration']
                    st.markdown(f"**Scene {scene_num}:**")
                    st.text_area(f"Scene {scene_num} Narration", value=narration, height=80, key=f"narr_view_{scene_num}", label_visibility="collapsed")
            
            # Generate audio
            if not st.session_state.audio_paths:
                st.markdown('<div class="info-card">🔊 Now generate audio (MP3) files for the narrations.</div>', unsafe_allow_html=True)
                
                if st.button("🔊 Generate Audio for All Scenes", type="primary"):
                    with st.spinner("🎵 Generating MP3 files using Google TTS at 1.25x speed..."):
                        try:
                            audio_paths = generate_scene_audios(
                                st.session_state.narrations,
                                st.session_state.page_info["title"],
                                base_dir="data/narrations",
                                lang=tts_lang,
                                tld=tts_accent,
                                slow=slow_speech,
                                speed=1.25  # 25% faster for better pacing
                            )
                            st.session_state.audio_paths = audio_paths
                            st.markdown(f'<div class="success-card">✅ Generated {len(audio_paths)} audio files at 1.25x speed!</div>', unsafe_allow_html=True)
                        except Exception as e:
                            st.markdown(f'<div class="error-card">❌ Error generating audio: {str(e)}</div>', unsafe_allow_html=True)
                            logger.error(f"Audio generation error: {str(e)}")
                        st.rerun()
            else:
                st.markdown(f'<div class="success-card">✅ Audio files ready for {len(st.session_state.audio_paths)} scenes!</div>', unsafe_allow_html=True)
                
                # Audio preview
                with st.expander("🎵 Preview Scene Audio", expanded=False):
                    for scene_key, scene_data in st.session_state.narrations["narrations"].items():
                        scene_num = scene_data["scene_number"]
                        mp3_path = st.session_state.audio_paths.get(scene_key)
                        if mp3_path and os.path.exists(mp3_path):
                            st.markdown(f"**Scene {scene_num}:** {scene_data['narration']}")
                            with open(mp3_path, "rb") as f:
                                st.audio(f.read(), format="audio/mp3")
                            st.markdown("---")

        # Step 6: Generate final video
        if st.session_state.comic_images and st.session_state.audio_paths:
            st.markdown("---")
            st.markdown('<div class="section-header">🎬 Step 6: Generate Final Video</div>', unsafe_allow_html=True)
            st.markdown('<div class="success-card">✅ All assets ready! You can now create the final video.</div>', unsafe_allow_html=True)
            
            if st.button("🎬 Generate Final Video", type="primary"):
                with st.spinner("🎥 Assembling video... This may take a few minutes..."):
                    audio_map = st.session_state.audio_paths
                    w, h = (1920, 1080) if resolution == "1920x1080" else (1280, 720)
                    out_dir = os.path.join("data", "videos")
                    os.makedirs(out_dir, exist_ok=True)
                    
                    try:
                        result = build_video(
                            images=st.session_state.comic_images,
                            scene_audio=audio_map,
                            out_dir=out_dir,
                            title=st.session_state.page_info["title"],
                            fps=int(fps),
                            resolution=(w, h),
                            crossfade_sec=0.3,
                            min_scene_seconds=float(min_scene_seconds),
                            head_pad=0.15,
                            tail_pad=0.15,
                            bg_music_path=None,
                            bg_music_volume=0.08
                        )
                        st.session_state.final_video = result["video_path"]
                        st.markdown('<div class="success-card">🎉 Video generated successfully!</div>', unsafe_allow_html=True)
                        
                        if os.path.exists(st.session_state.final_video):
                            st.video(st.session_state.final_video)
                            
                            with open(st.session_state.final_video, "rb") as f:
                                st.download_button(
                                    label="💾 Download Video (MP4)",
                                    data=f.read(),
                                    file_name=os.path.basename(st.session_state.final_video),
                                    mime="video/mp4",
                                    use_container_width=True
                                )
                    except Exception as e:
                        st.markdown(f'<div class="error-card">❌ Error generating video: {str(e)}</div>', unsafe_allow_html=True)
                        logger.error(f"Video generation error: {str(e)}")
        
        # If video already exists
        if hasattr(st.session_state, 'final_video') and os.path.exists(st.session_state.final_video):
            st.markdown("#### 🎥 Your Video:")
            st.video(st.session_state.final_video)
            with open(st.session_state.final_video, "rb") as f:
                st.download_button(
                    label="💾 Download Video (MP4)",
                    data=f.read(),
                    file_name=os.path.basename(st.session_state.final_video),
                    mime="video/mp4",
                    use_container_width=True
                )

# Call main function if script is run directly
if __name__ == "__main__":
    main()
