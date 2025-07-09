import docx
import PyPDF2
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image

def extract_text_from_file(file):
    used_ocr = False

    if file.type == "text/plain":
        try:
            return file.read().decode("utf-8"), used_ocr
        except UnicodeDecodeError:
            return file.read().decode("ISO-8859-1"), used_ocr

    elif file.type == "application/pdf":
        try:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted
            if text.strip():
                return text, used_ocr

            file.seek(0)
            images = convert_from_bytes(file.read())
            ocr_text = ''
            for img in images:
                ocr_text += pytesseract.image_to_string(img)
            used_ocr = True
            return ocr_text, used_ocr

        except Exception as e:
            raise ValueError(f"Error reading PDF: {str(e)}")

    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        text = '\n'.join([para.text for para in doc.paragraphs])
        return text, used_ocr

    else:
        raise ValueError("Unsupported file type")
