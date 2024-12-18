git pull

lsof -i:8000 | awk 'NR!=1 {print $2}' | xargs kill -9

nohup python3 ./main.py &

exit