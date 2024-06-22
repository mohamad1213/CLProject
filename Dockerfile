# Use the official Python image.
# https://hub.docker.com/_/python
FROM python:3.8-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000


# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "core.wsgi:application"]
