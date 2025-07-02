import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import urllib.parse

# --- AI CORE MODULE (Completed) ---
load_dotenv()
try:
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
except AttributeError:
    # This is a fallback for Streamlit Community Cloud where st.secrets is used
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

def get_structured_data(user_query: str) -> dict:
    master_prompt = """
    You are an expert business analyst. Your task is to extract key entities from a user's request for finding companies.
    Analyze the user's query and return a structured JSON object with the following keys:
    - "industry": A list of relevant industries.
    - "location": A list of relevant cities, states, or countries.
    - "stage": The funding stage of the company (e.g., "Seed", "Series A", "Public").
    - "technologies": A list of specific technologies mentioned.
    - "search_keywords": A list of 3-5 optimized search engine query strings based on the user's request.

    If a key is not mentioned in the query, return an empty list [] for it.
    
    User Query: "{query}"
    
    JSON Output:
    """
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    try:
        response = model.generate_content(master_prompt.format(query=user_query))
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        structured_data = json.loads(cleaned_response)
        return structured_data
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"error": "Failed to parse AI response. Please try a different query."}

# --- UI LOGIC ---
st.set_page_config(page_title="Smart Search", layout="centered")
st.title("Smart Search 🔎")
st.write("The AI-Powered Lead Finder. Describe your ideal company in plain English below.")

user_query = st.text_input("Enter your request:", placeholder="e.g., Seed-stage AI healthcare companies in Boston")
submit_button = st.button("Generate Search")

st.divider()

if submit_button and user_query:
    with st.spinner("AI is thinking..."):
        ai_results = get_structured_data(user_query)

    if "error" in ai_results:
        st.error(ai_results["error"])
    else:
        # --- PHASE 3: PRESENTATION LOGIC ---

        # "Show Your Work" Deconstruction Box
        with st.container(border=True):
            st.subheader("Interpreting Your Request...")
            # Displaying the extracted entities in a more readable format
            details_md = ""
            if ai_results.get("industry"):
                details_md += f"- **Industry:** {', '.join(ai_results['industry'])}\n"
            if ai_results.get("location"):
                details_md += f"- **Location:** {', '.join(ai_results['location'])}\n"
            if ai_results.get("stage"):
                details_md += f"- **Stage:** {', '.join(ai_results['stage'])}\n"
            if ai_results.get("technologies"):
                details_md += f"- **Technologies:** {', '.join(ai_results['technologies'])}\n"
            
            if details_md:
                st.markdown(details_md)
            else:
                st.write("Could not extract specific details, proceeding with general keywords.")

        st.write("") 

        # Module 3: The Link Generator
        with st.container(border=True):
            st.subheader("Generated Search Links")
            st.write("Click these links to open targeted searches in a new tab:")

            keywords_list = ai_results.get("search_keywords", [])
            
            # We use urllib.parse.quote_plus to make sure keywords are URL-safe
            google_link = f"https://www.google.com/search?q={urllib.parse.quote_plus(keywords_list[0])}"
            linkedin_link = f"https://www.linkedin.com/search/results/companies/?keywords={urllib.parse.quote_plus(keywords_list[1])}"
            crunchbase_link = f"https://www.crunchbase.com/discover/organization.companies/PRIMARY_ROLE=company,QUERY={urllib.parse.quote_plus(keywords_list[2])}"
            
            st.markdown(f"- [**Search on Google**]({google_link})")
            st.markdown(f"- [**Search on LinkedIn**]({linkedin_link})")
            st.markdown(f"- [**Search on Crunchbase**]({crunchbase_link})")
else:
    st.info("Your results will appear here once you click 'Generate Search'.")