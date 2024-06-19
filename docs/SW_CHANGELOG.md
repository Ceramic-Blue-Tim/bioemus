# Software Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- 
### Added
### Changed
### Fixed
### Removed 
-->

## [0.2.0] - 11 Mar 2024
### Added
- Select save/send format for spikes/waves from swconfig.json
- Debug flag for ZeroMQ recv/send timestamping of ext_stim/spikes/waves
- Debug flag to fix seeds of noise generator
- Make options to build debug executable with added flags
- Multiple waves monitoring
### Changed
- Simplified build scripts
- Injected stimulation current coding to sfi32
### Fixed
- File creation even if save disabled for local spikes/waves storage
- CSV header in binary saving was removed

## [0.1.0] - 10 Oct 2023
### Added
- Initial version released
