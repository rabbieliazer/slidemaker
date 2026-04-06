import streamlit as st
import subprocess
import os
import base64

# Page Configuration
st.set_page_config(page_title="Video Slide Maker", page_icon="🎬")

st.title("🎬 Video to Slide Converter")
st.write("Developed by tosh dvelopers. Upload a video to extract a 'slide' every few seconds.")

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

                # 4. Prepare for Download (The Base64 Workaround)
                # Read the file into memory to ensure the browser gets an MP4
                with open(output_filename, "rb") as f:
                    video_bytes = f.read()

                # Encode the video to base64
                b64 = base64.b64encode(video_bytes).decode()
                
                # Create a raw HTML download link with a custom aesthetic
                href = f'''
                <div style="margin-top: 20px; margin-bottom: 20px;">
                    <a href="data:video/mp4;base64,{b64}" download="converted_slides.mp4" 
                       style="display: inline-block; padding: 12px 24px; background-color: #000000; color: #D4AF37; 
                              border: 1px solid #D4AF37; text-decoration: none; border-radius: 4px; 
                              font-weight: bold; font-family: sans-serif; letter-spacing: 1px;">
                       📥 DOWNLOAD MP4 SLIDES
                    </a>
                </div>
                '''
                
                st.success(f"Successfully converted! Source FPS: {fps:.2f}")
                
                # Display the custom link
                st.markdown(href, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error during processing: {e}")
            
            finally:
                # 5. Cleanup: Remove files from server to save space
                if os.path.exists(input_filename):
                    os.remove(input_filename)
                if os.path.exists(output_filename):
                    os.remove(output_filename)