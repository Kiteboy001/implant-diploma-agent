FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir git+https://github.com/NousResearch/hermes-agent.git

ENV HERMES_HOME=/root/.hermes
RUN mkdir -p $HERMES_HOME/skills/implant-diploma-coach \
    && mkdir -p $HERMES_HOME/profiles/implant-diploma

COPY implant-diploma-coach/SKILL.md $HERMES_HOME/skills/implant-diploma-coach/SKILL.md
COPY SOUL.md $HERMES_HOME/profiles/implant-diploma/SOUL.md
COPY config.yaml $HERMES_HOME/config.yaml

RUN mkdir -p $HERMES_HOME/profiles/implant-diploma/skills/implant-diploma-coach \
    && cp $HERMES_HOME/skills/implant-diploma-coach/SKILL.md $HERMES_HOME/profiles/implant-diploma/skills/implant-diploma-coach/SKILL.md

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8642

ENTRYPOINT ["/entrypoint.sh"]
