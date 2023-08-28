import time
from MainApp import MainApp, SplashWindow

if __name__ == "__main__":
    import sys

    start = time.perf_counter()

    app = MainApp()

    splash = SplashWindow()
    splash.show()

    app.startup()
    app.show()

    splash.close()

    end = time.perf_counter()

    ms = (end - start) * 10 ** 6
    print(f"Elapsed {ms:.03f} micro secs.")

    sys.exit(app.app.exec_())


