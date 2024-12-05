import os
import streamlit as st 
from streamlit_option_menu import option_menu
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from urllib.parse import urlparse, parse_qs
import google.generativeai as genai



from gemini_utility import (load_gemini_pro_model,
                            gemini_pro_vision_response,
                            embedding_model_reponse,
                            gemini_pro_response,
                            configure_genai,
                            gemini_flash_text_extraction,
                            gemini_pro_missing_word,
                            generate_questions,
                            generate_blog,
                            initialize_gemini_pro_model,
                            #generate_gemini_pro_response,
                            generate_rude_response,
                            get_gemini_response,
                            input_image_details,
                            load_config,
                            extract_video_id,
                            extract_transcript_details,
                            generate_gemini_content
                          
                            )
from PIL import Image

working_directory= os.path.dirname(os.path.abspath(__file__))
print(working_directory)
#page configuration

st.set_page_config(
    page_title = "Gemini AI",
    page_icon = "🧠",
    layout='centered'
)
with st.sidebar:
    selected = option_menu(menu_title='Gemini AI',
                           options=['ChatBot',
                           'Image Captioning',                            
                           'Text Restoration Of Degreaded Images',
                           'Question Generator',
                           'Blog Generator',
                           'Rude Bot',
                           'Ask To Image',
                           'Youtube Video Summarizer',
                           'Embed Text',
                           'Ask me anything'],
                           menu_icon = 'robot',
                           icons=['robot','image-fill','textarea-t','question','bookmarks','robot','image-alt','youtube','textarea-t','patch-question-fill'],
                           default_index=5)
    
#function to translate terminolgy between gemini pro and streamlit

def translate_role_for_streamlit(user_role):
    if user_role == 'model':
        return "assistant"
    else:
        return user_role

if selected == 'ChatBot':
    model = load_gemini_pro_model()
    #initalize chat session in streamlit if not allready present
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = model.start_chat(history=[])

    #streamlit page title
    st.title('🤖ChatBot')

    #TO DISPLAY CHAT HISTORY
    for message in st.session_state.chat_session.history:
        with st.chat_message(translate_role_for_streamlit(message.role)):
            st.markdown(message.parts[0].text)

    #input filed for user meassage
    user_prompt=st.chat_input("Ask Gemin Pro..")

    if user_prompt:
        st.chat_message("user").markdown(user_prompt)

        gemini_response =st.session_state.chat_session.send_message(user_prompt)

        #display gemini response
        with st.chat_message("assistant"):
            st.markdown(gemini_response.text)


#Image Captioning 
if selected == 'Image Captioning':
    st.title("📸Snap Narate")

    uploaded_image = st.file_uploader("Upload an image...",type=["jpg","jpeg","png"])
    if st.button("Generate Caption"):
        # Open the image
        image = Image.open(uploaded_image)

        col1,col2 = st.columns(2)
        with col1:
            resized_image = image.resize((800,500))
            st.image(resized_image)
        defualt_prompt = " Generate two or more good attractive small and sweet  Captions for the image in 4 to 5 lines Remember to add relevant hashtags to increase visibility "

        # Get the caption output from model 
        caption = gemini_pro_vision_response(defualt_prompt, image)
        with col2:
            st.info(caption)

#Youtube Video Summarizer 
if selected == 'Youtube Video Summarizer':
   
    prompt = """Summarize the key points and insights from this video content. Focus on the main ideas, concepts, and important takeaways. Structure the summary to include:

    1. Main topic and core message
    2. Key points covered
    3. Important examples or case studies
    4. Practical takeaways or conclusions

    Make the summary clear, concise, and easy to understand. Keep it informative and engaging while maintaining accuracy to the original content.

    Transcript text:"""
# Streamlit UI

    st.title("📽️YouTube Transcript Summarizer")
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



#text restration for distorted image
if selected == 'Text Restoration Of Degreaded Images':
    configure_genai()
    #st.set_page_config(page_title="Text Extraction & Analysis", page_icon="📚", layout='centered')
    
    st.title("📝 Text Restoration of Degraded Historic  Images")    
    uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_image:
        col1, col2 = st.columns([1, 1])
        with col1:
            image = Image.open(uploaded_image)
            resized_image = image.resize((400, 300))
            st.image(resized_image, caption="Uploaded Image")

        if st.button("Process Image"):
            with st.spinner("Processing..."):
                # Extract Text
                default_prompt =  """You are an expert in text extraction from degraded historical images. Extract all readable text, using '__' for unclear or noisy areas. Return everything you can extract, even if some parts are illegible. For severely blurred sections, leave blank spaces marked with '___'."""
                extracted_text = gemini_flash_text_extraction(default_prompt, image)
                
                with col2:
                    st.subheader("📄 Extracted Text")
                    st.write(extracted_text)

                # Missing Word Analysis
                st.subheader("✨ Restored Text")
                context_prompt = f""" You are an expert in analyzing text and predictiong missing words .Analyze this extracted text: '{extracted_text}'
                    
                1. Check for missing/unclear words marked with '__' or '___'
                2. Fix any spelling or typing errors
                3. Fill blanks by analyzing context and surrounding words
                4. Format output:
                - If no issues: "Text is complete and clear: [original text]"
                - If corrections needed: Show restored text with changes in **asterisks**"""
                restored_text = gemini_pro_missing_word(context_prompt)
                st.write(restored_text)
                
                st.subheader("🔄 Changes Made")
                changes_prompt = f"Compare the following two texts and list only the changes made (words corrected, added, or modified). Original text: '{extracted_text}' Modified text: '{restored_text}'"
                changes = gemini_pro_missing_word(changes_prompt)
                st.write(changes)



#Quetion paper generator
if selected == 'Question Generator':
        # Streamlit UI
    st.title("❓Question Paper Generator")
    # Input fields for topic, question type, number of questions, and marks per question
    topic = st.text_input("Enter Topic:", "Artificial Intelligence")
    question_type = st.selectbox("Select Question Type:", ["MCQ", "Short Answer", "Long Answer"])
    num_questions = st.number_input("Number of Questions:", min_value=1, max_value=50, value=5)
    marks_per_question = st.number_input("Marks per Question:", min_value=1, max_value=20, value=1)

    # Generate button
    if st.button("Generate Questions"):
        with st.spinner("Generating questions..."):
            questions = generate_questions(topic, question_type, num_questions, marks_per_question)
        
        # Display generated questions
        if questions:
            st.success("Questions Generated Successfully!")
            for question in questions:
                st.write(question)
        else:
            st.error("No questions were generated.")


#Blog Generator 

if selected == 'Blog Generator':
    st.title("Blog Generator🧾")
    topic =st.text_input("Enter the Topic","Artificial Intelligence")
    role = st.selectbox("Select The Role:", ["Student", "Teacher", "Professional","Scientist"])
    lines = st.number_input("Enter the number of Lines", min_value=50, max_value=500, value=100)
    if st.button('Generate Blog📝'):
        with st.spinner("Generating Blog..."):
            blog = generate_blog(topic, role, lines)
        
        if blog:
            st.success("Questions Generated Successfully!📍")
            
            st.write(blog)
        else:
            st.error("Enable to crete a blog.")






def translate_role_for_streamlit(role):
    return "assistant" if role == "model" else "user"

if selected == 'Rude Bot':
    st.title('😎RudeBot')
    
    # Initialize model and chat session
    if "gemini_model" not in st.session_state:
        st.session_state.gemini_model = initialize_gemini_pro_model()
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle user input
    user_query = st.chat_input("Ask Gemini Pro..")
    if user_query:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # Generate and display response
        response = generate_rude_response(user_query, st.session_state.gemini_model.start_chat())
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)


if selected == 'Ask To Image':
    st.header("Ask about image🖼️")

    uploaded_file = st.file_uploader("🔼Choose an image ...",type=["jpg","jpeg","png"])
    image=""
    if uploaded_file is not None:
        image=Image.open(uploaded_file)
        st.image(image,caption="Uploaded Image",use_column_width=True)
    input = st.text_input("Input Prompt: ", key=input)
    submit = st.button("Tell me about the image")

    input_prompt = """
    As an expert in image analysis, your task is to thoroughly examine the uploaded image and provide detailed insights based on the following:

    Object Identification: Identify all visible objects, their attributes (e.g., color, size, shape, texture, and position), and relationships between them.
    Text Recognition: Extract and interpret any text within the image, noting its content, context, font, and placement.
    Contextual Understanding: Provide a comprehensive description of the scene, including relevant context, objects, and any other notable details.
    You will then respond to the user’s query, using the information extracted from the image to provide an accurate and detailed answer. The user may ask any question related to the image, and you should tailor your response to the query while referencing relevant image details
    Answer with precision and clarity based on the image content.
    """

    if submit:
        image_data = input_image_details(uploaded_file)
        respose= get_gemini_response(input_prompt,image_data,input)
        st.subheader("The Response is")
        st.write(respose)




#text embedding text
if selected == 'Embed Text':
    st.title("🔠Embed Text")
    #input text box
    input_text=st.text_area(label="",placeholder="Enter the text to get embeddings")

    if st.button("Get Embedding"):
        response= embedding_model_reponse(input_text)
        st.markdown(response)

#ask me question
if selected == 'Ask me anything':
    st.title("❓Ask me Question")
    #textbox to enter the prompt
    user_prompt = st.text_area(label="",placeholder="Ask me Anything !")
    if st.button("Get an Answer"):
        response = gemini_pro_response(user_prompt)
        st.markdown(response)
