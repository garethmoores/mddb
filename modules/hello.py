from modules import app

@app.route('/hello')
def index():
	return 'Hello'
