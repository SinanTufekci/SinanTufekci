"""The profile's header: the name and what I do, and beside it the chain it names, firmware to PCB to
control. A microcontroller sends pulses along copper traces to a driver and on to a two-link arm, and
feedback comes back from the arm; the arm's pen draws a cycloidal disc's profile among its ring pins
(inverse kinematics, frame by frame, so the pen sits on the line it draws). Then the arm steps aside
and the disc it drew turns as a cycloidal drive turns: its centre goes round the ring's on the input's
eccentric while the disc turns back, a ninth as fast, touching every pin all the way. It fades, the arm
comes back, and draws it again.

usage: python assets/header.py assets/header.svg   (Python 3.10+, nothing else needed)"""

import math
import sys
from itertools import pairwise
from pathlib import Path

W, H = 1400, 300
ACCENT = "#d97757"
FEEDBACK = "#6cb4ff"
SANS = "'Segoe UI', system-ui, -apple-system, 'Helvetica Neue', Arial, sans-serif"
MONO = "ui-monospace, 'Cascadia Mono', 'SF Mono', Menlo, Consolas, monospace"

LOOP = 14.0         # seconds
DRAW = 0.50         # the pen at work, from the start
ASIDE = 0.56        # the arm stepped aside by then...
BACK = 0.86         # ...and on its way back from then
SPIN = (0.50, 0.84)  # the disc turning
GONE = 0.92         # ...and faded out by then
STEPS = 360         # pen positions along the profile
TURNS = 2           # the input's turns while the disc turns

PINS, ECC, ROLLER = 10, 0.08, 0.13  # ring pins, eccentricity and pin radius, of the ring's radius
RADIUS = 76.0
BASE = (1196.0, 284.0)    # the arm's shoulder
L1, L2 = 136.0, 126.0     # its links
CENTRE = (1186.0, 120.0)  # the disc's centre as drawn
RING = (CENTRE[0] - ECC * RADIUS, CENTRE[1])  # the ring's: off by the eccentricity, every pin touches
REST = (1334.0, 68.0)     # where the pen waits while the disc turns: the arm up, clear of it, in frame


def cycloid(samples: int = 4000):
    """The disc's profile about its centre, in units of the ring's radius (PINS - 1 lobes)."""
    points = []
    for k in range(samples):
        t = 2 * math.pi * k / samples
        psi = math.atan2(math.sin((1 - PINS) * t), 1.0 / (ECC * PINS) - math.cos((1 - PINS) * t))
        x = math.cos(t) - ROLLER * math.cos(t + psi) - ECC * math.cos(PINS * t)
        y = -math.sin(t) + ROLLER * math.sin(t + psi) + ECC * math.sin(PINS * t)
        points.append((x, y))
    return points


def evenly(points, count):
    """count points along a closed curve, as far apart as one another along it."""
    loop = points + points[:1]
    lengths = [0.0]
    for (x0, y0), (x1, y1) in pairwise(loop):
        lengths.append(lengths[-1] + math.hypot(x1 - x0, y1 - y0))
    total, out, j = lengths[-1], [], 0
    for k in range(count + 1):
        want = total * k / count
        while j < len(lengths) - 2 and lengths[j + 1] < want:
            j += 1
        span = lengths[j + 1] - lengths[j] or 1.0
        t = (want - lengths[j]) / span
        (x0, y0), (x1, y1) = loop[j], loop[j + 1]
        out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    return out


def solve(x, y):
    """Shoulder and elbow angles, degrees, reaching (x, y) from BASE, the elbow out to the right."""
    dx, dy = x - BASE[0], y - BASE[1]
    d = min(math.hypot(dx, dy), L1 + L2 - 1e-6)
    elbow = -math.acos(max(-1.0, min(1.0, (d * d - L1 * L1 - L2 * L2) / (2 * L1 * L2))))
    shoulder = math.atan2(dy, dx) - math.atan2(L2 * math.sin(elbow), L1 + L2 * math.cos(elbow))
    return math.degrees(shoulder), math.degrees(elbow)


def unwrap(angles):
    out = [angles[0]]
    for a in angles[1:]:
        while a - out[-1] > 180:
            a -= 360
        while a - out[-1] < -180:
            a += 360
        out.append(a)
    return out


def near(angle, to):
    while angle - to > 180:
        angle -= 360
    while angle - to < -180:
        angle += 360
    return angle


def anim(attribute, values, times, kind="animate", extra=""):
    v = ";".join(values)
    k = ";".join(f"{t:.5f}".rstrip("0").rstrip(".") if t else "0" for t in times)
    tag = "animateTransform" if kind != "animate" else "animate"
    typed = f' type="{kind}"' if kind != "animate" else ""
    return (f'<{tag} attributeName="{attribute}"{typed} values="{v}" keyTimes="{k}" dur="{LOOP:g}s" '
            f'repeatCount="indefinite"{extra}/>')


def board():
    """The microcontroller, a crystal, an LED, passives, the driver, and the traces with their pulses:
    commands out to the arm, feedback back from it."""
    out = []
    mx, my, size = 902, 148, 80
    dx, dy = 1066, 214
    traces, pulses = [], []
    for k in range(4):  # the microcontroller to the driver
        y0, y1 = my + 18 + k * 14, dy + 7 + k * 8
        path = f"M{mx + size} {y0} H{mx + size + 22 + k * 6} L{dx - 24 - (3 - k) * 4} {y1} H{dx - 6}"
        traces.append((path, ACCENT))
        pulses.append((path, 1.5, k * 0.37, "#ffb08f"))
    for k in range(3):  # the driver to the arm
        y0 = dy + 9 + k * 9
        path = f"M{dx + 40} {y0} H{BASE[0] - 72 + k * 4} L{BASE[0] - 44 + k * 6} {BASE[1] - 2}"
        traces.append((path, ACCENT))
        pulses.append((path, 1.1, 0.25 + k * 0.4, "#ffb08f"))
    feedback = f"M{BASE[0] - 54} {BASE[1] + 6} H{mx + 40} V{my + size + 8}"  # the encoder, back to the microcontroller
    traces.append((feedback, FEEDBACK))
    pulses += [(feedback, 1.8, 0.0, "#a8d4ff"), (feedback, 1.8, 0.9, "#a8d4ff")]
    for k in range(3):  # in from the left: power and a bus
        y0 = my + 24 + k * 18
        path = f"M{mx - 68} {y0 + 40} H{mx - 44} L{mx - 22} {y0} H{mx - 6}"
        traces.append((path, ACCENT))
        pulses.append((path, 1.4, 0.5 + k * 0.45, "#ffb08f"))
    for path, colour in traces:
        out.append(f'<path d="{path}" fill="none" stroke="{colour}" stroke-opacity="0.26" stroke-width="2.4" '
                   f'stroke-linecap="round" stroke-linejoin="round"/>')
    for x, y in ((mx - 68, my + 64), (mx - 68, my + 82), (mx - 68, my + 100), (BASE[0] - 72, dy + 9),
                 (mx + 40, my + size + 8)):
        out.append(f'<circle cx="{x}" cy="{y}" r="4.2" fill="#0d1320" stroke="#b07a62" stroke-width="2"/>')
    # Passives on the lines: a capacitor and two resistors.
    for x, y in ((mx + size + 34, my + 18), (mx - 40, my + 37), (BASE[0] - 98, dy + 9)):
        out.append(f'<rect x="{x - 7}" y="{y - 3.5}" width="14" height="7" rx="1.5" fill="#3a3140"/>'
                   f'<rect x="{x - 7}" y="{y - 3.5}" width="3.5" height="7" fill="#c9cfd6"/>'
                   f'<rect x="{x + 3.5}" y="{y - 3.5}" width="3.5" height="7" fill="#c9cfd6"/>')
    for path, dur, begin, colour in pulses:
        out.append(f'<circle r="3.2" fill="{colour}" opacity="0"><animateMotion path="{path}" dur="{dur}s" '
                   f'begin="-{begin:.2f}s" repeatCount="indefinite"/><animate attributeName="opacity" '
                   f'values="0;1;1;0" keyTimes="0;0.1;0.85;1" dur="{dur}s" begin="-{begin:.2f}s" '
                   f'repeatCount="indefinite"/></circle>')
    # The microcontroller: a QFP, its pin 1 marked; nothing written on it.
    for k in range(8):
        o = 9 + k * 9
        out.append(f'<rect x="{mx - 6}" y="{my + o}" width="6" height="3.5" rx="1" fill="#8a929c"/>'
                   f'<rect x="{mx + size}" y="{my + o}" width="6" height="3.5" rx="1" fill="#8a929c"/>'
                   f'<rect x="{mx + o}" y="{my - 6}" width="3.5" height="6" rx="1" fill="#8a929c"/>'
                   f'<rect x="{mx + o}" y="{my + size}" width="3.5" height="6" rx="1" fill="#8a929c"/>')
    out.append(f'<rect x="{mx}" y="{my}" width="{size}" height="{size}" rx="5" fill="url(#chip)" stroke="#3a4352" '
               f'stroke-width="1.5"/><rect x="{mx + 8}" y="{my + 8}" width="{size - 16}" height="{size - 16}" rx="3" '
               f'fill="none" stroke="#ffffff" stroke-opacity="0.04"/><circle cx="{mx + 12}" cy="{my + 12}" r="3" '
               f'fill="#0b0f15" stroke="#3a4352"/>')
    # A crystal beside it, and the LED that blinks.
    out.append(f'<rect x="{mx + 12}" y="{my + size + 16}" width="26" height="12" rx="6" fill="url(#metal)" '
               f'stroke="#5a636e"/>')
    out.append(f'<rect x="{mx - 26}" y="{my + 4}" width="10" height="6" rx="1.5" fill="#1f3a2b"/>'
               f'<circle cx="{mx - 21}" cy="{my + 7}" r="9" fill="url(#led)">'
               f'<animate attributeName="opacity" values="1;0.15;1" dur="1.2s" repeatCount="indefinite"/></circle>')
    # The driver: an SOIC, pin 1 notched.
    for k in range(4):
        out.append(f'<rect x="{dx - 6}" y="{dy + 5 + k * 9}" width="6" height="3.5" rx="1" fill="#8a929c"/>'
                   f'<rect x="{dx + 34}" y="{dy + 5 + k * 9}" width="6" height="3.5" rx="1" fill="#8a929c"/>')
    out.append(f'<rect x="{dx}" y="{dy}" width="34" height="42" rx="3" fill="url(#chip)" stroke="#3a4352" '
               f'stroke-width="1.5"/><path d="M{dx + 12} {dy} a5 5 0 0 0 10 0" fill="#0b0f15" stroke="#3a4352"/>')
    return "".join(out)


def link(length: float, width: float, gradient: str) -> str:
    return (f'<rect x="{-width / 2}" y="{-width / 2}" width="{length + width}" height="{width}" rx="{width / 2}" '
            f'fill="url(#{gradient})" stroke="#8a929c" stroke-width="1.5"/>'
            f'<line x1="{width * 0.2}" y1="{-width * 0.18}" x2="{length - width * 0.2}" y2="{-width * 0.18}" '
            f'stroke="#ffffff" stroke-opacity="0.35" stroke-width="2" stroke-linecap="round"/>')


def joint(r: float) -> str:
    bolts = "".join(f'<circle cx="{r * 0.55 * math.cos(a):.1f}" cy="{r * 0.55 * math.sin(a):.1f}" r="1.6" '
                    f'fill="#5a636e"/>' for a in (0.5, 0.5 + 2.094, 0.5 + 4.189))
    return (f'<circle r="{r}" fill="url(#cap)" stroke="#d6dbe0" stroke-width="2.5"/><circle r="{r * 0.28}" '
            f'fill="#3a4352"/>{bolts}')


def main(out: str) -> None:
    local = [(x * RADIUS, y * RADIUS) for x, y in cycloid()]
    pen = evenly([(CENTRE[0] + x, CENTRE[1] + y) for x, y in local], STEPS)
    length = sum(math.hypot(x1 - x0, y1 - y0) for (x0, y0), (x1, y1) in pairwise(pen))

    # The arm: along the profile, aside, waiting, back to where it starts.
    shoulder, elbow = zip(*(solve(x, y) for x, y in pen))
    shoulder, elbow = unwrap(list(shoulder)), unwrap(list(elbow))
    rest = solve(*REST)
    rest = (near(rest[0], shoulder[-1]), near(rest[1], elbow[-1]))
    times = [DRAW * k / STEPS for k in range(STEPS + 1)] + [ASIDE, BACK, 1.0]
    shoulder += [rest[0], rest[0], shoulder[0]]
    elbow += [rest[1], rest[1], elbow[0]]
    turn_1 = anim("transform", [f"{a:.2f}" for a in shoulder], times, "rotate")
    turn_2 = anim("transform", [f"{a:.2f}" for a in elbow], times, "rotate")
    glow = anim("opacity", ["1", "1", "0.25", "0.25", "1"], [0, DRAW, ASIDE, BACK, 1.0])

    # The line the pen draws, shown till the disc takes its place.
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pen) + " Z"
    line = (f'<path d="{d}" fill="none" stroke="{ACCENT}" stroke-width="3" stroke-linejoin="round" '
            f'stroke-dasharray="{length:.1f} {length:.1f}" stroke-dashoffset="{length:.1f}" filter="url(#soft)">'
            + anim("stroke-dashoffset", [f"{length:.1f}", "0", "0"], [0, DRAW, 1.0])
            + f'<animate attributeName="opacity" values="1;0" keyTimes="0;{DRAW}" calcMode="discrete" '
              f'dur="{LOOP:g}s" repeatCount="indefinite"/></path>')

    # The disc, turning: its centre round the ring's at the eccentricity, the disc back a ninth as fast.
    frames = 120
    phases = [2 * math.pi * TURNS * k / frames for k in range(frames + 1)]
    spin_times = [SPIN[0] + (SPIN[1] - SPIN[0]) * k / frames for k in range(frames + 1)]
    e = ECC * RADIUS
    centres = [f"{RING[0] + e * math.cos(p):.2f} {RING[1] + e * math.sin(p):.2f}" for p in phases]
    turns = [f"{-math.degrees(p) / (PINS - 1):.2f}" for p in phases]
    move = anim("transform", [centres[0]] + centres + [centres[-1]], [0] + spin_times + [1.0], "translate")
    turn = anim("transform", [turns[0]] + turns + [turns[-1]], [0] + spin_times + [1.0], "rotate")
    shape = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in evenly(local, 360)) + " Z"
    holes = "".join(f'<circle cx="{RADIUS * 0.5 * math.cos(2 * math.pi * k / 5 + 0.3):.1f}" '
                    f'cy="{RADIUS * 0.5 * math.sin(2 * math.pi * k / 5 + 0.3):.1f}" r="{RADIUS * 0.11:.1f}" '
                    f'fill="#0d1320" stroke="{ACCENT}" stroke-opacity="0.7" stroke-width="2"/>' for k in range(5))
    disc = ('<g opacity="0">'
            + f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{SPIN[0]};{SPIN[0] + 0.0005};{SPIN[1]};{GONE};1" '
              f'calcMode="linear" dur="{LOOP:g}s" repeatCount="indefinite"/>'
            + f'<g>{move}<g>{turn}<path d="{shape}" fill="{ACCENT}" fill-opacity="0.16" stroke="{ACCENT}" '
              f'stroke-width="3" stroke-linejoin="round" filter="url(#soft)"/>{holes}'
              f'<circle r="{RADIUS * 0.17:.1f}" fill="#0d1320" stroke="{ACCENT}" stroke-width="2"/></g></g></g>')
    # The input: a shaft in the ring's centre, turning nine times as fast as the disc.
    shaft = (f'<g transform="translate({RING[0]:.1f} {RING[1]:.1f})"><g>'
             + anim("transform", ["0", "0"] + [f"{math.degrees(p):.1f}" for p in phases] + [f"{360 * TURNS}"],
                    [0, SPIN[0]] + spin_times + [1.0], "rotate")
             + f'<circle r="{RADIUS * 0.1:.1f}" fill="#2a3240" stroke="#9aa3ad" stroke-width="2"/>'
               f'<line x1="0" y1="0" x2="{RADIUS * 0.1:.1f}" y2="0" stroke="#e6e9ec" stroke-width="2.5" '
               f'stroke-linecap="round"/></g></g>')
    pins = (f'<circle cx="{RING[0]:.1f}" cy="{RING[1]}" r="{RADIUS:.1f}" fill="none" stroke="#ffffff" '
            f'stroke-opacity="0.06"/>' + "".join(
                f'<circle cx="{RING[0] + RADIUS * math.cos(2 * math.pi * k / PINS):.1f}" '
                f'cy="{RING[1] + RADIUS * math.sin(2 * math.pi * k / PINS):.1f}" r="{RADIUS * ROLLER:.1f}" '
                f'fill="#151b26" stroke="#8a929c" stroke-opacity="0.7" stroke-width="2"/>' for k in range(PINS)))

    arm = f'''<g transform="translate({BASE[0]} {BASE[1]})">
<path d="M-56 16 L-42 -4 H42 L56 16 Z" fill="#232a36"/><ellipse cx="0" cy="-4" rx="40" ry="7" fill="#2f3846"/>
<g>{turn_1}
{link(L1, 26, "upper")}
<g transform="translate({L1} 0)"><g>{turn_2}
{link(L2, 20, "fore")}
<circle cx="{L2}" cy="0" r="18" fill="url(#tip)">{glow}</circle>
<circle cx="{L2}" cy="0" r="5.5" fill="{ACCENT}" stroke="#ffd2bf" stroke-width="2"/>
</g>{joint(13)}</g>
</g>
{joint(18)}
</g>'''

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
<title id="t">Sinan Tüfekci</title>
<desc id="d">Sinan Tüfekci, mechatronics engineer building robots end to end, from firmware and PCBs to control and the tools around them. Beside the name, a microcontroller sends pulses along copper traces to a driver and a two-link robot arm, with feedback coming back; the arm's pen draws a cycloidal disc among its ring pins, then the disc turns as a cycloidal drive does.</desc>
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0d1320"/><stop offset="1" stop-color="#080b12"/></linearGradient>
<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{ACCENT}" stop-opacity="0.22"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/></radialGradient>
<radialGradient id="tip" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#ffb08f" stop-opacity="0.85"/><stop offset="1" stop-color="#ffb08f" stop-opacity="0"/></radialGradient>
<radialGradient id="led" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#7ee0a1"/><stop offset="0.35" stop-color="#4cc38a" stop-opacity="0.7"/><stop offset="1" stop-color="#4cc38a" stop-opacity="0"/></radialGradient>
<linearGradient id="chip" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1e2532"/><stop offset="1" stop-color="#11161f"/></linearGradient>
<linearGradient id="metal" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d6dbe0"/><stop offset="1" stop-color="#7d8590"/></linearGradient>
<linearGradient id="upper" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e3e7eb"/><stop offset="1" stop-color="#a7afb9"/></linearGradient>
<linearGradient id="fore" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f2f4f6"/><stop offset="1" stop-color="#b9c0c8"/></linearGradient>
<radialGradient id="cap" cx="0.4" cy="0.35" r="0.7"><stop offset="0" stop-color="#c9cfd6"/><stop offset="1" stop-color="#7d8590"/></radialGradient>
<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#ffffff" stroke-opacity="0.025"/></pattern>
<filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="{W}" height="{H}" rx="18" fill="url(#bg)"/>
<rect width="{W}" height="{H}" rx="18" fill="url(#grid)"/>
<circle cx="{CENTRE[0]}" cy="{CENTRE[1] + 30}" r="240" fill="url(#glow)"/>
<text x="90" y="128" font-family="{SANS}" font-size="72" font-weight="700" fill="#e6e3dd">Sinan Tüfekci</text>
<text x="92" y="182" font-family="{SANS}" font-size="32" fill="#9aa3ad">Mechatronics engineer · robots, end to end</text>
<g font-family="{MONO}" font-size="24">
<text x="92" y="238"><tspan fill="{ACCENT}">firmware</tspan><tspan fill="#56606c"> → </tspan><tspan fill="{ACCENT}">PCB</tspan><tspan fill="#56606c"> → </tspan><tspan fill="{ACCENT}">control</tspan><tspan fill="#56606c"> → </tspan><tspan fill="{ACCENT}">the tools around them</tspan></text>
</g>
{board()}
{pins}
{shaft}
{line}
{disc}
{arm}
</svg>
'''
    Path(out).write_text(svg, encoding="utf-8", newline="\n")
    print(len(svg), "bytes")


main(sys.argv[1])
