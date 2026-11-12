#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Картинки с формулами для курсовой (вариант 6: круглый волновод, E12).
Только matplotlib, LaTeX не нужен.

    python formulas_gen.py
    python formulas_gen.py --dpi 400 --outdir formulas
    python formulas_gen.py --only Q_pr

Физика: E_z ~ cos(k_z z), E_r/E_phi ~ sin(k_z z), H_r/H_phi ~ cos(k_z z);
потери на торцах НЕ нулевые, P_пр = P_бок + P_торц ~ (l+2a);
Q_пр = (pi*f*mu0*a/R_пов)*l/(l+2a) = (a/delta_ск)*l/(l+2a).
Названия по методичке: Q_пр, Q_д, Q_0.
"""

import os
import re
import math
import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

matplotlib.rcParams["mathtext.fontset"] = "cm"        # Computer Modern для формул
matplotlib.rcParams["font.family"] = "DejaVu Serif"   # кириллица в тексте

# ============================================================
# НАСТРОЙКИ
# ============================================================
OUTDIR   = "formulas"
DPI      = 300
FS       = 15        # кегль
WRAP     = 88        # символов в строке текста
WIDTH_IN = 6.6       # целевая ширина картинки, дюймы
GAP_LINE = 0.05      # между строками абзаца
GAP_BLOCK = 0.17     # между блоками

C_LIGHT = 299792458.0
MU0     = 4.0e-7 * math.pi
A_RAD   = 0.0335
L_RES   = 5.0 * A_RAD
NU_12   = 7.015586669815619
EPS_R   = 9.8
SIGMA   = {"Al": 2.62e7, "Au": 3.57e7}


# ============================================================
# КИРИЛЛИЦА В ИНДЕКСАХ -> ЛАТИНИЦА (mathtext не знает кириллицу)
# ============================================================
_SUB = {'кр': 'cr', 'рез': 'res', 'пов': 's', 'пр': 'w', 'д': 'd', 'ск': 'sk',
        'ф': 'ph', 'гр': 'gr', 'в': 'w', 'бок': 'side', 'торц': 'cap', 'п': 'p'}
_TR = {'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'e','ж':'zh','з':'z','и':'i',
       'й':'i','к':'k','л':'l','м':'m','н':'n','о':'o','п':'p','р':'r','с':'s','т':'t',
       'у':'u','ф':'f','х':'kh','ц':'ts','ч':'ch','ш':'sh','щ':'shch','ъ':'','ы':'y',
       'ь':'','э':'e','ю':'yu','я':'ya'}


def translit(s):
    if s in _SUB:
        return _SUB[s]
    out = []
    for ch in s:
        low = ch.lower()
        if low in _TR:
            t = _TR[low]
            out.append(t.capitalize() if ch.isupper() else t)
        else:
            out.append(ch)
    return "".join(out)


def brace(s, i):
    """s[i]=='{' -> (содержимое, индекс после '}')"""
    d = 0
    for j in range(i, len(s)):
        if s[j] == '{':
            d += 1
        elif s[j] == '}':
            d -= 1
            if d == 0:
                return s[i+1:j], j+1
    return s[i+1:], len(s)


def unwrap(s, cmds):
    """Снимает \\textbf{...} и т.п. с учётом вложенных скобок."""
    for c in cmds:
        p = '\\' + c
        while p in s:
            i = s.index(p); j = i + len(p)
            while j < len(s) and s[j] == ' ':
                j += 1
            if j < len(s) and s[j] == '{':
                inner, j2 = brace(s, j)
                s = s[:i] + inner + s[j2:]
            else:
                s = s[:i] + s[i+len(p):]
    return s


def clean_math(m):
    """Приводит формулу к подмножеству mathtext."""
    m = m.replace(r'\dfrac', r'\frac').replace(r'\tfrac', r'\frac')
    for b in [r'\displaystyle', r'\limits', r'\!', r'\bigl', r'\bigr', r'\Bigl',
              r'\Bigr', r'\big', r'\Big', r'\bigg', r'\Bigg']:
        m = m.replace(b, '')
    m = m.replace(r'\left.', '').replace(r'\right.', '')
    m = m.replace(r'\left', '').replace(r'\right', '')
    m = m.replace(r'\bm', r'\mathbf').replace(r'\boldsymbol', r'\mathbf')
    m = m.replace(r'\checkmark', r'\bullet')
    while r'\underbrace' in m:
        i = m.index(r'\underbrace'); j = i + len(r'\underbrace')
        while j < len(m) and m[j] == ' ': j += 1
        inner, j = brace(m, j); sub = ''
        if j < len(m) and m[j] == '_':
            j += 1
            if j < len(m) and m[j] == '{':
                sub, j = brace(m, j)
            elif j < len(m):
                sub, j = m[j], j+1
        m = m[:i] + '{' + inner + '}_{' + sub + '}' + m[j:]
    while r'\boxed' in m:
        i = m.index(r'\boxed'); j = i + len(r'\boxed')
        while j < len(m) and m[j] == ' ': j += 1
        inner, j = brace(m, j); m = m[:i] + inner + m[j:]
    while r'\phantom' in m:
        i = m.index(r'\phantom'); j = i + len(r'\phantom')
        while j < len(m) and m[j] == ' ': j += 1
        _, j = brace(m, j); m = m[:i] + ' ' + m[j:]
    m = re.sub(r'\\(text|mathrm|mathbf|textrm)\{([^{}]*)\}',
               lambda mo: '\\' + mo.group(1) + '{' + translit(mo.group(2)) + '}', m)
    m = m.replace(r'\text', r'\mathrm')
    return re.sub(r'\s+', ' ', m).strip()


def split_math(s):
    """Строка -> [('t', текст) | ('m', формула), ...]"""
    out = []
    for p in re.split(r'(\$[^$]*\$)', s):
        if not p:
            continue
        if p.startswith('$') and p.endswith('$') and len(p) > 2:
            out.append(('m', clean_math(p[1:-1])))
        else:
            p = unwrap(p, ('textbf', 'emph', 'textit', 'textrm', 'text'))
            p = p.replace(r'\%', '%').replace(r'\&', '&').replace(r'\_', '_')
            p = p.replace('{,}', ',').replace('---', '—').replace('--', '–')
            p = re.sub(r'\\[a-zA-Z]+', '', p)
            p = re.sub(r'[{}$]', '', p)
            p = re.sub(r'\s+', ' ', p).strip()
            if p:
                out.append(('t', p))
    return out


def build_lines(parts, wrap=WRAP):
    """Перенос по словам; формула — неделимый токен."""
    lines = []; cur = ""; n = 0

    def flush():
        nonlocal cur, n
        if cur.strip():
            lines.append(cur.rstrip())
        cur = ""; n = 0

    for kind, val in parts:
        if kind == 'm':
            tok = '$' + val + '$'; L = len(val) + 2
            if n and n + 1 + L > wrap:
                flush()
            cur += ((' ' if cur else '') + tok); n += (1 if n else 0) + L
        else:
            for w in val.split():
                if n and n + 1 + len(w) > wrap:
                    flush()
                cur += ((' ' if cur else '') + w); n += (1 if n else 0) + len(w)
    flush()
    return lines


# ============================================================
# РАЗБОР ТЕЛА НА БЛОКИ
# ============================================================
def parse(body, fs=FS):
    s = re.sub(r'\\begin\{minipage\}\{[^}]*\}|\\end\{minipage\}', '', body)
    s = s.replace(r'\centering', '').replace(r'\noindent', '').replace(r'\par', '')

    tabs, alns = [], []

    def gt(mo):
        tabs.append(mo.group(1)); return "\n@@T%d@@\n" % (len(tabs)-1)

    def ga(mo):
        alns.append(mo.group(1)); return "\n@@A%d@@\n" % (len(alns)-1)

    s = re.sub(r'\\begin\{tabular\}\{[^}]*\}(.*?)\\end\{tabular\}', gt, s, flags=re.S)
    s = re.sub(r'\$?\s*\\begin\{aligned\}(.*?)\\end\{aligned\}\s*\$?', ga, s, flags=re.S)
    # ГЛАВНОЕ: склеиваем многострочные $...$ ДО разбиения на строки
    s = re.sub(r'\$[^$]*\$', lambda mo: re.sub(r'\s*\n\s*', ' ', mo.group(0)), s, flags=re.S)
    s = re.sub(r'\\vspace\*?\{([0-9.]+)cm\}',
               lambda m: "\n@@G%s@@\n" % float(m.group(1)), s)

    blocks = []
    for raw in s.split('\n'):
        ln = raw.strip()
        if not ln:
            continue
        g = re.fullmatch(r'@@G([0-9.]+)@@', ln)
        if g:
            blocks.append({'k': 'gap', 'h': float(g.group(1))*0.39}); continue
        a = re.fullmatch(r'@@A(\d+)@@', ln)
        if a:
            rows = []
            for r in alns[int(a.group(1))].split(r'\\'):
                r = re.sub(r'\[[0-9]+pt\]', '', r).strip()
                if not r:
                    continue
                if '&' in r:
                    lhs, rhs = r.split('&', 1)
                    rows.append((clean_math(lhs.strip()),
                                 clean_math(rhs.strip().lstrip('='))))
                else:
                    rows.append((None, clean_math(r)))
            blocks.append({'k': 'align', 'rows': rows, 'fs': fs}); continue
        t = re.fullmatch(r'@@T(\d+)@@', ln)
        if t:
            rows = []
            for rr in tabs[int(t.group(1))].split(r'\\'):
                rr = re.sub(r'\[[0-9]+pt\]', '', rr)
                rr = re.sub(r'\\(toprule|midrule|bottomrule|hline)', '', rr.strip()).strip()
                if rr:
                    rows.append([split_math(c.strip()) for c in rr.split('&')])
            if rows:
                blocks.append({'k': 'table', 'rows': rows, 'fs': fs-2})
            continue
        for piece in re.split(r'\\\\(?:\[[0-9]+pt\])?', ln):
            piece = piece.strip()
            if not piece:
                continue
            bold = bool(re.search(r'\\textbf\{', piece))
            boxed = r'\boxed' in piece
            parts = split_math(piece)
            if not parts:
                continue
            if len(parts) == 1 and parts[0][0] == 'm':
                blocks.append({'k': 'math', 's': '$'+parts[0][1]+'$',
                               'fs': fs, 'bold': False, 'box': boxed})
            else:
                for i, l in enumerate(build_lines(parts)):
                    blocks.append({'k': 'text', 's': l, 'fs': fs,
                                   'bold': bold, 'box': boxed and i == 0})
    return blocks


# ============================================================
# РЕНДЕР: замер -> раскладка -> сохранение
# ============================================================
def render(body, path, fs=FS, width_in=WIDTH_IN):
    blocks = parse(body, fs)
    fig = plt.figure(figsize=(width_in, 20), dpi=DPI)
    rend = fig.canvas.get_renderer()
    bad = []

    def mk(s, size, bold):
        t = fig.text(0.5, 0.5, s, fontsize=size,
                     fontweight='bold' if bold else 'normal')
        try:
            bb = t.get_window_extent(renderer=rend)
            return t, bb.width/DPI, bb.height/DPI
        except Exception as e:
            t.remove()
            bad.append((s[:60], str(e).splitlines()[-1][:60]))
            t = fig.text(0.5, 0.5, re.sub(r'[\\${}]', ' ', s), fontsize=size)
            bb = t.get_window_extent(renderer=rend)
            return t, bb.width/DPI, bb.height/DPI

    items = []
    for b in blocks:
        if b['k'] == 'gap':
            items.append([b, None, 0., 0.]); continue
        if b['k'] == 'align':
            rows = []
            for lhs, rhs in b['rows']:
                tl = mk('$'+lhs+'$', b['fs'], False) if lhs else None
                tr = mk('$='+rhs+'$', b['fs'], False)
                rows.append((tl, tr))
            items.append([b, rows, 0., 0.]); continue
        if b['k'] == 'table':
            nc = max(len(r) for r in b['rows']); cells = []
            for r in b['rows']:
                row = []
                for c in range(nc):
                    parts = r[c] if c < len(r) else []
                    s = " ".join(('$'+v+'$' if k == 'm' else v) for k, v in parts)
                    row.append(mk(s, b['fs'], False))
                cells.append(row)
            items.append([b, cells, 0., 0.]); continue
        t, w, h = mk(b['s'], b['fs'], b['bold'])
        items.append([b, t, w, h])

    for b, obj, _, _ in items:
        if b['k'] == 'table':
            b['cw'] = [max(row[c][1] for row in obj)+0.20 for c in range(len(obj[0]))]
        if b['k'] == 'align':
            b['lw'] = max([(r[0][1] if r[0] else 0.) for r in obj])
            b['rw'] = max([r[1][1] for r in obj])

    need = [w for b, t, w, h in items if t is not None]
    need += [sum(b['cw']) for b, o, _, _ in items if b['k'] == 'table']
    need += [b['lw']+b['rw']+0.12 for b, o, _, _ in items if b['k'] == 'align']
    W = max(need + [width_in-0.7]) + 0.7

    def hgt(b, obj, w, h):
        if b['k'] == 'gap':
            return b['h']
        if b['k'] == 'table':
            return sum(max(c[2] for c in row)+0.07 for row in obj)
        if b['k'] == 'align':
            return sum(max((r[0][2] if r[0] else 0), r[1][2])+0.10 for r in obj)
        return h + GAP_LINE

    H = 0.42 + sum(hgt(*it) for it in items) + \
        GAP_BLOCK*sum(1 for it in items if it[0]['k'] != 'gap')
    H = max(H, 0.9)
    fig.set_size_inches(W, H)

    y = H - 0.22
    for b, obj, w, h in items:
        k = b['k']
        if k == 'gap':
            y -= b['h']; continue
        if k == 'table':
            x0 = (W - sum(b['cw']))/2
            for row in obj:
                rh = max(c[2] for c in row); x = x0
                for c in range(len(row)):
                    row[c][0].set_position(((x + b['cw'][c]/2)/W, (y - rh/2)/H))
                    row[c][0].set_ha('center'); row[c][0].set_va('center')
                    x += b['cw'][c]
                y -= rh + 0.07
            y -= GAP_BLOCK; continue
        if k == 'align':
            tot = b['lw'] + b['rw'] + 0.12
            xeq = (W - tot)/2 + b['lw']
            for tl, tr in obj:
                rh = max((tl[2] if tl else 0), tr[2])
                if tl:
                    tl[0].set_position(((xeq-0.06)/W, (y-rh/2)/H))
                    tl[0].set_ha('right'); tl[0].set_va('center')
                tr[0].set_position(((xeq+0.06)/W, (y-rh/2)/H))
                tr[0].set_ha('left'); tr[0].set_va('center')
                y -= rh + 0.10
            y -= GAP_BLOCK; continue
        obj.set_position((0.5, y/H)); obj.set_ha('center'); obj.set_va('top')
        if b['box']:
            fig.patches.append(Rectangle((((W-w)/2-0.13)/W, (y-h-0.07)/H),
                                         (w+0.26)/W, (h+0.14)/H,
                                         transform=fig.transFigure, fill=False,
                                         lw=1.1, ec='black'))
        y -= h + GAP_LINE

    fig.savefig(path, dpi=DPI, facecolor='white', bbox_inches='tight', pad_inches=0.14)
    plt.close(fig)
    return bad


# ============================================================
# КОНТРОЛЬНЫЙ ПРИМЕР (числа считаются)
# ============================================================
def numeric_table():
    kappa = NU_12 / A_RAD
    rows = []
    for p in (34, 44):
        beta = p*math.pi/L_RES
        omega = C_LIGHT/math.sqrt(EPS_R)*math.sqrt(kappa**2 + beta**2)
        f = omega/(2*math.pi)
        for name in ("Al", "Au"):
            s = SIGMA[name]
            delta = math.sqrt(2.0/(omega*MU0*s))
            Rs = 1.0/(s*delta)
            Qside = A_RAD/delta
            Qcaps = L_RES/(2.0*delta)
            Qpr = 1.0/(1.0/Qside + 1.0/Qcaps)
            rows.append("%d & %s & %.3f & %.3f & %.4f & %.0f & %.0f & %.0f & %.0f"
                        % (p, name, f/1e9, delta*1e6, Rs, Qside, Qcaps, Qpr, Qpr*Rs))
    return " \\\\\n".join(rows)


# ============================================================
# ФОРМУЛЫ
# ============================================================
FORMULAS = []


def add(name, body, fs=FS):
    FORMULAS.append((name, body, fs))


add("01_helmholtz.png", r"""
Уравнения Гельмгольца для комплексных амплитуд полей:
\vspace{0.3cm}
$\Delta \dot{\mathbf{E}} + k^2 \dot{\mathbf{E}} = 0, \qquad
 \Delta \dot{\mathbf{H}} + k^2 \dot{\mathbf{H}} = 0$
\vspace{0.25cm}
волновое число неограниченной среды
$k = \omega\sqrt{\varepsilon_0\varepsilon_r\mu_0\mu_r}
 = \dfrac{\omega}{c}\sqrt{\varepsilon_r\mu_r}$
""")

add("02_boundary.png", r"""
Граничные условия на идеально проводящей стенке $L$:
\vspace{0.3cm}
$E_\tau|_L = 0, \qquad H_n|_L = 0$
\vspace{0.25cm}
$E_\tau$ --- тангенциальная компонента электрического поля,
$H_n$ --- нормальная компонента магнитного поля.
""")

add("03_ez_solution.png", r"""
Продольная компонента $E_z$ в цилиндрических координатах:
\vspace{0.3cm}
$\dot{E}_z = \left[A_m J_m(\kappa r) + B_m N_m(\kappa r)\right]
 \left[C_m\cos(m\varphi) + D_m\sin(m\varphi)\right]e^{-\gamma z}$
\vspace{0.25cm}
Конечность поля на оси: $B_m = 0$, так как $N_m\to\infty$ при $r\to 0$.
Произвольный выбор начала отсчёта угла: $D_m = 0$.
\vspace{0.25cm}
$\boxed{\dot{E}_z = E_0 J_m(\kappa r)\cos(m\varphi)\,e^{-\gamma z}}$
""")

add("04_kappa_E.png", r"""
Граничное условие на боковой стенке: $E_z|_{r=a}=0$, откуда
\vspace{0.3cm}
$J_m(\kappa a) = 0 \quad\Rightarrow\quad \kappa a = \nu_{mn}$
\vspace{0.25cm}
$\nu_{mn}$ --- $n$-й корень функции Бесселя $J_m(x)$. Для E-волн
\vspace{0.2cm}
$\boxed{\kappa_E = \dfrac{\nu_{mn}}{a}}$
\vspace{0.25cm}
Для варианта 6 ($E_{12}$): $m=1$, $n=2$, $\nu_{12}=7{,}016$.
""")

add("05_dispersion.png", r"""
Дисперсионное уравнение ($\gamma$ --- постоянная распространения, $e^{-\gamma z}$):
\vspace{0.3cm}
$\gamma^2 = \kappa^2 - k^2
 = \left(\dfrac{\nu_{mn}}{a}\right)^2 - \omega^2\varepsilon_0\varepsilon_r\mu_0\mu_r$
\vspace{0.25cm}
Эквивалентная форма: $\gamma^2 + \kappa^2 = k^2$.
Для распространяющейся волны $\gamma = i\beta$, $\beta^2 = k^2-\kappa^2 > 0$.
""")

add("06_f_cr.png", r"""
Критическая частота моды ($\gamma = 0$):
\vspace{0.3cm}
$\boxed{f_{\text{кр}} = \dfrac{\kappa}{2\pi\sqrt{\varepsilon_0\varepsilon_r\mu_0\mu_r}}
 = \dfrac{c\,\nu_{mn}}{2\pi a\sqrt{\varepsilon_r\mu_r}}}$
\vspace{0.3cm}
Воздух ($\varepsilon_r=1$): $f_{\text{кр}} = 10{,}0$ ГГц, $a = 33{,}5$ мм.
MgO ($\varepsilon_r=9{,}8$): $f_{\text{кр}} = 3{,}19$ ГГц.
""")

add("07_Z_wave.png", r"""
Волновое сопротивление E-волны: $Z_{\text{в}} = E_r/H_\varphi$
\vspace{0.25cm}
Связь поперечных компонент с продольной:
$E_r = -\dfrac{\gamma}{\kappa_E^2}\dfrac{\partial E_z}{\partial r},\qquad
 H_\varphi = -\dfrac{i\omega\varepsilon_0\varepsilon_r}{\kappa_E^2}
 \dfrac{\partial E_z}{\partial r}$
\vspace{0.25cm}
При $\gamma = i\beta$:
\vspace{0.2cm}
$\boxed{Z_E = \dfrac{Z_0}{\sqrt{\varepsilon_r}}
 \sqrt{1-\left(\dfrac{f_{\text{кр}}}{f}\right)^2}},\qquad
 Z_0=\sqrt{\dfrac{\mu_0}{\varepsilon_0}}\approx 377\ \text{Ом}$
""")

add("08_velocities.png", r"""
Фазовая скорость $v_{\text{ф}}=\omega/\beta$ и групповая $v_{\text{гр}}=d\omega/d\beta$:
\vspace{0.3cm}
$\boxed{v_{\text{ф}} = \dfrac{c}{\sqrt{\varepsilon_r}\sqrt{1-(f_{\text{кр}}/f)^2}}
 \qquad
 v_{\text{гр}} = \dfrac{c}{\sqrt{\varepsilon_r}}\sqrt{1-(f_{\text{кр}}/f)^2}}$
\vspace{0.3cm}
$v_{\text{ф}}\cdot v_{\text{гр}} = \dfrac{c^2}{\varepsilon_r}$,
при $f\to\infty$ обе скорости стремятся к $c/\sqrt{\varepsilon_r}$.
""")

add("09_lambda.png", r"""
Длина волны в волноводе $\lambda_{\text{в}} = v_{\text{ф}}/f$:
\vspace{0.3cm}
$\boxed{\lambda_{\text{в}} =
 \dfrac{\lambda_0}{\sqrt{\varepsilon_r}\sqrt{1-(f_{\text{кр}}/f)^2}}},
 \qquad \lambda_0=\dfrac{c}{f}$
""")

add("10_skin_depth.png", r"""
Толщина скин-слоя (убывание амплитуды в $e$ раз):
\vspace{0.3cm}
$\boxed{\delta_{\text{ск}} = \sqrt{\dfrac{2}{\omega\mu_0\sigma}}
 = \sqrt{\dfrac{1}{\pi f\mu_0\sigma}}}$
""")

add("11_R_surface.png", r"""
Поверхностное сопротивление стенки:
\vspace{0.3cm}
$\boxed{R_{\text{пов}} = \dfrac{1}{\sigma\delta_{\text{ск}}}
 = \sqrt{\dfrac{\pi f\mu_0}{\sigma}} = \dfrac{\omega\mu_0\delta_{\text{ск}}}{2}}$
\vspace{0.3cm}
Полезное тождество: $\dfrac{\omega\mu_0}{2R_{\text{пов}}}=\dfrac{1}{\delta_{\text{ск}}}$.
""")

add("12_f_res.png", r"""
Резонатор --- отрезок волновода длиной $l$, замкнутый торцами.
Условие полуволнового резонанса:
\vspace{0.25cm}
$k_z = \dfrac{p\pi}{l},\quad p=1,2,3,\ldots$
\vspace{0.25cm}
Из $k^2=\kappa_E^2+k_z^2$:
\vspace{0.2cm}
$\boxed{f_{\text{рез}} = \dfrac{c}{2\pi a\sqrt{\varepsilon_r}}
 \sqrt{\nu_{mn}^2+\left(\dfrac{p\pi a}{l}\right)^2}}$
\vspace{0.3cm}
Для $a=33{,}5$ мм, $l=5a$, MgO: в диапазон 10\ldots13 ГГц попадают
$p=34\ldots44$ (11 гармоник).
""")

add("13_field_components.png", r"""
\textbf{Компоненты поля моды $E_{mnp}$ в цилиндрическом резонаторе}
(торцы при $z=0$ и $z=l$)
\vspace{0.3cm}
Из граничного условия $E_\tau|_{z=0}=0$ следует $E_{\text{отр}}=+E_{\text{пад}}$.
Обозначив $E_0=2E_{\text{пад}}$, $\kappa_E=\nu_{mn}/a$, $k_z=p\pi/l$:
\vspace{0.25cm}
$\begin{aligned}
E_z &= E_0\,J_m(\kappa_E r)\cos(m\varphi)\,\cos(k_z z)\\[4pt]
E_r &= -E_0\,\frac{k_z}{\kappa_E}\,J'_m(\kappa_E r)\cos(m\varphi)\,\sin(k_z z)\\[4pt]
E_\varphi &= E_0\,\frac{k_z m}{\kappa_E^2 r}\,J_m(\kappa_E r)\sin(m\varphi)\,\sin(k_z z)\\[4pt]
H_r &= -i\,E_0\,\frac{\omega\varepsilon_0\varepsilon_r m}{\kappa_E^2 r}\,
        J_m(\kappa_E r)\sin(m\varphi)\,\cos(k_z z)\\[4pt]
H_\varphi &= -i\,E_0\,\frac{\omega\varepsilon_0\varepsilon_r}{\kappa_E}\,
        J'_m(\kappa_E r)\cos(m\varphi)\,\cos(k_z z)\\[4pt]
H_z &= 0
\end{aligned}$
\vspace{0.25cm}
Ключевое: $E_z\sim\cos(k_z z)$, поперечные $E\sim\sin(k_z z)$, все $H\sim\cos(k_z z)$.
""", fs=14)

add("14_field_check.png", r"""
\textbf{Проверка корректности поля}
\vspace{0.3cm}
1) Уравнение Максвелла $\nabla\cdot\mathbf{E}=0$:
$\frac{1}{r}\frac{\partial(rE_r)}{\partial r}
 +\frac{1}{r}\frac{\partial E_\varphi}{\partial\varphi}
 = +k_z E_0 J_m\cos(m\varphi)\sin(k_z z)$
$\frac{\partial E_z}{\partial z} = -k_z E_0 J_m\cos(m\varphi)\sin(k_z z)$
Сумма тождественно равна нулю.
\vspace{0.25cm}
2) Торцы $z=0$ и $z=l$: $\sin(k_z z)=0$, значит $E_r=E_\varphi=0$;
$\cos(k_z z)=\pm1$, значит $H_r$ и $H_\varphi$ максимальны.
\vspace{0.25cm}
3) Боковая стенка $r=a$: $J_m(\nu_{mn})=0$, значит $E_z=E_\varphi=0$ и $H_r=0$.
\vspace{0.25cm}
4) $E$ вещественно, $H$ мнимо --- поля в квадратуре, как и должно быть в резонаторе.
\vspace{0.25cm}
Если записать $E_z\sim\sin$ и $E_r\sim\sin$ одновременно, то
$\nabla\cdot\mathbf{E}\neq0$ --- такой набор полей недопустим.
""", fs=14)

add("15_W_E.png", r"""
\textbf{Энергия электрического поля}
\vspace{0.25cm}
$W_E = \dfrac{\varepsilon_0\varepsilon_r}{4}\int_V|\mathbf{E}|^2dV
 = \dfrac{\varepsilon_0\varepsilon_r}{4}\int_0^l\!\int_0^{2\pi}\!\int_0^a
 \left(|E_r|^2+|E_\varphi|^2+|E_z|^2\right)r\,dr\,d\varphi\,dz$
\vspace{0.25cm}
Интегралы по углам и по оси ($m\ge1$, $p\ge1$):
$\int_0^{2\pi}\cos^2(m\varphi)d\varphi=\int_0^{2\pi}\sin^2(m\varphi)d\varphi=\pi$
$\int_0^l\sin^2(k_z z)dz=\int_0^l\cos^2(k_z z)dz=\frac{l}{2}$
\vspace{0.25cm}
Радиальные интегралы (оба равны, так как $J_m(\nu_{mn})=0$):
$\int_0^a J_m^2(\kappa_E r)\,r\,dr=\frac{a^2}{2}\left[J'_m(\nu_{mn})\right]^2$
$\int_0^a\left\{\left[J'_m(\kappa_E r)\right]^2
 +\frac{m^2}{\kappa_E^2r^2}J_m^2(\kappa_E r)\right\}r\,dr
 =\frac{a^2}{2}\left[J'_m(\nu_{mn})\right]^2$
\vspace{0.25cm}
Отсюда, с учётом $\kappa_E^2+k_z^2=\omega^2\varepsilon_0\varepsilon_r\mu_0$:
$\int_V|\mathbf{E}|^2dV=E_0^2\frac{\pi l a^2}{4}
 \left[J'_m(\nu_{mn})\right]^2\frac{\omega^2\varepsilon_0\varepsilon_r\mu_0}{\kappa_E^2}$
\vspace{0.25cm}
$\boxed{W_E = \dfrac{\pi\varepsilon_0\varepsilon_r^2\omega^2 l a^4}
 {16\,c^2\nu_{mn}^2}\,E_0^2\left[J'_m(\nu_{mn})\right]^2}$
""", fs=14)

add("16_W_H.png", r"""
\textbf{Энергия магнитного поля и полная запасённая энергия}
\vspace{0.25cm}
$W_H = \dfrac{\mu_0}{4}\int_V|\mathbf{H}|^2dV
 = \dfrac{\mu_0(\omega\varepsilon_0\varepsilon_r)^2}{4\kappa_E^2}
 \cdot\frac{\pi l}{2}\cdot\frac{a^2}{2}\left[J'_m(\nu_{mn})\right]^2$
\vspace{0.25cm}
На резонансе $\omega^2\mu_0\varepsilon_0\varepsilon_r=k^2$, поэтому
$\mu_0(\omega\varepsilon_0\varepsilon_r)^2=\varepsilon_0\varepsilon_r k^2$ и
\vspace{0.15cm}
$\boxed{W_H = W_E}$ --- контроль правильности полей и частоты
\vspace{0.25cm}
Полная запасённая энергия: $\boxed{W = W_E + W_H = 2W_E}$
""", fs=14)

add("17_P_side.png", r"""
\textbf{Мощность потерь в стенках: боковая поверхность}
\vspace{0.25cm}
$P_{\text{пр}} = \dfrac{R_{\text{пов}}}{2}\oint_S|H_\tau|^2dS$
\vspace{0.25cm}
При $r=a$ касательная компонента --- только $H_\varphi$, так как $H_z=0$,
а $H_r$ нормальна и обращается в нуль вместе с $J_m(\nu_{mn})$:
$|H_\varphi(a)|^2 = \left(\frac{\omega\varepsilon_0\varepsilon_r}{\kappa_E}\right)^2
 E_0^2\left[J'_m(\nu_{mn})\right]^2\cos^2(m\varphi)\cos^2(k_z z)$
\vspace{0.2cm}
$\int_0^l\!\int_0^{2\pi}|H_\varphi(a)|^2 a\,d\varphi\,dz
 = E_0^2\frac{(\omega\varepsilon_0\varepsilon_r)^2}{\kappa_E^2}
 \left[J'_m(\nu_{mn})\right]^2\cdot a\cdot\pi\cdot\frac{l}{2}$
\vspace{0.25cm}
$\boxed{P_{\text{бок}} = \dfrac{\pi R_{\text{пов}}\,\omega^2\varepsilon_0^2
 \varepsilon_r^2 a^3 l}{4\nu_{mn}^2}E_0^2\left[J'_m(\nu_{mn})\right]^2}$
""", fs=14)

add("18_P_caps.png", r"""
\textbf{Мощность потерь в стенках: торцы $z=0$ и $z=l$}
\vspace{0.25cm}
На торце $\cos^2(k_z z)=1$, касательны обе компоненты $H_r$ и $H_\varphi$:
$|H_\tau|^2 = (\omega\varepsilon_0\varepsilon_r)^2E_0^2
 \left[\frac{m^2}{\kappa_E^4r^2}J_m^2\sin^2(m\varphi)
 +\frac{1}{\kappa_E^2}J_m'^2\cos^2(m\varphi)\right]$
\vspace{0.2cm}
$\int_0^{2\pi}\!\int_0^a\left(|H_r|^2+|H_\varphi|^2\right)r\,dr\,d\varphi
 = E_0^2\frac{(\omega\varepsilon_0\varepsilon_r)^2}{\kappa_E^2}
 \cdot\pi\cdot\frac{a^2}{2}\left[J'_m(\nu_{mn})\right]^2$
\vspace{0.2cm}
Торцов два, поэтому
$\boxed{P_{\text{торц}} = \dfrac{\pi R_{\text{пов}}\,\omega^2\varepsilon_0^2
 \varepsilon_r^2 a^4}{2\nu_{mn}^2}E_0^2\left[J'_m(\nu_{mn})\right]^2}$
\vspace{0.25cm}
Потери на торцах не равны нулю: там $E_\tau=0$, но $H_\tau$ максимален,
поверхностный ток $J_s=[n\times H]$ максимален. Линии $E_z$ приходят на торец
нормально и замыкаются током проводимости.
""", fs=14)

add("19_P_total.png", r"""
\textbf{Суммарная мощность потерь в проводящих стенках}
\vspace{0.3cm}
$P_{\text{пр}} = P_{\text{бок}} + P_{\text{торц}}$
\vspace{0.25cm}
$\boxed{P_{\text{пр}} = \dfrac{\pi R_{\text{пов}}\,\omega^2\varepsilon_0^2
 \varepsilon_r^2 a^3\,(l+2a)}{4\nu_{mn}^2}
 E_0^2\left[J'_m(\nu_{mn})\right]^2}$
\vspace{0.3cm}
Распределение потерь по поверхностям:
$\dfrac{P_{\text{бок}}}{P_{\text{пр}}}=\dfrac{l}{l+2a},\qquad
 \dfrac{P_{\text{торц}}}{P_{\text{пр}}}=\dfrac{2a}{l+2a}$
\vspace{0.2cm}
Для $l=5a$: $\dfrac{5}{7}=71{,}4\%$ на боковую стенку и
$\dfrac{2}{7}=28{,}6\%$ на торцы.
""", fs=14)

add("20_Q_pr_derivation.png", r"""
\textbf{Вывод собственной добротности по потерям в стенках}
\vspace{0.25cm}
По определению (1.27) при $W=2W_E$:
$Q_{\text{пр}} = \omega_0\dfrac{W}{P_{\text{пр}}}
 = \omega_0\dfrac{2W_E}{P_{\text{пр}}}$
\vspace{0.2cm}
$Q_{\text{пр}} = \omega_0\cdot
 \dfrac{2\cdot\dfrac{\pi\varepsilon_0\varepsilon_r^2\omega_0^2 l a^4}
 {16c^2\nu_{mn}^2}E_0^2\left[J'_m(\nu_{mn})\right]^2}
 {\dfrac{\pi R_{\text{пов}}\omega_0^2\varepsilon_0^2\varepsilon_r^2 a^3(l+2a)}
 {4\nu_{mn}^2}E_0^2\left[J'_m(\nu_{mn})\right]^2}$
\vspace{0.25cm}
Сокращаются $\pi$, $\omega_0^2$, $\varepsilon_r^2$, $\nu_{mn}^2$, $E_0^2$,
$\left[J'_m(\nu_{mn})\right]^2$, $a^3$ и одна степень $\varepsilon_0$:
$Q_{\text{пр}} = \omega_0\cdot\frac{2}{16}\cdot\frac{4}{1}\cdot
 \frac{l\,a}{c^2\varepsilon_0 R_{\text{пов}}(l+2a)}
 = \frac{\omega_0\,l\,a}{2c^2\varepsilon_0 R_{\text{пов}}(l+2a)}$
\vspace{0.25cm}
Учитывая $c^2\varepsilon_0 = 1/\mu_0$ и $\omega_0=2\pi f_{\text{рез}}$:
\vspace{0.2cm}
$\boxed{Q_{\text{пр}} = \frac{\omega_0\mu_0 a}{2R_{\text{пов}}}\cdot\frac{l}{l+2a}
 = \frac{\pi f_{\text{рез}}\mu_0 a}{R_{\text{пов}}}\cdot\frac{l}{l+2a}}$
""", fs=14)

add("21_Q_pr.png", r"""
\textbf{Собственная добротность резонатора, обусловленная
потерями в проводящих стенках} (мода $E_{mnp}$, $p\ge1$)
\vspace{0.35cm}
$\boxed{Q_{\text{пр}} = \frac{\pi f_{\text{рез}}\,\mu_0\,a}{R_{\text{пов}}}
 \cdot\frac{l}{l+2a} = \frac{a}{\delta_{\text{ск}}}\cdot\frac{l}{l+2a}}$
\vspace{0.35cm}
Так как $R_{\text{пов}}=\dfrac{\omega_0\mu_0\delta_{\text{ск}}}{2}$, то
$\dfrac{\omega_0\mu_0}{2R_{\text{пов}}}=\dfrac{1}{\delta_{\text{ск}}}$.
\vspace{0.3cm}
Для $l=5a$: $\dfrac{l}{l+2a}=\dfrac{5}{7}$, то есть
$Q_{\text{пр}}=\dfrac{5}{7}\cdot\dfrac{a}{\delta_{\text{ск}}}$.
\vspace{0.3cm}
Все бесселевы множители и амплитуда $E_0$ сократились: результат зависит
только от $a$, $l$ и частоты, но не от индексов $m$, $n$, $p$.
""", fs=14)

add("22_Q_dielectric.png", r"""
\textbf{Собственная добротность, обусловленная потерями в диэлектрике}
\vspace{0.3cm}
$P_{\text{д}} = \dfrac{1}{2}\int_V \mathbf{J}\mathbf{E}^*dV
 = \dfrac{\omega\varepsilon_0\varepsilon_r\,\mathrm{tg}\,\delta}{2}
 \int_V|\mathbf{E}|^2dV
 = 2\omega\,\mathrm{tg}\,\delta\cdot W_E = \omega\,\mathrm{tg}\,\delta\cdot W$
\vspace{0.3cm}
$\boxed{Q_{\text{д}} = \dfrac{\omega_0 W}{P_{\text{д}}}
 = \dfrac{1}{\mathrm{tg}\,\delta}}$
\vspace{0.3cm}
При однородном заполнении $Q_{\text{д}}$ не зависит ни от геометрии,
ни от типа колебаний. Воздух: $\mathrm{tg}\,\delta\approx0$, $Q_{\text{д}}\to\infty$.
""", fs=14)

add("23_Q_total.png", r"""
\textbf{Полная собственная добротность резонатора}
\vspace{0.35cm}
$\boxed{\dfrac{1}{Q_0} = \dfrac{1}{Q_{\text{пр}}} + \dfrac{1}{Q_{\text{д}}}
 \qquad\Longleftrightarrow\qquad
 Q_0 = \dfrac{Q_{\text{пр}}\,Q_{\text{д}}}{Q_{\text{пр}}+Q_{\text{д}}}}$
\vspace{0.35cm}
$Q_{\text{пр}}$ --- потери в проводящих стенках (боковая поверхность и торцы),
$Q_{\text{д}}$ --- потери в диэлектрическом заполнении.
\vspace{0.3cm}
Итоговая добротность всегда меньше меньшей из парциальных.
Воздушное заполнение: $Q_0 = Q_{\text{пр}}$.
""", fs=14)

add("24_numeric_example.png", r"""
\textbf{Контрольный пример: вариант 6}
$a=33{,}5$ мм, $l=5a=167{,}5$ мм, $E_{12}$, MgO ($\varepsilon_r=9{,}8$)
\vspace{0.3cm}
\begin{tabular}{ccccccccc}
\toprule
$p$ & Металл & $f_{\text{рез}}$, ГГц & $\delta_{\text{ск}}$, мкм &
$R_{\text{пов}}$, Ом & $Q_{\text{бок}}$ & $Q_{\text{торц}}$ &
$Q_{\text{пр}}$ & $G$, Ом \\
\midrule
__ROWS__ \\
\bottomrule
\end{tabular}
\vspace{0.3cm}
Проверка: $Q_{\text{пр}}=\left(1/Q_{\text{бок}}+1/Q_{\text{торц}}\right)^{-1}
=\frac{5}{7}\,a/\delta_{\text{ск}}$.
""", fs=12)

add("25_summary_table.png", r"""
\textbf{Сводная таблица формул}
\vspace{0.3cm}
\begin{tabular}{ll}
\toprule
Величина & Формула \\
\midrule
Критическая частота &
$f_{\text{кр}}=\dfrac{c\,\nu_{mn}}{2\pi a\sqrt{\varepsilon_r\mu_r}}$ \\[8pt]
Волновое сопротивление &
$Z_E=\dfrac{Z_0}{\sqrt{\varepsilon_r}}\sqrt{1-(f_{\text{кр}}/f)^2}$ \\[8pt]
Фазовая скорость &
$v_{\text{ф}}=\dfrac{c}{\sqrt{\varepsilon_r}\sqrt{1-(f_{\text{кр}}/f)^2}}$ \\[8pt]
Групповая скорость &
$v_{\text{гр}}=\dfrac{c}{\sqrt{\varepsilon_r}}\sqrt{1-(f_{\text{кр}}/f)^2}$ \\[8pt]
Длина волны в волноводе &
$\lambda_{\text{в}}=\dfrac{\lambda_0}{\sqrt{\varepsilon_r}\sqrt{1-(f_{\text{кр}}/f)^2}}$ \\[8pt]
Толщина скин-слоя &
$\delta_{\text{ск}}=\sqrt{1/(\pi f\mu_0\sigma)}$ \\[8pt]
Поверхностное сопротивление &
$R_{\text{пов}}=1/(\sigma\delta_{\text{ск}})$ \\[8pt]
Резонансная частота &
$f_{\text{рез}}=\dfrac{c}{2\pi a\sqrt{\varepsilon_r}}
 \sqrt{\nu_{mn}^2+(p\pi a/l)^2}$ \\[8pt]
Добротность по стенкам &
$Q_{\text{пр}}=\dfrac{\pi f_{\text{рез}}\mu_0 a}{R_{\text{пов}}}\cdot\dfrac{l}{l+2a}$ \\[8pt]
Добротность по диэлектрику &
$Q_{\text{д}}=1/\mathrm{tg}\,\delta$ \\[8pt]
Полная собственная добротность &
$Q_0=\left(1/Q_{\text{пр}}+1/Q_{\text{д}}\right)^{-1}$ \\
\bottomrule
\end{tabular}
""", fs=13)


# ============================================================
# ЗАПУСК
# ============================================================
def main():
    global OUTDIR, DPI
    ap = argparse.ArgumentParser(description="Генератор формул (matplotlib)")
    ap.add_argument("--outdir", default=OUTDIR)
    ap.add_argument("--dpi", type=int, default=DPI)
    ap.add_argument("--only", default=None, help="подстрока имени файла")
    args = ap.parse_args()
    OUTDIR, DPI = args.outdir, args.dpi

    os.makedirs(OUTDIR, exist_ok=True)
    table = numeric_table()
    ok = warn = fail = 0
    for name, body, fs in FORMULAS:
        if args.only and args.only not in name:
            continue
        try:
            bad = render(body.replace("__ROWS__", table),
                         os.path.join(OUTDIR, name), fs=fs)
            if bad:
                warn += 1
                print("⚠ %-30s упрощено: %d" % (name, len(bad)))
                for s, e in bad[:2]:
                    print("     %s  |  %s" % (s, e))
            else:
                ok += 1
                print("✓ %s" % name)
        except Exception as e:
            fail += 1
            print("✗ %-30s %s: %s" % (name, type(e).__name__, str(e)[:110]))

    print("\n" + "="*60)
    print("Готово: %d чисто, %d с упрощением, %d ошибок  ->  %s/"
          % (ok, warn, fail, OUTDIR))
    print("="*60)


if __name__ == "__main__":
    main()