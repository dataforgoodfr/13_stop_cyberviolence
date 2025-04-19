FROM kantundpeterpan/chainlit_uv:dev
EXPOSE 8080
RUN apt-get update && apt-get install -y git

# Clone the repository
RUN git clone https://github.com/kantundpeterpan/13_stop_cyberviolence.git /app

# Install Python dependencies
WORKDIR /app/chatbot
RUN uv pip install -r chatbot_reqs.txt --system

# Define the entry point (optional, if only running one command)
ENTRYPOINT ["chainlit", "run", "chainlit_app.py", "--host", "0.0.0.0", "--port",  "8080"]