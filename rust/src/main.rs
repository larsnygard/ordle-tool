use clap::{Parser, Subcommand};
use std::collections::HashSet;

// Embed the wordlist at compile time.
// Path is relative to this source file (rust/src/main.rs -> ../../fullformsliste.txt).
const WORDLIST: &[u8] = include_bytes!("../../fullformsliste.txt");

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/// ISO-8859-1 bytes map 1:1 to Unicode code points, so each byte becomes a char.
fn latin1_line(bytes: &[u8]) -> String {
    bytes.iter().map(|&b| b as char).collect()
}

fn is_alpha(s: &str) -> bool {
    s.chars().all(|c| c.is_alphabetic())
}

fn has_unique_chars(s: &str) -> bool {
    let mut seen = HashSet::new();
    s.chars().all(|c| seen.insert(c))
}

/// Parse the embedded wordlist and return 5-letter alphabetic words.
/// When `unique_only` is true only words with no repeated letters are kept.
fn load_words(unique_only: bool) -> Vec<String> {
    let mut seen: HashSet<String> = HashSet::new();
    let mut words: Vec<String> = Vec::new();

    let mut start = 0usize;
    let mut first_line = true;

    for i in 0..=WORDLIST.len() {
        if i == WORDLIST.len() || WORDLIST[i] == b'\n' {
            let end = if i > 0 && WORDLIST[i.saturating_sub(1)] == b'\r' {
                i - 1
            } else {
                i
            };
            let line_bytes = &WORDLIST[start..end];

            if first_line {
                first_line = false;
            } else {
                let line = latin1_line(line_bytes);
                let parts: Vec<&str> = line.split_whitespace().collect();
                if parts.len() > 2 {
                    let word = parts[2].to_lowercase();
                    if word.chars().count() == 5 && is_alpha(&word) {
                        if !unique_only || has_unique_chars(&word) {
                            if seen.insert(word.clone()) {
                                words.push(word);
                            }
                        }
                    }
                }
            }
            start = i + 1;
        }
    }

    words.sort();
    words
}

// ---------------------------------------------------------------------------
// check subcommand
// ---------------------------------------------------------------------------

fn cmd_check(pattern: &str, include: &str, exclude: &str) {
    let pattern = pattern.to_lowercase();
    if pattern.chars().count() != 5 {
        eprintln!(
            "Feil: Mønsteret må være 5 tegn langt, fikk {}.",
            pattern.chars().count()
        );
        std::process::exit(1);
    }

    let required: HashSet<char> = include
        .to_lowercase()
        .chars()
        .filter(|c| !c.is_whitespace())
        .collect();
    let excluded: HashSet<char> = exclude
        .to_lowercase()
        .chars()
        .filter(|c| !c.is_whitespace())
        .collect();

    let words = load_words(false);

    let results: Vec<&String> = words
        .iter()
        .filter(|w| {
            // Pattern match: '.' is wildcard
            w.chars().zip(pattern.chars()).all(|(wc, pc)| pc == '.' || wc == pc)
                && required.iter().all(|c| w.contains(*c))
                && !excluded.iter().any(|c| w.contains(*c))
        })
        .collect();

    if results.is_empty() {
        println!("Ingen ord funnet.");
    } else {
        println!("Fant {} ord:", results.len());
        for w in results {
            println!("  {}", w);
        }
    }
}

// ---------------------------------------------------------------------------
// find subcommand
// ---------------------------------------------------------------------------

#[allow(clippy::too_many_arguments)]
fn search<'a>(
    remaining: &[&'a str],
    need: usize,
    start: usize,
    current: &mut Vec<&'a str>,
    used_chars: &mut HashSet<char>,
    required_letters: &HashSet<char>,
    include_words: &[String],
    total: &mut u64,
) {
    if current.len() == need {
        if !required_letters.is_empty()
            && !required_letters.iter().all(|c| used_chars.contains(c))
        {
            return;
        }
        let mut combo: Vec<&str> = include_words.iter().map(|s| s.as_str()).collect();
        combo.extend_from_slice(current);
        println!("Fant kombinasjon: {}", combo.join(", "));
        *total += 1;
        return;
    }

    for i in start..remaining.len() {
        let word = remaining[i];
        if word.chars().any(|c| used_chars.contains(&c)) {
            continue;
        }
        for c in word.chars() {
            used_chars.insert(c);
        }
        current.push(word);
        search(
            remaining,
            need,
            i + 1,
            current,
            used_chars,
            required_letters,
            include_words,
            total,
        );
        current.pop();
        for c in word.chars() {
            used_chars.remove(&c);
        }
    }
}

fn cmd_find(n: usize, include_words: &[String], letters: Option<&str>) {
    let required_letters: HashSet<char> = letters
        .map(|s| s.to_lowercase().chars().collect())
        .unwrap_or_default();

    eprintln!("Leser og filtrerer ordliste...");
    let words = load_words(true);
    eprintln!(
        "Fant {} unike 5-bokstavsord med unike bokstaver.",
        words.len()
    );

    // Validate included words
    let mut valid_include: Vec<String> = Vec::new();
    for w in include_words {
        let w = w.to_lowercase();
        if w.chars().count() != 5 || !is_alpha(&w) || !has_unique_chars(&w) {
            eprintln!(
                "Advarsel: Inkludert ord '{}' er ugyldig og vil bli ignorert.",
                w
            );
            continue;
        }
        valid_include.push(w);
    }

    let included_chars: HashSet<char> = valid_include.iter().flat_map(|w| w.chars()).collect();
    let total_included: usize = valid_include.iter().map(|w| w.chars().count()).sum();
    if included_chars.len() != total_included {
        eprintln!("Feil: Inkluderte ord har overlappende bokstaver.");
        std::process::exit(1);
    }

    if valid_include.len() >= n {
        let combined: String = valid_include[..n].concat();
        let combined_set: HashSet<char> = combined.chars().collect();
        if has_unique_chars(&combined)
            && required_letters.iter().all(|c| combined_set.contains(c))
        {
            println!("Fant kombinasjon: {}", valid_include[..n].join(", "));
            println!("\nFant totalt 1 kombinasjoner.");
        } else {
            println!("\nFant totalt 0 kombinasjoner.");
        }
        return;
    }

    let include_set: HashSet<&str> = valid_include.iter().map(|s| s.as_str()).collect();
    let remaining: Vec<&str> = words
        .iter()
        .filter(|w| {
            !include_set.contains(w.as_str())
                && !w.chars().any(|c| included_chars.contains(&c))
        })
        .map(|s| s.as_str())
        .collect();

    let need = n - valid_include.len();
    eprint!("Finner kombinasjoner av {} ord", n);
    if !valid_include.is_empty() {
        eprint!(", inkluderer: {}", valid_include.join(", "));
    }
    eprintln!("...");

    let mut total = 0u64;
    let mut current: Vec<&str> = Vec::with_capacity(need);
    let mut used_chars: HashSet<char> = included_chars.clone();

    search(
        &remaining,
        need,
        0,
        &mut current,
        &mut used_chars,
        &required_letters,
        &valid_include,
        &mut total,
    );

    println!("\nFant totalt {} kombinasjoner.", total);
}

// ---------------------------------------------------------------------------
// CLI definition
// ---------------------------------------------------------------------------

#[derive(Parser)]
#[command(name = "ordle", about = "Norsk Wordle-hjelper")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Finn ordkombinasjoner med unike bokstaver (for Wordle-start)
    Find {
        /// Antall ord i kombinasjonen
        #[arg(short = 'o', long = "combinations", default_value_t = 3)]
        combinations: usize,

        /// Ord som må være med (gjenta for flere: -i ord1 -i ord2)
        #[arg(short = 'i', long = "include")]
        include: Vec<String>,

        /// Bokstaver som alle må dekkes av kombinasjonen (f.eks. aeiourstln)
        #[arg(long)]
        letters: Option<String>,
    },

    /// Finn ord som passer til et Wordle-mønster
    Check {
        /// 5-tegns mønster, bruk '.' for ukjente posisjoner (f.eks. .ige.)
        pattern: String,

        /// Bokstaver som må finnes i ordet, uansett posisjon (gule)
        #[arg(short = 'i', long = "include", default_value = "")]
        include: String,

        /// Bokstaver som ikke finnes i ordet (grå)
        #[arg(short = 'x', long = "exclude", default_value = "")]
        exclude: String,
    },
}

fn main() {
    let cli = Cli::parse();

    match cli.command {
        Commands::Find {
            combinations,
            include,
            letters,
        } => cmd_find(combinations, &include, letters.as_deref()),

        Commands::Check {
            pattern,
            include,
            exclude,
        } => cmd_check(&pattern, &include, &exclude),
    }
}
