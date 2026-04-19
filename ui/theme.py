# ── Light Theme ───────────────────────────────────────────
BG        = "#F5F6FA"      # page background
SIDEBAR   = "#FFFFFF"      # sidebar white
CARD      = "#FFFFFF"      # card white
BORDER    = "#E2E8F0"      # subtle borders
ACCENT    = "#4F46E5"      # indigo primary
ACCENT_LT = "#EEF2FF"      # indigo tint bg
ACCENT2   = "#7C3AED"      # purple secondary
TEXT      = "#1E293B"      # near-black text
MUTED     = "#64748B"      # slate muted
SUCCESS   = "#059669"      # green
SUCCESS_LT= "#ECFDF5"
DANGER    = "#DC2626"      # red
DANGER_LT = "#FEF2F2"
WARN      = "#D97706"      # amber
WARN_LT   = "#FFFBEB"

FONT      = ("Segoe UI", 10)
SMALL     = ("Segoe UI", 9)
BOLD      = ("Segoe UI", 10, "bold")
TITLE     = ("Segoe UI", 15, "bold")
HEADING   = ("Segoe UI", 12, "bold")

def entry(parent, show=None, width=0):
    import tkinter as tk
    kw = dict(bg=CARD, fg=TEXT, insertbackground=ACCENT, relief="solid",
              font=FONT, bd=1, highlightthickness=1,
              highlightbackground=BORDER, highlightcolor=ACCENT)
    if width:
        kw['width'] = width
    e = tk.Entry(parent, **kw)
    if show:
        e.config(show=show)
    return e

def btn(parent, text, cmd, color=ACCENT, fg="white", small=False, outline=False):
    import tkinter as tk
    f = SMALL if small else FONT
    if outline:
        b = tk.Button(parent, text=text, command=cmd, bg=CARD, fg=color,
                      font=(f[0], f[1], "bold"), relief="solid", cursor="hand2",
                      bd=1, highlightthickness=1, highlightbackground=color,
                      activebackground=ACCENT_LT, activeforeground=color,
                      padx=10, pady=4 if small else 7)
    else:
        b = tk.Button(parent, text=text, command=cmd, bg=color, fg=fg,
                      font=(f[0], f[1], "bold"), relief="flat", cursor="hand2",
                      bd=0, activebackground=ACCENT2, activeforeground="white",
                      padx=10, pady=4 if small else 7)
    return b

def card_frame(parent, **kw):
    import tkinter as tk
    f = tk.Frame(parent, bg=CARD, relief="solid", bd=1,
                 highlightthickness=1, highlightbackground=BORDER, **kw)
    return f

def label(parent, text, font=None, color=None, bg=None):
    import tkinter as tk
    return tk.Label(parent, text=text,
                    font=font or FONT,
                    fg=color or TEXT,
                    bg=bg or BG)

def progress_bar(parent, pct, width=320, height=8):
    import tkinter as tk
    outer = tk.Frame(parent, bg=BORDER, height=height, width=width)
    outer.pack_propagate(False)
    fill_w = max(0, int(width * pct / 100))
    color = SUCCESS if pct == 100 else ACCENT
    if fill_w > 0:
        tk.Frame(outer, bg=color, height=height, width=fill_w).place(x=0, y=0)
    return outer

def scrollable(parent):
    import tkinter as tk
    from tkinter import ttk
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Vertical.TScrollbar", background=BORDER,
                    troughcolor=BG, bordercolor=BG, arrowcolor=MUTED)
    canvas = tk.Canvas(parent, bg=BG, highlightthickness=0)
    scroll = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    frame = tk.Frame(canvas, bg=BG)
    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=scroll.set)
    canvas.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")
    return frame
