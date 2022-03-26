from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware

from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.conf import settings

from .wsgi import application as django_app

app = FastAPI()


@app.get("/v2")
def read_main():
    return {"message": "Hello World"}


if settings.DEBUG:
    app.mount("/", WSGIMiddleware(StaticFilesHandler(django_app)))
else:
    app.mount("/", WSGIMiddleware(django_app))
