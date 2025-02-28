Project leverages the power of Google's Gemini Generative AI models to achieve diverse functionalities, showcasing the versatility of generative AI. Here's how the different Gemini models and generative AI capabilities are used in your project:

Key Functionalities:
1.ChatBot
Interactive chatbot using the gemini_pro_model.
Maintains a chat history and handles user queries with intelligent responses.

2.Image Captioning
Users can upload images, and the system generates captions using gemini_pro_vision_response.

3.YouTube Video Summarizer
Extracts transcripts from YouTube videos and generates a detailed summary based on predefined prompts.

4.Text Restoration of Degraded Images
Extracts text from degraded images and attempts to restore it to readable form, analyzing and correcting unclear or missing words.

5.Question Paper Generator
Generates questions of a specified type (MCQ, Short Answer, Long Answer) for a given topic, including marks allocation.

6.Blog Generator
Creates blogs tailored to specific topics and roles, like "Student" or "Professional," with user-defined lengths.

7.Rude Bot
A playful chatbot variant that provides "rude" or humorous responses based on user queries.

8.Ask To Image
Users can upload images and ask questions about their content. The app analyzes the image to provide detailed responses.

9.Embed Text
Converts input text into embeddings using a model for downstream tasks.

10.Ask Me Anything
Provides an open-ended query interface for asking questions unrelated to other functionalities.

Code Structure Observations:
Gemini Utilities:
Centralized utility functions from gemini_utility handle model interactions, responses, and content generation.

Streamlit Pages:
The app dynamically switches between functionalities based on the selected menu option.

Prompts Design:
Prompts are designed to elicit detailed and context-specific outputs from the AI models.

API Key Configuration:
API key for google.generativeai is loaded via load_config().

Error Handling:
The app includes basic error handling for tasks like loading thumbnails and missing configurations.
