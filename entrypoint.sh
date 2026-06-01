#!/bin/bash
# Set port from Railway's PORT env var, default to 8642
export API_SERVER_PORT=${PORT:-8642}
export API_SERVER_HOST=0.0.0.0

exec hermes --profile implant-diploma --skills implant-diploma-coach gateway run
