import os
import openai
import streamlit as st
from PIL import Image
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Streamlit App Title
st.markdown("# Water Conservation Visualizer")
message = "Generate custom visuals with our AI-powered image tool. Simply input a water conservation tip or keyword to create a unique visual representation."
st.write(message)

# Set up the OpenAI API key
openai.api_key = os.environ["OPENAI_API_KEY"]  # Store your API key in an .env file

def download_image(filename, url):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)
        return filename
    else:
        print("Error downloading image from URL:", url)
        return None

def filename_from_input(prompt):
    # Clean the prompt to create a filename
    alphanum = "".join([char if char.isalnum() or char == " " else "" for char in prompt])
    alphanumSplit = alphanum.split()[:3]  # Use the first three words
    return "images/" + "_".join(alphanumSplit) + ".png"

# Generate an image using OpenAI's DALL-E
def get_image(prompt, model="dall-e-2"):
    try:
        response = openai.Image.create(
            prompt=prompt,
            model=model,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        
        # Ensure the 'images' directory exists
        Path("images").mkdir(exist_ok=True)

        # Save the image locally
        filename = str(Path(__file__).parent / filename_from_input(prompt))
        downloaded_filename = download_image(filename, image_url)
        
        if downloaded_filename:
            return downloaded_filename
        else:
            print("Failed to download image.")
            return None
    except Exception as e:
        print(f"Error generating image: {e}")
        return None

# Create a form for input
with st.form(key="chat"):
    prompt = st.text_input('Enter Water Conservation Tip or Keyword')
    submitted = st.form_submit_button("Submit")
    
    if submitted:
        image_path = get_image(prompt)
        if image_path and Path(image_path).exists():
            image = Image.open(image_path)
            st.image(image, caption='Generated Image for Conservation Tip')
        else:
            st.error("Failed to generate or retrieve the image.")
