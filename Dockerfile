# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install uv
RUN pip install uv

# Copy the dependency files
COPY pyproject.toml .

# Install dependencies
RUN uv pip install --system .

# Copy the rest of the application's code
COPY . /app

# Command to run the application
CMD ["python", "-m", "src.main"]
