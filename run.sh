#!/bin/bash

chown -R redis:redis /db
cd /app/Server/
ollama serve &
sleep 30s
python3 ollama_setting.py
ollama create volair_local_model -f Modelfile
ollama create nomic-embed-text-volair -f Modelfile_2

python3 /app/Server/ssl_setting.py

service nginx start 


cd /app/Server/volair_on_PREM/api/
python3 main.py --host=0.0.0.0 --port=3000 &

python3 /app/Server/volair_on_PREM/dash/manage.py makemigrations --noinput
python3 /app/Server/volair_on_PREM/dash/manage.py migrate --noinput
python3 /app/Server/volair_on_PREM/dash/manage.py collectstatic --noinput


cd /app/Server/volair_on_PREM/dash/

echo "from app import models; models.User.objects.create_superuser('$admin_username', 'onprem@volair.co', '$admin_pass', access_key='$admin_key')" | python3 manage.py shell


gunicorn --bind localhost:3001 --workers=5 --timeout 0 dash.wsgi:application
