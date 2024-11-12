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

def translate_text(text, target_language):
    """Translate a single text component if the target language is not English."""
    if target_language != "English":
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"Translate the following text to {target_language}:"},
                    {"role": "user", "content": text}
                ]
            )
            translated_text = response.choices[0].message.content.strip()
            return translated_text
        except Exception as e:
            st.error("Translation error. Falling back to English.")
            return text
    return text

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
             "content": "Imagine you are an expert water conservationist. Provide and list 10 personalized water conservation tips based on the user inputs and climate data. The response should be in a numbered bullet-point format suitable for practical home water management and sustainability planning."},
            {"role": "user",
             "content": prompt}
        ]
    )
    return completion.choices[0].message.content

# Sidebar content
st.sidebar.markdown("# H2Optimize")
language = st.sidebar.selectbox(
    "Choose your language", ["English", "Spanish", "Mandarin", "Cantonese", "Vietnamese"]
)

# Initialize translated text only if language is not English
if language != "English":
    # Combine all text as one formatted block
    combined_text = (
        "Water Conservation Tips Generator\n\n"
        "Welcome to H2Optimize, the AI-powered platform designed to transform your water habits. By analyzing "
        "your household’s unique water usage—from appliance use to daily activities—we provide personalized tips "
        "to help you conserve water effectively. Start conserving today and make every drop count for a sustainable future!\n\n"
        "This application was created for Santa Clara County locations.\n\n"
        "Select the city you are located in:\n\n"
        "How many people are in the household?\n\n"
        "Appliance usage (e.g., washing machine, dishwasher, water softener, etc.)\n\n"
        "Water features (e.g., garden, hot tub, swimming pool, etc.)\n\n"
        "Describe showering, bathtub, and toilet usage\n\n"
        "How many times do you wash your car?\n\n"
        "Enter the year (e.g., 2024):\n\n"
        "Enter the month (1-12):\n\n"
        "Submit"
    )

    # Translate all text in one API call
    translated_combined_text = translate_text(combined_text, language)

    # Check if translation was successful
    if translated_combined_text and "Water Conservation" not in translated_combined_text:
        # Split by double newlines
        translated_parts = translated_combined_text.split("\n\n")
        if len(translated_parts) >= 12:  # Ensure enough parts for all labels
            header = translated_parts[0]
            welcome_message = translated_parts[1]
            location_message = translated_parts[2]
            location_label = translated_parts[3]
            household_size_label = translated_parts[4]
            appliances_label = translated_parts[5]
            water_features_label = translated_parts[6]
            showering_usage_label = translated_parts[7]
            car_wash_label = translated_parts[8]
            input_year_label = translated_parts[9]
            input_month_label = translated_parts[10]
            submit_label = translated_parts[11]
        else:
            st.error("Translation error. Falling back to English.")
            language = "English"
    else:
        language = "English"

# Default English labels if translation failed or English is selected
if language == "English":
    header = "Water Conservation Tips Generator"
    welcome_message = ("Welcome to H2Optimize, the AI-powered platform designed to transform your water habits. "
                       "By analyzing your household’s unique water usage—from appliance use to daily activities—we "
                       "provide personalized tips to help you conserve water effectively. Start conserving today and "
                       "make every drop count for a sustainable future!")
    location_message = "This application was created for Santa Clara County locations."
    location_label = "Select the city you are located in:"
    household_size_label = "How many people are in the household?"
    appliances_label = "Appliance usage (e.g., washing machine, dishwasher, water softener, etc.)"
    water_features_label = "Water features (e.g., garden, hot tub, swimming pool, etc.)"
    showering_usage_label = "Describe showering, bathtub, and toilet usage"
    car_wash_label = "How many times do you wash your car?"
    input_year_label = "Enter the year (e.g., 2024):"
    input_month_label = "Enter the month (1-12):"
    submit_label = "Submit"

# Page content for Water Conservation Tips Generator
st.markdown(f"# {header}")
st.write(welcome_message)
st.write(location_message)

# Form for user inputs
with st.form(key="water_habits_form"):
    location = st.selectbox(location_label, ["Choose a city"] + santa_clara_cities)
    household_size = st.number_input(household_size_label, min_value=1, step=1)
    appliances = st.text_input(appliances_label)
    water_features = st.text_input(water_features_label)
    showering_usage = st.text_input(showering_usage_label)
    car_wash = st.text_input(car_wash_label)
    input_year = st.number_input(
        input_year_label, min_value=2024, max_value=datetime.now().year, step=1
    )
    input_month = st.number_input(input_month_label, min_value=1, max_value=12, step=1)

    submitted = st.form_submit_button(submit_label)

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
        st.write("Personalized Water Conservation Tips:")
        st.write(tips)