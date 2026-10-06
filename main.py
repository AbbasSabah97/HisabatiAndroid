# -*- coding: utf-8 -*-
"""حساباتي - تطبيق أندرويد للحسابات الشخصية (Kivy + SQLite)"""
import os, sqlite3, datetime
from arfix import font_chars, safe_text
from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex as hx
try:
    import arabic_reshaper
    from bidi.algorithm import get_display

    def ar(t):
        return safe_text(get_display(arabic_reshaper.reshape(str(t))), GLYPHS)
except ImportError:
    def ar(t):
        return str(t)

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = next((p for p in (os.path.join(HERE, "fonts", "Amiri-Regular.ttf"), os.path.join(HERE, "Amiri-Regular.ttf"), "/system/fonts/NotoNaskhArabic-Regular.ttf",
                         "/system/fonts/NotoSansArabic-Regular.ttf") if os.path.exists(p)), "Roboto")
GLYPHS = font_chars(FONT) if FONT.lower().endswith(".ttf") else None
NAVY, ACC, GOLD, RED, GREEN, INK = hx("#1e1b4b"), hx("#4338ca"), hx("#d4a017"), hx("#dc2626"), hx("#16a34a"), hx("#1e1b4b")
MONTHS = ["كانون الثاني", "شباط", "آذار", "نيسان", "أيار", "حزيران", "تموز", "آب", "أيلول", "تشرين الأول", "تشرين الثاني", "كانون الأول"]
MR = [ar(m) for m in MONTHS]
CATS = ["طعام", "سكن وإيجار", "مواصلات", "فواتير وخدمات", "صحة", "تعليم", "ترفيه", "ملابس", "أخرى"]
SOURCES = ["الراتب", "مكافأة", "أعمال حرة", "أخرى"]
db = None


def Q(sql, a=()):
    return db.execute(sql, a).fetchall()


def X(sql, a=()):
    db.execute(sql, a)
    db.commit()


def fmt(n):
    return f"{round(n):,}"


class Opt(SpinnerOption):
    def __init__(self, **k):
        super().__init__(**k)
        self.font_name = FONT


class Bar(Widget):
    def __init__(self, col, **k):
        super().__init__(**k)
        with self.canvas:
            Color(*col)
            self.r = Rectangle()
        self.bind(pos=self._u, size=self._u)

    def _u(self, *a):
        self.r.pos, self.r.size = self.pos, self.size


def lab(text, size=14, color=INK, **k):
    return Label(text=ar(text), font_name=FONT, font_size=sp(size), color=color, **k)


def btn(text, cb, color=ACC, **k):
    b = Button(text=ar(text), font_name=FONT, font_size=sp(15), background_normal="", background_color=color, color=(1, 1, 1, 1), **k)
    b.bind(on_release=lambda *_: cb())
    return b


def spin(values, text, **k):
    return Spinner(text=text, values=values, font_name=FONT, option_cls=Opt, background_normal="", background_color=hx("#c7d2fe"), color=INK, **k)


def inp(hint, filt=None, **k):
    try:
        return TextInput(hint_text=ar(hint), font_name=FONT, multiline=False, input_filter=filt, base_direction="rtl", halign="right", **k)
    except TypeError:
        return TextInput(hint_text=ar(hint), font_name=FONT, multiline=False, input_filter=filt, halign="right", **k)


class AccApp(App):
    title = "حساباتي"

    def build(self):
        global db
        Window.clearcolor = hx("#f1f2fb")
        Window.softinput_mode = "below_target"
        db = sqlite3.connect(os.path.join(self.user_data_dir, "accounts.db"))
        db.executescript("""CREATE TABLE IF NOT EXISTS income(id INTEGER PRIMARY KEY AUTOINCREMENT, d TEXT, src TEXT, amount REAL, note TEXT);
        CREATE TABLE IF NOT EXISTS expenses(id INTEGER PRIMARY KEY AUTOINCREMENT, d TEXT, cat TEXT, amount REAL, note TEXT);
        CREATE TABLE IF NOT EXISTS budgets(cat TEXT PRIMARY KEY, lim REAL);""")
        now = datetime.date.today()
        self.y, self.m = now.year, now.month
        root = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(6))
        top = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(4))
        top.add_widget(btn("الميزانيات", self.budgets, GOLD, size_hint_x=.9))
        self.sy = spin([str(y) for y in range(now.year - 5, now.year + 2)], str(now.year), size_hint_x=.7)
        self.sm = spin(MR, MR[now.month - 1])
        for w in (self.sy, self.sm):
            top.add_widget(w)
            w.bind(text=lambda *_: self.pick())
        root.add_widget(top)
        cards = BoxLayout(size_hint_y=None, height=dp(66), spacing=dp(4))
        self.cv = {}
        for key, title, col in (("bal", "المتبقي", NAVY), ("exp", "المصروفات", RED), ("inc", "الدخل", GREEN)):
            c = BoxLayout(orientation="vertical")
            with c.canvas.before:
                Color(1, 1, 1, 1)
                rc = Rectangle()
            c.bind(pos=lambda i, v, r=rc: setattr(r, "pos", v), size=lambda i, v, r=rc: setattr(r, "size", v))
            c.add_widget(lab(title, 12, size_hint_y=.4))
            self.cv[key] = Label(text="0", font_size=sp(19), bold=True, color=col)
            c.add_widget(self.cv[key])
            cards.add_widget(c)
        root.add_widget(cards)
        self.chart = BoxLayout(size_hint_y=None, height=dp(170), spacing=dp(2))
        root.add_widget(self.chart)
        self.insight = lab("", 12, color=hx("#92400e"), size_hint_y=None, height=dp(34))
        self.insight.bind(size=lambda i, v: setattr(i, "text_size", (v[0], None)))
        root.add_widget(self.insight)
        sv = ScrollView()
        self.lst = GridLayout(cols=1, size_hint_y=None, spacing=dp(3))
        self.lst.bind(minimum_height=self.lst.setter("height"))
        sv.add_widget(self.lst)
        root.add_widget(sv)
        bt = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(6))
        bt.add_widget(btn("+ دخل / راتب", lambda: self.form("i"), GREEN))
        bt.add_widget(btn("+ مصروف", lambda: self.form("e"), RED))
        root.add_widget(bt)
        self.refresh()
        return root

    def pick(self):
        if self.sm.text in MR:
            self.y, self.m = int(self.sy.text), MR.index(self.sm.text) + 1
            self.refresh()

    def ym(self, back=0):
        y, m = self.y, self.m - back
        if m < 1:
            y, m = y - 1, 12
        return f"{y}-{m:02d}"

    def refresh(self):
        m = self.ym()
        inc = Q("SELECT id,d,src,amount,note FROM income WHERE substr(d,1,7)=?", (m,))
        exp = Q("SELECT id,d,cat,amount,note FROM expenses WHERE substr(d,1,7)=?", (m,))
        ti, te = sum(r[3] for r in inc), sum(r[3] for r in exp)
        self.cv["inc"].text, self.cv["exp"].text, self.cv["bal"].text = fmt(ti), fmt(te), fmt(ti - te)
        sql = "SELECT cat,SUM(amount) FROM expenses WHERE substr(d,1,7)=? GROUP BY cat ORDER BY SUM(amount) DESC"
        cur, prv, bud = dict(Q(sql, (m,))), dict(Q(sql, (self.ym(1),))), dict(Q("SELECT cat,lim FROM budgets"))
        self.chart.clear_widgets()
        if not cur:
            self.chart.add_widget(lab("لا توجد مصروفات في هذا الشهر", 13))
        else:
            mx = max(cur.values())
            for c, v in reversed(list(cur.items())):
                h = max(v / mx * 0.7, 0.02)
                col = BoxLayout(orientation="vertical")
                col.add_widget(lab(fmt(v), 9, size_hint_y=.12))
                col.add_widget(Widget(size_hint_y=0.7 - h + 0.0001))
                col.add_widget(Bar(RED if c in bud and v > bud[c] else ACC, size_hint_y=h))
                col.add_widget(lab(c.split()[0], 9, size_hint_y=.18))
                self.chart.add_widget(col)
        diff = {c: cur.get(c, 0) - prv.get(c, 0) for c in set(cur) | set(prv)}
        top = max(diff, key=diff.get) if diff else None
        self.insight.text = ar("لا توجد مصروفات في الشهر السابق للمقارنة." if not prv else
                               (f"أكثر فئة ارتفاعاً عن الشهر السابق: {top} (+{fmt(diff[top])})" if top and diff[top] > 0 else "لم يرتفع الإنفاق في أي فئة عن الشهر السابق."))
        self.lst.clear_widgets()
        rows = [("i",) + r for r in inc] + [("e",) + r for r in exp]
        for r in sorted(rows, key=lambda x: (x[2], x[1]), reverse=True):
            k, i, d, c, a, n = r
            b = Button(text=ar(f"{d}   {c}   {fmt(a)}   {n or ''}"), font_name=FONT, font_size=sp(14), size_hint_y=None, height=dp(44),
                       background_normal="", background_color=hx("#dcfce7") if k == "i" else hx("#fee2e2"), color=INK, halign="right", valign="middle")
            b.bind(size=lambda inst, v: setattr(inst, "text_size", (v[0] - dp(14), None)))
            b.bind(on_release=lambda inst, r=r: self.form(r[0], r[1:]))
            self.lst.add_widget(b)

    def form(self, kind, rec=None):
        inc = kind == "i"
        opts = SOURCES if inc else CATS
        y0, m0, d0 = (rec[1] if rec else datetime.date.today().isoformat()).split("-")
        g = GridLayout(cols=1, spacing=dp(6), padding=dp(8))
        row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(4))
        sd = spin([f"{i:02d}" for i in range(1, 32)], d0)
        sm = spin(MR, MR[int(m0) - 1])
        sy = spin(sorted({str(y) for y in range(self.y - 5, self.y + 2)} | {y0}), y0)
        for w in (sd, sm, sy):
            row.add_widget(w)
        g.add_widget(row)
        back = {ar(o): o for o in opts}
        cat = spin(list(back), ar(rec[2]) if rec else ar(opts[0]), size_hint_y=None, height=dp(44))
        amt = inp("المبلغ", "float", size_hint_y=None, height=dp(44))
        note = inp("ملاحظات", size_hint_y=None, height=dp(44))
        if rec:
            amt.text, note.text = str(int(rec[3]) if rec[3] == int(rec[3]) else rec[3]), rec[4] or ""
        for w in (cat, amt, note):
            g.add_widget(w)
        pop = Popup(title=ar("دخل / راتب" if inc else "مصروف"), title_font=FONT, content=g, size_hint=(.96, .8))

        def save():
            try:
                a = float(amt.text.replace(",", ""))
                d = f"{sy.text}-{MR.index(sm.text) + 1:02d}-{sd.text}"
                datetime.date.fromisoformat(d)
                assert a > 0
            except (ValueError, AssertionError):
                amt.hint_text = ar("أدخل مبلغاً صحيحاً وتاريخاً صالحاً")
                return
            tb, cl = ("income", "src") if inc else ("expenses", "cat")
            if rec:
                X(f"UPDATE {tb} SET d=?,{cl}=?,amount=?,note=? WHERE id=?", (d, back.get(cat.text, cat.text), a, note.text, rec[0]))
            else:
                X(f"INSERT INTO {tb}(d,{cl},amount,note) VALUES(?,?,?,?)", (d, back.get(cat.text, cat.text), a, note.text))
            pop.dismiss()
            self.sy.text, self.sm.text = sy.text, sm.text
            self.pick()

        def rm():
            X(f"DELETE FROM {'income' if inc else 'expenses'} WHERE id=?", (rec[0],))
            pop.dismiss()
            self.refresh()
        bt = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))
        bt.add_widget(btn("حفظ", save, GREEN))
        if rec:
            bt.add_widget(btn("حذف", rm, RED))
        bt.add_widget(btn("إلغاء", pop.dismiss, hx("#6b7280")))
        g.add_widget(bt)
        pop.open()

    def budgets(self):
        saved = dict(Q("SELECT cat,lim FROM budgets"))
        g = GridLayout(cols=2, spacing=dp(6), padding=dp(8), size_hint_y=None, row_default_height=dp(42), row_force_default=True)
        g.bind(minimum_height=g.setter("height"))
        fields = {}
        for c in CATS:
            fields[c] = inp("السقف الشهري", "float")
            fields[c].text = str(int(saved[c])) if c in saved else ""
            g.add_widget(fields[c])
            g.add_widget(lab(c, 14))
        sv = ScrollView()
        sv.add_widget(g)
        box = BoxLayout(orientation="vertical", spacing=dp(6))
        box.add_widget(sv)
        pop = Popup(title=ar("الميزانيات الشهرية لكل فئة"), title_font=FONT, content=box, size_hint=(.96, .9))

        def save():
            for c, f in fields.items():
                try:
                    v = float(f.text)
                except ValueError:
                    v = 0
                X("REPLACE INTO budgets(cat,lim) VALUES(?,?)", (c, v)) if v > 0 else X("DELETE FROM budgets WHERE cat=?", (c,))
            pop.dismiss()
            self.refresh()
        bt = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))
        bt.add_widget(btn("حفظ", save, GREEN))
        bt.add_widget(btn("إلغاء", pop.dismiss, hx("#6b7280")))
        box.add_widget(bt)
        pop.open()


if __name__ == "__main__":
    AccApp().run()
