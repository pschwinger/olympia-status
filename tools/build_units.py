#!/usr/bin/env python3
"""Generate unit / artifact / selection pages from board/manifest.js + the storyboard registry.
One data source, one command, no drift. Run from the olympia-status repo root:  python3 tools/build_units.py
"""
import json, os, re, subprocess, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SB = os.path.expanduser("~/Projects/empirica-storyboard")

# ---------- data ----------
def load_manifest():
    js = "var V='media/v/', I='/empirica-imagegen/out/', R='media/r/';" + \
         open(f"{ROOT}/board/manifest.js").read().replace("var EX=R+'Unit 1/Pilot 2/Olympic Museum/1_Execution/';","")
    out = subprocess.run(["node","-e", js + ";var EX=R+'Unit 1/';console.log(JSON.stringify({A:A,MANIFEST:MANIFEST}))"],
                         capture_output=True, text=True, cwd=f"{ROOT}/board")
    return json.loads(out.stdout)

def all_cards(man):
    for sec in man["MANIFEST"]:
        pools = list(sec.get("shots", []))
        for sc in sec.get("scenes", []): pools += sc.get("shots", [])
        for sh in pools:
            if sh.get("num"): yield sec, sh


import hashlib
def poster_for(src):
    """Board poster rule: posters/md5(pref+rel)[:10].jpg ; generate from local media if absent."""
    if src.startswith("media/v/"): pref, rel = "V", src[len("media/v/"):]
    elif src.startswith("media/r/"): pref, rel = "R", src[len("media/r/"):]
    else: return None
    h = hashlib.md5((pref+rel).encode()).hexdigest()[:10]
    p = f"{ROOT}/board/posters/{h}.jpg"
    if not os.path.exists(p):
        local = f"{ROOT}/board/{src}"
        if os.path.exists(local):
            subprocess.run(["ffmpeg","-loglevel","error","-y","-ss","1.5","-i",local,"-frames:v","1","-q:v","4","-vf","scale=560:-1",p])
        if not os.path.exists(p): return None
    return f"board/posters/{h}.jpg"

REG = json.load(open(f"{SB}/assets/registry.json"))["artefacts"]

# ---------- unit definitions (museum text marked verbatim) ----------
UNITS = {
1: dict(title="From Discovery to Revival", ours="Revival of the Olympic Games",
  museum_visuals="ruins being uncovered · archaeological drawings, maps of Olympia · excavation photos · athletes, musicians with lyre and aulos, spectators, Temple of Zeus · Philhellenic paintings, Romantic landscapes · Zappas Olympiads, early modern imagery",
  artifacts=["SM_RV_1","SM_RV_16"],
  story="We made the 1875 rediscovery (1a) the proving ground: real archival photographs found and cited, character sheets as types never portraits, the environment matched to the true geography, and the scene built shot by measured shot - five prompt versions to one scene of record, then the continuation and the 30-second coverage roll. The kotinos, this unit's artefact, carries the Crowning, the Cutting of the Wreath (every beat sourced to Pausanias) and the with/without proof."),
2: dict(title="The First Modern Games & the Olympic Symbols", ours="Symbols & ceremonies",
  museum_visuals="Sorbonne 1894, delegates, the Coubertin-Vikelas handshake · animated Athens 1896 stadium · parade of nations, Greece first · animated rings · torch lighting, relay across continents · flag, anthem, oath",
  artifacts=["SM_RV_6","SM_RV_12"],
  story="The First Flame is the fidelity flagship: every frame of the animated Berlin 1936 torch is a crop of a verified still - a formal certificate of provenance, zero possibility of invention. The 1896 medal taught the hardest lesson of the project: objects that ARE text defeat every prompt-level prohibition, so text-dominant artifacts now default to deterministic treatment (the failed take is published, labeled, as the evidence)."),
3: dict(title="The Mesolympic Games, Athens 1906", ours="Victory & honour (old card)",
  museum_visuals="Athens modernised: trams, electric light, decorated streets · Panathenaic Stadium full, royal guests · Sherring winning the marathon · medals, cups by sculptors as prizes",
  artifacts=["SM_RV_3","SM_RV_14"],
  story="The Marathon Cup carries this unit today; the 1906 participation medal - digitised but never used - got its first shots ever in the overnight run, deterministic over the real reverse. Open research: whether the cup was the awarded prize or a commemorative piece decides how its scene is staged - where the record is silent, the ledger says so."),
4: dict(title="Olympic Values through Sports & Music", ours="Athletes & their objects",
  museum_visuals="equipment as instruments · rhythm and silence · Excellence, Friendship, Respect · the museum's deepest unit: 18 named objects, 17 delivered",
  artifacts=["SM_RV_8","SM_RV_18"],
  story="The Drop introduced the person guard: the gymnast composed facing away, because the real Sydney 2000 team's identities are not ours to invent. Shoe and racket shots run clean on inscriptions. Five of Philipp's shot notes (medal scale, arrow flight, club silhouette, runner coverage, the epee as a real scene) are queued as the fix round."),
5: dict(title="International Olympic Day, a Global Movement", ours="Legacy",
  museum_visuals="Olympic Day 23 June · the Olympic Day Run in 150+ countries · the Museum in Thessaloniki as organiser · digital video content, no physical artefacts",
  artifacts=[],
  story="No physical artefacts exist in this unit; the Museum plans digital content here. Our context shots and the present-day run beat are the placeholders until this unit's digital story is designed."),
}

SEC2UNIT = {"u1a":1,"ab-kling":1,"crowning":1,"cutting":1,"beat1":1,"firstflame":2,"club":4,"trailerB":4,"context":5}
KEY2UNIT = {"a1":1,"a2":1,"s6":1,"s3":1,"t-kot":1,"t-with":1,"t-without":1,"t-real":1,
            "a3":2,"a4":2,"s2":2,"t-torch":2,"fail-1896-s3":2,
            "a5":3,"s4":3,"a6":5,"s5":4,"s1b":4,
            "v22-run3":1,"wreath-a":1,"part2-armA":1,"part2-armB":1,"cov30":1,"night-cut":1}
def unit_of(sec, sh):
    k = sh["key"]
    if k in KEY2UNIT: return KEY2UNIT[k]
    if k.startswith("sm_rv_16") or k.startswith("1a_v"): return 1
    if k.startswith("sm_rv_6"): return 2
    if k.startswith("sm_rv_3"): return 3
    return SEC2UNIT.get(sec["id"])

KEY2ART = {"a1":["SM_RV_16"],"s6":["SM_RV_16"],"t-with":["SM_RV_16"],"t-without":["SM_RV_16"],"t-real":["SM_RV_16"],"t-kot":["SM_RV_16"],
           "ab-long":["SM_RV_16"],"ab-short":["SM_RV_16"],"night-cut":["SM_RV_16","SM_RV_6","SM_RV_3"],"wreath-a":["SM_RV_16"],
           "a2":["SM_RV_1"],"s3":["SM_RV_1"],"a3":["SM_RV_6"],"fail-1896-s3":["SM_RV_6"],
           "a4":["SM_RV_12"],"s2":["SM_RV_12"],"t-torch":["SM_RV_12"],
           "a5":["SM_RV_14"],"s4":["SM_RV_14"],"b7":["SM_RV_8"],"b2":["SM_RV_18"],"s1b":["SM_RV_18"],"t-shoes-real":["SM_RV_18"],
           "b4":["SM_RV_13"],"s5":["SM_RV_13"]}
def arts_of(sec, sh):
    k=sh["key"]
    if k in KEY2ART: return KEY2ART[k]
    m=re.match(r"(sm_rv_\d+)_", k)
    if m: return [m.group(1).upper().replace("SM_RV","SM_RV")]
    a=sh.get("asset")
    if isinstance(a,dict) and a.get("code"): return [a["code"]]
    for sid,codes in {"firstflame":["SM_RV_12"],"crowning":["SM_RV_16"],"cutting":["SM_RV_16"],"club":["SM_RV_8"],"beat1":["SM_RV_16"],"ab-kling":["SM_RV_16"]}.items():
        if sec["id"]==sid: return codes
    return []

SELECTED = ["night-cut","v22-run3","part2-armA","cov30","ff-master"]

# ---------- html ----------
CSS = open(f"{ROOT}/tools/site.css").read() if os.path.exists(f"{ROOT}/tools/site.css") else ""
NAV = """<div id="olynav" style="position:sticky;top:0;z-index:999;display:flex;gap:6px;flex-wrap:wrap;align-items:center;background:#1e2418;padding:8px 14px;border-bottom:1px solid #3a4030">
<a href="index.html" style="text-decoration:none;font:600 12px Archivo,system-ui;padding:5px 10px;border-radius:7px;background:#54682f;color:#fff">⌂ Home</a>
<a href="units.html" style="text-decoration:none;font:600 12px Archivo,system-ui;padding:5px 10px;border-radius:7px;color:#cfd3c0">🏛 Units</a>
<a href="artifacts.html" style="text-decoration:none;font:600 12px Archivo,system-ui;padding:5px 10px;border-radius:7px;color:#cfd3c0">🏺 Artifacts</a>
<a href="selection.html" style="text-decoration:none;font:600 12px Archivo,system-ui;padding:5px 10px;border-radius:7px;color:#cfd3c0">★ Selection</a>
<a href="casestudy.html" style="text-decoration:none;font:600 12px Archivo,system-ui;padding:5px 10px;border-radius:7px;color:#cfd3c0">🔬 Method</a>
<a href="board/review.html" style="text-decoration:none;font:600 12px Archivo,system-ui;padding:5px 10px;border-radius:7px;color:#cfd3c0">🗄 Working room</a>
<span style="margin-left:auto;font:600 10px 'IBM Plex Mono',monospace;letter-spacing:.1em;color:#8b8f80">OLYMPIA · REEVALUATE</span></div>"""

STYLE = """<style>
:root{--bg:#edeee6;--surface:#f6f6f1;--surface-2:#e7e9df;--ink:#191c15;--steel:#454a3c;--muted:#6d7261;--hair:#d3d5c8;--olive:#54682f;--bronze:#a06a24;--good:#3f7a4c;--flame:#ba5a1e}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#13150e;--surface:#1a1d14;--surface-2:#20241a;--ink:#dce0d2;--steel:#a7ad98;--muted:#7f846d;--hair:#282c1f;--olive:#9fb56b;--bronze:#cf9748;--good:#77b183;--flame:#d9743a}}
:root[data-theme="dark"]{--bg:#13150e;--surface:#1a1d14;--surface-2:#20241a;--ink:#dce0d2;--steel:#a7ad98;--muted:#7f846d;--hair:#282c1f;--olive:#9fb56b;--bronze:#cf9748;--good:#77b183;--flame:#d9743a}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:Archivo,system-ui,sans-serif;font-size:15.5px;line-height:1.55}
.wrap{max-width:1060px;margin:0 auto;padding:clamp(20px,3vw,44px) clamp(14px,3vw,32px) 90px}
h1{font-family:Fraunces,serif;font-weight:500;font-size:clamp(1.8rem,4.5vw,2.7rem);line-height:1.06;margin:0 0 8px}
h2{font-family:Fraunces,serif;font-weight:500;font-size:1.45rem;margin:34px 0 6px}
.k{font-family:'IBM Plex Mono',monospace;font-size:10.5px;letter-spacing:.18em;text-transform:uppercase;color:var(--bronze);margin:24px 0 6px}
p{max-width:76ch}.muted{color:var(--steel)}
.mtag{display:inline-block;font-size:.65rem;letter-spacing:.08em;text-transform:uppercase;background:rgba(138,109,31,.12);color:#8a6d1f;border:1px solid rgba(138,109,31,.4);border-radius:4px;padding:0 6px;margin-right:6px}
.musdoc{background:rgba(138,109,31,.06);border:1px solid rgba(138,109,31,.25);border-radius:10px;padding:12px 16px;margin:10px 0;font-size:.95rem}
.cardgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:12px;margin:14px 0}
.card{background:var(--surface);border:1px solid var(--hair);border-radius:12px;padding:12px 14px;margin:0;font-size:.92rem}
.card b{font-size:.95rem}
.card .muted{font-size:.84rem;max-height:5.2em;overflow:hidden}
.card video{width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:10px;border:1px solid var(--hair);background:#000;display:block}
.num{display:inline-block;background:#8a6d1f;color:#fff;border-radius:5px;font-size:11px;font-weight:700;padding:1px 7px;margin-right:7px}
.fl{display:inline-block;font-size:.72rem;color:#fff;background:var(--flame);border-radius:5px;padding:1px 7px;margin-left:6px}
.vers{display:flex;gap:5px;flex-wrap:wrap;margin:8px 0}
.vers button{font-size:12px;padding:3px 10px;border:1px solid var(--hair);border-radius:6px;background:var(--surface-2);color:var(--steel);cursor:pointer}
.vers button.on{background:var(--olive);color:#fff;border-color:var(--olive)}
.meta{font-size:.85rem;color:var(--muted);margin-top:6px}
.meta a{color:var(--bronze)}
.marks{display:flex;gap:5px;margin-top:8px}
.mbtn{font-size:11px;font-weight:600;padding:2px 10px;border:1px solid var(--hair);border-radius:6px;background:transparent;color:var(--muted);cursor:pointer}
.mbtn[data-m="keep"].on{background:#1d7a3e;border-color:#1d7a3e;color:#fff}.mbtn[data-m="change"].on{background:#a87616;border-color:#a87616;color:#fff}.mbtn[data-m="no"].on{background:#a33636;border-color:#a33636;color:#fff}
.fb{width:100%;min-height:30px;margin-top:6px;font-size:12.5px;border:1px solid var(--hair);border-radius:8px;background:var(--surface-2);color:var(--ink);padding:6px 9px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px}
.tile{background:var(--surface);border:1px solid var(--hair);border-radius:12px;padding:14px 16px;text-decoration:none;color:var(--ink)}
.tile b{display:block;margin-bottom:4px}.tile span{font-size:.85rem;color:var(--steel)}
.bar{position:fixed;bottom:14px;right:14px;display:flex;gap:8px;z-index:99}
.bar button{font:600 12.5px Archivo;padding:8px 14px;border-radius:9px;border:1px solid var(--hair);background:var(--olive);color:#fff;cursor:pointer}
.jump{margin-left:8px}.jump input{width:70px;font-size:12px;padding:4px 8px;border:1px solid var(--hair);border-radius:6px;background:var(--surface);color:var(--ink)}
img.thumb{max-width:100%;border-radius:8px;border:1px solid var(--hair)}
.foot{margin-top:60px;padding-top:14px;border-top:1px solid var(--hair);font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--muted)}
</style>"""

JS = """<script>
var MKEY='olympia-marks-v1', FKEY='olympia-review-v1';
function mload(){try{return JSON.parse(localStorage.getItem(MKEY)||'{}')}catch(e){return{}}}
function msave(d){try{localStorage.setItem(MKEY,JSON.stringify(d))}catch(e){}}
function floadd(){try{return JSON.parse(localStorage.getItem(FKEY)||'{}')}catch(e){return{}}}
document.addEventListener('click',function(e){
  var b=e.target.closest&&e.target.closest('.mbtn');
  if(b){var row=b.closest('.marks'),d=mload(),k=row.dataset.shot;
    if(d[k]===b.dataset.m){delete d[k]}else{d[k]=b.dataset.m}
    msave(d);row.querySelectorAll('.mbtn').forEach(function(x){x.classList.toggle('on',d[k]===x.dataset.m)});return;}
  var v=e.target.closest&&e.target.closest('.vers button');
  if(v){var card=v.closest('.card'),vid=card.querySelector('video');vid.src=v.dataset.src;vid.load();
    card.querySelectorAll('.vers button').forEach(function(x){x.classList.remove('on')});v.classList.add('on');}
});
document.addEventListener('input',function(e){if(e.target.classList&&e.target.classList.contains('fb')){
  var d=floadd();var k=e.target.dataset.shot;if(e.target.value.trim())d[k]=e.target.value.trim();else delete d[k];
  try{localStorage.setItem(FKEY,JSON.stringify(d))}catch(e2){}}});
window.addEventListener('DOMContentLoaded',function(){
  var m=mload(),f=floadd();
  document.querySelectorAll('.marks').forEach(function(r){var v=m[r.dataset.shot];r.querySelectorAll('.mbtn').forEach(function(b){b.classList.toggle('on',b.dataset.m===v)})});
  document.querySelectorAll('.fb').forEach(function(t){if(f[t.dataset.shot])t.value=f[t.dataset.shot]});
});
function copyAll(){var m=mload(),f=floadd(),rows=[];
  document.querySelectorAll('.marks').forEach(function(r){var k=r.dataset.shot,n=r.dataset.num,mm=m[k],ff=f[k];
    if(mm||ff)rows.push({n:parseInt(n||9999),line:'#'+(n||'?')+' ['+k+'] '+(mm?mm.toUpperCase():'')+(mm&&ff?' — ':'')+(ff||'')});});
  rows.sort(function(a,b){return a.n-b.n});
  var out='Olympia review — marks ('+new Date().toISOString().slice(0,10)+')\\n\\n'+(rows.length?rows.map(function(r){return r.line}).join('\\n'):'(nothing marked)');
  if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(out).then(function(){var b=document.getElementById('cpy');b.textContent='Copied ✓';setTimeout(function(){b.textContent='Copy my marks'},1500)})}else{window.prompt('Copy:',out)}}
function jumpN(){var n=document.getElementById('jn').value.replace('#','');var el=document.getElementById('v'+n);
  if(el){el.scrollIntoView({behavior:'smooth'});el.style.outline='3px solid var(--bronze)';setTimeout(function(){el.style.outline=''},2500)}else{alert('#'+n+' is not on this page — try the Working room (full archive).')}}
</script>"""

BAR = """<div class="bar"><span class="jump"><input id="jn" placeholder="#nr"><button onclick="jumpN()">Jump</button></span><button id="cpy" onclick="copyAll()">Copy my marks</button></div>"""

def head(title):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow">
<title>{html.escape(title)}</title><meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500&family=Archivo:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
</head><body>{NAV}{STYLE}<div class="wrap">"""

FOOT = """<p class="foot">REEVALUATE · every claim traceable to a ledger · full archive in the <a href="board/review.html" style="color:var(--bronze)">working room</a></p></div>""" + JS + "</body></html>"

def render_card(sec, sh, prefix="board/"):
    vs = sh.get("versions") or []
    first = vs[0] if vs else None
    vid = ""
    if first:
        po = poster_for(first["src"])
        pa = f' poster="{po}"' if po else ""
        vid = f'<video controls preload="none"{pa} src="{prefix}{html.escape(first["src"])}"></video>' 
    btns = ""
    if len(vs) > 1:
        btns = '<div class="vers">' + "".join(
            f'<button data-src="{prefix}{html.escape(v["src"])}" class="{"on" if i==0 else ""}">{html.escape(v.get("label","v"))}</button>'
            for i,v in enumerate(vs)) + "</div>"
    meta = []
    if sh.get("prompt"): meta.append(f'<a href="{prefix}{html.escape(sh["prompt"])}" target="_blank">prompt</a>')
    if sh.get("ledger"): meta.append(f'<a href="{prefix}{html.escape(sh["ledger"])}" target="_blank">ledger (model · measurements · cost)</a>')
    flag = f'<span class="fl">{html.escape(sh["flag"])}</span>' if sh.get("flag") else ""
    desc = f'<p class="muted" style="font-size:.92rem">{sh.get("desc","")}</p>' if sh.get("desc") else ""
    return f"""<div class="card" id="v{sh["num"]}"><span class="num">#{sh["num"]}</span><b>{html.escape(sh.get("title",""))}</b>{flag}
{desc}{vid}{btns}<div class="meta">{" · ".join(meta) if meta else ""}</div>
<div class="marks" data-shot="{sh["key"]}" data-num="{sh["num"]}"><button class="mbtn" data-m="keep">keep</button><button class="mbtn" data-m="change">change</button><button class="mbtn" data-m="no">no</button></div>
<textarea class="fb" data-shot="{sh["key"]}" placeholder="feedback for #{sh["num"]}…"></textarea></div>"""


CARDS = {  # artifact -> (card_key, scenario caption, note)
 "SM_RV_18":("c1","long jumper lacing at the board",""), "SM_RV_23":("c2","water polo shot",""),
 "SM_RV_8":("c3","clubs crossed overhead",""), "SM_RV_19":("c4","wrestler on the mat, 1980",""),
 "SM_RV_9":("c5","archer at full draw",""), "SM_RV_17":("c6","fencer en garde (with the epee)",""),
 "SM_RV_13":("c6","fencer en garde (with the mask)",""), "SM_RV_7":("c7","gymnast framed in the hoop",""),
 "SM_RV_11":("c8","balance pose",""), "SM_RV_22":("c9","hands tying the belt",""),
 "SM_RV_10":("c10","open-water start",""), "SM_RV_20":("c11","glove open for the catch",""),
 "SM_RV_21":("c11","glove open for the catch",""), "SM_RV_15":("c12","low over the table",""),
 "SM_RV_1":("m1","the 1870 medal in hand","NOTE: shown as a LEGACY image (marble stadium, today) - the researched 1870 period card (pre-marble stadium, male athlete type) is being regenerated; both will stand."),
 "SM_RV_2":("m2","Greco-Roman wrestler, Moscow 1980 (neutral backdrop)",""),
 "SM_RV_3":("m3","athlete in the marble Panathenaic, 1906",""),
 "SM_RV_4":("m4","weightlifter at the platform, Sydney 2000",""),
 "SM_RV_5":("m5","taekwondo athlete, Beijing 2008",""),
 "SM_RV_6":("m6","athlete at the first modern Games, 1896",""),
}
def card_section(code):
    if code not in CARDS: return ""
    k, cap, note = CARDS[code]
    n = f'<p style="font-size:.85rem;color:var(--flame);max-width:80ch">{note}</p>' if note else ""
    return f"""<p class="k">The proof — same prompt, with and without the collection</p>
<p class="muted" style="font-size:.92rem">{cap} · the only difference between the two images is the museum digitisation attached as reference.</p>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px;max-width:920px">
<div><a href="board/media/cards/{k}_without.jpg" target="_blank"><img class="thumb" style="max-height:200px;width:100%;object-fit:cover" src="board/media/cards/{k}_without.jpg" alt="without the collection"></a><p style="font-size:.85rem;color:var(--steel)"><b style="color:var(--flame)">WITHOUT:</b> the AI invents a generic object.</p></div>
<div><a href="board/media/cards/{k}_with.jpg" target="_blank"><img class="thumb" style="max-height:200px;width:100%;object-fit:cover" src="board/media/cards/{k}_with.jpg" alt="with the collection"></a><p style="font-size:.85rem;color:var(--steel)"><b style="color:var(--good)">WITH:</b> the real object survives, invariants gated.</p></div>
</div>{n}
"""

def build():
    man = load_manifest()
    cards = list(all_cards(man))
    os.makedirs(f"{ROOT}", exist_ok=True)
    by_unit = {u: [] for u in UNITS}
    by_art = {}
    for sec, sh in cards:
        u = unit_of(sec, sh)
        if u in by_unit: by_unit[u].append((sec, sh))
        for a in arts_of(sec, sh): by_art.setdefault(a, []).append((sec, sh))

    # unit pages
    for u, d in UNITS.items():
        rows = sorted(by_unit[u], key=lambda t: t[1]["num"])
        vids = "".join(render_card(sec, sh) for sec, sh in rows)
        arts = " · ".join(f'<a href="artifact-{a}.html" style="color:var(--bronze)">{html.escape(REG.get(a,{}).get("name",a))}</a>' for a in d["artifacts"]) or "no physical artefacts in this unit"
        page = head(f"Unit {u} — {d['title']}") + f"""
<p class="k">Unit {u} of 5 · the Museum's structure</p><h1>{html.escape(d['title'])}</h1>
<p class="muted">(our working name: “{html.escape(d['ours'])}”)</p>
<div class="musdoc"><span class="mtag">Museum</span><i>Unit title above is the Museum's own. Visuals the Museum's document asks for: {html.escape(d['museum_visuals'])}.</i></div>
<p class="k">What we decided to try</p><p>{html.escape(d['story'])}</p>
<p class="k">The artefacts of this unit</p><p>{arts}</p>
<p class="k">Every video · numbered · mark and comment freely</p>
<p class="muted" style="font-size:.9rem">Everything is shown — finals, tests and documented failures alike. Prompt and ledger (model, measurements, cost) are one click on each card. Quote a number and everyone knows which video you mean.</p>
<div class="cardgrid">{vids}</div>{"" if vids else '<p class="muted">Nothing produced for this unit yet — honestly stated.</p>'}
""" + BAR + FOOT
        open(f"{ROOT}/unit-{u}.html","w").write(page)

    # units index
    tiles = "".join(f'<a class="tile" href="unit-{u}.html"><b>Unit {u} — {html.escape(d["title"])}</b><span>{len(by_unit[u])} videos · {html.escape(d["ours"])}</span></a>' for u,d in UNITS.items())
    open(f"{ROOT}/units.html","w").write(head("The Five Units") + f"""
<h1>The five units</h1><p class="muted">The Museum's own structure. Each page: what the Museum wrote, what we decided to try, the research, and every video — numbered, with prompts and measurements.</p>
<div class="grid">{tiles}</div>""" + FOOT)

    # artifact pages + index
    art_tiles = ""
    for code, rows in sorted(by_art.items()):
        r = REG.get(code, {})
        rows = sorted({sh["num"]:(sec,sh) for sec,sh in rows}.values(), key=lambda t:t[1]["num"])
        vids = "".join(render_card(sec, sh) for sec, sh in rows)
        hero = ""
        for _sec,_sh in rows:
            _vs=_sh.get("versions") or []
            if _vs:
                _po = poster_for(_vs[0]["src"])
                if _po: hero = f'<img class="thumb" src="{_po}" alt="" style="max-width:300px;margin:6px 0 10px">'; break
        inv = html.escape(str(r.get("invariants",""))[:600])
        na = html.escape(str(r.get("not_asserted",""))[:400])
        page = head(f"{r.get('name',code)}") + f"""
<p class="k">Artifact · {code}</p><h1>{html.escape(r.get('name',code))}</h1>
{hero}
<p>{html.escape(str(r.get('claim',''))[:500])}</p>
<div class="musdoc"><b>What a generated image must hold:</b> <span class="muted">{inv}</span></div>
{f'<div class="musdoc" style="border-color:rgba(186,90,30,.4)"><b>Not asserted:</b> <span class="muted">{na}</span></div>' if na else ''}
{card_section(code)}
<p class="k">Every video this artifact appears in</p>
<div class="cardgrid">{vids}</div>""" + BAR + FOOT
        open(f"{ROOT}/artifact-{code}.html","w").write(page)
        art_tiles += f'<a class="tile" href="artifact-{code}.html"><b>{html.escape(r.get("name",code))}</b><span>{code} · {len(rows)} videos</span></a>'
    open(f"{ROOT}/artifacts.html","w").write(head("The Artifacts") + f"""
<h1>The artifacts</h1><p class="muted">One page per museum object we have used: the registry card (what it is, what a generated frame must hold, what is never asserted) and every video it appears in.</p>
<div class="grid">{art_tiles}</div>""" + FOOT)

    # selection page — FFP FINALS (Philipp 13:10: he cuts the finals himself in Premiere; slots stay empty until he delivers)
    slots = ""
    for u, d in UNITS.items():
        fn = f"ffp-final/ffp_final_unit_{u}.mp4"
        exists = os.path.exists(f"{ROOT}/{fn}")
        body = (f'<video controls preload="metadata" src="{fn}" style="width:100%;max-width:820px;border-radius:10px;border:1px solid var(--hair);background:#000"></video>'
                if exists else '<p class="muted" style="font-style:italic">Awaiting the FFP final cut — edited by FFP in Premiere Pro from the unit material. This slot fills when the cut is delivered.</p>')
        slots += f'<div class="card"><b>FFP FINAL — Unit {u} · {html.escape(d["title"])}</b>{body}</div>'
    open(f"{ROOT}/selection.html","w").write(head("FFP Finals") + f"""
<h1>FFP finals</h1>
<p class="muted">One final film per unit, cut by FFP in Premiere Pro from the material on the unit pages. These are the versions of record for presentation; everything they were cut from stays visible on the unit pages and in the working room.</p>
{slots}""" + FOOT)

    print(f"built: 5 unit pages ({sum(len(v) for v in by_unit.values())} unit-mapped cards), {len(by_art)} artifact pages, units/artifacts/selection indexes")

if __name__ == "__main__":
    build()
