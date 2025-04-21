import streamlit as st
from moviepy.editor import (
    VideoFileClip,
    CompositeVideoClip,
    AudioFileClip,
    ColorClip,
    ImageClip,
)
from gtts import gTTS
import tempfile
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np

st.set_page_config(page_title="KICK_FC Shorts AI", layout="centered")

st.title("🎬 KICK_FC Shorts AI")

option = st.radio("Choose an option:", ["Script to Video", "Video to Short"])

if option == "Script to Video":
    script = st.text_area("✍️ Enter your script:")
    if st.button("🎥 Generate Video"):
        if script:
            with st.spinner("Generating video..."):
                # Convert text to speech
                tts = gTTS(text=script, lang="en")
                audio_path = os.path.join(tempfile.gettempdir(), "temp_audio.mp3")
                tts.save(audio_path)

                # Create a background color clip
                background = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=5)

                # Load font
                font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Or any default font path
                font_size = 60

                # Create caption image
                font = ImageFont.truetype(font_path, font_size)
                text_img = Image.new("RGBA", (1000, 400), (0, 0, 0, 0))
                draw = ImageDraw.Draw(text_img)
                draw.text((10, 10), script, font=font, fill="white")

                # Convert PIL image to MoviePy clip
                text_clip = (
                    ImageClip(np.array(text_img))
                    .set_duration(5)
                    .set_position("center")
                )

                # Add audio
                audio = AudioFileClip(audio_path).subclip(0, 5)

                # Combine everything
                video = CompositeVideoClip([background, text_clip])
                video = video.set_audio(audio)

                # Export
                output_path = os.path.join(tempfile.gettempdir(), "output.mp4")
                video.write_videofile(output_path, fps=24)

                # Show in app
                st.video(output_path)
        else:
            st.warning("Please enter a script.")

elif option == "Video to Short":
    uploaded_video = st.file_uploader("📹 Upload your video", type=["mp4", "mov"])
    if uploaded_video:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp:
            temp.write(uploaded_video.read())
            temp_path = temp.name

        with st.spinner("Trimming video..."):
            clip = VideoFileClip(temp_path).subclip(0, 15)
            output_path = os.path.join(tempfile.gettempdir(), "short_video.mp4")
            clip.write_videofile(output_path, fps=24)

        st.video(output_path)
