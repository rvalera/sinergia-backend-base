export CONFIG_TYPE=dev
# Prod
nohup gunicorn -b 0.0.0.0:60000 -w 4  manage:app > sinergia.log  2> sinergia.error.log  &
# nohup gunicorn -b 127.0.0.1:60000 -w 4  manage:app > sinergia.log  2> sinergia.error.log  &

# Test
# gunicorn -b 0.0.0.0:60000 -w 4  manage:app 
# Kill Unicorn Processes
# pkill -f gunicorn

