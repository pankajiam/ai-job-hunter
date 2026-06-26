# modules/resume_parser.py
import pdfplumber
import os

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Takes the path of a PDF file and returns all the text inside it.
    """
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        text = f"Error reading PDF: {str(e)}"
    return text.strip()


def save_uploaded_file(uploaded_file) -> str:
    """
    Saves a Streamlit uploaded file to the uploads/ folder.
    Returns the file path where it was saved.
    """
    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path