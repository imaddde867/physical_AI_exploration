"""Render the saved character; run with Blender --background --python this_file -- ..."""
import argparse
import json
import math
from pathlib import Path
import sys

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from frame_timing import frame_times


def select_clip(clip):
    """Select a native saved Action; retain the original foundation's clip names."""
    scene = bpy.context.scene
    rig = bpy.data.objects["Crying head 2 | source rig"]
    actor = rig.parent
    for track in rig.animation_data.nla_tracks:
        track.mute = True
    actor.animation_data.action = None
    actor.rotation_euler = actor["rest_rotation"]
    library = bpy.data.texts.get("STATE LIBRARY")
    states = json.loads(library.as_string()) if library else {}
    name = "look_around" if clip == "look" and states else clip
    if name in states:
        action = bpy.data.actions[states[name]["action"]]
    else:
        action = bpy.data.actions[{
            "rest": "DERIVED | Watch rest", "look": "DERIVED | Watch rest",
            "idle": "SOURCE | Idle", "move": "SOURCE | move",
        }[clip]]
    rig.animation_data.action = action
    rig.animation_data.action_slot = action.slots[0]
    scene.frame_start, scene.frame_end = map(int, action.frame_range)
    if clip == "look" and not states:
        rig.animation_data.action = None
        track = rig.animation_data.nla_tracks.new()
        track.name = "Preview | repeated watching rest"
        strip = track.strips.new("DERIVED | Watch rest", 1, action)
        strip.action_slot = action.slots[0]
        strip.repeat = 3
        actor.animation_data.action = bpy.data.actions["DERIVED | Look around"]
        actor.animation_data.action_slot = actor.animation_data.action.slots[0]
        scene.frame_end = int(actor.animation_data.action.frame_range[1])
    scene.frame_set(scene.frame_start)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clip", choices=("watch", "look_left", "look_right", "look_around",
                        "lean_back", "lean_in", "shift", "scratch", "rest", "idle", "move", "look"),
                        default="watch")
    parser.add_argument("--camera", choices=("window", "full", "quarter"), default="window")
    parser.add_argument("--fps", type=int, choices=(12, 15, 20, 24, 25, 30, 60), default=30)
    parser.add_argument("--size", type=int, default=1, help="Integer multiple of 240 x 280")
    parser.add_argument("--output", type=Path, required=True, help="New output folder")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    if not 1 <= args.size <= 8:
        parser.error("--size must be between 1 and 8")
    output = args.output.resolve()
    # Never mix a new render with an old frame sequence.
    output.mkdir(parents=True, exist_ok=False)
    scene = bpy.context.scene
    rig = bpy.data.objects["Crying head 2 | source rig"]
    assert len(rig.data.bones) == 95
    select_clip(args.clip)
    times = frame_times(scene.frame_start, scene.frame_end, 24, args.fps)
    scene.camera = bpy.data.objects[{
        "window": "CAM | Window close-up",
        "full": "CAM | Full character",
        "quarter": "CAM | Three quarter",
    }[args.camera]]
    # Evaluate real Blender subframes; 30 FPS must not become slower 24 FPS motion.
    scene.render.fps = 24
    scene.render.fps_base = 1
    scene.render.resolution_x = 240 * args.size
    scene.render.resolution_y = 280 * args.size
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.use_persistent_data = True
    for index, source_time in enumerate(times, 1):
        frame = math.floor(source_time)
        scene.frame_set(frame, subframe=source_time-frame)
        scene.render.filepath = str(output / f"frame-{index:04d}.png")
        bpy.ops.render.render(write_still=True)
    frames = sorted(output.glob("frame-*.png"))
    expected = len(times)
    assert len(frames) == expected and all(p.stat().st_size for p in frames)
    (output / "render.json").write_text(json.dumps({
        "clip": args.clip, "camera": args.camera, "playback_fps": args.fps,
        "source_fps": 24, "frame_step": 24 / args.fps, "frames": len(frames),
        "source_duration_seconds": (scene.frame_end-scene.frame_start)/24,
        "playback_duration_seconds": len(frames)/args.fps,
        "resolution": [scene.render.resolution_x, scene.render.resolution_y],
        "blend": bpy.data.filepath,
    }, indent=2) + "\n")
    print(f"Rendered {len(frames)} frames to {output}; play the sequence at {args.fps} FPS")


if __name__ == "__main__":
    main()
