# document_parser.py

import os
import pdfplumber
import docx
import pandas as pd
from pptx import Presentation
from PIL import Image
from io import BytesIO
import pytesseract
import fitz  # PyMuPDF

import shutil  # Add this import at the top

def process_file(file_path, document_type):
    ext = os.path.splitext(file_path)[-1].lower()
    output_folder = "extracted_data"

    # 🧹 Clear old extracted data
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)  # Delete the entire folder and its contents
    os.makedirs(output_folder, exist_ok=True)

    txt_file_path = os.path.join(output_folder, os.path.basename(file_path).replace(ext, ".txt"))
    extracted_images = []


    if ext == ".pdf":
        extracted_images = extract_text_and_images_from_pdf(file_path, txt_file_path, output_folder)
    elif ext in [".pptx"]:
        extracted_images = extract_text_and_images_from_pptx(file_path, txt_file_path, output_folder)
    elif ext == ".csv":
        extracted_images = extract_text_from_csv(file_path, txt_file_path)
    elif ext == ".docx":
        extracted_images = extract_text_and_images_from_docx(file_path, txt_file_path, output_folder)
    elif ext in [".jpg", ".jpeg", ".png"]:
        extracted_images = extract_text_from_image(file_path, txt_file_path)
    else:
        return None, []

    return txt_file_path, extracted_images

def extract_text_and_images_from_pdf(pdf_path, txt_file_path, output_folder):
    all_text = []
    extracted_images = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                all_text.append(f"--- Page {i+1} ---\n{text}")

    with open(txt_file_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(all_text))

    try:
        doc = fitz.open(pdf_path)
        for i, page in enumerate(doc):
            for img_index, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image = Image.open(BytesIO(image_bytes))
                img_path = os.path.join(output_folder, f"{os.path.basename(pdf_path)}_p{i+1}_img{img_index+1}.png")
                image.save(img_path)
                extracted_images.append(img_path)
    except Exception as e:
        print(f"Image extraction failed: {e}")

    return extracted_images

def extract_text_and_images_from_docx(docx_path, txt_file_path, output_folder):
    doc = docx.Document(docx_path)
    all_text = [para.text for para in doc.paragraphs if para.text.strip()]

    with open(txt_file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(all_text))

    return []

def extract_text_from_csv(csv_path, txt_file_path):
    try:
        # Try utf-8 first
        df = pd.read_csv(csv_path)
    except UnicodeDecodeError:
        # Fallback to a more lenient encoding if UTF-8 fails
        df = pd.read_csv(csv_path, encoding='ISO-8859-1')

    with open(txt_file_path, "w", encoding="utf-8") as txt_file:
        txt_file.write(df.to_string(index=False))

    print(f"Extracted text from CSV: {txt_file_path}")
    return []
    

def extract_text_and_images_from_pptx(pptx_path, txt_file_path, output_folder):
    presentation = Presentation(pptx_path)
    full_text = []
    for i, slide in enumerate(presentation.slides):
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                full_text.append(shape.text)

    with open(txt_file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(full_text))

    return []

def extract_text_from_image(image_path, txt_file_path):
    img = Image.open(image_path).convert("L")
    text = pytesseract.image_to_string(img)
    with open(txt_file_path, "w", encoding="utf-8") as f:
        f.write(text)
    return [image_path]
