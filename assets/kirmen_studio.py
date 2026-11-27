"""Banner for Kirmen Studio in the GitHub profile README.

Draws a Type-IV pressure vessel between headstock and tailstock chucks with a
±55° helical carbon-fiber weave, while a 4-axis payout carriage travels along
its rail, pivots the delivery eye at each dome turnaround and lays a glowing
active fiber band onto the rotating vessel.

Pure Python 3.10+ (stdlib only), SMIL SVG (no JS), GitHub-camo safe.

usage: python assets/kirmen_studio.py assets/kirmen-studio.svg
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

W, H = 860, 340
LOOP = 10.0  # seconds

# Vessel geometry (right column of the 860x340 card)
CY = 148.0
X_CYL_L = 486.0
X_CYL_R = 702.0
DOME_L = 48.0
R_CYL = 60.0
R_BOSS = 15.0

X_DOME_L = X_CYL_L - DOME_L  # 438
X_DOME_R = X_CYL_R + DOME_L  # 750

# Official Kirmen brand mark path (from medinsweb/public/assets/kirmen/kirmen_mark_light.svg, viewBox 0 0 1024 1024)
KIRMEN_MARK_PATH = (
    "M523.710 437.388 C523.710 460.996 537.273 482.624 558.450 493.057 "
    "C566.832 497.186 576.154 499.125 585.482 499.125 C595.116 499.125 604.661 497.098 613.284 492.734 "
    "C621.978 488.340 629.262 481.561 636.793 475.487 C647.783 466.623 658.773 457.753 669.764 448.895 "
    "C674.181 445.329 678.516 441.071 683.368 438.116 C684.790 437.253 686.452 436.612 688.132 436.612 "
    "C693.830 436.612 699.610 443.321 703.528 447.021 C731.777 473.731 752.037 507.671 765.154 544.097 "
    "C766.839 548.784 771.086 559.352 771.086 563.922 C771.086 569.684 766.199 574.243 760.513 574.243 "
    "C758.821 574.243 757.159 573.761 755.708 572.892 C753.100 571.323 750.968 568.809 748.683 566.806 "
    "C744.765 563.352 740.676 560.092 736.476 556.990 C715.006 541.142 690.705 529.306 665.934 519.619 "
    "C657.587 516.353 649.099 513.029 640.487 510.561 C640.558 515.079 640.599 519.596 640.599 524.113 "
    "C640.599 650.712 610.459 792.995 552.276 905.801 C548.199 913.707 543.946 921.520 539.500 929.227 "
    "C537.679 932.375 536.005 936.282 533.279 938.761 C531.464 940.399 529.138 941.157 526.718 941.157 "
    "C519.886 941.157 512.855 939.859 506.058 939.172 C492.295 937.785 478.526 936.399 464.763 935.013 "
    "C458.161 934.349 451.552 933.685 444.950 933.022 C441.343 932.657 437.055 932.822 433.701 931.324 "
    "C430.047 929.691 427.657 925.920 427.657 921.943 C427.657 920.674 427.909 919.411 428.356 918.231 "
    "C429.489 915.229 431.281 912.398 432.744 909.543 C435.504 904.139 438.189 898.687 440.797 893.207 "
    "C445.044 884.284 449.097 875.267 452.968 866.174 C461.098 847.077 468.464 827.658 475.149 808.009 "
    "C494.580 750.948 508.602 692.036 517.836 632.490 C522.706 601.099 526.201 569.485 528.151 537.776 "
    "C528.791 527.350 529.279 516.911 529.572 506.467 C529.602 505.322 529.590 503.971 529.572 502.526 "
    "C529.455 492.528 522.195 484.046 512.338 482.383 C510.499 482.072 508.666 481.761 506.875 481.532 "
    "C496.372 480.192 485.846 479.035 475.301 478.054 C443.100 475.047 410.763 473.607 378.426 473.607 "
    "C310.151 473.607 241.606 479.716 174.700 493.503 C154.646 497.633 134.732 502.467 115.072 508.188 "
    "C108.563 510.086 102.084 512.077 95.640 514.174 C91.981 515.361 87.769 517.546 83.880 517.546 "
    "C78.106 517.546 73.477 512.841 73.477 507.090 C73.477 501.744 74.041 496.352 74.341 491.018 "
    "C74.934 480.580 75.527 470.153 76.120 459.721 C76.655 450.270 77.190 440.830 77.730 431.378 "
    "C78.000 426.615 78.000 421.745 78.599 417.005 C78.811 415.330 79.328 413.697 80.315 412.305 "
    "C83.522 407.747 103.829 401.538 109.938 399.423 C193.432 370.581 284.017 358.945 372.123 358.945 "
    "C422.258 358.945 472.394 362.933 521.795 371.551 C516.732 336.588 506.293 297.995 489.511 266.809 "
    "C487.432 262.956 485.229 259.173 482.873 255.478 C481.458 253.246 479.689 251.096 478.556 248.700 "
    "C477.962 247.437 477.604 246.027 477.604 244.629 C477.604 238.990 482.098 234.008 487.878 234.008 "
    "C492.577 234.008 499.180 238.396 503.339 240.593 C538.718 259.232 570.503 284.919 593.459 317.897 "
    "C596.361 322.067 602.382 329.316 602.382 334.467 C602.382 336.623 601.577 338.591 600.232 340.259 "
    "C596.755 344.588 591.063 348.830 586.868 352.618 C576.812 361.712 566.756 370.799 556.699 379.892 "
    "C548.052 387.710 538.583 395.053 532.392 405.092 C526.394 414.808 523.710 426.027 523.710 437.388 Z "
    "M544.363 437.194 C544.363 427.684 547.694 418.350 553.733 411.001 C557.821 406.026 563.096 401.932 "
    "567.866 397.620 C576.348 389.954 584.830 382.283 593.318 374.611 C621.490 349.141 649.669 323.677 "
    "677.841 298.206 C712.510 266.868 747.185 235.530 781.854 204.185 C792.533 194.528 803.218 184.871 "
    "813.903 175.214 C819.812 169.869 825.522 163.907 832.048 159.313 C840.765 153.175 851.227 149.950 "
    "861.871 149.950 C890.254 149.950 913.158 173.423 913.158 201.642 C913.158 214.260 908.312 226.654 "
    "899.847 236.006 C895.494 240.811 890.131 244.640 885.097 248.694 C877.185 255.079 869.272 261.458 "
    "861.360 267.843 C834.656 289.384 807.952 310.924 781.243 332.458 C742.450 363.750 703.652 395.041 "
    "664.859 426.333 C652.547 436.260 640.241 446.187 627.934 456.114 C621.508 461.295 615.258 467.105 "
    "608.374 471.657 C601.630 476.116 593.653 478.471 585.576 478.471 C563.108 478.471 544.363 459.633 "
    "544.363 437.194 Z M399.343 582.889 C399.343 579.635 400.371 576.422 402.263 573.773 "
    "C404.671 570.395 408.043 567.476 410.874 564.439 C416.942 557.930 423.016 551.422 429.084 544.907 "
    "C438.530 534.786 447.969 524.659 457.415 514.532 C462.390 509.199 467.195 503.513 472.488 498.525 "
    "C480.365 499.254 488.236 500.082 496.090 501.010 C500.390 501.515 504.795 501.891 509.019 502.743 "
    "C508.702 514.967 508.561 527.379 507.286 539.538 C487.843 552.655 468.399 565.772 448.956 578.883 "
    "C442.982 582.913 437.008 586.948 431.034 590.972 C428.156 592.916 425.330 595.266 422.241 596.858 "
    "C419.967 598.027 417.453 598.597 414.904 598.597 C406.404 598.597 399.343 591.330 399.343 582.889 Z"
)


def vessel_radius(x: float) -> float:
    """Smooth Type-IV pressure-vessel radius profile r(x)."""
    if X_CYL_L <= x <= X_CYL_R:
        return R_CYL
    if x < X_CYL_L:
        u = min(1.0, max(0.0, (X_CYL_L - x) / DOME_L))
    else:
        u = min(1.0, max(0.0, (x - X_CYL_R) / DOME_L))
    # Elliptical dome tapering smoothly to the polar boss radius
    r = R_BOSS + (R_CYL - R_BOSS) * math.sqrt(max(0.0, 1.0 - u * u))
    return r


def vessel_outline_path() -> str:
    """Closed SVG path for the pressure vessel body + domes."""
    top_pts: list[tuple[float, float]] = []
    # Left dome: boss -> equator
    n_dome = 28
    for i in range(n_dome + 1):
        ang = math.pi * 0.5 * (1.0 - i / n_dome)  # pi/2 -> 0
        x = X_CYL_L - DOME_L * math.sin(ang)
        r = R_BOSS + (R_CYL - R_BOSS) * math.cos(ang)
        top_pts.append((x, CY - r))
    # Right dome: equator -> boss
    for i in range(n_dome + 1):
        ang = math.pi * 0.5 * (i / n_dome)  # 0 -> pi/2
        x = X_CYL_R + DOME_L * math.sin(ang)
        r = R_BOSS + (R_CYL - R_BOSS) * math.cos(ang)
        top_pts.append((x, CY - r))
    bot_pts = [(x, 2 * CY - y) for x, y in reversed(top_pts)]
    pts = top_pts + bot_pts
    cmds = [f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"]
    cmds.extend(f"L{x:.1f} {y:.1f}" for x, y in pts[1:])
    cmds.append("Z")
    return " ".join(cmds)


def build_helical_weave() -> str:
    """Static ±55° geodesic-like carbon-fiber bands clipped to the vessel."""
    # Helical pitch along x for one full 360° turn: p = 2*pi*R / tan(55°)
    pitch = 2.0 * math.pi * R_CYL / math.tan(math.radians(55.0))
    xs = [X_DOME_L + 3.0 + (X_DOME_R - X_DOME_L - 6.0) * i / 140 for i in range(141)]
    n_bands = 10
    lines: list[str] = []

    for direction in (1.0, -1.0):
        # Back-ish subtle bands and bright front-side segments
        for b in range(n_bands):
            phi0 = 2.0 * math.pi * b / n_bands + (0.18 if direction < 0 else 0.0)
            seg: list[tuple[float, float]] = []
            for x in xs:
                r = vessel_radius(x)
                # Slightly accelerated turn near domes (Clairaut-like feel)
                s = (x - X_CYL_L) / pitch
                phi = phi0 + direction * 2.0 * math.pi * s
                if math.cos(phi) >= -0.05:
                    y = CY + r * math.sin(phi)
                    seg.append((x, y))
                else:
                    if len(seg) >= 3:
                        d = "M" + " L".join(f"{px:.1f} {py:.1f}" for px, py in seg)
                        stroke = "#6f86ad" if direction > 0 else "#4f6282"
                        op = "0.28" if direction > 0 else "0.22"
                        lines.append(
                            f'      <path d="{d}" fill="none" stroke="{stroke}" '
                            f'stroke-opacity="{op}" stroke-width="5.2" stroke-linecap="round"/>'
                        )
                        lines.append(
                            f'      <path d="{d}" fill="none" stroke="#c8d8f0" '
                            f'stroke-opacity="0.10" stroke-width="1.1" stroke-linecap="round"/>'
                        )
                    seg = []
            if len(seg) >= 3:
                d = "M" + " L".join(f"{px:.1f} {py:.1f}" for px, py in seg)
                stroke = "#6f86ad" if direction > 0 else "#4f6282"
                op = "0.28" if direction > 0 else "0.22"
                lines.append(
                    f'      <path d="{d}" fill="none" stroke="{stroke}" '
                    f'stroke-opacity="{op}" stroke-width="5.2" stroke-linecap="round"/>'
                )
                lines.append(
                    f'      <path d="{d}" fill="none" stroke="#c8d8f0" '
                    f'stroke-opacity="0.10" stroke-width="1.1" stroke-linecap="round"/>'
                )
    return "\n".join(lines)


def smoothstep(t: float) -> float:
    return t * t * (3.0 - 2.0 * t)


def build_active_animation():
    """Generate synchronized carriage, eye rotation, taut tow and active laid path."""
    # Keyframe sampling across full 10s cycle:
    # 0.00..0.44: forward helical pass (left dome -> right dome)
    # 0.44..0.50: right dome turnaround (carriage slows/dwells, eye pivots +24 -> -24)
    # 0.50..0.94: return helical pass (right dome -> left dome)
    # 0.94..1.00: left dome turnaround (eye pivots -24 -> +24)
    n_frames = 120
    x_min = X_DOME_L + 10.0  # 448
    x_max = X_DOME_R - 10.0  # 740

    car_xs: list[float] = []
    eye_ys: list[float] = []
    eye_angs: list[float] = []
    c_xs: list[float] = []
    c_ys: list[float] = []

    for i in range(n_frames + 1):
        u = i / n_frames
        if u < 0.44:
            p = u / 0.44
            # Ease gently at dome boundaries
            s = 0.08 * smoothstep(min(1.0, p * 5.0)) + 0.84 * p + 0.08 * (
                1.0 - smoothstep(min(1.0, (1.0 - p) * 5.0))
            )
            cx = x_min + (x_max - x_min) * s
            # Front-side contact wave along lower-front face of vessel
            r = vessel_radius(cx)
            cy = CY + r * math.sin(math.radians(-38.0 + 78.0 * p))
            # Payout eye leads slightly ahead of contact point along X
            ex = min(x_max + 8.0, cx + 18.0)
            ey = CY + r + 34.0
            ang = 24.0
        elif u < 0.50:
            p = smoothstep((u - 0.44) / 0.06)
            cx = x_max
            r = vessel_radius(cx)
            cy = CY + r * math.sin(math.radians(40.0 * (1.0 - 2.0 * p)))
            ex = x_max + 8.0 - 16.0 * p
            ey = CY + r + 34.0
            ang = 24.0 - 48.0 * p
        elif u < 0.94:
            p = (u - 0.50) / 0.44
            s = 0.08 * smoothstep(min(1.0, p * 5.0)) + 0.84 * p + 0.08 * (
                1.0 - smoothstep(min(1.0, (1.0 - p) * 5.0))
            )
            cx = x_max - (x_max - x_min) * s
            r = vessel_radius(cx)
            cy = CY + r * math.sin(math.radians(38.0 - 78.0 * p))
            ex = max(x_min - 8.0, cx - 18.0)
            ey = CY + r + 34.0
            ang = -24.0
        else:
            p = smoothstep((u - 0.94) / 0.06)
            cx = x_min
            r = vessel_radius(cx)
            cy = CY + r * math.sin(math.radians(-40.0 * (1.0 - 2.0 * p)))
            ex = x_min - 8.0 + 16.0 * p
            ey = CY + r + 34.0
            ang = -24.0 + 48.0 * p

        car_xs.append(ex)
        eye_ys.append(ey)
        eye_angs.append(ang)
        c_xs.append(cx)
        c_ys.append(cy)

    # Forward active laid path (u in [0, 0.44]) & return active laid path (u in [0.50, 0.94])
    fwd_pts = [(c_xs[i], c_ys[i]) for i in range(0, int(n_frames * 0.44) + 1)]
    ret_pts = [(c_xs[i], c_ys[i]) for i in range(int(n_frames * 0.50), int(n_frames * 0.94) + 1)]

    def path_and_len(pts: list[tuple[float, float]]) -> tuple[str, float]:
        d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
        length = sum(
            math.hypot(pts[k + 1][0] - pts[k][0], pts[k + 1][1] - pts[k][1])
            for k in range(len(pts) - 1)
        )
        return d, length

    fwd_d, fwd_len = path_and_len(fwd_pts)
    ret_d, ret_len = path_and_len(ret_pts)

    return {
        "car_x": ";".join(f"{v:.1f}" for v in car_xs),
        "eye_y": ";".join(f"{v:.1f}" for v in eye_ys),
        "eye_ang": ";".join(f"{v:.1f}" for v in eye_angs),
        "c_x": ";".join(f"{v:.1f}" for v in c_xs),
        "c_y": ";".join(f"{v:.1f}" for v in c_ys),
        "car_x0": f"{car_xs[0]:.1f}",
        "eye_y0": f"{eye_ys[0]:.1f}",
        "c_x0": f"{c_xs[0]:.1f}",
        "c_y0": f"{c_ys[0]:.1f}",
        "fwd_d": fwd_d,
        "fwd_len": f"{fwd_len:.1f}",
        "ret_d": ret_d,
        "ret_len": f"{ret_len:.1f}",
    }


def generate() -> str:
    vessel_d = vessel_outline_path()
    weave_svg = build_helical_weave()
    anim = build_active_animation()
    dur = f"{LOOP:.1f}s"

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
  <title id="t">Kirmen Studio - composite filament winding CAM and 3D simulation</title>
  <desc id="d">A Type-IV pressure vessel rotating between headstock and tailstock chucks while a 4-axis carriage moves along its rail, pivoting the payout eye at each dome turnaround and laying a helical carbon-fiber band onto the surface.</desc>
  <defs>
    <radialGradient id="bg" cx="68%" cy="46%" r="72%">
      <stop offset="0%" stop-color="#111930"/>
      <stop offset="55%" stop-color="#080c17"/>
      <stop offset="100%" stop-color="#03050a"/>
    </radialGradient>
    <radialGradient id="glow" cx="595" cy="148" r="210" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#ff8c38" stop-opacity="0.14"/>
      <stop offset="55%" stop-color="#d97757" stop-opacity="0.04"/>
      <stop offset="100%" stop-color="#d97757" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="gridfade" cx="595" cy="158" r="265" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#fff"/>
      <stop offset="100%" stop-color="#000"/>
    </radialGradient>
    <mask id="gridmask"><rect width="{W}" height="{H}" fill="url(#gridfade)"/></mask>
    <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
      <path d="M24 0H0V24" fill="none" stroke="#9ab4df" stroke-opacity="0.075" stroke-width="1"/>
    </pattern>
    <linearGradient id="vessel" x1="0" y1="88" x2="0" y2="208" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#1b263d"/>
      <stop offset="18%" stop-color="#2c3d5c"/>
      <stop offset="30%" stop-color="#3a4e73"/>
      <stop offset="44%" stop-color="#22304a"/>
      <stop offset="72%" stop-color="#141d2e"/>
      <stop offset="100%" stop-color="#0b101d"/>
    </linearGradient>
    <linearGradient id="chuck" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#3a465e"/>
      <stop offset="45%" stop-color="#222b3d"/>
      <stop offset="100%" stop-color="#111724"/>
    </linearGradient>
    <linearGradient id="rail" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#394761"/>
      <stop offset="100%" stop-color="#1a2233"/>
    </linearGradient>
    <clipPath id="card"><rect width="{W}" height="{H}" rx="16"/></clipPath>
    <clipPath id="vessel-clip"><path d="{vessel_d}"/></clipPath>
    <filter id="tow-glow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="2.6" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <style>
    .sans {{ font-family: 'Segoe UI Variable Display', 'Segoe UI', system-ui, -apple-system, 'Helvetica Neue', Arial, sans-serif; }}
    .mono {{ font-family: ui-monospace, 'Cascadia Mono', 'SF Mono', Menlo, Consolas, monospace; }}
    .chip {{ fill: #ffffff; fill-opacity: 0.055; stroke: #ffffff; stroke-opacity: 0.14; }}
    .chiptext {{ font-family: ui-monospace, 'Cascadia Mono', 'SF Mono', Menlo, Consolas, monospace; font-size: 11px; fill: #b8c6de; text-anchor: middle; letter-spacing: 0.6px; }}
    @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
  </style>

  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>
    <rect width="{W}" height="{H}" fill="url(#grid)" mask="url(#gridmask)"/>
    <rect width="{W}" height="{H}" fill="url(#glow)"/>

    <!-- Left column: Brand mark, title, subtitle & spec chips -->
    <g transform="translate(36, 46) scale(0.047)">
      <path d="{KIRMEN_MARK_PATH}" fill="#f5f5f7"/>
    </g>
    <text x="90" y="75" class="sans" font-size="27" font-weight="700" fill="#f4f6fa" letter-spacing="-0.4">Kirmen Studio</text>
    <text x="90" y="96" class="mono" font-size="11.5" fill="#d97757" letter-spacing="1.4">FILAMENT WINDING CAM</text>

    <text x="40" y="138" class="sans" font-size="14.5" fill="#b4bfd4">G-code generation &amp; 3D simulation</text>
    <text x="40" y="159" class="sans" font-size="14.5" fill="#b4bfd4">for composite filament winding.</text>

    <!-- Spec chips -->
    <rect x="40" y="186" width="62" height="24" rx="6" class="chip"/>
    <text x="71" y="202" class="chiptext">HOOP</text>
    <rect x="110" y="186" width="80" height="24" rx="6" class="chip"/>
    <text x="150" y="202" class="chiptext">HELICAL</text>
    <rect x="198" y="186" width="68" height="24" rx="6" class="chip"/>
    <text x="232" y="202" class="chiptext">POLAR</text>

    <rect x="40" y="218" width="76" height="24" rx="6" class="chip"/>
    <text x="78" y="234" class="chiptext">3D SIM</text>
    <rect x="124" y="218" width="106" height="24" rx="6" class="chip"/>
    <text x="177" y="234" class="chiptext">5 CNC POSTS</text>

    <!-- Subtle G-code status line -->
    <line x1="40" y1="268" x2="310" y2="268" stroke="#ffffff" stroke-opacity="0.09"/>
    <text x="40" y="292" class="mono" font-size="11.5" fill="#7c8aa3">G1 X.. Y.. Z.. A..  ·  ±55° GEODESIC</text>
    <text x="40" y="311" class="mono" font-size="11" fill="#5e6b82">medinstech.com/kirmen</text>

    <!-- Right column: 4-axis filament winding machine & Type-IV pressure vessel -->
    <!-- Mandrel centerline (A axis) -->
    <line x1="364" y1="{CY:.1f}" x2="826" y2="{CY:.1f}" stroke="#9ab4df" stroke-opacity="0.22" stroke-width="1" stroke-dasharray="14 5 3 5"/>

    <!-- Headstock (left) & Tailstock (right) -->
    <rect x="372" y="108" width="24" height="80" rx="3" fill="url(#chuck)" stroke="#556684" stroke-width="1"/>
    <rect x="396" y="122" width="18" height="52" rx="2" fill="url(#chuck)" stroke="#6a7d9e" stroke-width="1"/>
    <line x1="396" y1="133" x2="414" y2="133" stroke="#8ea4c9" stroke-opacity="0.35"/>
    <line x1="396" y1="163" x2="414" y2="163" stroke="#8ea4c9" stroke-opacity="0.35"/>
    <!-- Left polar shaft & boss -->
    <rect x="414" y="139" width="26" height="18" rx="1.5" fill="#2c3952" stroke="#6c80a3" stroke-width="0.9"/>

    <!-- Right polar shaft & boss -->
    <rect x="748" y="139" width="26" height="18" rx="1.5" fill="#2c3952" stroke="#6c80a3" stroke-width="0.9"/>
    <polygon points="774,135 790,127 790,169 774,161" fill="url(#chuck)" stroke="#6a7d9e" stroke-width="1"/>
    <rect x="790" y="114" width="20" height="68" rx="3" fill="url(#chuck)" stroke="#556684" stroke-width="1"/>

    <!-- Mandrel rotation indicator (A axis) -->
    <path d="M817 129 A18 22 0 0 1 817 167" fill="none" stroke="#6cb4ff" stroke-opacity="0.55" stroke-width="1.3"/>
    <polygon points="817,169 813,162 821,163" fill="#6cb4ff" fill-opacity="0.65"/>
    <text x="832" y="152" class="mono" font-size="11" fill="#6cb4ff" fill-opacity="0.85">A</text>

    <!-- Pressure Vessel body -->
    <path d="{vessel_d}" fill="url(#vessel)" stroke="#62789e" stroke-opacity="0.55" stroke-width="1.2"/>

    <!-- Clipped wound carbon-fiber helical weave + active glowing band -->
    <g clip-path="url(#vessel-clip)">
{weave_svg}

      <!-- Active freshly laid forward pass (+55 deg) -->
      <path d="{anim['fwd_d']}" fill="none" stroke="#ff8c38" stroke-opacity="0.36" stroke-width="8.5" stroke-linecap="round"
            stroke-dasharray="{anim['fwd_len']}" stroke-dashoffset="{anim['fwd_len']}" filter="url(#tow-glow)">
        <animate attributeName="stroke-dashoffset"
                 values="{anim['fwd_len']};0;0;{anim['fwd_len']}"
                 keyTimes="0;0.44;0.52;1" dur="{dur}" repeatCount="indefinite"/>
        <animate attributeName="opacity"
                 values="0.95;0.95;0.18;0.18;0"
                 keyTimes="0;0.44;0.54;0.96;1" dur="{dur}" repeatCount="indefinite"/>
      </path>
      <path d="{anim['fwd_d']}" fill="none" stroke="#ffc48c" stroke-width="2.4" stroke-linecap="round"
            stroke-dasharray="{anim['fwd_len']}" stroke-dashoffset="{anim['fwd_len']}">
        <animate attributeName="stroke-dashoffset"
                 values="{anim['fwd_len']};0;0;{anim['fwd_len']}"
                 keyTimes="0;0.44;0.52;1" dur="{dur}" repeatCount="indefinite"/>
        <animate attributeName="opacity"
                 values="0.95;0.95;0.22;0.22;0"
                 keyTimes="0;0.44;0.54;0.96;1" dur="{dur}" repeatCount="indefinite"/>
      </path>

      <!-- Active freshly laid return pass (-55 deg) -->
      <path d="{anim['ret_d']}" fill="none" stroke="#ff8c38" stroke-opacity="0.36" stroke-width="8.5" stroke-linecap="round"
            stroke-dasharray="{anim['ret_len']}" stroke-dashoffset="{anim['ret_len']}" filter="url(#tow-glow)">
        <animate attributeName="stroke-dashoffset"
                 values="{anim['ret_len']};{anim['ret_len']};0;0"
                 keyTimes="0;0.50;0.94;1" dur="{dur}" repeatCount="indefinite"/>
        <animate attributeName="opacity"
                 values="0;0;0.95;0.95;0.2"
                 keyTimes="0;0.49;0.50;0.94;1" dur="{dur}" repeatCount="indefinite"/>
      </path>
      <path d="{anim['ret_d']}" fill="none" stroke="#ffc48c" stroke-width="2.4" stroke-linecap="round"
            stroke-dasharray="{anim['ret_len']}" stroke-dashoffset="{anim['ret_len']}">
        <animate attributeName="stroke-dashoffset"
                 values="{anim['ret_len']};{anim['ret_len']};0;0"
                 keyTimes="0;0.50;0.94;1" dur="{dur}" repeatCount="indefinite"/>
        <animate attributeName="opacity"
                 values="0;0;0.95;0.95;0.2"
                 keyTimes="0;0.49;0.50;0.94;1" dur="{dur}" repeatCount="indefinite"/>
      </path>
    </g>

    <!-- Vessel crisp outer rim -->
    <path d="{vessel_d}" fill="none" stroke="#859dc4" stroke-opacity="0.45" stroke-width="1.2"/>

    <!-- Linear Carriage Rail (X axis) -->
    <rect x="382" y="286" width="424" height="7" rx="3" fill="url(#rail)" stroke="#556684" stroke-opacity="0.55" stroke-width="0.9"/>
    <rect x="382" y="297" width="424" height="4" rx="2" fill="#182032"/>
    <rect x="378" y="282" width="8" height="22" rx="2" fill="#2c384f"/>
    <rect x="802" y="282" width="8" height="22" rx="2" fill="#2c384f"/>
    <text x="818" y="294" class="mono" font-size="11" fill="#7c8aa3">X</text>

    <!-- Taut free fiber tow from payout eye to tangent contact point -->
    <line x1="{anim['car_x0']}" y1="{anim['eye_y0']}" x2="{anim['c_x0']}" y2="{anim['c_y0']}"
          stroke="#ff8c38" stroke-opacity="0.45" stroke-width="4.6" stroke-linecap="round" filter="url(#tow-glow)">
      <animate attributeName="x1" values="{anim['car_x']}" dur="{dur}" repeatCount="indefinite"/>
      <animate attributeName="y1" values="{anim['eye_y']}" dur="{dur}" repeatCount="indefinite"/>
      <animate attributeName="x2" values="{anim['c_x']}" dur="{dur}" repeatCount="indefinite"/>
      <animate attributeName="y2" values="{anim['c_y']}" dur="{dur}" repeatCount="indefinite"/>
    </line>
    <line x1="{anim['car_x0']}" y1="{anim['eye_y0']}" x2="{anim['c_x0']}" y2="{anim['c_y0']}"
          stroke="#ffe2c2" stroke-width="1.6" stroke-linecap="round">
      <animate attributeName="x1" values="{anim['car_x']}" dur="{dur}" repeatCount="indefinite"/>
      <animate attributeName="y1" values="{anim['eye_y']}" dur="{dur}" repeatCount="indefinite"/>
      <animate attributeName="x2" values="{anim['c_x']}" dur="{dur}" repeatCount="indefinite"/>
      <animate attributeName="y2" values="{anim['c_y']}" dur="{dur}" repeatCount="indefinite"/>
    </line>

    <!-- Contact point glow dot -->
    <circle cx="{anim['c_x0']}" cy="{anim['c_y0']}" r="4.2" fill="#ff8c38" stroke="#ffe8cf" stroke-width="1.2" filter="url(#tow-glow)">
      <animate attributeName="cx" values="{anim['c_x']}" dur="{dur}" repeatCount="indefinite"/>
      <animate attributeName="cy" values="{anim['c_y']}" dur="{dur}" repeatCount="indefinite"/>
    </circle>

    <!-- Animated Carriage + Z arm + Pivoting Payout Eye -->
    <g>
      <!-- Z-axis rod connecting carriage to payout eye -->
      <line x1="{anim['car_x0']}" y1="286" x2="{anim['car_x0']}" y2="{anim['eye_y0']}"
            stroke="#5b6f91" stroke-width="5" stroke-linecap="round">
        <animate attributeName="x1" values="{anim['car_x']}" dur="{dur}" repeatCount="indefinite"/>
        <animate attributeName="x2" values="{anim['car_x']}" dur="{dur}" repeatCount="indefinite"/>
        <animate attributeName="y2" values="{anim['eye_y']}" dur="{dur}" repeatCount="indefinite"/>
      </line>
      <line x1="{anim['car_x0']}" y1="286" x2="{anim['car_x0']}" y2="{anim['eye_y0']}"
            stroke="#9fb5d9" stroke-opacity="0.45" stroke-width="1.2">
        <animate attributeName="x1" values="{anim['car_x']}" dur="{dur}" repeatCount="indefinite"/>
        <animate attributeName="x2" values="{anim['car_x']}" dur="{dur}" repeatCount="indefinite"/>
        <animate attributeName="y2" values="{anim['eye_y']}" dur="{dur}" repeatCount="indefinite"/>
      </line>

      <!-- Carriage block riding the rail -->
      <g transform="translate({anim['car_x0']}, 288)">
        <animateTransform attributeName="transform" type="translate"
                          values="{';'.join(f'{x} 288' for x in anim['car_x'].split(';'))}"
                          dur="{dur}" repeatCount="indefinite"/>
        <rect x="-18" y="-10" width="36" height="20" rx="4" fill="#232e44" stroke="#7c93ba" stroke-width="1.1"/>
        <circle cx="-9" cy="0" r="2.2" fill="#ff8c38"/>
        <circle cx="9" cy="0" r="2.2" fill="#6cb4ff"/>
      </g>

      <!-- Payout eye head (pivots with winding angle) -->
      <g transform="translate({anim['car_x0']}, {anim['eye_y0']})">
        <animateTransform attributeName="transform" type="translate"
                          values="{';'.join(f'{x} {y}' for x, y in zip(anim['car_x'].split(';'), anim['eye_y'].split(';')))}"
                          dur="{dur}" repeatCount="indefinite"/>
        <g>
          <animateTransform attributeName="transform" type="rotate"
                            values="{anim['eye_ang']}" dur="{dur}" repeatCount="indefinite"/>
          <rect x="-11" y="-5" width="22" height="10" rx="3" fill="#2c3a54" stroke="#d97757" stroke-width="1.2"/>
          <circle cx="0" cy="0" r="2.6" fill="#ffe2c2"/>
        </g>
      </g>
    </g>

    <!-- Subtle dimension callout above vessel -->
    <g stroke="#9ab4df" stroke-opacity="0.28" stroke-width="0.9" fill="none">
      <path d="M438 66 V54 H750 V66"/>
    </g>
    <text x="594" y="48" class="mono" font-size="11" fill="#7c8aa3" text-anchor="middle">TYPE IV · PRESSURE VESSEL · 4-AXIS</text>
  </g>
</svg>
'''


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("assets/kirmen-studio.svg")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(generate(), encoding="utf-8")
    print(f"Wrote {out} ({out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
