git pull

if [ -n "$(lsof -i:8000 | awk 'NR!=1 {print $2}')" ]; then
    echo "kill existing process"
    lsof -i:8000 | awk 'NR!=1 {print $2}' | xargs kill -9
fi

if [ -f "nohup.log" ]; then
    rm nohup.log
fi

if [ -f "nohup.out" ]; then
    rm nohup.out
fi

if [ -f "nohup.err" ]; then
    rm nohup.err
fi


nohup python3 ./main.py > nohup.log 2>&1 &

exit