import re
import os
import json
import logging
from typing import List, Dict, Any
from groq import Groq

# Configure logging
logger = logging.getLogger("WikiComicGenerator")


class StoryGenerator:
    def __init__(self, api_key: str, text_dir: str = "data/text"):
        """
        Initialize the Groq story generator
        
        Args:
            api_key: Groq API key
            text_dir: Directory to store generated text content
        """
        self.client = Groq(api_key=api_key)
        self.text_dir = text_dir
        self.create_text_directory()
        logger.info("StoryGenerator initialized with Groq client")

    def create_text_directory(self) -> None:
        """Create text directory for storing story content"""
        try:
            if not os.path.exists(self.text_dir):
                os.makedirs(self.text_dir)
                logger.info(f"Created text directory: {self.text_dir}")
        except Exception as e:
            logger.error(f"Failed to create text directory: {str(e)}")
            raise RuntimeError(f"Failed to create text directory: {str(e)}")

    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a string to be used as a filename
        
        Args:
            filename: Original filename string
            
        Returns:
            Sanitized filename safe for all operating systems
        """
        # Replace invalid characters with underscores
        sanitized = re.sub(r'[\\/*?:"<>|]', '_', filename)
        # Limit filename length
        return sanitized[:200]

    def generate_comic_storyline(self, title: str, content: str, target_length: str = "medium", max_chars: int = 25000) -> str:
        """
        Generate a comic storyline from Wikipedia content
        
        Args:
            title: Title of the Wikipedia article
            content: Content of the Wikipedia article
            target_length: Desired length of the story (short, medium, long)
            
        Returns:
            Generated comic storyline
        """
        logger.info(f"Generating comic storyline for: {title} with target length: {target_length}")
        
        # Map target length to approximate word count
        length_map = {
            "short": 500,
            "medium": 1000,
            "long": 2000
        }
        
        word_count = length_map.get(target_length, 1000)
        
        # Check content length and truncate if necessary to avoid token limits
        # Groq's llama-3.3-70b-versatile has a 12,000 TPM limit on free tier
        # We need to keep the request under ~8,000 tokens (including prompt)
        # Default 25K chars (~6,250 tokens) is safe for most Wikipedia articles
        # This leaves room for the prompt and output
        
        if len(content) > max_chars:
            logger.info(f"Content too long ({len(content)} chars), truncating to {max_chars} chars")
            logger.warning(f"Reducing content to fit within Groq's token limits (12,000 TPM)")
            
            # Smart truncation - try to cut at paragraph boundary
            truncated = content[:max_chars]
            last_paragraph = truncated.rfind('\n\n')
            if last_paragraph > max_chars * 0.8:  # If we find a paragraph break in last 20%
                content = content[:last_paragraph] + "\n\n[Content truncated to fit token limits]"
            else:
                content = truncated + "...[Content truncated to fit token limits]"
            
            logger.info(f"Truncated content to {len(content)} chars (~{len(content)//4} tokens)")
        
        # Create comprehensive prompt for the LLM with enhanced detail and flow
        prompt = f"""
        You are creating a detailed, engaging comic book storyline for "{title}" strictly from the provided Wikipedia content. This storyline will be read by STUDENTS, so use SIMPLE, CLEAR language that everyone can understand. Make it exciting and easy to follow!
        
        HARD REQUIREMENTS:
        - Target length: ~{word_count} words (±100 words) - prioritize completeness over strict word count
        - 5 acts with clear narrative progression and smooth transitions
        - Chronologically accurate with clear timeline markers
        - Historically/factually accurate; no invented facts or fabricated details
        - Use ONLY details present in the provided source content
        - If any detail is uncertain or missing in the source, omit it rather than inventing
        - Cover the COMPLETE story arc from beginning to end with no gaps
        - USE SIMPLE WORDS - avoid complex vocabulary, write like you're explaining to a friend
        - BE ENGAGING - make it exciting, use active voice, keep students interested
        
        FORMAT (FOLLOW EXACTLY):
        # {title}: Comprehensive Comic Storyline
        
        ## Story Overview
        [3-4 sentences providing a compelling summary of the complete narrative arc, including the beginning, major turning points, climax, and resolution. Make it engaging and informative.]
        
        ## Historical/Contextual Background
        [2-3 sentences establishing the time period, setting, and broader context. Help readers understand the world this story takes place in and why it matters.]
        
        ## Main Characters & Key Figures
        [4-8 character entries with 2-3 sentences each. Include:
        - Character name and primary role
        - Key personality traits and motivations
        - Their significance to the overall story
        Make characters feel real and three-dimensional.]
        
        ## Act 1: The Beginning - [Specific Descriptive Title]
        [~{word_count // 5} words covering:
        - Initial situation and setting
        - Introduction of main characters
        - The world before the main events
        - Early signs of change or conflict
        - The inciting incident that sets everything in motion
        Include specific details, dates, locations, and circumstances.]
        
        ## Act 2: Rising Action - [Specific Descriptive Title]
        [~{word_count // 5} words covering:
        - How characters respond to the initial challenge
        - Escalating tensions and growing stakes
        - Early victories or setbacks
        - Character development and relationship dynamics
        - New complications that raise the stakes
        Show clear progression and build momentum.]
        
        ## Act 3: Turning Point - [Specific Descriptive Title]
        [~{word_count // 5} words covering:
        - The critical moment where everything changes
        - Major conflicts reaching their peak
        - Difficult choices and their consequences
        - Shifts in power, understanding, or circumstances
        - The point of no return
        This is the heart of the story - make it powerful.]
        
        ## Act 4: Climax & Resolution - [Specific Descriptive Title]
        [~{word_count // 5} words covering:
        - The final confrontation or ultimate challenge
        - How conflicts are resolved
        - Victories, defeats, sacrifices, or transformations
        - The immediate aftermath of major events
        - Direct consequences of the climax
        Show the emotional and factual resolution.]
        
        ## Act 5: Lasting Impact & Legacy - [Specific Descriptive Title]
        [~{word_count // 5} words covering:
        - Long-term effects and changes
        - How the world/society was transformed
        - The ultimate legacy of events and characters
        - Final reflections on significance
        - Connection to broader history or future events
        Give proper closure while highlighting enduring importance.]
        
        ## Key Themes & Messages
        [3-5 bullet points identifying the major themes, lessons, or important ideas that run through this story. What should audiences take away?]
        
        ## Critical Moments for Visualization
        [8-10 bullet points describing the most visually powerful, emotionally significant, or narratively crucial moments that would make excellent comic scenes. Include:
        - Specific event description
        - Why this moment matters
        - Visual/emotional impact potential
        These will guide scene selection.]
        
        ## Timeline & Chronology
        [Create a clear chronological sequence of 8-12 major events with approximate dates/time periods where available. This ensures the story flows in proper order.]
        
        WRITING GUIDELINES FOR STUDENTS:
        - Write in SIMPLE, CLEAR language that students can easily understand
        - Avoid complex words - use everyday language (e.g., "brave" not "valorous", "happy" not "jubilant")
        - Use SHORT sentences that are easy to follow
        - Make it EXCITING - use active voice and vivid descriptions
        - Use specific names, dates, locations, and facts from the source
        - Build clear cause-and-effect relationships between events
        - Show character growth and change over time
        - Create emotional connection while maintaining accuracy
        - Ensure smooth transitions between acts with connecting phrases
        - Make the chronology crystal clear - use time markers like "First...", "Then...", "After that..."
        - Leave no important story elements uncovered
        - Balance engaging storytelling with factual accuracy
        - Think: "Would a 12-year-old understand this?" If not, simplify it!
        
        SOURCE MATERIAL (your only source - use all relevant details):
        {content}
        
        Create a storyline that is comprehensive, engaging, and provides everything needed for detailed scene generation and narration. Cover the entire story from beginning to end with depth and detail.
        """
        
        try:
            # Generate storyline using Groq with Llama 3.3 70B Versatile
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an expert storyteller who creates engaging, easy-to-understand comic book storylines for STUDENTS. You write in SIMPLE, CLEAR language that anyone can understand - avoiding complex vocabulary and using everyday words. You make history and facts exciting by telling stories in an engaging, active way. Your storylines are accurate but written like you're telling an exciting story to a friend, not writing a textbook. You use short sentences, simple words, and always think: 'Would a student understand this?'"},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.4,
                max_tokens=12000,  # Increased for comprehensive storylines
                top_p=0.9
            )
            
            storyline = response.choices[0].message.content
            logger.info(f"Successfully generated comic storyline for: {title}")
            
            return storyline
            
        except Exception as e:
            logger.error(f"Failed to generate storyline: {str(e)}")
            return f"Error generating storyline: {str(e)}"

    def generate_scene_prompts(self, title: str, storyline: str, comic_style: str, num_scenes: int = 10, 
                              age_group: str = "general", education_level: str = "standard",
                              negative_concepts: List[str] = None, character_sheet: str = "", style_sheet: str = "") -> List[str]:
        """
        Generate detailed scene prompts for comic panels based on the storyline
        
        Args:
            title: Title of the article
            storyline: Generated comic storyline
            comic_style: Selected comic art style
            num_scenes: Number of scene prompts to generate (default 10)
            age_group: Target age group (kids, teens, general, adult)
            education_level: Education level for content complexity (basic, standard, advanced)
            
        Returns:
            List of scene prompts for image generation
        """
        logger.info(f"Generating {num_scenes} scene prompts for comic in {comic_style} style, targeting {age_group} with {education_level} education level")
        
        # Prepare style-specific guidance based on comic style
        style_guidance = {
            "manga": "Use manga-specific visual elements like speed lines, expressive emotions, and distinctive panel layouts. Character eyes should be larger, with detailed hair and simplified facial features. Use black and white with screen tones for shading.",
            "superhero": "Use bold colors, dynamic poses with exaggerated anatomy, dramatic lighting, and action-oriented compositions. Include detailed musculature and costumes with strong outlines and saturated colors.",
            "cartoon": "Use simplified, exaggerated character features with bold outlines. Employ bright colors, expressive faces, and playful physics. Include visual effects like motion lines and impact stars.",
            "noir": "Use high-contrast black and white or muted colors with dramatic shadows. Feature low-key lighting, rain effects, and urban settings. Characters should have realistic proportions with hardboiled expressions.",
            "european": "Use detailed backgrounds with architectural precision and clear line work. Character designs should be semi-realistic with consistent proportions. Panel layouts should be regular and methodical.",
            "indie": "Use unconventional art styles with personal flair. Panel layouts can be experimental and fluid. Line work may be sketchy or deliberately unpolished. Colors can be watercolor-like or limited palette.",
            "retro": "Use halftone dots for shading, slightly faded colors, and classic panel compositions. Character designs should reflect the comics of the 50s-70s with simplified but distinctive features.",
        }.get(comic_style.lower(), f"Incorporate distinctive visual elements of {comic_style} style consistently in all panels.")
        
        # Prepare age-appropriate guidance
        age_guidance = {
            "kids": "Use simple, clear vocabulary and straightforward concepts. Avoid complex themes, frightening imagery, or adult situations. Characters should be expressive and appealing. Educational content should be presented in an engaging, accessible way.",
            "teens": "Use relatable language and themes important to adolescents. Include more nuanced emotional content and moderate complexity. Educational aspects can challenge readers while remaining accessible.",
            "general": "Balance accessibility with depth. Include some complexity in both themes and visuals while remaining broadly appropriate. Educational content should be informative without being overly technical.",
            "adult": "Include sophisticated themes, complex characterizations, and nuanced storytelling. Educational content can be presented with full complexity and technical detail where appropriate."
        }.get(age_group.lower(), "Create content appropriate for a general audience with balanced accessibility and depth.")
        
        # Prepare education level guidance
        education_guidance = {
            "basic": "Use simple vocabulary, clear explanations, and focus on foundational concepts. Break down complex ideas into easily digestible components with examples.",
            "standard": "Use moderate vocabulary and present concepts with appropriate depth for general understanding. Balance educational content with narrative engagement.",
            "advanced": "Use field-specific terminology where appropriate and explore concepts in depth. Present nuanced details and sophisticated analysis of the subject matter."
        }.get(education_level.lower(), "Present educational content with balanced complexity suitable for interested general readers.")
        
        # Create comprehensive prompt for scene generation with enhanced chronological flow
        negatives_text = ""
        if negative_concepts:
            negatives_text = "\nGLOBAL BANS (strictly avoid): " + ", ".join(negative_concepts)
        sheets_text = ""
        if style_sheet:
            sheets_text += f"\nSTYLE SHEET (follow consistently): {style_sheet}"
        if character_sheet:
            sheets_text += f"\nCHARACTER SHEET (identities, outfits, colors): {character_sheet}"
        prompt = f"""
        Based on the storyline for "{title}", create EXACTLY {num_scenes} exciting scene descriptions for comic panels. Tell the story in order, making each scene flow naturally into the next. Make it ENGAGING and VISUAL!

        CORE REQUIREMENTS FOR EVERY SCENE:
        1. Tell the story in ORDER - each scene follows the previous one naturally
        2. Visual description ONLY (NO text, captions, speech bubbles, or words on images)
        3. Use 80-120 SIMPLE, CLEAR words describing: what we see, who is there, what they're doing, how they look, the mood
        4. Keep characters and places looking the same across all scenes
        5. Follow the {comic_style} comic style
        6. Only use facts from the storyline - don't make up new things
        7. Absolutely NO text, letters, logos, watermarks, or words in images
        8. Each scene must move the story forward and connect to the next scene
        9. Use SIMPLE words students can understand - avoid complex vocabulary

        SCENE DISTRIBUTION STRATEGY:
        - Scenes 1-2: Opening/Setup (introduce setting, main characters, initial situation)
        - Scenes 3-4: Early Development (first challenges, rising action begins)
        - Scenes 5-6: Mid-Story Turning Points (escalating conflict, crucial developments)
        - Scenes 7-8: Climax & Resolution (peak drama, major events, decisive moments)
        - Scenes 9-{num_scenes}: Aftermath & Legacy (resolution, lasting impact, conclusion)
        
        Ensure complete story coverage from first moment to final impact.

        HOW TO MAKE SCENES ENGAGING:
        - Make each scene unique and exciting - something students will remember
        - Use camera angles to show emotion: close-ups for feelings, wide shots to show the big picture
        - Show what characters are feeling through their faces and body language
        - Include details that show where and when this is happening
        - Make sure scenes connect smoothly - if someone is running in one scene, show where they're going in the next
        - Focus on the most exciting or important moments
        - Use light and shadows to create mood (bright for happy, dark for scary/serious)

        STYLE PARAMETERS:
        - Comic Style: {comic_style} — {style_guidance}
        - Age Group: {age_group} — {age_guidance}
        - Education Level: {education_level} — {education_guidance}
        {negatives_text}
        {sheets_text}

        COMPLETE STORYLINE (your authoritative source for all scene content):
        {storyline}

        OUTPUT FORMAT (FOLLOW EXACTLY):
        Scene [number]: [Specific, descriptive scene title that indicates chronological position]
        Narrative Context: [1-2 sentences explaining where this fits in the story flow and what narrative purpose it serves]
        Visual Description: [80-120 words of detailed, visual-only description including:
        - Setting and environment details
        - Character positioning, actions, and expressions
        - Camera angle and composition choices
        - Lighting, atmosphere, and mood
        - Key visual elements that convey the story moment
        - Color palette suggestions if appropriate
        - Emotional tone through visual elements]
        Style Notes: {comic_style} with [specific stylistic elements to emphasize for this particular scene]
        Continuity: [Brief note on how this connects to previous/next scene]

        CRITICAL GUIDELINES:
        - Cover the ENTIRE story arc across all {num_scenes} scenes with no gaps
        - Maintain perfect chronological sequence - never jump backward in time without reason
        - Ensure smooth visual transitions between consecutive scenes
        - Balance establishing shots, action scenes, and emotional moments
        - Make key story moments visually powerful and clear
        - Every scene must feel essential to telling the complete story
        - Create strong visual variety while maintaining consistency

        Produce EXACTLY {num_scenes} scenes that tell the complete story of "{title}" from beginning to end with perfect narrative flow and visual storytelling excellence.
        """
        
        try:
            # Generate scene prompts using Groq with Llama 3.3 70B Versatile
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an expert comic artist who creates exciting, easy-to-understand scene descriptions for STUDENTS. You use SIMPLE, CLEAR words that anyone can understand. You describe what people see in each panel using everyday language, making sure the story is exciting and easy to follow. You never use complex vocabulary - you explain things like you're talking to a friend. Your scenes flow naturally from one to the next, and you always make sure NO text appears in the images."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.4,
                max_tokens=12000,  # Increased for detailed scene prompts
                top_p=0.9
            )
            
            scenes_text = response.choices[0].message.content
            
            # Process the text to extract individual scene prompts
            scene_prompts = []
            scene_pattern = re.compile(r'Scene \d+:.*?(?=Scene \d+:|$)', re.DOTALL)
            matches = scene_pattern.findall(scenes_text)
            
            for match in matches:
                # Remove any dialog lines to ensure no text renders
                cleaned = re.sub(r'^\s*Dialog\s*:\s*.*$', '', match, flags=re.IGNORECASE | re.MULTILINE)
                # Also remove narrator/caption/voiceover style lines
                cleaned = re.sub(r'^\s*(Narrator|Caption|Voiceover|Voice-over|Announcer)\s*:\s*.*$', '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
                scene_prompts.append(cleaned.strip())
            
            # If we didn't get enough scenes, pad with generic ones WITHOUT any text
            while len(scene_prompts) < num_scenes:
                scene_num = len(scene_prompts) + 1
                scene_prompts.append(f"""Scene {scene_num}: Additional scene from {title}
                Visual: A character from the story stands in a relevant setting from {title}, looking thoughtful. No on-screen text, no captions, no speech.
                Style: {comic_style} style with appropriate elements for {age_group} audience.""")
            
            # If we got too many scenes, truncate
            scene_prompts = scene_prompts[:num_scenes]
            
            # Validate each scene prompt to ensure it contains NO dialog/text
            validated_prompts = []
            for i, prompt in enumerate(scene_prompts):
                scene_num = i + 1
                
                # Strip any remaining dialog-like lines if present (ensure no text artifacts)
                prompt = re.sub(r'^\s*Dialog\s*:\s*.*$', '', prompt, flags=re.IGNORECASE | re.MULTILINE)
                prompt = re.sub(r'^\s*(Narrator|Caption|Voiceover|Voice-over|Announcer)\s*:\s*.*$', '', prompt, flags=re.IGNORECASE | re.MULTILINE)
                # Also remove any quoted lines that might be interpreted as dialog
                prompt = re.sub(r'^\s*"[^"]+"\s*$', '', prompt, flags=re.MULTILINE)
                
                validated_prompts.append(prompt)
            
            logger.info(f"Successfully generated {len(validated_prompts)} scene prompts")
            return validated_prompts
            
        except Exception as e:
            logger.error(f"Failed to generate scene prompts: {str(e)}")
            return [f"Error generating scene prompt: {str(e)}"]

    def save_story_content(self, title: str, storyline: str, scene_prompts: List[str], page_info: Dict[str, Any] = None) -> Dict[str, str]:
        """
        Save story content to text files for further processing
        
        Args:
            title: Title of the story
            storyline: Generated storyline
            scene_prompts: List of scene prompts
            page_info: Wikipedia page information (optional)
            
        Returns:
            Dictionary with file paths of saved content
        """
        try:
            # Sanitize title for filename
            safe_title = self.sanitize_filename(title)
            
            # Create story directory
            story_dir = os.path.join(self.text_dir, safe_title)
            if not os.path.exists(story_dir):
                os.makedirs(story_dir)
                logger.info(f"Created story directory: {story_dir}")
            
            file_paths = {}
            
            # Save storyline
            storyline_path = os.path.join(story_dir, f"{safe_title}_storyline.txt")
            with open(storyline_path, 'w', encoding='utf-8') as f:
                f.write(f"# {title} - Comic Storyline\n\n")
                f.write(storyline)
            file_paths['storyline'] = storyline_path
            logger.info(f"Saved storyline to: {storyline_path}")
            
            # Save scene prompts
            scenes_path = os.path.join(story_dir, f"{safe_title}_scene_prompts.txt")
            with open(scenes_path, 'w', encoding='utf-8') as f:
                f.write(f"# {title} - Scene Prompts\n\n")
                for i, prompt in enumerate(scene_prompts, 1):
                    f.write(f"## Scene {i}\n")
                    f.write(prompt)
                    f.write("\n\n" + "="*50 + "\n\n")
            file_paths['scenes'] = scenes_path
            logger.info(f"Saved scene prompts to: {scenes_path}")
            
            # Save page info as JSON for reference
            if page_info:
                page_info_path = os.path.join(story_dir, f"{safe_title}_page_info.json")
                with open(page_info_path, 'w', encoding='utf-8') as f:
                    json.dump(page_info, f, ensure_ascii=False, indent=2)
                file_paths['page_info'] = page_info_path
                logger.info(f"Saved page info to: {page_info_path}")
            
            # Create combined content file
            combined_path = os.path.join(story_dir, f"{safe_title}_combined.txt")
            with open(combined_path, 'w', encoding='utf-8') as f:
                f.write(f"# {title} - Complete Story Content\n\n")
                f.write("## Storyline\n")
                f.write(storyline)
                f.write("\n\n" + "="*80 + "\n\n")
                f.write("## Scene Prompts\n\n")
                for i, prompt in enumerate(scene_prompts, 1):
                    f.write(f"### Scene {i}\n")
                    f.write(prompt)
                    f.write("\n\n" + "-"*50 + "\n\n")
            file_paths['combined'] = combined_path
            logger.info(f"Saved combined content to: {combined_path}")
            
            return file_paths
            
        except Exception as e:
            logger.error(f"Failed to save story content: {str(e)}")
            return {}

    def generate_and_save_story(self, title: str, content: str, target_length: str = "medium",
                               comic_style: str = "western comic", num_scenes: int = 10,
                               age_group: str = "general", education_level: str = "standard",
                               page_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate complete story and save all content to text files
        
        Args:
            title: Title of the story
            content: Wikipedia content
            target_length: Desired length of the story
            comic_style: Selected comic art style
            num_scenes: Number of scenes to generate
            age_group: Target age group
            education_level: Education level for content complexity
            page_info: Wikipedia page information (optional)
            
        Returns:
            Dictionary containing generated content and file paths
        """
        logger.info(f"Generating complete story for '{title}'")
        
        # Generate storyline
        storyline = self.generate_comic_storyline(title, content, target_length)
        
        # Generate scene prompts
        scene_prompts = self.generate_scene_prompts(
            title, storyline, comic_style, num_scenes, age_group, education_level
        )
        
        # Save all content to text files
        file_paths = self.save_story_content(title, storyline, scene_prompts, page_info)
        
        return {
            "title": title,
            "storyline": storyline,
            "scene_prompts": scene_prompts,
            "file_paths": file_paths
        }
