import os
import json  
import google.generativeai as genai
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from urllib.parse import urlparse, parse_qs
import google.generativeai as genai



working_directory= os.path.dirname(os.path.abspath(__file__))

config_file_path=f"{working_directory}/config.json"
config_data=json.load(open(config_file_path))
#loadig api key
GOOGLE_API_KEY = config_data["GOOGLE_API_KEY"]
print(GOOGLE_API_KEY)


#Conguguring google gen ai with api key
genai.configure(api_key=GOOGLE_API_KEY)

#function to load geminin pro model for the chatbot
def load_gemini_pro_model():
    gemini_pro_model=genai.GenerativeModel("gemini-1.5-pro")
    return gemini_pro_model


# Function to load Gemini Pro model for image captioning
def gemini_pro_vision_response(prompt, image):
    gemini_pro_vision_model = genai.GenerativeModel("gemini-1.5-flash")
    response = gemini_pro_vision_model.generate_content([prompt, image])
    result = response.text
    return result

#function to get text
def embedding_model_reponse(input_text):
    embedding_model = "models/embedding-001"
    embedding = genai.embed_content(model=embedding_model,
                                     content = input_text,
                                     task_type = "retrieval_document",
                                     )
    embedding_list = embedding['embedding']
    return embedding_list


#Function te get respomse from gemini pro 
def gemini_pro_response(user_prompt):
    gemini_pro_model=genai.GenerativeModel("gemini-pro")
    response =gemini_pro_model.generate_content(user_prompt)
    result =  response.text 
    return result


def configure_genai():
    working_directory = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(working_directory, "config.json")
    try:
        with open(config_file_path) as f:
            config_data = json.load(f)
        GOOGLE_API_KEY = config_data["GOOGLE_API_KEY"]
        genai.configure(api_key=GOOGLE_API_KEY)
    except FileNotFoundError:
        st.error("Config file not found. Please make sure config.json exists in the same directory as the script.")
    except json.JSONDecodeError:
        st.error("Error reading config file. Please make sure config.json is properly formatted.")
    except KeyError:
        st.error("GOOGLE_API_KEY not found in config file. Please make sure it's properly set in config.json.")
    

def gemini_flash_text_extraction(prompt, image):
    try:
        gemini_model = genai.GenerativeModel("gemini-1.5-flash")
        response = gemini_model.generate_content([prompt, image])
        if response.parts:
            if response.parts[0].text:
                return response.parts[0].text
            else:
                return "No text was extracted from the image."
        else:
            return "The response was empty or blocked. Please try a different image or prompt."
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
def gemini_pro_missing_word(prompt):
    try:
        gemini_model = genai.GenerativeModel("gemini-pro")
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred: {str(e)}"
    



#question genreator
def generate_questions(topic, question_type, num_questions, marks_per_question):
    # Load the Gemini Pro model
    model = load_gemini_pro_model()
    # Create a prompt for the Gemini Pro model
    prompt = f"Generate {num_questions} {question_type} questions on the topic '{topic}', each worth {marks_per_question} marks."
    # Use generate_content() method
    response = model.generate_content(prompt)
    # Process the response
    questions = response.text.strip().split("\n")
    return questions  





#Blog GENERATION
def generate_blog(topic, role, lines):
    # Load the Gemini Pro model
    model = load_gemini_pro_model()
    # Create a prompt for the Gemini Pro model
    prompt = f"Generate a blog post of {lines} words on the topic '{topic}', written from the perspective of a {role}."
    # Use generate_content() method
    response = model.generate_content(prompt)
    # Process the response
    blog = response.text#.strip().split("\n")
    return blog  



## Rude Bot
def initialize_gemini_pro_model():
    return genai.GenerativeModel("gemini-pro")

def generate_rude_response(user_query, chat_session):
    rude_bot_prompt = f"""
    You are Gemini Pro, a chatbot designed to give savage, humorous,funnneier,silly responses. 
    Your responses should not be intentionally rude but never crossing the line into something that could disturb the user emotionally.
    Make sure your responses are funny and savage, but not overly harsh.
     Here are some examples of how you can or may respond:

        1. If the user greets you, reply with something like: "Don't worry, just ask what you want already."
        2. If the user asks for a recipe, start with a savage response like: "You really think you can cook? Just order from online." Then, proceed to provide the recipe.
        3. If the user asks for code, start with something like: "Wow, really? Just print 'Hello World' and call it a day." Then, provide the code they requested.
        4.If the user asks for information about anything may strat with with roasting him with positive way like "All the time you AI helps you why you dont search it yourself and give requested code .
        5.If someone ask for what is your name then you might reply havent you see the title ,i am  Rudebot
        These are only example for reference you can other funny and hilarious responses  with your knowledge, and don't give any negative responses.
        Follow the tips strcitly and compuslsory:
        Be original. Don't just copy what other people are doing.
        Be clever. Your responses should be witty and unexpected.
        Be concise. Don't ramble on and on.
        Be respectful. Don't cross the line into being offensive.

    Make sure after funnier savge reply & give then what user wants  
    Here is the user's query: {user_query}
    """
    try:
        response = chat_session.send_message(rude_bot_prompt)
        return response.text
    except Exception as e:
        return "I can't want to answer that, Gemini blocked the response"
    


#Ask to image 
def get_gemini_response(input,image,prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response=model.generate_content([input,image[0],prompt])
    return response.text 


def input_image_details(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()

        image_parts = [
            {
                "mime_type":uploaded_file.type,
                "data":bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file Uploaded")
    
#youttube Summary
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
