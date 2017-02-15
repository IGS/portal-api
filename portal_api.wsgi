import sys
from conf import app_root
from app import application

sys.path.append(app_root)

if __name__ == "__main__":
    application.run()
