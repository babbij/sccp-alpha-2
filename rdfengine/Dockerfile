FROM python:3-stretch
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . /app
EXPOSE 8080
CMD python ./rdfengine/run.py
