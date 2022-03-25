from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware

from .wsgi import application as django_app

app = FastAPI()


@app.get("/v2")
def read_main():
    from fastapi_django_test.something.models import Something

    print(Something.objects.all())

    return {"message": "Hello World"}


app.mount("/", WSGIMiddleware(django_app))
