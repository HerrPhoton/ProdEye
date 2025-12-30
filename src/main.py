from .app.bootstrap import bootstrap


def main():
    pipeline = bootstrap()

    while True:
        pipeline.run_once()

if __name__ == "__main__":
    main()
