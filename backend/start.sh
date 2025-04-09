#!/bin/bash
source venv/bin/activate
gunicorn -w 4 -k gevent --bind 0.0.0.0:5000 'app:create_app()'


