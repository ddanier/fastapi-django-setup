from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from .wsgi import application as django_app

app = FastAPI()


@app.get("/v2")
def read_main():
    return {"message": "Hello World"}


app.mount("/", WSGIMiddleware(django_app))
