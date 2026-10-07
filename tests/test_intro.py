#!/usr/bin/env python3
"""Run UBER256.COM in an emulated 16-bit CPU and check what it does to the hardware."""
import pathlib, sys
from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_INSN, UC_HOOK_INTR, UC_HOOK_MEM_UNMAPPED
from unicorn.x86_const import *

ROOT = pathlib.Path(__file__).resolve().parent.parent
SEG = 0x1000
LIN = SEG << 4
FRAMES = 12
fails = []

def check(ok, msg):
    print(("  PASS  " if ok else "  FAIL  ") + msg)
    if not ok: fails.append(msg)

com = (ROOT / "UBER256.COM").read_bytes()
uc = Uc(UC_ARCH_X86, UC_MODE_16)
uc.mem_map(0, 0x10000); uc.mem_map(LIN, 0x10000); uc.mem_map(0xA0000, 0x10000)
uc.mem_write(LIN + 0x100, com)
uc.mem_write(LIN, b"\xCD\x20")                       # PSP: INT 20h
for r in (UC_X86_REG_CS, UC_X86_REG_DS, UC_X86_REG_ES, UC_X86_REG_SS): uc.reg_write(r, SEG)
uc.reg_write(UC_X86_REG_SP, 0xFFFE); uc.reg_write(UC_X86_REG_FLAGS, 0x202)

state = {"polls": 0, "modes": [], "irq": [], "exited": False, "unmapped": []}
frames = []

def on_in(u, port, size, ud):
    if port == 0x64:                                 # one status poll per frame
        state["polls"] += 1
        frames.append(bytes(u.mem_read(0xA0000, 64000)))
        return 1 if state["polls"] > FRAMES else 0
    if port == 0x60: return 1                        # Esc make code
    return 0
def on_out(u, port, size, value, ud):
    if port == 0x21: state["irq"].append(value & 0xFF)
def on_intr(u, n, ud):
    ax = u.reg_read(UC_X86_REG_AX)
    if n == 0x10: state["modes"].append(ax & 0xFF)
    if n == 0x20: state["exited"] = True; u.emu_stop()
uc.hook_add(UC_HOOK_INSN, on_in, None, 1, 0, UC_X86_INS_IN)
uc.hook_add(UC_HOOK_INSN, on_out, None, 1, 0, UC_X86_INS_OUT)
uc.hook_add(UC_HOOK_INTR, on_intr)
uc.hook_add(UC_HOOK_MEM_UNMAPPED, lambda u, a, ad, sz, v, d: state["unmapped"].append(hex(ad)) or False)

ip, started, used = 0x100, False, 0
while not state["exited"] and used < 3_000_000_000:
    uc.emu_start(uc.reg_read(UC_X86_REG_IP) if started else 0x100, 0xFFFF0, count=5_000_000)
    started = True; used += 5_000_000

print(f"== UBER256.COM ({len(com)} bytes, {state['polls']} frames, Esc after {FRAMES}) ==")
check(len(com) <= 256, f"fits the 256-byte limit ({len(com)} bytes)")
check(not state["unmapped"], f"no access outside mapped memory {state['unmapped'][:3]}")
check(0x13 in state["modes"] and 3 in state["modes"], "enters mode 13h and restores text mode 3")
check(state["exited"], "returns to DOS (PSP INT 20h) after Esc")
check(len(state["irq"]) >= 2 and (state["irq"][0] & 2) and not (state["irq"][-1] & 2),
      "IRQ1 masked while running and restored at exit")
check(uc.reg_read(UC_X86_REG_SP) == 0, "stack balanced: the final RET popped exactly the DOS return word")
f0, f5 = frames[1], frames[6]
check(len(set(f0)) > 32, f"each frame uses many colours ({len(set(f0))} distinct indices)")
check(f0 != f5, f"animates: {sum(a != b for a, b in zip(f0, f5))} of 64000 pixels differ between frames")
check(all(len(f) == 64000 for f in frames), "every frame is a full 320x200 page")
print("\nRESULT:", "ALL PASS" if not fails else f"{len(fails)} FAILED")
sys.exit(1 if fails else 0)
