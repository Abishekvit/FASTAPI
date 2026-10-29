# from fastapi import APIRouter, status, HTTPException, Depends
# from google import genai
# from google.genai import types
# import json
# from sqlalchemy.orm import Session
# from ..schemas import GPTRequest,CodeNote,CodeNoteResponse,UserResponse
# from .. import database,models,oauth2,models
# from fastapi.responses import StreamingResponse

# router = APIRouter(prefix="/gpt", tags=["GPT"])

# client = genai.Client(
#     api_key=""
# )

# # Server Sent Events for streaming , server sends them to client as SSE, sends completion event at the end
# @router.post("/streaming")
# def chat_stream(request: GPTRequest):
#     def events():
#         usage = None

#         for chunk in client.models.generate_content_stream(
#             # a piece of data is retrieved and called as chunk
#             #there it was content
#             model="gemini-3.6-flash",
#             contents=request.message,
#             config=types.GenerateContentConfig(
#                 system_instruction="""
#                             The application is made considering the Fact of SERVER SENT EVENTS, streaming, so be it any question/
#                             always give string message as a whole with proper spacing and punctuations.
#                             Should be given with repect to a developer
#                             """,
#                 temperature=0.7,
#             ),
#         ):
#             if chunk.text:
#                 data = json.dumps({"text": chunk.text})
#                 #SSE have text attribute
#                 yield f"event: chunk\ndata: {data}\n\n"
#         yield "event: done\ndata: {}\n\n"
#         #done event to show all messages or tokens have reached
#         #yield allows to return multiple items instead of one

#     return StreamingResponse(
#         events(),
#         media_type="text/event-stream",
#         headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
#     )
#     #Streaming Response keeps HTTP Response, and sends each yielded SSE Event
#     #Generator example def numbers():
#     # yield 1
#     # yield 2
#     # yield 3


# @router.post("/", status_code=status.HTTP_200_OK,response_model=list[CodeNoteResponse])
# def chat(request: GPTRequest):
#     response = client.models.generate_content(
#         model="gemini-3.6-flash",
#         contents=request.message,
#         config=types.GenerateContentConfig(
#             system_instruction="""
#             You are a short-note-making bot for a developer learning.

#             Do not assume the user knows development concepts.
#             The input will be code.

#             Return key points explaining the purpose of each object,
#             one line per object, 

#             structure is line number, significance, name, advantage, for each in key value pair
#             Give json as output..

#             If the code has 3 classes, explain the need for each class.
#             """,
#             response_mime_type="application/json",
#             response_schema= list[CodeNote],
#             temperature=0.7,
#         ),
#     )
    
#     if not response.text:
#         return {"reply": "No response from Gemini."}
#     usage = response.usage_metadata

#     if usage is not None:
#         print("Input:", usage.prompt_token_count)
#         # input token
#         print("Output:", usage.candidates_token_count)
#         # visible generated tokens
#         print("Thoughts:", usage.thoughts_token_count)
#         # tokens used for reasoning
#         print("Total:", usage.total_token_count)
#         # total = all + tool + cached input content tokens etc.
#     else:
#         print("Gemini did not return token usage metadata")
#     print(response)
#     return response.parsed
# #response is object of api , and parsed gives actual object in json


# #response is object of api , and parsed gives actual object in json