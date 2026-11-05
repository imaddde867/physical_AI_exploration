# Crying head 2 — reusable character foundation

Prepared 2026-11-06. Open **`crying-head-2-master.blend`** for everyday work.
The main shot is a face looking toward the viewer through the 240 × 280 screen,
with original claws around the edges. No wall or generated anatomy is used.
The previous Occupant checkpoints remain separate.

## Saved assets

- `crying-head-2-master.blend`: packed character, original rig/actions, organized
  controls, three cameras, studio lighting and optional whole-character turns.
- `crying-head-2-source.blend`: clean imported source with repaired/packed maps,
  before portrait setup and the actor parent.
- `vendor/crying-head-2/original.zip`: untouched downloaded FBX archive, alongside
  extracted source/maps. Git ignores this folder; include it in local backups.
- `character.json`: source, checksum, actual control chains, clips and changes.
- `ATTRIBUTION.md`: creator credit and CC BY-SA 4.0 license links.
- `character-checks.json`: verification results from the saved master.

The selected model is [Crying head 2 by CommunicationNode](https://sketchfab.com/3d-models/crying-head-2-2867ed3cd41243caaf9dd24eeccf6ca5).
Preserve attribution and license information with shared assets.

## Rig and motion

The mesh has 3,322 vertices and a 95-bone rig. Its topology, skin weights,
bone names/hierarchy and source animation keys are preserved. Used material maps
are packed. The supplied AO map is retained inside the master without multiplying
it into the painted base color. DirectX normal conversion is done with nodes.

There are **12 paired appendage chains**, including smaller appendages, rather
than only the six prominent limbs noticed in the preview. All remain individually
movable. Pose-mode bone collections organize their original controls:

- `Basic`: head and parent of the attached anatomy.
- `Jaw`, `Jaw.001`: jaw/mouth, with five mouth-finger chains.
- `Virus1.L/R`, `.004.L/R`, `.009.L/R`, `.013.L/R`, `.017.L/R`, `.021.L/R`:
  appendage roots. Weighted descendants are mapped in `character.json`.
- `ACTOR | placement + whole-character looks`: overall placement and rotation.

The imported controls use **FK**: select and rotate bones. The FBX supplies no IK
constraints, eyes/eyelids or shape keys. Attention comes from head orientation,
leaning, jaw movement and appendages. It is not a humanoid standing/sitting rig.
Duplicate a source action before editing it. No new anatomy has been added.

| Action | Frames at 24 FPS | Purpose |
| --- | --- | --- |
| `SOURCE | Idle` | 1–77 | Original living idle, matching endpoints |
| `SOURCE | move` | 1–20 | Original movement, matching endpoints |
| `DERIVED | Watch rest` | 1–77 | Closed-mouth watching; other original idle movement retained |
| `DERIVED | Look around` | 1–229 | Whole-character turns over three repeated resting cycles |

**Watch rest is the default**, using mouth-test C3: a neutral closed jaw.
The exposed teeth remain part of the source design. The original open-mouth Idle
is preserved as a separate action. Only Jaw location/rotation were replaced in
the resting take; the other original animation channels remain unchanged.

Actions and the character collection are retained as Blender assets. The native
asset library is registered as `MacDesk Character`. The look action turns the whole actor;
it is not independent eye or neck tracking. New gestures and reactive transitions
still require animation and visual review.

## Shots and everyday workflow

Open the master and keep working in that saved scene. Do not reimport or rebuild
it for normal pose, material, lighting or camera changes. Save new takes separately.

- `CAM | Window close-up`: primary shot, 240 × 280. Face toward viewer; appendages
  intentionally crop at screen edges. User preferred the third viewing angle (75°
  in the source orientation), slightly closer. The current polished take is
  **layout C3**: recentered on the closed face, corrected 16° for vertical
  alignment, and another 10% closer. This camera correction does not alter anatomy.
- `CAM | Full character`: inspection shot, checked against every source animation
  frame. Use this to see the complete creature and all appendages.
- `CAM | Three quarter`: alternate shot, adjustable for new material.

Select the rig in Pose mode and use named bone collections. Use the actor parent
for overall placement. Source timing stays at **24 FPS**; directly changing it to
12 FPS would slow the motion. The helper samples it for 12 FPS playback instead.

From the repository root:

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  -b animation/crying-head-2-master.blend --python-exit-code 1 \
  --python animation/render_character.py -- \
  --clip look --camera window --output animation/tmp/new-look
```

Options: `--clip rest|idle|move|look` (default `rest`), `--camera window|full|quarter`, `--fps 12|24`,
`--size 1..8` (multiples of 240 × 280). The output folder must be new to prevent
mixing sequences. Rendering does not save changes back to the master. Playback FPS
is recorded in `render.json`. Encode using that FPS:

```sh
ffmpeg -framerate 12 -pattern_type glob \
  -i 'animation/tmp/new-look/frame-*.png' \
  -c:v libx264 -pix_fmt yuv420p animation/tmp/new-look.mp4
```

Generated previews and comparison grids belong in ignored `tmp/`.
`shot-comparisons.json` records 56 angle/distance/lighting, jaw and layout tests.
Large labeled grids are in `tmp/comparisons/`, `tmp/mouth-comparisons/` and
`tmp/layout-comparisons/`. Mouth C3 is approved; layout C3 is the current working
composition, rather than a separately approved final visual design.

## Verification and limits

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  -b animation/crying-head-2-master.blend --python-exit-code 1 \
  --python animation/check_character.py
```

The check compares master geometry, skin weights, bones and original keyframes to
the source import; checks packed material textures; evaluates both source clips
and the wide camera; and exercises all 12 appendage roots independently. Both
source clip endpoints match exactly. This does not prove future poses are free of
self-intersections.

The RP2040 will play exported pixels, not run the 3D rig. Compression, RGB565,
flash budget, reactive transitions and device playback are not part of this
foundation and have not been measured for this character.

## Installed connection

Blender 5.2.2 LTS is installed at `/Applications/Blender.app`. Official
[Blender Lab MCP](https://projects.blender.org/lab/blender_mcp), source revision
`dbbf836ad4b1025f14a2b3b504c43903f39e0b04`, add-on 1.0.0 / server 1.0.2,
is registered as `blender-lab`. Its isolated environment is
`~/.local/share/macdesk-blender/venv`; local address `127.0.0.1:9876`.
No paid API is required.

```sh
open -n -a /Applications/Blender.app --args --online-mode \
  "$PWD/animation/crying-head-2-master.blend"
```

`occupant-stage.blend` and `create_stage.py` remain historical scaffolding,
not the working character master.
