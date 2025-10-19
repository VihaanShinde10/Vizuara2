import os
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from PIL import Image

# -------------------------------------------------
# 🎬 MoviePy setup (supports MoviePy 2.x and 1.x)
# -------------------------------------------------
MOVIEPY_AVAILABLE = False
MOVIEPY_VERSION = 0

try:
    from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip, VideoClip, vfx
    MOVIEPY_AVAILABLE = True
    MOVIEPY_VERSION = 2
    print("🎬 MoviePy 2.x detected and loaded")
except ImportError:
    try:
        import moviepy.editor as mpe
        MOVIEPY_AVAILABLE = True
        MOVIEPY_VERSION = 1
        print("🎬 MoviePy 1.x detected and loaded")
    except ImportError as e:
        print(f"⚠️ MoviePy not available: {e}")
        print("Please install: pip install moviepy")

# Configure imageio-ffmpeg
try:
    import imageio_ffmpeg
    os.environ["IMAGEIO_FFMPEG_EXE"] = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    pass


# -------------------------------------------------
# Utility functions
# -------------------------------------------------
def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _get_audio_duration_seconds(audio_path: str) -> float:
    """Get audio duration using pydub."""
    try:
        from pydub import AudioSegment
        seg = AudioSegment.from_file(audio_path)
        return seg.duration_seconds
    except Exception:
        return 0.0


def _estimate_scene_duration(audio_path: Optional[str], min_seconds: float, head_pad: float, tail_pad: float) -> float:
    """Estimate scene duration based on audio file or minimum fallback."""
    duration = min_seconds
    if audio_path and os.path.exists(audio_path):
        d = _get_audio_duration_seconds(audio_path)
        if d > 0:
            duration = max(min_seconds, d + head_pad + tail_pad)
        else:
            try:
                if MOVIEPY_VERSION == 2:
                    with AudioFileClip(audio_path) as audio:
                        duration = max(min_seconds, audio.duration + head_pad + tail_pad)
                elif MOVIEPY_VERSION == 1:
                    audio = mpe.AudioFileClip(audio_path)
                    duration = max(min_seconds, audio.duration + head_pad + tail_pad)
                    audio.close()
            except Exception:
                duration = max(min_seconds, head_pad + tail_pad)
    return duration


def _apply_ken_burns_v2(clip, duration: float, scene_num: int, kb_zoom_start: float, kb_zoom_end: float, kb_pan: str, resolution: Tuple[int, int]):
    """Apply Ken Burns effect for MoviePy 2.x"""
    w, h = resolution
    
    # Get base frame once for efficiency
    base_frame = clip.get_frame(0)
    base_img = Image.fromarray(base_frame.astype(np.uint8))
    
    def make_frame(t):
        progress = min(1.0, max(0.0, t / duration)) if duration > 0 else 0
        zoom = kb_zoom_start + (kb_zoom_end - kb_zoom_start) * progress
        
        # Calculate pan direction
        pan_strength = 0.06
        dx, dy = 0, 0
        if kb_pan == "left" or (kb_pan == "auto" and scene_num % 4 == 1):
            dx = -pan_strength * progress
        elif kb_pan == "right" or (kb_pan == "auto" and scene_num % 4 == 2):
            dx = pan_strength * progress
        elif kb_pan == "up" or (kb_pan == "auto" and scene_num % 4 == 3):
            dy = -pan_strength * progress
        elif kb_pan == "down" or (kb_pan == "auto" and scene_num % 4 == 0):
            dy = pan_strength * progress
        
        # Zoom image
        zoomed_w = max(w, int(base_img.width * zoom))
        zoomed_h = max(h, int(base_img.height * zoom))
        img_zoomed = base_img.resize((zoomed_w, zoomed_h), Image.LANCZOS)
        zoomed = np.array(img_zoomed, dtype=np.uint8)
        
        # Calculate crop with pan
        center_x = zoomed_w // 2 + int(w * dx)
        center_y = zoomed_h // 2 + int(h * dy)
        
        x1 = max(0, min(center_x - w // 2, zoomed_w - w))
        y1 = max(0, min(center_y - h // 2, zoomed_h - h))
        x2 = min(zoomed_w, x1 + w)
        y2 = min(zoomed_h, y1 + h)
        
        cropped = zoomed[y1:y2, x1:x2]
        
        # Ensure correct output size
        if cropped.shape[0] != h or cropped.shape[1] != w:
            output = np.zeros((h, w, 3), dtype=np.uint8)
            h_crop = min(cropped.shape[0], h)
            w_crop = min(cropped.shape[1], w)
            output[:h_crop, :w_crop] = cropped[:h_crop, :w_crop]
            return output
            
        return cropped
    
    return VideoClip(make_frame, duration=duration)


def _apply_ken_burns_v1(clip, duration: float, scene_num: int, kb_zoom_start: float, kb_zoom_end: float, kb_pan: str, resolution: Tuple[int, int]):
    """Apply Ken Burns effect for MoviePy 1.x"""
    from moviepy.editor import vfx as vfx1
    
    w, h = resolution
    
    def zoom_func(t):
        progress = min(1.0, max(0.0, t / duration)) if duration > 0 else 0
        return kb_zoom_start + (kb_zoom_end - kb_zoom_start) * progress
    
    zclip = clip.fx(vfx1.resize, lambda t: zoom_func(t))
    
    def pos_func(t):
        progress = min(1.0, max(0.0, t / duration)) if duration > 0 else 0
        pan_strength = 0.06
        dx, dy = 0, 0
        
        if kb_pan == "left" or (kb_pan == "auto" and scene_num % 4 == 1):
            dx = -pan_strength * progress
        elif kb_pan == "right" or (kb_pan == "auto" and scene_num % 4 == 2):
            dx = pan_strength * progress
        elif kb_pan == "up" or (kb_pan == "auto" and scene_num % 4 == 3):
            dy = -pan_strength * progress
        elif kb_pan == "down" or (kb_pan == "auto" and scene_num % 4 == 0):
            dy = pan_strength * progress
        
        return (int(w * dx), int(h * dy))
    
    bg = mpe.ColorClip(size=resolution, color=(0, 0, 0), duration=duration)
    zclip = zclip.set_position(pos_func)
    return mpe.CompositeVideoClip([bg, zclip]).set_duration(duration)


# -------------------------------------------------
# 🎥 Main video build function
# -------------------------------------------------
def build_video(
    images: List[str],
    scene_audio: Dict[str, str],
    out_dir: str,
    title: str,
    fps: int = 30,
    resolution: Tuple[int, int] = (1920, 1080),
    crossfade_sec: float = 0.3,
    min_scene_seconds: float = 2.0,
    head_pad: float = 0.15,
    tail_pad: float = 0.15,
    bg_music_path: Optional[str] = None,
    bg_music_volume: float = 0.08,
    ken_burns: bool = True,
    kb_zoom_start: float = 1.05,
    kb_zoom_end: float = 1.15,
    kb_pan: str = "auto"
) -> Dict[str, Any]:
    """Build a complete video from images and audio files."""
    
    if not MOVIEPY_AVAILABLE:
        raise ImportError("❌ MoviePy is required. Install with: pip install moviepy")
    
    if not images:
        raise ValueError("❌ No images provided")
    
    _ensure_dir(out_dir)
    safe_title = title.replace('/', '_').replace('\\', '_')
    video_path = os.path.join(out_dir, f"{safe_title}.mp4")
    
    timings = []
    current_start = 0.0
    video_clips = []
    audio_tracks = []
    
    print("🎞 Building video with MoviePy...")
    print(f"   Processing {len(images)} scenes...")
    
    # Create video clips with timing for CompositeVideoClip
    for idx, img_path in enumerate(images):
        scene_num = idx + 1
        scene_key = f"scene_{scene_num}"
        audio_path = scene_audio.get(scene_key)
        
        if not os.path.exists(img_path):
            print(f"⚠️ Image not found: {img_path}, skipping scene {scene_num}")
            continue
        
        duration = _estimate_scene_duration(audio_path, min_scene_seconds, head_pad, tail_pad)
        
        try:
            # Create base image clip
            if MOVIEPY_VERSION == 2:
                img_clip = ImageClip(img_path, duration=duration)
                img_clip = img_clip.resized(resolution)
                
                # Apply Ken Burns
                if ken_burns:
                    img_clip = _apply_ken_burns_v2(img_clip, duration, scene_num, kb_zoom_start, kb_zoom_end, kb_pan, resolution)
                
                # Set start time for this clip
                img_clip = img_clip.with_start(current_start)
                
                # Apply crossfade using vfx for MoviePy 2.x
                if crossfade_sec > 0 and len(video_clips) > 0:
                    img_clip = img_clip.with_effects([vfx.CrossFadeIn(crossfade_sec)])
            else:
                img_clip = mpe.ImageClip(img_path).set_duration(duration)
                img_clip = img_clip.resize(resolution)
                
                if ken_burns:
                    img_clip = _apply_ken_burns_v1(img_clip, duration, scene_num, kb_zoom_start, kb_zoom_end, kb_pan, resolution)
                
                img_clip = img_clip.set_start(current_start)
                
                if crossfade_sec > 0 and len(video_clips) > 0:
                    img_clip = img_clip.crossfadein(crossfade_sec)
            
            video_clips.append(img_clip)
            
            # Add audio
            if audio_path and os.path.exists(audio_path):
                try:
                    if MOVIEPY_VERSION == 2:
                        narr = AudioFileClip(audio_path)
                        narr = narr.with_start(current_start)
                    else:
                        narr = mpe.AudioFileClip(audio_path)
                        narr = narr.audio_fadein(head_pad).audio_fadeout(tail_pad)
                        narr = narr.set_start(current_start)
                    
                    audio_tracks.append(narr)
                except Exception as e:
                    print(f"⚠️ Could not load audio for scene {scene_num}: {e}")
            
            timings.append({
                "scene": scene_num,
                "start": current_start,
                "end": current_start + duration,
                "duration": duration,
                "image": img_path,
                "audio": audio_path if audio_path and os.path.exists(audio_path) else None
            })
            
            # Update start time (with crossfade overlap)
            current_start += duration - (crossfade_sec if crossfade_sec > 0 and len(video_clips) > 1 else 0)
            
            print(f"   ✓ Scene {scene_num} processed ({duration:.1f}s)")
            
        except Exception as e:
            print(f"⚠️ Error processing scene {scene_num}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    if not video_clips:
        raise ValueError("❌ No valid clips were created")
    
    # Combine clips using CompositeVideoClip for proper crossfade
    print(f"   Combining {len(video_clips)} video clips...")
    if MOVIEPY_VERSION == 2:
        final_video = CompositeVideoClip(video_clips)
    else:
        final_video = mpe.CompositeVideoClip(video_clips)
    
    print(f"✅ Combined {len(video_clips)} video scenes")
    
    # Combine audio
    if audio_tracks:
        print(f"   Processing {len(audio_tracks)} audio tracks...")
        
        if MOVIEPY_VERSION == 2:
            base_audio = CompositeAudioClip(audio_tracks)
        else:
            base_audio = mpe.CompositeAudioClip(audio_tracks)
        
        # Add background music
        if bg_music_path and os.path.exists(bg_music_path):
            try:
                if MOVIEPY_VERSION == 2:
                    music = AudioFileClip(bg_music_path)
                    music = music.with_volume_scaled(bg_music_volume)
                    music = music.with_duration(final_video.duration)
                    final_audio = CompositeAudioClip([base_audio, music])
                else:
                    music = mpe.AudioFileClip(bg_music_path).volumex(bg_music_volume)
                    music = music.set_duration(final_video.duration)
                    final_audio = mpe.CompositeAudioClip([base_audio, music])
                
                print("🎵 Added background music")
            except Exception as e:
                print(f"⚠️ Could not add background music: {e}")
                final_audio = base_audio
        else:
            final_audio = base_audio
        
        if MOVIEPY_VERSION == 2:
            final_video = final_video.with_audio(final_audio)
        else:
            final_video = final_video.set_audio(final_audio)
    else:
        print("⚠️ No audio tracks found, creating silent video")
    
    # Write video
    print(f"🧾 Writing final video to {video_path}")
    print(f"   This may take a while...")
    
    try:
        final_video.write_videofile(
            video_path,
            fps=fps,
            codec="libx264",
            audio_codec="aac",
            threads=4,
            preset='medium',
            temp_audiofile=os.path.join(out_dir, "temp-audio.m4a"),
            remove_temp=True,
            logger='bar'
        )
    except Exception as e:
        # Cleanup on failure
        for clip in video_clips:
            try:
                clip.close()
            except:
                pass
        try:
            final_video.close()
        except:
            pass
        raise Exception(f"❌ Failed to write video: {e}")
    
    # Cleanup
    print("🧹 Cleaning up resources...")
    for clip in video_clips:
        try:
            clip.close()
        except:
            pass
    try:
        final_video.close()
    except:
        pass
    
    print("🎉 Video generation complete:")
    print(f"   • Output: {video_path}")
    print(f"   • Scenes: {len(video_clips)}")
    print(f"   • Duration: {current_start:.1f}s")
    print(f"   • Resolution: {resolution[0]}x{resolution[1]}")
    print(f"   • FPS: {fps}")
    
    return {"video_path": video_path, "timings": timings, "duration": current_start}