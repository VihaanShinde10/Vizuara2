import os
import logging
from typing import Dict, Any, List, Optional
from gtts import gTTS

# Configure logging
logger = logging.getLogger("WikiComicGenerator")

# Try to import pydub for audio speed adjustment
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    logger.warning("pydub not installed. Audio speed adjustment will not be available.")
    logger.warning("Install with: pip install pydub")
    PYDUB_AVAILABLE = False


def ensure_directory(path: str) -> None:
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)


def adjust_audio_speed(input_path: str, output_path: str, speed: float = 1.25) -> bool:
    """
    Adjust the playback speed of an audio file
    
    Args:
        input_path: Path to input audio file
        output_path: Path to save speed-adjusted audio
        speed: Speed multiplier (1.25 = 25% faster, 0.8 = 20% slower)
        
    Returns:
        Boolean indicating success
    """
    if not PYDUB_AVAILABLE:
        logger.error("pydub not available. Cannot adjust audio speed.")
        logger.error("Install with: pip install pydub")
        # Copy the file as-is if pydub not available
        try:
            import shutil
            shutil.copy2(input_path, output_path)
            logger.warning(f"Copied audio without speed adjustment (pydub not installed)")
            return True
        except Exception as copy_error:
            logger.error(f"Failed to copy audio file: {str(copy_error)}")
            return False
    
    try:
        # Load audio file
        audio = AudioSegment.from_mp3(input_path)
        
        # Calculate new frame rate for speed adjustment
        # Increasing frame rate speeds up playback
        new_frame_rate = int(audio.frame_rate * speed)
        
        # Change frame rate (speeds up audio)
        adjusted_audio = audio._spawn(audio.raw_data, overrides={
            "frame_rate": new_frame_rate
        })
        
        # Convert back to standard frame rate for compatibility
        adjusted_audio = adjusted_audio.set_frame_rate(audio.frame_rate)
        
        # Export adjusted audio
        adjusted_audio.export(output_path, format="mp3", bitrate="192k")
        
        logger.info(f"✓ Adjusted audio speed to {speed}x")
        return True
        
    except Exception as e:
        logger.error(f"Error adjusting audio speed: {str(e)}")
        # Try to use original file if speed adjustment fails
        try:
            import shutil
            shutil.copy2(input_path, output_path)
            logger.warning(f"Using original audio without speed adjustment due to error")
            return True
        except:
            return False


def synthesize_to_mp3(text: str, output_path: str, lang: str = "en", tld: str = "com", 
                     slow: bool = False, speed: float = 1.0) -> None:
    """
    Synthesize the given text to an MP3 file using Google Text-to-Speech (gTTS).
    
    Args:
        text: Text to convert to speech
        output_path: Path where MP3 file will be saved
        lang: Language code (e.g., 'en' for English, 'hi' for Hindi, 'es' for Spanish)
        tld: Top-level domain for accent ('com' for US, 'co.uk' for UK, 'co.in' for India, etc.)
        slow: Whether to use slower speech rate (overridden by speed parameter)
        speed: Speed multiplier (1.0 = normal, 1.25 = 25% faster, default: 1.0)
    """
    ensure_directory(os.path.dirname(output_path))
    
    try:
        # Generate base TTS audio
        tts = gTTS(text=text, lang=lang, tld=tld, slow=slow)
        
        # If speed adjustment is needed and available, generate to temp file first
        if speed != 1.0 and abs(speed - 1.0) > 0.01:
            temp_path = output_path.replace('.mp3', '_temp.mp3')
            tts.save(temp_path)
            logger.info(f"Generated TTS audio (will adjust speed to {speed}x)")
            
            # Adjust speed
            success = adjust_audio_speed(temp_path, output_path, speed)
            
            # Clean up temp file
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except:
                pass
            
            if not success:
                raise Exception("Failed to adjust audio speed")
        else:
            # No speed adjustment needed
            tts.save(output_path)
            logger.info("Generated TTS audio (no speed adjustment)")
            
    except Exception as e:
        logger.error(f"Error generating TTS: {str(e)}")
        raise


def estimate_tts_duration_seconds(text: str, speed: float = 1.0) -> float:
    """
    Rough estimate for English: ~2.5 words/sec at normal speed.
    
    Args:
        text: Text to estimate duration for
        speed: Speed multiplier (1.25 = 25% faster)
        
    Returns:
        Estimated duration in seconds
    """
    words = [w for w in text.strip().split() if w]
    base_duration = len(words) / 2.5
    # Adjust for speed
    adjusted_duration = base_duration / speed if speed > 0 else base_duration
    return max(0.0, adjusted_duration)


def generate_scene_audios(narrations: Dict[str, Any], title: str, base_dir: str = "data/narration", 
                         lang: str = "en", tld: str = "com", slow: bool = False, speed: float = 1.25) -> Dict[str, str]:
    """
    Generate MP3 files per scene from a narrations dict produced by NarrationGenerator.
    
    Args:
        narrations: Dictionary containing narration data for each scene
        title: Title of the story
        base_dir: Base directory for storing audio files
        lang: Language code (e.g., 'en', 'hi', 'es', 'fr')
        tld: Top-level domain for accent ('com'=US, 'co.uk'=UK, 'co.in'=India, 'com.au'=Australia)
        slow: Whether to use slower speech rate (overridden by speed parameter)
        speed: Speed multiplier (1.0 = normal, 1.25 = 25% faster, default: 1.25)

    Returns a mapping of scene keys to generated MP3 paths.
    """
    safe_title = title.replace('/', '_')
    out_dir = os.path.join(base_dir, safe_title, "audio")
    ensure_directory(out_dir)

    scene_to_path: Dict[str, str] = {}
    narrs = narrations.get("narrations", {})
    
    logger.info(f"Generating audio for {len(narrs)} scenes at {speed}x speed")
    
    for scene_key, scene_data in narrs.items():
        scene_num = scene_data.get("scene_number")
        text = scene_data.get("narration", "").strip()
        if not text:
            logger.warning(f"No narration text for scene {scene_num}")
            continue
            
        mp3_path = os.path.join(out_dir, f"scene_{scene_num}.mp3")
        try:
            synthesize_to_mp3(text, mp3_path, lang=lang, tld=tld, slow=slow, speed=speed)
            scene_to_path[scene_key] = mp3_path
            
            # Estimate duration
            duration = estimate_tts_duration_seconds(text, speed)
            logger.info(f"✓ Generated audio for scene {scene_num} (~{duration:.1f}s at {speed}x speed)")
            
        except Exception as e:
            logger.error(f"✗ Error generating audio for scene {scene_num}: {str(e)}")
            continue

    logger.info(f"Successfully generated {len(scene_to_path)}/{len(narrs)} audio files")
    return scene_to_path


