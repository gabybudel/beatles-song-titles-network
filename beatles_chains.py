"""Chains in the Beatles song titles network.

Reproduces the results reported in

    G. Budel and R. E. Kooij, "Any time at All you need is Love me Do you want
    to know a Secret: Chains in the Beatles Song Titles Network".

Every Beatles song title of at least two words is a link of a directed
multigraph: it runs from a node holding its first word to a node holding its
last word. A chain of song titles, in which each title starts with the word the
previous one ended on, is then a trail of that network: a walk that may revisit
nodes but uses no link twice. The longest chain is the longest trail.

Running this script prints, in the order of the paper,

    the network statistics of Table 1                         (Section 3)
    the trail census of Table 2 and the longest chain         (Section 4)
    the longest chain sharing no song with it                 (Section 5)
    the longest chain among the songs the Beatles wrote       (Section 6)

Usage:

    pip install -r requirements.txt
    python beatles_chains.py
"""

import argparse
import re
from collections import Counter
from pathlib import Path

import networkx as nx
import pandas as pd

DATA = Path(__file__).resolve().parent / "data" / "beatles_song_titles.csv"
BEATLES = ("Lennon", "McCartney", "Harrison", "Starkey", "Starr")


# --------------------------------------------------------------- the network

def load_songs(path):
    """The song titles, one per row, with their nodes, link label and credit."""
    songs = pd.read_csv(path, dtype=str, keep_default_na=False)
    for column in ("song_title", "source", "edge_label", "target", "writers"):
        songs[column] = songs[column].str.strip()
    songs["beatles_original"] = songs["beatles_original"].str.strip() == "yes"
    return songs


def build_network(songs):
    """The song titles network: one link per song title, first word to last."""
    network = nx.MultiDiGraph()
    for song in songs.itertuples(index=False):
        network.add_edge(
            song.source,
            song.target,
            label=song.edge_label,
            title=song.song_title,
        )
    return network


# ------------------------------------------------------------------- trails

def enumerate_trails(network):
    """Count every trail of the network and collect the longest ones.

    An exhaustive depth-first search: starting from each node in turn, extend
    the current trail along every link that it has not used yet and backtrack
    when none is left. Every trail of the network is reached exactly once, so
    the longest trails found are the longest that exist.
    """
    links = {node: sorted(network.out_edges(node, keys=True)) for node in network}
    census = Counter()
    longest = []
    best = 0
    trail = []
    used = set()

    def extend(node):
        nonlocal longest, best
        for link in links[node]:
            if link in used:
                continue
            used.add(link)
            trail.append(link)
            census[len(trail)] += 1
            if len(trail) > best:
                best = len(trail)
                longest = [tuple(trail)]
            elif len(trail) == best:
                longest.append(tuple(trail))
            extend(link[1])
            trail.pop()
            used.remove(link)

    for node in sorted(network):
        extend(node)
    return census, longest


def titles_of(network, trail):
    """The song titles of a trail, in order."""
    return [network.edges[link]["title"] for link in trail]


# ---------------------------------------------------------------- reporting

def drop_subtitle(title):
    """'So How Come (No One Loves Me)' -> 'So How Come', as in the network."""
    return re.sub(r"\s+", " ", re.sub(r"\s*\([^)]*\)\s*", " ", title)).strip()


def as_sentence(network, trail):
    """A trail written out as one running sentence, as the paper prints it.

    The words that are nodes of the network keep the capital they carry in the
    song title; the words inside a title are lowercased, so that the chain
    reads as a sentence and the nodes it visits stand out. This is a matter of
    presentation only and does not touch the network.
    """
    def inner(word):
        acronym = len(word) > 1 and word.isupper()
        if word == "I" or word.startswith("I'") or acronym:
            return word
        return word.lower()

    words = []
    for link in trail:
        title = drop_subtitle(network.edges[link]["title"]).split()
        if words:
            # The pivot word is already written; a split contraction such as
            # It -> It's only rejoins the word that is standing there.
            if title[0].startswith(link[0]):
                words[-1] += title[0][len(link[0]):]
        else:
            words.append(title[0])
        words.extend(inner(word) for word in title[1:-1])
        words.append(title[-1])
    return " ".join(words)


def print_statistics(network, songs):
    """The network statistics of Table 1, with the details of Section 3."""
    components = sorted(
        (len(component) for component in nx.weakly_connected_components(network)),
        reverse=True,
    )
    pairs = Counter((u, v) for u, v in network.edges())
    multi = sorted(pair for pair, count in pairs.items() if count > 1)
    loops = sorted(u for u, v in network.edges() if u == v)
    out_degree = max(network.out_degree, key=lambda item: item[1])
    in_degree = max(network.in_degree, key=lambda item: item[1])

    print(f"Number of song titles                     {len(songs):>5}")
    print(f"Number of nodes                           {network.number_of_nodes():>5}")
    print(f"Number of links                           {network.number_of_edges():>5}")
    print(f"Number of connected components            {len(components):>5}")
    print(f"Size of largest connected component       {components[0]:>5}")
    print(f"Size of second-largest connected component{components[1]:>5}")
    print(f"Number of multi-link node pairs           {len(multi):>5}")
    print(f"Number of self-loops                      {len(loops):>5}")
    print()
    sizes = Counter(components)
    distribution = ", ".join(
        f"{count} of size {size}" for size, count in sorted(sizes.items(), reverse=True)
    )
    print(f"Component sizes: {distribution}")
    print("Multi-link node pairs: " + ", ".join(f"{u}-{v}" for u, v in multi))
    print("Self-loops: " + ", ".join(loops))
    print(f"Highest out-degree: {out_degree[1]}, at the node {out_degree[0]}")
    print(f"Highest in-degree: {in_degree[1]}, at the node {in_degree[0]}")


def print_census(census):
    """The number of trails of each length, as in Table 2."""
    lengths = range(1, max(census) + 2)
    print("Length of chain    " + "".join(f"{length:>6}" for length in lengths))
    print("Number of chains   " + "".join(f"{census[length]:>6}" for length in lengths))
    print(f"\nTotal number of chains: {sum(census.values())}")


def print_chains(network, longest):
    """The longest chains found, written out and listed song by song."""
    length = len(longest[0])
    if len(longest) == 1:
        print(f"The longest chain consists of {length} song titles and is unique.\n")
    else:
        print(f"The longest chain consists of {length} song titles; "
              f"there are {len(longest)} of that length.\n")
    for number, trail in enumerate(longest, start=1):
        if len(longest) > 1:
            print(f"Chain {number}")
        print(f"  {as_sentence(network, trail)}")
        for position, title in enumerate(titles_of(network, trail), start=1):
            print(f"    {position}. {title}")
        print()


def section(title):
    print(f"\n{title}\n{'=' * len(title)}\n")


# --------------------------------------------------------------------- main

def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--data", type=Path, default=DATA,
                        help="edge list to read (default: data/beatles_song_titles.csv)")
    arguments = parser.parse_args()

    songs = load_songs(arguments.data)
    network = build_network(songs)

    section("Section 3. Properties of the Beatles song titles network")
    print_statistics(network, songs)

    section("Section 4. The longest chain of Beatles song titles")
    census, longest = enumerate_trails(network)
    print_census(census)
    print()
    print_chains(network, longest)

    section("Section 5. The longest disjoint chain of Beatles song titles")
    without_winner = network.copy()
    without_winner.remove_edges_from(longest[0])
    print(f"Leaving out the {len(longest[0])} song titles of the longest chain "
          f"leaves {without_winner.number_of_edges()} song titles.\n")
    _, disjoint = enumerate_trails(without_winner)
    print_chains(without_winner, disjoint)

    section("Section 6. The longest chain of Beatles originals")
    originals = songs[songs["beatles_original"]]
    written_by = ", ".join(BEATLES[:-1]) + f" or {BEATLES[-1]}"
    print(f"Of the {len(songs)} song titles, {len(originals)} are credited to "
          f"{written_by}.\n")
    originals_network = build_network(originals)
    print_statistics(originals_network, originals)
    print()
    originals_census, originals_longest = enumerate_trails(originals_network)
    print_census(originals_census)
    print()
    print_chains(originals_network, originals_longest)


if __name__ == "__main__":
    main()
