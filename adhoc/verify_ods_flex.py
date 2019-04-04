"""Verify a ODS flex list."""

import argparse
import csv
import re

def argparser():
    """Handle command-line arguments."""
    aparser = argparse.ArgumentParser(description=__file__.__doc__)
    aparser.add_argument('--source-file', '-s', required=True,
                         help='Source filepath')
    aparser.add_argument('--target-file', '-o',
                         help='Source filepath')
    return aparser

def main(args):
    """Main loop."""
    entries = {}
    with open(args.source_file, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='@')
        for row in csv_reader:
            # -dømme@@60160497@flex@-dømme@@prim@a@----@
            form, _dummy, entry_id, _origin, lemma, homno, status, prior, pos = row[:9]
            if (entry_id, lemma, pos) not in entries:
                entries[(entry_id, lemma, pos)] = list()
            entries[(entry_id, lemma, pos)].append((form, status))

    candidates = []
    for (entry_id, lemma, pos), forms in entries.items():
        if pos == 'sb.' \
            and lemma[-1] != '-' \
            and len(forms) < 4:
            candidates.append(re.sub(r',\d+', r'', lemma))

    reversed = [candidate[::-1] for candidate in candidates]
    reversed.sort()
    backwardssorted = [candidate[::-1] for candidate in reversed]
    if args.target_file:
        out_file = open(args.target_file, 'w')
    for candidate in backwardssorted:
        print(candidate)
        if args.target_file:
            out_file.write('%s\n' % candidate)
    if args.target_file:
        out_file.close()

    import ipdb; ipdb.set_trace()


if __name__ == "__main__":
    PARSER = argparser()
    ARGS = PARSER.parse_args()
    main(ARGS)
