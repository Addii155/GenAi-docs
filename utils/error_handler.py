def handle_file_error(exception, filename):
    error_msg = str(exception)

    if isinstance(exception, UnicodeDecodeError):
        return f"❌ Cannot decode text in file: {filename}. Try opening it manually to check encoding."

    elif isinstance(exception, ValueError):
        return error_msg

    elif "pdftoppm" in error_msg.lower():
        return f"⚠️ Poppler is not installed or not in PATH. OCR can't be applied to {filename}."

    elif "tesseract" in error_msg.lower():
        return f"⚠️ Tesseract OCR engine is not configured. OCR cannot be performed on {filename}."

    elif "Could not read page count" in error_msg:
        return f"⚠️ Could not determine page count — {filename} might be corrupted or image-based."

    else:
        return f"❌ Unexpected error while processing {filename}: {error_msg}"
