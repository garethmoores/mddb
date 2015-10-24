from flask import Flask

app = Flask(__name__)

import modules.hello

if __name__ == "__main__":
	app.run()
