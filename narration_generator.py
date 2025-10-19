import os
import json
import logging
from typing import List, Dict, Any, Optional
from groq import Groq


class NarrationGenerator:
    def __init__(self, api_key: str, text_dir: str = "data/text", narration_dir: str = "data/narration"):
        """
        Initialize the Narration Generator
        
        Args:
            api_key: Groq API key
            text_dir: Directory containing story text files
            narration_dir: Directory to store generated narration files
        """
        self.client = Groq(api_key=api_key)
        self.text_dir = text_dir
        self.narration_dir = narration_dir
        self.create_narration_directory()
        logger.info("NarrationGenerator initialized with Groq client")

    def create_narration_directory(self) -> None:
        """Create narration directory for storing generated narration files"""
        try:
            if not os.path.exists(self.narration_dir):
                os.makedirs(self.narration_dir)
                logger.info(f"Created narration directory: {self.narration_dir}")
        except Exception as e:
            logger.error(f"Failed to create narration directory: {str(e)}")
            raise RuntimeError(f"Failed to create narration directory: {str(e)}")

    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a string to be used as a filename
        
        Args:
            filename: Original filename string
            
        Returns:
            Sanitized filename safe for all operating systems
        """
        # Replace invalid characters with underscores
        sanitized = filename.replace('\\', '_').replace('/', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_').replace(':', '_')
        # Limit filename length
        return sanitized[:200]

    def load_story_content(self, title: str) -> Dict[str, Any]:
        """
        Load story content from text files
        
        Args:
            title: Title of the story
            
        Returns:
            Dictionary containing loaded story content
        """
        try:
            safe_title = self.sanitize_filename(title)
            story_dir = os.path.join(self.text_dir, safe_title)
            
            if not os.path.exists(story_dir):
                logger.error(f"Story directory not found: {story_dir}")
                return {}
            
            content = {}
            
            # Load storyline
            storyline_path = os.path.join(story_dir, f"{safe_title}_storyline.txt")
            if os.path.exists(storyline_path):
                with open(storyline_path, 'r', encoding='utf-8') as f:
                    content['storyline'] = f.read()
            
            # Load scene prompts
            scenes_path = os.path.join(story_dir, f"{safe_title}_scene_prompts.txt")
            if os.path.exists(scenes_path):
                with open(scenes_path, 'r', encoding='utf-8') as f:
                    content['scene_prompts'] = f.read()
            
            # Load page info
            page_info_path = os.path.join(story_dir, f"{safe_title}_page_info.json")
            if os.path.exists(page_info_path):
                with open(page_info_path, 'r', encoding='utf-8') as f:
                    content['page_info'] = json.load(f)
            
            # Load combined content
            combined_path = os.path.join(story_dir, f"{safe_title}_combined.txt")
            if os.path.exists(combined_path):
                with open(combined_path, 'r', encoding='utf-8') as f:
                    content['combined'] = f.read()
            
            logger.info(f"Successfully loaded story content for: {title}")
            return content
            
        except Exception as e:
            logger.error(f"Failed to load story content: {str(e)}")
            return {}

    def generate_scene_narration(self, title: str, scene_prompt: str, scene_number: int, 
                                narration_style: str = "dramatic", voice_tone: str = "engaging",
                                target_seconds: int = 20, min_words: int = 40, max_words: int = 70) -> str:
        """
        Generate narration for a specific scene
        
        Args:
            title: Title of the story
            scene_prompt: Scene prompt text
            scene_number: Number of the scene
            narration_style: Style of narration (dramatic, educational, storytelling, documentary)
            voice_tone: Tone of voice (engaging, serious, playful, informative)
            
        Returns:
            Generated narration text for the scene
        """
        logger.info(f"Generating narration for scene {scene_number} of '{title}'")
        
        # Style-specific guidance - SIMPLIFIED FOR STUDENTS
        style_guidance = {
            "dramatic": "Tell the story in an exciting way that makes students feel like they're watching a movie. Use simple but powerful words that create emotion. Make them feel what's happening - the tension, the excitement, the joy or sadness.",
            "educational": "Explain what's happening in a clear, easy way that helps students learn. Use simple words to explain why things matter and what they mean. Make learning fun and interesting, not boring.",
            "storytelling": "Tell it like you're sharing an exciting story with friends. Use simple words, short sentences, and make students care about what happens to the characters. Keep them wanting to know 'what happens next?'",
            "documentary": "Explain the facts clearly using simple language. Help students understand what really happened and why it's important. Be informative but not boring - make history come alive with clear, interesting explanations."
        }.get(narration_style.lower(), "Use simple, clear, and engaging language to describe what's happening.")
        
        # Voice tone guidance - SIMPLIFIED FOR STUDENTS
        tone_guidance = {
            "engaging": "Sound excited and energetic! Make students want to listen. Use a friendly, enthusiastic voice like you're telling them something really cool. Keep the energy up!",
            "serious": "Use a calm, respectful voice that shows this is important. Don't be boring, but show that what you're saying matters. Be thoughtful and clear.",
            "playful": "Keep it light and fun! Use a friendly, warm voice that makes learning enjoyable. Smile while you talk - students should feel like learning is fun, not a chore.",
            "informative": "Be clear and helpful, like a good teacher. Explain things simply so everyone understands. Be friendly but focused on helping students learn."
        }.get(voice_tone.lower(), "Use a clear, friendly tone that students will enjoy listening to.")
        
        # Determine word range based on target seconds if provided
        # At 1.25x speed playback: 20 seconds actual = 16 seconds of audio content
        # At ~2.5 words per second: 16 * 2.5 = 40 words for 20 seconds at 1.25x
        if target_seconds and target_seconds > 0:
            # Adjust for 1.25x playback speed
            actual_audio_seconds = target_seconds / 1.25  # 20 / 1.25 = 16 seconds
            approx_words = int(actual_audio_seconds * 2.5)  # 16 * 2.5 = 40 words
            lo = max(min_words, approx_words - 10)
            hi = max(max_words, approx_words + 10)
        else:
            lo = min_words
            hi = max_words

        # Load story content for context
        story_content = self.load_story_content(title)
        storyline = story_content.get('storyline', '')
        
        # Create comprehensive prompt for narration generation
        prompt = f"""
        You are creating an engaging, easy-to-understand voice-over narration for scene {scene_number} of "{title}". This will be heard by STUDENTS, so use SIMPLE, CLEAR language that everyone can understand. Make it exciting but brief!
        
        CORE REQUIREMENTS:
        - Length: {lo}–{hi} words (short but powerful for {target_seconds} seconds at 1.25x speed)
        - Structure: 2-4 SHORT, SIMPLE sentences that flow naturally
        - Use SIMPLE WORDS - avoid complex vocabulary (e.g., say "brave" not "valiant", "happy" not "jubilant")
        - Content: Explain what's happening, why it matters, and how people feel
        - Pacing: Mix short and medium sentences to keep it interesting
        - Use ONLY facts from the storyline and scene - don't make things up
        - If you're not sure about something, leave it out
        - Think: "Would a 12-year-old understand every word?" If not, simplify it!
        
        NARRATION STYLE GUIDANCE:
        Style: {narration_style}
        {style_guidance}
        
        VOICE TONE GUIDANCE:
        Tone: {voice_tone}
        {tone_guidance}
        
        WHAT TO INCLUDE (in simple language):
        - Where & When: Where is this happening? What time is it? What's the mood?
        - What's Happening: What are people doing? What do they look like? How do they feel?
        - Why It Matters: Why is this moment important? What does it mean for the story?
        - The Stakes: What could go wrong? What are people trying to achieve?
        - The Flow: How does this connect to what happened before and what comes next?
        - Make It Real: Help students imagine they're there - what would they see and feel?
        
        COMPLETE STORYLINE (your authoritative source - use this for context and accuracy):
        {storyline}
        
        CURRENT SCENE DETAILS (visual context for this specific moment):
        {scene_prompt}
        
        IMPORTANT GUIDELINES FOR STUDENTS:
        - Write like you're telling an exciting story to a friend - keep it natural and engaging
        - Use SIMPLE WORDS that students understand - no fancy vocabulary
        - Use SHORT SENTENCES that are easy to follow
        - Make every word count - be clear and interesting, not wordy
        - Help students feel connected to the story and care about what happens
        - Use present tense to make it feel like it's happening now (e.g., "Rama fights" not "Rama fought")
        - Don't just describe what students can see - explain WHY it matters
        - Connect smoothly to help the story flow from scene to scene
        - Build excitement that makes students want to see what happens next
        
        Generate an engaging narration of {lo}–{hi} words using SIMPLE, STUDENT-FRIENDLY language that brings this scene to life. Output ONLY the narration text with no extra words, labels, or formatting.
        """
        
        try:
            # Generate narration using Groq with Llama 3.3 70B Versatile
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an expert storyteller who creates engaging narrations for STUDENTS using SIMPLE, CLEAR language. You avoid complex words and write like you're explaining something exciting to a friend. You use short sentences, everyday vocabulary, and make sure everything is easy to understand. You make facts interesting and help students care about the story. You always think: 'Would a student understand every single word I'm using?' If not, you choose a simpler word. Your narrations are accurate, engaging, and perfect for young learners."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.4,
                max_tokens=2000,  # Increased for detailed narration
                top_p=0.9
            )
            
            narration = response.choices[0].message.content.strip()
            logger.info(f"Successfully generated narration for scene {scene_number}")
            
            return narration
            
        except Exception as e:
            logger.error(f"Failed to generate narration for scene {scene_number}: {str(e)}")
            return f"Error generating narration: {str(e)}"

    def generate_all_scene_narrations(self, title: str, narration_style: str = "dramatic", 
                                    voice_tone: str = "engaging") -> Dict[str, Any]:
        """
        Generate narration for all scenes of a story
        
        Args:
            title: Title of the story
            narration_style: Style of narration
            voice_tone: Tone of voice
            
        Returns:
            Dictionary containing all generated narrations and metadata
        """
        logger.info(f"Generating narrations for all scenes of '{title}'")
        
        # Load story content
        story_content = self.load_story_content(title)
        if not story_content:
            logger.error(f"Could not load story content for: {title}")
            return {}
        
        # Parse scene prompts from the loaded content
        scene_prompts = self._parse_scene_prompts(story_content.get('scene_prompts', ''))
        
        if not scene_prompts:
            logger.error(f"No scene prompts found for: {title}")
            return {}
        
        # Generate narration for each scene
        narrations = {}
        for i, scene_prompt in enumerate(scene_prompts, 1):
            narration = self.generate_scene_narration(
                title, scene_prompt, i, narration_style, voice_tone
            )
            narrations[f"scene_{i}"] = {
                "scene_number": i,
                "narration": narration,
                "scene_prompt": scene_prompt
            }
        
        # Save narrations to files
        file_paths = self._save_narrations(title, narrations, narration_style, voice_tone)
        
        result = {
            "title": title,
            "narration_style": narration_style,
            "voice_tone": voice_tone,
            "total_scenes": len(scene_prompts),
            "narrations": narrations,
            "file_paths": file_paths
        }
        
        logger.info(f"Successfully generated {len(scene_prompts)} narrations for '{title}'")
        return result

    def _parse_scene_prompts(self, scene_prompts_text: str) -> List[str]:
        """
        Parse individual scene prompts from the loaded text
        
        Args:
            scene_prompts_text: Raw text containing scene prompts
            
        Returns:
            List of individual scene prompts
        """
        try:
            # Split by scene markers
            scenes = []
            lines = scene_prompts_text.split('\n')
            current_scene = []
            
            for line in lines:
                if line.strip().startswith('## Scene'):
                    if current_scene:
                        scenes.append('\n'.join(current_scene).strip())
                    current_scene = [line]
                elif line.strip().startswith('==='):
                    if current_scene:
                        scenes.append('\n'.join(current_scene).strip())
                        current_scene = []
                elif current_scene:
                    current_scene.append(line)
            
            # Add the last scene if exists
            if current_scene:
                scenes.append('\n'.join(current_scene).strip())
            
            # Filter out empty scenes
            scenes = [scene for scene in scenes if scene.strip()]
            
            logger.info(f"Parsed {len(scenes)} scene prompts")
            return scenes
            
        except Exception as e:
            logger.error(f"Failed to parse scene prompts: {str(e)}")
            return []

    def _save_narrations(self, title: str, narrations: Dict[str, Any], 
                        narration_style: str, voice_tone: str) -> Dict[str, str]:
        """
        Save generated narrations to files
        
        Args:
            title: Title of the story
            narrations: Dictionary containing all narrations
            narration_style: Style of narration used
            voice_tone: Tone of voice used
            
        Returns:
            Dictionary with file paths of saved narrations
        """
        try:
            safe_title = self.sanitize_filename(title)
            narration_story_dir = os.path.join(self.narration_dir, safe_title)
            
            if not os.path.exists(narration_story_dir):
                os.makedirs(narration_story_dir)
                logger.info(f"Created narration directory: {narration_story_dir}")
            
            file_paths = {}
            
            # Save individual scene narrations
            for scene_key, scene_data in narrations.items():
                scene_num = scene_data['scene_number']
                narration_text = scene_data['narration']
                scene_prompt = scene_data['scene_prompt']
                
                scene_file = os.path.join(narration_story_dir, f"scene_{scene_num}_narration.txt")
                with open(scene_file, 'w', encoding='utf-8') as f:
                    f.write(f"# Scene {scene_num} Narration - {title}\n\n")
                    f.write(f"**Style:** {narration_style}\n")
                    f.write(f"**Tone:** {voice_tone}\n\n")
                    f.write("## Narration Text\n")
                    f.write(narration_text)
                    f.write("\n\n" + "="*50 + "\n\n")
                    f.write("## Original Scene Prompt\n")
                    f.write(scene_prompt)
                
                file_paths[scene_key] = scene_file
            
            # Save complete narration file
            complete_file = os.path.join(narration_story_dir, f"{safe_title}_complete_narration.txt")
            with open(complete_file, 'w', encoding='utf-8') as f:
                f.write(f"# Complete Narration - {title}\n\n")
                f.write(f"**Style:** {narration_style}\n")
                f.write(f"**Tone:** {voice_tone}\n")
                f.write(f"**Total Scenes:** {len(narrations)}\n\n")
                f.write("="*80 + "\n\n")
                
                for scene_key, scene_data in narrations.items():
                    scene_num = scene_data['scene_number']
                    narration_text = scene_data['narration']
                    f.write(f"## Scene {scene_num}\n\n")
                    f.write(narration_text)
                    f.write("\n\n" + "-"*50 + "\n\n")
            
            file_paths['complete'] = complete_file
            
            # Save narrations as JSON for programmatic access
            json_file = os.path.join(narration_story_dir, f"{safe_title}_narrations.json")
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(narrations, f, ensure_ascii=False, indent=2)
            file_paths['json'] = json_file
            
            logger.info(f"Saved narrations to: {narration_story_dir}")
            return file_paths
            
        except Exception as e:
            logger.error(f"Failed to save narrations: {str(e)}")
            return {}

    def generate_enhanced_narration(self, title: str, scene_number: int, 
                                  additional_context: str = "", 
                                  narration_style: str = "dramatic",
                                  voice_tone: str = "engaging") -> str:
        """
        Generate enhanced narration with additional context
        
        Args:
            title: Title of the story
            scene_number: Number of the scene
            additional_context: Additional context to include
            narration_style: Style of narration
            voice_tone: Tone of voice
            
        Returns:
            Enhanced narration text
        """
        logger.info(f"Generating enhanced narration for scene {scene_number} of '{title}'")
        
        # Load story content
        story_content = self.load_story_content(title)
        if not story_content:
            return "Error: Could not load story content"
        
        # Parse scene prompts
        scene_prompts = self._parse_scene_prompts(story_content.get('scene_prompts', ''))
        
        if scene_number > len(scene_prompts) or scene_number < 1:
            return f"Error: Scene {scene_number} not found"
        
        scene_prompt = scene_prompts[scene_number - 1]
        
        # Add additional context to the prompt
        enhanced_prompt = f"{scene_prompt}\n\nAdditional Context: {additional_context}"
        
        # Generate enhanced narration
        narration = self.generate_scene_narration(
            title, enhanced_prompt, scene_number, narration_style, voice_tone
        )
        
        return narration

# Configure logging
logger = logging.getLogger("WikiComicGenerator")
