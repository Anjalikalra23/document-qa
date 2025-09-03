import streamlit as st
from openai import OpenAI
import PyPDF2
from io import BytesIO

def read_pdf(uploaded_file):
    """Read PDF file and extract text content"""
    try:
        # Reset file pointer to beginning
        uploaded_file.seek(0)
        
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.read()))
        text = ""
        
        # Extract text from all pages
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None

# Show title and description.
st.title("HW1 Anjali Kalra")
st.write(
    "Upload a document below and ask a question about it — GPT will answer! "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
    "Supported file types: .txt and .pdf"
)

# Ask user for their OpenAI API key via ⁠ st.text_input ⁠.
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Model selection
    model_options = ["gpt-3.5-turbo", "gpt-4", "gpt-5-chat-latest", "gpt-5-nano"]
    selected_model = st.selectbox("Select GPT Model:", model_options, index=1)

    # Let the user upload a file via ⁠ st.file_uploader ⁠.
    uploaded_file = st.file_uploader(
        "Upload a document (.txt or .pdf)", type=("txt", "pdf")
    )

    # Initialize document variable
    document = None
    
    if uploaded_file:
        # Check file extension and process accordingly
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'txt':
            try:
                document = uploaded_file.read().decode('utf-8')
                st.success(f"Successfully loaded text file: {uploaded_file.name}")
            except Exception as e:
                st.error(f"Error reading text file: {str(e)}")
                document = None
        elif file_extension == 'pdf':
            document = read_pdf(uploaded_file)
            
        else:
            st.error("Unsupported file type. Please upload a .txt or .pdf file.")
            document = None

    # Ask the user for a question via ⁠ st.text_area ⁠.
    question = st.text_area(
        "Now ask a question about the document!",
        placeholder="Can you give me a short summary?",
        disabled=not document,
    )

    if document and question:
        # Add a button to generate the answer
        if st.button(" Answer", type="primary"):
            with st.spinner(f"Generating answer using {selected_model}..."):
                try:
                    # Process the uploaded file and question.
                    messages = [
                        {
                            "role": "user",
                            "content": f"Here's a document: {document} \n\n---\n\n {question}",
                        }
                    ]

                    # Generate an answer using the OpenAI API.
                    stream = client.chat.completions.create(
                        model=selected_model,
                        messages=messages,
                        stream=True,
                    )

                    # Stream the response to the app using ⁠ st.write_stream ⁠.
                    st.subheader("Answer:")
                    st.write_stream(stream)
                    
                except Exception as e:
                    st.error(f"Error generating answer: {str(e)}")

    # Clear document when file is removed
    if not uploaded_file:
        document = None