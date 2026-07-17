# Changelog

All notable changes to AI_Tutor are documented here, newest first.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## Unreleased

### Fixed
- Fixed a crash in the CLI dev menu: any option that reads student progress or profile data now shows a clear "storage not initialized/unreadable" message instead of crashing with a stack trace when the underlying JSON files are missing or corrupted.
