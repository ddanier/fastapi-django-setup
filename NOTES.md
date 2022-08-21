Staticfiles files not work without collectstatic:
-> https://docs.djangoproject.com/en/4.0/ref/contrib/staticfiles/#runserver
-> We use unicorn to run the dev server, thus this cannot work
-> We can use the StaticFilesHandler on WSGI mount to get this working


