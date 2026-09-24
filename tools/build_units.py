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
    """EXACT board rule: pref = V if src starts with media/v/ else R; rel = src minus V/R prefix; posters/md5(pref+rel)[:10].jpg."""
    if src.startswith("media/v/"): pref, rel = "V", src[len("media/v/"):]
    elif src.startswith("media/r/"): pref, rel = "R", src[len("media/r/"):]
    else: pref, rel = "R", src
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
            "v22-run3":1,"wreath-a":1,"part2-armA":1,"part2-armB":1,"cov30":1,"night-cut":1,"campaign-v3":1,
            "hands-e1":4,"hands-e4":4,"hands-e6":4,"hands-e2":4,"hands-e3":4,"hands-e5":4,"hands-e7":4,"hands-e8":4,"hands-e9":4,"hands-e10":4,"hands-e11":1}
def unit_of(sec, sh):
    k = sh["key"]
    if k in KEY2UNIT: return KEY2UNIT[k]
    if k.startswith("sm_rv_16") or k.startswith("1a_v"): return 1
    if k.startswith("sm_rv_6"): return 2
    if k.startswith("sm_rv_3"): return 3
    return SEC2UNIT.get(sec["id"])

KEY2ART = {"a1":["SM_RV_16"],"s6":["SM_RV_16"],"t-with":["SM_RV_16"],"t-without":["SM_RV_16"],"t-real":["SM_RV_16"],"t-kot":["SM_RV_16"],
           "ab-long":["SM_RV_16"],"ab-short":["SM_RV_16"],"night-cut":["SM_RV_16","SM_RV_6","SM_RV_3"],"wreath-a":["SM_RV_16"],"campaign-v3":["SM_RV_16","SM_RV_18","SM_RV_22","SM_RV_8"],
           "a2":["SM_RV_1"],"s3":["SM_RV_1"],"a3":["SM_RV_6"],"fail-1896-s3":["SM_RV_6"],
           "a4":["SM_RV_12"],"s2":["SM_RV_12"],"t-torch":["SM_RV_12"],
           "a5":["SM_RV_14"],"s4":["SM_RV_14"],"b7":["SM_RV_8"],"b2":["SM_RV_18"],"s1b":["SM_RV_18"],"t-shoes-real":["SM_RV_18"],
           "b4":["SM_RV_13"],"s5":["SM_RV_13"],
           "hands-e1":["SM_RV_18"],"hands-e4":["SM_RV_23"],"hands-e6":["SM_RV_15"],"hands-e2":["SM_RV_22"],"hands-e3":["SM_RV_8","SM_RV_7","SM_RV_11"],"hands-e5":["SM_RV_13","SM_RV_17"],"hands-e7":["SM_RV_10"],"hands-e8":["SM_RV_19"],"hands-e9":["SM_RV_20","SM_RV_21"],"hands-e10":["SM_RV_9"],"hands-e11":["SM_RV_16"]}
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
NAV = """<div id="olynav" style="position:sticky;top:0;z-index:999;display:flex;gap:6px;flex-wrap:wrap;align-items:center;background:#ffffff;padding:8px 14px;border-bottom:1px solid #e3e3e3">
<a href="pilot-1.html" style="text-decoration:none;font:600 12px Archivo,system-ui;padding:5px 10px;border-radius:7px;background:#3d3350;color:#efe6ff">👗 Pilot 1</a>
<a href="index.html" style="text-decoration:none;font:600 12px Archivo,system-ui;padding:5px 10px;border-radius:7px;background:#54682f;color:#fff">⌂ Home</a>
<a href="olympic.html" style="text-decoration:none;font:600 12px Archivo,system-ui;padding:5px 10px;border-radius:7px;background:#f2c230;color:#1f1f1f">🏅 Olympic</a>
<a href="empirica.html" style="text-decoration:none;font:600 12px Archivo,system-ui;padding:5px 10px;border-radius:7px;background:#6F6AAF;color:#fff">◎ Empirica</a>
<a href="casestudy.html" style="text-decoration:none;font:600 12px Archivo,system-ui;padding:5px 10px;border-radius:7px;background:#2FB89F;color:#fff">🔬 Method</a>
<a href="units.html" style="text-decoration:none;font:600 12px Archivo,system-ui;padding:5px 10px;border-radius:7px;color:#3a3a3a">🏛 Units</a>
<a href="artifacts.html" style="text-decoration:none;font:600 12px Archivo,system-ui;padding:5px 10px;border-radius:7px;color:#3a3a3a">🏺 Artifacts</a>
<a href="selection.html" style="text-decoration:none;font:600 12px Archivo,system-ui;padding:5px 10px;border-radius:7px;color:#3a3a3a">★ Final Selection</a>
<a href="initial-tests.html" style="text-decoration:none;font:600 12px Archivo,system-ui;padding:5px 10px;border-radius:7px;color:#3a3a3a">🧪 Initial tests</a>
<a href="board/review.html" style="text-decoration:none;font:600 12px Archivo,system-ui;padding:5px 10px;border-radius:7px;color:#3a3a3a">🗄 Working room</a>
<span style="margin-left:auto;display:flex;align-items:center;gap:10px"><span style="font:600 10px 'IBM Plex Mono',monospace;letter-spacing:.1em;color:#7a7a7a">OLYMPIA · REEVALUATE</span><img src="board/media/brand/reevaluate-logo.png" alt="REEVALUATE" style="height:38px;width:auto"></span></div><style>body{position:relative}.wrap{position:relative;z-index:1}body::before{content:"";position:fixed;left:0;top:52px;width:min(20vw,250px);height:calc(100vh - 52px);background:url(board/media/brand/circuit-left.png) no-repeat left top/contain;pointer-events:none;z-index:0}body::after{content:"";position:fixed;right:0;bottom:0;width:min(17vw,210px);height:100vh;background:url(board/media/brand/circuit-right.png) no-repeat left top/contain;transform:rotate(180deg);pointer-events:none;z-index:0}@media (max-width:1180px){body::before,body::after{display:none}}</style>"""

STYLE = """<style>
:root{--bg:#ffffff;--surface:#f7f7f7;--surface-2:#efefef;--ink:#1f1f1f;--steel:#474747;--muted:#6f6f6f;--hair:#dedede;--olive:#54682f;--bronze:#a06a24;--good:#3f7a4c;--flame:#ba5a1e}


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
.card .muted{font-size:.84rem;max-height:5.2em;overflow:hidden;cursor:pointer;position:relative}
.card .muted:not(.open)::after{content:'… more ▾';position:absolute;right:0;bottom:0;background:var(--surface);padding-left:8px;color:var(--bronze);font-weight:600}
.card .muted.open{max-height:none}
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
#lb{position:fixed;inset:0;background:rgba(10,12,8,.92);display:none;align-items:center;justify-content:center;z-index:1000;cursor:zoom-out}
#lb.on{display:flex}
#lb img{max-width:94vw;max-height:92vh;border-radius:10px}
#lb .x{position:fixed;top:14px;right:18px;font:700 26px Archivo;color:#fff;background:rgba(0,0,0,.5);border:1px solid #666;border-radius:10px;padding:2px 14px;cursor:pointer}
.foot{margin-top:60px;padding-top:14px;border-top:1px solid var(--hair);font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--muted)}
</style>"""

JS = """<script>
var MKEY='olympia-marks-v1', FKEY='olympia-review-v1';
function mload(){try{return JSON.parse(localStorage.getItem(MKEY)||'{}')}catch(e){return{}}}
function msave(d){try{localStorage.setItem(MKEY,JSON.stringify(d))}catch(e){}}
function floadd(){try{return JSON.parse(localStorage.getItem(FKEY)||'{}')}catch(e){return{}}}
document.addEventListener('click',function(e){
  var L=e.target.closest&&e.target.closest('a.lb');
  if(L){e.preventDefault();var lb=document.getElementById('lb');lb.querySelector('img').src=L.getAttribute('href');lb.classList.add('on');return;}
  if(e.target.closest&&e.target.closest('#lb')){document.getElementById('lb').classList.remove('on');return;}
  var d=e.target.closest&&e.target.closest('.card .muted');
  if(d&&!e.target.closest('a')){d.classList.toggle('open');return;}
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
  document.querySelectorAll('.card .muted').forEach(function(d){if(d.scrollHeight<=d.clientHeight+4)d.classList.add('open');});
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
document.addEventListener('keydown',function(e){if(e.key==='Escape'){var lb=document.getElementById('lb');if(lb)lb.classList.remove('on');}});
function jumpN(){var n=document.getElementById('jn').value.replace('#','');var el=document.getElementById('v'+n);
  if(el){el.scrollIntoView({behavior:'smooth'});el.style.outline='3px solid var(--bronze)';setTimeout(function(){el.style.outline=''},2500)}else{alert('#'+n+' is not on this page — try the Working room (full archive).')}}
</script>"""

BAR = """<div class="bar"><span class="jump"><input id="jn" placeholder="#nr"><button onclick="jumpN()">Jump</button></span><button id="cpy" onclick="copyAll()">Copy my marks</button></div>"""

def head(title):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow">
<title>{html.escape(title)}</title><meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500&family=Archivo:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
</head><body>{NAV}{STYLE}<div class="wrap">"""

FOOT = """<div id="lb"><span class="x">✕ close</span><img src="" alt=""></div><p class="foot">REEVALUATE · every claim traceable to a ledger · full archive in the <a href="board/review.html" style="color:var(--bronze)">working room</a></p></div>""" + JS + "</body></html>"

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
 "SM_RV_18":("c1","long jumper lacing at the board",""), "SM_RV_23":("c2","water polo shot","NOTE: closed under the restored standard (owner ruling, 2026-09-11): the ball's real printing is PRESENT but unreadable at viewing scale - the brief's own below-resolvability rule, which an interim stricter rule had overridden. The earlier attempt that INVENTED a near-brand wordmark remains the hard fail the text rule exists to prevent: accuracy and legibility are separate axes."),
 "SM_RV_8":("c3","clubs crossed overhead",""), "SM_RV_19":("c4","wrestler on the mat, 1980",""),
 "SM_RV_9":("c5","archer at full draw",""), "SM_RV_17":("c6","fencer en garde (with the epee)",""),
 "SM_RV_13":("c6","fencer en garde (with the mask)",""), "SM_RV_7":("c7","gymnast framed in the hoop",""),
 "SM_RV_11":("c8","balance pose",""), "SM_RV_22":("c9","hands tying the belt",""),
 "SM_RV_10":("c10","open-water start",""), "SM_RV_20":("c11","glove open for the catch",""),
 "SM_RV_21":("c11","glove open for the catch",""), "SM_RV_15":("c12","low over the table",""),
 "SM_RV_1":("m1","the 1870 medal in hand","NOTE: the period question stands (this stages the marble stadium of today, not the 1870 pre-marble ground) but the pair itself is now locked - only the medal differs between the arms."),
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
<p class="muted" style="font-size:.92rem">{cap} · pair-locked: the WITH arm is an edit of the WITHOUT arm, so the ONLY difference between the two images is the object itself - same person, same pose, same light.</p>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px;max-width:920px">
<div><a class="lb" href="board/media/cards/{k}_without.jpg"><img class="thumb" style="aspect-ratio:16/9;width:100%;object-fit:cover" src="board/media/cards/{k}_without.jpg" alt="without the collection"></a><p style="font-size:.85rem;color:var(--steel)"><b style="color:var(--flame)">WITHOUT:</b> the AI invents a generic object.</p></div>
<div><a class="lb" href="board/media/cards/{k}_with.jpg"><img class="thumb" style="aspect-ratio:16/9;width:100%;object-fit:cover" src="board/media/cards/{k}_with.jpg" alt="with the collection"></a><p style="font-size:.85rem;color:var(--steel)"><b style="color:var(--good)">WITH:</b> the real object survives, invariants gated.</p></div>
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
        chips = " ".join(f'<a href="unit-{x}.html" style="text-decoration:none;font:600 12px Archivo,system-ui;padding:4px 10px;border-radius:7px;{"background:#54682f;color:#fff" if x==u else "color:var(--bronze);border:1px solid var(--hair)"}">Unit {x}</a>' for x in UNITS)
        prev_u, next_u = (u-1 if u>1 else 5), (u+1 if u<5 else 1)
        subnav = f'<div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin:10px 0 18px"><a href="units.html" style="text-decoration:none;font:600 12px Archivo,system-ui;padding:4px 10px;border-radius:7px;color:var(--steel);border:1px solid var(--hair)">← All units</a> {chips} <a href="unit-{prev_u}.html" style="text-decoration:none;font:600 12px Archivo,system-ui;padding:4px 10px;border-radius:7px;color:var(--steel);border:1px solid var(--hair)">‹ previous</a><a href="unit-{next_u}.html" style="text-decoration:none;font:600 12px Archivo,system-ui;padding:4px 10px;border-radius:7px;color:var(--steel);border:1px solid var(--hair)">next ›</a></div>'
        page = head(f"Unit {u} — {d['title']}") + subnav + f"""
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
    all_codes = sorted(set(by_art) | set(CARDS))
    for code in all_codes:
        rows = by_art.get(code, [])
        r = REG.get(code, {})
        rows = sorted({sh["num"]:(sec,sh) for sec,sh in rows}.values(), key=lambda t:t[1]["num"]) if rows else []
        vids = "".join(render_card(sec, sh) for sec, sh in rows)
        render_rel = f"board/media/renders/{code}.jpg"
        if os.path.exists(f"{ROOT}/{render_rel}"):
            hero = (f'<a class="lb" href="{render_rel}"><img class="thumb" src="{render_rel}" alt="the digitised object" style="max-width:320px;margin:6px 0 2px"></a>'
                    f'<p class="muted" style="font-size:.8rem;margin:2px 0 10px">The Museum&rsquo;s digitisation &middot; the reference every generated frame is measured against.</p>')
        else:
            hero = ""
            for _sec,_sh in rows:
                _vs=_sh.get("versions") or []
                if _vs:
                    _po = poster_for(_vs[0]["src"])
                    if _po: hero = f'<img class="thumb" src="{_po}" alt="" style="max-width:300px;margin:6px 0 10px">'; break
        must = str(r.get("identity") or r.get("invariants") or "")
        holds = r.get("hold_invariants") or []
        if holds: must += " Checked every frame: " + " · ".join(holds) + "."
        inv = html.escape(must)
        na = html.escape(str(r.get("not_asserted","")))
        insc = r.get("inscriptions") or {}
        insc_html = ""
        if insc:
            lis = "".join(f'<li><b>{html.escape(str(k))}:</b> {html.escape(str(v))}</li>' for k,v in insc.items())
            insc_html = ('<div class="musdoc" style="border-color:rgba(140,125,60,.45)"><b>Real text on the object:</b> '
                         '<span class="muted">recorded here, never re-rendered by the model - generated frames keep these surfaces below reading size.</span>'
                         f'<ul style="margin:6px 0 0;padding-left:18px;font-size:.88rem;color:var(--steel)">{lis}</ul></div>')
        _i = all_codes.index(code)
        _prev, _next = all_codes[_i-1], all_codes[(_i+1) % len(all_codes)]
        asub = f'<div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin:10px 0 18px"><a href="artifacts.html" style="text-decoration:none;font:600 12px Archivo,system-ui;padding:4px 10px;border-radius:7px;color:var(--steel);border:1px solid var(--hair)">← All artifacts</a><a href="artifact-{_prev}.html" style="text-decoration:none;font:600 12px Archivo,system-ui;padding:4px 10px;border-radius:7px;color:var(--steel);border:1px solid var(--hair)">‹ {html.escape(REG.get(_prev,{}).get("name",_prev)[:22])}</a><a href="artifact-{_next}.html" style="text-decoration:none;font:600 12px Archivo,system-ui;padding:4px 10px;border-radius:7px;color:var(--steel);border:1px solid var(--hair)">{html.escape(REG.get(_next,{}).get("name",_next)[:22])} ›</a></div>'
        page = head(f"{r.get('name',code)}") + asub + f"""
<p class="k">Artifact · {code}</p><h1>{html.escape(r.get('name',code))}</h1>
{hero}
<p class="k">What it is</p>
<p>{html.escape(str(r.get('claim','')))}</p>
<div class="musdoc"><b>What a generated frame must hold:</b> <span class="muted">{inv}</span></div>
{insc_html}
{f'<div class="musdoc" style="border-color:rgba(186,90,30,.4)"><b>Never asserted:</b> <span class="muted">{na}</span></div>' if na else ''}
{card_section(code)}
<p class="k">Every video this artifact appears in</p>
{f'<div class="cardgrid">{vids}</div>' if vids else '<p class="muted">No videos of this object yet — the proof card above is its first appearance.</p>'}""" + BAR + FOOT
        open(f"{ROOT}/artifact-{code}.html","w").write(page)
        timg = (f'<img src="{render_rel}" alt="" loading="lazy" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:8px;margin-bottom:8px">'
                if os.path.exists(f"{ROOT}/{render_rel}") else "")
        art_tiles += f'<a class="tile" href="artifact-{code}.html">{timg}<b>{html.escape(r.get("name",code))}</b><span>{code} · {len(rows)} videos</span></a>'
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
    hands_eps = [("E01","The long jumper"),("E02","The weightlifter, 1976"),("E03","The ensemble"),("E04","The water polo player"),("E05","The fencer"),("E06","The table tennis player"),("E07","The marathon swimmer"),("E08","The wrestler, 1980"),("E09","The softballer"),("E10","The archer"),("E11","The judoka — finale")]
    hands_grid = "".join(f'<div><video controls preload="metadata" src="board/media/v/hands/{c}.mp4" style="width:100%;border-radius:8px;border:1px solid var(--hair);background:#000"></video><p style="font-size:.85rem;color:var(--steel);margin-top:4px"><b>{c}</b> · {n}</p></div>' for c,n in hands_eps)
    hands_html = f"""
<p class="k">THE HANDS REMEMBER — the finished series</p>
<h2>Eleven athletes, eleven objects, one ritual each</h2>
<p class="muted">One ~30-second film per athlete type and museum object, produced serially with a review round after every episode. The assembled cut below plays all eleven in order — from the silent stadium to the crowded hall (EDIT · 11 sources, hard cuts; a woven version with generated transitions is planned). Every episode's prompt, measurements and verdicts are on its numbered card in the working room (#104–#114).</p>
<video controls preload="metadata" src="board/media/v/hands/CUT_A_series.mp4" style="width:100%;max-width:880px;border-radius:12px;border:1px solid var(--hair);background:#000;display:block;margin-bottom:14px"></video>
<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px;max-width:1200px">{hands_grid}</div>
"""
    open(f"{ROOT}/selection.html","w").write(head("FFP Finals") + f"""
<h1>FFP finals</h1>
{hands_html}
<p class="k" style="margin-top:26px">The unit finals</p>
<p class="muted">One final film per unit, cut by FFP in Premiere Pro from the material on the unit pages. These are the versions of record for presentation; everything they were cut from stays visible on the unit pages and in the working room.</p>
{slots}""" + FOOT)


    OLY_STYLE = r"""<style>
/* Olympic page: deck typography option - Aptos Display / Arial, purple + teal from the logo, full-width text */
.wrap{max-width:none;margin:0;padding-left:max(24px,min(21vw,265px));padding-right:max(24px,min(18vw,225px))}
@media (max-width:1180px){.wrap{padding-left:clamp(14px,3vw,32px);padding-right:clamp(14px,3vw,32px)}}
p{max-width:none}
body{font-family:Arial,"Helvetica Neue",Helvetica,sans-serif;font-size:19px;line-height:1.6;color:#2b2b2b}
h1{font-family:"Aptos Display",Aptos,"Helvetica Neue",Arial,sans-serif;font-weight:700;font-size:clamp(2.4rem,4.6vw,3.6rem);color:#6F6AAF;letter-spacing:-.01em}
h2{font-family:"Aptos Display",Aptos,"Helvetica Neue",Arial,sans-serif;font-weight:700;font-size:clamp(1.5rem,2.4vw,2rem);color:#6F6AAF;margin-top:44px}
.k{font-family:Arial,sans-serif;font-size:13px;letter-spacing:.2em;color:#2FB89F;font-weight:700}
.muted{color:#4a4a4a}
.tile{border-left:5px solid #2FB89F;border-radius:10px;padding:16px 18px}
.tile b{color:#6F6AAF;font-size:1.05rem}.tile span{font-size:.95rem;color:#4a4a4a}
.grid{grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:14px}
.musdoc{background:rgba(111,106,175,.07);border:1px solid rgba(111,106,175,.35);color:#6F6AAF;font-size:1rem}
a{color:#2FB89F}
</style>"""
    oly = """
<p class="k">PILOT 2 · FROM MUSEUMS TO SCREENS</p>
<h1>&ldquo;Olympic Games &amp; Music&rdquo;</h1>
<p class="muted" style="font-size:1.15rem;margin-bottom:6px">Leveraging digitised cultural-heritage artefacts for creative and sustainable advertising.</p>
<p style="margin-top:0"><span class="k" style="margin:0 10px 0 0">Partners</span><b>Olympic Museum of Thessaloniki</b> &middot; <b>SPK / Ethnological Museum of Berlin</b> &middot; <b>FFP Productions</b></p>

<h2>What is Pilot 2?</h2>
<p>Pilot 2 of REEVALUATE is a collaborative initiative between the Olympic Museum of Thessaloniki, the Ethnological Museum of Berlin and FFP Productions of Austria, combining cultural-heritage expertise with digital tools and creative production. The pilot focuses on the relationship between the Olympic Games, sports and music, bringing together historical artefacts, photographs, documents, sports objects and audio material, while exploring how Olympic and musical heritage can be digitised, enriched and creatively reused.</p>

<h2>How can digitised museum collections become new creative experiences?</h2>
<p class="muted">The pilot combines:</p>
<div class="grid" style="margin:10px 0 6px">
<div class="tile"><b>Olympic heritage</b><span>Historical artefacts</span></div>
<div class="tile"><b>Music and sound archives</b><span>Audio material from the collections</span></div>
<div class="tile"><b>Digital content</b><span>3D scanning and digitisation</span></div>
<div class="tile"><b>Expert contextualisation</b><span>Curators and historians</span></div>
<div class="tile"><b>Public participation</b><span>Campaigns that guided the selection</span></div>
<div class="tile"><b>Creative storytelling</b><span>Historical research and content development</span></div>
</div>
<p class="muted"><b>From preserving the past &rarr; to experiencing it today.</b></p>

<h2>Providing the content, expertise and museum setting</h2>
<p>The Thessaloniki Olympic Museum selected material from its collection that reflects the history, evolution and values of the Olympic Movement. Museum curators and historians contribute their expertise by providing historical context, developing the narrative and enriching the information connected to each asset.</p>
<p>At the same time, the public was actively involved through dedicated campaigns designed to identify which artefacts attracted the greatest interest. This feedback helped guide the selection of objects for 3D digitisation and for their inclusion as key elements of the final creative production and its storytelling. The selected material is then organised and made accessible through the REEVALUATE platforms, supporting its further use in creative and media production.</p>
<p class="muted">The objects themselves, with what each film must hold and what is never asserted about them, are on the <a href="artifacts.html" style="color:var(--bronze)">Artifacts</a> page.</p>

<h2>One film. Five chapters. One Olympic journey.</h2>
<p>The film follows five thematic units, developed by the Olympic Museum of Thessaloniki together with the Ethnological Museum of Berlin (SPK), providing a rich curatorial narrative spanning antiquity to the present day in one continuous narrative.</p>
<div class="grid" style="margin:10px 0 6px">
<a class="tile" href="unit-1.html"><b>1 &middot; From Discovery to Revival</b><span>Olympia lost and found again: the excavations of 1829 and 1875</span></a>
<a class="tile" href="unit-2.html"><b>2 &middot; The First Modern Games</b><span>The Revival and the Olympic symbols</span></a>
<a class="tile" href="unit-3.html"><b>3 &middot; The Mesolympic Games</b><span>Athens 1906</span></a>
<a class="tile" href="unit-4.html"><b>4 &middot; Olympic Values through Sports &amp; Music</b><span>The Hands Remember: eleven athletes, eleven objects</span></a>
<a class="tile" href="unit-5.html"><b>5 &middot; International Olympic Day</b><span>A global movement</span></a>
</div>

<h2>The outcome</h2>
<p>The final outcome brings Olympic heritage and music together, transforming selected museum material into a contemporary audiovisual experience. Presented within the &ldquo;Olympic Experience&rdquo; immersive exhibition at the Thessaloniki Olympic Museum, the film combines digitised artefacts, historical material, music and sound to bring the Olympic story to life and become a bridge between the Museum&rsquo;s collections and its visitors.</p>
<p>The result is an experience that connects past and present, brings Olympic heritage closer to new generations, and strengthens the Museum&rsquo;s educational and experiential role.</p>
<div class="musdoc" style="font-family:'IBM Plex Mono',monospace;font-size:.9rem;text-align:center">Heritage &rarr; Context &rarr; Public Input &rarr; Digitisation &rarr; Creative Reuse &rarr; Film / Museum Experience</div>
<p class="muted">In our production pipeline we use a guidance system for AI called <a href="empirica.html"><b>Empirica</b></a>. The finished films are on the <a href="selection.html">Final Selection</a> page; how they were made and verified is under <a href="casestudy.html">Method</a>.</p>
"""
    open(f"{ROOT}/olympic.html","w").write(head("Olympic Games & Music") + OLY_STYLE + oly + FOOT)

    EMP_STYLE = r"""<style>
.pipe,.loop{display:flex;align-items:stretch;gap:10px;flex-wrap:wrap;margin:16px 0 8px}
.node,.step{flex:1 1 170px;background:#f7f7f7;border:1px solid #dedede;border-top:5px solid #2FB89F;border-radius:10px;padding:14px 16px;min-width:160px}
.node b,.step b{display:block;color:#6F6AAF;font-size:1.05rem;margin-bottom:4px}
.node span,.step span{font-size:.92rem;color:#4a4a4a;line-height:1.45}
.node.hi{border-top-color:#6F6AAF;background:rgba(111,106,175,.06)}
.node.human{border-top-color:#f2c230}
.arrow{align-self:center;color:#2FB89F;font-size:1.6rem;font-weight:700;padding:0 2px}
.tile b{font-size:1.5rem;display:block}
@media (max-width:900px){.arrow{display:none}}
</style>"""

    emp = """
<p class="k">THE SYSTEM BEHIND THE PRODUCTION</p>
<h1>Empirica &amp; Empirica Cortex &mdash; how it works</h1>
<p class="muted" style="font-size:1.05rem;margin-top:-4px">In plain terms: what it is, and what you get out of it.</p>
<p style="font-size:1.2rem;max-width:68ch">Think of it as <b>three things working together</b> &mdash; a careful way of working, a shared memory for the whole company, and the assistant you actually talk to. Most tools give you one of the three. This gives you all three, joined up &mdash; so what one person learns, the next person can use.</p>

<h2>The three parts</h2>
<div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;margin:10px 0">
<div class="card3" style="border-top-color:#2FB89F"><span class="role">The way of working</span><h3>Empirica</h3><p>A careful method. The assistant is honest about what it actually knows.</p><ul>
<li>It tells you when it <b>checked</b> something versus when it&rsquo;s only <b>assuming</b>.</li><li>It won&rsquo;t call a job &ldquo;done&rdquo; unless it really is.</li><li>If it&rsquo;s unsure, it says so &mdash; it never quietly fills in a guess.</li><li>That honesty is what lets you trust the answers.</li></ul></div>
<div class="card3" style="border-top-color:#f2c230"><span class="role">The shared memory</span><h3>Cortex</h3><p>Where everything is kept and shared &mdash; not documents you open, a memory the whole company works from.</p><ul>
<li>Keeps decisions, useful facts, open questions and contacts.</li><li>Gives each person their tools the moment they sign in.</li><li>Carries messages and files between people.</li><li>Runs the scheduled jobs &mdash; like the weekly report &mdash; on its own.</li></ul></div>
<div class="card3" style="border-top-color:#6F6AAF"><span class="role">The assistant (any model)</span><h3>Claude</h3><p>The part you talk to &mdash; in chat, on your desktop, wherever you open it.</p><ul>
<li>You steer it by talking, in plain language.</li><li>It reads from and writes to the shared memory for you.</li><li>It forgets each conversation &mdash; which is exactly why the shared memory exists.</li><li>Same you, whichever way you open it.</li></ul></div>
</div>

<h2>How a piece of work flows</h2>
<svg viewBox="0 0 1100 310" role="img" aria-label="Five elements: you start, it checks, a threshold gate, it works, it keeps, then the loop feeds back into the next start." style="max-width:1100px;display:block;margin:6px auto 0">
<defs><marker id="ar" markerWidth="9" markerHeight="9" refX="7" refY="3.2" orient="auto"><path d="M0,0 L7,3.2 L0,6.4 z" fill="#9a9a9a"/></marker></defs>
<g font-family="Arial,Helvetica,sans-serif">
<g><rect x="10" y="66" width="190" height="104" rx="10" fill="#fff" stroke="#2FB89F" stroke-width="2.5"/><text x="28" y="96" fill="#1f8a76" font-size="12" font-weight="700" letter-spacing="1.6">1 · YOU START</text><text x="28" y="124" fill="#1f1f1f" font-size="16">You open a conversation</text><text x="28" y="148" fill="#5a5a5a" font-size="13">your tools are already there</text></g>
<g><rect x="230" y="66" width="190" height="104" rx="10" fill="#fff" stroke="#f2c230" stroke-width="2.5"/><text x="248" y="96" fill="#a8790a" font-size="12" font-weight="700" letter-spacing="1.6">2 · IT CHECKS</text><text x="248" y="124" fill="#1f1f1f" font-size="16">Before acting</text><text x="248" y="148" fill="#5a5a5a" font-size="13">it looks at what&rsquo;s known</text></g>
<g><path d="M515,62 L568,118 L515,174 L462,118 Z" fill="#f3f1fa" stroke="#6F6AAF" stroke-width="3"/><text x="515" y="112" fill="#6F6AAF" font-size="11" font-weight="700" text-anchor="middle" letter-spacing="1.2">THRESHOLD</text><text x="515" y="130" fill="#6F6AAF" font-size="11" font-weight="700" text-anchor="middle" letter-spacing="1.2">GATE</text><text x="515" y="196" fill="#6F6AAF" font-size="12" text-anchor="middle">claims named and grounded,</text><text x="515" y="212" fill="#6F6AAF" font-size="12" text-anchor="middle">or it does not proceed</text></g>
<g><rect x="610" y="66" width="190" height="104" rx="10" fill="#fff" stroke="#6F6AAF" stroke-width="2.5"/><text x="628" y="96" fill="#6F6AAF" font-size="12" font-weight="700" letter-spacing="1.6">3 · IT WORKS</text><text x="628" y="124" fill="#1f1f1f" font-size="16">The actual work</text><text x="628" y="148" fill="#5a5a5a" font-size="13">reports, records, messages</text></g>
<g><rect x="830" y="66" width="190" height="104" rx="10" fill="#fff" stroke="#2FB89F" stroke-width="2.5"/><text x="848" y="96" fill="#1f8a76" font-size="12" font-weight="700" letter-spacing="1.6">4 · IT KEEPS</text><text x="848" y="124" fill="#1f1f1f" font-size="16">What matters</text><text x="848" y="148" fill="#5a5a5a" font-size="13">so next time is better</text></g>
<path d="M206,118 L224,118" stroke="#9a9a9a" stroke-width="1.6" marker-end="url(#ar)"/>
<path d="M426,118 L456,118" stroke="#9a9a9a" stroke-width="1.6" marker-end="url(#ar)"/>
<path d="M574,118 L604,118" stroke="#9a9a9a" stroke-width="1.6" marker-end="url(#ar)"/>
<path d="M806,118 L824,118" stroke="#9a9a9a" stroke-width="1.6" marker-end="url(#ar)"/>
<path d="M925,176 L925,246 Q925,258 913,258 L117,258 Q105,258 105,246 L105,182" fill="none" stroke="#9a9a9a" stroke-width="1.6" stroke-dasharray="4 4" marker-end="url(#ar)"/>
<text x="515" y="290" fill="#5a5a5a" font-size="13" text-anchor="middle">Next conversation, next person, next team &mdash; the same memory answers.</text>
</g></svg>
<div class="pull">The point isn&rsquo;t any single step &mdash; it&rsquo;s the circle. What one person learns or decides, the next person can find.</div>

<h2>What you get, by size</h2>
<div class="scale"><div class="scalehead"><span class="num" style="background:#2FB89F">01</span><h3>One person</h3></div><p class="claim">It stops starting from scratch &mdash; and it stops sounding equally sure about things it checked and things it assumed.</p><table>
<tr><td>Nothing restarts from zero</td><td>Your tools and the way you like to work are there every time you open it. Nothing to install, nothing to paste in.</td></tr>
<tr><td>&ldquo;Done&rdquo; really means done</td><td>For anything with several steps, it works out what &ldquo;finished&rdquo; looks like first &mdash; then checks it against that, so nothing is called done when it isn&rsquo;t.</td></tr>
<tr><td>It&rsquo;s honest when unsure</td><td>If it&rsquo;s guessing, it says so, in writing. It never quietly fills a gap to look more confident than it is.</td></tr>
<tr><td>It fits how you work</td><td>A short first chat sets how independently it acts and when it checks in with you. Changeable any time.</td></tr></table></div>
<div class="scale"><div class="scalehead"><span class="num" style="background:#f2c230;color:#1f1f1f">02</span><h3>A team working together</h3></div><p class="claim">Handing work over that carries itself &mdash; no status meeting, no shared spreadsheet that someone forgets to update.</p><table>
<tr><td>Work lands when its owner accepts it</td><td>You send a to-do list to a colleague; their assistant presents it, and on their &ldquo;yes&rdquo; it becomes their own list of tasks &mdash; and you&rsquo;re told it was accepted.</td></tr>
<tr><td>Progress you can ask for</td><td>&ldquo;Where does the team stand on the list I sent?&rdquo; is answered from the system itself, not from someone remembering to update a status column.</td></tr>
<tr><td>Files travel with the work</td><td>Spreadsheets and images arrive as the original; longer documents arrive as readable text. Nothing is lost quietly along the way.</td></tr>
<tr><td>Honest timing</td><td>A message lands the next time the other person looks &mdash; usually within the hour in work time. It&rsquo;s stated plainly, never over-promised.</td></tr></table></div>
<div class="scale"><div class="scalehead"><span class="num" style="background:#6F6AAF">03</span><h3>The whole company</h3></div><p class="claim">Improve something once and everyone gets it &mdash; and who-sees-what becomes a setting someone owns, not an accident of who was in the room.</p><table>
<tr><td>Improve it once, everyone gets it</td><td>A tool improved centrally reaches every seat at once &mdash; no re-rolling it out person by person.</td></tr>
<tr><td>Ask for a change, and it becomes company-wide</td><td>&ldquo;Change this so that&hellip;&rdquo; is noted, confirmed by a person, and then live for everyone. What one person needs becomes a shared capability.</td></tr>
<tr><td>Who-sees-what is a setting</td><td>Access can be narrowed to teams, controlled by an admin &mdash; not left to chance.</td></tr>
<tr><td>The important jobs don&rsquo;t depend on you</td><td>The weekly report and the daily sync run on the server, with every laptop shut. Company output never waits on whose machine is awake.</td></tr>
<tr><td>One health view for everything</td><td>A single check covers the whole company &mdash; are the scheduled jobs running, is everyone set up &mdash; which no one seat can see on its own.</td></tr></table></div>

<h2>How it sits under this production</h2>
<h2>The pipeline</h2>
<svg viewBox="0 0 1000 330" role="img" aria-label="Pipeline: producer to autonomy to storyboard to imagegen to videogen, acknowledgements returning, Cortex and Empirica as layers beneath" style="max-width:1000px;display:block;margin:6px auto 0">
<defs><marker id="af" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#2b2b2b"/></marker><marker id="ab" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#6F6AAF"/></marker></defs>
<g font-family="Arial,Helvetica,sans-serif">
<g><rect x="15" y="40" width="170" height="74" rx="10" fill="#fff" stroke="#f2c230" stroke-width="3"/><text x="100" y="70" font-size="18" font-weight="700" fill="#a8790a" text-anchor="middle">producer</text><text x="100" y="94" font-size="12.5" fill="#2b2b2b" text-anchor="middle">the brief, the taste, the spend</text></g>
<g><rect x="215" y="40" width="170" height="74" rx="10" fill="#fff" stroke="#2FB89F" stroke-width="3"/><text x="300" y="70" font-size="18" font-weight="700" fill="#1f8a76" text-anchor="middle">autonomy</text><text x="300" y="94" font-size="12.5" fill="#2b2b2b" text-anchor="middle">orchestrates · measures</text></g>
<g><rect x="415" y="40" width="170" height="74" rx="10" fill="#f3f1fa" stroke="#6F6AAF" stroke-width="3"/><text x="500" y="70" font-size="18" font-weight="700" fill="#6F6AAF" text-anchor="middle">storyboard</text><text x="500" y="94" font-size="12.5" fill="#2b2b2b" text-anchor="middle">shot list · claim ledger</text></g>
<g><rect x="615" y="40" width="170" height="74" rx="10" fill="#fff" stroke="#2FB89F" stroke-width="3"/><text x="700" y="70" font-size="18" font-weight="700" fill="#1f8a76" text-anchor="middle">imagegen</text><text x="700" y="94" font-size="12.5" fill="#2b2b2b" text-anchor="middle">sheets · plates · keyframes</text></g>
<g><rect x="815" y="40" width="170" height="74" rx="10" fill="#fff" stroke="#2FB89F" stroke-width="3"/><text x="900" y="70" font-size="18" font-weight="700" fill="#1f8a76" text-anchor="middle">videogen</text><text x="900" y="94" font-size="12.5" fill="#2b2b2b" text-anchor="middle">film · gate ledger</text></g>
<path d="M187,77 L211,77" stroke="#2b2b2b" stroke-width="2.5" marker-end="url(#af)"/>
<path d="M387,77 L411,77" stroke="#2b2b2b" stroke-width="2.5" marker-end="url(#af)"/>
<path d="M587,77 L611,77" stroke="#2b2b2b" stroke-width="2.5" marker-end="url(#af)"/>
<path d="M787,77 L811,77" stroke="#2b2b2b" stroke-width="2.5" marker-end="url(#af)"/>
<path d="M900,116 L900,150 L500,150 L500,118" fill="none" stroke="#6F6AAF" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#ab)"/>
<path d="M700,116 L700,140 L520,140 L520,118" fill="none" stroke="#6F6AAF" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#ab)"/>
<path d="M480,116 L480,160 L300,160 L300,118" fill="none" stroke="#6F6AAF" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#ab)"/>
<path d="M280,116 L280,170 L100,170 L100,118" fill="none" stroke="#6F6AAF" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#ab)"/>
<text x="600" y="188" font-size="12.5" fill="#6F6AAF" text-anchor="middle">acknowledgements, each with a ledger</text>
<rect x="15" y="210" width="970" height="44" rx="8" fill="#6F6AAF" fill-opacity=".12" stroke="#6F6AAF" stroke-width="2"/>
<text x="500" y="238" font-size="15" font-weight="700" fill="#6F6AAF" text-anchor="middle">CORTEX · the shared memory and the messages between the practices</text>
<rect x="15" y="266" width="970" height="44" rx="8" fill="#2FB89F" fill-opacity=".12" stroke="#2FB89F" stroke-width="2"/>
<text x="500" y="294" font-size="15" font-weight="700" fill="#1f8a76" text-anchor="middle">EMPIRICA · the way of working under every seat</text>
</g></svg>
<p class="muted">Nothing downstream is generated without a spec. Nothing is accepted without a verdict.</p>

<h2>The loop every task runs in</h2>
<div class="loop">
<div class="step"><b>PREFLIGHT</b><span>Before acting: what do I know, what am I unsure of, what does this rest on? Thirteen self-assessed vectors, written down.</span></div>
<div class="arrow">&rarr;</div>
<div class="step"><b>investigate</b><span>Read the record, the sources, the previous ledgers. Log what is learned: findings, unknowns, assumptions.</span></div>
<div class="arrow">&rarr;</div>
<div class="step"><b>CHECK</b><span>Name the two or three claims the next action stands on, and how each was grounded: read, ran, retrieved, or merely assumed.</span></div>
<div class="arrow">&rarr;</div>
<div class="step"><b>act</b><span>Write the spec, generate the frame, gate the film. Commit as you go.</span></div>
<div class="arrow">&rarr;</div>
<div class="step"><b>POSTFLIGHT</b><span>Each claim adjudicated: held, refuted, or untested. Mistakes logged with what prevents them. Belief compared to outcome: that is calibration.</span></div>
</div>

<h2>The claim ledger: what a historical frame is allowed to say</h2>
<p>A generated frame of an ancient rite is a claim about the past, and it inherits whatever authority its source has, or none. So every shot carries four lines: <b>what it asserts</b>, <b>on whose authority</b>, <b>how confident</b>, and <b>what the record does not say</b>, which is kept out of frame or deliberately abstracted. Where the record is silent, the ledger says so. Where a source may be unreliable, it says that too.</p>
<div class="musdoc"><b>Worked example, the cutting of the wreath.</b> Claim: branches were cut by a <i>pais amphithales</i>, a boy with both parents living, using golden shears. Sourced: Pausanias, via the Olympia Museum. Not shown: his face, his clothing. The record does not describe them.</div>
<p>The same discipline runs on the object side. Each museum artefact has a registry card: what it is, what a generated frame must hold, and what is never asserted about it. The generating practices bind the real digitisation, never a description of it, and a frame that invents a marking the object does not carry fails the gate even when it looks right.</p>

<h2>Measuring the films: gates and ledgers</h2>
<p>Before a film is generated its thresholds are written: for the MoMu dress, twelve; for the rediscovery of Olympia, ten. On delivery every threshold gets a verdict, PASS, FAIL or PARTIAL, with the evidence. The failures stay on the record beside the successes, because a record that cannot show where it was wrong cannot be trusted where it says it was right.</p>
<div class="grid" style="margin:10px 0">
<div class="tile"><b>37</b><span>gate ledgers on this site, one per delivered film or take</span></div>
<div class="tile"><b>258 held &middot; 4 refuted &middot; 64 untested</b><span>claims adjudicated across this practice's transactions</span></div>
<div class="tile"><b>161 findings &middot; 34 mistakes</b><span>logged in this practice's graph; the mistakes carry a prevention each</span></div>
<div class="tile"><b>11 of 11</b><span>Hands Remember episodes gated PASS after review rounds</span></div>
</div>
<p class="muted">Two examples are on this site on purpose. Under <a href="unit-1.html">Unit 1</a> the failed take that forged an athlete's handwriting is kept beside the version that ships. On <a href="pilot-1.html">Pilot 1</a> the dress film that came back the wrong colour says so on the page, with the cause named.</p>

<h2>Cortex: how the practices talk</h2>
<p>The practitioners are not one program. They are separate AIs, each in its own project, and Cortex is the mesh between them. A practitioner that is uncertain asks a peer directly; a practitioner that needs work done proposes it, and a human accepts or declines before anything runs. Findings and lessons marked as shared cross the practice boundary, so a colour failure measured by videogen becomes doctrine in storyboard's spec the same day. A listener wakes each practice when a peer delivers, so the chain runs without anyone waiting on a message.</p>
<p class="muted">What this buys the museum: a film whose every frame can be asked <i>where does this come from</i>, and answered.</p>
<div class="musdoc" style="margin-top:40px;font-size:1.05rem">In our production pipeline we use a guidance system for AI called <b>Empirica</b>. The finished films are on the <a href="selection.html">Final Selection</a> page; how they were made and verified is under <a href="casestudy.html">Method</a>.</div>
"""
    open(f"{ROOT}/empirica.html","w").write(head("Empirica") + OLY_STYLE + EMP_STYLE + emp + FOOT)

    tests_html = """
<h1>Initial tests</h1>
<p class="muted">Where this started. These are early integration tests, kept unedited as a baseline against which the current work can be read. They predate the claim ledger, so nothing in them is a sourced historical assertion; they were made to answer a narrower question, which is whether digitised museum objects could carry a finished-looking frame at all.</p>

<p class="k">TEST 1 · EXPORTED 28 JUNE 2025 · 1 MIN 34 SEC</p>
<h2>Reevaluate Tests V2 &mdash; FFP Productions</h2>
<p class="muted">Titled on screen as <i>integration examples 16:9 &amp; 9:16 of digitalized elements in Advertising or Social Media</i>. It opens on an <b>Original Elements</b> board showing the source objects side by side: a marble relief of a youth, an olive wreath, a small Herakles statuette photographed on a windowsill, and both faces of a bronze George I medal. The rest of the reel places those elements into finished compositions; the athlete raising a wreath beside a column, the same figure in a ruined colonnade at golden hour, the medal in close-up, and the statuette shot against a window.</p>

<video controls preload="metadata" src="board/media/v/initial-tests/initial-test-01_v12_2025-06-28.mp4" style="width:100%;max-width:960px;border-radius:12px;border:1px solid var(--hair);background:#000;display:block;margin:14px 0"></video>

<div class="musdoc">
<p style="margin:0 0 8px"><b>How to read this against the current work.</b> Several of these objects are still in the registry; the George I medal is <b>SM_RV_1</b>, and it carries a correction of its own on its artifact page. What changed in the fifteen months since is not the rendering. It is that every frame now states what it claims, on whose authority, and what the record does not say. These tests make no such claims, which is the honest reason they sit in their own section rather than beside the finals.</p>
<p style="margin:0"><b>Provenance.</b> Source file <code>export28.6.25_v12_tests reevaluate.mp4</code>, dated 28 June 2025, produced by FFP Productions. Re-encoded for web delivery at 1280&times;720, from 101 MB to 18 MB; the runtime is unchanged at 93.96 seconds and no frame was cut. The original is held outside this repository.</p>
</div>
"""
    open(f"{ROOT}/initial-tests.html","w").write(head("Initial tests") + tests_html + FOOT)

    print(f"built: 5 unit pages ({sum(len(v) for v in by_unit.values())} unit-mapped cards), {len(by_art)} artifact pages, units/artifacts/selection indexes, initial-tests")

if __name__ == "__main__":
    build()
