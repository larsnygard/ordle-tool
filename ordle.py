import argparse
import requests
import zipfile
import os
import itertools
from collections import Counter

# URL to the Norwegian word list from Språkbanken (National Library of Norway)
# WORDLIST_URL = "https://github.com/open-dict-data/fullform_bm/releases/download/1.0/fullform_bm.zip"
# ZIP_FILE = "fullform_bm.zip"
WORDLIST_FILE = "fullformsliste.txt"

def has_unique_chars(word):
    """Checks if a word consists of unique characters."""
    return len(set(word)) == len(word)

def download_wordlist():
    """Downloads and extracts the Norwegian word list."""
    print("Nedlasting er deaktivert. Bruker lokal fil.")
    return False


def get_five_letter_unique_words():
    """
    Reads the wordlist and returns a list of 5-letter words 
    with unique characters.
    """
    if not os.path.exists(WORDLIST_FILE):
        print(f"'{WORDLIST_FILE}' ikke funnet.")
        if not download_wordlist():
            return []

    words = []
    print(f"Leser ord fra {WORDLIST_FILE} og filtrerer...")
    try:
        with open(WORDLIST_FILE, 'r', encoding='latin-1') as f:
            next(f) # Skip header line
            for line in f:
                parts = line.strip().split()
                if len(parts) > 2:
                    word = parts[2].lower()
                    # Keep words with 5 letters, all alphabetic, and unique characters
                    if len(word) == 5 and word.isalpha() and has_unique_chars(word):
                        words.append(word)
    except IOError as e:
        print(f"Kunne ikke lese filen {WORDLIST_FILE}: {e}")
        return []
    
    # Remove duplicates
    unique_words = sorted(list(set(words)))
    print(f"Fant {len(unique_words)} unike 5-bokstavsord med unike bokstaver.")
    return unique_words

def find_word_combinations(words, n, include=None, required_letters=None):
    """
    Finds combinations of n words where all characters across the words are unique.
    An optional list of words to include can be provided.
    An optional set of letters that must all appear in the combination can be provided.
    """
    if include is None:
        include = []
    if required_letters is None:
        required_letters = set()
    else:
        required_letters = set(required_letters)

    if not words:
        print("Ordlisten er tom, kan ikke finne kombinasjoner.")
        return

    # Validate included words
    for word in include:
        if len(word) != 5 or not word.isalpha() or not has_unique_chars(word):
            print(f"Advarsel: Inkludert ord '{word}' er ugyldig og vil bli ignorert.")
            include.remove(word)
    
    if len(include) >= n:
        print("Antall inkluderte ord er lik eller større enn antall ord i kombinasjonen.")
        # Check if the included words themselves form a valid combination
        combined = "".join(include[:n])
        if has_unique_chars(combined) and required_letters.issubset(set(combined)):
             print(f"Fant kombinasjon: {', '.join(include[:n])}")
             print("\nFant totalt 1 kombinasjoner.")
        else:
             print("\nFant totalt 0 kombinasjoner.")
        return

    print(f"Finner kombinasjoner av {n} ord, inkludert: {', '.join(include)}...")
    
    # Pre-calculate the character set of included words
    included_chars = set("".join(include))
    if len(included_chars) != len("".join(include)):
        print("Feil: Inkluderte ord har overlappende bokstaver. Kan ikke danne en gyldig kombinasjon.")
        return

    # Filter the main word list to exclude words that have common characters with the included words
    remaining_words = [
        word for word in words 
        if not set(word) & included_chars and word not in include
    ]

    total_combinations = 0
    # We need to find n - len(include) more words
    for combo_rest in itertools.combinations(remaining_words, n - len(include)):
        combined_str = "".join(combo_rest)
        if has_unique_chars(combined_str):
            final_combo = include + list(combo_rest)
            all_chars = set(included_chars | set(combined_str))
            if required_letters and not required_letters.issubset(all_chars):
                continue
            print(f"Fant kombinasjon: {', '.join(final_combo)}")
            total_combinations += 1
            
    print(f"\nFant totalt {total_combinations} kombinasjoner.")


def main():
    parser = argparse.ArgumentParser(
        description="Finn ordkombinasjoner med unike bokstaver fra en norsk ordliste."
    )
    parser.add_argument(
        "-N",
        "--new",
        action="store_true",
        help="Tvinger nedlasting av en ny ordliste."
    )
    parser.add_argument(
        "-o",
        "--combinations",
        type=int,
        default=3,
        metavar="n",
        help="Antall ord i hver kombinasjon (standard: 3)."
    )
    parser.add_argument(
        "-i",
        "--include",
        type=str,
        nargs='+',
        default=[],
        metavar="ord",
        help="En liste med ord som må være med i kombinasjonen."
    )
    parser.add_argument(
        "--letters",
        type=str,
        default="",
        metavar="bokstaver",
        help="Bokstaver som alle må finnes i kombinasjonen (f.eks. aeiourstln)."
    )

    args = parser.parse_args()

    if args.new:
        if not download_wordlist():
            return # Stop if download fails

    # Get the filtered list of words
    five_letter_words = get_five_letter_unique_words()
    
    # Find and print combinations
    if five_letter_words:
        find_word_combinations(five_letter_words, args.combinations, args.include, args.letters)

if __name__ == "__main__":
    main()
