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
message = (
    "Generate custom visuals with our AI-powered image tool followed by some tips. "
    "Simply input a water conservation tip or keyword to create a unique visual representation."
)
st.write(message)

# Set up the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")  # Use `os.getenv` for better error handling

# Helper function to download an image from a URL
def download_image(filename, url):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)
        return filename
    else:
        print("Error downloading image from URL:", url)
        return None

# Helper function to create a filename from the input prompt
def filename_from_input(prompt):
    # Clean the prompt to create a filename
    alphanum = "".join([char if char.isalnum() or char == " " else "" for char in prompt])
    alphanum_split = alphanum.split()[:3]  # Use the first three words
    return "images/" + "_".join(alphanum_split) + ".png"

# Generate an image using OpenAI's DALL-E
def get_image(prompt, model="dall-e-2"):
    try:
        response = openai.Image.create(
            prompt=prompt,
            model=model,
            n=1,
            size="512x512"
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

# Generate water conservation tips using GPT
def get_completion(prompt, model="gpt-3.5-turbo"):
    try:
        completion = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system",
                 "content": "Imagine you are an expert water conservationist. Provide and list 10 personalized water conservation tips based on the user inputs and climate data. The response should be in a numbered bullet-point format suitable for practical home water management and sustainability planning."},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error generating tips: {e}")
        return "Could not generate tips at this time. Please try again later."

# Create a form for user input
with st.form(key="chat"):
    prompt = st.text_input('Enter Water Conservation Tip or Keyword')
    submitted = st.form_submit_button("Submit")
    
    if submitted:
        # Generate and display the image
        st.markdown("### Generated Image")
        image_path = get_image(prompt)
        if image_path and Path(image_path).exists():
            image = Image.open(image_path)
            st.image(image, caption='Generated Image for Conservation Tip')
        else:
            st.error("Failed to generate or retrieve the image.")
        
        # Generate and display the tips
        st.markdown("### Water Conservation Tips:")
        tips = get_completion(prompt)
        if tips:
            st.markdown(tips)
        else:
            st.error("Failed to generate tips.")
