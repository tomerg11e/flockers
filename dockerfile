FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the application files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir solara mesa

# Expose the application port
EXPOSE 8765

# Command to run the application
CMD ["solara", "run", "app.py", "--port", "8765", "--host", "0.0.0.0"]

