export CONFIG_TYPE=dev
nohup gunicorn -b localhost:8084 -w 8  manage:app > sinergia.log  2> sinergia.error.log  &
# Kill Unicorn Processes
# pkill -f gunicorn
