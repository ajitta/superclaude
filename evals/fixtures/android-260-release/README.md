# Tally for Android

Build: `./gradlew assembleRelease`.

Releases are cut from `main`: set `versionName` and `versionCode` in
`app/build.gradle`, add a CHANGELOG entry, and tag `vX.Y.Z`. CI builds the
bundle and uploads it to the Google Play production track.
