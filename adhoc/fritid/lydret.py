from doctest import debug
import click
import csv
from itertools import product
from typing import List, Tuple


CONVERSIONS = [
    ("ɑ̃", "~a"),
    ("ɑ̃", "~q"),
    ("ɶ̃", "~Ø"),
    ("ɶ̃", "~C"),
    ("ɒ̃", "~å"),
    ("i", "i"),
    ("e", "e"),
    ("ε", "æ"),
    ("æ", "A"),
    ("a", "a"),
    ("ɑ", "q"),
    ("a", "W"),
    ("a", "ä"),
    ("y", "y"),
    ("ø", "ø"),
    ("œ", "Ø"),
    ("ɶ", "C"),
    ("u", "u"),
    ("o", "o"),
    ("ɔ", "Å"),
    ("ɒ", "å"),
    ("ʌ", "c"),
    ("ə", "E"),
    ("b", "b"),
    ("d", "d"),
    ("ð", "D"),
    ("f", "f"),
    ("g", "g"),
    ("h", "h"),
    ("j", "5"),
    ("j", "J"),
    ("k", "k"),
    ("l", "l"),
    ("m", "m"),
    ("n", "n"),
    ("ŋ", "G"),
    ("p", "p"),
    ("ʁ", "r"),
    ("ɐ̯", "R"),
    ("s", "s"),
    ("ɕ", "S"),
    ("t", "t"),
    ("w", "w"),
    ("v", "v"),
    ("ɹ", "7"),
    ("χ", "Þ"),
    ("ç", "Ü"),
    ("ʃ", "$"),
    ("θ", "þ"),
]

# A list of letters with there most expected phonetic transcription
MOST_EXPECTED = [
    ("a", ["a", "æ", "ɑ"]),
    ("b", ["b"]),
    #    ("c", ["k", "s"]),
    ("d", ["d"]),
    ("e", ["e"]),
    ("f", ["f"]),
    ("g", ["g"]),
    ("h", ["h"]),
    ("i", ["i"]),
    ("j", ["j"]),
    ("k", ["g", "k"]),
    ("l", ["l"]),
    ("m", ["m"]),
    ("n", ["n"]),
    ("o", ["o"]),
    ("p", ["p", "b"]),
    #    ("q", ["k", "g"]),
    ("r", ["ʁ"]),
    ("s", ["s"]),
    ("t", ["t", "d"]),
    ("u", ["u", "w"]),
    ("v", ["v"]),
    #    ("w", ["v", "w"]),
    ("x", ["ks"]),
    ("y", ["y"]),
    ("z", ["s"]),
    ("æ", ["ε"]),
    ("ø", ["ø"]),
    ("å", ["ɒ"]),
]


def load_fonliste(filename) -> List[dict]:
    """Loads a CSV file with phonetic transcriptions in SAMPA format and converts them to IPA."""
    # Open the CSV file and read the data
    with open(filename, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(
            csvfile,
            delimiter="\t",
            fieldnames=["entry_id", "word", "phonetic_transcription"],
        )
        data = []
        for row in reader:
            # Convert the phonetic transcription from SAMPA to IPA
            phonetic_transcription = row["phonetic_transcription"]
            ipa_transcription = phonetic_transcription
            for api, ascii in CONVERSIONS:
                ipa_transcription = ipa_transcription.replace(ascii, api)
            stress_symbols = ["ˈ", "ˌ", "H", "Z", ";"]
            for stress_symbol in stress_symbols:
                ipa_transcription = ipa_transcription.replace(stress_symbol, "")
            row["ipa"] = ipa_transcription
            data.append(row)

    return data


def filter_words_by_pronunciation_old(
    words: List[dict], expected: List[Tuple[str, List[str]]]
) -> List[dict]:
    expected_pronunciations = {}
    for char, pronunciations in expected:
        for p in pronunciations:
            expected_pronunciations.setdefault(char, []).append(p)

    filtered_words = []

    for word in words:
        char_possibilities = [
            expected_pronunciations.get(char, "#") for char in word["word"]
        ]
        possible_pronunciations = ["".join(p) for p in product(*char_possibilities)]
        print(possible_pronunciations)
        if word["ipa"] in possible_pronunciations:
            filtered_words.append(word)

    return filtered_words


def filter_words_by_pronunciation(
    words: List[dict],
    expected: List[Tuple[str, List[str]]],
    debug_word: str | None = None,
) -> Tuple[List[dict], dict]:
    expected_pronunciations = {}
    for char, pronunciations in expected:
        for p in pronunciations:
            expected_pronunciations.setdefault(char, []).append(p)

    filtered_words = []
    count_chars_unexpected = {}

    for word in words:
        char_possibilities = [
            expected_pronunciations.get(char, "#") for char in word["word"]
        ]
        possible_pronunciations = ["".join(p) for p in product(*char_possibilities)]

        # Handle double consonants
        consonants = [
            "mm",
            "nn",
            "pp",
            "tt",
            "kk",
            "bb",
            "dd",
            "gg",
            "ff",
            "ss",
            "vv",
            "zz",
            "jj",
            "ll",
            "rr",
        ]
        new = []
        for p in possible_pronunciations:
            new.append(p)
            for consonant in consonants:
                if consonant in p:
                    new.append(p.replace(consonant, consonant[0]))
        possible_pronunciations = new
        if debug_word and debug_word == word["word"]:
            print(possible_pronunciations)
        if word["ipa"] in possible_pronunciations:
            filtered_words.append(word)
        else:
            chars_unexpected = [
                char
                for char, ipa in zip(word["word"], word["ipa"])
                if ipa not in expected_pronunciations.get(char, [])
            ]
            chars_unexpected_count = {
                char: chars_unexpected.count(char) for char in chars_unexpected
            }
            count_chars_unexpected[word["word"]] = chars_unexpected_count

    return filtered_words, count_chars_unexpected


@click.group()
def cli():
    pass


@cli.command()
@click.argument("filepath")
@click.option("--word", default=None, help="Filter output to only include this word")
@click.option(
    "--show-unexpecteds", default=False, help="Filter output to only include this word"
)
def filter(filepath: str, word: str | None = None, show_unexpecteds: bool = False):
    words = load_fonliste(filepath)
    if word:
        print(f"Data for word: {word}")
        founds = [w for w in words if w["word"] == word]
        print(founds)
    filtered_words, unexpecteds = filter_words_by_pronunciation(
        words, MOST_EXPECTED, debug_word=word
    )
    for fword in filtered_words:
        if not word:
            print(fword["word"], fword["ipa"])
        else:
            if fword["word"] == word:
                print(fword["word"], fword["ipa"])

    if word:
        print("Unexpected:")
        print(unexpecteds.get(word, ""))

    if show_unexpecteds:
        print("Unexpected:")
        for word, unexpected in unexpecteds.items():
            print(word, unexpected)


#    print("Unexpected:")
#    for word, unexpected in unexpecteds.items():
#        print(word, unexpected)


if __name__ == "__main__":
    filter()
