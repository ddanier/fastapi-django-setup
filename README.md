# fastapi-django-setup

This small repo is my very own test on getting my first framework love (Django)
together with my current framework love (FastAPI). The two argue a lot about things
like async and testing and seems to not liking my idea...but we will get there.

This is possibly far from being a solution for everyone, but still may contain things
you can just copy for your own marriage plans. I try to avoid any bad "social" patterns
and keep this all as clean as possible. So far no lawyer was necessary, so thats a good
thing.

Have fun with it. 👍🙃

## Some more serious details and notes

* The basic goal is to use DJango like normal and have FastAPI provide the API URLs
  using the Django ORM. Also I would like to use the Django admin again.
* Using Django as a mount in FastAPI will loose the static files handling Django normally
  enabled on your local dev server. See `main.py` on how to solve this.
* I created some code to automatically convert Django models to pydantic models, see
  `utils/models/django.py` for details. This is not finished yet, but may be a good
  starting point for you.
* Testing the FastAPI API URLs is somewhat special. Django normally uses transactions to
  reset the DB state after each test. This is not working correctly when not using the
  Django `TestCase` class - which we don't want to and cannot do as we are in FastAPI here.
  My current solution is to set the tests to use the `transactional_db` fixture of
  `pytest-django`, this will recreate the DB for each test. Slower, but working.
* Some things in the repo are just my personal best practices (like using `dirty-equals`
  in the tests). Make your own choices. 😉

