from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from guardrails import Guard
from guardrails.hub import ToxicLanguage

app = FastAPI(title="Toxic Language Detection API",
              version="1.0.0",
              docs_url="/docs",  # Swagger UI
              redoc_url="/redoc"
              )


# Define the request model
class TextInput(BaseModel):
    text: str


# Set up the guard
guard = Guard().use(
    ToxicLanguage, threshold=0.5,
    validation_method="full",
    on_fail="noop"
)


@app.post("/validate")
async def validate_text(input_data: TextInput):
    try:
        result = guard.validate(input_data.text)
        return {"valid": result.__dict__, "message": "Text passed toxic language validation."}
    except Exception as e:
        return {
            "valid": False,
            "message": "Text failed toxic language validation.",
            "error": str(e)
        }


@app.get("/")
def root():
    return {"status": "Toxic language detection API running."}