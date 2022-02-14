import os
import dotenv
dotenv.load_dotenv()

if not os.path.isfile('skin_model.h5'):
        os.system('sh downloadSkinModel.sh')

from index import app
# run 
if __name__ == '__main__': 
        app.run()
