---
title: PDF and Image Content Summarizer
emoji: 📄
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: "1.12.2"
app_file: app.py
pinned: false
---

Check out the configuration reference at [Hugging Face Spaces Config Reference](https://huggingface.co/docs/hub/spaces-config-reference).

# PDF and Image Content Summarizer and Query Answerer

This Streamlit app allows users to upload a PDF or image and enter a query to get summarized content or answers based on the file content. 

## Features
- Upload PDF or image files.
- Enter text queries to get responses based on the uploaded file content.
- Summarizes tables and images from PDF files.
- Extracts and summarizes text from images.

## Usage

1. Upload a PDF or image file.
2. Enter your query in the text area.
3. Get summarized content or answers based on the file content.

## Requirements

Ensure you have the necessary dependencies installed:

```bash
pip install streamlit unstructured[all-docs] pillow pydantic lxml matplotlib langchain-core langchain-google-genai pytesseract

