# The Beatles song titles network

Data and code for the paper

> G. Budel and R. E. Kooij, *Any time at All you need is Love me Do you want to know a Secret:
> Chains in the Beatles Song Titles Network*.

A chain of Beatles song titles is a sequence of titles in which each title begins with the word
the previous one ended on, as in *Get Back* followed by *Back In The U.S.S.R.* Written as a
network, every song title of at least two words becomes a link running from a node that holds its
first word to a node that holds its last word, carrying the words in between as its label. A chain
is then a trail of that network: a walk that may pass through a node more than once but never uses
a link twice, so that no song is repeated. The longest chain of Beatles song titles is the longest
trail of the network.

This repository contains the edge list of the network and a single script that reproduces every
number and every chain reported in the paper.

## Contents

| File | Description |
| --- | --- |
| `beatles_chains.py` | Builds the network and runs the searches; prints the results of Sections 3 to 6 |
| `data/beatles_song_titles.csv` | The 276 song titles as an edge list; the input the script reads |
| `data/beatles_song_titles.txt` | The same table in fixed-width columns, for reading without a spreadsheet |
| `requirements.txt` | Python dependencies |

## Requirements

Python 3.10 or newer, with NetworkX and pandas:

```
pip install -r requirements.txt
```

## Usage

```
python beatles_chains.py
```

The script takes well under a second and writes its results to standard output. Pass `--data` to
run it on another edge list with the same columns, for instance the song titles of another artist:

```
python beatles_chains.py --data my_song_titles.csv
```

Part of the output:

```
Section 4. The longest chain of Beatles song titles
===================================================

Length of chain         1     2     3     4     5     6     7     8
Number of chains      276   233   151    60    17     4     1     0

Total number of chains: 742

The longest chain consists of 7 song titles and is unique.

  Hallelujah, I love her So how Come and get It's only Love you To know her is to love Her Majesty
    1. Hallelujah, I Love Her So
    2. So How Come (No One Loves Me)
    3. Come And Get It
    4. It's Only Love
    5. Love You To
    6. To Know Her Is To Love Her
    7. Her Majesty
```

## What is reproduced

| Output | Result | In the paper |
| --- | --- | --- |
| Network statistics | 345 nodes, 276 links, 89 connected components, the largest of size 132 | Table 1, Section 3 |
| Trail census | 742 chains in total, of which 276 of length 1 down to 1 of length 7 | Table 2, Section 4 |
| Longest chain | 7 song titles, and it is the only chain of that length | Table 3, Section 4 |
| Longest disjoint chain | 5 song titles, in 5 variants that differ only in their first song | Table 4, Section 5 |
| Longest chain of originals | 4 song titles, in 3 variants, out of 199 titles written by a Beatle | Section 6 |

Each search is an exhaustive depth-first search: starting from each node in turn, the current
trail is extended along every link it has not used yet and abandoned when no unused link is left.
This enumerates all trails of the network, so the longest ones it finds are the longest that
exist. The longest path problem is NP-hard in general, but this network is small and sparse enough
for the enumeration to finish in milliseconds.

## The data

The song titles are those of the 309 songs recorded by The Beatles as listed in the
[Beatles Bible](https://www.beatlesbible.com/songs/), together with the songwriting credits given
there, accessed 15 September 2026. The 33 titles that consist of a single word, such as
*Yesterday*, cannot form a link and are left out, which leaves 276 titles.

Three conventions are applied when a title is split into a first word, a last word and the words
in between:

- Contractions are split where the sound of the first word does not change, so *It's Only Love*
  runs from **It** to **Love** with the label *s Only*, while *Don't Bother Me* keeps **Don't** as
  its first word.
- Parenthetical additions are dropped, so *I Want You (She's So Heavy)* is a link from **I** to
  **You**. The `song_title` column keeps the addition; the node and label columns do not.
- A title of exactly two words gives a link with an empty label.

Columns of `data/beatles_song_titles.csv`:

| Column | Description |
| --- | --- |
| `song_title` | The song title as listed in the Beatles Bible |
| `source` | First word of the title: the node the link starts at |
| `edge_label` | Words between the first and the last word; empty for two-word titles |
| `target` | Last word of the title: the node the link ends at |
| `writers` | Songwriting credit as listed in the Beatles Bible |
| `beatles_original` | `yes` if Lennon, McCartney, Harrison or Starkey/Starr is among the credited writers |

`beatles_original` is what Section 6 filters on. Arrangements of traditional songs count as no, so
*Maggie Mae*, on which all four Beatles are credited as arrangers, is not treated as an original.

## Citation

If you use this data or code, please cite the paper:

```bibtex
@article{BudelKooijBeatles,
  author  = {Budel, Gabriel and Kooij, Robert E.},
  title   = {Any time at All you need is Love me Do you want to know a Secret:
             Chains in the Beatles Song Titles Network},
  year    = {2026}
}
```

## License

MIT, see [LICENSE](LICENSE). The song titles and songwriting credits are facts about the Beatles
catalogue and are reproduced here for research purposes; the Beatles Bible is credited above as
their source.
