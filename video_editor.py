import os
import shutil
import subprocess
from typing import List, Dict, Any, Optional, Tuple

# -------------------------------------------------
# 🎬 MoviePy setup (supports MoviePy 2.x and 1.x)
# -------------------------------------------------
MOVIEPY_AVAILABLE = False
MOVIEPY_VERSION = 0

try:
    # ✅ Try MoviePy 2.x (new import structure)
    from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips
    import moviepy.audio.fx.all as afx
    from moviepy.audio.fx.all import audio_fadein, audio_fadeout
    MOVIEPY_AVAILABLE = True
    MOVIEPY_VERSION = 2
    print("🎬 MoviePy 2.x detected and loaded")
except ImportError:
    try:
        # ✅ Fallback: MoviePy 1.x (old import style)
        import moviepy.editor as mpe
        import moviepy.audio.fx.all as afx
        from moviepy.audio.fx.all import audio_fadein, audio_fadeout
        MOVIEPY_AVAILABLE = True
        MOVIEPY_VERSION = 1
        print("🎬 MoviePy 1.x detected and loaded")
    except ImportError:
        MOVIEPY_AVAILABLE = False
        MOVIEPY_VERSION = 0
        print("⚠️ MoviePy not available — will use FFmpeg fallback")

# 🎥 Configure imageio-ffmpeg for MoviePy
try:
    import imageio_ffmpeg
    os.environ["IMAGEIO_FFMPEG_EXE"] = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    pass


# -------------------------------------------------
# Utility functions
# -------------------------------------------------
def _ensure_dir(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)


def _get_audio_duration_seconds(audio_path: str) -> float:
    """Try to get duration using pydub for more reliable reading."""
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
    bg_music_volume: float = 0.08
) -> Dict[str, Any]:
    """
    Build a complete video from a list of images and corresponding audio files.
    Supports MoviePy 1.x / 2.x and FFmpeg fallback.
    """
    _ensure_dir(out_dir)
    safe_title = title.replace('/', '_')
    video_path = os.path.join(out_dir, f"{safe_title}.mp4")

    timings = []
    current_start = 0.0
    clips = []
    audio_tracks = []

    # -------------------------------------------------
    # 🎬 MoviePy Mode
    # -------------------------------------------------
    if MOVIEPY_AVAILABLE:
        print("🎞 Building video with MoviePy...")

        for idx, img_path in enumerate(images):
            scene_num = idx + 1
            scene_key = f"scene_{scene_num}"
            audio_path = scene_audio.get(scene_key)
            duration = _estimate_scene_duration(audio_path, min_scene_seconds, head_pad, tail_pad)

            try:
                if MOVIEPY_VERSION == 2:
                    img_clip = ImageClip(img_path).resized(new_size=resolution).with_duration(duration)
                else:
                    img_clip = mpe.ImageClip(img_path).resize(newsize=resolution).set_duration(duration)

                if crossfade_sec > 0 and clips:
                    try:
                        img_clip = img_clip.crossfadein(crossfade_sec)
                    except Exception:
                        pass
                clips.append(img_clip)

                if audio_path and os.path.exists(audio_path):
                    if MOVIEPY_VERSION == 2:
                        narr = AudioFileClip(audio_path)
                    else:
                        narr = mpe.AudioFileClip(audio_path)
                    narr = audio_fadein(narr, head_pad)
                    narr = audio_fadeout(narr, tail_pad)
                    audio_tracks.append(narr.set_start(current_start))

            except Exception as e:
                print(f"⚠️ Scene {scene_num} error: {e}")

            timings.append({
                "scene": scene_num,
                "start": current_start,
                "end": current_start + duration,
                "duration": duration,
                "image": img_path,
                "audio": audio_path if audio_path and os.path.exists(audio_path) else None
            })

            current_start += duration - (crossfade_sec if crossfade_sec > 0 else 0)

        # Combine clips
        try:
            if MOVIEPY_VERSION == 2:
                final_video = concatenate_videoclips(clips, method="compose")
            else:
                final_video = mpe.concatenate_videoclips(clips, method="compose")
            print(f"✅ Combined {len(clips)} video scenes")
        except Exception as e:
            raise Exception(f"❌ Clip concatenation failed: {e}")

        # Combine audio
        try:
            if audio_tracks:
                if MOVIEPY_VERSION == 2:
                    base_audio = CompositeAudioClip(audio_tracks)
                else:
                    base_audio = mpe.CompositeAudioClip(audio_tracks)

                if bg_music_path and os.path.exists(bg_music_path):
                    try:
                        if MOVIEPY_VERSION == 2:
                            music = AudioFileClip(bg_music_path)
                            music = afx.multiply_volume(music, bg_music_volume)
                            music = music.with_duration(final_video.duration)
                            final_audio = CompositeAudioClip([base_audio, music])
                            final_video = final_video.with_audio(final_audio)
                        else:
                            music = mpe.AudioFileClip(bg_music_path).volumex(bg_music_volume)
                            music = music.set_start(0).set_duration(final_video.duration)
                            final_video = final_video.set_audio(mpe.CompositeAudioClip([music, base_audio]))
                        print("🎵 Added background music")
                    except Exception as e:
                        print(f"⚠️ Music error: {e}, narration only")
                        if MOVIEPY_VERSION == 2:
                            final_video = final_video.with_audio(base_audio)
                        else:
                            final_video = final_video.set_audio(base_audio)
                else:
                    if MOVIEPY_VERSION == 2:
                        final_video = final_video.with_audio(base_audio)
                    else:
                        final_video = final_video.set_audio(base_audio)
        except Exception as e:
            print(f"⚠️ Audio composition error: {e}")

        # Write video
        print(f"🧾 Writing final video to {video_path}")
        try:
            final_video.write_videofile(
                video_path,
                fps=fps,
                codec="libx264",
                audio_codec="aac",
                threads=4,
                temp_audiofile=os.path.join(out_dir, "temp-audio.m4a"),
                remove_temp=True,
                logger=None
            )
            print(f"✅ Video written successfully: {video_path}")
        except Exception as e:
            raise Exception(f"❌ Failed to write video: {e}")

        finally:
            for clip in clips:
                try:
                    clip.close()
                except Exception:
                    pass
            try:
                final_video.close()
            except Exception:
                pass
            print("🧹 Cleaned up MoviePy resources")

    # -------------------------------------------------
    # ⚙️ FFmpeg fallback
    # -------------------------------------------------
    else:
        print("⚙ Using FFmpeg-only fallback mode...")
        if shutil.which("ffmpeg") is None:
            raise ImportError("❌ FFmpeg not installed. Please install MoviePy or FFmpeg.")

        tmp_dir = os.path.join(out_dir, "_segments")
        _ensure_dir(tmp_dir)
        segment_paths = []
        w, h = resolution

        for idx, img_path in enumerate(images):
            scene_num = idx + 1
            audio_path = scene_audio.get(f"scene_{scene_num}")
            duration = _estimate_scene_duration(audio_path, min_scene_seconds, head_pad, tail_pad)
            seg_path = os.path.join(tmp_dir, f"seg_{scene_num:02d}.mp4")

            vf = f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black,format=yuv420p"
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1", "-i", img_path
            ]
            if audio_path and os.path.exists(audio_path):
                cmd += ["-i", audio_path, "-shortest"]
            else:
                cmd += ["-t", f"{duration:.3f}"]
            cmd += [
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-vf", vf,
                "-c:a", "aac",
                seg_path
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            segment_paths.append(seg_path)

        list_file = os.path.join(tmp_dir, "concat.txt")
        with open(list_file, "w", encoding="utf-8") as f:
            for p in segment_paths:
                f.write(f"file '{os.path.abspath(p)}'\n")

        concat_cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", video_path]
        result = subprocess.run(concat_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"❌ FFmpeg concatenation failed: {result.stderr}")

        shutil.rmtree(tmp_dir, ignore_errors=True)
        print(f"✅ FFmpeg video successfully created: {video_path}")

    # -------------------------------------------------
    # ✅ Summary
    # -------------------------------------------------
    print("🎉 Video generation complete:")
    print(f"   • Output: {video_path}")
    print(f"   • Scenes: {len(images)}")
    print(f"   • Duration: {current_start:.1f}s")
    print(f"   • Resolution: {resolution[0]}x{resolution[1]}")
    print(f"   • FPS: {fps}")

    return {"video_path": video_path, "timings": timings, "duration": current_start}
