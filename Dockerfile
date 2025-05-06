# Use official Python 3.12 base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy project files into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 for FastAPI
EXPOSE 8000

# Set the default command to start the FastAPI API
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
