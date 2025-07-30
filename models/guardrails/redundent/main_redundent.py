from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from guardrails import Guard
from guardrails.hub import RedundantSentences

app = FastAPI(title="Redundant Language Detection API",
              version="1.0.0",
              docs_url="/docs",  # Swagger UI
              redoc_url="/redoc"
              )

# Define the request model
class TextInput(BaseModel):
    text: str


# Set up the guard
guard = Guard().use(
    RedundantSentences,
    on_fail="noop"
)


@app.post("/validate")
async def validate_text(input_data: TextInput):
    try:
        result = guard.validate(input_data.text)
        return {"valid": result.__dict__, "message": "Text passed Redundant language validation."}
    except Exception as e:
        return {
            "valid": False,
            "message": "Text failed Redundant language validation.",
            "error": str(e)
        }


@app.get("/")
def root():
    return {"status": "Redundant language detection API running."}