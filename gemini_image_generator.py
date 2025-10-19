import os
import re
import time
import logging
from typing import List, Optional
from google import genai
from PIL import Image
from io import BytesIO

# Configure logging
logger = logging.getLogger("WikiComicGenerator")


class GeminiImageGenerator:
    """Comic image generator using Google Gemini 2.5 Flash Image model"""

    def __init__(self, api_key: str):
        """Initialize the Gemini Image Generator"""
        self.api_key = api_key
        self.client = None
        logger.info("GeminiImageGenerator initializing...")
        self._initialize_client()

    def _initialize_client(self) -> bool:
        """Initialize the Gemini client and test API key validity"""
        try:
            if not self.api_key:
                logger.error("No Gemini API key provided")
                return False

            self.client = genai.Client(api_key=self.api_key)
            logger.info("Gemini client initialized successfully")

            try:
                _ = self.client.models.generate_content(
                    model="gemini-2.5-flash-image",
                    contents="test"
                )
                logger.info("✓ Gemini API key validated successfully")
                return True
            except Exception as test_error:
                logger.warning(f"API key test failed: {test_error}")
                logger.warning("Proceeding anyway (model may still work)")
                return True

        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            logger.error("Please check your GEMINI_API_KEY in the .env file")
            return False

    def _clean_scene_prompt(self, scene_prompt: str) -> str:
        """Extract only visual description from the scene prompt"""
        cleaned = re.sub(
            r"^\s*(Narrator|Caption|Voiceover|Voice-over|Announcer)\s*:\s*.*$",
            "",
            scene_prompt,
            flags=re.IGNORECASE | re.MULTILINE,
        )
        cleaned = re.sub(r"^\s*Dialog\s*:\s*.*$", "", cleaned, flags=re.IGNORECASE | re.MULTILINE)

        visual_match = re.search(
            r'Visual[:\s]+(.+?)(?=\n(?:Dialog|Style|Narrative|Continuity):|$)',
            cleaned,
            re.DOTALL | re.IGNORECASE
        )
        visual_description = (
            visual_match.group(1).strip() if visual_match else cleaned.strip()
        )

        style_match = re.search(
            r'Style[:\s]+(.+?)(?=\n|$)',
            scene_prompt,
            re.DOTALL | re.IGNORECASE
        )
        style_info = style_match.group(1).strip() if style_match else ""

        visual_description = re.sub(
            r'^(Scene \d+:|Visual:|Description:)',
            '',
            visual_description,
            flags=re.IGNORECASE
        ).strip()

        return visual_description, style_info

    def _enhance_prompt_for_gemini(
        self,
        scene_prompt: str,
        style_sheet: str = "",
        character_sheet: str = "",
        negative_concepts: Optional[List[str]] = None,
        aspect_ratio: str = "16:9"
    ) -> str:
        """Enhance the prompt for Gemini model"""
        visual_description, style_info = self._clean_scene_prompt(scene_prompt)

        parts = [
            f"Create a single comic book panel with this exact visual content:\n{visual_description}"
        ]

        if style_info:
            parts.append(f"\nArt style: {style_info}")
        if style_sheet:
            parts.append(f"\nStyle consistency requirements: {style_sheet}")
        if character_sheet:
            parts.append(f"\nCharacter appearance consistency: {character_sheet}")

        parts.append(f"""
Technical requirements:
- Aspect ratio: {aspect_ratio} (landscape)
- High quality comic book art
- Cinematic lighting, balanced framing
- Vibrant but not oversaturated colors
- NO text, captions, or speech bubbles
- NO watermarks, logos, or UI elements
- Character consistency across panels
        """)

        if negative_concepts:
            parts.append(f"\nAvoid: {', '.join(negative_concepts)}")

        parts.append("""
Quality standards:
- Professional comic book art
- Clear expressions and clean background
- Consistent art style
- Absolutely NO text or writing
        """)

        return "\n".join(parts)

    def generate_comic_image(
        self,
        scene_prompt: str,
        output_path: str,
        scene_num: int,
        attempt: int = 1,
        max_retries: int = 3,
        style_sheet: str = "",
        character_sheet: str = "",
        negative_concepts: Optional[List[str]] = None,
        aspect_ratio: str = "16:9"
    ) -> bool:
        """Generate a single comic panel"""
        if not self.client:
            logger.error(f"Gemini client not initialized for scene {scene_num}")
            return self._create_placeholder_image(output_path, scene_num, "Client not initialized")

        try:
            prompt = self._enhance_prompt_for_gemini(
                scene_prompt,
                style_sheet, character_sheet,
                negative_concepts, aspect_ratio
            )

            logger.info(f"🎨 Generating image for scene {scene_num} (Attempt {attempt})")
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=prompt
            )

            image_found = False
            for candidate in getattr(response, "candidates", []):
                content = getattr(candidate, "content", None)
                if not content:
                    continue
                for part in getattr(content, "parts", []):
                    inline_data = getattr(part, "inline_data", None)
                    if inline_data and inline_data.mime_type.startswith("image/"):
                        try:
                            save_path = os.path.splitext(output_path)[0] + ".jpg"
                            os.makedirs(os.path.dirname(save_path), exist_ok=True)

                            img_data = BytesIO(inline_data.data)
                            image = Image.open(img_data)

                            if image.mode in ("RGBA", "LA", "P"):
                                rgb = Image.new("RGB", image.size, (255, 255, 255))
                                if image.mode == "P":
                                    image = image.convert("RGBA")
                                rgb.paste(image, mask=image.split()[-1] if image.mode in ("RGBA", "LA") else None)
                                image = rgb

                            image.save(save_path, "JPEG", quality=95)
                            logger.info(f"✅ Saved scene {scene_num}: {save_path}")
                            image_found = True
                            break
                        except Exception as err:
                            logger.error(f"❌ Error saving image scene {scene_num}: {err}")
                if image_found:
                    break

            if not image_found:
                logger.warning(f"⚠️ No image data for scene {scene_num}")
                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time}s (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    return self.generate_comic_image(
                        scene_prompt, output_path, scene_num,
                        attempt + 1, max_retries,
                        style_sheet, character_sheet, negative_concepts, aspect_ratio
                    )
                return self._create_placeholder_image(output_path, scene_num, "No image data received")

            return True

        except Exception as e:
            msg = str(e)
            logger.error(f"❌ Error generating image scene {scene_num}: {msg}")
            if "RESOURCE_EXHAUSTED" in msg or "QUOTA" in msg:
                return self._create_placeholder_image(output_path, scene_num, "Gemini quota exhausted")

            if attempt < max_retries:
                wait_time = 2 ** attempt
                logger.info(f"Retrying in {wait_time}s (Attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                return self.generate_comic_image(
                    scene_prompt, output_path, scene_num,
                    attempt + 1, max_retries,
                    style_sheet, character_sheet, negative_concepts, aspect_ratio
                )

            return self._create_placeholder_image(output_path, scene_num, msg[:100])

    def _create_placeholder_image(self, output_path: str, scene_num: int, error_msg: str) -> bool:
        """Generate placeholder when Gemini fails"""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            img = Image.new("RGB", (1280, 720), color=(240, 240, 245))
            from PIL import ImageDraw, ImageFont

            draw = ImageDraw.Draw(img)
            try:
                font_title = ImageFont.truetype("Arial", 48)
                font_text = ImageFont.truetype("Arial", 24)
            except:
                font_title = font_text = ImageFont.load_default()

            draw.text((500, 250), f"Scene {scene_num}", fill=(50, 50, 80), font=font_title)
            draw.text((400, 350), "Image generation failed", fill=(90, 90, 120), font=font_text)
            draw.text((400, 400), error_msg[:60], fill=(120, 120, 140), font=font_text)

            placeholder_path = os.path.splitext(output_path)[0] + ".jpg"
            img.save(placeholder_path, "JPEG", quality=95)
            logger.info(f"🪧 Placeholder created for scene {scene_num}")
            return True

        except Exception as err:
            logger.error(f"Failed to create placeholder image: {err}")
            return False

    def generate_comic_strip(
        self,
        scene_prompts: List[str],
        output_dir: str,
        comic_title: str,
        style_sheet: str = "",
        character_sheet: str = "",
        negative_concepts: Optional[List[str]] = None,
        aspect_ratio: str = "16:9"
    ) -> List[str]:
        """Generate all comic panels"""
        logger.info(f"🎞️ Generating {len(scene_prompts)} scenes for {comic_title}")
        if not self.client:
            logger.error("Gemini client not initialized.")
            return []

        safe_title = re.sub(r'[\\/*?:"<>|]', '_', comic_title)
        comic_dir = os.path.join(output_dir, safe_title)
        os.makedirs(comic_dir, exist_ok=True)
        logger.info(f"Saving images to {comic_dir}")

        image_paths = []
        for i, prompt in enumerate(scene_prompts):
            scene_num = i + 1
            output_path = os.path.join(comic_dir, f"scene_{scene_num}.jpg")

            logger.info(f"Processing scene {scene_num}/{len(scene_prompts)}")
            success = self.generate_comic_image(
                scene_prompt=prompt,
                output_path=output_path,
                scene_num=scene_num,
                style_sheet=style_sheet,
                character_sheet=character_sheet,
                negative_concepts=negative_concepts,
                aspect_ratio=aspect_ratio
            )

            jpg_path = os.path.splitext(output_path)[0] + ".jpg"
            if os.path.exists(jpg_path):
                image_paths.append(jpg_path)

            if scene_num < len(scene_prompts):
                time.sleep(1)

        logger.info(f"✅ Comic strip done: {len(image_paths)} images generated.")
        return image_paths
