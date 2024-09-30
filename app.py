import validators
import streamlit as st
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import YoutubeLoader, UnstructuredURLLoader
from dotenv import load_dotenv
import os

## Load environment variables
load_dotenv()

## Streamlit APP
st.set_page_config(page_title="Text Summarizer", page_icon="📝")

# Add some extra styling effects for the webpage
st.markdown(
    """
    <style>
    .main-header { font-size: 40px; text-align: center; font-weight: bold; color: #4CAF50; }
    .description { text-align: center; font-size: 18px; color: #888888; margin-bottom: 20px; }
    .footer { font-size: 16px; text-align: center; color: #888888; margin-top: 50px; padding-top: 20px; border-top: 1px solid #888888; }
    </style>
    """, 
    unsafe_allow_html=True
)

# Main page
st.markdown('<div class="main-header">🌟 RapidRecap: Summarize Content from YouTube or Website</div>', unsafe_allow_html=True)
st.markdown('<div class="description">🔍 This tool allows you to summarize content from YouTube videos and websites. Simply enter a URL, and get a quick and concise summary! 🚀</div>', unsafe_allow_html=True)
st.subheader('Summarize URL 📑')

# Sidebar for API key and URL input
with st.sidebar:
    st.markdown("🛠️ **Settings**")
    groq_api_key = st.text_input("Groq API Key 🔑", value="", type="password")

# If the API key is not provided, check the environment variable
if not groq_api_key.strip():
    groq_api_key = os.getenv("GROQ_API_KEY")

generic_url = st.text_input("Enter a YouTube or Website URL 🌐", label_visibility="collapsed")

# Langchain Model using Groq API
if groq_api_key:
    try:
        llm = ChatGroq(model="Gemma-7b-It", groq_api_key=groq_api_key)
    except Exception as e:
        st.error("Failed to initialize Groq API with the provided key. Please enter a valid Groq API Key. ⚠️")
        st.stop()
else:
    st.error("Please enter your Groq API Key to continue. ⚠️")
    st.stop()

# Prompt template for summarization
prompt_template = """
Provide a summary of the following content in 300 words:
Content:{text}
"""
prompt = PromptTemplate(template=prompt_template, input_variables=["text"])

# Summarize button
if st.button("Summarize the Content from YT or Website 🎯"):
    # Validate inputs
    if not generic_url.strip():
        st.error("Please provide the URL to summarize. ⚠️")
    elif not validators.url(generic_url):
        st.error("Please enter a valid URL (YouTube or website) ⚠️")
    else:
        try:
            with st.spinner("Processing... ⏳"):
                # Load YouTube or website data
                if "youtube.com" in generic_url:
                    loader = YoutubeLoader.from_youtube_url(generic_url, add_video_info=True)
                else:
                    loader = UnstructuredURLLoader(
                        urls=[generic_url], ssl_verify=False,
                        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"}
                    )
                docs = loader.load()

                # Chain for summarization
                chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)
                output_summary = chain.run(docs)

                st.success(output_summary)
        except Exception as e:
            st.exception(f"Exception: {e}")

# Footer
st.markdown('<div class="footer">✨ Developed by Your Name | Powered by LangChain and Groq LLM 🚀</div>', unsafe_allow_html=True)
