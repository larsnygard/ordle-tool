import argparse
import os

WORDLIST_FILE = "fullformsliste.txt"


def get_five_letter_words():
    if not os.path.exists(WORDLIST_FILE):
        print(f"'{WORDLIST_FILE}' ikke funnet.")
        return []

    words = set()
    try:
        with open(WORDLIST_FILE, 'r', encoding='latin-1') as f:
            next(f)  # Skip header line
            for line in f:
                parts = line.strip().split()
                if len(parts) > 2:
                    word = parts[2].lower()
                    if len(word) == 5 and word.isalpha():
                        words.add(word)
    except IOError as e:
        print(f"Kunne ikke lese filen {WORDLIST_FILE}: {e}")
        return []

    return sorted(words)


def matches_pattern(word, pattern):
    for wc, pc in zip(word, pattern):
        if pc != '.' and wc != pc:
            return False
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Finn ord som passer til et Wordle-mønster."
    )
    parser.add_argument(
        "pattern",
        type=str,
        help="5-tegns mønster. Bruk '.' for ukjente posisjoner, f.eks. '.ige.'"
    )
    parser.add_argument(
        "-i",
        "--include",
        type=str,
        default="",
        metavar="bokstaver",
        help="Bokstaver som må finnes et sted i ordet (gule bokstaver i Wordle)."
    )
    parser.add_argument(
        "-x",
        "-e",
        "--exclude",
        type=str,
        default="",
        metavar="bokstaver",
        help="Bokstaver som ikke finnes i ordet (grå bokstaver i Wordle)."
    )

    args = parser.parse_args()

    pattern = args.pattern.lower()
    if len(pattern) != 5:
        print(f"Feil: Mønsteret må være 5 tegn langt, fikk {len(pattern)}.")
        return

    required = set(args.include.lower()) - {' '}
    excluded = set(args.exclude.lower()) - {' '}

    words = get_five_letter_words()

    results = [
        w for w in words
        if matches_pattern(w, pattern)
        and required.issubset(set(w))
        and not excluded & set(w)
    ]

    if results:
        print(f"Fant {len(results)} ord:")
        for w in results:
            print(f"  {w}")
    else:
        print("Ingen ord funnet.")


if __name__ == "__main__":
    main()
