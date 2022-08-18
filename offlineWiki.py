import reader

"""
Wikipedia scraper and reader
Scrapes wikipedia pages into text files, which are stored in a directory.
Leaves an index file and a navigator. File structure outlined below.
wikiscraper (dir)
| Navigator
| Articles (dir)
| | Index.txt
| | ...txt
| | ...txt
"""

if __name__ == '__main__':
    reader.Reader()
