
import application.config

from application import app
if __name__ == '__main__':
    app.run(debug = application.config.DEBUG)
