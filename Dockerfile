# Use Playwright's official image (includes Chromium + dependencies)
FROM mcr.microsoft.com/playwright/python:v1.47.0-focal

WORKDIR /app

# Copy dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Expose Render's required port
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
