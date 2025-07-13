import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
from src.mcqgenerator.utils import read_file, get_table_data
from src.mcqgenerator.MCQGenerator import generate_evaluate_chain
from src.mcqgenerator.logger import logging

# Load environment variables
load_dotenv()

# Load the JSON response structure
with open(r'D:\quize\backend\ai\MCQ-Generator-master\Response.json', 'r') as file:
    RESPONSE_JSON = json.load(file)

# App title
st.title('🧠 MCQ Generator with OpenRouter + Langchain')

# Streamlit form
with st.form('user_inputs'):
    uploaded_file = st.file_uploader('📄 Upload a PDF or TXT file')
    mcq_count = st.number_input('🔢 No. of MCQs', min_value=3, max_value=50)
    subject = st.text_input('📚 Subject', max_chars=40)
    tone = st.text_input('🎯 Complexity Level (Tone)', max_chars=20, placeholder='Simple')
    button = st.form_submit_button('🚀 Generate MCQs')

    if button and uploaded_file is not None and mcq_count and subject and tone:
        with st.spinner('🧠 Generating MCQs using AI...'):
            try:
                text = read_file(uploaded_file)

                # Call the LangChain-based generator
                response = generate_evaluate_chain(
                    {
                        'text': text,
                        'number': mcq_count,
                        'subject': subject,
                        'tone': tone,
                        'response_json': json.dumps(RESPONSE_JSON)
                    }
                )

            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error('❌ Error during MCQ generation.')

            else:
                if isinstance(response, dict):
                    quiz = response.get('quiz')
                    if quiz:
                        print("DEBUG: Raw quiz value:", quiz)
                        table_data = get_table_data(quiz)

                        # Debugging info
                        print("DEBUG: Type of table_data:", type(table_data))
                        print("DEBUG: Sample table_data:", table_data[:1] if isinstance(table_data, list) else table_data)

                        # Try to parse if table_data is a string (e.g., JSON)
                        if table_data and isinstance(table_data, str):
                            try:
                                table_data = json.loads(table_data)
                                print("DEBUG: Parsed table_data as JSON:", table_data)
                            except Exception as e:
                                print("DEBUG: Failed to parse table_data as JSON:", e)

                        if table_data and isinstance(table_data, list):
                            df = pd.DataFrame(table_data)
                            df.index = df.index + 1
                            st.subheader("📋 Generated MCQs")
                            st.table(df)

                            st.subheader("📝 AI's Review")
                            st.text_area(label='Review', value=response.get('review', ''), height=150)
                        else:
                            st.error(f'⚠️ Could not parse quiz into table format. Type: {type(table_data)}, Value: {str(table_data)[:300]}')
                    else:
                        st.error('⚠️ No quiz data returned.')
                else:
                    st.warning('Unexpected response format received:')
                    st.write(response)
