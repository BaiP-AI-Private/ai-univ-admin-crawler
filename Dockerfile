# Use official Python 3.12 base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy project files into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the default command to run the main script
CMD ["python", "main.py"]
