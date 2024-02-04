import os
import pickle
import random
import re
from typing import List, Tuple, Optional
from copy import deepcopy


class Crossword:
    def __init__(
        self,
        width: int,
        height: int,
        horizontal_word: str,
        vertical_word: str,
        words_file: str,
    ):
        self.words = read_unique_words(words_file)
        self.width = width
        self.height = height
        self.crossword = self.create_crossword(horizontal_word, vertical_word)
        self.working_copy = None

    def create_crossword(
        self, horizontal_word: str, vertical_word: str
    ) -> List[List[str]]:
        if (
            len(horizontal_word) != self.width - 2
            or len(vertical_word) != self.height - 2
        ):
            raise ValueError(
                "Word lengths must match the crossword dimensions minus two for the block cells"
            )
        if horizontal_word[0] != vertical_word[0]:
            raise ValueError("The first letters of the words must match")

        # Create crossword with blocks at the end of each row
        crossword = [
            [" " for _ in range(self.width - 1)] + ["#"] for _ in range(self.height - 1)
        ]
        crossword[0] = ["#" for _ in range(self.width)]
        for i in range(self.height - 1):
            crossword[i][0] = "#"

        for i in range(1, self.width - 1):
            crossword[1][i] = horizontal_word[i - 1]
        for i in range(1, self.height - 1):
            crossword[i][1] = vertical_word[i - 1]

        # Add blocks at the end of the columns
        crossword.append(["#" for _ in range(self.width)])

        return crossword

    def find_matching_words(self, regex: str) -> List[str]:
        pattern = re.compile(rf"^{regex}$")
        matching_words = [word for word in self.words if pattern.match(word)]
        return matching_words

    def cell(self, row: int, col: int) -> str:
        return self.crossword[row][col]

    def find_first_empty(self) -> Optional[Tuple[int, int]]:
        for i, row in enumerate(self.crossword):
            for j, cell in enumerate(row):
                if cell == " ":
                    return (i, j)
        return None

    def get_horizontal_from_point(
        self, row: int, col: int
    ) -> Optional[Tuple[Tuple[int, int], List[str]]]:
        """Find next missing word in the crossword. Return None if no more words are missing."""
        end_col = start_col = col

        while start_col > 0 and self.crossword[row][start_col - 1] != "#":
            start_col -= 1
        while end_col < self.width and self.crossword[row][end_col + 1] != "#":
            end_col += 1

        cells = self.get_horizontal_cells(row, start_col, end_col)
        return (row, start_col), cells

    def get_vertical_from_point(
        self, row: int, col: int
    ) -> Optional[Tuple[Tuple[int, int], List[str]]]:
        """Find next missing word in the crossword. Return None if no more words are missing."""
        end_row = start_row = row

        while start_row > 0 and self.crossword[start_row - 1][col] != "#":
            start_row -= 1
        while end_row < self.height and self.crossword[end_row + 1][col] != "#":
            end_row += 1

        cells = self.get_vertical_cells(start_row, end_row, col)
        return (start_row, col), cells

    def get_horizontal_cells(self, row: int, start_col: int, end_col: int) -> List[str]:
        return self.crossword[row][start_col : end_col + 1]

    def get_vertical_cells(self, start_row: int, end_row: int, col: int) -> List[str]:
        cells = []
        for i in range(start_row, end_row + 1):
            cells.append(self.crossword[i][col])
        return cells

    def get_possible_characters_for_vertical_from_cell(
        self, row: int, col: int
    ) -> List[str]:
        vertical = self.get_vertical_from_point(row, col)
        if vertical is None:
            print("No vertical found")
            return []
        (start_row, _), cells = vertical
        regex = "".join(["." if cell == " " else cell for cell in cells])
        possible_words = self.find_matching_words(regex)
        return list(set([word[row - start_row] for word in possible_words]))

    def get_next_unknown(self):
        empty_cell = self.find_first_empty()

        print(empty_cell)
        if not empty_cell:
            print("No more empties!")
            return None
        row, col = empty_cell

        # Get cells of horizontal word
        horiz = self.get_horizontal_from_point(row, col)
        if horiz is None:
            print("No horiz found")
            return None
        (row, start_col), cells = horiz

        horiz_regex = r""
        for i in range(start_col, start_col + len(cells)):
            print(i)
            if self.cell(row, i) == " ":
                letters = self.get_possible_characters_for_vertical_from_cell(row, i)
                regex_letters = rf"[{r''.join(letters)}]"
                horiz_regex += regex_letters
            else:
                horiz_regex += self.cell(row, i)
        horiz_regex = rf"^{horiz_regex}$"
        print(horiz_regex)

        import ipdb

        ipdb.set_trace()

        # print(horiz)

        # verts = self.get_vertical_from_point(row, col)
        # print(verts)
        # if verts is None:
        #     print("No verts found")
        #     return None

        # (start_row, start_col), cells = verts

        # # Convert cells to string with . for unknown letters
        # unknown_word = "".join(["." if cell == " " else cell for cell in cells])
        # print(unknown_word)
        # fills = self.find_matching_words(unknown_word)
        # print(fills)
        # letter_idx = row - start_row
        # # Get unique letters for the letter_idx in fills
        # letters = set()
        # for fill in fills:
        #     letters.add(fill[letter_idx])
        # print(letters)

        # while self.crossword[row][col] != "#":

        # horiz = self.get_horizontal_from_point(*empty_cell)
        # if horiz is None:
        #     print("No horiz found")
        #     return None
        # (row, col), cells = horiz
        # print(horiz)


def read_unique_words(filepath: str) -> List[str]:
    pickle_filepath = "/tmp/FILENAME-TRIE.pickle"
    if os.path.exists(pickle_filepath):
        print("Loading trie from pickle")
        with open(pickle_filepath, "rb") as file:
            trie = pickle.load(file)
    else:
        print("Creating words list trie")
        with open(filepath, "r") as file:
            lines = file.readlines()
        words = [
            line.split("@")[0].lower()
            for line in lines
            if re.match("^[a-zæøå]+$", line.split("@")[0].lower())
        ]
        words = list(set(words))
    return words


def print_crossword(crossword: List[List[str]]) -> None:
    for row in crossword:
        print(" ".join(row))


if __name__ == "__main__":
    cw = Crossword(7, 7, "kaffe", "kinds", "/Users/nhs/Arkiv/ddo/aktuel_ddo_flex.txt")
    print(cw.crossword)
    print_crossword(cw.crossword)
    cw.get_next_unknown()
