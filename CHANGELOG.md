# Changelog

Pushing a `vX.Y.Z` tag runs `.github/workflows/release.yml`, which builds, tests and
attaches `UBER256.COM` to a GitHub release using that version's section below.

## [1.0.0] - 2026-10-07

First standalone release (split out of [uber40k-dos-demo](https://github.com/djayuffe/uber40k-dos-demo)).

- 196-byte intro (60 bytes under the 256-byte limit): a seamless rainbow palette built
  from three phase-shifted triangle waves, and two ring families whose centres orbit
  each other, folded into a moire.
- Clean exit: Esc restores text mode and the keyboard interrupt mask.
- `build.sh` enforces the 256-byte limit; `tests/run_tests.sh` runs the real binary in an
  emulated 16-bit CPU; CI and tag-driven releases on GitHub Actions.
