import streamlit as st
from multimodal_rag_chat import partition_pdf_elements, classify_elements, summarize_tables, generate_img_summaries, handle_query, handle_image_query

# Google API Key (Make sure to replace this with your actual API key)
GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"

st.title("PDF and Image Content Summarizer and Query Answerer")

st.header("Upload PDF or Image")
uploaded_file = st.file_uploader("Choose a PDF or Image file", type=["pdf", "jpg", "jpeg", "png"])
query = st.text_input("Enter your query")

if uploaded_file is not None and query:
    file_type = uploaded_file.type
    file_path = "temp." + file_type.split('/')[1]
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    if file_type.startswith("application/pdf"):
        raw_pdf_elements = partition_pdf_elements(file_path)
        Header, Footer, Title, NarrativeText, Text, ListItem, img, tab = classify_elements(raw_pdf_elements)
        
        text_elements = Header + Footer + Title + NarrativeText + Text + ListItem
        text_response = handle_query(query, GOOGLE_API_KEY, text_elements)
        
        st.header("Query Response")
        st.write(text_response)
        
        if tab:
            st.header("Table Summaries")
            table_summaries = summarize_tables(tab, GOOGLE_API_KEY)
            st.write(table_summaries)
        
        if img:
            st.header("Image Summaries")
            img_base64_list, image_summaries = generate_img_summaries("extracted_data", GOOGLE_API_KEY)
            st.write(image_summaries)

    elif file_type.startswith("image"):
        image_query_response = handle_image_query(file_path, query, GOOGLE_API_KEY)
        st.header("Image Query Response")
        st.write(image_query_response)