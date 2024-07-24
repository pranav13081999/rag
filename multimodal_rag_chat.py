import os
import base64
from unstructured.partition.pdf import partition_pdf
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from PIL import Image
import pytesseract

# Function to partition PDF
def partition_pdf_elements(filename):
    raw_pdf_elements = partition_pdf(
        filename=filename,
        strategy="hi_res",
        extract_images_in_pdf=True,
        extract_image_block_types=["Image", "Table"],
        extract_image_block_to_payload=False,
        extract_image_block_output_dir="extracted_data"
    )
    return raw_pdf_elements

# Function to classify elements
def classify_elements(raw_pdf_elements):
    Header, Footer, Title, NarrativeText, Text, ListItem, img, tab = [], [], [], [], [], [], [], []

    for element in raw_pdf_elements:
        if "unstructured.documents.elements.Header" in str(type(element)):
            Header.append(str(element))
        elif "unstructured.documents.elements.Footer" in str(type(element)):
            Footer.append(str(element))
        elif "unstructured.documents.elements.Title" in str(type(element)):
            Title.append(str(element))
        elif "unstructured.documents.elements.NarrativeText" in str(type(element)):
            NarrativeText.append(str(element))
        elif "unstructured.documents.elements.Text" in str(type(element)):
            Text.append(str(element))
        elif "unstructured.documents.elements.ListItem" in str(type(element)):
            ListItem.append(str(element))
        elif "unstructured.documents.elements.Image" in str(type(element)):
            img.append(str(element))
        elif "unstructured.documents.elements.Table" in str(type(element)):
            tab.append(str(element))
    return Header, Footer, Title, NarrativeText, Text, ListItem, img, tab

# Function to summarize tables
def summarize_tables(tab, google_api_key):
    prompt_text = """You are an assistant tasked with summarizing tables for retrieval. \
    These summaries will be embedded and used to retrieve the raw table elements. \
    Give a concise summary of the table that is well optimized for retrieval. Table {element} """
    prompt = ChatPromptTemplate.from_template(prompt_text)

    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=google_api_key)
    summarize_chain = {"element": lambda x: x} | prompt | model | StrOutputParser()
    table_summaries = summarize_chain.batch(tab, {"max_concurrency": 5})
    return table_summaries

# Function to encode image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Function to summarize images
def image_summarize(img_base64, prompt, google_api_key):
    chat = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=google_api_key, max_output_tokens=512)
    msg = chat.invoke(
        [
            HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
                ]
            )
        ]
    )
    return msg.content

# Function to generate image summaries
def generate_img_summaries(path, google_api_key):
    img_base64_list = []
    image_summaries = []
    prompt = """You are an assistant tasked with summarizing images for retrieval. \
    These summaries will be embedded and used to retrieve the raw image. \
    Give a concise summary of the image that is well optimized for retrieval.
    also give the image output if possible"""
    base64_image = encode_image(path)
    img_base64_list.append(base64_image)
    image_summaries.append(image_summarize(base64_image, prompt, google_api_key))
    return img_base64_list, image_summaries

# Function to handle text-based queries
def handle_query(query, google_api_key, text_elements):
    prompt_text = f"You are an assistant tasked with answering the following query based on the provided text elements:\n\n{query}\n\nText elements: {text_elements}"
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=google_api_key)
    msg = model.invoke([HumanMessage(content=prompt_text)])
    return msg.content

# Function to extract text from an image
def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

# Function to handle image-based queries
def handle_image_query(image_path, query, google_api_key):
    extracted_text = extract_text_from_image(image_path)
    prompt_text = f"You are an assistant tasked with answering the following query based on the extracted text from the image:\n\n{query}\n\nExtracted text: {extracted_text}"
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=google_api_key)
    msg = model.invoke([HumanMessage(content=prompt_text)])
    return msg.content
