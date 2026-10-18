**Short answer:** about 1–3 days of focused work to build it, plus roughly 1–2 weeks of calendar time to get through the Mac App Store. Most of the risk is in the App Store step, not the code.

## Rough breakdown

| Phase | Effort |
|---|---|
| Menu bar app (SwiftUI `MenuBarExtra`, track title/artist, play/pause, next/prev) | 0.5–1 day |
| Spotify integration (reading state, live updates, handling Spotify not running) | 0.5–1 day |
| Polish (album art, launch at login, settings, icon, edge cases) | 0.5–1 day |
| Sandboxing + entitlements + signing for the App Store | 0.5 day (longer if you hit entitlement issues) |
| App Store Connect setup (listing, screenshots, privacy policy URL, description) | 0.5 day |
| App Review | usually 1–3 days per submission; expect 1–2 rejections for this kind of app |

If you have done Swift/macOS work before, the coding is a weekend. If you're new to Xcode, signing, and App Store Connect, budget a week or two part-time.

## The parts that actually decide the timeline

**1. How you talk to Spotify. This is the big one.**
- **AppleScript / Apple Events to the Spotify desktop app.** This is the simplest route. Spotify exposes `name of current track`, `playpause`, `next track`, and so on, and you can watch the `com.spotify.client.PlaybackStateChanged` distributed notification for live updates. The catch is that a sandboxed App Store app needs the `com.apple.security.temporary-exception.apple-events` entitlement targeting `com.spotify.client`. App Review often questions it, so you need a clear justification. Apps like this have been approved, but it's the most likely reason for a rejection. The user also gets a macOS Automation permission prompt the first time.
- **Spotify Web API.** It's sandbox-friendly, but you need OAuth, and playback control needs Spotify **Premium**. Spotify has also tightened API access: new apps stay in development mode, capped at a small number of allowlisted users, unless you qualify for extended quota, which is now aimed at established businesses. In practice that rules it out for a public App Store app from an individual developer. Check Spotify's current developer policy before you go this way.
- **The private MediaRemote framework** (system Now Playing). It isn't allowed on the App Store, and recent macOS versions have restricted it anyway. Skip it.

My recommendation is AppleScript plus the distributed notification, with a short, clear entitlement justification in your review notes.

**2. Naming and branding.** Don't put "Spotify" in the app name or icon, and don't use their logo. App Review rejects apps on IP grounds (guideline 5.2), and Spotify has its own branding rules. Something like "Tune Bar: now playing for Spotify" in the subtitle is the safer pattern.

**3. Account and admin overhead.** You need the Apple Developer Program ($99/yr). Enrollment can take anywhere from hours to a few days, especially for an organization account, which needs a D-U-N-S number. You'll also need a privacy policy URL, even if you collect nothing.

**4. Minimum functionality.** App Review sometimes pushes back on very thin utilities (guideline 4.2). Small extras such as album art, keyboard shortcuts, or launch at login help it read as a real app.

## Realistic total
- **Working app on your own Mac:** 1–2 days, or a few hours with an AI assistant doing most of the code.
- **Live on the Mac App Store:** about 1–2 weeks of calendar time, with maybe 3–5 days of actual work. Most of the wait is review round-trips and entitlement back-and-forth.

If you'd rather skip the App Store risk entirely, distributing a notarized `.dmg` outside the store (direct download, Homebrew cask) removes the sandbox and entitlement problem. That cuts the "ship it" step to about half a day.

Want me to scaffold the Xcode project with the `MenuBarExtra` + AppleScript bridge to start?
