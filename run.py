import os
import dotenv
dotenv.load_dotenv()

if not os.path.isfile('model.h5'):
        os.system('sh downloadModel.sh')

from index import app
# run 
if __name__ == '__main__': 
        app.run()
