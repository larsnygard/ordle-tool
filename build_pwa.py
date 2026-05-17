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
.top-actions{{display:flex;align-items:center;gap:.6rem}}
.lang-selector{{display:flex;gap:8px}}
.lang-selector span{{cursor:pointer;font-size:1.5rem;opacity:.6;transition:opacity .2s}}
.lang-selector span.active{{opacity:1}}
.help-link{{
  border:1px solid #3a3a3c;background:transparent;color:#d7dadc;
  border-radius:999px;padding:.25rem .6rem;font-size:.8rem;cursor:pointer;
  text-transform:uppercase;letter-spacing:.05em
}}
.help-link:hover{{border-color:#538d4e;color:#fff}}
.modal{{
  position:fixed;inset:0;background:rgba(0,0,0,.58);display:none;
  align-items:center;justify-content:center;padding:1rem;z-index:20
}}
.modal.open{{display:flex}}
.modal-card{{
  width:min(100%,460px);background:#1a1a1b;border:1px solid #3a3a3c;
  border-radius:12px;padding:1rem 1rem .9rem;position:relative
}}
.modal-card h2{{font-size:1.1rem;color:#d7dadc;margin-bottom:.65rem}}
.modal-body{{color:#d7dadc;font-size:.92rem;line-height:1.45}}
.modal-body ul{{padding-left:1.2rem;margin:.2rem 0 .7rem}}
.modal-body li{{margin:.2rem 0}}
.modal-close{{
  position:absolute;right:.55rem;top:.45rem;background:transparent;border:none;
  color:#818384;font-size:1.4rem;cursor:pointer;line-height:1
}}
.modal-close:hover{{color:#fff}}
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
.btn-row{{display:flex;gap:.5rem}}
.btn-row .btn{{width:auto;flex:1}}
.btn.alt{{background:#3a3a3c}}
.btn.alt:hover{{background:#4a4a4c}}
.btn.alt:active{{background:#2f2f31}}
/* results */
.res{{margin-top:1.4rem}}
.cnt{{color:#818384;font-size:.85rem;margin-bottom:.7rem}}
.wlist{{display:flex;flex-wrap:wrap;gap:6px}}
.word{{background:#3a3a3c;border-radius:5px;padding:.3rem .6rem;
       font-family:monospace;font-size:.95rem;letter-spacing:.04em}}
.clist{{list-style:none}}
.clist li{{background:#3a3a3c;border-radius:5px;padding:.45rem .8rem;
           margin-bottom:4px;font-family:monospace;font-size:.95rem}}
.combo-word{{cursor:pointer;user-select:none}}
.combo-sep{{opacity:.75;padding:0 .2rem}}
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
  <button class="help-link" id="help-link" type="button" onclick="openHelp()">Hjelp</button>
  <h1 id="app-title">Ordle</h1>
  <div class="lang-selector">
    <span onclick="setLanguage('no')" class="active">🇳🇴</span>
    <span onclick="setLanguage('en')">🇬🇧</span>
  </div>
</div>

<div class="tabs">
  <button class="tab" id="tab-find" onclick="showTab('find')">Finn kombinasjoner</button>
  <button class="tab active" id="tab-check" onclick="showTab('check')">Sjekk ord</button>
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
  <label id="label-notcombo">Bokstaver som IKKE må finnes i kombinasjonen</label>
  <input type="text" id="fx" placeholder="f.eks. rst" autocomplete="off" autocorrect="off" spellcheck="false">
  <div class="btn-row">
    <button class="btn" id="btn-find" onclick="runFind(false)">Finn (maks 100)</button>
    <button class="btn alt" id="btn-random" onclick="runFind(true)">Tilfeldig sett</button>
  </div>
  <label style="display:flex;align-items:center;gap:.5em;font-size:.92rem;margin:.5em 0 0 .1em">
    <input type="checkbox" id="find-randomize" style="margin:0 .4em 0 0;vertical-align:middle">
    <span id="find-randomize-label">Vis i tilfeldig rekkefølge</span>
  </label>
  <div class="res" id="fres"></div>
</div>

<div id="help-modal" class="modal" aria-hidden="true">
  <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="help-title">
    <button class="modal-close" id="help-close" type="button" onclick="closeHelp()" aria-label="Close">&times;</button>
    <h2 id="help-title">Slik bruker du verktøyet</h2>
    <div class="modal-body" id="help-body"></div>
  </div>
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
  ['check','find'].forEach((id) => {{
    document.getElementById('tab-' + id).classList.toggle('active', id===t);
    document.getElementById('s-'+id).classList.toggle('on', id===t);
  }});
  window._activeTab = t;
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

function addWordToList(inputId, word){{
  const input = document.getElementById(inputId);
  const words = input.value
    .split(',')
    .map(s => s.trim().toLowerCase())
    .filter(s => s.length > 0);
  const idx = words.indexOf(word);
  if(idx >= 0) {{
    words.splice(idx, 1);
  }} else {{
    words.push(word);
  }}
  input.value = words.join(',');
}}

function renderComboLine(words){{
  const parts=[];
  for(let i=0;i<words.length;i++){{
    const w=words[i];
    parts.push(`<span class="combo-word" data-word="${{w}}">${{w}}</span>`);
    if(i<words.length-1) parts.push('<span class="combo-sep"> · </span>');
  }}
  return parts.join('');
}}

function comboInteractionHint(){{
  return translations[currentLang].comboHint;
}}

function updateHelpContent(){{
  const t = translations[currentLang];
  const tab = window._activeTab || (document.getElementById('s-find').classList.contains('on') ? 'find' : 'check');
  if(tab==='find'){{
    document.getElementById('help-title').textContent = t.helpTitleFind;
    document.getElementById('help-body').innerHTML = t.helpBodyFind;
  }}else{{
    document.getElementById('help-title').textContent = t.helpTitleSolver;
    document.getElementById('help-body').innerHTML = t.helpBodySolver;
  }}
}}

function openHelp(){{
  const modal=document.getElementById('help-modal');
  updateHelpContent();
  modal.classList.add('open');
  modal.setAttribute('aria-hidden','false');
}}

function closeHelp(){{
  const modal=document.getElementById('help-modal');
  modal.classList.remove('open');
  modal.setAttribute('aria-hidden','true');
}}

function attachComboInteractions(){{
  const fres=document.getElementById('fres');
  let pressTimer=null;
  let touchTarget=null;
  let touchStartX=0;
  let touchStartY=0;
  let suppressNextClickWord='';

  const clearPress=()=>{{
    if(pressTimer){{
      clearTimeout(pressTimer);
      pressTimer=null;
    }}
    touchTarget=null;
  }};

  fres.addEventListener('pointerdown', e=>{{
    const t=e.target.closest('.combo-word');
    if(!t) return;
    t.dataset.longPress='0';
    t.dataset.ignoreNextContext='0';
  }});

  fres.addEventListener('pointerup', clearPress);
  fres.addEventListener('pointercancel', clearPress);

  // Real touchscreens are less consistent with pointer long-press.
  // Use explicit touch events for robust long-press exclude behavior.
  fres.addEventListener('touchstart', e=>{{
    const t=e.target.closest('.combo-word');
    if(!t) return;
    const touch=e.changedTouches[0];
    touchStartX=touch.clientX;
    touchStartY=touch.clientY;
    touchTarget=t;
    t.dataset.longPress='0';
    t.dataset.ignoreNextContext='0';
    pressTimer=setTimeout(()=>{{
      if(!touchTarget) return;
      addWordToList('fe', t.dataset.word);
      t.dataset.longPress='1';
      t.dataset.ignoreNextContext='1';
      suppressNextClickWord=t.dataset.word;
    }}, 550);
  }}, {{passive:true}});

  fres.addEventListener('touchmove', e=>{{
    if(!touchTarget || !pressTimer) return;
    const touch=e.changedTouches[0];
    if(!touch) return;
    const dx=Math.abs(touch.clientX-touchStartX);
    const dy=Math.abs(touch.clientY-touchStartY);
    if(dx>10 || dy>10) clearPress();
  }}, {{passive:true}});

  fres.addEventListener('touchend', clearPress, {{passive:true}});
  fres.addEventListener('touchcancel', clearPress, {{passive:true}});

  fres.addEventListener('click', e=>{{
    const t=e.target.closest('.combo-word');
    if(!t) return;
    if(suppressNextClickWord && suppressNextClickWord===t.dataset.word){{
      suppressNextClickWord='';
      return;
    }}
    if(t.dataset.longPress==='1'){{
      t.dataset.longPress='0';
      return;
    }}
    addWordToList('fi', t.dataset.word);
  }});

  fres.addEventListener('contextmenu', e=>{{
    const t=e.target.closest('.combo-word');
    if(!t) return;
    e.preventDefault();
    if(t.dataset.ignoreNextContext==='1'){{
      t.dataset.ignoreNextContext='0';
      return;
    }}
    addWordToList('fe', t.dataset.word);
  }});
}}

// Enter key in check inputs
['cpat','ci','ce'].forEach(id=>{{
  document.getElementById(id).addEventListener('keydown',e=>{{if(e.key==='Enter')runCheck();}});
}});

// ── FIND ──
function shuffleInPlace(arr){{
  for(let i=arr.length-1;i>0;i--){{
    const j=Math.floor(Math.random()*(i+1));
    [arr[i],arr[j]]=[arr[j],arr[i]];
  }}
}}

function runFind(randomOnly=false){{
  const randomizeList = document.getElementById('find-randomize')?.checked;
  const n=parseInt(document.getElementById('fn').value);
  const rawInc=document.getElementById('fi').value;
  const rawExc=document.getElementById('fe').value;
  const reqStr=document.getElementById('fr').value.toLowerCase().replace(/[^a-z\u00e6\u00f8\u00e5]/g,'');
  const excReqStr=document.getElementById('fx').value.toLowerCase().replace(/[^a-z\u00e6\u00f8\u00e5]/g,'');
  const required=new Set(reqStr);
  const excluded=new Set(excReqStr);
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
  for(const c of excluded){{
    if(required.has(c)){{
      el.innerHTML=`<div class="err">Feil: Bokstaven '${{c}}' kan ikke være både påkrevd og ekskludert.</div>`;return;
    }}
    if(incChars.has(c)){{
      el.innerHTML=`<div class="err">Feil: Ekskludert bokstav '${{c}}' finnes i inkluderte ord.</div>`;return;
    }}
  }}
  if(incChars.size!==incWords.reduce((s,w)=>s+[...w].length,0)){{
    el.innerHTML='<div class="err">Feil: Inkluderte ord har overlappende bokstaver.</div>';return;
  }}
  if(incWords.length>=n){{
    el.innerHTML='<div class="err">Feil: Antall inkluderte ord m&aring; v&aelig;re mindre enn kombinasjonst&oslash;rrelsen.</div>';return;
  }}

  el.innerHTML=randomOnly
    ? '<div class="spin">Genererer tilfeldig sett...</div>'
    : '<div class="spin">S&oslash;ker\u2026</div>';
  setTimeout(()=>{{
    const remaining=WORDS_UNIQ.filter(w=>
      !excSet.has(w)&&
      [...w].every(c=>!incChars.has(c))&&
      [...w].every(c=>!excluded.has(c))
    );
    const need=n-incWords.length;
    const combos=[];

    function randomSearch(){{
      const order=[...remaining];
      shuffleInPlace(order);

      function pick(start,current,used){{
        if(current.length===need){{
          if(required.size>0){{
            const all=new Set([...incChars,...used]);
            for(const c of required) if(!all.has(c)) return null;
          }}
          return [...incWords,...current];
        }}
        for(let i=start;i<order.length;i++){{
          const w=order[i];
          if([...w].some(c=>used.has(c))) continue;
          for(const c of w) used.add(c);
          current.push(w);
          const found=pick(i+1,current,used);
          if(found) return found;
          current.pop();
          for(const c of w) used.delete(c);
        }}
        return null;
      }}

      return pick(0,[],new Set());
    }}

    if(randomOnly){{
      const one=randomSearch();
      if(!one){{
        el.innerHTML='<div class="cnt">Ingen kombinasjoner funnet.</div>';
        return;
      }}
      el.innerHTML=
        '<div class="cnt">Tilfeldig kombinasjon</div>'+
        `<div class="note">${{comboInteractionHint()}}</div>`+
        `<ul class="clist"><li>${{renderComboLine(one)}}</li></ul>`;
      return;
    }}

    // --- Combo generation logic ---
    let allCombos = [];
    function collectAllCombos(start,current,used){{
      if(allCombos.length>=10000) return; // hard cap for perf
      if(current.length===need){{
        if(required.size>0){{
          const all=new Set([...incChars,...used]);
          for(const c of required) if(!all.has(c))return;
        }}
        allCombos.push([...incWords,...current]);
        return;
      }}
      for(let i=start;i<remaining.length;i++){{
        const w=remaining[i];
        if([...w].some(c=>used.has(c)))continue;
        for(const c of w)used.add(c);
        current.push(w);
        collectAllCombos(i+1,current,used);
        current.pop();
        for(const c of w)used.delete(c);
      }}
    }}

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

    if(randomizeList){{
      // Generate 100 random valid combos, shuffling include-words into each
      let found = 0;
      let shownCombos = [];
      const maxTries = 10000;
      let tries = 0;
      while(found < 100 && tries < maxTries){{
        tries++;
        // Pick random words for the rest
        const pool = remaining.slice();
        for(let i=pool.length-1;i>0;i--){{
          const j=Math.floor(Math.random()*(i+1));
          [pool[i],pool[j]]=[pool[j],pool[i]];
        }}
        let used = new Set(incWords.flatMap(w=>[...w]));
        let combo = [...incWords];
        for(let i=0;i<need;i++){{
          let foundIdx = -1;
          for(let j=0;j<pool.length;j++){{
            const w = pool[j];
            if([...w].some(c=>used.has(c))) continue;
            foundIdx = j; break;
          }}
          if(foundIdx === -1){{ combo = null; break; }}
          const w = pool[foundIdx];
          combo.push(w);
          for(const c of w) used.add(c);
          pool.splice(foundIdx,1);
        }}
        if(combo){{
          // Check required letters
          if(required.size>0){{
            const all=new Set(combo.flatMap(w=>[...w]));
            let ok = true;
            for(const c of required) if(!all.has(c)) ok = false;
            if(!ok) continue;
          }}
          // Shuffle the combo so include-words are not always first
          for(let i=combo.length-1;i>0;i--){{
            const j=Math.floor(Math.random()*(i+1));
            [combo[i],combo[j]]=[combo[j],combo[i]];
          }}
          // Avoid duplicates
          const key = combo.join(',');
          if(!shownCombos.some(arr=>arr.join(',')===key)){{
            shownCombos.push(combo);
            found++;
          }}
        }}
      }}
      if(shownCombos.length===0){{
        el.innerHTML='<div class="cnt">Ingen kombinasjoner funnet.</div>';
      }}else{{
        const trunc=tries>=maxTries;
        el.innerHTML=
          `<div class="cnt">Viser ${{shownCombos.length}} tilfeldige kombinasjoner${{trunc?' (maks 100, tilfeldig utvalg)':''}}</div>`+
          `<div class="note">${{comboInteractionHint()}}</div>`+
          '<ul class="clist">'+shownCombos.map(c=>`<li>${{renderComboLine(c)}}</li>`).join('')+'</ul>';
      }}
    }}else{{
      search(0,[],new Set());
      if(combos.length===0){{
        el.innerHTML='<div class="cnt">Ingen kombinasjoner funnet.</div>';
      }}else{{
        const trunc=combos.length>=100;
        let shownCombos = combos.slice();
        el.innerHTML=
          `<div class="cnt">Viser ${{combos.length}} kombinasjoner${{trunc?' (maks 100 &ndash; bruk inkluder-feltet for &aring; begrense s&oslash;ket)':''}}</div>`+
          `<div class="note">${{comboInteractionHint()}}</div>`+
          '<ul class="clist">'+shownCombos.map(c=>`<li>${{renderComboLine(c)}}</li>`).join('')+'</ul>';
      }}
    }}
  }},10);
}}

['fi','fe','fr','fx'].forEach(id=>{{
  document.getElementById(id).addEventListener('keydown',e=>{{if(e.key==='Enter')runFind(false);}});
}});

// ── LANGUAGE SWITCHING ──
const translations = {{
  no: {{
    pageTitle: 'Ordle - Norsk Wordle-hjelper',
    appTitle: 'Ordle',
    tabCheck: 'Løser',
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
    labelNotcombo: 'Bokstaver som IKKE må finnes i kombinasjonen',
    fxPlaceholder: 'f.eks. rst',
    btnFind: 'Finn (maks 100)',
    btnRandom: 'Tilfeldig sett',
    findRandomize: 'Tilfeldig rekkefølge',
    comboHint: 'Trykk/klikk på ord for å inkludere. Høyreklikk eller langt trykk for å ekskludere.',
    helpLink: 'Hjelp',
    helpTitleSolver: 'Slik bruker du Løser',
    helpBodySolver: '<ul><li>Bruk Løser for å finne ord som matcher mønster, inkluderte bokstaver og ekskluderte bokstaver.</li><li>Fyll inn mønsteret (bruk . for ukjent bokstav), bokstaver som må være med, og bokstaver som ikke skal være med. Trykk Søk for å se alle ord som passer.</li></ul>',
    helpTitleFind: 'Slik bruker du Finn kombinasjoner',
    helpBodyFind: '<ul><li>Bruk Finn kombinasjoner for å bygge ordsett uten overlappende bokstaver.</li><li>Fyll inn antall ord, ord som skal inkluderes eller ekskluderes, og bokstaver som må eller ikke må være med.</li><li>Trykk Finn for en liste, eller Tilfeldig sett for ett forslag.</li><li>Trykk/klikk et ord for å inkludere, høyreklikk eller langt trykk for å ekskludere. Randomize gir tilfeldig utvalg i listen.</li></ul>',
    footer: 'Spill Wordle på norsk: <a href="https://ordle.no" target="_blank" rel="noopener">ordle.no</a><br>Ordliste: <a href="https://www.nb.no/sprakbanken/ressurskatalog/oai-nb-no-sbr-5/" target="_blank" rel="noopener">Norsk ordbank – bokmål 2005</a>&copy; Universitetet i Bergen &amp; Språkrådet,distribuert av <a href="https://www.nb.no/sprakbanken" target="_blank" rel="noopener">Språkbanken</a>,lisens <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">CC BY 4.0</a><br>Ordle-verktøy: <a href="https://github.com/larsnygard/ordle-tool" target="_blank" rel="noopener">github.com/larsnygard/ordle-tool</a>,lisens <a href="https://www.gnu.org/licenses/gpl-3.0.html" target="_blank" rel="noopener">GPL&nbsp;3</a>'
  }},
  en: {{
    pageTitle: 'Worlde - English Wordle Helper',
    appTitle: 'Worlde',
    tabCheck: 'Solver',
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
    labelNotcombo: 'Letters that must NOT appear in the combination',
    fxPlaceholder: 'e.g. rst',
    btnFind: 'Find (max 100)',
    btnRandom: 'Random set',
    findRandomize: 'Randomize',
    comboHint: 'Tap/click a word to include it. Right-click or long-press to exclude it.',
    helpLink: 'Help',
    helpTitleSolver: 'How to use Solver',
    helpBodySolver: '<ul><li>Use Solver to find words that match your pattern, required letters, and excluded letters.</li><li>Fill in the pattern (use . for unknown letters), letters that must be included, and letters to exclude.</li><li>Press Search to see all matching words.</li></ul>',
    helpTitleFind: 'How to use Find combinations',
    helpBodyFind: '<ul><li>Use Find combinations to build sets of words with no overlapping letters.</li><li>Set number of words, include/exclude words, and required/excluded letters.</li><li>Press Find for a list, or Random set for one suggestion.</li><li>Tap/click a word to include it, right-click or long-press to exclude it. Randomize gives a random list sample.</li></ul>',
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
  document.getElementById('label-notcombo').textContent = t.labelNotcombo;
  document.getElementById('fx').placeholder = t.fxPlaceholder;
  document.getElementById('btn-find').textContent = t.btnFind;
  document.getElementById('btn-random').textContent = t.btnRandom;
  document.getElementById('find-randomize-label').textContent = t.findRandomize;
  document.getElementById('help-link').textContent = t.helpLink;
  updateHelpContent();
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
  // Always show Find tab by default after language switch
  showTab('find');
}}

// Initialize language on page load
window.addEventListener('DOMContentLoaded', function() {{
  setLanguage(currentLang);
  showTab('find');
  attachComboInteractions();
  document.getElementById('find-randomize').addEventListener('change',()=>runFind(false));
  document.getElementById('help-modal').addEventListener('click', (e)=>{{
    if(e.target.id==='help-modal') closeHelp();
  }});
  document.addEventListener('keydown', (e)=>{{
    if(e.key==='Escape') closeHelp();
  }});
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

