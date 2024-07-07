# -----------------------------------------------------------------------------
# Copyright contributors to the SAX4BPM project
# -----------------------------------------------------------------------------
from . import create_app

if __name__ == "__main__":
    app = create_app()     
    #when running in Flask config in VScode, make sure what is the flask config port in .vscode/launch.json 
    app.run(host="0.0.0.0",port=9801)