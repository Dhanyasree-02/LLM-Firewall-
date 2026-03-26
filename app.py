import streamlit as st
import requests

st.set_page_config(page_title="LLM Firewall", layout="centered")

st.title("🔥 LLM Firewall System")

user_input = st.text_area("Enter your prompt:")

if st.button("Check Prompt"):

    if user_input.strip() == "":
        st.warning("Please enter a prompt")

    else:
        try:
            response = requests.post(
                "http://127.0.0.1:8000/check",
                json={"text": user_input}
            )

            data = response.json()

            st.subheader("🛡️ Firewall Result")

            # BLOCKED
            if data["status"] == "blocked":
                st.error("❌ BLOCKED")
                st.json(data["reason"])

            # ALLOWED
            else:
                st.success("✅ ALLOWED")

                st.subheader("🤖 LLM Response")
                st.write(data.get("llm_response", "No response received"))

                st.subheader("📊 Classification")
                st.json(data["classification"])

                st.progress(data["classification"]["confidence"])

        except Exception as e:
            st.error(f"Error: {e}")