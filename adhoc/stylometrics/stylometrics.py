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


def get_documents(source_path):
    for root, dirs, files in os.walk(source_path):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    basename = os.path.basename(file_path)
                    if ".paragraphed" in basename:
                        basename = basename.split(".paragraphed")[0]
                    if "_" in basename:
                        author = basename.split("_")[1]
                        title = basename.split("_")[2]
                    else:
                        author = basename
                        title = basename
                    content = f.read().strip()

                    yield (author, f"{title}__1", content[: len(content) // 2])
                    yield (author, f"{title}__2", content[len(content) // 2 :])


def create_corpus(
    source_path: str,
    language: str = "da",
    force_new=False,
    do_calibrate: bool = True,
    save_file: str | None = None,
):
    if not save_file:
        temp_dir = gettempdir()
        pickle_file = os.path.join(temp_dir, os.path.basename(source_path) + ".pickle")
    else:
        if not save_file.endswith(".pickle"):
            save_file += ".pickle"
        pickle_file = save_file

    if os.path.exists(pickle_file) and not force_new:
        with open(pickle_file, "rb") as f:
            corpus = pickle.load(f)
        logger.info("Loaded corpus from pickle file")
    else:
        corpus = Corpus()
        logger.info("Reading documents")
        for author, title, content in get_documents(source_path):
            corpus.add_book(author, title, content)

        logger.info("Tokenising corpus")
        if language == "da":
            corpus.tokenise(tokenise_remove_pronouns_da)
        else:
            corpus.tokenise(tokenise_remove_pronouns_en)

        if do_calibrate:
            logger.info("Calibrating reference corpus")
            calibrate(corpus)

        logger.info("Saving corpus to pickle file")
        with open(pickle_file, "wb") as f:
            pickle.dump(corpus, f)
        logger.info("Created corpus and saved to pickle file")

        logger.info("Finished")
    return corpus


@click.command()
@click.option("--source-path", required=True, type=click.Path(exists=True))
@click.option("--work", multiple=True)
@click.option("--language", type=click.Choice(["da", "en"]), default="da")
@click.option("--force-new", type=bool, default=False, is_flag=True)
@click.option("--vocab-size", type=int, default=50)
@click.option("--save-file", type=str, default=None)
def main(source_path, work: List[str], language, force_new, vocab_size, save_file):
    reference_corpus = create_corpus(
        source_path, language, force_new, do_calibrate=True, save_file=save_file
    )
    work_corpus = Corpus()
    for work_file in work:
        with open(work_file, "r") as f:
            work_corpus.add_book(
                "unknown", os.path.basename(work_file), f.read().strip()
            )

        work_corpus.tokenise(tokenise_remove_pronouns_da)

    logger.info(f"Calculating Burrows' Delta with vocab size {vocab_size}")
    df_deltas = calculate_burrows_delta(
        reference_corpus, work_corpus, vocab_size=vocab_size
    )
    # Sort df_deltas by the first column, which is the Burrows' Delta values
    df_deltas.sort_values(by=df_deltas.columns[0], inplace=True, ascending=False)
    print(df_deltas)

    import ipdb

    ipdb.set_trace()


if __name__ == "__main__":
    main()
