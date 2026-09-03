# 1a · k2 — CLOSE-UP: "The lever"

**Requested by Philipp (2026-08-22):** take k1 v1 and make a second shot, a close-up of the men moving the column.

## How this shot is derived (the chain)

| Step | What | Who | Why |
|---|---|---|---|
| 1 | **Composition + moment** come from k1 v1: the two men in the middle distance with a timber bar against the stone (frame ~2.5 s, cropped) | storyboard (done) | the close-up must be *the same event* the wide shows — continuity |
| 2 | **Costume + identity** come from the **workman design sheet**, *not* from v1. In v1 the two levering men are bare-chested — the 1875/76 photograph shows every labourer in a shirt, and bare chest is on our NEVER list. The wide got away with it at distance; a close-up cannot. | storyboard → imagegen | sheet-first; a close-up is the high-fidelity regime |
| 3 | **Keyframe first**: imagegen composites ONE start image of the close-up (below), gated | imagegen | the rule k1 v3 proved: fix scale/pose in the still, then animate |
| 4 | **Animate from the start image** in Seedance 2.5 omni-reference, 5 s, then re-check across the clip | videogen | |
| 5 | Philipp reviews; k2 joins k1 on the board with its prompt beside it | | |

## What I need from Philipp (taste calls only — everything else is derivable)

1. **Which beat?** (a) the *strain* — bar bent, feet dug in, the stone not yet moving; or (b) the *give* — the stone tips and settles, dust. **My recommendation: (b)**, because it's the consequence the wide shows, and a close-up of a thing *happening* cuts better than one of effort. *(Default if you don't say: b.)*
2. **How tight?** (a) hands + bar + stone edge only — abstract, no faces; or (b) two men waist-up, faces in profile. **Recommendation: (b)** — faces are types, never named persons, so nothing is asserted. *(Default: b.)*
3. **v1 as the hero?** v1 is the version with the chest-high drum. If you prefer it to v3 as the wide, that's your call and I'll record it — but the close-up works with either.

## What is derived, and from where (the claim ledger)

| Element | Status | Source |
|---|---|---|
| Large stone being moved by hand with a timber lever | **Sourced** | 1875/76 excavation photograph (picks, bars, spoil); Curtius/Adler reports describe manual haulage |
| Labourers in shirts, working fustanella, headcloth, sash | **Sourced** | the 1875/76 photograph; the character sheet |
| The stone is a fluted Doric drum of the Temple of Zeus | **Sourced** | drum geometry from the 2019/2020 Commons photographs |
| A timber bar (not an iron crow) | **Assumed, conf 0.6** | period-plausible; the photograph doesn't resolve the material — kept generic "timber bar", not asserted in close-up detail |
| *Not shown / not asserted* | | any named person; any specific find; any text or mark on the stone; any tool we can't source (no block-and-tackle, no rails) |

## References (one @mention per entity — 4)

| @ | File | Role |
|---|---|---|
| @Image1 | `k1_v1_blockcrew_crop.jpg` (crop from k1 v1 at ~2.5 s) | **composition + moment** — sets 16:9 |
| @Image2 | `workman_prod.png` | **costume + identity** for both men (two different men of the same type: the second is darker-bearded, a size heavier) |
| @Image3 | `Commons_2019_Temple-of-Zeus_re-erected-column_CC-BY-SA-4.0.jpg` | **the stone's surface** — fluting, pitted shell-limestone (the column itself must NOT appear standing) |
| @Image4 | `env_temple-of-zeus_1870s.png` | **background** — the trench wall and spoil behind the men |

Pre-flight: none of these carries an inscribed surface or a mount. @Image3 shows a standing column — it is a *texture* reference; the prompt forbids a standing column explicitly.

## The start image (imagegen, 1920×1080) — then the motion (videogen)

> Close on two workmen from the waist up, in profile and three-quarter, straining at a long timber bar wedged under the edge of a huge fluted limestone drum that fills the right half of the frame — pitted, pale, the fluting catching hard sun, as in @Image3 but lying on its side, never standing. The men are the type in @Image2: white shirts with wide sleeves pushed up, dark sashes, knee-length dust-grubby white fustanellas, white headcloths; one with a full dark moustache, the other heavier, dark-bearded. Shirts ON. Forearms corded, hands gripping the bar, dust on the cloth. Behind them the raw earth trench wall and gravel spoil from @Image4, soft. Hard high sun, dust hanging in the light. Composition and moment as in @Image1.
>
> Photographic realism; natural skin and cloth texture; bleached limestone and pale dust dominate; the white shirts are the brightest thing in frame.
>
> No bare chests, no Evzone parade dress, no pom-pommed shoes, no fez, no standing column, no modern tools, no rope-and-pulley, no text, no lettering, no watermark. Faces are not any real person. Extra fingers, deformed hands excluded.

**Motion (Seedance 2.5 · `omni_reference` · `start_image` = the keyframe · 5 s · 1080p · audio off):**

> Locked-off close-up. ONE ACTION: the two men heave down on the bar together; the drum's edge lifts a hand's width, rocks, and SETTLES back into the earth with a soft drop of dust off its face. Their shoulders drop as it lands. Nothing else moves but the dust. No camera move.

## Gates (whole-clip)

1. **Costume** — shirts on, both men, every frame (the v1 drift must not return); headcloth, sash, fustanella per the sheet.
2. **Action** — the drum edge visibly lifts and settles; a gesture without the stone moving is a reject.
3. **Scale** — the drum's visible height exceeds the men's torso height in every frame (measured start / mid / end).
4. **Text** — none, any frame; exploratory pass.
5. **Hands** — the grip on the bar: five digits, clean, both men.
6. **Continuity with the wide** — same stone type, same light direction, same dust.

**Output:** `out/1a-the-rediscovery/k2_start.png` → `k2.mp4` + ledgers. Then Philipp reviews.
