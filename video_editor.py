import os
import shutil
import subprocess
from typing import List, Dict, Any, Optional, Tuple

# Configure imageio-ffmpeg for moviepy
try:
    import imageio_ffmpeg
    os.environ["IMAGEIO_FFMPEG_EXE"] = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    pass


def _ensure_dir(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)


def _get_audio_duration_seconds(audio_path: str) -> float:
    try:
        from pydub import AudioSegment
        seg = AudioSegment.from_file(audio_path)
        return seg.duration_seconds
    except Exception:
        return 0.0


def _estimate_scene_duration(audio_path: Optional[str], min_seconds: float, head_pad: float, tail_pad: float) -> float:
    duration = min_seconds
    if audio_path and os.path.exists(audio_path):
        # Prefer pydub to avoid hard dependency
        d = _get_audio_duration_seconds(audio_path)
        if d > 0:
            duration = max(min_seconds, d + head_pad + tail_pad)
        else:
            try:
                # Try moviepy 2.x first
                from moviepy import AudioFileClip
                audio = AudioFileClip(audio_path)
                duration = max(min_seconds, audio.duration + head_pad + tail_pad)
                audio.close()
            except Exception:
                try:
                    # Fall back to moviepy 1.x
                    import moviepy.editor as mpe
                    audio = mpe.AudioFileClip(audio_path)
                    duration = max(min_seconds, audio.duration + head_pad + tail_pad)
                    audio.close()
                except Exception:
                    duration = max(min_seconds, head_pad + tail_pad)
    return duration


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
    bg_music_volume: float = 0.08
) -> Dict[str, Any]:
    """
    Build a video from images and audio with improved robustness.
    Handles both MoviePy 1.x and 2.x with proper fallbacks.
    """
    moviepy_version = 0
    use_moviepy = False
    
    # Try importing MoviePy with better detection
    try:
        # Try moviepy 2.x imports first
        from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips
        import moviepy.audio.fx.all as afx
        use_moviepy = True
        moviepy_version = 2
        print("✓ MoviePy 2.x detected and loaded")
    except ImportError:
        try:
            # Fall back to moviepy 1.x imports
            import moviepy.editor as mpe
            from moviepy.audio.fx.audio_fadein import audio_fadein
            from moviepy.audio.fx.audio_fadeout import audio_fadeout
            from moviepy.audio.fx.volumex import volumex
            use_moviepy = True
            moviepy_version = 1
            print("✓ MoviePy 1.x detected and loaded")
        except ImportError as e:
            print(f"⚠ MoviePy not available: {str(e)}")
            print("⚠ Falling back to FFmpeg-only mode")
            use_moviepy = False
            moviepy_version = 0

    _ensure_dir(out_dir)
    safe_title = title.replace('/', '_')
    video_path = os.path.join(out_dir, f"{safe_title}.mp4")

    clips = []
    audio_tracks = []
    timings = []
    current_start = 0.0

    for idx, img_path in enumerate(images):
        scene_num = idx + 1
        scene_key = f"scene_{scene_num}"
        audio_path = scene_audio.get(scene_key)

        duration = _estimate_scene_duration(audio_path, min_scene_seconds, head_pad, tail_pad)

        if use_moviepy:
            if moviepy_version == 2:
                # MoviePy 2.x with robust error handling
                w, h = resolution
                
                # Create image clip with multiple fallback attempts
                img_clip = None
                try:
                    img_clip = ImageClip(img_path).resized(new_size=(w, h)).with_duration(duration)
                except Exception:
                    try:
                        img_clip = ImageClip(img_path).resized((w, h)).with_duration(duration)
                    except Exception:
                        try:
                            img_clip = ImageClip(img_path).with_duration(duration)
                        except Exception as e:
                            raise Exception(f"Failed to create image clip for scene {scene_num}: {e}")
                
                # Apply crossfade only if supported and not first clip
                if crossfade_sec > 0 and len(clips) > 0:
                    try:
                        img_clip = img_clip.crossfadein(crossfade_sec)
                    except (AttributeError, Exception):
                        pass  # Silently skip if crossfade not available
                
                clips.append(img_clip)

                # Handle audio with proper fade effects
                if audio_path and os.path.exists(audio_path):
                    try:
                        narr = AudioFileClip(audio_path)
                        
                        # Try to apply fade effects using MoviePy 2.x
                        try:
                            # Method 1: Using audio.fx.all module
                            narr = afx.audio_fadein(narr, head_pad)
                            narr = afx.audio_fadeout(narr, tail_pad)
                        except (AttributeError, Exception):
                            try:
                                # Method 2: Using with_effects if available
                                narr = narr.audio_fadein(head_pad).audio_fadeout(tail_pad)
                            except (AttributeError, Exception):
                                # Method 3: Manual volume envelope (most compatible)
                                try:
                                    def make_fade(clip, fadein_duration, fadeout_duration):
                                        """Apply fade in/out using volume adjustment"""
                                        def envelope(t):
                                            if t < fadein_duration:
                                                return t / fadein_duration
                                            elif t > clip.duration - fadeout_duration:
                                                return (clip.duration - t) / fadeout_duration
                                            return 1.0
                                        return clip.with_volume_scaled(envelope)
                                    
                                    narr = make_fade(narr, head_pad, tail_pad)
                                except Exception:
                                    pass  # Use audio without fades if all methods fail
                        
                        audio_tracks.append(narr.with_start(current_start))
                    except Exception as e:
                        print(f"⚠ Could not load audio for scene {scene_num}: {e}")
                        
            else:
                # MoviePy 1.x with proper error handling
                try:
                    img_clip = mpe.ImageClip(img_path).resize(newsize=resolution).set_duration(duration)
                except Exception:
                    img_clip = mpe.ImageClip(img_path).set_duration(duration)
                
                if crossfade_sec > 0 and len(clips) > 0:
                    try:
                        img_clip = img_clip.crossfadein(crossfade_sec)
                    except (AttributeError, Exception):
                        pass  # Skip crossfade if not available
                
                clips.append(img_clip)

                if audio_path and os.path.exists(audio_path):
                    try:
                        narr = mpe.AudioFileClip(audio_path)
                        try:
                            narr = audio_fadein(narr, head_pad)
                            narr = audio_fadeout(narr, tail_pad)
                        except Exception:
                            pass  # Use audio without fades if effects fail
                        audio_tracks.append(narr.set_start(current_start))
                    except Exception as e:
                        print(f"⚠ Could not load audio for scene {scene_num}: {e}")

        timings.append({
            "scene": scene_num,
            "start": current_start,
            "end": current_start + duration,
            "duration": duration,
            "image": img_path,
            "audio": audio_path if audio_path and os.path.exists(audio_path) else None
        })

        current_start += duration - (crossfade_sec if crossfade_sec > 0 else 0)

    if use_moviepy:
        if moviepy_version == 2:
            # MoviePy 2.x with robust concatenation
            try:
                final_video = concatenate_videoclips(clips, method="compose")
                print(f"✓ Successfully concatenated {len(clips)} video clips")
            except Exception as e:
                try:
                    # Try without method parameter
                    final_video = concatenate_videoclips(clips)
                    print(f"✓ Successfully concatenated {len(clips)} video clips (basic mode)")
                except Exception as e2:
                    raise Exception(f"Failed to concatenate video clips: {e2}")

            # Handle audio composition with multiple fallback strategies
            if audio_tracks:
                try:
                    base_audio = CompositeAudioClip(audio_tracks)
                    print(f"✓ Successfully composed {len(audio_tracks)} audio tracks")
                    
                    # Handle background music if provided
                    if bg_music_path and os.path.exists(bg_music_path):
                        try:
                            music = AudioFileClip(bg_music_path)
                            
                            # Try multiple volume adjustment methods
                            volume_adjusted = False
                            try:
                                # Method 1: Using audio.fx.all
                                music = afx.multiply_volume(music, bg_music_volume)
                                volume_adjusted = True
                            except Exception:
                                try:
                                    # Method 2: Using volumex if available
                                    music = music.with_volume_scaled(lambda t: bg_music_volume)
                                    volume_adjusted = True
                                except Exception:
                                    print(f"⚠ Volume adjustment not available, using original volume")
                            
                            # Set duration and combine with narration
                            music = music.with_start(0).with_duration(final_video.duration)
                            final_audio = CompositeAudioClip([music, base_audio])
                            final_video = final_video.with_audio(final_audio)
                            print(f"✓ Added background music {'with' if volume_adjusted else 'without'} volume adjustment")
                        except Exception as e:
                            print(f"⚠ Background music error: {e}, using narration only")
                            final_video = final_video.with_audio(base_audio)
                    else:
                        final_video = final_video.with_audio(base_audio)
                except Exception as e:
                    print(f"⚠ Audio composition error: {e}, video will have no audio")
                    
        else:
            # MoviePy 1.x with error handling
            try:
                final_video = mpe.concatenate_videoclips(clips, method="compose")
                print(f"✓ Successfully concatenated {len(clips)} video clips")
            except Exception:
                final_video = mpe.concatenate_videoclips(clips)
                print(f"✓ Successfully concatenated {len(clips)} video clips (basic mode)")

            if audio_tracks:
                try:
                    base_audio = mpe.CompositeAudioClip(audio_tracks)
                    print(f"✓ Successfully composed {len(audio_tracks)} audio tracks")
                    
                    if bg_music_path and os.path.exists(bg_music_path):
                        try:
                            music = mpe.AudioFileClip(bg_music_path)
                            music = volumex(music, bg_music_volume)
                            music = music.set_start(0).set_duration(final_video.duration)
                            final_video = final_video.set_audio(mpe.CompositeAudioClip([music, base_audio]))
                            print(f"✓ Added background music")
                        except Exception as e:
                            print(f"⚠ Background music error: {e}, using narration only")
                            final_video = final_video.set_audio(base_audio)
                    else:
                        final_video = final_video.set_audio(base_audio)
                except Exception as e:
                    print(f"⚠ Audio composition error: {e}, video will have no audio")

        # Write video file with comprehensive error handling and fallbacks
        write_success = False
        print(f"🎬 Writing video to: {video_path}")
        
        # Try method 1: Full parameters with optimizations
        try:
            final_video.write_videofile(
                video_path,
                fps=fps,
                codec="libx264",
                audio_codec="aac",
                preset="medium",
                threads=4,
                temp_audiofile=os.path.join(out_dir, "temp-audio.m4a"),
                remove_temp=True,
                logger=None  # Suppress verbose output
            )
            print(f"✓ Video written successfully with optimized settings")
            write_success = True
        except Exception as e:
            print(f"⚠ Full parameter write failed: {e}")
            
            # Try method 2: Basic parameters
            if not write_success:
                try:
                    print(f"Retrying with basic parameters...")
                    final_video.write_videofile(
                        video_path,
                        fps=fps,
                        codec="libx264",
                        audio_codec="aac",
                        logger=None
                    )
                    print(f"✓ Video written successfully with basic settings")
                    write_success = True
                except Exception as e2:
                    print(f"⚠ Basic parameter write failed: {e2}")
                    
                    # Try method 3: Minimal parameters (last resort)
                    if not write_success:
                        try:
                            print(f"Final attempt with minimal parameters...")
                            final_video.write_videofile(video_path, fps=fps)
                            print(f"✓ Video written successfully with minimal settings")
                            write_success = True
                        except Exception as e3:
                            raise Exception(f"All video write attempts failed. Last error: {e3}")

        # Cleanup resources properly
        try:
            print(f"Cleaning up resources...")
            for clip in clips:
                try:
                    clip.close()
                except Exception:
                    pass
            if 'base_audio' in locals():
                try:
                    base_audio.close()
                except Exception:
                    pass
            if 'music' in locals():
                try:
                    music.close()
                except Exception:
                    pass
            if 'final_audio' in locals():
                try:
                    final_audio.close()
                except Exception:
                    pass
            final_video.close()
            print(f"✓ Resources cleaned up")
        except Exception as e:
            print(f"⚠ Cleanup warning: {e}")
    else:
        # Fallback: FFmpeg-only assembly (when MoviePy is not available)
        print(f"Using FFmpeg-only mode for video assembly...")
        if shutil.which("ffmpeg") is None:
            raise ImportError(
                "Neither MoviePy nor FFmpeg is available. Please install one of them:\n"
                "  - MoviePy: pip install moviepy\n"
                "  - FFmpeg: https://ffmpeg.org/download.html"
            )

        tmp_dir = os.path.join(out_dir, "_segments")
        _ensure_dir(tmp_dir)
        segment_paths: List[str] = []

        w, h = resolution
        for t in timings:
            scene = t["scene"]
            image = t["image"]
            audio = t["audio"]
            duration = max(t["duration"], 0.5)
            seg_path = os.path.join(tmp_dir, f"seg_{scene:02d}.mp4")

            # Build video segment from image and audio
            vf = f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black,format=yuv420p"
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1", "-i", image,
                "-i", audio if audio else image,
                "-t", f"{duration:.3f}",
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-vf", vf,
                "-c:a", "aac", "-shortest",
                seg_path
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            segment_paths.append(seg_path)

        # Concat segments
        list_file = os.path.join(tmp_dir, "concat.txt")
        with open(list_file, "w", encoding="utf-8") as f:
            for p in segment_paths:
                f.write(f"file '{p}'\n")

        cmd_concat = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file,
            "-c", "copy", video_path
        ]
        result = subprocess.run(cmd_concat, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"FFmpeg concatenation failed: {result.stderr}")
        
        print(f"✓ Video assembled successfully using FFmpeg")
        
        # Cleanup temporary files
        try:
            shutil.rmtree(tmp_dir)
            print(f"✓ Temporary files cleaned up")
        except Exception as e:
            print(f"⚠ Could not remove temporary files: {e}")

    print(f"🎉 Video generation complete: {video_path}")
    print(f"   - Total scenes: {len(images)}")
    print(f"   - Total duration: {current_start:.1f}s")
    print(f"   - Resolution: {resolution[0]}x{resolution[1]}")
    print(f"   - FPS: {fps}")
    
    return {"video_path": video_path, "timings": timings, "duration": current_start}