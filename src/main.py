import time
from MainApp import MainApp, SplashWindow

if __name__ == "__main__":
    import sys

    app = MainApp()

    splash = SplashWindow()
    splash.show()

    app.startup()
    app.show()

    splash.close()

    sys.exit(app.app.exec_())


