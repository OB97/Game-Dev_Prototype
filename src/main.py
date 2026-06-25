from src.core.engine import Engine


def main():
    # Instantiate and start our core game engine loop
    game = Engine(width=1024, height=768, title="Wizard")
    game.run()


if __name__ == "__main__":
    main()
