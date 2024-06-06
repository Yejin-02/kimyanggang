# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Set environment variables
ENV BASE_URL=/api/v1

# Copy only the dependency files first
COPY pyproject.toml ./

# Install poetry package manager
RUN pip install poetry

# Install dependencies
RUN poetry config virtualenvs.create false && poetry install --no-root

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
