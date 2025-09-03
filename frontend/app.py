import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="HR Resource Query Chatbot", layout="wide")

st.title("🤖 HR Resource Query Chatbot")

st.sidebar.header("List of Operation")
choice = st.sidebar.radio('Choose operation',["Chat with HR Assistant", "Employee Search"])

if choice == "Chat with HR Assistant":
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    query = st.text_input("Enter your query")

    if st.button("Ask"):
        if query.strip():
            try:
                response = requests.post(f"{API_BASE}/chat", json={"query": query})
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "No response")
                    st.session_state.chat_history.append((query, answer))
                else:
                    st.error("Error from backend API")
            except Exception as e:
                st.error(f"API request failed: {e}")

    for q, a in st.session_state.chat_history[::-1]:
        st.markdown(f"**You:** {q}")
        st.markdown(f"**Bot:** {a}")
        st.markdown("---")

elif choice == "Employee Search":
    with st.form("search_form"):
        skills = st.text_input("Skills (comma-separated)", placeholder="Python,AWS,Docker")
        min_experience = st.number_input("Minimum Experience (years)", min_value=0, value=0)
        projects = st.text_input("Projects (comma-separated)", placeholder="Healthcare,Finance")
        availability = st.selectbox("Availability", ["available", "busy"])
        submitted = st.form_submit_button("Search Employees")

    if submitted:
        try:
            params = {
                "skills": skills if skills else None,
                "min_experience": min_experience,
                "projects": projects if projects else None,
                "availability": availability if availability else None
            }
            response = requests.get(f"{API_BASE}/employees/search", params=params)
            if response.status_code == 200:
                data = response.json()
                st.success(f"Found {data['count']} matching employees")

                for emp in data["employees"]:
                    with st.expander(f"👤 {emp['name']}"):
                        st.write(f"**Skills:** {', '.join(emp.get('skills', []))}")
                        st.write(f"**Experience:** {emp.get('experience_years', 0)} years")
                        st.write(f"**Projects:** {', '.join(emp.get('projects', []))}")
                        st.write(f"**Availability:** {emp.get('availability', 'Unknown')}")
            else:
                st.error("Error fetching employees")
        except Exception as e:
            st.error(f"API request failed: {e}")
