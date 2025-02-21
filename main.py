import json
from xai_assistant_cls import XAIAssistant
from icecream import ic
import streamlit as st
import os
import datetime
import uuid
from utils import clean_latex_formatting, save_state_json
from welcome import welcome_page
#from survey import survey
from german_survey import survey
from chat import chat_page
from images import get_images
from decision_popover import decision
from thanks import thank_you_page
from config import ASSISTANT_ID
from images import save_upload_images
from sciebo_uploader import Sciebo


def initialize(image_path):
    if "user_uuid" not in st.session_state:
        #set_page_styling()
        user_uuid = str(uuid.uuid4())
        start_time = datetime.datetime.now().isoformat()

        if not "assistant" in st.session_state:
            if os.environ.get("SMOKE_TEST"):
                st.session_state["assistant"] = None
            else:
                st.session_state["assistant"] = XAIAssistant(assistant_id=ASSISTANT_ID)
            # Initialize the assistant
            survey_data = st.session_state.get("survey", {})
            st.session_state["assistant"].frame_with_survey_data(survey_data)

        assistant = st.session_state["assistant"]
        print(f'Selected Image path during AI intialization: {image_path}')

        assistant_response = assistant.initialize_assistant(image_path)
        # Store the assistant's response or any other relevant information in the session state
        st.session_state["user_uuid"] = user_uuid
        st.session_state["start_time"] = start_time
        st.session_state["assistant_response"] = assistant_response
        st.session_state["saved_image"] = image_path

        #save_state_json()


def main():
    if "page" not in st.session_state:
        st.session_state["page"] = "welcome"

    if st.session_state["page"] == "welcome":
        welcome_page()

    elif st.session_state["page"] == "survey":
        survey()
        save_state_json()
    elif st.session_state["page"] == "chat":
        survey_data = st.session_state.get("survey", {})
        skin_color = survey_data.get("skin_color", "default")  # Assuming "skin_color" is the key for the skin color data
        image_path = get_images(skin_color)
        with st.container():
                print('Inside chat page container with only title , header and image uploader')
                st.title("🤖 Medical Diagnostic Assistant")
                #col1, col2 = st.columns([1, 1]) #making two columns one for image upload and one for camera input
                st.subheader("Diagnose your skin condition with the Medical Assistant", divider="gray")
                 #this is a placeholder for image upload
                st.session_state["saved_image"]=image_path  #update state.saved_image with image path
                initialize(image_path)  #Pass the image path during initialization
                decision() #this loads the chat and buttons
        chat_page()
        save_state_json()

    elif st.session_state["page"] == "thanks":
        image_path = st.session_state["saved_image"]
        uuid = st.session_state.get("user_uuid")
        Sciebo.upload_image(image_path,uuid)
        Sciebo.upload_state_data(uuid)
        save_state_json()
        thank_you_page()


if __name__ == "__main__":
    main()
