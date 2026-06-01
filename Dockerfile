FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Install Hermes Agent from GitHub
RUN pip install --no-cache-dir git+https://github.com/NousResearch/hermes-agent.git

# Create Hermes home and directories
ENV HERMES_HOME=/root/.hermes
RUN mkdir -p $HERMES_HOME/skills/implant-diploma-coach \
    && mkdir -p $HERMES_HOME/profiles/implant-diploma

# Copy skill and personality
COPY implant-diploma-coach/SKILL.md $HERMES_HOME/skills/implant-diploma-coach/SKILL.md
COPY SOUL.md $HERMES_HOME/profiles/implant-diploma/SOUL.md

# Create profile config
RUN mkdir -p $HERMES_HOME/profiles/implant-diploma/skills/implant-diploma-coach \
    && cp $HERMES_HOME/skills/implant-diploma-coach/SKILL.md $HERMES_HOME/profiles/implant-diploma/skills/implant-diploma-coach/SKILL.md

# Expose API port
EXPOSE 8642

# Run the agent gateway with implant diploma profile
CMD ["hermes", "--profile", "implant-diploma", "--skills", "implant-diploma-coach", "gateway", "run"]
