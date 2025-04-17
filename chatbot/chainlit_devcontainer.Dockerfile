FROM mcr.microsoft.com/devcontainers/python:3
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the project into the image
# ADD . /app
ADD ./chatbot_reqs.txt /build/chatbot_reqs.txt

# Sync the project into a new environment, using the frozen lockfile
RUN uv pip install -r /build/chatbot_reqs.txt --system
RUN uv pip install chainlit --system
WORKDIR /app
# ENV PATH="/app/.venv/bin:$PATH"
