import streamlit as st
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.file_handler import extract_text_from_file
from utils.error_handler import handle_file_error
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_core.output_parsers import StrOutputParser
import time

load_dotenv()

st.set_page_config(page_title="GenAI Doc Viewer", layout="wide")
st.title("GenAI Multi-Document Viewer")

uploaded_files = st.file_uploader(
    "Upload your documents (.txt, .pdf, .docx)",
    type=["txt", "pdf", "docx"],
    accept_multiple_files=True
)

prompt = PromptTemplate.from_template(
template = """
Extract key structured information from the following document:
{text}
""")
output_parser = StrOutputParser()


model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.2,
)


chain = prompt | model | output_parser


def process_file(file):
    try:
        start_time = time.time()

        content = extract_text_from_file(file)

        if not content:
            return file.name, "⚠️ File is empty or unreadable.", None, 0
        try:
            result = chain.invoke({
                "text": content
            })
        except Exception as e:
            if "Token" in str(e) or "length" in str(e) or "too long" in str(e).lower():
                result = "❌ GenAI Error: Input text too long — the document exceeds the model's token limit."
            else:
                result = f"❌ GenAI Error: {str(e)}"

        end_time = time.time()
        return file.name, content, result, end_time - start_time

    except Exception as e:
        return file.name, None, handle_file_error(e, file.name), 0


if uploaded_files:
    with st.spinner(" Processing files..."):
        results_map = {}
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(process_file, file): file.name for file in uploaded_files}
            for future in as_completed(futures):
                result = future.result()
                results_map[result[0]] = result  
    for file in uploaded_files:
        filename = file.name
        content, output, time_taken = None, None, 0
        if filename in results_map:
            _, content, output, time_taken = results_map[filename]
        st.markdown(f"## 📁 {filename}")
        # if time_taken > 20:
        #     st.warning("⚠️ Processing took longer than expected. Please check the file size or content.")
        #     continue
        if time_taken:
            st.markdown(f"⏱ Processed in {time_taken:.2f} seconds")
        if isinstance(output, str) and (output.startswith("⚠️") or output.startswith("❌") or output.startswith("Error")):
            st.error(output)
        elif content and output:
            st.markdown(output)
        else:
            st.warning("⚠️ No content or result available.")

