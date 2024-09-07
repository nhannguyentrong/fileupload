# Stage 1: Build environment
FROM python:3.12.5-alpine3.20 

WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies (separate from the final image)
RUN pip install --no-cache-dir -r requirements.txt


# Copy the application code
COPY . .

# Expose the port Flask will run on
EXPOSE 5000

# Command to run the Flask app
CMD ["flask", "run", "--host=0.0.0.0"]
