# 1. Use an official, lightweight Python runtime as a parent image
FROM python:3.12-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the requirements file into the container first (avoids rebuilding layers unnecessarily)
COPY requirements.txt .

# 4. Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your local backend application code into the container
COPY . .

# 6. Expose the port that FastAPI runs on internally
EXPOSE 8000

# 7. The command to run your FastAPI application using Uvicorn when the container starts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]