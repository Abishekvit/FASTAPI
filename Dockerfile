FROM python:3.11.1
#to run all commands specify the python version
WORKDIR /usr/src/app
# creating a folder inside container for neatness
COPY requirements.txt ./
#copy the file requirements.txt to the working directory
RUN pip install --no-cache-dir -r requirements.txt
# no cache dir means, usually it keeps extra copy of downloaded file in .whl so that if you delete it doesnt need to sownload from net, but that takes a lot of space 
COPY . .
#all files
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

#to run docker build -t fastapi-app .  
# docker login
# docker tag fastapi-api abishek122/fastapi-api:latest
# docker push abishek122/fastapi-api:latest
