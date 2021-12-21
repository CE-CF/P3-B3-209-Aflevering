from control_unit.communication.coms import app

# * Til at køre production server
# gunicorn control_unit.communication.run:app --workers 5


if __name__ == "__main__":
	app.run(host='0.0.0.0', port=8000)