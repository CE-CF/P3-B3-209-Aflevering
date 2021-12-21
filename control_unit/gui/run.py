from .flaskr import app

def run_gui():
    app.run(host="localhost", port=5000)
