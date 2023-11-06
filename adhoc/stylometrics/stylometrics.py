import click
import logging
import os
import pickle
import re
from faststylometry import Corpus
from faststylometry import load_corpus_from_folder
from faststylometry import tokenise_remove_pronouns_en
from faststylometry import calculate_burrows_delta
from faststylometry import predict_proba, calibrate
from tempfile import gettempdir
from sklearn.linear_model import LogisticRegression
from typing import List

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
logger.info("Started")


pronouns = {
    "da": [
        "han",
        "hans",
        "hun",
        "hende",
        "hendes",
        "den",
        "det",
        "jeg",
        "mig",
        "du",
        "dig",
        "vi",
        "os",
        "jer",
        "de",
        "dem",
        "min",
        "mit",
        "mine",
        "din",
        "dit",
        "dine",
        "sin",
        "sit",
        "sine",
        "vores",
        "jeres",
        "deres",
        "sig",
    ]
}

re_words = re.compile(r"\w+")
is_number_pattern = re.compile(r".*\d.*")


def tokenise_remove_pronouns_da(text: str) -> list:
    """
    Tokenise a sentence according to English rules, and remove all pronouns.
    Remove all apostrophes since words like don't etc can be written in nonstandard ways.

    :param text: the original sentence.
    :return: all non-pronoun tokens.
    """
    text_normalised = re.sub("['’]", "", text.lower())
    tokens = [
        tok
        for tok in re_words.findall(text_normalised)
        if not is_number_pattern.match(tok)
    ]

    tokens_without_stopwords = [tok for tok in tokens if tok not in pronouns["da"]]

    return tokens_without_stopwords


def split_text(text: str, splits: int = 2) -> List[str]:
    if splits == 1:
        return [text]
    elif splits == 2:
        return [text[: len(text) // 2], text[len(text) // 2 :]]
    elif splits == 3:
        return [
            text[: len(text) // 3],
            text[len(text) // 3 : (2 * len(text)) // 3],
            text[(2 * len(text)) // 3 :],
        ]
    else:
        raise ValueError("Splits must be 1, 2 or 3")


def get_documents(
    source_path,
    splits: int = 2,
    skips: List[str] | None = None,
    no_authors: bool = False,
):
    for root, _, files in os.walk(source_path):
        for file in files:
            if skips:
                skip_it = False
                for skip in skips:
                    if file == skip:
                        skip_it = True
                        break
                    if "*" in skip and re.search(rf"{skip}", file):
                        skip_it = True
                        break
                if skip_it:
                    logger.info(f"Skipping {file}")
                    continue
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    basename = os.path.basename(file_path)
                    if ".paragraphed" in basename:
                        basename = basename.split(".paragraphed")[0]
                    if no_authors:
                        author = basename
                        title = basename
                    elif "_" in basename:
                        author = basename.split("_")[1]
                        title = basename.split("_")[2]
                    elif re.search(r"\d\.txt$", basename):
                        author = re.sub(r" *\d\.txt$", "", basename)
                        title = basename
                    elif basename.endswith(".txt"):
                        author = basename.replace(".txt", "")
                        title = basename
                    else:
                        author = basename
                        title = basename
                    content = f.read().strip()

                    for i, split in enumerate(split_text(content, splits)):
                        yield (author, f"{title}__{i}", split)
                    # if splits == 1:
                    #     yield (author, title, content)
                    # elif splits == 2:
                    #     yield (author, f"{title}__1", content[: len(content) // 2])
                    #     yield (author, f"{title}__2", content[len(content) // 2 :])
                    # elif splits == 3:
                    #     yield (author, f"{title}__1", content[: len(content) // 3])
                    #     yield (
                    #         author,
                    #         f"{title}__2",
                    #         content[len(content) // 3 : (2 * len(content)) // 3],
                    #     )
                    #     yield (
                    #         author,
                    #         f"{title}__3",
                    #         content[(2 * len(content)) // 3 :],
                    #     )
                    # else:
                    #     raise ValueError("Splits must be 1, 2 or 3")


def get_corpus_filepath(name: str, save_dir: str | None) -> str:
    if not save_dir:
        save_dir = gettempdir()
    pickle_file = os.path.join(save_dir, f"{name}_burrows.pickle")
    return pickle_file


def create_corpus(
    name: str,
    source_path: str,
    skips: List[str] | None = None,
    language: str = "da",
    do_calibrate: bool = True,
    save_dir: str | None = None,
    splits: int = 2,
    no_authors: bool = False,
):
    pickle_file = get_corpus_filepath(name, save_dir)
    corpus = Corpus()
    logger.info("Reading documents")
    for author, title, content in get_documents(
        source_path, splits=splits, skips=skips, no_authors=no_authors
    ):
        corpus.add_book(author, title, content)

    logger.info("Tokenising corpus")
    if language == "da":
        corpus.tokenise(tokenise_remove_pronouns_da)
    else:
        corpus.tokenise(tokenise_remove_pronouns_en)

    if do_calibrate:
        logger.info("Calibrating reference corpus")
        calibrate(corpus)

    logger.info(f"Saving corpus to pickle file to {pickle_file}")
    with open(pickle_file, "wb") as f:
        pickle.dump(corpus, f)
    logger.info("Created corpus and saved to pickle file")

    logger.info("Finished")
    return corpus


def load_reference_corpus(name: str, save_dir: str | None):
    pickle_file = get_corpus_filepath(name, save_dir)

    logger.info(f"Loading reference corpus from pickle file {pickle_file}")
    with open(pickle_file, "rb") as f:
        corpus = pickle.load(f)
    return corpus


@click.group()
def cli():
    pass


@click.command()
@click.option("--name", type=str, required=True)
@click.option("--source-path", required=True, type=click.Path(exists=True))
@click.option("--skip", type=str, multiple=True)
@click.option("--language", type=click.Choice(["da", "en"]), default="da")
@click.option("--save-dir", type=click.Path(exists=True))
@click.option("--splits", type=int, default=2)
@click.option("--no-authors", type=bool, default=False)
def create(name, source_path, skip, language, save_dir, splits, no_authors):
    create_corpus(
        name,
        source_path,
        language=language,
        skips=skip,
        do_calibrate=True,
        save_dir=save_dir,
        splits=splits,
        no_authors=no_authors,
    )


@click.command()
@click.option("--work", multiple=True)
@click.option("--reference-name", required=True)
@click.option("--source-path", type=click.Path(exists=True))
@click.option("--skip", type=str, multiple=True)
@click.option("--vocab-size", type=int, default=50)
@click.option("--language", type=click.Choice(["da", "en"]), default="da")
@click.option("--save-dir", type=click.Path(exists=True))
@click.option("--splits", type=int, default=1)
@click.option("--no-authors", type=bool, default=False)
def analyze(
    work,
    reference_name,
    source_path,
    skip,
    vocab_size,
    language,
    save_dir,
    splits,
    no_authors,
):
    if source_path:
        skips = list(skip) + [os.path.basename(item) for item in work]
        reference_corpus = create_corpus(
            reference_name,
            source_path,
            language=language,
            skips=skips,
            do_calibrate=True,
            save_dir=save_dir,
            splits=splits,
            no_authors=no_authors,
        )
    else:
        reference_corpus = load_reference_corpus(reference_name, save_dir=save_dir)
    work_corpus = Corpus()
    for work_file in work:
        with open(work_file, "r") as f:
            name = os.path.basename(work_file)
            work_corpus.add_book("unknown", name, f.read().strip())
            # for i, split in enumerate(split_text(f.read().strip(), splits=splits)):
            #     work_corpus.add_book(
            #         "unknown", splits > 1 and f"{name}__{i}" or name, split
            #     )

        work_corpus.tokenise(tokenise_remove_pronouns_da)

    logger.info(f"Calculating Burrows' Delta with vocab size {vocab_size}")
    df_deltas = calculate_burrows_delta(
        reference_corpus, work_corpus, vocab_size=vocab_size
    )
    # Sort df_deltas by the first column, which is the Burrows' Delta values
    df_deltas.sort_values(by=df_deltas.columns[0], inplace=True, ascending=True)
    print(df_deltas)

    logger.info("Calculating probabilities")
    probs = predict_proba(reference_corpus, work_corpus)
    probs.sort_values(by=probs.columns[0], inplace=True, ascending=False)
    print(probs)

    import ipdb

    ipdb.set_trace()


cli.add_command(create)
cli.add_command(analyze)

if __name__ == "__main__":
    cli()
