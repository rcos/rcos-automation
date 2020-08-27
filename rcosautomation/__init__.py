from dotenv import load_dotenv
load_dotenv()
import os

from .views import app

if __name__ == '__main__':
    app.run(threaded=True, port=os.environ.get('PORT'))