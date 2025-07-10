import docx
import PyPDF2

def extract_text_from_file(file):
    if file.type == "text/plain":
        try:
            return file.read().decode("utf-8")
        except UnicodeDecodeError:
            return file.read().decode("ISO-8859-1")

    elif file.type == "application/pdf":
        try:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
            return text
        except Exception as e:
            raise ValueError(f"Error reading PDF: {str(e)}")

    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        try:
            doc = docx.Document(file)
            return '\n'.join([para.text for para in doc.paragraphs])
        except Exception as e:
            raise ValueError(f"Error reading DOCX: {str(e)}")

    else:
        raise ValueError("Unsupported file type")
