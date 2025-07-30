from fastapi import FastAPI
from pydantic import BaseModel
from guardrails import Guard
from guardrails.hub import DetectJailbreak

app = FastAPI(title="Direct Jailbreak API",
              version="1.0.0",
              docs_url="/docs",
              redoc_url="/redoc"
              )


class TextInput(BaseModel):
    text: str


guard = Guard().use(
    DetectJailbreak, threshold=0.8,
    validation_method="full",
    on_fail="noop"
)


@app.post("/validate")
async def validate_text(input_data: TextInput):
    try:
        result = guard.validate(input_data.text)
        return {"valid": result.__dict__, "message": "Text passed jailbreak language validation."}
    except Exception as e:
        return {
            "valid": False,
            "message": "Text failed jail break language validation.",
            "error": str(e)
        }


@app.get("/")
def root():
    return {"status": "Jailbreak language detection API running."}
