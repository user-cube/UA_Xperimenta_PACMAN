echo "Make venv" &&
python3 -m venv venv &&
echo "Initializing venv" &&
source /venv/bin/activate &&
echo "Installing requirements.txt" &&
pip install -r requirements.txt 


