import streamlit as st
import whisper
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip, ColorClip
from gtts import gTTS
import tempfile
import os

st.set_page_config(page_title="KICK_FC Shorts AI", layout="centered")
st.title("🎬 KICK_FC AI Shorts Generator")
st.markdown("Create YouTube Shorts from long videos or scripts — instantly, with style.")

option = st.radio("Choose your content type:", ("📹 Long Video", "📝 Script/Text"))

if option == "📹 Long Video":
    uploaded_file = st.file_uploader("Upload your long video (MP4)", type=["mp4"])

    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
            temp_video.write(uploaded_file.read())
            video_path = temp_video.name

        st.video(video_path)
        st.write("⚙️ Transcribing...")

        model = whisper.load_model("base")
        result = model.transcribe(video_path)
        transcription = result["text"]

        st.success("✅ Transcription done!")
        st.text_area("📝 Transcript:", transcription, height=100)

        # Trim to 60s max
        video = VideoFileClip(video_path)
        short_clip = video.subclip(0, min(60, video.duration))

        # Add subtitle (first 60 characters)
        subtitle = TextClip(transcription[:60] + "...", fontsize=60, color='white', font="Arial-Bold")
        subtitle = subtitle.set_position('bottom').set_duration(short_clip.duration)

        final_clip = CompositeVideoClip([short_clip, subtitle])

        output_path = os.path.join(tempfile.gettempdir(), "kickfc_short_video.mp4")
        final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

        with open(output_path, "rb") as file:
            st.download_button("📥 Download Your Short", file, file_name="kickfc_short_video.mp4")

elif option == "📝 Script/Text":
    script = st.text_area("✍️ Enter your script (max ~60 seconds worth):", height=150)

    if st.button("🎥 Generate Video") and script:
        tts = gTTS(script)
        audio_path = os.path.join(tempfile.gettempdir(), "tts.mp3")
        tts.save(audio_path)

        audio = AudioFileClip(audio_path)
        duration = audio.duration

        background = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=duration)
        caption = TextClip(script, fontsize=60, color='white', size=(1000, None), method='pillow')
        caption = caption.set_duration(duration).set_position("center")

        final = CompositeVideoClip([background, caption.set_start(0)]).set_audio(audio)

        output_path = os.path.join(tempfile.gettempdir(), "kickfc_text_short.mp4")
        final.write_videofile(output_path, fps=24)

        with open(output_path, "rb") as f:
            st.download_button("📥 Download Short", f, file_name="kickfc_text_short.mp4")
