# UBER256

**A 256-byte DOS intro: rainbow moire in 196 bytes of hand-written x86 assembly.**

[![CI](https://github.com/djayuffe/uber256-dos-intro/actions/workflows/ci.yml/badge.svg)](https://github.com/djayuffe/uber256-dos-intro/actions/workflows/ci.yml)

![UBER256 running in DOSBox](screenshot.jpg)

A single `.COM` file, no assets, no libraries. It switches to VGA mode 13h, builds its own
256-colour palette, and draws two families of concentric rings whose centres orbit each
other, so the interference pattern (a moire) swirls while the colours roll through the
palette. Press **Esc** to exit cleanly back to DOS.

| | |
|---|---|
| Size | **196 bytes** (limit 256, enforced by `build.sh`) |
| CPU | 386+ (real mode) |
| Video | VGA mode 13h, 320x200x256 |
| Audio | none |

Its big brother is [uber40k-dos-demo](https://github.com/djayuffe/uber40k-dos-demo):
a full 18-scene show with a 3D engine and Sound Blaster FM music.

## Run it

Download `UBER256.COM` from the [latest release](../../releases/latest) and run it in
DOSBox (`mount c .`, `c:`, `UBER256.COM`), or build it:

```sh
./build.sh        # NASM build + 256-byte gate
./run-dosbox.sh   # run it in DOSBox
```

Needs [NASM](https://www.nasm.us/) and [DOSBox](https://www.dosbox.com/)
(macOS: `brew install nasm` and `brew install --cask dosbox`).

## How it works

- **Palette**: `tri(i)` is a triangle wave 0..63. The red, green and blue channels use
  `tri(i)`, `tri(i+85)` and `tri(i+170)`, which gives a seamless rainbow loop with no
  table and no sine.
- **Rings**: for each pixel, `r^2 = dx^2 + dy^2` from a centre, `>>5`, folded through
  `tri` into a ring profile. Squared distance replaces a square root.
- **Moire**: a second ring family centred on a point that orbits the first (the orbit is
  two `tri` waves a quarter turn apart: a circle without a sine table). The two profiles
  are added and stretched over the palette; the frame counter then rolls the colours.
- **Pixels**: `STOSB` straight into `A000:0000`; the loop counters double as coordinates.
- **Exit**: Esc is read from the 8042 keyboard controller (`64h`/`60h`). IRQ1 is masked at
  the PIC meanwhile, because the BIOS handler would otherwise drain the controller first
  and Esc would almost never be seen; the mask is restored on exit.

## Testing

`tests/run_tests.sh` runs the real binary in an emulated 16-bit CPU (Unicorn) and checks
the size limit, that it enters mode 13h and restores text mode, that every frame is a full
page and animates, that IRQ1 is masked and restored, that the stack is balanced and that
it returns to DOS after Esc. CI runs it on every push; a `vX.Y.Z` tag publishes a release.

## License

MIT
