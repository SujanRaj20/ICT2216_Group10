# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY flask_app/requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the working directory contents into the container at /app
COPY flask_app/ /app/

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=app.py
# Run flask command when the container launches
CMD ["flask", "run", "--host=0.0.0.0"]

# # Use an official Python runtime as a parent image
# FROM python:3.8-slim

# # Set the working directory in the container
# WORKDIR /app

# # Copy the requirements file into the container at /app
# COPY flask_app/requirements.txt /app/

# # Install any needed packages specified in requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy the rest of the working directory contents into the container at /app
# COPY flask_app/ /app/

# # Make port 5000 available to the world outside this container
# EXPOSE 5000

# # # Optional: copy db_connector.py if provided
# # ARG DB_CONNECTOR
# # COPY $DB_CONNECTOR /app/modules/db_connector.py

# # Define environment variable
# ENV FLASK_APP=app.py

# # Run flask command when the container launches
# CMD ["flask", "run", "--host=0.0.0.0"]
