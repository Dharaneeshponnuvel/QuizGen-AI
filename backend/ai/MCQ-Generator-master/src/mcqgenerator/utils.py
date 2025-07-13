import os 
import traceback
import PyPDF2
import json

def read_file(file):
    if file.name.endswith(".pdf"):
        try:
            pdf_reader = PyPDF2.PdfFileReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
                return text
        
        except Exception as e:
            raise Exception('Error reading the PDF file')
    
    elif file.name.endswith(".txt"):
        return file.read().decode('utf-8')
    
    else:
        raise Exception(
            'Unsupported file format only PDF and Text file supported.'
        )


def get_table_data(quiz_str):
    try:
        # Accept both dict and str input
        if isinstance(quiz_str, dict):
            quiz_dict = quiz_str
        elif isinstance(quiz_str, str):
            try:
                quiz_dict = json.loads(quiz_str)
            except Exception:
                # If it's already a string but not JSON, return error
                print("get_table_data: Input string is not valid JSON.")
                return False
        else:
            print(f"get_table_data: Unsupported input type: {type(quiz_str)}")
            return False

        quiz_table_data = []
        # iterating over the quiz dictionary and extracting the required information
        for key, value in quiz_dict.items():
            try:
                mcq = value['mcq']
                options = " || ".join([
                    f"{option} -> {option_value}" for option, option_value in value['options'].items()
                ])
                correct = value['correct']
                quiz_table_data.append({'MCQ': mcq, 'Choices': options, 'Correct': correct})
            except Exception as e:
                print(f"get_table_data: Error parsing MCQ item: {e}, value: {value}")
                continue
        if not quiz_table_data:
            print("get_table_data: No valid MCQs found in input.")
            return False
        return quiz_table_data
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return False
    