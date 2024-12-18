git pull

netstat -nap | grep 8000  | awk '{print $7}' | awk -F '/' '{print $1}' | xargs kill -9

nohup python3 ./main.py &