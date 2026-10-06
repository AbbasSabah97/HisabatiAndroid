# -*- coding: utf-8 -*-
"""يمنع ظهور المربعات: يقرأ الرموز الموجودة فعلاً في الخط، ويستبدل أي رمز ناقص بحرفه الأساسي."""
import struct
import unicodedata


def font_chars(path):
    """مجموعة رموز يونيكود التي يحويها ملف الخط TTF (قراءة جدول cmap بدون مكتبات خارجية)."""
    try:
        d = open(path, "rb").read()
        n = struct.unpack(">H", d[4:6])[0]
        off = None
        for i in range(n):
            rec = d[12 + 16 * i:28 + 16 * i]
            if rec[:4] == b"cmap":
                off = struct.unpack(">I", rec[8:12])[0]
        cm, chars = d[off:], set()
        for i in range(struct.unpack(">H", cm[2:4])[0]):
            pid, eid, so = struct.unpack(">HHI", cm[4 + 8 * i:12 + 8 * i])
            fmt = struct.unpack(">H", cm[so:so + 2])[0]
            if fmt == 4:
                x2 = struct.unpack(">H", cm[so + 6:so + 8])[0]
                seg = x2 // 2
                ends = struct.unpack(f">{seg}H", cm[so + 14:so + 14 + x2])
                starts = struct.unpack(f">{seg}H", cm[so + 16 + x2:so + 16 + 2 * x2])
                for s, e in zip(starts, ends):
                    if s != 0xFFFF:
                        chars.update(range(s, e + 1))
            elif fmt == 12:
                for g in range(struct.unpack(">I", cm[so + 12:so + 16])[0]):
                    s, e, _ = struct.unpack(">III", cm[so + 16 + 12 * g:so + 28 + 12 * g])
                    chars.update(range(s, e + 1))
        return chars or None
    except Exception:
        return None


def safe_text(text, glyphs):
    """يستبدل كل رمز غير موجود في الخط بحرفه الأساسي (الترتيب هنا بصري، لذا يُعكس الحرف المركّب)."""
    if not glyphs:
        return text
    out = []
    for ch in text:
        if ord(ch) < 128 or ord(ch) in glyphs:
            out.append(ch)
            continue
        dec = unicodedata.decomposition(ch)
        base = "".join(chr(int(x, 16)) for x in dec.split()[1:]) if dec.startswith("<") else ""
        out.append(base[::-1] if base and all(ord(b) in glyphs for b in base) else ch)
    return "".join(out)
