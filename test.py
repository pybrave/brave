import typer,click
print(typer.__version__)
print(click.__version__)

def main(name: str):
    print(f"Hello {name}")


if __name__ == "__main__":
    typer.run(main)