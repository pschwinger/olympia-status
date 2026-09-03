# 1a · THE WHOLE SCENE IN ONE GENERATION — Seedance 2.5 multishot test

**Philipp (2026-08-22):** "why don't we use Seedance and create the whole video? … just say what we want in different scenes and see what happens."

**What we know:** Seedance 2.5 on Higgsfield = **4–30 s per generation**, 1080p, omni-reference (image refs + optional start image). The `seedance-genhq` skill's multishot format — timestamped `[t–t] Shot N:` lines, one action per shot, 1–4 s each, `Final beat:` last — makes the model **cut between shots inside one clip**, so lens, grade and characters stay consistent for free. The GenHQ corpus documents this for 2.0 only (15 s cap, "up to 3 shots in one scene"); **five shots in 20 s on 2.5 is untested. That's the experiment.**

**Format checklist (GenHQ / seedance-genhq):** bracketed timestamps tiling the runtime · subject + action in the first 20–30 words of every shot · 10–15 words per second · every referent named (no pronouns — the v4 lesson) · `Final beat:` with motion alive · never "fast" · one diegetic Audio line · ≤ 7 refs.

## References (5, bound + scoped)

| @ | File | Role · scope |
|---|---|---|
| @Image1 | `k1_v3_start.png` (2K upscaled) | **the scene + light + stone** — the hero frame; Shot 2 opens on it |
| @Image2 | `workman_prod.png` | **the workman** — governs his and every labourer's dress exactly (shirt, sash, fustanella, headcloth; no vest) |
| @Image3 | `archaeologist_prod_v2.png` | **the archaeologist** — governs his dress exactly (sack coat, bowler, staff) |
| @Image4 | `env_temple-of-zeus_1870s.png` | **the empty dig** — Shot 1 opens on it; background only elsewhere |
| @Image5 | `1a_storyboard_panels.jpg` | **blocking only** — framing of Shots 2–4; never on screen |

## The prompt (Seedance 2.5 · omni_reference · 20 s · 16:9 · 1080p · audio off) — ≈ 14 w/s

```
[00:00-00:04] Shot 1: The empty excavation from @Image4 under hard noon sun — fallen column drums, the raw trench, the wooded hill behind; no people yet. Locked-off eye-level wide, dust in the light, albumen tone. Hard cut to Shot 2.
[00:04-00:10] Shot 2: The workman from @Image2 stands at the foot of the towering drum, opening on @Image1, as two labourers behind him lever a limestone block with a timber bar; the block tips and settles with a drop of dust; the workman turns his head toward the block, and the archaeologist from @Image3 steps forward on the trench lip to look. Match Panel 1 in @Image5. Locked-off wide, then one slow push toward the workman. Hard cut to Shot 3.
[00:10-00:14] Shot 3: Two labourers dressed as @Image2, waist-up in profile, heave down together on the timber bar under the edge of the fluted drum; the drum's edge lifts a hand's width, rocks, and settles back with dust off its face as their shoulders drop. Close-up, shallow focus on hands and stone. Match Panel 2 in @Image5. Hard cut to Shot 4.
[00:14-00:17] Shot 4: The workman's dusty hands from @Image2 sweep earth off the flute of a buried drum, the fluting emerging under his palm. Low angle from the trench floor, macro, very shallow focus. Match Panel 3 in @Image5. Hard cut to Shot 5.
[00:17-00:20] Shot 5: Final beat: the archaeologist from @Image3 on the trench lip, medium three-quarter, takes off his bowler and looks down the uncovered colonnade; dust keeps drifting through the light past him through the closing frame.
Audio: Natural diegetic sound only — picks on limestone, the timber bar creaking, the dull settle of stone into gravel, breath, wind off the hill, distant voices. Full sound design. No music, no score.
```

No bare chests, no Evzone parade dress, no pith helmet, no standing column, no modern object, no text or lettering anywhere. Faces are not any real person.

## Claims (unchanged from k1/k2 ledgers) · *Shot 5 is new:* the hat-off look is **Invented** as a gesture (no source describes it); nothing factual is asserted by it.

## Gates (whole clip, per shot)
1. **Cuts happen where the timestamps say** (the format's core claim — does 2.5 honour five hard cuts in 20 s?)
2. **Same workman / same archaeologist across all shots** (the in-clip consistency claim)
3. **Scale** — drum/man ratio > 1.0 in Shots 2–3
4. **Each shot's one action occurs on the named object** (block in 2, drum edge in 3, flute in 4)
5. **Costume NEVERs every frame; zero text; hands**

**What we learn either way:** if it holds, a three-shot scene becomes one generation and consistency is free; if cuts smear or characters drift between shots, we know 2.5's multishot ceiling and stay with shot-by-shot start images.
