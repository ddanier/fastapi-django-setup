default:
    just --list

install-pre-commit:
    #!/usr/bin/env bash
    if ( which pre-commit > /dev/null 2>&1 )
    then
        pre-commit install --install-hooks
    else
        echo "-----------------------------------------------------------------"
        echo "pre-commit is not installed - cannot enable pre-commit hooks!"
        echo "Recommendation: Install pre-commit ('brew install pre-commit')."
        echo "-----------------------------------------------------------------"
    fi

install: install-pre-commit (poetry "install")

update: (poetry "install") (manage-py "migrate")

poetry *args:
    poetry {{args}}

run *args="--host 0.0.0.0 --port 8000 --reload": (poetry "run" "uvicorn" "fastapi_django_test.main:app" args)

test *args: (poetry "run" "pytest" "--cov=fastapi_django_test" "--cov-report" "term-missing:skip-covered" args)

ruff *args: (poetry "run" "ruff" "check" "fastapi_django_test" args)

mypy *args:  (poetry "run" "mypy" "fastapi_django_test" args)

lint: ruff mypy

manage-py *args: (poetry "run" "python" "manage.py" args)
