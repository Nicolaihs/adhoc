import click
import re
from itertools import permutations, product
from typing import Dict, List, Set, Union


VOWEL = r"aeiouyæøå"
CONSONANT = r"bcdfghjklmnpqrstvwxz"

substitution_rules = {
    r"(\w)\1": [r"\1"],  # remove double consonants
    r"nd": [r"nn", r"n"],  # nd -> nn or n
    r"pp": [r"bb", r"b"],  # pp -> bb or b
    r"dt": [r"t", r"dt"],  # dt -> t or dt
    r"ige": [r"ije", r"ie"],  # ige -> ije or ie
    r"igh": [r"ih"],  # igh -> ih
    # r"g$": [r"k"],  # g -> k
    r"gt$": [r"kt", r"g"],  # gt -> kt, g
    r"k$": [r"g"],  # k -> g
    r"b$": [r"p"],  # b -> p
    r"p$": [r"b"],  # p -> b
    #    r"e$": [r"er"],  # add "r" after "e" at the end of the word
    r"er$": [r"e"],  # remove "r" after "e" at the end of the word
    r"^v": [r"hv"],  # add "h" before "v" at the beginning of the word
    r"^hv": [r"v"],  # remove "h" before "v" at the beginning of the word
    r"hj": [r"j"],  # hj -> j
    rf"c([{VOWEL}])": [r"s\1"],  # c -> s or k
    r"sc": [r"ss", r"s"],  # sc -> ss or s
    r"tiel": [r"siel", r"tjel"],  # tiel -> siel
    r"w": [r"v"],  # w -> v
    r"tion": [r"sjon", r"sion"],  # tion -> sjon
    r"nktion": [r"ngsjon", r"ngsion", r"nsion"],  # ktion -> ksjon
    r"nkt": [r"ngt"],  # nkt -> ngt
    r"et($|h)": [r"ed\1"],  # et -> ed
    r"([rj])æ": [r"\1e", r"\1a"],  # ræ -> re or ra
    r"ky": [r"kø"],
    r"z": [r"s"],
    r"ci": [r"si", r"sj"],
    r"mø": [r"my"],
    r"af": [r"av"],
    r"aner": [r"ander"],
    r"ikt": [r"igt"],
    r"ulgt": [r"ult"],
    r"ntlig": [r"nlig"],
    r"jer": [r"jær"],
    r"bonde": [r"bånne", r"bånde"],
    r"arkæ": [r"akæ"],
    r"ugl": [r"ul"],
    r"alv": [r"al"],
    r"tsj": [r"tsch", r"tch"],
}


@click.command()
@click.argument("input_file", type=click.File("r"))
def main(input_file) -> None:
    for line in input_file:
        word = line.strip()
        misspellings = apply_rules(word, substitution_rules)
        output_str = f"{','.join(misspellings)}"
        print(output_str)


def apply_rules(word: str, substitution_rules: Dict[str, List[str]]) -> List[str]:
    results = [word]

    for pattern, subs in substitution_rules.items():
        temp_results = results.copy()

        for result in results:
            for sub in subs:
                temp_result = re.sub(pattern, sub, result)
                if temp_result != result:
                    temp_results.append(temp_result)

        results = temp_results

    return list(set(results))  # Remove duplicates


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


if __name__ == "__main__":
    main()
