import click
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt


@click.command()
@click.option(
    "--direction",
    default="random",
    type=click.Choice(["horizontal", "vertical", "random"], case_sensitive=False),
)
@click.option("--color", default="black")
@click.option("--background-color", default="white")
@click.option("--output-dir", default="/tmp")
@click.option("--file", type=click.Path(exists=True))
@click.option("--width", default=1000)
@click.option("--height", default=500)
@click.option("--name", default="wordcloud")
def generate_wordcloud(
    direction: str,
    color: str,
    background_color: str,
    output_dir: str,
    file: str,
    width: int,
    height: int,
    name: str,
):
    # Read the file
    with open(file, "r") as f:
        words = f.read().splitlines()

    words = [word for word in words if word != ""]
    words = [word.replace('"', "") for word in words]

    # Convert non-ascii characters to ascii
    # words = [re.sub(r"[^\x00-\x7F]+", "", word) for word in words]

    # Generate the wordcloud
    wordcloud = WordCloud(
        width=width,
        height=height,
        prefer_horizontal=_get_direction_ratio(direction),
        color_func=lambda *args, **kwargs: color,
        background_color=background_color,
        #        regexp=r"[^#][^#]+",
        regexp=r"[a-zæøåA-ZÆÆÅ][^#]+",
        collocations=False,
    ).generate("#".join(words))

    # Save to output directory
    wordcloud.to_file(f"{output_dir}/{name}.png")
    # wordcloud.to_file(f"{output_dir}/wordcloud.svg")


def _get_direction_ratio(direction: str) -> float:
    if direction == "horizontal":
        return 1.0
    elif direction == "vertical":
        return 0.0
    else:  # random
        return 0.5


if __name__ == "__main__":
    generate_wordcloud()
