from argparse import RawTextHelpFormatter
import requests
from typing import Optional
import warnings
import streamlit as st
from langflow.load import run_flow_from_json
import os
from dotenv import load_dotenv
load_dotenv()


BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "e0156070-00ea-46a8-a1d6-8412034b3ae4"
FLOW_ID = "938ad8fc-d6a7-45e7-ae5b-830ff89d7ad6"
APPLICATION_TOKEN = os.environ.get("APP_TOKEN")
ENDPOINT = "designer" # The endpoint name of the flow

# def run_flow(design):
#     TWEAKS = {
#     "TextInput-e0vrw": {
#         "input_value": design
#         },
#     }

#     result = run_flow_from_json(flow="DESIGNER.json",
#                                 input_value="message",
#                                 fallback_to_env_vars=True, # False by default
#                                 tweaks=TWEAKS)
#     return result
def run_flow(message: str) -> dict:

    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{ENDPOINT}"

    payload = {
        "input_value": message,
        "output_type": "text",
        "input_type": "text",
    }
    headers = {"Authorization": "Bearer " + APPLICATION_TOKEN, "Content-Type": "application/json"}
    response = requests.post(api_url, json=payload, headers=headers)
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}


st.title("UX Design AI Assistant")

if not APPLICATION_TOKEN:
    st.error(
        "Please set the `APP_TOKEN` environment variable to your Langflow Application Token."
    )
else:
    user_input = st.text_area(
        "Enter your design idea or question for the UX AI:",
        placeholder="e.g., I want to design a mobile app for language learning...",
        height=150,
    )

    if st.button("Run AI Analysis"):
        if not user_input:
            st.warning("Please enter some text for the AI to process.")
        else:
            with st.spinner("Running AI analysis..."):
                result = run_flow(user_input)

                if "error" in result:
                    st.error(f"Error from Langflow API: {result['error']}")
                elif "outputs" in result and result["outputs"]:
                    # Assuming the text output is in the first output of the first output group
                    try:
                        ai_output_text = result["outputs"][0]["outputs"][0]["results"]["text"]["text"]
                        st.subheader("AI Analysis Output:")
                        st.markdown(ai_output_text)  # Use st.markdown to render markdown
                    except (KeyError, IndexError, TypeError):
                        st.error("Could not extract text output from API response. Check the API response format.")
                        st.json(result) # Display the raw JSON response for debugging
                else:
                    st.warning("No output received from the AI. Check your Langflow flow.")
                    st.json(result) # Display the raw JSON response for debugging