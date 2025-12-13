# ==========================================
# Stage 1: Builder
# ==========================================
FROM python:3.11-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# ==========================================
# Stage 2: Final
# ==========================================
FROM python:3.11-slim

WORKDIR /app

# Create a non-root user
RUN addgroup --system app && adduser --system --group app

# Install runtime dependencies (libpq for Postgres & netcat for wait-for-db)
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

# Copy wheels from builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install dependencies
RUN pip install --no-cache /wheels/*

# Copy project files
COPY . .

# Setup Directories for Static and Media
# Ensure the folder exists so permissions can be set
RUN mkdir -p /app/staticfiles && mkdir -p /app/media

# Copy entrypoint and make it executable
COPY entrypoint.sh .
# Fix windows formatting just in case
RUN sed -i 's/\r$//g' /app/entrypoint.sh 
RUN chmod +x /app/entrypoint.sh

# Change ownership to non-root user
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Expose port 5005 (Sesuai request)
EXPOSE 5005

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]