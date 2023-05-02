import click
import re
from itertools import permutations, product
from typing import Dict, List, Union

substitution_rules = {
    r"(\w)\1": [r"\1"],  # remove double consonants
    r"nd": [r"nn", r""],  # remove double consonants
    r"ige": [r"ije", r"ie"],  # remove double consonants
    r"igh": [r"ih"],  # remove double consonants
    r"nd": r"nn",  # remove double consonants
    r"e(\b)": [r"er\1"],  # add "r" after "e" at the end of the word
    r"er$": [r"e"],  # remove "r" after "e" at the end of the word
    r"\b(v[^\W\d_]*?)": ["h\g<1>"],  # add "h" before "v" at the beginning of the word
}


@click.command()
@click.argument("input_file", type=click.File("r"))
def main(input_file):
    # substitution_rules = load_substitution_rules(rules_file)
    for line in input_file:
        word = line.strip()
        misspellings = get_misspellings(word, substitution_rules)
        output_str = f"{word},{','.join(misspellings)}"
        print(output_str)


def get_misspellings(
    word: str, substitution_rules: Dict[str, Union[str, List[str]]]
) -> List[str]:
    misspellings = set()

    # Convert single string substitutions to a list
    substitution_rules = {
        rule: (substitutions if isinstance(substitutions, list) else [substitutions])
        for rule, substitutions in substitution_rules.items()
    }

    # Apply all substitution rules to the word
    for rule, substitutions in substitution_rules.items():
        for substitution in substitutions:
            misspelling = re.sub(rule, substitution, word)
            misspellings.add(misspelling)

    # Generate all possible combinations of substitutions
    for rule_order in permutations(substitution_rules.keys(), len(substitution_rules)):
        for substitutions in product(
            *(substitution_rules[rule] for rule in rule_order)
        ):
            misspelling = word
            for rule, substitution in zip(rule_order, substitutions):
                misspelling = re.sub(rule, substitution, misspelling)
            misspellings.add(misspelling)

    # Remove the original word from the list of misspellings
    misspellings.discard(word)

    return list(misspellings)


def get_misspellings_old(
    word: str, substitution_rules: Dict[str, List[str]]
) -> List[str]:
    misspellings = set()

    # apply all substitution rules to the word
    for rule, substitutions in substitution_rules.items():
        for substitution in substitutions:
            misspelling = re.sub(rule, substitution, word)
            misspellings.add(misspelling)

    # generate all possible combinations of substitutions
    for rules in product(substitution_rules.keys(), repeat=len(substitution_rules)):
        if all(rule in word for rule in rules):
            continue  # skip combinations that would lead to an infinite loop
        for substitutions in product(*(substitution_rules[rule] for rule in rules)):
            misspelling = word
            for rule, substitution in zip(rules, substitutions):
                misspelling = re.sub(rule, substitution, misspelling)
            misspellings.add(misspelling)

    # remove the original word from the list of misspellings
    misspellings.discard(word)

    return list(misspellings)


if __name__ == "__main__":
    main()

# import re
# from itertools import product
# from typing import Dict, List


# def get_misspellings(word: str, substitution_rules: Dict[str, List[str]]) -> List[str]:
#     misspellings = set()

#     # apply all substitution rules to the word
#     for rule, substitutions in substitution_rules.items():
#         for substitution in substitutions:
#             misspelling = re.sub(rule, substitution, word)
#             misspellings.add(misspelling)

#     # generate all possible combinations of substitutions
#     for rules in product(substitution_rules.keys(), repeat=len(substitution_rules)):
#         if all(rule in word for rule in rules):
#             continue  # skip combinations that would lead to an infinite loop
#         for substitutions in product(*(substitution_rules[rule] for rule in rules)):
#             misspelling = word
#             for rule, substitution in zip(rules, substitutions):
#                 misspelling = re.sub(rule, substitution, misspelling)
#             misspellings.add(misspelling)

#     # remove the original word from the list of misspellings
#     misspellings.discard(word)

#     return list(misspellings)


# if __name__ == "__main__":
#     word = "komme"
#     misspellings = get_misspellings(word, substitution_rules)
#     print(misspellings)
