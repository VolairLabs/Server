import os

generate_command = 'openssl req -x509 -newkey rsa:4096 -keyout /db/volair.private.pem -out /db/volair.origin.pem -days 365 -nodes -subj "/C=US/ST=Denial/L=Springfield/O=Dis/CN=www.volair.co"'

if not os.path.exists("/db/volair.private.pem"):
    os.system(generate_command)
