# haiku-net

The beginnings of a website / social media / platform that lets users interact only through the means of haiku.

# running
```bash
# if not already created
python -m venv .venv

source .venv/bin/activate

pip install -e .
# if not already initialised
flask --app flaskr init-db
flask --app flaskr run --debugger
```

# testing
```bash
pip install pytest coverage

python -m pytest

coverage run -m pytest
coverage report
coverage html
```
