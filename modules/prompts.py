import streamlit as st
import json
import os

PROMPT_FILE = "prompts/prompts.json"

def load_prompts():
    if os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_prompts(prompts):
    os.makedirs(os.path.dirname(PROMPT_FILE), exist_ok=True)
    with open(PROMPT_FILE, "w", encoding="utf-8") as f:
        json.dump(prompts, f, ensure_ascii=False, indent=2)

def show():
    st.header("Prompt Library Management")
    st.markdown("Manage and organize your security testing prompts.")

    prompts = load_prompts()

    col1, col2 = st.columns([2, 1])
    with col1:
        new_prompt = st.text_area("Add New Prompt", height=100)
    with col2:
        category = st.selectbox("Category", ["Jailbreak", "Injection", "Toxicity"])
        if st.button("Add Prompt", type="primary"):
            if new_prompt.strip():
                prompts.append({"prompt": new_prompt, "category": category})
                save_prompts(prompts)
                st.success("Prompt added and saved!")
            else:
                st.warning("Please enter a prompt before adding.")

    st.markdown("### Existing Prompts")
    for i, item in enumerate(prompts):
        st.markdown(f"**{item['category']}**: {item['prompt']}")
