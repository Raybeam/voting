#!/bin/bash
# Find out the location of the script, not the working directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
# Navigate to the backend directory
cd "${DIR}/.."
# Activate virtualenv
. ~/voting-venv/bin/activate
# Start Django with Gunicorn
gunicorn --bind 127.0.0.1:8000 -w 4 --access-logfile - --error-logfile - wsgi