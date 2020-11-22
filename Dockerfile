FROM python:3.8-slim-buster

# Make sure pip is up-to date
RUN pip install --upgrade pip

# Copy the application code
COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt
COPY . /app/

# Install the application
WORKDIR /app/
RUN python setup.py install

EXPOSE $SERVER_PORT

ENTRYPOINT ["python", "actions/app.py"]
