from fastapi import APIRouter, status, HTTPException
from google import genai
from google.genai import types

from ..schemas import GPTRequest,CodeNote,CodeNoteResponse

router = APIRouter(prefix="/gpt", tags=["GPT"])

client = genai.Client(
    api_key=""
)


@router.post("/", status_code=status.HTTP_200_OK,response_model=list[CodeNoteResponse])
def chat(request: GPTRequest):
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=request.message,
        config=types.GenerateContentConfig(
            system_instruction="""
            You are a short-note-making bot for a developer learning.

            Do not assume the user knows development concepts.
            The input will be code.

            Return key points explaining the purpose of each object,
            one line per object, 
            structure is line number, significance, name, advantage, for each in key value pair
            Give json as output

            If the code has 3 classes, explain the need for each class.
            """,
            response_mime_type="application/json",
            response_schema= list[CodeNote],
            temperature=0.7,
        ),
    )

    if not response.text:
        return {"reply": "No response from Gemini."}
    print(response)
    return response.parsed
#response is object of api , and parsed gives actual object in json