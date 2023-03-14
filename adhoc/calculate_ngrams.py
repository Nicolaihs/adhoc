#!/usr/bin/python
# -*- coding: utf8 -*-
"""Train a ngram model from a given (raw) text corpus"""

import argparse
import json
import logging

# import nltk.data
import os
import re
import string
import tempfile
from gensim.models.phrases import Phrases, Phraser

from adhoc import logger

# TODO: Add chi-square scorer:
# from scipy.stats import chi2_contingency
# ... scoring=chi2_contingency
# TODO: Add t-test scorer:
# from scipy.stats import ttest_ind


def argparser():
    """Handle command-line arguments."""
    aparser = argparse.ArgumentParser(description=__file__.__doc__)
    aparser.add_argument("--source-path", "-s", help="Source path")
    aparser.add_argument(
        "--model-file", "-n", required=True, help="Filepath to model file"
    )
    aparser.add_argument(
        "--min-count", "-m", type=int, default=5, help="Minimum occurence of words"
    )
    aparser.add_argument("--threshold", "-t", type=float, default=7, help="Threshold")
    aparser.add_argument("--scorer", default="default", help="Scorer (default / npmi)")
    aparser.add_argument(
        "--connector-words",
        help="Use these connector words. If omitted, use default list",
    )
    aparser.add_argument("--keep-chars", help="Special characters to keep")
    aparser.add_argument("--export-file", help="Export to this file.")
    return aparser


CONNECTOR_WORDS = "og i det at en til på af der de den med for ikke jeg som har så var et han om men vi kan man sig fra ved hun skal også havde eller du vil være da ud nu hvor blev kunne noget over efter når meget op jo år selv mig hvad hvis dem her sin alle sådan mange have ham få to mere skulle ind bliver godt hans været deres andre altså må ja kun ville end nogle lidt min lige helt mod denne kom hele sammen går under egen eget egne of al alt sir hr fru frk mr mrs ms miss the næste pr st bl ganske godt god".split()


# class OldMySentences(object):
#     """Memory-friendly iterator.

#     Based on https://rare-technologies.com/word2vec-tutorial/"""

#     def __init__(self, dirname, keep_chars=None):
#         self.root_dir = dirname
#         self.dirnames = dirname.split(",")
#         self.tokenizer = nltk.data.load("tokenizers/punkt/danish.pickle")
#         punctuation = string.punctuation
#         punctuation += "«»"
#         if keep_chars:
#             for char in keep_chars:
#                 punctuation = punctuation.replace(char, "")
#         self.subregex = re.compile("[%s]" % re.escape(punctuation))

#     def __iter__(self):
#         i = 0
#         while i < len(self.dirnames):
#             dirname = self.dirnames[i]
#             for fname in os.listdir(dirname):
#                 if os.path.isdir(os.path.join(dirname, fname)):
#                     logging.info("Dir added: %s" % os.path.join(dirname, fname))
#                     self.dirnames.append(os.path.join(dirname, fname))
#                 else:
#                     if fname[0] in (".",):
#                         logging.info("File %s skipped" % os.path.join(dirname, fname))
#                         continue
#                     doc = open(os.path.join(dirname, fname), encoding="utf-8").read()
#                     doc = doc.lower()
#                     doc = self.subregex.sub("", doc)
#                     sentences = self.tokenizer.sentences_from_text(doc)
#                     for line in sentences:
#                         yield line.split()
#             i += 1


def clean_up_sentence(sentence: str, keep_chars: str = "") -> str:
    """Remove punctuation and make lowercase."""
    punctuation = string.punctuation
    punctuation += "«»"
    if keep_chars:
        for char in keep_chars:
            punctuation = punctuation.replace(char, "")
    subregex = re.compile("[%s]" % re.escape(punctuation))
    sentence = sentence.lower()
    sentence = subregex.sub("", sentence)
    return sentence


class MySentences(object):
    def __init__(self, dirname, keep_chars: str = ""):
        self.dirnames = [dirname]
        self.keep_chars = keep_chars

    def __iter__(self):
        for dirname in self.dirnames:
            for fname in os.listdir(dirname):
                if fname[0] in (".",):
                    logging.info("File %s skipped" % os.path.join(dirname, fname))
                    continue
                if os.path.isdir(os.path.join(dirname, fname)):
                    logging.info("Dir added: %s" % os.path.join(dirname, fname))
                    self.dirnames.append(os.path.join(dirname, fname))
                    continue
                #                print(os.path.join(dirname, fname))
                for line in open(os.path.join(dirname, fname)):
                    line = clean_up_sentence(line, self.keep_chars)
                    yield line.split()


def main(args):
    """Setup corpus and create model."""
    if args.source_path:
        # set up the streamed corpus
        sentences = MySentences(args.source_path, keep_chars=args.keep_chars)
        if args.connector_words:
            connector_words = args.connector_words.split(",")
        else:
            connector_words = CONNECTOR_WORDS
        logger.info(f"The following connector words are used: {connector_words}")
        phrases = Phrases(
            sentences,
            min_count=args.min_count,
            threshold=args.threshold,
            progress_per=100_000,
            scoring=args.scorer,
            connector_words=frozenset(connector_words),
        )
        model = Phraser(phrases)
        model.save(args.model_file)
    else:
        model = Phraser.load(args.model_file)

    if args.export_file:
        logger.info(f"Exporting phrasegrams to {args.export_file}")
        export = {
            "size": len(model.phrasegrams),
            "scorer": model.scoring.__name__,
            "threshold": model.threshold,
            "min_count": model.min_count,
            "delimiter": model.delimiter,
            "connector_words": list(model.connector_words),
            "phrasegrams": model.phrasegrams,
        }
        with open(args.export_file, "w") as export_file:
            export_file.write(json.dumps(export))


if __name__ == "__main__":
    PARSER = argparser()
    ARGS = PARSER.parse_args()
    main(ARGS)
