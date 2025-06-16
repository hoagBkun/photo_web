import logging
import os

# Cấu hình logging
logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), 'flask.log'),
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)

logging.debug("Starting run.py")

from app import create_app

try:
    app = create_app()
    logging.debug("App created successfully")
except Exception as e:
    logging.error(f"Error creating app: {str(e)}")
    raise

if __name__ == '__main__':
    logging.debug("Running Flask app with debug=True")
    app.run(debug=True)
    