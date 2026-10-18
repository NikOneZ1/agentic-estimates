## Estimate: Spotify now-playing menu bar app, shipped on the Mac App Store

**Bottom line:** ~2–3h of agent work (P90 ~5h) · ~2–3h of your time (P90 ~4h) · on the store in ~2–4 days (P90 ~1–2 weeks)
The code is the small part. What sets the date is Apple: App Review takes ~1–2 days per submission, and this app is more likely than most to be rejected at least once. A sandboxed app sending Apple Events to Spotify needs a "temporary exception" entitlement that reviewers question, and putting "Spotify" in the name or icon can trigger a trademark rejection.

What I checked on this machine: I can run parallel subagents and `gh` is installed. You have a valid **Developer ID Application** signing cert, so it looks like you're already in the Apple Developer Program. Missing: **full Xcode** (only Command Line Tools are installed, so I can't archive or upload a Mac App Store build), an App Store Connect API key, Mac App Store distribution certs, and the Spotify desktop app (I need it to test against). There's no calibration log yet, so these numbers come straight from the default priors.

| # | Unit | Type | Lane | Agent | You | Wait |
|---|------|------|------|-------|-----|------|
| 1 | Install Xcode from the App Store, open it once, sign in with your Apple ID | human + wait | – | – | 5–10m | 30–60m download |
| 2 | Install Spotify and log in (so I can test against it) | human | – | – | 5m | – |
| 3 | Research: sandbox + Apple Events entitlements for `com.spotify.client`, Spotify's AppleScript dictionary, App Review precedents | research | C | 10–20m | – | – |
| 4 | Scaffold a SwiftUI `MenuBarExtra` app: LSUIElement, entitlements, usage string, bundle ID | build | A | 10–20m | – | – |
| 5 | Now-playing: listen for Spotify's `PlaybackStateChanged` distributed notification, plus an initial fetch over Apple Events | build | A | 15–30m | – | – |
| 6 | Controls: play/pause, next, previous; handle "Spotify not running" and "permission denied" states | build | A | 10–20m | – | – |
| 7 | Menu UI: truncated title, artwork, buttons, launch at login (SMAppService), app icon | build | A | 20–40m (×2 for polish) | – | – |
| 8 | Privacy policy page (GitHub Pages via `gh`), support URL, listing copy, keywords | build | B | 10–20m | 5m review | – |
| 9 | Approve the Automation prompt, then QA the app: track changes, skip, pause, Spotify quit/relaunch, light/dark menu bar | human | – | – | 15–30m | – |
| 10 | Signing for distribution: Mac App Store certs + provisioning profile (Xcode automatic signing), create an App Store Connect API key | human | – | – | 15–25m | – |
| 11 | App Store Connect: create the app record, privacy label ("no data collected"), price, category | human | – | – | 20–40m | – |
| 12 | Archive, export, upload (2–4 native build cycles), screenshots | build | A | 15–30m | 10m to approve screenshots | 10–60m processing |
| 13 | Submit for review | human + wait | – | – | 5m | ~1–2d |
| 14 | If rejected: reply in Resolution Center, fix, resubmit | unknown | A | 15–45m | 15–30m | +1–3d per cycle |

**Critical path:** 1 → 4 → 5/6 → 7 → 9 → 12 → 13. Archiving and uploading need full Xcode, so start that download first. QA has to happen before the upload, and review can't start until the upload is processed.
**Parallel lanes:** A: app code (4–7, 12) · B: listing and privacy page (8) · C: entitlement and review research (3). Steps 10–11 (your App Store Connect setup) can happen while I'm building lane A.

**What I need from you (in unblock order):**
1. Start the Xcode download now (it's the longest wait on day 1). Install Spotify.
2. Decide: **free or paid?** Free is simpler. Paid also means accepting the Paid Apps agreement and adding tax and banking info in App Store Connect: another 20–40 min of your time, and the banking info can take a day to verify.
3. Pick a name that doesn't start with "Spotify" (something like "<Name> for Spotify" is the usual pattern) and don't use the Spotify logo.
4. Create an App Store Connect API key (Users and Access → Integrations) so I can upload and check build status from the CLI. Otherwise each upload means you clicking through Xcode's Organizer.
5. Approve the macOS Automation prompt the first time the app runs, then do the QA pass.

**Where this could blow up:**
- **Sandbox + Apple Events (unknown, timebox 1h).** Spotify doesn't publish scripting access groups, so the realistic route is the `com.apple.security.temporary-exception.apple-events` entitlement plus a written justification for the reviewer. Apple sometimes accepts this for a small "control app X" tool and sometimes rejects it. Each rejection adds about 1–3 calendar days. The Spotify Web API doesn't solve it: it needs OAuth, it requires Premium for playback control, and new Spotify developer apps are capped at a small number of users unless Spotify grants extended quota. The private MediaRemote framework isn't allowed on the App Store.
- **Trademark (guideline 5.2).** A name, icon or screenshots that look like Spotify's own branding is a common reason for rejection. It costs little to avoid if we plan for it up front.
- **Fallback if the App Store says no:** you already have a Developer ID cert, so I can notarize and ship a direct-download DMG (with no sandbox restrictions) the same day. That takes ~20–30 min of agent work and no review queue.

**Faster if:** Xcode is installed and you've created the App Store Connect API key before I start. Then signing, upload and build-status checks all run from the CLI, which saves you ~20–30 min of Organizer and dashboard clicking. Turning on computer use would let me click through the menu bar UI myself and take the screenshots, which cuts the QA step down to a quick final look.

**Human-era comparison:** a solo Mac developer without agents would typically quote 1–2 weeks: about 3–5 days to build and polish (including figuring out sandboxing and Apple Events), plus a day of App Store Connect work, plus review. Nearly all of the difference is in steps 3–7 and 12. The App Review wait and your App Store Connect clicking take as long as they always did.
