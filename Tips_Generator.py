import os
import openai
import streamlit as st
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.environ["OPENAI_API_KEY"]

# Load the climate data
climate_data = pd.read_csv('sc_avgtemp.csv')

# Map month names to numbers
month_map = {
    'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
    'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
}
climate_data['Month'] = climate_data['Month'].map(month_map)

# List of Santa Clara County cities
santa_clara_cities = [
    "Campbell", "Cupertino", "Gilroy", "Los Altos", "Los Altos Hills",
    "Los Gatos", "Milpitas", "Monte Sereno", "Morgan Hill", "Mountain View",
    "Palo Alto", "San Jose", "Santa Clara", "Saratoga", "Sunnyvale"
]

st.sidebar.image("logo/group_logo.png", use_column_width=True)

st.sidebar.markdown("# H2Optimize")
language = st.sidebar.selectbox("Select your language", ["English", "Spanish", "Mandarin", "Cantonese", "Vietnamese"])

# Function to translate multiple labels in a single call
def translate_labels(labels, target_language):
    if target_language == "English":  # Skip translation if English is selected
        return labels

    labels_text = "\n".join(labels.values())
    translation_prompt = f"Translate the following text to {target_language}:\n{labels_text}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", 
             "content": f"You are a helpful assistant that translates text to {target_language}."},
            {"role": "user",
             "content": translation_prompt}
        ]
    )
    
    # Split the response by lines and map back to labels
    translated_text = response.choices[0].message.content.split("\n")
    return dict(zip(labels.keys(), translated_text))

# Function to translate a single text block (for the tips)
def translate_text(text, target_language):
    if target_language == "English":  # Skip translation if English is selected
        return text
    
    translation_prompt = f"Translate the following text to {target_language}:\n{text}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", 
             "content": f"You are a helpful assistant that translates text to {target_language}."},
            {"role": "user",
             "content": translation_prompt}
        ]
    )
    return response.choices[0].message.content

# Define default labels and translate if necessary
labels = {
    "header": "Water Conservation Tips Generator",
    "welcome_message": "Welcome to H2Optimize, the AI-powered platform designed to transform your water habits. "
                   "By analyzing your household’s unique water usage—from appliance use to daily activities—we "
                   "provide personalized tips to help you conserve water effectively. Start conserving today and "
                   "make every drop count for a sustainable future!",
    "location_message": "This application was created for Santa Clara County locations.",
    "location_label": "Select the city you are located in:",
    "choose_city_option": "Choose a city",  # Add "Choose a city" option to labels for translation
    "household_size_label": "How many people are in the household?",
    "appliances_label": "Appliance usage (e.g., washing machine, dishwasher, water softener, etc.)",
    "water_features_label": "Water features (e.g., garden, hot tub, swimming pool, etc.)",
    "showering_usage_label": "Describe showering, bathtub, and toilet usage",
    "car_wash_label": "How many times do you wash your car?",
    "input_year_label": "Enter the year (e.g., 2024):",
    "input_month_label": "Select the month:",
    "submit_label": "Submit"
}

labels = translate_labels(labels, language)

# Function to find the closest match for a given year and month
def get_closest_month_year(avg_temp_data, input_year, input_month):
    month_data = avg_temp_data[avg_temp_data['Month'] == input_month]
    if not month_data[month_data['Year'] == input_year].empty:
        closest_row = month_data[month_data['Year'] == input_year].iloc[0]
    else:
        closest_row = month_data.sort_values(by='Year').iloc[0]
    return closest_row['Avg Temp'], closest_row['Year'], closest_row['Month']

# Function to get climate data from the CSV file based on user input
def get_climate_data_from_csv(input_year, input_month):
    if not climate_data.empty:
        avg_temp, closest_year, closest_month = get_closest_month_year(climate_data, input_year, input_month)
        if closest_year is not None:
            print(f"Note: Found closest data for {int(closest_year)}-{int(closest_month):02d} with Avg Temp: {avg_temp}")
            return f"Average Temperature for {int(closest_year)}-{int(closest_month):02d}: {avg_temp}"
        else:
            print("Note: No valid past data found in the dataset.")
            return "Climate data for the selected month and year is not available."
    else:
        print("Note: No data found in the dataset.")
        return "Climate data for the selected month and year is not available."

# Create a function to generate water conservation tips
def get_completion(prompt, model="gpt-3.5-turbo"):
    completion = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system",
             "content": "Imagine you are an expert water conservationist. Review the given user inputs and state the areas that need to be improved.\
                Provide and list 10 personalized water conservation tips that are based on the user inputs and climate data. Ensure that the tips are\
                relatively short, but still percise and clear. The response should be in a numbered\
                bullet-point format suitable for practical home water management and sustainability planning. For example, first you tell the user the\
                areas that need to be improved and then list the 10 personalized water conservation tips. Make sure to highlight the bigger headers that\
                separate the two sections, such as Areas that Need Improvement and Personalized Water Conservation Tips for the selected city."},
            {"role": "user",
             "content": prompt}
        ]
    )
    return completion.choices[0].message.content

# Cache for translated months to reduce API calls
translated_month_cache = {}

# Function to get translated month names, minimizing API calls
def get_translated_months(target_language):
    if target_language == "English":
        return list(month_map.keys())  # Return the default English month names
    
    # Check if the months for the selected language are already cached
    if target_language in translated_month_cache:
        return translated_month_cache[target_language]
    
    # Translate the month names if not cached
    month_names = list(month_map.keys())
    translated_month_names = translate_text("\n".join(month_names), target_language)
    translated_month_list = translated_month_names.split("\n")
    
    # Cache the result for future use
    translated_month_cache[target_language] = translated_month_list
    
    return translated_month_list

# Get the translated month names
translated_month_names = get_translated_months(language)
month_map_translated = dict(zip(translated_month_names, month_map.values()))  # Update month_map with translated names

# Page content for Water Conservation Tips Generator
st.markdown(f"# {labels['header']}")
st.write(labels['welcome_message'])
st.write(labels['location_message'])

# Form for user inputs
with st.form(key="water_habits_form"):
    location = st.selectbox(labels["location_label"], [labels["choose_city_option"]] + santa_clara_cities)
    household_size = st.number_input(labels["household_size_label"], min_value=1, step=1)
    appliances = st.text_input(labels["appliances_label"])
    water_features = st.text_input(labels["water_features_label"])
    showering_usage = st.text_input(labels["showering_usage_label"])
    car_wash = st.text_input(labels["car_wash_label"])
    input_year = st.number_input(
        labels["input_year_label"], min_value=2024, max_value=datetime.now().year, step=1
    )
    input_month_name = st.selectbox(labels["input_month_label"], list(month_map_translated.keys()))  # Translated month names

    submitted = st.form_submit_button(labels["submit_label"])

# Convert selected month name to its corresponding number for further processing
input_month = month_map_translated[input_month_name]

if submitted:
    if location == "Choose a city":
        st.error("Please select a valid city to continue.")
    else:
        # Continue with processing only if a valid city is chosen
        climate_data_info = get_climate_data_from_csv(int(input_year), int(input_month))
        user_inputs = f"""
        Location: {location}
        Household size: {household_size}
        Appliances: {appliances}
        Water features: {water_features}
        Climate Data: {climate_data_info}
        Showering/bathroom usage: {showering_usage}
        Car wash frequency: {car_wash}
        """
        tips = get_completion(user_inputs)

        # Translate tips if language is not English
        if language != "English":
            translated_tips = translate_text(tips, language)
        else:
            translated_tips = tips

        # Display the translated header
        st.write(translated_tips)
