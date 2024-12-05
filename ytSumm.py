import os
import json
import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from urllib.parse import urlparse, parse_qs

# Configuration setup
def load_config():
    try:
        working_directory = os.path.dirname(os.path.abspath(__file__))
        config_file_path = os.path.join(working_directory, "config.json")
        with open(config_file_path) as f:
            config_data = json.load(f)
        return config_data.get("GOOGLE_API_KEY")
    except Exception as e:
        st.error(f"Error loading configuration: {e}")
        return None
    
prompt = """Summarize the key points and insights from this video content. Focus on the main ideas, concepts, and important takeaways. Structure the summary to include:

1. Main topic and core message
2. Key points covered
3. Important examples or case studies
4. Practical takeaways or conclusions

Make the summary clear, concise, and easy to understand. Keep it informative and engaging while maintaining accuracy to the original content.

Transcript text:"""
# Extract video ID from various YouTube URL formats
def extract_video_id(url):
    try:
        # Handle different YouTube URL formats
        parsed_url = urlparse(url)
        if parsed_url.hostname in ('youtu.be', 'www.youtu.be'):
            return parsed_url.path[1:]
        if parsed_url.hostname in ('youtube.com', 'www.youtube.com'):
            if parsed_url.path == '/watch':
                return parse_qs(parsed_url.query)['v'][0]
            if parsed_url.path.startswith('/embed/'):
                return parsed_url.path.split('/')[2]
            if parsed_url.path.startswith('/v/'):
                return parsed_url.path.split('/')[2]
        return None
    except Exception:
        return None

def extract_transcript_details(youtube_video_url):
    try:
        video_id = extract_video_id(youtube_video_url)
        if not video_id:
            st.error("Invalid YouTube URL. Please check the URL and try again.")
            return None
        
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join(item["text"] for item in transcript_text)
        return transcript
    except TranscriptsDisabled:
        st.error("Subtitles are disabled for this video. Unable to retrieve transcript.")
        return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

def generate_gemini_content(transcript_text, prompt):
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt + transcript_text)
        return response.text
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return None

# Streamlit UI
st.title("YouTube Transcript Summarizer")
st.write("Enter a YouTube video URL to get a detailed summary of its content.")

# Initialize session state for the input field
if 'youtube_link' not in st.session_state:
    st.session_state.youtube_link = ''

youtube_link = st.text_input("Enter YouTube Video Link:", st.session_state.youtube_link)

if youtube_link:
    video_id = extract_video_id(youtube_link)
    if video_id:
        # Display thumbnail with error handling
        try:
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            st.image(thumbnail_url, use_container_width=True)
        except Exception:
            try:
                # Fallback to default thumbnail if maxresdefault is not available
                thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
                st.image(thumbnail_url, use_container_width=True)
            except Exception as e:
                st.error(f"Error loading thumbnail: {e}")

if st.button("Get Detailed Summary"):
    # Initialize API
    api_key = load_config()
    if not api_key:
        st.error("API key not found. Please check your configuration.")
    else:
        genai.configure(api_key=api_key)
        
        with st.spinner("Generating summary..."):
            transcript_text = extract_transcript_details(youtube_link)
            if transcript_text:
                summary = generate_gemini_content(transcript_text, prompt)
                if summary:
                    st.markdown('## Detailed Summary')
                    st.write(summary)