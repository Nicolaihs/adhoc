from collections import Counter
from typing import List, Set


def read_definitions(file_path: str) -> List[str]:
    with open(file_path, "r") as file:
        definitions = file.readlines()
    return [
        definition.strip()
        .replace(",", "")
        .replace("(", "")
        .replace(")", "")
        .replace(";", "")
        .replace(":", "")
        for definition in definitions
    ]


def read_dictionary_forms(file_path: str) -> Set[str]:
    with open(file_path, "r") as file:
        forms = []
        for row in file:
            if not "@" in row:
                continue
            form = row.split("@")[0]
            forms.append(form)
        forms = [form.split("@")[0] for form in forms]

    return set(form.strip() for form in forms)


def find_lexical_gaps_by_definitions(
    definitions: List[str], dictionary: Set[str], threshold: int = 5
) -> List[str]:
    definition_words = []
    for definition in definitions:
        definition_words.extend(definition.split())
    word_counts = Counter(definition_words)
    lexical_gaps = [
        (word, count)
        for word, count in word_counts.items()
        if count > threshold and word not in dictionary
    ]
    return lexical_gaps


if __name__ == "__main__":
    # Example usage
    definitions_file = "/Users/nhs/arkiv/ddo/definitions.txt"
    forms_file = "/Users/nhs/arkiv/ddo/aktuel_ddo_flex.txt"

    definitions = read_definitions(definitions_file)
    dictionary_forms = read_dictionary_forms(forms_file)
    lexical_gaps = find_lexical_gaps_by_definitions(definitions, dictionary_forms, 0)

    # Sort by frequency
    lexical_gaps.sort(key=lambda x: x[1], reverse=True)
    for word, count in lexical_gaps:
        if word[0].isupper():
            continue
        if word[-1] == "-":
            continue
        print(f"{word}: {count}")
