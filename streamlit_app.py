# PDF Upload & Analysis Dashboard (Streamlit + OpenAI + PDF parsing)
# Fully automatic, deployable in 5 min on Streamlit Cloud (free), requiring zero code maintenance by user

import streamlit as st
from PyPDF2 import PdfReader
from openai import OpenAI
import pandas as pd
import tempfile

client = OpenAI()

st.set_page_config(page_title="PDF Analysis Dashboard", layout="wide")
st.title("📄 PDF Upload & Analysis Dashboard")

uploaded_file = st.file_uploader("Upload your PDF for analysis", type="pdf")

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name
    
    reader = PdfReader(tmp_path)
    extracted_text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    
    with st.expander("📄 Extracted Text (raw)"):
        st.write(extracted_text[:5000] + "..." if len(extracted_text) > 5000 else extracted_text)
    
    st.info("Sending extracted text for in-depth analysis...")

    prompt = f"""
You are a professional document analyst. Analyze the following PDF text thoroughly:
- Provide a concise summary (max 10 lines).
- Extract any structured data or tables in CSV format if present.
- Identify key topics.
- Identify the sentiment and tone.
- Provide action points if applicable.

PDF Text:
{extracted_text[:12000]}"""

    response = client.chat.completions.create(
        model="gpt-4o-preview",
        messages=[
            {"role": "system", "content": "You are a professional PDF analysis assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    analysis_result = response.choices[0].message.content

    st.subheader("📝 Analysis Result")
    st.write(analysis_result)

    st.download_button("Download Analysis as TXT", analysis_result, file_name="analysis.txt")

    # Optional structured reporting using CSV table extraction if tables detected
    if "CSV:" in analysis_result:
        csv_start = analysis_result.find("CSV:") + len("CSV:")
        csv_content = analysis_result[csv_start:].strip()
        try:
            df = pd.read_csv(pd.compat.StringIO(csv_content))
            st.subheader("📊 Extracted Table")
            st.dataframe(df)
        except Exception as e:
            st.warning("Table parsing error or no valid CSV detected.")

st.markdown("---")
st.caption("⚡ Built for easy PDF upload, deep analysis, and instant reporting without code.")
