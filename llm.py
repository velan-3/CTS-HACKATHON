import streamlit as st
from model import Model
import asyncio
import os

# def main():
st.title("Summarization Testing")

    # Create an instance of the Model
model = Model()

    # Query input
print("query box")
query = st.text_input("Enter your query:")

if st.button("Search"):
    with st.spinner("Searching..."):
            # Run retrieval asynchronously
            result =  model.run_retrieval()
            st.write(result)

# if __name__ == "__main__":
#     # # Set up environment variables if needed
#     # if 'HUGGING_FACE_HUB_API_KEY' not in os.environ:
#     #     os.environ['HUGGING_FACE_HUB_API_KEY'] = "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"
    
#     # Run the Streamlit app
#     main()
