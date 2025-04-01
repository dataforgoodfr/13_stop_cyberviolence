FROM python:3.13-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the project into the image
# ADD . /app
ADD ./chatbot_reqs.txt /build/chatbot_reqs.txt

# Sync the project into a new environment, using the frozen lockfile
# WORKDIR /app
RUN uv pip install -r /build/chatbot_reqs.txt --system
RUN uv pip install chainlit --system
# ENV PATH="/app/.venv/bin:$PATH"