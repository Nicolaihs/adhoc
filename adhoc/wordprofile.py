# -*- coding: utf-8 -*-
"""Count words in corpus, year by year"""

import argparse
import logging
import os
import pandas as pd
from collections import Counter
from bounter import HashTable, bounter
from itertools import chain
from string import punctuation


# set up logging so we see what's going on
logging.basicConfig(
    format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO
)


def argparser():
    """Handle command-line arguments."""
    aparser = argparse.ArgumentParser(description=__file__.__doc__)
    aparser.add_argument("--source-path", "-s", help="Source path")
    aparser.add_argument(
        "--table-storage",
        "-t",
        required=True,
        default="/tmp/wordprofile.pandas",
        help="Filepath to storage table",
    )
    aparser.add_argument(
        "--frequency-table-file", help="Filepath for storage of total frequency table."
    )
    aparser.add_argument(
        "--output-file", "-o", help="Filepath to storage lemmacandidates"
    )
    aparser.add_argument(
        "--minimum-frequency",
        "-mf",
        type=int,
        default=50,
        help="Minimum total frequency",
    )
    aparser.add_argument(
        "--initial-zero-cols",
        "-zc",
        type=int,
        default=3,
        help="Number of years word did not exists",
    )
    aparser.add_argument(
        "--keep-characters",
        "-kc",
        help="Special characters to keep from tokens (punctuation is otherwise stripped)",
    )
    aparser.add_argument("--word", help="Choose a single word (for debugging purposes)")
    return aparser


def ppm(freq, size):
    """Return parts-per-million"""
    return (freq / size) * 1000000


def countInFile(filename, keep_characters):
    puncts = punctuation + "«»"
    if keep_characters:
        for char in keep_characters:
            puncts = puncts.replace(char, "")
    with open(filename) as f:
        table = str.maketrans("", "", puncts)
        linewords = (line.translate(table).lower().split() for line in f)
        return Counter(chain.from_iterable(linewords))


def count_corpus(dirname, keep_characters):
    """Count all words in corpus (with root dir)"""
    dirnames = [
        dirname,
    ]
    counts = bounter(size_mb=256)  # Counter()
    no_of_docs = 0
    i = 0
    while i < len(dirnames):
        dirname = dirnames[i]
        for fname in sorted(os.listdir(dirname)):
            if os.path.isdir(os.path.join(dirname, fname)):
                dirnames.append(os.path.join(dirname, fname))
                logging.info(
                    "... adding directory to subcorpus: %s "
                    % os.path.join(dirname, fname)
                )
            else:
                no_of_docs += 1
                counts.update(
                    countInFile(os.path.join(dirname, fname), keep_characters)
                )
                if no_of_docs % 1000 == 0:
                    logging.info("... %s documents considered" % no_of_docs)
        i += 1
    return counts


def main(args):
    """Main loop"""
    if args.source_path:
        table = process_corpus(args)
    else:
        logging.info("Loading counts...")
        table = pd.read_pickle(args.table_storage)
        logging.info("..finished")

    col_sums = []
    logging.info("Corpus info:")
    for column in table:
        col_sums.append(table[column].sum())
        logging.info("- %s: %s tokens" % (column, table[column].sum()))

    if args.frequency_table_file:
        frequency_table(args, table)

    lemma_candidates(args, table, col_sums)


def lemma_candidates(args, table, col_sums):
    """Loop through table, finding lemma candidates"""
    logging.info("Looping through table identifying lemma candidates")
    logging.info("-- minimum frequency: %s" % args.minimum_frequency)
    logging.info("-- initial zero cols: %s" % args.initial_zero_cols)
    with open(args.output_file, "w") as foutput:
        # Get col names from pandas table
        colnames = table.columns.tolist()
        foutput.write(f"word;total_freq;{';'.join(colnames)}\n")
        for index, data in table.iterrows():
            if args.word and index != args.word:
                continue
            vector = data.tolist()
            if args.initial_zero_cols and any(data[: args.initial_zero_cols]):
                #                logging.info(f"Skipping {index} due to initial zero cols {vector}")
                continue
            if args.minimum_frequency and sum(vector) < args.minimum_frequency:
                #                logging.info(
                #                   f"Skipping {index} due to minimum frequency {vector}: {sum(vector)}"
                #              )
                continue

            out = f"{index};{sum(vector)};{';'.join(map(str, vector))}\n"
            foutput.write(out)
    #            print(out)
    logging.info("... finished.")


def frequency_table(args, table):
    """Store sums for each token in csv table"""
    logging.info("Storing frequency table (%s)" % args.frequency_table_file)
    foutput = open(args.frequency_table_file, "w")
    for index, data in table.iterrows():
        if ";" in index:
            continue
        vector = data.tolist()

        out = "%s;%s;%s\n" % (index, ";".join(map(str, vector)), sum(vector))
        foutput.write(out)
    foutput.close()
    logging.info("... finished.")


def process_corpus(args):
    root_dir = args.source_path
    table = pd.DataFrame()
    for fname in sorted(os.listdir(root_dir)):
        if os.path.isdir(os.path.join(root_dir, fname)):
            logging.info("Counting subcorpus %s" % (os.path.join(root_dir, fname)))
            counts = count_corpus(os.path.join(root_dir, fname), args.keep_characters)

            new = pd.DataFrame(
                data=list(dict(counts).values()),
                index=list(dict(counts).keys()),
                columns=[fname],
            )

            table = pd.concat([table, new], axis=1)
            table = table.fillna(0)
            for column in table:
                table[column] = pd.to_numeric(table[column], downcast="integer")
            # logging.info(u'... top: %s' % counts[fname].most_common(10))
    #            logging.info(u'... no_of_words: %s' % sum(corpora[fname].values()))
    #                doc = open(os.path.join(dirname, fname)).read()
    #                doc = unicodify(doc)
    #                doc = doc.lower()

    #                for line in sentences:
    #                    yield line.split()
    table.to_pickle(args.table_storage)
    return table


if __name__ == "__main__":
    PARSER = argparser()
    ARGS = PARSER.parse_args()
    main(ARGS)
