import argparse

def main():
    parser = argparse.ArgumentParser(description="Your script description here.")
    parser.add_argument("--option", type=str, help="Example option")
    args = parser.parse_args()

    print("Hello, World!")
    if args.option:
        print(f"Option provided: {args.option}")

if __name__ == "__main__":
    main()