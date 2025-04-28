from flask import Flask, render_template, request
import logging
from app.api.routes import api
from app.config.config import LOG_FORMAT, LOG_LEVEL

# Configure logging
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    # Register blueprints
    app.register_blueprint(api, url_prefix='/api')
    
    @app.route('/')
    def index():
        return render_template('index.html')
        
    @app.route('/map')
    def map():
        return render_template('map.html')
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True) 