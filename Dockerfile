FROM python:3.12-slim as base
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY req.txt req.txt
RUN pip install --no-cache-dir -r req.txt
RUN python -m nltk.downloader -d /opt/nltk_data punkt
RUN guardrails configure --enable-metrics --enable-remote-inferencing  --token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJnaXRodWJ8NTg1MTk4MiIsImFwaUtleUlkIjoiYzU4MDIzOGUtNTc1MC00M2JkLTgxNzEtYTAxZmQ0YzVlYTExIiwic2NvcGUiOiJyZWFkOnBhY2thZ2VzIiwicGVybWlzc2lvbnMiOltdLCJpYXQiOjE3NTMzODM5MzIsImV4cCI6NDkwNjk4MzkzMn0.wjL6KccAqYKnLjZLwPPaj3Bam1ERlADpVCTPNlfMLNI


FROM base as finalbase
RUN curl -O https://curl.se/ca/cacert.pem\n
RUN SSL_CERT_FILE=cacert.pem

FROM finalbase as guard-rails-ai-toxic-detection
RUN guardrails hub install hub://guardrails/toxic_language
COPY models/guardrails/toxic_prompt/main_toxic.py main_toxic.py

FROM base as guard-rails-ai-pii
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
        g++ \
        libopenblas-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
RUN guardrails hub install hub://guardrails/detect_pii

FROM finalbase as guard-rails-ai-jail-break
RUN guardrails hub install hub://guardrails/detect_jailbreak
COPY models/guardrails/jail_break/main_jailbreak.py main_jailbreak.py


FROM base as guard-rails-ai-redundent
RUN guardrails hub install hub://guardrails/redundant_sentences
COPY models/guardrails/redundent/punkt_configure.py punkt_configure.py
RUN python punkt_configure.py
COPY models/guardrails/redundent/main_redundent.py main_redundent.py

#FROM base as guard-rails-ai-sensetive
#RUN guardrails hub install hub://guardrails/sensitive_topics
#COPY models/guardrails/redundent/main_redundent.py main_redundent.py


FROM ollama/ollama as ollama
EXPOSE 11434
CMD ["ollama", "serve"]


#FROM ollama as phi3
#RUN ollama pull phi3
#EXPOSE 11434
#CMD ["ollama", "serve"]
#
#FROM ollama as mistral
#RUN ollama pull mistral
#
#
#FROM ollama as gemma
#RUN ollama pull gemma
#
#
#FROM ollama as llama3
#RUN ollama pull llama3
#
