#!/usr/bin/env python3
"""Build the Ordle PWA into docs/ with embedded word lists."""
import json
import os

WORDLIST_NO = "fullformsliste.txt"
WORDLIST_EN_ALL = "english_words_all.txt"
WORDLIST_EN_UNIQ = "english_words_unique.txt"
OUT_DIR = "docs"

# ── Extract Norwegian word lists ────────────────────────────────────────────
print(f"Reading {WORDLIST_NO}...")
all5_no: set[str] = set()
uniq5_no: set[str] = set()

with open(WORDLIST_NO, encoding="latin-1") as f:
    next(f)  # skip header
    for line in f:
        parts = line.strip().split()
        if len(parts) > 2:
            w = parts[2].lower()
            if len(w) == 5 and w.isalpha():
                all5_no.add(w)
                if len(set(w)) == 5:
                    uniq5_no.add(w)

words_all_no_js  = json.dumps(sorted(all5_no),  ensure_ascii=False)
words_uniq_no_js = json.dumps(sorted(uniq5_no), ensure_ascii=False)
print(f"  Norwegian all 5-letter words : {len(all5_no):,}")
print(f"  Norwegian unique-char words  : {len(uniq5_no):,}")

# ── Extract English word lists ──────────────────────────────────────────────
print(f"Reading {WORDLIST_EN_ALL}...")
all5_en = set()
with open(WORDLIST_EN_ALL, encoding="utf-8") as f:
    for line in f:
        w = line.strip()
        if w and len(w) == 5:
            all5_en.add(w)

print(f"Reading {WORDLIST_EN_UNIQ}...")
uniq5_en = set()
with open(WORDLIST_EN_UNIQ, encoding="utf-8") as f:
    for line in f:
        w = line.strip()
        if w and len(w) == 5:
            uniq5_en.add(w)

words_all_en_js  = json.dumps(sorted(all5_en),  ensure_ascii=False)
words_uniq_en_js = json.dumps(sorted(uniq5_en), ensure_ascii=False)
print(f"  English all 5-letter words : {len(all5_en):,}")
print(f"  English unique-char words  : {len(uniq5_en):,}")

os.makedirs(OUT_DIR, exist_ok=True)

# ── manifest.json ───────────────────────────────────────────────────────────
manifest = {
    "name": "Ordle",
    "short_name": "Ordle",
    "description": "Norsk Wordle-hjelper",
    "start_url": "./",
    "display": "standalone",
    "background_color": "#121213",
    "theme_color": "#538d4e",
    "icons": [
        {"src": "icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any maskable"},
    ],
}
with open(f"{OUT_DIR}/manifest.json", "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

# ── icon.svg ────────────────────────────────────────────────────────────────
icon_svg = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect width="100" height="100" rx="18" fill="#538d4e"/>
  <text x="50" y="72" font-family="system-ui,sans-serif" font-size="62"
        font-weight="bold" fill="white" text-anchor="middle">O</text>
</svg>"""
with open(f"{OUT_DIR}/icon.svg", "w", encoding="utf-8") as f:
    f.write(icon_svg)

# ── sw.js ───────────────────────────────────────────────────────────────────
sw_js = """\
const CACHE = 'ordle-v1';
const ASSETS = ['./','./index.html','./manifest.json','./icon.svg'];

self.addEventListener('install', e =>
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS))));

self.addEventListener('activate', e =>
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))));

self.addEventListener('fetch', e =>
  e.respondWith(caches.match(e.request).then(r => r || fetch(e.request))));
"""
with open(f"{OUT_DIR}/sw.js", "w", encoding="utf-8") as f:
    f.write(sw_js)

# ── index.html ──────────────────────────────────────────────────────────────
html = f"""\
<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ordle</title>
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#538d4e">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="apple-touch-icon" href="icon.svg">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:system-ui,sans-serif;background:#121213;color:#fff;
     max-width:520px;margin:0 auto;padding:1rem 1rem 3rem}}
.header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:1.2rem}}
h1{{flex:1;text-align:center;font-size:1.8rem;color:#538d4e;letter-spacing:.1em;margin:0}}
.lang-selector{{display:flex;gap:8px}}
.lang-selector span{{cursor:pointer;font-size:1.5rem;opacity:.6;transition:opacity .2s}}
.lang-selector span.active{{opacity:1}}
/* tabs */
.tabs{{display:flex;gap:4px;margin-bottom:1.5rem}}
.tab{{flex:1;padding:.65rem;text-align:center;border:none;border-radius:6px;
      cursor:pointer;background:#3a3a3c;color:#fff;font-size:1rem;
      transition:background .15s}}
.tab.active{{background:#538d4e}}
/* sections */
.sec{{display:none}}.sec.on{{display:block}}
/* form */
label{{display:block;margin-bottom:.3rem;font-size:.82rem;
       color:#818384;text-transform:uppercase;letter-spacing:.05em}}
input[type=text],select{{
  width:100%;padding:.65rem .85rem;background:#1a1a1b;
  border:2px solid #3a3a3c;border-radius:6px;color:#fff;
  font-size:1rem;margin-bottom:1rem}}
input:focus,select:focus{{outline:none;border-color:#538d4e}}
/* submit */
.btn{{width:100%;padding:.8rem;background:#538d4e;color:#fff;border:none;
      border-radius:6px;font-size:1.05rem;cursor:pointer;
      transition:background .15s}}
.btn:hover{{background:#6aaf63}}
.btn:active{{background:#3e7040}}
/* results */
.res{{margin-top:1.4rem}}
.cnt{{color:#818384;font-size:.85rem;margin-bottom:.7rem}}
.wlist{{display:flex;flex-wrap:wrap;gap:6px}}
.word{{background:#3a3a3c;border-radius:5px;padding:.3rem .6rem;
       font-family:monospace;font-size:.95rem;letter-spacing:.04em}}
.clist{{list-style:none}}
.clist li{{background:#3a3a3c;border-radius:5px;padding:.45rem .8rem;
           margin-bottom:4px;font-family:monospace;font-size:.95rem}}
.spin{{text-align:center;padding:2rem;color:#818384}}
.err{{color:#e05252;margin-top:.6rem;font-size:.9rem;
      background:#2a1a1a;padding:.6rem .8rem;border-radius:6px}}
.note{{color:#818384;font-size:.8rem;margin-top:.5rem}}
footer{{margin-top:2.5rem;padding-top:1rem;border-top:1px solid #3a3a3c;
        font-size:.75rem;color:#818384;line-height:1.6}}
footer a{{color:#818384}}
</style>
</head>
<body>
<div class="header">
  <h1 id="app-title">Ordle</h1>
  <div class="lang-selector">
    <span onclick="setLanguage('no')" class="active">🇳🇴</span>
    <span onclick="setLanguage('en')">🇬🇧</span>
  </div>
</div>

<div class="tabs">
  <button class="tab active" id="tab-check" onclick="showTab('check')">Sjekk ord</button>
  <button class="tab" id="tab-find" onclick="showTab('find')">Finn kombinasjoner</button>
</div>

<!-- ── CHECK ── -->
<div id="s-check" class="sec on">
  <label id="label-pattern">Mønster — bruk . for ukjent bokstav</label>
  <input type="text" id="cpat" maxlength="5" placeholder="f.eks. ..a.e" autocomplete="off" autocorrect="off" spellcheck="false">
  <label id="label-must">Bokstaver som MÅ finnes — gule bokstaver</label>
  <input type="text" id="ci" placeholder="f.eks. ae" autocomplete="off" autocorrect="off" spellcheck="false">
  <label id="label-not">Bokstaver som IKKE finnes — grå bokstaver</label>
  <input type="text" id="ce" placeholder="f.eks. rst" autocomplete="off" autocorrect="off" spellcheck="false">
  <button class="btn" id="btn-search" onclick="runCheck()">Søk</button>
  <div class="res" id="cr"></div>
</div>

<!-- ── FIND ── -->
<div id="s-find" class="sec">
  <label id="label-numwords">Antall ord i kombinasjonen</label>
  <select id="fn">
    <option value="2" id="opt-2">2 ord</option>
    <option value="3" id="opt-3" selected>3 ord</option>
    <option value="4" id="opt-4">4 ord</option>
    <option value="5" id="opt-5">5 ord</option>
  </select>
  <label id="label-include">Inkluder disse ordene (kommaseparert)</label>
  <input type="text" id="fi" placeholder="f.eks. sterk,byliv" autocomplete="off" autocorrect="off" spellcheck="false">
  <label id="label-exclude">Ekskluder disse ordene (kommaseparert)</label>
  <input type="text" id="fe" placeholder="f.eks. alder,smitt" autocomplete="off" autocorrect="off" spellcheck="false">
  <label id="label-mustcombo">Bokstaver som MÅ finnes i kombinasjonen</label>
  <input type="text" id="fr" placeholder="f.eks. aeiou" autocomplete="off" autocorrect="off" spellcheck="false">
  <button class="btn" id="btn-find" onclick="runFind()">Finn (maks 100)</button>
  <div class="res" id="fres"></div>
</div>

<footer id="footer-main">
  Spill Wordle på norsk: <a href="https://ordle.no" target="_blank" rel="noopener">ordle.no</a><br>
  Ordliste: <a href="https://www.nb.no/sprakbanken/ressurskatalog/oai-nb-no-sbr-5/" target="_blank" rel="noopener">Norsk ordbank &ndash; bokmål 2005</a>
  &copy; Universitetet i Bergen &amp; Språkrådet,
  distribuert av <a href="https://www.nb.no/sprakbanken" target="_blank" rel="noopener">Språkbanken</a>,
  lisens <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">CC BY 4.0</a><br>
  Ordle-verktøy: <a href="https://github.com/larsnygard/ordle-tool" target="_blank" rel="noopener">github.com/larsnygard/ordle-tool</a>,
  lisens <a href="https://www.gnu.org/licenses/gpl-3.0.html" target="_blank" rel="noopener">GPL&nbsp;3</a>
</footer>

<script>
const WORDS_ALL_NO  = {words_all_no_js};
const WORDS_UNIQ_NO = {words_uniq_no_js};
const WORDS_ALL_EN  = {words_all_en_js};
const WORDS_UNIQ_EN = {words_uniq_en_js};

let WORDS_ALL  = WORDS_ALL_NO;
let WORDS_UNIQ = WORDS_UNIQ_NO;

// ── tab switching ──
function showTab(t) {{
  ['check','find'].forEach((id,i) => {{
    document.querySelectorAll('.tab')[i].classList.toggle('active', id===t);
    document.getElementById('s-'+id).classList.toggle('on', id===t);
  }});
}}

// ── CHECK ──
function getPattern(){{
  const raw=document.getElementById('cpat').value.toLowerCase().padEnd(5,'.');
  return raw.split('').map(c=>(/[a-z\u00e6\u00f8\u00e5]/.test(c)?c:'.')).join('');
}}

function runCheck(){{
  const pat=getPattern();
  const inc=new Set([...document.getElementById('ci').value.toLowerCase().replace(/[^a-z\u00e6\u00f8\u00e5]/g,'')]);
  const exc=new Set([...document.getElementById('ce').value.toLowerCase().replace(/[^a-z\u00e6\u00f8\u00e5]/g,'')]);
  const el=document.getElementById('cr');

  const shown=[]; let total=0;
  for(const w of WORDS_ALL){{
    let ok=true;
    for(let i=0;i<5;i++) if(pat[i]!=='.'&&w[i]!==pat[i]){{ok=false;break;}}
    if(!ok) continue;
    for(const c of inc) if(!w.includes(c)){{ok=false;break;}}
    if(!ok) continue;
    for(const c of exc) if(w.includes(c)){{ok=false;break;}}
    if(!ok) continue;
    total++;
    if(shown.length<100) shown.push(w);
  }}

  if(total===0){{
    el.innerHTML='<div class="cnt">Ingen ord funnet.</div>';return;
  }}
  const truncMsg=total>100?`Viser 100 av ${{total}} ord`:`Fant ${{total}} ord`;
  el.innerHTML=`<div class="cnt">${{truncMsg}}</div>`+
    '<div class="wlist">'+shown.map(w=>`<span class="word">${{w}}</span>`).join('')+'</div>';
}}

// Enter key in check inputs
['cpat','ci','ce'].forEach(id=>{{
  document.getElementById(id).addEventListener('keydown',e=>{{if(e.key==='Enter')runCheck();}});
}});

// ── FIND ──
function runFind(){{
  const n=parseInt(document.getElementById('fn').value);
  const rawInc=document.getElementById('fi').value;
  const rawExc=document.getElementById('fe').value;
  const reqStr=document.getElementById('fr').value.toLowerCase().replace(/[^a-z\u00e6\u00f8\u00e5]/g,'');
  const required=new Set(reqStr);
  const el=document.getElementById('fres');

  const incWords=rawInc.split(',').map(s=>s.trim().toLowerCase()).filter(s=>s.length>0);
  const excWords=rawExc.split(',').map(s=>s.trim().toLowerCase()).filter(s=>s.length>0);
  // validate include words
  for(const w of incWords){{
    if([...w].length!==5||!/^[a-z\u00e6\u00f8\u00e5]+$/u.test(w)){{
      el.innerHTML=`<div class="err">Feil: '${{w}}' er ikke et gyldig 5-bokstavsord.</div>`;return;
    }}
    if(new Set(w).size!==[...w].length){{
      el.innerHTML=`<div class="err">Feil: '${{w}}' har gjentatte bokstaver.</div>`;return;
    }}
  }}
  // validate exclude words
  for(const w of excWords){{
    if([...w].length!==5||!/^[a-z\u00e6\u00f8\u00e5]+$/u.test(w)){{
      el.innerHTML=`<div class="err">Feil: '${{w}}' er ikke et gyldig 5-bokstavsord.</div>`;return;
    }}
    if(new Set(w).size!==[...w].length){{
      el.innerHTML=`<div class="err">Feil: '${{w}}' har gjentatte bokstaver.</div>`;return;
    }}
  }}
  const excSet=new Set(excWords);
  for(const w of incWords){{
    if(excSet.has(w)){{
      el.innerHTML=`<div class="err">Feil: '${{w}}' kan ikke være både inkludert og ekskludert.</div>`;return;
    }}
  }}
  const incChars=new Set(incWords.flatMap(w=>[...w]));
  if(incChars.size!==incWords.reduce((s,w)=>s+[...w].length,0)){{
    el.innerHTML='<div class="err">Feil: Inkluderte ord har overlappende bokstaver.</div>';return;
  }}
  if(incWords.length>=n){{
    el.innerHTML='<div class="err">Feil: Antall inkluderte ord m&aring; v&aelig;re mindre enn kombinasjonst&oslash;rrelsen.</div>';return;
  }}

  el.innerHTML='<div class="spin">S&oslash;ker\u2026</div>';
  setTimeout(()=>{{
    const remaining=WORDS_UNIQ.filter(w=>!excSet.has(w)&&[...w].every(c=>!incChars.has(c)));
    const need=n-incWords.length;
    const combos=[];

    function search(start,current,used){{
      if(combos.length>=100)return;
      if(current.length===need){{
        if(required.size>0){{
          const all=new Set([...incChars,...used]);
          for(const c of required) if(!all.has(c))return;
        }}
        combos.push([...incWords,...current]);
        return;
      }}
      for(let i=start;i<remaining.length;i++){{
        if(combos.length>=100)return;
        const w=remaining[i];
        if([...w].some(c=>used.has(c)))continue;
        for(const c of w)used.add(c);
        current.push(w);
        search(i+1,current,used);
        current.pop();
        for(const c of w)used.delete(c);
      }}
    }}

    search(0,[],new Set());

    if(combos.length===0){{
      el.innerHTML='<div class="cnt">Ingen kombinasjoner funnet.</div>';
    }}else{{
      const trunc=combos.length>=100;
      el.innerHTML=
        `<div class="cnt">Viser ${{combos.length}} kombinasjoner${{trunc?' (maks 100 &ndash; bruk inkluder-feltet for &aring; begrense s&oslash;ket)':''}}</div>`+
        '<ul class="clist">'+combos.map(c=>`<li>${{c.join(' \u00b7 ')}}</li>`).join('')+'</ul>';
    }}
  }},10);
}}

['fi','fe','fr'].forEach(id=>{{
  document.getElementById(id).addEventListener('keydown',e=>{{if(e.key==='Enter')runFind();}});
}});

// ── LANGUAGE SWITCHING ──
const translations = {{
  no: {{
    pageTitle: 'Ordle - Norsk Wordle-hjelper',
    appTitle: 'Ordle',
    tabCheck: 'Sjekk ord',
    tabFind: 'Finn kombinasjoner',
    labelPattern: 'Mønster — bruk . for ukjent bokstav',
    cpatPlaceholder: 'f.eks. ..a.e',
    labelMust: 'Bokstaver som MÅ finnes — gule bokstaver',
    ciPlaceholder: 'f.eks. ae',
    labelNot: 'Bokstaver som IKKE finnes — grå bokstaver',
    cePlaceholder: 'f.eks. rst',
    btnSearch: 'Søk',
    labelNumwords: 'Antall ord i kombinasjonen',
    opt2: '2 ord',
    opt3: '3 ord',
    opt4: '4 ord',
    opt5: '5 ord',
    labelInclude: 'Inkluder disse ordene (kommaseparert)',
    fiPlaceholder: 'f.eks. sterk,byliv',
    labelExclude: 'Ekskluder disse ordene (kommaseparert)',
    fePlaceholder: 'f.eks. alder,smitt',
    labelMustcombo: 'Bokstaver som MÅ finnes i kombinasjonen',
    frPlaceholder: 'f.eks. aeiou',
    btnFind: 'Finn (maks 100)',
    footer: 'Spill Wordle på norsk: <a href="https://ordle.no" target="_blank" rel="noopener">ordle.no</a><br>Ordliste: <a href="https://www.nb.no/sprakbanken/ressurskatalog/oai-nb-no-sbr-5/" target="_blank" rel="noopener">Norsk ordbank – bokmål 2005</a>&copy; Universitetet i Bergen &amp; Språkrådet,distribuert av <a href="https://www.nb.no/sprakbanken" target="_blank" rel="noopener">Språkbanken</a>,lisens <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">CC BY 4.0</a><br>Ordle-verktøy: <a href="https://github.com/larsnygard/ordle-tool" target="_blank" rel="noopener">github.com/larsnygard/ordle-tool</a>,lisens <a href="https://www.gnu.org/licenses/gpl-3.0.html" target="_blank" rel="noopener">GPL&nbsp;3</a>'
  }},
  en: {{
    pageTitle: 'Worlde - English Wordle Helper',
    appTitle: 'Worlde',
    tabCheck: 'Check word',
    tabFind: 'Find combinations',
    labelPattern: 'Pattern — use . for unknown letter',
    cpatPlaceholder: 'e.g. ..a.e',
    labelMust: 'Letters that MUST appear — yellow letters',
    ciPlaceholder: 'e.g. ae',
    labelNot: 'Letters that must NOT appear — gray letters',
    cePlaceholder: 'e.g. rst',
    btnSearch: 'Search',
    labelNumwords: 'Number of words in combination',
    opt2: '2 words',
    opt3: '3 words',
    opt4: '4 words',
    opt5: '5 words',
    labelInclude: 'Include these words (comma-separated)',
    fiPlaceholder: 'e.g. stork,birth',
    labelExclude: 'Exclude these words (comma-separated)',
    fePlaceholder: 'e.g. adieu,crane',
    labelMustcombo: 'Letters that must appear in the combination',
    frPlaceholder: 'e.g. aeiou',
    btnFind: 'Find (max 100)',
    footer: 'Play Wordle in English: <a href="https://www.nytimes.com/games/wordle/" target="_blank" rel="noopener">nytimes.com/games/wordle</a><br>Wordlist: Public domain 5-letter English words<br>Worlde-tool: <a href="https://github.com/larsnygard/ordle-tool" target="_blank" rel="noopener">github.com/larsnygard/ordle-tool</a>,license <a href="https://www.gnu.org/licenses/gpl-3.0.html" target="_blank" rel="noopener">GPL&nbsp;3</a>'
  }}
}};

function detectInitialLanguage() {{
  const lang = navigator.language.split('-')[0];
  return ['en', 'no'].includes(lang) ? lang : 'no';
}}

let currentLang = detectInitialLanguage();

function setLanguage(lang) {{
  if(!translations[lang]) lang = 'no';
  currentLang = lang;
  document.documentElement.lang = lang;
  const t = translations[lang];
  
  // Update language selector active state
  document.querySelectorAll('.lang-selector span').forEach((s,i) => {{
    s.classList.toggle('active', (i===0 && lang==='no') || (i===1 && lang==='en'));
  }});
  
  document.title = t.pageTitle;
  document.getElementById('app-title').textContent = t.appTitle;
  // Tabs
  document.getElementById('tab-check').textContent = t.tabCheck;
  document.getElementById('tab-find').textContent = t.tabFind;
  // Check section
  document.getElementById('label-pattern').textContent = t.labelPattern;
  document.getElementById('cpat').placeholder = t.cpatPlaceholder;
  document.getElementById('label-must').textContent = t.labelMust;
  document.getElementById('ci').placeholder = t.ciPlaceholder;
  document.getElementById('label-not').textContent = t.labelNot;
  document.getElementById('ce').placeholder = t.cePlaceholder;
  document.getElementById('btn-search').textContent = t.btnSearch;
  // Find section
  document.getElementById('label-numwords').textContent = t.labelNumwords;
  document.getElementById('opt-2').textContent = t.opt2;
  document.getElementById('opt-3').textContent = t.opt3;
  document.getElementById('opt-4').textContent = t.opt4;
  document.getElementById('opt-5').textContent = t.opt5;
  document.getElementById('label-include').textContent = t.labelInclude;
  document.getElementById('fi').placeholder = t.fiPlaceholder;
  document.getElementById('label-exclude').textContent = t.labelExclude;
  document.getElementById('fe').placeholder = t.fePlaceholder;
  document.getElementById('label-mustcombo').textContent = t.labelMustcombo;
  document.getElementById('fr').placeholder = t.frPlaceholder;
  document.getElementById('btn-find').textContent = t.btnFind;
  // Footer
  document.getElementById('footer-main').innerHTML = t.footer;
  
  // Switch wordlists based on language
  if(lang === 'en') {{
    WORDS_ALL = WORDS_ALL_EN;
    WORDS_UNIQ = WORDS_UNIQ_EN;
  }} else {{
    WORDS_ALL = WORDS_ALL_NO;
    WORDS_UNIQ = WORDS_UNIQ_NO;
  }}
}}

// Initialize language on page load
window.addEventListener('DOMContentLoaded', function() {{
  setLanguage(currentLang);
}});

// ── Service Worker ──
if('serviceWorker' in navigator){{
  navigator.serviceWorker.register('./sw.js');
}}
</script>
</body>
</html>
"""

with open(f"{OUT_DIR}/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"\nPWA written to {OUT_DIR}/")
print(f"  index.html  {os.path.getsize(f'{OUT_DIR}/index.html')//1024} KB")
print(f"  sw.js")
print(f"  manifest.json")
print(f"  icon.svg")
