# Use an official Python runtime as a parent image
FROM python:3.12.2-slim

# Create a non-root user and group with UID and GID 1000
RUN groupadd -g 1000 flaskgroup && \
    useradd -r -u 1000 -g flaskgroup flaskuser

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Change ownership of the application directory
RUN chown -R flaskuser:flaskgroup /app

# Change ownership of the application directory and Python site-packages
RUN chown -R flaskuser:flaskgroup /app && \
    mkdir -p /home/flaskuser/.local && \
    chown -R flaskuser:flaskgroup /home/flaskuser/.local

# Switch to the non-root user
USER flaskuser

# Install dependencies as the non-root user
ENV PATH=/home/flaskuser/.local/bin:$PATH
RUN pip install --user --no-cache-dir -r requirements.txt


# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV FLASK_APP=app.py

# Run app.py when the container launches
#CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]
#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]

CMD ["python", "app.py"]
