#!/usr/bin/env python3
"""Build the Ordle PWA into docs/ with embedded word lists."""
import json
import os

WORDLIST = "fullformsliste.txt"
OUT_DIR = "docs"

# ── Extract word lists ──────────────────────────────────────────────────────
print(f"Reading {WORDLIST}...")
all5: set[str] = set()
uniq5: set[str] = set()

with open(WORDLIST, encoding="latin-1") as f:
    next(f)  # skip header
    for line in f:
        parts = line.strip().split()
        if len(parts) > 2:
            w = parts[2].lower()
            if len(w) == 5 and w.isalpha():
                all5.add(w)
                if len(set(w)) == 5:
                    uniq5.add(w)

words_all_js  = json.dumps(sorted(all5),  ensure_ascii=False)
words_uniq_js = json.dumps(sorted(uniq5), ensure_ascii=False)
print(f"  all 5-letter words : {len(all5):,}")
print(f"  unique-char words  : {len(uniq5):,}")

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
h1{{text-align:center;margin-bottom:1.2rem;font-size:1.8rem;
    color:#538d4e;letter-spacing:.1em}}
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
</style>
</head>
<body>
<h1>Ordle</h1>

<div class="tabs">
  <button class="tab active" onclick="showTab('check')">Sjekk ord</button>
  <button class="tab"        onclick="showTab('find')">Finn kombinasjoner</button>
</div>

<!-- ── CHECK ── -->
<div id="s-check" class="sec on">
  <label>M&oslash;nster &mdash; bruk . for ukjent bokstav</label>
  <input type="text" id="cpat" maxlength="5" placeholder="f.eks. ..a.e" autocomplete="off" autocorrect="off" spellcheck="false">
  <label>Bokstaver som M&Aring; finnes &mdash; gule bokstaver</label>
  <input type="text" id="ci" placeholder="f.eks. ae" autocomplete="off" autocorrect="off" spellcheck="false">
  <label>Bokstaver som IKKE finnes &mdash; gr&aring; bokstaver</label>
  <input type="text" id="ce" placeholder="f.eks. rst" autocomplete="off" autocorrect="off" spellcheck="false">
  <button class="btn" onclick="runCheck()">S&oslash;k</button>
  <div class="res" id="cr"></div>
</div>

<!-- ── FIND ── -->
<div id="s-find" class="sec">
  <label>Antall ord i kombinasjonen</label>
  <select id="fn">
    <option value="2">2 ord</option>
    <option value="3" selected>3 ord</option>
    <option value="4">4 ord</option>
    <option value="5">5 ord</option>
  </select>
  <label>Inkluder disse ordene (kommaseparert)</label>
  <input type="text" id="fi" placeholder="f.eks. sterk,byliv" autocomplete="off" autocorrect="off" spellcheck="false">
  <label>Bokstaver som M&Aring; finnes i kombinasjonen</label>
  <input type="text" id="fr" placeholder="f.eks. aeiou" autocomplete="off" autocorrect="off" spellcheck="false">
  <button class="btn" onclick="runFind()">Finn (maks 100)</button>
  <div class="res" id="fres"></div>
</div>

<script>
const WORDS_ALL  = {words_all_js};
const WORDS_UNIQ = {words_uniq_js};

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
  const reqStr=document.getElementById('fr').value.toLowerCase().replace(/[^a-z\u00e6\u00f8\u00e5]/g,'');
  const required=new Set(reqStr);
  const el=document.getElementById('fres');

  const incWords=rawInc.split(',').map(s=>s.trim().toLowerCase()).filter(s=>s.length>0);
  // validate include words
  for(const w of incWords){{
    if([...w].length!==5||!/^[a-z\u00e6\u00f8\u00e5]+$/u.test(w)){{
      el.innerHTML=`<div class="err">Feil: '${{w}}' er ikke et gyldig 5-bokstavsord.</div>`;return;
    }}
    if(new Set(w).size!==[...w].length){{
      el.innerHTML=`<div class="err">Feil: '${{w}}' har gjentatte bokstaver.</div>`;return;
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
    const remaining=WORDS_UNIQ.filter(w=>[...w].every(c=>!incChars.has(c)));
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

['fi','fr'].forEach(id=>{{
  document.getElementById(id).addEventListener('keydown',e=>{{if(e.key==='Enter')runFind();}});
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
