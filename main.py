import argparse


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Cube Classification Pipeline — fetch and classify a single Magic card."
    )
    parser.add_argument("card", help="Card name or identifier to look up")
    args = parser.parse_args(argv)
    print(f"Card identifier: {args.card}")


if __name__ == "__main__":
    main()
