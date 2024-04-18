FROM --platform=linux/amd64 python:3.12-slim

WORKDIR /dialog-app

# Install the requirements
RUN pip install poetry
COPY ./pyproject.toml /dialog-app/pyproject.toml
RUN poetry install

# Copy the app folders and files
COPY main.py /dialog-app/main.py
COPY ./templates /dialog-app/templates
COPY questions.json /dialog-app/questions.json

# Run app
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]