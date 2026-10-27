# Mac Integration Feasibility Audit

As of 2026-10-27. **Verified** means documented interface or repository fact; **Conditional** means user permission, app setup, account, or policy gates apply; **Unavailable** means no supported general interface was verified. This is feasibility research, not implementation status.

## 1. Existing project and smallest architecture

### Takeaway
**Verified:** The repository is a software prototype with a Mac Python CLI host speaking JSONL over USB to an ESP32-S3 rendering one approved 240×240 face, six moods, blink, and optional MPU-6050 shake events. No timers, macOS integrations, notification reading, screen capture, music, or AI exist. Keep expressive face first; use occasional short text/events from one Mac host process. Add opt-in semantic screen awareness later, event-driven rather than continuous capture.

### Cited Findings
- README describes the Mac Python host, USB serial, ESP32-S3, display, optional motion sensor, and explicitly says the prototype has no AI/voice/camera/network/local model now. — [README](../../README.md)
- Protocol v1 contains allowlisted face commands; architecture calls firmware deterministic/offline and notes that one-way SPI cannot verify illuminated pixels. — [Architecture](../../docs/architecture.md)
- Current host command API is face-only; demo can simulate or print device shake events. — [Protocol](../../macdesk/protocol.py); [demo](../../macdesk/demo.py); [firmware](../../firmware/src/main.cpp)
- ScreenCaptureKit supports picking a display/app/window and capture streams; Apple requires screen capture permission and recommends the system content sharing picker. — [macOS capture sample](https://developer.apple.com/documentation/screencapturekit/capturing-screen-content-in-macos?language=objc); [Apple privacy session](https://developer.apple.com/videos/play/wwdc2023/10053/?time=1530)
- Apple Vision offers OCR using VNRecognizeTextRequest. — [VNRecognizeTextRequest](https://developer.apple.com/documentation/vision/vnrecognizetextrequest?changes=_1&language=objc)

### Inferences
- Smallest architecture: existing Mac-side host handles timers, event arbitration, integrations and USB; ESP32 remains a rendering/input peripheral. Send compact state/event values and optionally bounded short text.
- No extra hardware is required for the first prototype. Existing target parts remain as specified in [shopping list](../../docs/shopping-list.md). Do not buy camera, microphone, GPU, or AI subscription for the face-first objective.
- Start with deterministic timers/manual events, then short text, foreground app identity, supported coding-tool hooks, optional user-started OCR, and music metadata. Separate cloud/model features from this local baseline.
- Face reactions can be driven by track/status metadata; lyrics are not needed. Timer, USB, Claude Code hook, or local OCR operation alone does not imply API charges. Model API use or external lyrics service may introduce fees/terms.

### Gaps
- No physical hardware is confirmed purchased or tested. Actual display readability, color, brightness, host reconnect and timing remain unverified.
- Protocol has no text or timer fields; a protocol extension is future work, not available now. Text display behavior must suit a 240×240 screen.

## 2. macOS data, permissions, and access

### Takeaway
**Verified:** macOS gives apps APIs for their own notifications and for foreground-app changes. No supported general third-party API was found to subscribe to arbitrary apps’ notification payloads. Screen pixels and system audio can be captured with user authorization; OCR only processes the image it is given. Prefer explicit, bounded capture.

### Cited Findings
- UNUserNotificationCenter is for the calling app’s local/remote notifications, authorization, delivered notifications, and actions. It does not document cross-app notification reading. — [UNUserNotificationCenter](https://developer.apple.com/documentation/usernotifications/unusernotificationcenter?changes=latest__7&language=objc); [asking permission](https://developer.apple.com/documentation/usernotifications/asking-permission-to-use-notifications)
- Foundation NotificationCenter is scoped to a single program; DistributedNotificationCenter is interprocess messaging, not a documented inbox for arbitrary user-facing notifications. — [NotificationCenter](https://developer.apple.com/documentation/foundation/notificationcenter?changes=l_1_2_2)
- NSWorkspace posts didActivateApplicationNotification and identifies the app being activated. This supports app identity, not its window contents. — [didActivateApplicationNotification](https://developer.apple.com/documentation/AppKit/NSWorkspace/didActivateApplicationNotification?changes=latest_major&language=obj_2)
- ScreenCaptureKit supports selectable display/app/window capture and requires screen-recording permission; Apple’s sample notes restart after first grant to enable capture. — [macOS capture sample](https://developer.apple.com/documentation/screencapturekit/capturing-screen-content-in-macos?language=objc)
- ScreenCaptureKit audio is off by default. Core Audio system-audio taps need NSAudioCaptureUsageDescription and first-use recording permission; microphone capture separately requires permission and usage text. — [capturesAudio](https://developer.apple.com/documentation/screencapturekit/scstreamconfiguration/capturesaudio); [system audio taps](https://developer.apple.com/documentation/coreaudio/capturing-system-audio-with-core-audio-taps?changes=late_1_5_5); [media capture authorization](https://developer.apple.com/documentation/AVFoundation/requesting-authorization-to-capture-and-save-media?changes=_4_3)
- Vision provides text recognition on supplied images; it does not grant image capture access. — [VNRecognizeTextRequest](https://developer.apple.com/documentation/vision/vnrecognizetextrequest?changes=_1&language=objc)

### Inferences
- Notifications: own timer/local notifications are **Verified**; app-specific supported integrations are **Conditional**; arbitrary app notification-body ingestion is **Unavailable through the documented general Apple API**. Do not represent screen recording or accessibility access as notification permission.
- Foreground app name/bundle ID can be a low-scope signal. Ask separately before screen capture, show active/pause/stop controls, choose a window/app over the whole display, and prefer local OCR. Require a separate opt-in before sending any image/text to a cloud model.
- Audio reactivity can be an amplitude-only local signal but system output capture requires explicit authorization. Track metadata is less invasive; use raw system audio only as an opt-in fallback.
- Accessibility APIs target assistive clients and require separate privacy access; this audit did not verify a stable universal semantic reader across arbitrary windows. Treat it as app-specific/brittle, not guaranteed screen understanding.

### Gaps
- Exact permission, entitlement, signing, picker, and grant persistence behavior depends on macOS version and packaging. The target laptop OS is unknown.
- Python background-process permission behavior versus a signed native app was not validated for a particular implementation.

## 3. Music metadata, reactions, and lyrics

### Takeaway
**Conditional:** Apple Music MusicKit and Spotify’s OAuth Web API can supply playback/track metadata for reactions, gated by consent/account/scopes. Lyrics are separate: Apple’s Song model provides a hasLyrics availability flag, not a documented lyrics-text field. Do not promise extracting/displaying lyrics without a confirmed licensed source and terms.

### Cited Findings
- MusicKit offers Apple Music catalog, playback, and music library features; user authorization is required and subscription capabilities gate features. — [MusicKit](https://developer.apple.com/documentation/musickit?changes=_3)
- Apple Song includes title, artist, duration, and hasLyrics availability boolean. The cited API page does not document lyrics text. — [Song](https://developer.apple.com/documentation/musickit/song)
- Spotify playback-state API returns current item, position, active device and playing status, requires OAuth user-read-playback-state; Web API getting started says Premium is required. — [Get playback state](https://developer.spotify.com/documentation/web-api/reference/get-information-about-the-users-current-playback); [Web API](https://developer.spotify.com/documentation/web-api?rd=1)
- Spotify’s API policy notes prohibit synchronizing Spotify recordings with visual media and restrict commercial streaming integrations. Confirm current terms before distribution. — [Get playback state policy notes](https://developer.spotify.com/documentation/web-api/reference/get-information-about-the-users-current-playback)

### Inferences
- First music feature should react to title/artist/play/pause/track change, with no history retention and a toggle. Apple Music is native; Spotify adds app registration, OAuth scopes and current policy constraints.
- “React to music” is feasible without lyrics (metadata or a local amplitude meter). Lyrics should be a separate future feature pending provider license, attribution, territory, and display terms.
- Occasional short text could show track/artist when enabled. Avoid lyric excerpts absent verified rights.

### Gaps
- No official general API was verified for reading live Apple Music lyrics from another process or for Spotify lyric text. This is not a claim that no licensed lyrics service exists.
- Exact Apple developer requirements and costs depend on whether metadata, library, playback control, or full catalog playback is implemented; review at implementation.

## 4. Codex and Claude status

### Takeaway
**Conditional:** Supported hooks and APIs exist, but they expose agent workflows, not universal telemetry from arbitrary desktop chats. Claude Code provides hooks and a scriptable statusline with structured session data including context/cost-related fields. Codex provides SDK/app-server/CLI and plugins/hooks for workflows it runs or explicitly integrates with; no supported general attachment to private state of an already-running Codex desktop conversation was verified. Claude Desktop MCP extensions are distinct from Claude Code CLI hooks.

### Cited Findings
- OpenAI distinguishes Codex SDK (start/resume/stream Codex tasks) and app-server (connect an application to a local Codex process and stream events). This is not a GUI chat scraping API. — [Codex as a platform](https://developers.openai.com/blog/codex-as-a-platform)
- Codex plugins can bundle MCP/skills and manually installed desktop plugin lifecycle hooks; hooks require available scripts and user trust. — [Package your plugin](https://developers.openai.com/plugins/build/plugins)
- Claude Code supports event-based hooks with structured inputs. — [Hooks reference](https://code.claude.com/docs/en/hooks)
- Claude Code statusline runs configured shell script, receives JSON session data on stdin, and documents context, spend-limit, prompt-cache and cost/duration fields. — [Status line](https://code.claude.com/docs/en/statusline)
- Claude Desktop supports configured local MCP servers and desktop extensions for local files/apps. This is a separate integration mode from Claude Code hooks. — [Local MCP servers](https://support.anthropic.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop); [connectors](https://support.anthropic.com/en/articles/11725091-when-to-use-desktop-and-web-connectors)
- OpenAI Docs MCP is documentation-only, not an API for desktop session state. — [Docs MCP](https://developers.openai.com/learn/docs-mcp)

### Inferences
- Claude Code: opt-in hook/statusline script can publish minimal local state to the Mac host via a local file/socket; do not read undocumented ~/.claude internals.
- Codex: first react to foreground app identity. For live agent events, Buddy can launch/manage a Codex workflow using official SDK/app-server or consume an explicitly configured supported hook/plugin. Do not promise existing GUI chat token counts.
- Define “token usage” carefully. Claude Code has documented session/context/cost status data. Codex can stream events for Buddy-owned sessions; this does not imply access to subscription allowance or current GUI chat token tally.
- Local forwarding has no model API cost by itself. A model summary/vision call incurs normal API usage and shares input with that service per its policies.

### Gaps
- Confirm current SDK/app-server event schemas, token fields, and version compatibility before guaranteeing exact Codex metrics.
- No general Claude Desktop current-conversation-usage API was verified. Desktop MCP access is configured and scoped, not automatic blanket state access.

## 5. Purchase verdict and critical gotchas

### Takeaway
**Verified verdict:** Existing purchase target is enough for the face-first prototype; no extra computer, camera, microphone, screen, or AI subscription is needed. The BOM price is an estimate, and real electrical/display behavior remains unverified.

### Cited Findings
- README says quoted basket is an estimate and calls out pre-soldered headers, backlight pin, actual dimensions and printer-model checks. — [README](../../README.md); [shopping list](../../docs/shopping-list.md)
- Development notes state actual macOS release, SSD, and live performance are unknown; M4 specs are a model profile, not measurement. — [Development host](../../docs/development-host.md)
- Screen, music, OCR and coding-agent integration surfaces documented above carry separate permission/account/policy qualifiers. — [ScreenCaptureKit](https://developer.apple.com/documentation/screencapturekit?changes=latest_be_8); [MusicKit](https://developer.apple.com/documentation/musickit?changes=_3); [Spotify playback](https://developer.spotify.com/documentation/web-api/reference/get-information-about-the-users-current-playback); [Codex SDK](https://developers.openai.com/codex/sdk); [Claude hooks](https://code.claude.com/docs/en/hooks)

### Inferences
- Buy the already scoped ESP32-S3/display items after the listed parts checks; defer optional IMU if needed. Verify assembled hardware before promising robust behavior.
- Keep data minimal: no screen images by default, no notification payloads, no music history. Transient status and user-enabled short text are enough for the first integration phases.
- Unknowns that matter before broader commitments: target macOS version; actual hardware/stock; user’s active music and agent products/accounts; desired text layout and licensing route.

### Gaps
- No live check of laptop OS, purchased inventory, hardware, subscriptions, API credentials, display legibility, or current checkout pricing was performed.
