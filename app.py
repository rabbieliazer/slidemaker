import streamlit as st
import subprocess
import os

# Page Configuration
st.set_page_config(page_title="Tosh Video Slide Maker", page_icon="🎬")

st.title("🎬 Video to Slide Converter")
st.write("Upload a video to extract a 'slide' every few seconds. Powered by Cloud FFmpeg.")

# 1. User Inputs
uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "avi", "mkv"])
seconds = st.number_input("Seconds per slide", min_value=1, value=3)

if uploaded_file is not None:
    # Define temporary file names
    input_filename = "input_video.mp4"
    output_filename = "output_slides.mp4"

    # Save uploaded file to the cloud server disk
    with open(input_filename, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if st.button("Start Conversion"):
        with st.spinner("Processing... The cloud server is extracting frames."):
            try:
                # 2. Get Frame Rate using ffprobe
                probe_cmd = [
                    "ffprobe", "-v", "error", "-select_streams", "v:0",
                    "-show_entries", "stream=avg_frame_rate",
                    "-of", "default=noprint_wrappers=1:nokey=1", input_filename
                ]
                fr_str = subprocess.check_output(probe_cmd).decode().strip()
                
                # Handle fractional frame rates (e.g., 30000/1001)
                if '/' in fr_str:
                    num, den = map(int, fr_str.split('/'))
                    fps = num / den
                else:
                    fps = float(fr_str)

                # Calculate how many frames to skip
                frame_skip = int(fps * seconds)

                # 3. Run FFmpeg command
                # We use -vsync vfr to ensure the output stays as a video of slides
                ffmpeg_cmd = [
                    "ffmpeg", "-i", input_filename, 
                    "-vf", fr"select='not(mod(n\,{frame_skip}))'", 
                    "-vsync", "vfr", "-y", output_filename
                ]
                
                subprocess.run(ffmpeg_cmd, check=True)

                # 4. Prepare for Download
                # We read the file into memory to ensure the browser gets an MP4, not an HTML error
                with open(output_filename, "rb") as f:
                    video_bytes = f.read()

                st.success(f"Successfully converted! Source FPS: {fps:.2f}")
                
                st.download_button(
                    label="Click here to Download MP4",
                    data=video_bytes,
                    file_name="converted_slides.mp4",
                    mime="video/mp4"
                )

            except Exception as e:
                st.error(f"Error during processing: {e}")
            
            finally:
                # 5. Cleanup: Remove files from server to save space
                if os.path.exists(input_filename):
                    os.remove(input_filename)
                if os.path.exists(output_filename):
                    os.remove(output_filename)
