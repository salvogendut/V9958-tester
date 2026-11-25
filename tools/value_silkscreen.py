"""Place KiCad's reference and value fields together outside populated footprints."""

import pcbnew as p
from polarity import is_plus

M = p.FromMM
SIZE = 1.0
STROKE = 0.16
CLEARANCE = 0.3


def bounds(box):
    return tuple(p.ToMM(v) for v in (box.GetLeft(), box.GetTop(), box.GetRight(), box.GetBottom()))


def overlaps(a, b):
    return (a[0] < b[2] + CLEARANCE and a[2] > b[0] - CLEARANCE and
            a[1] < b[3] + CLEARANCE and a[3] > b[1] - CLEARANCE)


def fields(fp, angle):
    for field in (fp.Reference(), fp.Value()):
        field.SetVisible(True)
        field.SetLayer(p.F_SilkS)
        field.SetTextSize(p.VECTOR2I(M(SIZE), M(SIZE)))
        field.SetTextThickness(M(STROKE))
        field.SetHorizJustify(p.GR_TEXT_H_ALIGN_CENTER)
        field.SetVertJustify(p.GR_TEXT_V_ALIGN_CENTER)
        field.SetTextAngle(p.EDA_ANGLE(angle, p.DEGREES_T))
    return fp.Reference(), fp.Value()


def placements(fp, body, outline, obstacles):
    """Try one line and two lines on each side, using KiCad's actual font metrics."""
    ref, value = fields(fp, 0)
    rw, rh = p.ToMM(ref.GetBoundingBox().GetWidth()), p.ToMM(ref.GetBoundingBox().GetHeight())
    vw, vh = p.ToMM(value.GetBoundingBox().GetWidth()), p.ToMM(value.GetBoundingBox().GetHeight())
    gap = 0.45
    # Offsets are the field centres relative to the centre of the whole inscription.
    formats = [(rw + gap + vw, max(rh, vh), (-(gap + vw)/2, 0), ((gap + rw)/2, 0)),
               (max(rw, vw), rh + gap + vh, (0, -(gap + vh)/2), (0, (gap + rh)/2))]
    x0, y0, x1, y1 = body
    cx, cy = (x0 + x1)/2, (y0 + y1)/2
    candidates = []
    for fmt, (w, h, ref_offset, value_offset) in enumerate(formats):
        for angle in (0, 90):
            width, height = (h, w) if angle else (w, h)
            for extra in (0.0, 1.0, 2.5, 4.0, 5.5):
                distance = CLEARANCE + 0.1 + extra
                sides = [(cx, y0 - distance - height/2), (cx, y1 + distance + height/2),
                         (x0 - distance - width/2, cy), (x1 + distance + width/2, cy)]
                for side, (x, y) in enumerate(sides):
                    along_x = side < 2
                    span = x1 - x0 if along_x else y1 - y0
                    for shift in (0, -0.5, 0.5, -1.5, 1.5, -3, 3, -5, 5, -span/3, span/3, -7.5, 7.5):
                        px, py = (x + shift, y) if along_x else (x, y + shift)
                        box = (px-width/2, py-height/2, px+width/2, py+height/2)
                        if any(box[i] < outline[i] + 0.7 for i in (0, 1)):
                            continue
                        if any(box[i] > outline[i] - 0.7 for i in (2, 3)):
                            continue
                        if any(overlaps(box, other) for other in obstacles):
                            continue
                        # Prefer labels parallel to their component's long side and
                        # centred on it. The nearest row wins in dense resistor banks.
                        alignment = (along_x != (x1-x0 >= y1-y0))
                        sideways = (along_x == bool(angle))
                        score = extra*3 + abs(shift)*0.65 + 1.6*alignment + 1.8*sideways
                        score += fmt*0.8 + (side % 2)*0.45 + bool(angle)*0.25
                        candidates.append((score, box, angle, ref_offset, value_offset))
    return sorted(candidates)


def apply_value_silkscreen(board):
    outline = bounds(board.GetBoardEdgesBoundingBox())
    footprints = list(board.GetFootprints())
    bodies = {fp.GetReference(): bounds(fp.GetBoundingBox(False, False)) for fp in footprints}
    obstacles = list(bodies.values())
    obstacles.extend(bounds(item.GetBoundingBox()) for item in board.GetDrawings()
                     if item.GetLayer() == p.F_SilkS)
    obstacles.extend(bounds(item.GetBoundingBox()) for fp in footprints
                     for item in fp.GraphicalItems() if is_plus(item))
    components = []
    for fp in footprints:
        ref = fp.GetReference()
        if ref.startswith(('H', 'TP')):
            if fp.Reference().IsVisible():
                obstacles.append(bounds(fp.Reference().GetBoundingBox()))
        elif ref == "C29" and "SRAM" in board.GetTitleBlock().GetTitle():
            # This capacitor sits between the comparator and the SDIP socket.
            # Use the two clear strips above the footprint for its complete BOM value.
            ref_field, value_field = fields(fp, 0)
            for field, x, y, angle in ((ref_field, 31.3, 51, 0), (value_field, 32.4, 46.0, 90)):
                field.SetTextSize(p.VECTOR2I(M(0.9), M(0.9)))
                field.SetTextAngle(p.EDA_ANGLE(angle, p.DEGREES_T))
                field.SetPosition(p.VECTOR2I(M(x), M(y)))
                box = bounds(field.GetBoundingBox())
                if any(overlaps(box, obstacle) for obstacle in obstacles):
                    raise ValueError(f"Obstructed SRAM capacitor inscription: {field.GetText()}")
                obstacles.append(box)
        else:
            components.append(fp)
    remaining = {}
    for fp in components:
        ref = fp.GetReference()
        remaining[ref] = (fp, placements(fp, bodies[ref], outline, obstacles))
    while remaining:
        # Reserve the tightest locations first. Reference breaks ties reproducibly.
        ref = min(remaining, key=lambda r: (len(remaining[r][1]), r))
        fp, options = remaining.pop(ref)
        if not options:
            raise ValueError(f'No clear component-side value location for {ref}')
        _, box, angle, ref_offset, value_offset = options[0]
        cx, cy = (box[0] + box[2])/2, (box[1] + box[3])/2
        for field, (dx, dy) in zip(fields(fp, angle), (ref_offset, value_offset)):
            if angle:
                dx, dy = dy, -dx
            delta = p.VECTOR2I(M(cx+dx), M(cy+dy)) - field.GetBoundingBox().GetCenter()
            field.SetPosition(field.GetPosition() + delta)
        for _, options in remaining.values():
            options[:] = [option for option in options if not overlaps(box, option[1])]
