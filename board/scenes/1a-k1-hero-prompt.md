# 1a · k1 — THE HERO SHOT: "The first drum"

> **v2 (2026-08-22, after Philipp's review of v1):** v1's characters were static (my spec said so) and the drums were chest-high (my spec said so) — both wrong against the 1875/76 photograph, where the drum dwarfs the man, and against the record (20.7 m temple). v2: drums huge and many; both characters REACT to the block. v1 kept on the board as a version.

**The story moment (derived, not invented).** The museum's narrative focus for 1a: *"Olympia had been lost to time… the rediscovery reconnects the modern world with ancient Olympic heritage… In 1875 a German mission begins the excavation… They discover the site of the first Olympic Games. The world looks once again to Greece."* The verified record: first German season, winter–spring 1875/76; a large local workforce; photography from day one; the Temple of Zeus drums lying where the earthquakes of AD 522/551 dropped them, under centuries of Alpheios silt.

So the moment is **the first drum.** Not a treasure, not the Hermes (1877 — not yet). A fluted Doric column drum of the Temple of Zeus, buried since the sixth century, coming clear of the earth under a workman's hands — and the German scholar, who has only ever read about this temple, seeing it with his own eyes. *"Europe wanted to see the grandeur of the past with its own eyes."* That line is the museum's; the shot is its literal picture.

**Claim:** the German excavations of 1875–81 uncovered the Temple of Zeus with a large local workforce. Sourced (Commons 1875/76 photograph; LoC 1897; Curtius/Adler reports; DAI).
**Not asserted:** any named person (no "Curtius" — a type); any specific find; an exact date; that this is the *very first* drum (it is *a* first drum, a representative morning). No text anywhere in frame.

---

## References (one @mention per entity — 6 total, under the 7 cap)

| @ | File | Role in the prompt |
|---|---|---|
| @Image1 | `env_temple-of-zeus_1870s.png` | **the setting** — sets aspect ratio (1920×1080, first ref) |
| @Image2 | `workman_prod.png` | **the workman** (identity + costume + the pick) |
| @Image3 | `archaeologist_prod_v2.png` | **the archaeologist** (identity + sack coat + staff) |
| @Image4 | `OlympiaGermanExcavation.jpg` | **the crowd + composition** — the real 1875/76 photograph |
| @Image5 | `1a_storyboard_panels.jpg` | **blocking only** — Storyboard Mode; never on screen |
| @Image6 | `LoC_1897 (cropped single frame)` | **the view + the hill** — the Kronos hill as it really sits behind the temple |

Pre-flight (done): LoC is the cropped single frame, not the stereo card. No reference carries an inscribed surface — 1a has no museum artefact. `ref_cropped: true` would be declared if it did.

---

## The prompt (Seedance 2.5 · mode `omni_reference` · 6 s · 16:9 · 1080p · `generate_audio: false`)

> Open on the setting from @Image1, held exactly — the excavation cut through the Temple of Zeus at Olympia, 1875, camera on the south side looking north so the rounded, wooded Kronos hill from @Image6 fills the upper third. Match the framing and composition of Panel 1 in @Image5 (storyboard reference). Hard, high spring sun; fine dust hanging in the light; pale shell-limestone and raw earth; the Doric column drums — HUGE, each taller than a man and more than two metres across, a sea of them, many dozens, tumbled in two long collapsed rows and heaped where they fell, each a stack of several drums come apart — the fallen colonnade of a temple that stood twenty metres high.
>
> In the foreground, left of centre, @Image2 (the workman — the same man, the same knee-length dust-grubby fustanella, white headcloth, dark sash, bare lower legs, rough shoes) stands on the rubble of the cut with his pick, two-fifths of the frame tall, turned three-quarters toward camera. He is dwarfed by the drum beside him: it rises well above his head, and he stands at its foot.
>
> At the left edge, on the trench lip, @Image3 (the archaeologist — the same bearded man in the same high-buttoned dark sack coat, bowler hat, wooden measuring staff) stands with his back half to camera, watching the work.
>
> Beyond them, on the spoil heaps across the middle distance, a crowd of forty or more workmen in fustanellas and dark caps, arranged like the crowd in @Image4, a few boys seated at the front — small figures, no faces readable.
>
> THE ACTION, in order: two workmen in the middle distance lever a huge limestone block with a timber bar; it tips and SETTLES into the spoil with a visible drop of dust. As it lands, the foreground workman TURNS HIS HEAD toward the sound, and the archaeologist on the lip takes one step forward and leans on his staff, LOOKING at the block — both react to the same event, nothing else. The camera is locked off; then one slow push toward the workman as he turns.
>
> Photographic realism, natural skin and cloth texture, no stylisation. Bleached limestone and pale dust dominate; the only strong darks are the archaeologist's wool suit and the trench shadow; the white fustanellas are the brightest thing in frame.
>
> No standing columns, no intact temple, no mountains, no sea, no lawn, no modern paths or ropes or visitors, no cypress avenue, no text, no lettering, no signage, no watermark. No pith helmet, no khaki, no Evzone parade dress, no pom-pommed shoes, no fez. Faces are not any real person. Extra fingers, six fingers, deformed hands excluded.
>
> **Audio:** none generated. (If a pass with sound is wanted: picks on stone, a timber bar creaking, the block's dull settle, dust, distant voices in Greek, wind off the hill — diegetic only, no music.)

---

## Gates (videogen, whole-clip, before it reaches the Review Room)

1. **Location** — background matches @Image1: Kronos hill rounded and wooded; drums in two lines; no standing column; no modern object.
2. **Characters** — same workman and archaeologist as the sheets (costume NEVER lists); no third "hero" character invented.
3. **Scale** — the drums DWARF the men: the foreground drum rises above the workman's head; the far rows are a sea of drums, not a tidy pair of lines. Check against the 1875/76 photograph.
4. **Action** — the block visibly tips and settles, AND both characters react to it (workman turns his head; archaeologist steps and looks). Static characters = reject.
5. **Text** — zero lettering anywhere, any frame (exploratory pass: "is there anything in frame that is not specified?").
6. **Hands** — the known failures.

**Output:** `out/1a-the-rediscovery/k1.mp4` + ledger (refs, prompt, per-gate result, candidates). Then Philipp reviews. k2/k3 derive from k1 only after that.
