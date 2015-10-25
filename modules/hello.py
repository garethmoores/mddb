from modules import app

@app.route('/hello')
def hello():
	return 'Hello'
