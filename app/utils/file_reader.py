# File: app/utils/file_reader.py

import os
import pdfplumber # Make sure pdfplumber is installed: pip install pdfplumber
from docx import Document # Make sure python-docx is installed: pip install python-docx
import traceback

def extract_text_from_raw(file_path: str, ext: str) -> str:
    """
    Reads a file from the given path and extracts text content based on its extension.

    Args:
        file_path: The path to the temporary file provided by Gradio.
        ext: The file extension (e.g., '.pdf', '.docx', '.txt').

    Returns:
        The extracted text as a string, or an empty string if extraction fails.
    """
    text = ""
    file_basename = os.path.basename(file_path)
    print(f"Attempting to extract text from: {file_basename} (type: {ext})")

    try:
        if ext == '.pdf':
            # Use pdfplumber directly with the file path
            with pdfplumber.open(file_path) as pdf:
                all_pages_text = [page.extract_text() or "" for page in pdf.pages]
                text = "\n".join(all_pages_text)
            print(f"Extracted {len(text)} characters from PDF: {file_basename}")

        elif ext == '.docx':
            # Use python-docx directly with the file path
            document = Document(file_path)
            all_paras_text = [p.text for p in document.paragraphs]
            text = "\n".join(all_paras_text)
            print(f"Extracted {len(text)} characters from DOCX: {file_basename}")

        elif ext == '.txt':
            # Try reading with utf-8, fallback to latin-1
            try:
                with open(file_path, 'r', encoding='utf-8') as txt_file:
                    text = txt_file.read()
            except UnicodeDecodeError:
                print(f"Warning: UTF-8 decoding failed for {file_basename}. Trying 'latin-1'.")
                try:
                    with open(file_path, 'r', encoding='latin-1') as txt_file:
                         text = txt_file.read()
                except Exception as e_enc:
                     print(f"Error reading text file {file_basename} with fallback encoding: {e_enc}")
                     text = "" # Ensure text is empty on failure
            print(f"Extracted {len(text)} characters from TXT: {file_basename}")

        else:
            print(f"Warning: Unsupported file extension '{ext}' for file: {file_basename}")
            text = "" # Return empty string for unsupported types

    except FileNotFoundError:
        print(f"Error: File not found at path: {file_path}")
        text = ""
    except Exception as e:
        # Catch other potential errors during file reading/parsing
        print(f"Error extracting text from {file_basename} ({ext}): {e}")
        traceback.print_exc()
        text = "" # Return empty string on error

    # Basic cleanup (optional) - remove extra whitespace
    if text:
        cleaned_lines = [line.strip() for line in text.splitlines() if line.strip()]
        text = '\n'.join(cleaned_lines)

    if not text:
         print(f"Warning: No text could be extracted from {file_basename}")

    return text