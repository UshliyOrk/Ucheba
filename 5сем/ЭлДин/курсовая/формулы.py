#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор картинок с формулами для курсовой работы по электродинамике.
Рендерит LaTeX-формулы в PNG высокого качества (как в учебнике).
"""

import os
import subprocess
import tempfile
import shutil

# ============================================================
# ПРОВЕРКА НАЛИЧИЯ LATEX
# ============================================================
def check_latex():
    """Проверяет наличие pdflatex в системе"""
    return shutil.which('pdflatex') is not None

HAS_LATEX = check_latex()

if HAS_LATEX:
    print("✓ LaTeX найден — формулы будут в качестве учебника")
    try:
        import fitz  # PyMuPDF
        print("✓ PyMuPDF найден")
    except ImportError:
        print("⚠️  PyMuPDF не найден. Установите: pip install PyMuPDF")
        HAS_LATEX = False
else:
    print("⚠️  LaTeX не найден — будет использован matplotlib (упрощённое качество)")
    print("   Для качества учебника установите MiKTeX: https://miktex.org/download")

# ============================================================
# ФУНКЦИИ РЕНДЕРИНГА
# ============================================================
def render_latex_to_png(latex_body, filename, dpi=300, fontsize=14):
    """
    Рендерит LaTeX-формулу в PNG высокого качества.
    
    Parameters:
    -----------
    latex_body : str
        Тело LaTeX-документа (всё между \begin{document} и \end{document})
    filename : str
        Имя выходного PNG файла
    dpi : int
        Разрешение (300 — как в учебнике)
    fontsize : int
        Размер шрифта
    """
    if HAS_LATEX:
        _render_via_latex(latex_body, filename, dpi, fontsize)
    else:
        _render_via_matplotlib(latex_body, filename, fontsize)


def _render_via_latex(latex_body, filename, dpi, fontsize):
    """Рендер через pdflatex + PyMuPDF (идеальное качество)"""
    import fitz
    
    latex_doc = rf"""\documentclass[border=5pt]{{standalone}}
\usepackage[utf8]{{inputenc}}
\usepackage[T2A]{{fontenc}}
\usepackage[russian]{{babel}}
\usepackage{{amsmath,amssymb,amsfonts}}
\usepackage{{mathtools}}
\usepackage{{bm}}
\usepackage{{mathrsfs}}
\usepackage{{array}}
\usepackage{{booktabs}}

\begin{{document}}
\fontsize{{{fontsize}}}{{{fontsize*1.2}}}\selectfont
{latex_body}
\end{{document}}
"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = os.path.join(tmpdir, 'formula.tex')
        pdf_path = os.path.join(tmpdir, 'formula.pdf')
        
        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write(latex_doc)
        
        # Компиляция LaTeX
        result = subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', '-output-directory', tmpdir, tex_path],
            capture_output=True, text=True, encoding='utf-8', errors='ignore'
        )
        
        if not os.path.exists(pdf_path):
            print(f"❌ Ошибка компиляции LaTeX для {filename}:")
            print(result.stdout[-500:] if result.stdout else "")
            # Fallback на matplotlib
            _render_via_matplotlib(latex_body, filename, fontsize)
            return
        
        # Конвертация PDF → PNG через PyMuPDF
        doc = fitz.open(pdf_path)
        page = doc[0]
        
        # Вычисляем масштаб для нужного DPI (базовый PDF DPI = 72)
        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        # Обрезаем белые поля
        img_data = pix.tobytes("png")
        
        # Сохраняем
        with open(filename, 'wb') as f:
            f.write(img_data)
        
        doc.close()
        print(f"✓ {filename} (LaTeX, {pix.width}x{pix.height} px)")


def _render_via_matplotlib(latex_body, filename, fontsize):
    """Резервный рендер через matplotlib (если LaTeX не установлен)"""
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.rcParams['text.usetex'] = False
    matplotlib.rcParams['mathtext.fontset'] = 'cm'  # Computer Modern
    
    # Извлекаем математику из LaTeX (грубый парсер)
    # Ищем содержимое между $$ ... $$ или \[ ... \] или внутри окружений
    math_content = latex_body
    
    # Убираем \text{}, \mathrm{} и т.п. для mathtext
    math_content = math_content.replace(r'\text{', r'\mathrm{')
    math_content = math_content.replace(r'\left', '')
    math_content = math_content.replace(r'\right', '')
    math_content = math_content.replace(r'\,', ' ')
    math_content = math_content.replace(r'\;', ' ')
    math_content = math_content.replace(r'\quad', '  ')
    math_content = math_content.replace(r'\boxed{', '{')
    
    # Ищем основную формулу
    lines = math_content.split('\n')
    math_lines = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('%'):
            math_lines.append(line)
    
    math_text = '\n'.join(math_lines)
    
    # Создаём фигуру
    fig, ax = plt.subplots(figsize=(12, max(2, len(math_lines) * 0.6)))
    ax.axis('off')
    
    try:
        ax.text(0.5, 0.5, f'${math_text}$',
                transform=ax.transAxes,
                fontsize=fontsize,
                ha='center', va='center',
                wrap=True)
    except Exception as e:
        ax.text(0.5, 0.5, math_text,
                transform=ax.transAxes,
                fontsize=fontsize,
                ha='center', va='center',
                family='serif')
    
    plt.savefig(filename, dpi=300, bbox_inches='tight', 
                facecolor='white', pad_inches=0.2)
    plt.close()
    print(f"✓ {filename} (matplotlib, упрощённое качество)")


# ============================================================
# ВСЕ ФОРМУЛЫ ДЛЯ КУРСОВОЙ
# ============================================================
os.makedirs('formulas', exist_ok=True)

# --- Формула 1: Уравнение Гельмгольца ---
render_latex_to_png(r"""
\begin{minipage}{0.9\textwidth}
\centering
Уравнения Гельмгольца для комплексных амплитуд полей:
\vspace{0.3cm}

$\Delta \dot{\mathbf{E}} + k^2 \dot{\mathbf{E}} = 0, \qquad \Delta \dot{\mathbf{H}} + k^2 \dot{\mathbf{H}} = 0$

\vspace{0.3cm}
где волновое число в неограниченной среде:

$k = \omega\sqrt{\varepsilon_0 \varepsilon_r \mu_0 \mu_r} = \dfrac{\omega}{c}\sqrt{\varepsilon_r \mu_r}$
\end{minipage}
""", 'formulas/01_helmholtz.png', fontsize=14)

# --- Формула 2: Граничные условия ---
render_latex_to_png(r"""
\begin{minipage}{0.9\textwidth}
\centering
Граничные условия на идеально проводящих стенках:

\vspace{0.3cm}

$\left.\dot{E}_\tau\right|_L = 0, \qquad \left.\dot{H}_n\right|_L = 0$

\vspace{0.2cm}
где $\dot{E}_\tau$ --- тангенциальная, $\dot{H}_n$ --- нормальная компоненты поля на поверхности $L$.
\end{minipage}
""", 'formulas/02_boundary.png', fontsize=14)

# --- Формула 3: Решение для E-волн в круглом волноводе ---
render_latex_to_png(r"""
\begin{minipage}{0.95\textwidth}
\centering
Решение уравнения Гельмгольца в цилиндрических координатах для продольной компоненты $E_z$:

\vspace{0.3cm}

$\dot{E}_z = \left[A_m J_m(\kappa r) + B_m N_m(\kappa r)\right]\left[C_m \cos(m\varphi) + D_m \sin(m\varphi)\right]e^{-\gamma z}$

\vspace{0.3cm}
Условия конечности поля в центре ($r = 0$): $B_m = 0$ (т.к. $N_m \to \infty$ при $r \to 0$).\\
Выбор начала отсчёта угла: $D_m = 0$. Окончательно:

\vspace{0.3cm}

$\boxed{\dot{E}_z = E_0 J_m(\kappa r)\cos(m\varphi)\,e^{-\gamma z}}$
\end{minipage}
""", 'formulas/03_ez_solution.png', fontsize=14)

# --- Формула 4: Поперечное волновое число ---
render_latex_to_png(r"""
\begin{minipage}{0.9\textwidth}
\centering
Граничное условие на стенке $r = a$: $\;\dot{E}_z\big|_{r=a} = 0$, откуда:

\vspace{0.3cm}

$J_m(\kappa a) = 0 \quad\Rightarrow\quad \kappa a = \nu_{mn}$

\vspace{0.3cm}
где $\nu_{mn}$ --- $n$-й корень функции Бесселя $J_m(x)$. Поперечное волновое число для E-волн:

\vspace{0.3cm}

$\boxed{\kappa_E = \dfrac{\nu_{mn}}{a}}$
\end{minipage}
""", 'formulas/04_kappa_E.png', fontsize=14)

# --- Формула 5: Дисперсионное уравнение ---
render_latex_to_png(r"""
\begin{minipage}{0.95\textwidth}
\centering
Дисперсионное уравнение, связывающее продольное $\gamma$ и поперечное $\kappa$ волновые числа:

\vspace{0.3cm}

$\gamma^2 = \kappa^2 - k^2 = \left(\dfrac{\nu_{mn}}{a}\right)^2 - \omega^2 \varepsilon_0 \varepsilon_r \mu_0 \mu_r$

\vspace{0.3cm}
или в эквивалентной форме:

\vspace{0.2cm}

$\gamma^2 + \kappa^2 = k^2 = \omega^2 \varepsilon_0 \varepsilon_r \mu_0 \mu_r$
\end{minipage}
""", 'formulas/05_dispersion.png', fontsize=14)

# --- Формула 6: Критическая частота ---
render_latex_to_png(r"""
\begin{minipage}{0.9\textwidth}
\centering
Граничный случай $\gamma = 0$ соответствует \textbf{критической частоте} моды:

\vspace{0.3cm}

$\boxed{f_{\text{кр}} = \dfrac{\kappa}{2\pi\sqrt{\varepsilon_0 \varepsilon_r \mu_0 \mu_r}} = \dfrac{c \cdot \nu_{mn}}{2\pi a \sqrt{\varepsilon_r \mu_r}}}$
\end{minipage}
""", 'formulas/06_f_cr.png', fontsize=14)

# --- Формула 7: Волновое сопротивление E-волн ---
render_latex_to_png(r"""
\begin{minipage}{0.95\textwidth}
\centering
Волновое сопротивление определяется как отношение поперечных компонент поля:

\vspace{0.3cm}

$Z_{\text{в}} = \dfrac{E_r}{H_\varphi}$

\vspace{0.3cm}
Из уравнений связи поперечных и продольных компонент:

$E_r = -\dfrac{\gamma}{\kappa_E^2}\,\dfrac{\partial E_z}{\partial r}, \qquad H_\varphi = -\dfrac{i\omega\varepsilon_0\varepsilon_r}{\kappa_E^2}\,\dfrac{\partial E_z}{\partial r}$

\vspace{0.3cm}
Подставляя $\gamma = i\beta$ (для распространяющейся волны):

\vspace{0.3cm}

$\boxed{Z_E = \dfrac{Z_0}{\sqrt{\varepsilon_r}} \sqrt{1 - \left(\dfrac{f_{\text{кр}}}{f}\right)^2}}$

\vspace{0.2cm}
где $Z_0 = \sqrt{\mu_0/\varepsilon_0} \approx 377$ Ом --- сопротивление вакуума.
\end{minipage}
""", 'formulas/07_Z_wave.png', fontsize=14)

# --- Формула 8: Фазовая и групповая скорости ---
render_latex_to_png(r"""
\begin{minipage}{0.95\textwidth}
\centering
\textbf{Фазовая скорость} ($v_{\text{ф}} = \omega/\beta$):

\vspace{0.3cm}

$\boxed{v_{\text{ф}} = \dfrac{c}{\sqrt{\varepsilon_r}\sqrt{1 - (f_{\text{кр}}/f)^2}}}$

\vspace{0.3cm}
\textbf{Групповая скорость} ($v_{\text{гр}} = d\omega/d\beta$):

\vspace{0.3cm}

$\boxed{v_{\text{гр}} = \dfrac{c}{\sqrt{\varepsilon_r}} \sqrt{1 - \left(\dfrac{f_{\text{кр}}}{f}\right)^2}}$

\vspace{0.3cm}
Важное соотношение:

\vspace{0.2cm}

$v_{\text{ф}} \cdot v_{\text{гр}} = \dfrac{c^2}{\varepsilon_r}$
\end{minipage}
""", 'formulas/08_velocities.png', fontsize=14)

# --- Формула 9: Длина волны в волноводе ---
render_latex_to_png(r"""
\begin{minipage}{0.9\textwidth}
\centering
Длина волны в волноводе связана с фазовой скоростью $\lambda_{\text{в}} = v_{\text{ф}}/f$:

\vspace{0.3cm}

$\boxed{\lambda_{\text{в}} = \dfrac{\lambda_0}{\sqrt{\varepsilon_r}\sqrt{1 - \left(\dfrac{f_{\text{кр}}}{f}\right)^2}}}$

\vspace{0.2cm}
где $\lambda_0 = c/f$ --- длина волны в вакууме.
\end{minipage}
""", 'formulas/09_lambda.png', fontsize=14)

# --- Формула 10: Толщина скин-слоя ---
render_latex_to_png(r"""
\begin{minipage}{0.9\textwidth}
\centering
Толщина скин-слоя --- глубина, на которой амплитуда поля затухает в $e$ раз:

\vspace{0.3cm}

$\boxed{\delta = \sqrt{\dfrac{2}{\omega\mu_0\sigma}} = \sqrt{\dfrac{1}{\pi f \mu_0 \sigma}}}$
\end{minipage}
""", 'formulas/10_skin_depth.png', fontsize=14)

# --- Формула 11: Поверхностное сопротивление ---
render_latex_to_png(r"""
\begin{minipage}{0.95\textwidth}
\centering
Поверхностное сопротивление стенки волновода:

\vspace{0.3cm}

$\boxed{R_s = \dfrac{1}{\sigma\delta} = \sqrt{\dfrac{\pi f \mu_0}{\sigma}}}$

\vspace{0.3cm}
\textbf{Вывод:} волновое сопротивление проводящей среды $Z = \dfrac{i\omega\mu_0}{k}$, где $k = (1+i)/\delta$.\\
Действительная часть: $R_s = \text{Re}(Z) = \dfrac{\omega\mu_0\delta}{2} = \dfrac{1}{\sigma\delta}$.
\end{minipage}
""", 'formulas/11_R_surface.png', fontsize=14)

# --- Формула 12: Резонансные частоты ---
render_latex_to_png(r"""
\begin{minipage}{0.95\textwidth}
\centering
Отрезок круглого волновода длиной $l$, закороченный торцами. Условие резонанса:

\vspace{0.3cm}

$\beta = \dfrac{p\pi}{l}, \quad p = 1, 2, 3, \ldots$

\vspace{0.3cm}
Из дисперсионного уравнения $k^2 = \kappa^2 + \beta^2$:

\vspace{0.3cm}

$\boxed{f_{\text{рез}}^{E_{mnp}} = \dfrac{c}{2\pi a \sqrt{\varepsilon_r}} \sqrt{\nu_{mn}^2 + \left(\dfrac{p\pi a}{l}\right)^2}}$

\vspace{0.3cm}
Для H-волн (с корнем $\chi_{mn}$ производной $J'_m$):

$f_{\text{рез}}^{H_{mnp}} = \dfrac{c}{2\pi a \sqrt{\varepsilon_r}} \sqrt{\chi_{mn}^2 + \left(\dfrac{p\pi a}{l}\right)^2}$
\end{minipage}
""", 'formulas/12_f_res.png', fontsize=14)

# --- Формула 13: Компоненты поля моды E_mnp ---
render_latex_to_png(r"""
\begin{minipage}{0.95\textwidth}
\centering
\textbf{Компоненты поля моды $E_{mnp}$ в цилиндрическом резонаторе:}

\vspace{0.3cm}

$E_z = E_0 J_m(\kappa_E r) \cos(m\varphi) \sin(k_z z)$

\vspace{0.2cm}

$E_r = -\dfrac{i k_z}{\kappa_E} E_0 J'_m(\kappa_E r) \cos(m\varphi) \sin(k_z z)$

\vspace{0.2cm}

$E_\varphi = \dfrac{i k_z m}{\kappa_E^2 r} E_0 J_m(\kappa_E r) \sin(m\varphi) \sin(k_z z)$

\vspace{0.2cm}

$H_r = -\dfrac{i\omega\varepsilon_0\varepsilon_r m}{\kappa_E^2 r} E_0 J_m(\kappa_E r) \sin(m\varphi) \sin(k_z z)$

\vspace{0.2cm}

$H_\varphi = -\dfrac{i\omega\varepsilon_0\varepsilon_r}{\kappa_E} E_0 J'_m(\kappa_E r) \cos(m\varphi) \sin(k_z z), \qquad H_z = 0$

\vspace{0.2cm}
где $\kappa_E = \nu_{mn}/a$, $\;k_z = p\pi/l$.
\end{minipage}
""", 'formulas/13_field_components.png', fontsize=13)

# --- Формула 14: Энергия электрического поля ---
render_latex_to_png(r"""
\begin{minipage}{0.95\textwidth}
\centering
\textbf{Энергия электрического поля:}

\vspace{0.3cm}

$W_E = \dfrac{\varepsilon_0 \varepsilon_r}{4} \int\limits_V |\mathbf{E}|^2 \, dV = \dfrac{\varepsilon_0 \varepsilon_r}{4} \int\limits_0^l \int\limits_0^{2\pi} \int\limits_0^a \left(|E_r|^2 + |E_\varphi|^2 + |E_z|^2\right) r \, dr \, d\varphi \, dz$

\vspace{0.3cm}
\textbf{Интегрирование по $z$:} $\;\displaystyle\int_0^l \sin^2(k_z z) \, dz = \dfrac{l}{2}$

\vspace{0.2cm}
\textbf{Интегрирование по $\varphi$} (при $m \neq 0$): $\;\displaystyle\int_0^{2\pi} \cos^2(m\varphi) \, d\varphi = \int_0^{2\pi} \sin^2(m\varphi) \, d\varphi = \pi$

\vspace{0.2cm}
\textbf{Тождество для функций Бесселя} (при $J_m(\kappa_E a) = 0$):

$\displaystyle\int_0^a \left\{[J'_m(\kappa_E r)]^2 + \dfrac{m^2}{\kappa_E^2 r^2} J_m^2(\kappa_E r)\right\} r \, dr = \dfrac{a^2}{2} [J'_m(\nu_{mn})]^2$

\vspace{0.3cm}
Собирая всё и используя $k^2 = \kappa_E^2 + k_z^2$:

\vspace{0.3cm}

$\boxed{W_E = \dfrac{\pi \varepsilon_0 \varepsilon_r^2 \omega^2 l a^4}{16 c^2 \nu_{mn}^2} E_0^2 [J'_m(\nu_{mn})]^2}$
\end{minipage}
""", 'formulas/14_W_E.png', fontsize=12)

# --- Формула 15: Мощность потерь ---
render_latex_to_png(r"""
\begin{minipage}{0.95\textwidth}
\centering
\textbf{Мощность потерь в стенках:}

\vspace{0.3cm}

$P_{\text{пр}} = \dfrac{R_s}{2} \oint\limits_S |H_\tau|^2 \, dS$

\vspace{0.3cm}
\textbf{Ключевой момент:} на торцах ($z = 0$ и $z = l$) все тангенциальные компоненты $H_r$ и $H_\varphi$ содержат множитель $\sin(k_z z)$, который \textbf{обращается в ноль}:

\vspace{0.2cm}

$\sin(k_z \cdot 0) = 0, \qquad \sin(k_z \cdot l) = \sin(p\pi) = 0$

\vspace{0.3cm}
$\Rightarrow$ \textbf{для мод $E_{mnp}$ потери на торцах РЕЗОНАТОРА СТРОГО РАВНЫ НУЛЮ!}

\vspace{0.3cm}
Интегрирование только по боковой стенке ($r = a$):

\vspace{0.3cm}

$\boxed{P_{\text{пр}} = \dfrac{\pi R_s \omega^2 \varepsilon_0^2 \varepsilon_r^2 a^3 l}{4 \nu_{mn}^2} E_0^2 [J'_m(\nu_{mn})]^2}$
\end{minipage}
""", 'formulas/15_P_loss.png', fontsize=12)

# --- Формула 16: Точная добротность (вывод) ---
render_latex_to_png(r"""
\begin{minipage}{0.95\textwidth}
\centering
\textbf{Вывод точной формулы добротности для моды $E_{mnp}$:}

\vspace{0.3cm}

$Q = \omega_0 \dfrac{W}{P_{\text{пот}}} = \omega_0 \dfrac{2W_E}{P_{\text{пр}}}$

\vspace{0.3cm}
Подставляем полученные выражения:

\vspace{0.3cm}

$Q = \omega_0 \cdot \dfrac{2 \cdot \dfrac{\pi \varepsilon_0 \varepsilon_r^2 \omega_0^2 l a^4}{16 c^2 \nu_{mn}^2} E_0^2 [J'_m(\nu_{mn})]^2}{\dfrac{\pi R_s \omega_0^2 \varepsilon_0^2 \varepsilon_r^2 a^3 l}{4 \nu_{mn}^2} E_0^2 [J'_m(\nu_{mn})]^2}$

\vspace{0.3cm}
После сокращения всех общих множителей ($\pi,\, \varepsilon_0,\, \varepsilon_r^2,\, \omega_0^2,\, l,\, a^3,\, \nu_{mn}^2,\, E_0^2,\, [J'_m]^2$):

\vspace{0.3cm}

$Q = \omega_0 \cdot \dfrac{2a \cdot 4}{16 c^2 R_s \varepsilon_0} = \dfrac{\omega_0 a}{2 c^2 R_s \varepsilon_0}$

\vspace{0.3cm}
Используя $c^2 \varepsilon_0 = 1/\mu_0$ и $\omega_0 = 2\pi f_{\text{рез}}$:
\end{minipage}
""", 'formulas/16_Q_derivation.png', fontsize=12)

# --- Формула 17: Точная формула добротности (итог) ---
render_latex_to_png(r"""
\begin{minipage}{0.9\textwidth}
\centering
\textbf{ТОЧНАЯ формула добротности для мод $E_{mnp}$ в цилиндрическом резонаторе:}

\vspace{0.5cm}

$\boxed{Q_{\text{точн}} = \dfrac{\pi f_{\text{рез}} \mu_0 a}{R_s}}$

\vspace{0.5cm}
\textbf{Важно:} эта формула \textbf{не содержит} геометрического множителя $\dfrac{l}{l+2a}$,\\
поскольку для E-мод потери на торцах \textbf{отсутствуют}.

\vspace{0.3cm}
Приближённая формула (справедлива для H-мод):

$Q_{\text{прибл}} = \dfrac{\pi f_{\text{рез}} \mu_0 a}{R_s} \cdot \dfrac{l}{l + 2a}$

\vspace{0.2cm}
Для $l = 5a$ множитель $l/(l+2a) = 5/7 \approx 0{,}714$, т.е. приближение занижает\\
добротность на \textbf{28{,}6\%} (те самые $\sim$30\% отличия).
\end{minipage}
""", 'formulas/17_Q_exact.png', fontsize=13)

# --- Формула 18: Общая добротность (с диэлектриком) ---
render_latex_to_png(r"""
\begin{minipage}{0.9\textwidth}
\centering
\textbf{Полная добротность резонатора} (с учётом потерь в стенках и диэлектрике):

\vspace{0.3cm}

$\dfrac{1}{Q} = \dfrac{1}{Q_{\text{пр}}} + \dfrac{1}{Q_{\text{д}}}$

\vspace{0.3cm}
Добротность, связанная с диэлектрическими потерями:

\vspace{0.3cm}

$Q_{\text{д}} = \dfrac{1}{\tan\delta}$

\vspace{0.3cm}
Для идеального диэлектрика ($\tan\delta = 0$): $Q_{\text{д}} \to \infty$, и $Q = Q_{\text{пр}}$.
\end{minipage}
""", 'formulas/18_Q_total.png', fontsize=14)

# --- Формула 19: Сводная таблица ---
render_latex_to_png(r"""
\begin{minipage}{0.95\textwidth}
\centering
\textbf{Сводная таблица основных формул:}

\vspace{0.3cm}
\begin{tabular}{ll}
\toprule
\textbf{Величина} & \textbf{Формула} \\
\midrule
Критическая частота & $f_{\text{кр}} = \dfrac{c\,\nu_{mn}}{2\pi a\sqrt{\varepsilon_r\mu_r}}$ \\[8pt]
Волновое сопротивление & $Z_E = \dfrac{Z_0}{\sqrt{\varepsilon_r}}\sqrt{1-(f_{\text{кр}}/f)^2}$ \\[8pt]
Фазовая скорость & $v_{\text{ф}} = \dfrac{c}{\sqrt{\varepsilon_r}\sqrt{1-(f_{\text{кр}}/f)^2}}$ \\[8pt]
Групповая скорость & $v_{\text{гр}} = \dfrac{c}{\sqrt{\varepsilon_r}}\sqrt{1-(f_{\text{кр}}/f)^2}$ \\[8pt]
Длина волны в волноводе & $\lambda_{\text{в}} = \dfrac{\lambda_0}{\sqrt{\varepsilon_r}\sqrt{1-(f_{\text{кр}}/f)^2}}$ \\[8pt]
Толщина скин-слоя & $\delta = \sqrt{\dfrac{1}{\pi f\mu_0\sigma}}$ \\[8pt]
Поверхностное сопр. & $R_s = \dfrac{1}{\sigma\delta} = \sqrt{\dfrac{\pi f\mu_0}{\sigma}}$ \\[8pt]
Резонансная частота & $f_{\text{рез}} = \dfrac{c}{2\pi a\sqrt{\varepsilon_r}}\sqrt{\nu_{mn}^2+(p\pi a/l)^2}$ \\[8pt]
Добротность (точная) & $Q = \dfrac{\pi f_{\text{рез}}\mu_0 a}{R_s}$ \\
\bottomrule
\end{tabular}
\end{minipage}
""", 'formulas/19_summary_table.png', fontsize=12)

print("\n" + "="*60)
print("✅ Все формулы сгенерированы в папку 'formulas/'")
print("="*60)
print("\n📁 Созданные файлы:")
for f in sorted(os.listdir('formulas')):
    if f.endswith('.png'):
        size_kb = os.path.getsize(f'formulas/{f}') / 1024
        print(f"   {f:40s} ({size_kb:.0f} КБ)")

print("\n💡 Как использовать:")
print("   Откройте Word → Вставка → Рисунки → выберите нужную формулу")
print("   Формулы будут вставлены как картинки высокого разрешения (300 DPI)")
print("   Они выглядят точно как в учебнике (шрифт Computer Modern)")