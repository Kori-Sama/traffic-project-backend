if [ -d ".venv" ]; then
    echo "-- venv exists"
else
    echo "-- creating venv"
    python3 -m venv .venv
fi

echo "-- activating venv"
source .venv/bin/activate

echo "-- installing requirements"
pip install -r requirements.txt

echo "-- finished installation"