# NEON SNAKE - Kivy Android project

This project is a Kivy port of the supplied Pygame game.

## Files
- `main.py`: Kivy version of the game.
- `buildozer.spec`: Android app configuration.
- `.github/workflows/build-apk.yml`: optional cloud build workflow.

## Build note
Kivy's official Android packaging guide recommends Buildozer. Buildozer itself runs on Linux/macOS (or Windows through WSL), so the included GitHub Actions workflow can build in a cloud Linux runner after the project is placed in a GitHub repository.

The workflow is manually started from the repository's Actions tab. When it finishes, download the `NEON-SNAKE-APK` artifact.

The first Android build can take a while because the Android SDK/NDK and Python dependencies need to be downloaded.

## Gameplay port
Includes the original game's menu, swipe movement, food, coins and saved wallet, score/best record, three levels, moving enemy, obstacles, pause/resume, restart and home screens. Save data is written to the app's private data directory.
