FROM python:3.13-slim-bookworm
# get uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install necessary tools
RUN apt-get update && \
    apt-get install -y git curl nodejs && \
    rm -rf /var/lib/apt/lists/*

# Clone only the requirements.txt file
RUN git init
RUN git remote add origin https://github.com/dataforgoodfr/13_stop_cyberviolence.git
RUN git config core.sparsecheckout true
RUN echo "chatbot/chatbot_reqs.txt" >> .git/info/sparse-checkout
RUN git pull origin main
RUN uv pip install -r chatbot/chatbot_reqs.txt --system
RUN rm -r chatbot
    
# Install pnpm
# RUN wget -qO- https://get.pnpm.io/install.sh | ENV="$HOME/.bashrc" SHELL="$(which bash)" bash -
ENV SHELL='bash'
RUN curl -fsSL https://get.pnpm.io/install.sh | sh -
# Add pnpm to PATH (the install script puts it in $HOME/.local/share/pnpm)
ENV PNPM_HOME="/root/.local/share/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

# Verify installation
RUN pnpm --version

# install chainlit fork
RUN uv pip install git+https://github.com/kantundpeterpan/chainlit.git@dev_monster#subdirectory=backend/ --system

