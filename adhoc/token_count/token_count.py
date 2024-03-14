import click
import csv
from collections import Counter
from pathlib import Path
from string import punctuation
from tqdm import tqdm

# Add all unicode quotes to punctuation
PUNCTUATION = punctuation + "“”‘’«»„—–"


@click.command()
@click.argument("src_dir")
@click.argument("output_file")
@click.option(
    "--lower",
    is_flag=True,
    help="Convert tokens to lowercase before counting",
)
def count_tokens(src_dir: str, output_file: str, lower: bool) -> None:
    """Count tokens in all .txt files in all subdirectories of the source directory."""
    token_counter = Counter()
    txt_files = list(Path(src_dir).rglob("*.txt"))
    for txt_file in tqdm(txt_files, desc="Processing files"):
        with open(txt_file, "r") as file:
            for line in file:
                tokens = line.split()
                tokens = [token.strip(PUNCTUATION) for token in tokens]
                tokens = [token for token in tokens if token]
                if lower:
                    tokens = [token.lower() for token in tokens]
                token_counter.update(tokens)

    with open(output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Token", "Count"])
        for token, count in sorted(
            token_counter.items(), key=lambda item: item[1], reverse=True
        ):
            writer.writerow([token, count])

    print(f"Token counts have been written to {output_file}")


if __name__ == "__main__":
    count_tokens()
