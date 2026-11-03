# hov172 AutoPkg recipes

AutoPkg recipes for apps published by Ayala Solutions. Add the repo once and every app in it becomes available:

```bash
autopkg repo-add hov172/autopkg-recipes
```

That short form is all AutoPkg needs: it expands to `https://github.com/hov172/autopkg-recipes` on its own, and the repo is public, so no GitHub account is required. The recipes are YAML and need AutoPkg 2.3 or later.

## Apps

| App | Recipes | Source |
|-----|---------|--------|
| Stash Video | `StashVideo.download`, `StashVideo.munki`, `StashVideo.jamf`, `StashVideo.intune` | [hov172/StashVideos](https://github.com/hov172/StashVideos) |
| DisplayHelp | `DisplayHelp.download`, `DisplayHelp.munki`, `DisplayHelp.jamf`, `DisplayHelp.intune` | [hov172/DisplayHelp](https://github.com/hov172/DisplayHelp) |
| BonjourView | `BonjourView.download`, `BonjourView.pkg`, `BonjourView.munki`, `BonjourView.jamf`, `BonjourView.intune` | [hov172/BonjourView](https://github.com/hov172/BonjourView) |

Every download recipe fetches the vendor's signed and notarized artifact straight from GitHub Releases and fails if the Developer ID signature does not match Team ID `N859JA9UCJ`. Stash Video and DisplayHelp ship flat packages, which are deployed as is. BonjourView ships a zipped app bundle, so its `.pkg` recipe wraps the verified app in a package with AutoPkg's `AppPkgCreator` and, if `SIGNING_IDENTITY` is set, signs it with that `Developer ID Installer` identity. It is empty by default (unsigned); set it in a recipe override to sign.

The `.jamf` and `.intune` recipes also upload the app icon (the `.png` next to each recipe), and the Jamf recipes create the category if it does not exist yet.

## Setup

```bash
# Avoid GitHub API rate limits
defaults write com.github.autopkg GITHUB_TOKEN "ghp_..."

# Jamf Pro (for .jamf recipes)
autopkg repo-add grahampugh/jamf-upload
defaults write com.github.autopkg JSS_URL "https://yourorg.jamfcloud.com"
defaults write com.github.autopkg CLIENT_ID "..."
defaults write com.github.autopkg CLIENT_SECRET "..."

# Microsoft Intune (for .intune recipes)
autopkg repo-add almenscorner/intune-uploader
/usr/local/autopkg/python -m pip install -r ~/Library/AutoPkg/RecipeRepos/com.github.almenscorner.intune-uploader/IntuneUploader/requirements.txt
defaults write com.github.autopkg CLIENT_ID "..."
defaults write com.github.autopkg CLIENT_SECRET "..."
defaults write com.github.autopkg TENANT_ID "..."
```

Jamf Pro and Intune both read `CLIENT_ID` and `CLIENT_SECRET`, so the two blocks above overwrite each other if you run both from one machine. Put each service's credentials in its own recipe overrides, or keep two preference files and pick one per run with `autopkg run --prefs ~/Library/Preferences/com.github.autopkg.intune.plist ...`.

Munki recipes need the Munki tools installed (`makepkginfo`) and `MUNKI_REPO` set. If you remove an item from the repo by hand and want to re-import the same version, delete `catalogs/all` before running the recipe: Munki 7.4.1's `makecatalogs` does not rewrite `all` when it empties out, and `MunkiImporter` reads that catalog to decide an item already exists.

## Run

```bash
autopkg make-override StashVideo.munki.recipe.yaml   # recommended: pin trust info
autopkg run -v StashVideo.munki
autopkg run -v BonjourView.jamf
autopkg run -v BonjourView.intune
```

## Override inputs

Set these in a recipe override to change where and how an app lands. Defaults are the same for all three apps unless noted.

| Recipes | Input | Default | What it does |
|---------|-------|---------|--------------|
| `.munki` | `MUNKI_CATALOG` | `testing` | Catalog the item is imported into |
| `.munki` | `MUNKI_REPO_SUBDIR` | `apps/<NAME>` | Folder inside the repo for the pkg and pkginfo |
| `.munki` | `pkginfo` | per app | Any pkginfo key (category, description, `minimum_os_version`, ...) |
| `.jamf` | `CATEGORY` | `Utilities` | Jamf Pro category for the package; created if missing |
| `.intune` | `CATEGORY` | `Productivity` (DisplayHelp: `Business`) | One Intune app category; created if missing |
| `.intune` | `DISPLAY_NAME`, `PUBLISHER`, `DESCRIPTION` | per app | Text shown in the Company Portal |
| `.intune` | `MINIMUM_OS` | `v14_0` | Intune macOS version key |
| `BonjourView.pkg` | `SIGNING_IDENTITY` | empty | Developer ID Installer identity used to sign the built pkg |

## DisplayHelp notes

- Requires macOS 14 or later.
- The app updates itself and is also distributed through Homebrew, so the Munki pkginfo detects the installed version from the app bundle, not the package receipt. A copy that is already current or newer is left alone however it was installed.
- Installs a login agent and the DisplayHelp Updater helper. Deploy the `DisplayHelp-BackgroundItems.mobileconfig` published with each release so standard users are not prompted to approve them.

## BonjourView notes

- Requires macOS 14 or later.
- Releases ship a zipped app, so the `.pkg` recipe wraps it in a package. The Munki pkginfo detects the installed version from the app bundle, so a copy dragged in from the release dmg counts as installed.
- The bundle identifier and version are read from the downloaded app, so the child recipes follow whatever the release carries.

## Stash Video notes

- Requires macOS 14 or later.
- The app updates itself (Settings > Updates) and is also distributed through Homebrew, so the Munki pkginfo detects the installed version from the app bundle, not the package receipt.
- The download recipe unpacks the pkg and reads the bundle identifier and version from `Stash Video.app` inside it. Stash Video 2.0 moves from `com.ayala.solutions.yt-dlp-gui-Macos` to `com.ayalasolutions.stashvideo`, and the Munki and Intune recipes pick up whichever the release ships without an override.
- The installer also places `yt-dlp` and `ffmpeg` symlinks in `/usr/local/bin`. Each release also publishes a matching `StashVideo-Uninstaller-<version>.pkg`.
- A configuration profile that pre-approves the app's background helper is published with each release as `StashVideo-BackgroundItems.mobileconfig`. Deploy it alongside the package if you do not want users prompted for Background Items.
