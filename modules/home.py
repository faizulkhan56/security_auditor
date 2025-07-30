import streamlit as st

def show():
    st.markdown(
        '<div class="main-header"><h1>LLM Security & Compliance Auditor</h1><br></div>',
        unsafe_allow_html=True)
    col1, col2  = st.columns(2)
    with col1:
        st.markdown("""
        <div class="card">
            <h4>🔬 Research</h4>
            <ul style="font-size: 0.9em;">
                <li><strong>PromptInject</strong> - NeurIPS 2022 </li>
                <li><strong>Jailbreaking ChatGPT</strong> - ArXiv 2023</li>
                <li><strong>Universal Triggers</strong> - EMNLP 2023</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="card">
            <h4>🛡️ Frameworks</h4>
            <ul style="font-size: 0.9em;">
                <li><strong>OWASP LLM Top 10</strong></li>
                <li><strong>NIST AI RMF</strong></li>
                <li><strong>Microsoft Responsible AI</strong></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="card">
            <h4>📖 Industry</h4>
            <ul style="font-size: 0.9em;">
                <li><strong>Anthropic</strong> - Constitutional AI</li>
                <li><strong>OpenAI</strong> - GPT-4 System Card</li>
                <li><strong>HuggingFace</strong> - Ethical Guidelines</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="card">
            <h4>🔧 Tools</h4>
            <ul style="font-size: 0.9em;">
                <li><strong>Garak</strong> - Vulnerability scanner</li>
                <li><strong>PromptFoo</strong> - Evaluation framework</li>
                <li><strong>LangTest</strong> - Testing library</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

