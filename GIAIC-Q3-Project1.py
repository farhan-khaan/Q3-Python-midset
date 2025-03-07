import streamlit as st
import pandas as pd
import os
import base64
from io import BytesIO
import io

st.set_page_config(page_title="📊 Data Sweeper", page_icon=":bar_chart:", layout="wide")

# Custom CSS
st.markdown(
    """
    <style>
    .reportview-container .main .block-container {
        max-width: 1200px;
        padding: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🧹 Data Sweeper")
st.write("🚀 This app helps you transform and clean your CSV/Excel files. Upload a dataset to get started.")

# File upload
st.sidebar.title("📂 Upload your file")
uploaded_file = st.sidebar.file_uploader("📁 Choose a file", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_file:
    for file in uploaded_file:
        file_ext = os.path.splitext(file.name)[-1].lower()

        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"❌ Unsupported file type: {file_ext}. Please upload CSV or Excel files.")
            continue

        st.write(f"### 📄 {file.name} Preview")
        st.write(df.head())

        # 🔹 Handle Missing Values
        df.fillna("Not Available", inplace=True)

        # 🔹 Convert Date Columns to Readable Format
        date_columns = ['Current Case Status Date', 'Date of 1st Institution', 'Date of Institution']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')

        # 🔹 Convert 'Hearing Date' to datetime
        if 'Hearing Date' in df.columns:
            df['Hearing Date'] = pd.to_datetime(df['Hearing Date'], errors='coerce')

        # 🔹 Drop Unnecessary Columns If Mostly Empty
        cols_to_drop = ['FIR NO', 'Challan']
        for col in cols_to_drop:
            if col in df.columns and df[col].isnull().sum() > 90:  # Drop if more than 90% missing
                df.drop(columns=[col], inplace=True)

        # Data Overview
        st.write("#### ℹ️ Data Info")
        buffer = io.StringIO()  # ✅ Use StringIO() for text-based output
        df.info(buf=buffer)
        st.text(buffer.getvalue())  # ✅ Now it will work correctly

        st.write("#### ❓ Missing Values")
        st.write(df.isnull().sum())

        st.write("#### 🔁 Duplicates")
        st.write(df.duplicated().sum())

        # Data Cleaning
        st.subheader("🛠 Data Cleaning Options")
        if st.checkbox(f"🧽 Remove Duplicates for {file.name}"):
            df.drop_duplicates(inplace=True)
            st.success("✅ Duplicates removed!")

        columns = st.multiselect(f"🎛 Select columns to keep for {file.name}", df.columns)
        if columns:
            df = df[columns]
            st.success("✅ Columns filtered!")

        # Data Visualization
        if st.checkbox(f"📊 Show Data Visualization for {file.name}"):
            st.bar_chart(df.select_dtypes(include=['number']).iloc[:, :2])

        # File Conversion
        st.subheader("🔄 File Conversion Options")
        conversion_type = st.radio("📥 Select file format", ["CSV", "Excel"], key=file.name)
        if st.button(f"💾 Convert {file.name} to {conversion_type}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                mime_type = "text/csv"
                file_name = f"{file.name}.csv"
            else:
                df.to_excel(buffer, index=False, engine="xlsxwriter")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                file_name = f"{file.name}.xlsx"

            buffer.seek(0)
            st.download_button(f"⬇️ Download {conversion_type}", buffer, file_name=file_name, mime=mime_type)

st.sidebar.info("💡 This app is developed by **GIAIC-Q3-Project1** team. 📩 Contact us at [farhankhaan@yahoo.com](mailto:farhankhaan@yahoo.com).")

st.success("✅ Data Cleaning and Transformation completed successfully!")
st.write("👋 Thanks for using Data Sweeper!")
