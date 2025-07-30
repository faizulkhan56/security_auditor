import streamlit as st
from modules.constants import probe_dict
from services.garak_runner import run_garak_live
from services.promptfoo_runner import run_promptfoo_live
from services.chat_handler import run_custom_chat

def show():
    st.header("Scan LLM for Vulnerabilities")
    tab1, tab2, tab3 = st.tabs(["Garak Scanner", "Promptfoo Scanner", "Custom Chat"])

    # --- Garak Scanner Tab ---
    with tab1:
        st.subheader("Garak Scanner")
        col1, col2 = st.columns([3, 1])
        with col1:
            model_type = st.selectbox("Model Type", ["HuggingFace", "OpenAI", "REST API"], index=0,
                                      key="garak_model_type")
            model_input = st.text_input("Model name or endpoint (e\.g\., OpenAI, HuggingFace, REST API URL)")
            submodel = model_input

            attack_type_options = ["Prompt Injection", "Jailbreak", "Info Leak", "Toxicity", "Malware"]
            attack_types = st.multiselect("Attack Type (multi-select)", options=attack_type_options, placeholder="Select attack types")

        with col2:
            token = st.text_input("API Token / Key (if needed)", type="password")

        probe_bases = list(probe_dict.keys())
        probe_primary = st.multiselect("Probe Primary (multi)", probe_bases, key="probe_primary")

        probe_secondary = []
        for p in probe_primary:
            probe_secondary += st.multiselect(f"Probe Secondary for {p} (multi)", probe_dict[p], key=f"probe_secondary_{p}")

        # Compose probe string(s) - for all combinations of selected primary and secondaries
        probe_str = ",".join([f"{p}.{s}" for p in probe_primary for s in probe_dict[p] if s in probe_secondary])

        gen_col, par_col = st.columns(2)
        with gen_col:
            generations = st.text_input("Generations", value="", placeholder="Leave blank if not needed", key="garak_generations")
        with par_col:
            parallel_requests = st.text_input("Parallel Requests", value="", placeholder="Leave blank if not needed", key="garak_parallel_requests")

        # Dynamically construct command preview
        cmd_parts = ["garak", "--model_type", model_type.lower()]
        if submodel or model_input:
            cmd_parts += ["--model_name", submodel or model_input]
        if probe_str:
            cmd_parts += ["--probes", probe_str]
        if generations.strip():
            cmd_parts += ["--generations", generations]
        if parallel_requests.strip():
            cmd_parts += ["--parallel_requests", parallel_requests]
        if attack_types:
            cmd_parts += ["--attack_types", ",".join(attack_types)]

        st.markdown("**Command Preview:**")
        st.code(" ".join(cmd_parts), language="bash")

        output_placeholder = st.empty()
        if st.button("Start Garak Scan", type="primary"):
            cmd = [c for c in cmd_parts if c]
            def on_update(text):
                output_placeholder.text_area("Live Scan Output", text, height=400)
            with st.spinner("Running Garak scan..."):
                logs, code = run_garak_live(cmd, on_update)
                output_placeholder.text_area("Scan Finished. Output:", logs, height=400)

    # --- Promptfoo Scanner Tab ---
    with tab2:
        st.subheader("Promptfoo Scanner")
        st.info("Run prompt evaluation suites with Promptfoo. Make sure promptfoo is installed.")
        pf_model = st.text_input("Model name or endpoint for Promptfoo", key="promptfoo_model")
        pf_suite = st.text_input("Path to promptfoo test suite YAML", key="promptfoo_suite")
        output_placeholder2 = st.empty()
        if st.button("Run Promptfoo Scan", type="primary"):
            cmd = ["promptfoo", "test", pf_suite, "--provider", pf_model]
            def on_update(text):
                output_placeholder2.text_area("Promptfoo Output", text, height=400)
            with st.spinner("Running Promptfoo scan..."):
                logs, code = run_promptfoo_live(cmd, on_update)
                output_placeholder2.text_area("Promptfoo Scan Finished. Output:", logs, height=400)

    # --- Custom Chat Tab ---
    with tab3:
        st.subheader("AI Chat (Direct Messaging with Model/Endpoint)")

        # Inputs, side by side
        col_m, col_k = st.columns([3, 2])
        with col_m:
            chat_model = st.text_input(
                "Model/Endpoint", key="custom_chat_model",
                placeholder="e.g. http://localhost:11434/api/chat")
        with col_k:
            chat_api_key = st.text_input(
                "API Token / Key (if needed for chat)", type="password",
                key="custom_chat_api_key", placeholder="sk-...")

        st.caption("Example: http://localhost:11434/api/chat or OpenAI endpoint, or anything REST-conversational.")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "custom_chat_input" not in st.session_state:
            st.session_state.custom_chat_input = ""

        # Chat window (5–8 messages visible, stylish background)
        st.markdown("""
        <div id="chat-window" style="
            max-height:300px;
            min-height:20px;
            overflow-y:auto;
            background:linear-gradient(130deg,#10141a,#181e25 65%);
            padding:12px 10px 4px 10px;
            border-radius:14px;
            border:1.5px solid #444c56;
            margin-bottom:13px;">
        """, unsafe_allow_html=True)

        if st.session_state.chat_history:
            for speaker, text in st.session_state["chat_history"][-8:]:
                preview = text if len(text) < 400 else text[:380] + "…"
                if speaker == "You":
                    st.markdown(
                        f'<div style="text-align:right;margin-bottom:6px;"><span style="background:#6366f1;box-shadow:0 2px 8px #2222; color:#fff;padding:8px 15px;border-radius:20px 18px 4px 20px;display:inline-block;font-size:1em;max-width:75%;word-break:break-word;">{preview}</span></div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div style="text-align:left;margin-bottom:6px;"><span style="background:#f1f3f4;box-shadow:0 2px 8px #ccc2; color:#23272f;padding:8px 15px;border-radius:20px 20px 20px 5px;display:inline-block;font-size:1em;max-width:75%;word-break:break-word;">{preview}</span></div>',
                        unsafe_allow_html=True
                    )
        else:
            st.markdown(
                '<div style="text-align:center;color:#aaa;padding:20px;">Start a conversation...</div>',
                unsafe_allow_html=True
            )

        st.markdown('</div>', unsafe_allow_html=True)

        col1, col2 = st.columns([7, 1])
        with col1:
            user_input = st.text_input("Message...", key="custom_chat_input", value="", label_visibility="collapsed")
        with col2:
            send_now = st.button("Send", key="custom_chat_send", use_container_width=True)

        ready_for_chat = chat_model.strip() and user_input.strip()
        # if not chat_model.strip():
        #     st.warning("Please enter your Model/Endpoint before starting a chat.", icon="⚠️")

        # When sending, call the callback
        if send_now and ready_for_chat:
            st.session_state.chat_history.append(("You", user_input))
            with st.spinner("Waiting for model/endpoint..."):
                reply = run_custom_chat(chat_model, user_input)
                st.session_state.chat_history.append(("Model", reply))
            st.rerun()

        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()

