# FASTAPI
DECORATOR FACTORY Get takes aruguments like / route, reponse model and status code and create a custom decorator function
Decorator factory also tell FASTAPI to fetch data from route - UVICORN
pydantic is intelligent so post : PostClass , fastapi understadn validation task and validates, + variables like id of route and other custom parameters are know to decorator function along with our backend logic and return message
Stuff like dependencies are also put into root function becuase they are being used too
the return message is cached by fastapi and it makes it into json and uses UVICORN to connect to network and send
it wraps everything together and replaces that over get..., so next time fast api sees get it know what to call


