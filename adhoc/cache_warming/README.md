# Instructions for Downloading and Using the cache_warming Command-Line Utility

This script takes as input a text file containing a list of words, and performs a lookup for each word in the list. The script can be used to warm the cache of a web application, for example a dictionary, by performing lookups for a large number of words in a short amount of time.

The file may contain a list of words on each line, separated by a comma:

  word1,word2,word3,word4,word5
  word6
  word7,word8,word9

The `common_misspellings` utility can be used to create a file like this with common misspellings from a list of correctly spelled words.

## Step 1: Download the cache_warming Utility

- [Provide a download link to the utility's executable file or instructions to get it]

## Step 2: Open a Terminal or Command Prompt

- **Windows**: Press `Win + R`, type `cmd`, and press Enter
- **macOS**: Press `Cmd + Space`, type `Terminal`, and press Enter
- **Linux**: Press `Ctrl + Alt + T`

## Step 3: Using the cache_warming Utility

After opening the terminal, navigate to the directory where the `cache_warming` utility is located using the `cd` command, for example:
`cd C:\path\to\your\cache_warming_directory` or `cd Downloads/`

Now, you can run the command with the following syntax:
`cache_warming INPUT_FILE --delay=D --start-row=R --base-urls="URL_1,URL_2"`

Replace the parameters with the corresponding values as explained below:

- `INPUT_FILE`: Replace this with the name (and path if necessary) of the input_file for which you want to run cache_warming.
- `D`: Replace this with the desired delay (in seconds) between each lookup. Default value is 1 second.
- `R`: Replace this with the starting row number in your input file. Default value is 0.
- `URL_1,URL_2`: Replace this with a comma-separated list of base URLs to lookup. Use `{word}` as a placeholder where the query word should be inserted. The default value is `https://ordnet.dk/ddo/ordbog?={word}`.

### Example Usage

To use the utility with default options, type the following command in the terminal (replacing `your_input_file.txt` with the name of your input file):
`cache_warming your_input_file.txt`

To customize options, you can use a command like the following:
cache_warming your_input_file.txt --delay=2 --start-row=10 --base-urls="<https://ordnet.dk/ddo/ordbog?={word}>,<https://ordnet.dk/ddo/ordbog/?query={word}>"
