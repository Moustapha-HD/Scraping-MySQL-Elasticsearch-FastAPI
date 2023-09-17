#FROM python:3.9
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

# Install Python tools
RUN pip install --upgrade pip && pip install pandas && pip install elasticsearch && pip install elasticsearch_dsl

RUN pip install mysql-connector-python && pip install sqlalchemy

RUN pip install FastAPI & pip install uvicorn

RUN pip install Depends & pip install Query && pip install status

RUN pip install fastapi && pip install pydantic

# Move into src
WORKDIR /usr/app/src

# Copy the .py into src
COPY ./api_fitness.py .

# Execute api_fitness
#CMD uvicorn api_fitness:api --reload
#CMD python3 api_fitness.py
CMD ["uvicorn", "api_fitness:api", "--host", "0.0.0.0", "--port", "8000"]