import streamlit as st
import os
import glob
import google.generativeai as genai

# --- CONFIGURATION ---
st.set_page_config(page_title="SecretKeeper AI", page_icon="🔒")
# Try to get key from Streamlit Secrets (Cloud)
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    # Fallback for local testing (optional, or just use secrets.toml)
    api_key = "PASTE_YOUR_KEY_HERE_ONLY_FOR_LOCAL_TESTING" 

genai.configure(api_key=api_key)

# --- SIDEBAR CONTROLS ---
st.sidebar.title("🛠️ System Controls")
if st.sidebar.button("🔄 Reload Knowledge Base"):
    st.cache_resource.clear()
    st.rerun()

# --- LOAD KNOWLEDGE ---
@st.cache_resource
def load_vault():
    vault_data = ""
    files = glob.glob("my_vault/*.txt")
    
    # DEBUG INFO
    loaded_files = []
    
    if not files:
        return "", ["No files found! Check 'my_vault' folder."]
        
    for file_name in files:
        with open(file_name, "r", encoding="utf-8") as f:
            content = f.read()
            vault_data += f"\n--- SOURCE: {file_name} ---\n{content}\n"
            loaded_files.append(file_name)
            
    return vault_data, loaded_files

vault_context, file_list = load_vault()

# --- SIDEBAR STATUS ---
st.sidebar.success("System Online")
st.sidebar.markdown("### 📂 Loaded Files:")
for f in file_list:
    st.sidebar.code(f)

# --- MAIN UI ---
st.title("🔒 SecretKeeper AI")

# Check if vault is empty
if not vault_context:
    st.error("⚠️ The Vault is empty! Please put .txt files in the 'my_vault' folder.")
else:
    # Initialize Chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_input := st.chat_input("Ask about the secret files..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        prompt = f"""
        You are SecretKeeper AI. Answer based ONLY on the text below.
        If the answer is not in the text, say "ACCESS DENIED".
        
        VAULT DATA:
        {vault_context}
        
        USER QUESTION: 
        {user_input}
        """

        try:
            model = genai.GenerativeModel('gemini-flash-latest')
            response = model.generate_content(prompt)
            bot_reply = response.text
        except Exception as e:
            bot_reply = f"Error: {e}"

        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.markdown(bot_reply)
