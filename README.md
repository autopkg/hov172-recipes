# hov172 AutoPkg recipes

AutoPkg recipes for apps published by Ayala Solutions. Add the repo once and every app in it becomes available:

```bash
autopkg repo-add hov172/autopkg-recipes
```

That short form is all AutoPkg needs: it expands to `https://github.com/hov172/autopkg-recipes` on its own, and the repo is public, so no GitHub account is required.

## Apps

| App | Recipes | Source |
|-----|---------|--------|
| Stash Video | `StashVideo.download`, `StashVideo.munki`, `StashVideo.jamf`, `StashVideo.intune` | [hov172/StashVideos](https://github.com/hov172/StashVideos) |
| DisplayHelp | `DisplayHelp.download`, `DisplayHelp.munki`, `DisplayHelp.jamf`, `DisplayHelp.intune` | [hov172/DisplayHelp](https://github.com/hov172/DisplayHelp) |
| BonjourView | `BonjourView.download`, `BonjourView.pkg`, `BonjourView.munki`, `BonjourView.jamf`, `BonjourView.intune` | [hov172/BonjourView](https://github.com/hov172/BonjourView) |

Every download recipe fetches the vendor's signed and notarized artifact straight from GitHub Releases and fails if the Developer ID signature does not match Team ID `N859JA9UCJ`. Stash Video and DisplayHelp ship flat packages, which are deployed as is. BonjourView ships a zipped app bundle, so its `.pkg` recipe wraps the verified app in a package with AutoPkg's `AppPkgCreator` and, if `SIGNING_IDENTITY` is set, signs it with that `Developer ID Installer` identity. It is empty by default (unsigned); set it in a recipe override to sign.

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

Munki recipes need the Munki tools installed (`makepkginfo`) and `MUNKI_REPO` set. If you remove an item from the repo by hand and want to re-import the same version, delete `catalogs/all` before running the recipe: Munki 7.4.1's `makecatalogs` does not rewrite `all` when it empties out, and `MunkiImporter` reads that catalog to decide an item already exists.

## Run

```bash
autopkg make-override StashVideo.munki.recipe.yaml   # recommended: pin trust info
autopkg run -v StashVideo.munki
autopkg run -v BonjourView.jamf
autopkg run -v BonjourView.intune
```

## DisplayHelp notes

- Requires macOS 14 or later.
- The app updates itself and is also distributed through Homebrew, so the Munki pkginfo detects the installed version from the app bundle, not the package receipt. A copy that is already current or newer is left alone however it was installed.
- Installs a login agent and the DisplayHelp Updater helper. Deploy the `DisplayHelp-BackgroundItems.mobileconfig` published with each release so standard users are not prompted to approve them.

## BonjourView notes

- Requires macOS 14 or later.
- Releases ship a zipped app, so the `.pkg` recipe wraps it in a package. The Munki pkginfo detects the installed version from the app bundle, so a copy dragged in from the release dmg counts as installed.

## Stash Video notes

- Requires macOS 14 or later.
- The app updates itself (Settings > Updates) and is also distributed through Homebrew, so the Munki pkginfo detects the installed version from the app bundle, not the package receipt.
- The installer also places `yt-dlp` and `ffmpeg` symlinks in `/usr/local/bin`.
- A configuration profile that pre-approves the app's background helper is published with each release as `StashVideo-BackgroundItems.mobileconfig`. Deploy it alongside the package if you do not want users prompted for Background Items.
