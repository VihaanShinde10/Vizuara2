# VidyAI Vizuara - Complete Guide 📚

**Version 3.1 - Student-Friendly Edition**  
**Everything You Need in One Place**  
**Last Updated:** October 18, 2025

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [What's New in v3.1](#whats-new-in-v31)
3. [Installation & Setup](#installation--setup)
4. [AI Models Explained](#ai-models-explained)
5. [Step-by-Step Usage](#step-by-step-usage)
6. [Settings Guide](#settings-guide)
7. [Troubleshooting](#troubleshooting)
8. [FFmpeg Installation](#ffmpeg-installation)
9. [Before & After Examples](#before--after-examples)
10. [Tips & Best Practices](#tips--best-practices)

---

## 🚀 Quick Start

### 1. Install Requirements

```bash
# Install Python packages
pip install streamlit groq google-generativeai gtts pydub pillow moviepy

# Or use requirements.txt
pip install -r requirements.txt
```

### 2. Get API Keys

```bash
# Groq API (for text generation)
Visit: https://console.groq.com
Sign up → Create API key → Copy it

# Gemini API (for images)
Visit: https://aistudio.google.com/app/apikey  
Sign in → Create API key → Copy it
```

### 3. Create .env File

```bash
# Create file named .env in VidyAi_Vizuara folder
GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY=your_gemini_key_here
```

### 4. Run the App

```bash
cd VidyAi_Vizuara
streamlit run final.py
```

### 5. Create Your First Video!

1. Enter a topic (e.g., "Moon Landing")
2. Click through each step (6 steps total)
3. Wait ~18 minutes
4. Download your educational video!

**That's it!** 🎉

---

## ✨ What's New in v3.1

### Major Improvements:

#### 1. **Student-Friendly Language** ✅
- **Before:** "In the resplendent palace of Ayodhya, a new era dawns..."
- **After:** "In the beautiful palace of Ayodhya, Queen Kausalya holds baby Rama..."
- All content now uses simple, clear English
- No complex vocabulary
- Short, easy sentences

#### 2. **Engaging Flow** ✅
- Natural transitions ("First...", "Then...", "After that...")
- Story-telling style instead of textbook style
- Active voice throughout
- "What happens next?" excitement

#### 3. **Better UI** ✅
- Fixed alignment issues
- Consistent spacing
- Clean, professional design
- Proper step indicators

#### 4. **Robust Video Generation** ✅
- Fixed audio fade warnings
- Fixed crossfade issues
- No more spam messages
- Clear status updates
- Better error handling

---

## 🔧 Installation & Setup

### Prerequisites

- Windows 10/11
- Python 3.8 or higher
- Internet connection
- 2GB free disk space

### Detailed Installation

#### Step 1: Install Python Packages

```bash
# Core packages
pip install streamlit
pip install groq
pip install google-generativeai
pip install gtts
pip install pydub
pip install pillow
pip install numpy

# Video processing (choose one):
# Option A: MoviePy (RECOMMENDED - includes FFmpeg)
pip install moviepy

# Option B: Just FFmpeg (manual installation required)
# See FFmpeg section below
```

#### Step 2: Set Up API Keys

**Create .env file:**

```bash
# In VidyAi_Vizuara folder, create file named: .env
# Add these lines:

GROQ_API_KEY=gsk_your_actual_key_here
GEMINI_API_KEY=your_actual_gemini_key_here
```

**Get Keys:**

**Groq API Key:**
1. Go to https://console.groq.com
2. Sign up (free)
3. Click "Create API Key"
4. Copy the key
5. Paste in .env file

**Gemini API Key:**
1. Go to https://aistudio.google.com/app/apikey
2. Sign in with Google
3. Click "Create API Key"
4. Copy the key
5. Paste in .env file

#### Step 3: Verify Installation

```bash
# Test imports
python -c "import streamlit; print('✅ Streamlit OK')"
python -c "import groq; print('✅ Groq OK')"
python -c "from google import genai; print('✅ Gemini OK')"
python -c "from gtts import gTTS; print('✅ gTTS OK')"
python -c "from moviepy import ImageClip; print('✅ MoviePy OK')"

# If all print OK, you're ready!
```

#### Step 4: Run the Application

```bash
cd VidyAi_Vizuara
streamlit run final.py
```

Browser will open automatically at `http://localhost:8501`

---

## 🤖 AI Models Explained

### The Complete Pipeline

```
Wikipedia Article
       ↓
[GROQ Llama 3.3 70B] → Writes storyline (simple language)
       ↓
[GROQ Llama 3.3 70B] → Creates 10 scene descriptions
       ↓
[Gemini 2.5 Flash] → Draws 10 comic panels
       ↓
[GROQ Llama 3.3 70B] → Writes 10 narrations
       ↓
[gTTS] → Speaks narrations (creates audio)
       ↓
[MoviePy] → Combines images + audio
       ↓
Final Educational Video! 🎬
```

### Model Details

#### 1. Groq (Llama 3.3 70B) - The Writer 📝

**What it does:** Writes all text content
**Where used:**
- `story_generator.py` - Storyline and scenes
- `narration_generator.py` - Narration text

**Cost:** FREE (6,000 tokens/minute)
**Speed:** ⚡ Very fast (500+ tokens/sec)

**Configuration:**
```python
model="llama-3.3-70b-versatile"
temperature=0.4  # Balanced creativity
max_tokens=12000 # Max output length
```

**What it generates:**
- Storyline: ~1,000 words in simple English
- Scene prompts: 10 visual descriptions
- Narrations: 10 scripts (40-70 words each)

#### 2. Gemini 2.5 Flash Image - The Artist 🎨

**What it does:** Creates comic panel images
**Where used:**
- `gemini_image_generator.py`

**Cost:** FREE (1,500 requests/day = 150 videos/day)
**Speed:** 🚀 Fast (1 image/minute)

**Configuration:**
```python
model="gemini-2.5-flash-image"
temperature=0.7  # Creativity level
```

**What it generates:**
- 10 high-quality comic images
- 1024x1024 resolution
- JPG format

#### 3. gTTS - The Voice Actor 🗣️

**What it does:** Converts text to speech
**Where used:**
- `tts_generator.py`

**Cost:** FREE (unlimited)
**Speed:** ⚡ Very fast (1 audio/second)

**Configuration:**
```python
lang="en"      # Language
tld="com"      # Accent (US)
speed=1.25     # 25% faster
```

**What it generates:**
- 10 MP3 audio files
- Natural voice
- Multiple languages supported

#### 4. MoviePy - The Film Editor 🎬

**What it does:** Assembles final video
**Where used:**
- `video_editor.py`

**Cost:** FREE (local software)
**Speed:** 🐌 Moderate (2 minutes)

**What it does:**
- Combines images + audio
- Adds transitions
- Exports MP4 video
- 1920x1080 resolution

### Cost Breakdown

| Service | Per Video | Daily Limit | Monthly Cost |
|---------|-----------|-------------|--------------|
| Groq | FREE | ~40 videos | $0.00 |
| Gemini | FREE | ~150 videos | $0.00 |
| gTTS | FREE | Unlimited | $0.00 |
| MoviePy | FREE | Unlimited | $0.00 |
| **TOTAL** | **$0.00** | **100+ videos** | **$0.00** |

**You can create 100+ videos per day for FREE!** 🎉

### Processing Time

For a typical 10-scene video:

```
Groq (storyline)     :  2 min ████████
Groq (scenes)        :  1 min ████
Gemini (10 images)   : 10 min ████████████████████████
Groq (narrations)    :  2 min ████████
gTTS (10 audio)      :  1 min ████
MoviePy (video)      :  2 min ████████
                       ──────────────
TOTAL                : ~18 minutes
```

---

## 📖 Step-by-Step Usage

### Complete Workflow

#### Step 1: Search Wikipedia 🔍

1. Open the app
2. Enter a topic in the search box
   - Examples: "Albert Einstein", "Moon Landing", "Ramayana"
3. Click "🔎 Search"
4. Select from results

**Time:** 30 seconds

#### Step 2: Generate Storyline 📖

1. Review Wikipedia summary (optional)
2. Adjust settings in sidebar:
   - Story Length: Medium (recommended)
   - Comic Style: Cartoon or Comic Book
   - Number of Scenes: 10
3. Click "✨ Generate Comic Storyline"
4. Review the storyline

**Time:** 2 minutes

**What you get:**
- 1,000-word story in simple language
- 5 acts with clear structure
- Timeline and characters
- Key themes

#### Step 3: Generate Scene Prompts 🎬

1. Click "🎭 Generate Scene Prompts"
2. Wait for AI to create descriptions
3. Review scene prompts (optional)

**Time:** 1 minute

**What you get:**
- 10 visual scene descriptions
- Clear, detailed prompts for images
- Chronologically ordered

#### Step 4: Generate Images 🎨

1. Make sure Gemini API key is entered
2. Click "🎨 Generate All Comic Images"
3. Watch progress bar
4. View generated images

**Time:** 10 minutes

**What you get:**
- 10 high-quality comic panels
- Consistent art style
- Saved as JPG files

#### Step 5: Generate Narration & Audio 🎙️

1. Configure narration settings:
   - Style: Educational (recommended for students)
   - Tone: Engaging
   - Language: English
   - Accent: US (or your preference)
2. Click "🎙️ Generate All Scene Narrations"
3. Review narrations (optional)
4. Click "🔊 Generate Audio for All Scenes"
5. Listen to audio samples

**Time:** 3 minutes total

**What you get:**
- 10 narration texts (simple language)
- 10 MP3 audio files
- Natural voice at 1.25x speed

#### Step 6: Generate Final Video 🎥

1. Configure video settings:
   - Resolution: 1920x1080 (Full HD)
   - Frame Rate: 30 fps
   - Min Scene Duration: 3 seconds
2. Click "🎬 Generate Final Video"
3. Wait for video assembly
4. Watch and download!

**Time:** 2 minutes

**What you get:**
- Complete MP4 video
- 3-5 minutes duration
- Professional quality
- Synchronized audio and visuals

### Total Time: ~18 minutes

---

## ⚙️ Settings Guide

### Story Settings

**Story Length:**
- **Short** (500 words) - Quick overview
- **Medium** (1000 words) - Balanced ⭐ RECOMMENDED
- **Long** (2000 words) - Detailed story

**Comic Art Style:**
- **Cartoon** - Fun, colorful (great for younger students) ⭐
- **Comic Book** - Classic style (popular with all ages) ⭐
- **Manga** - Japanese style
- **Graphic Novel** - Serious, detailed
- **Superhero** - Bold, action-oriented
- **Noir** - Dark, dramatic

**Number of Scenes:**
- **3-5** - Very quick story
- **10** - Complete story ⭐ RECOMMENDED
- **15** - Detailed, comprehensive

### Narration Settings

**Narration Style:**
- **Dramatic** - Exciting, movie-like
- **Educational** - Clear explanations ⭐ RECOMMENDED
- **Storytelling** - Like telling to friends ⭐ RECOMMENDED
- **Documentary** - Factual, informative

**Voice Tone:**
- **Engaging** - Enthusiastic, exciting ⭐ RECOMMENDED
- **Serious** - Respectful, thoughtful
- **Playful** - Fun, lighthearted
- **Informative** - Clear, helpful

**Language:**
- English (en) ⭐
- Hindi (hi)
- Spanish (es)
- French (fr)
- And 6 more...

**Accent (English only):**
- 🇺🇸 US (com) ⭐ RECOMMENDED
- 🇬🇧 UK (co.uk)
- 🇮🇳 India (co.in)
- 🇦🇺 Australia (com.au)
- 🇨🇦 Canada (ca)
- 🇿🇦 South Africa (co.za)

### Video Settings

**Resolution:**
- **1280x720** (720p) - Faster processing
- **1920x1080** (1080p) - Full HD ⭐ RECOMMENDED

**Frame Rate:**
- **24 fps** - Cinematic
- **25 fps** - PAL standard
- **30 fps** - Standard ⭐ RECOMMENDED

**Min Scene Duration:**
- **2 seconds** - Fast-paced
- **3 seconds** - Balanced ⭐ RECOMMENDED
- **5 seconds** - Slow-paced

### Recommended Settings for Students

```
✅ Story Length: Medium
✅ Comic Style: Cartoon or Comic Book
✅ Scenes: 10
✅ Narration Style: Educational
✅ Voice Tone: Engaging
✅ Language: English
✅ Accent: US
✅ Resolution: 1920x1080
✅ FPS: 30
✅ Scene Duration: 3 seconds
```

---

## 🔍 Troubleshooting

### Common Issues & Solutions

#### 1. API Key Errors

**Problem:** "⚠️ Please enter your Groq API key"

**Solutions:**
```bash
# Check .env file exists
ls .env

# Check .env file content
cat .env

# Make sure format is correct:
GROQ_API_KEY=gsk_yourkey
GEMINI_API_KEY=yourkey

# No spaces around =
# No quotes around keys
# Keys on separate lines
```

#### 2. Video Generation Fails

**Problem:** "Neither MoviePy nor FFmpeg is available"

**Solution:**
```bash
# Install MoviePy (easiest)
pip install moviepy

# Restart app
streamlit run final.py
```

**Alternative:** Install FFmpeg (see FFmpeg section below)

#### 3. Images Not Generating

**Problem:** Gemini API errors

**Solutions:**
- Check API key is correct
- Check daily limit (1,500 requests/day)
- Wait a few minutes and try again
- Check internet connection

#### 4. Audio Not Working

**Problem:** No audio in video

**Solutions:**
```bash
# Install pydub
pip install pydub

# Install ffmpeg (for audio processing)
pip install moviepy

# Check audio files exist
ls data/narration/YourTopic/
```

#### 5. UI Looks Wrong

**Problem:** Misaligned elements

**Solutions:**
- Refresh page (F5)
- Clear browser cache
- Try different browser (Chrome recommended)
- Restart Streamlit app

#### 6. App Won't Start

**Problem:** Streamlit errors

**Solutions:**
```bash
# Update streamlit
pip install --upgrade streamlit

# Check Python version
python --version  # Should be 3.8+

# Reinstall packages
pip install -r requirements.txt
```

#### 7. Slow Performance

**Problem:** Generation takes too long

**Solutions:**
- Reduce number of scenes (try 5 instead of 10)
- Use 720p resolution instead of 1080p
- Close other applications
- Check internet speed
- Try during off-peak hours

---

## 🎬 FFmpeg Installation

### Why FFmpeg?

FFmpeg is needed for video generation. You have 2 options:

### Option 1: Install MoviePy (EASIEST ⭐)

```bash
# This includes FFmpeg automatically
pip install moviepy

# That's it! No manual configuration needed.
```

**This is the RECOMMENDED method!** ✅

### Option 2: Manual FFmpeg Installation

If MoviePy doesn't work, install FFmpeg manually:

#### For Windows:

**Step 1: Download**
- Go to: https://www.gyan.dev/ffmpeg/builds/
- Download: `ffmpeg-release-essentials.7z`

**Step 2: Extract**
- Use 7-Zip to extract
- You'll get a folder like: `ffmpeg-2024-10-18-essentials_build`

**Step 3: Copy to Location**
```bash
# Create folder
mkdir C:\ffmpeg
mkdir C:\ffmpeg\bin

# Copy these files from extracted folder to C:\ffmpeg\bin\:
# - ffmpeg.exe
# - ffplay.exe
# - ffprobe.exe
```

**Step 4: Add to PATH**

Method A - PowerShell (Administrator):
```powershell
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\ffmpeg\bin", "Machine")
```

Method B - GUI:
1. Press `Win + X` → System
2. Advanced system settings
3. Environment Variables
4. Edit "Path" in System variables
5. Add: `C:\ffmpeg\bin`
6. Click OK on all dialogs

**Step 5: Verify**
```bash
# Close and reopen PowerShell
ffmpeg -version

# Should show version info
```

**Step 6: Restart App**
```bash
streamlit run final.py
```

### Verify Video Generation Works

```bash
# Test command
python -c "from video_editor import build_video; print('✅ Video editor OK')"
```

---

## 📊 Before & After Examples

### Language Improvements

#### Example 1: Storyline

**Before (Complex):**
> "The commencement of the narrative unfolds within the resplendent confines of the palace of Ayodhya, where Queen Kausalya cradles the serene newborn Rama, whilst jubilant servants and family members congregate, basking in the warm, golden luminescence of celebration..."

**After (Student-Friendly):**
> "Our story starts in the beautiful palace of Ayodhya. Queen Kausalya holds baby Rama. Happy servants and family gather around them. Golden light fills the room as everyone celebrates. This baby will change the kingdom's future."

#### Example 2: Narration

**Before (Too Formal):**
> "In the depths of the primordial forest, shrouded in ominous shadows, the malevolent figure of Ravana emerges with nefarious intent..."

**After (Simple):**
> "Deep in the dark forest, Ravana appears from the shadows. He looks scary and evil. Sita is afraid as he comes closer..."

#### Example 3: Scene Description

**Before (Technical):**
> "Scene 3: The Abduction - A pivotal moment wherein the protagonist's beloved is forcibly removed from her sanctuary by the antagonist, establishing the central conflict of the narrative arc through dramatic chiaroscuro lighting and dynamic compositional elements..."

**After (Clear):**
> "Scene 3: Sita is Kidnapped
> 
> Ravana grabs Sita in the forest. She looks scared. Rama and Lakshmana see what's happening and start running to help. Dark shadows make it look dangerous."

### Key Vocabulary Changes

| ❌ Complex | ✅ Simple |
|-----------|----------|
| resplendent | beautiful |
| serene | calm, peaceful |
| jubilant | very happy |
| unwavering | steady, loyal |
| precariously | dangerously |
| malevolent | evil |
| primordial | ancient, old |
| chiaroscuro | light and shadow |
| countenance | face |
| celestial | heavenly |

### Video Generation Improvements

**Before (Spam Warnings):**
```
Audio fade effects not available, using plain audio...
Crossfade not available, skipping...
Audio fade effects not available, using plain audio...
Crossfade not available, skipping...
[Repeated 10 times - very annoying!]
```

**After (Clean Output):**
```
✓ MoviePy 2.x detected and loaded
✓ Successfully concatenated 10 video clips
✓ Successfully composed 10 audio tracks
✓ Video written successfully with optimized settings
✓ Resources cleaned up
🎉 Video generation complete: Ramayana.mp4
   - Total scenes: 10
   - Total duration: 165.3s
   - Resolution: 1920x1080
   - FPS: 30
```

---

## 💡 Tips & Best Practices

### For Best Results

#### 1. Choose Good Topics

**✅ Good Topics:**
- Historical events (Moon Landing, World War II)
- Famous people (Einstein, Marie Curie)
- Scientific concepts (Solar System, Photosynthesis)
- Cultural stories (Greek Mythology, Ramayana)
- Sports heroes (Sachin Tendulkar)

**❌ Avoid:**
- Very recent events (may lack Wikipedia content)
- Controversial topics
- Topics with limited information

#### 2. Optimal Settings

```
✅ Use "Medium" story length
✅ Use "Educational" narration style  
✅ Use "Engaging" voice tone
✅ Generate 10 scenes (not too few, not too many)
✅ Use 1080p resolution for quality
✅ Use 30 fps for smooth playback
```

#### 3. Test First

```bash
# Before generating full video:
# 1. Generate just 3 scenes first
# 2. Check quality
# 3. If good, generate full 10 scenes
```

#### 4. Check Generated Content

- Read the storyline - is it simple and clear?
- Review scene prompts - are they visual and detailed?
- Listen to audio - is it engaging and natural?
- Watch video preview - does it flow well?

#### 5. For Classroom Use

- ✅ Preview video before showing to students
- ✅ Prepare discussion questions
- ✅ Have students take notes during video
- ✅ Follow up with comprehension check
- ✅ Let students create their own videos!

### Performance Tips

#### Speed Up Generation

```bash
# Use fewer scenes
Scenes: 5 instead of 10

# Use lower resolution  
Resolution: 720p instead of 1080p

# Close other applications
# Use during off-peak hours
```

#### Save Resources

```bash
# Reuse generated content
# Storylines saved in: data/text/
# Images saved in: data/images/
# Audio saved in: data/narration/
# Videos saved in: data/videos/

# Can regenerate video without regenerating everything!
```

#### Batch Processing

```python
# Create multiple topics in sequence:
topics = ["Moon Landing", "Einstein", "Photosynthesis"]

for topic in topics:
    # Generate each video
    # Wait ~18 minutes between each
```

---

## 🎓 For Teachers

### Classroom Integration

**Perfect for:**
- History lessons
- Science explanations
- Literature summaries
- Social studies
- Language arts

### Lesson Plan Ideas

#### 1. Direct Instruction
- Show video at beginning of lesson
- Introduce new topics
- Provide visual overview
- Generate interest

#### 2. Review & Reinforcement
- Use as end-of-unit review
- Summarize key concepts
- Prepare for tests
- Reinforce learning

#### 3. Student Projects
- Have students create videos
- Research and learn
- Develop presentation skills
- Use technology meaningfully

#### 4. Flipped Classroom
- Assign video as homework
- Students watch before class
- Use class time for discussion
- Deepen understanding

### Assessment Ideas

**Discussion Questions:**
- What was the main idea?
- Why is this important?
- What did you learn?
- What questions do you have?

**Activities:**
- Write a summary
- Create a timeline
- Draw key scenes
- Act out important moments

**Projects:**
- Create your own video
- Write an essay
- Make a presentation
- Design a poster

---

## 📈 Success Metrics

### What Makes a Good Video?

✅ **Content Quality:**
- Simple, clear language
- Accurate facts
- Engaging storyline
- Good flow

✅ **Visual Quality:**
- Clear images
- Consistent style
- Good composition
- Appropriate for age

✅ **Audio Quality:**
- Clear voice
- Good pacing
- Natural tone
- Proper volume

✅ **Educational Value:**
- Teaches something new
- Easy to understand
- Memorable
- Interesting

### Typical Results

**For a 10-scene video:**
- Duration: 3-5 minutes
- File size: 50-100 MB
- Processing time: ~18 minutes
- Quality: HD (1920x1080)
- Audio: Clear, natural voice
- Cost: $0.00 (FREE!)

---

## 🎉 Summary

### What You Get

**VidyAI Vizuara creates:**
- ✅ Educational videos
- ✅ Simple, student-friendly language
- ✅ Engaging storylines
- ✅ High-quality visuals
- ✅ Natural narration
- ✅ Professional results
- ✅ Completely FREE

### Quick Stats

```
Time per video:    ~18 minutes
Cost per video:    $0.00
Videos per day:    100+
Quality:           HD 1080p
Languages:         10+
Free forever:      YES! ✅
```

### Ready to Start?

```bash
# 1. Install packages
pip install moviepy

# 2. Get API keys
# Groq: console.groq.com
# Gemini: aistudio.google.com/app/apikey

# 3. Create .env file
GROQ_API_KEY=your_key
GEMINI_API_KEY=your_key

# 4. Run app
streamlit run final.py

# 5. Create videos!
🎬 Enter topic → Generate → Download!
```

---

## 📞 Need Help?

### Check Logs

```bash
# View application logs
tail -f wiki_comic_generator.log
```

### Common Commands

```bash
# Restart app
streamlit run final.py

# Test components
python -c "from story_generator import StoryGenerator; print('OK')"
python -c "from video_editor import build_video; print('OK')"

# Check versions
pip show streamlit
pip show moviepy
ffmpeg -version
```

### Still Stuck?

1. Read this guide again
2. Check all API keys
3. Verify all packages installed
4. Try with a simple topic first
5. Check internet connection

---

## 🎯 Final Checklist

Before creating your first video:

- [ ] Python 3.8+ installed
- [ ] All packages installed (`pip install moviepy`)
- [ ] Groq API key obtained
- [ ] Gemini API key obtained
- [ ] .env file created with both keys
- [ ] App runs (`streamlit run final.py`)
- [ ] Internet connection working
- [ ] 2GB free disk space

**All checked? You're ready to create amazing educational videos!** 🚀

---

**Made with ❤️ for Students and Teachers**

**Version:** 3.1 - Student-Friendly Edition  
**Last Updated:** October 18, 2025  
**Team:** Airavat

**🎊 Everything you need is in this one guide! 🎊**

