import streamlit as st
import subprocess
import os

st.set_page_config(page_title="Video to Slide Converter")

st.title("🎬 Video to Slide Converter")
st.write("Upload a video and extract slides automatically.")

# 1. File Uploader
uploaded_file = st.file_input("Choose a video file", type=["mp4", "mov", "avi", "mkv"])
seconds = st.number_input("Seconds per slide", min_value=1, value=3)

if uploaded_file is not None:
    # Save uploaded file to the server temporarily
    with open("input_video", "wb") as f:
        f.write(uploaded_file.getbuffer())

    if st.button("Convert to Slides"):
        with st.spinner("Processing... This is running on our high-speed servers."):
            # 2. Get Frame Rate using ffprobe
            probe_cmd = [
                "ffprobe", "-v", "error", "-select_streams", "v:0",
                "-show_entries", "stream=avg_frame_rate",
                "-of", "default=noprint_wrappers=1:nokey=1", "input_video"
            ]
            fr_str = subprocess.check_output(probe_cmd).decode().strip()
            
            if '/' in fr_str:
                num, den = map(int, fr_str.split('/'))
                fps = num / den
            else:
                fps = float(fr_str)

            frame_skip = int(fps * seconds)
            output_name = "output_slides.mp4"

            # 3. Run FFmpeg
            ffmpeg_cmd = [
                "ffmpeg", "-i", "input_video", 
                "-vf", f"select='not(mod(n\,{frame_skip}))'", 
                "-vsync", "vfr", "-y", output_name
            ]
            subprocess.run(ffmpeg_cmd)

            # 4. Provide Download Link
            with open(output_name, "rb") as file:
                st.download_button(
                    label="Download Resulting Slides",
                    data=file,
                    file_name="converted_slides.mp4",
                    mime="video/mp4"
                )
        st.success("Done!")