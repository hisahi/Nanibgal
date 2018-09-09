
import application.config

from application import app
if __name__ == '__main__':
    app.run(debug = application.config.DEBUG, 
            host = "0.0.0.0" if application.config.PUBLIC else "localhost", 
            port = application.config.PORT)
