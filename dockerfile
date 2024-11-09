# Use the official Python image from the Docker Hub
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose port 8000
EXPOSE 8000

# Expose ports 502 and 5000 to 5200
EXPOSE 502 5000-5200

# Create a volume for the data
VOLUME [ "/app/data/" ]

# Specify the command to run the application
CMD ["python", "app.py"]