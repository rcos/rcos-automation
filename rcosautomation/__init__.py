from .views import app
import os
from dotenv import load_dotenv
load_dotenv()


if __name__ == '__main__':
    app.run(threaded=True, port=os.environ.get('PORT'))
