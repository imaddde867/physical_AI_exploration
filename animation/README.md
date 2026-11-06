# MacDesk Buddy — finished character handoff

**Current working scene: `crying-head-2-anchored.blend`.** It is open in Blender
with the calm, closed-mouth watching state selected. The approved source look,
original rig, texture maps and earlier takes are preserved.

## Saved checkpoints

| Checkpoint | Contents |
| --- | --- |
| `f44e690` | Approved 3D character foundation |
| `f56683c` | Calm idle and eight-state library; pushed before polish |
| `f1ec032` | Approved 30 FPS polish and frame-rate tools, before planted contacts |

`crying-head-2-master.blend` and `crying-head-2-polish.blend` retain those earlier
working scenes. `crying-head-2-source.blend` retains the clean source import.
The final planted scene contains all eight new `ANCHORED | ...` Actions.

## Current behavior library

| State | Behavior |
| --- | --- |
| `watch` | Calm centered watching, closed mouth, slight living motion |
| `look_left` | Look toward the viewer's left and return |
| `look_right` | Look toward the viewer's right and return |
| `look_around` | Look left, then right, and return |
| `lean_back` | Draw the head back within the supporting limbs' reach |
| `lean_in` | Lean slightly closer and return |
| `shift` | Small supported settling movement |
| `scratch` | Release one claw, scratch the scalp, and regrip |

Eight original gripping segments are fixed to world-space GRIP controls.
Non-stretch IK bends their proximal joints as the head moves. The four smaller
head appendages remain free. Scratch releases only its active claw; the other
seven supports remain planted. Backward excursion is about 49% of the earlier
floating take, preserving idle movement while respecting reach.

No wall, extra limbs or mesh changes were added. The original 3,322-vertex mesh,
95-bone hierarchy, skin weights and source animation keys remain intact. All
needed material textures are packed. Creator credit/license: `ATTRIBUTION.md`.

The GRIP controls are inside the character asset collection and are not parented
to the moving head. `contacts_enabled` is the rig's native on/off switch. Move
contacts only within joint reach, then rerun validation. `CONTACT MAP` inside the
scene and `contacts.json` record the actual mesh-tip vertices and anchors.

All states use frames 1–193 at 24 FPS: eight seconds excluding the repeated final
pose. Start/end poses and neighboring samples share the idle phase. Enter and
leave pre-rendered gestures at that common boundary; arbitrary-phase interruption
and event scheduling are not implemented.

## Finished previews

- [Floating versus planted](previews/floating-vs-planted.mp4): left is the approved floating polish, right is the new planted version.
- [Planted calm idle](previews/planted-watch.mp4)
- [Planted left glance](previews/planted-look-left.mp4)
- [Planted right glance](previews/planted-look-right.mp4)
- [Planted look around](previews/planted-look-around.mp4)
- [Earlier polished state grid](previews/polished-all-states.mp4)
- [12/24/30 FPS comparison](previews/fps-comparison.mp4)

The remaining preview queue was stopped at the user's wrap-up request. All eight
native planted states are complete and checked; the four finished contact clips
above are retained. Reconstructible render caches and rejected prototypes were
removed from the active workflow. Unique loose drafts were preserved locally in
`.local-archive/2026-11-06/` rather than published or discarded.

## Continue working

Use this saved scene for edits; do not rebuild it for normal posing or lighting.
Select the rig and its Action. For another shot use `CAM | Full character` or
`CAM | Three quarter`. The default window camera is 240 × 280.

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
  -b animation/crying-head-2-anchored.blend --python-exit-code 1 \
  --python animation/render_character.py -- \
  --clip scratch --fps 30 --output animation/tmp/new-scratch
```

The helper supports 12/15/20/24/25/30/60 FPS and resolution multiples via `--size`.
It evaluates real Blender subframes, preserves the eight-second state timing,
and excludes the duplicated endpoint. Output PNG indices are consecutive;
`render.json` records cadence and duration. Encode at that recorded FPS, not a
hardcoded old preview rate. The output directory must be new.

The initial authoring recipes are `build_states.py`, `polish_states.py` and
`anchor_contacts.py`. Native constraints keep contacts planted between samples;
they are not simulated with image warps. Original SOURCE and earlier STATE/POLISH
Actions remain available. Disable contacts to inspect their unmodified free poses.

## Validation and remaining work

- 45 non-GUI Python tests passed; the AppKit smoke test was not rerun.
- `check_character.py`: packed maps, source geometry/weights/bones/keyframes preserved.
- `check_states.py`: all eight states, shared idle boundaries, closed jaw and fixed bone lengths.
- `check_contacts.py`: all eight states at 30 FPS, actual planted tip drift below 0.001 screen pixel, connected joints, scratch release/regrip.

Run a scene check with Blender's `--python` option as in the render command above.
Reports are `character-checks.json`, `anchored-checks.json` and `contact-checks.json`.
Complete mesh self-collision detection is not implemented.

The [frame-rate decision](../docs/hardware/display-frame-rate.md) distinguishes
panel scanning from delivered animation FPS. 30 FPS is an offline target, not a
measured board result. Next: vendor board demo, transfer benchmark, actual color
and tearing checks, then compressed frame export and device event scheduling.
No firmware flashing or physical playback validation has been performed.

## Installed connection

Blender 5.2.2 LTS is installed at `/Applications/Blender.app`. Official
[Blender Lab MCP](https://projects.blender.org/lab/blender_mcp), source revision
`dbbf836ad4b1025f14a2b3b504c43903f39e0b04`, add-on 1.0.0 / server 1.0.2,
is registered as `blender-lab`. Its isolated environment is
`~/.local/share/macdesk-blender/venv`; local address `127.0.0.1:9876`.
No paid API is required.

```sh
open -n -a /Applications/Blender.app --args --online-mode \
  "$PWD/animation/crying-head-2-anchored.blend"
```

`occupant-stage.blend` and `create_stage.py` remain historical scaffolding,
not the working character master.
