FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements.txt and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install yt-dlp
RUN apt-get update && apt-get install -y wget && \
    wget https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -O /usr/local/bin/yt-dlp && \
    chmod a+rx /usr/local/bin/yt-dlp

# Copy the FastAPI application code to the container
COPY . .

# Make the youtube_subtitle.sh executable
RUN chmod +x youtube_subtitle.sh

# Expose port 8000 for the FastAPI server
EXPOSE 8000

# Set environment variables for OpenAI key and other configuration (Coolify will handle .env)
# ENV OPENAI_API_KEY=${OPENAI_API_KEY}

# Command to run the application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
