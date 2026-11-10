import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pptx import Presentation
from pptx.util import Inches, Pt, Cm, Emu
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from docx import Document
from docx.shared import Pt as DocxPt, Cm as DocxCm, RGBColor as DocxRGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ==========================================
# ФИРМЕННЫЕ ЦВЕТА СПбГЭТУ «ЛЭТИ»
# ==========================================
LETI_BLUE = RGBColor(0x00, 0x33, 0xA0)     # Основной синий ЛЭТИ
LETI_BLUE_LIGHT = RGBColor(0x4A, 0x7B, 0xC8)
LETI_WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LETI_GRAY = RGBColor(0x6B, 0x6B, 0x6B)
LETI_DARK = RGBColor(0x1A, 0x1A, 0x1A)
LETI_BG = RGBColor(0xF5, 0xF7, 0xFA)

# ==========================================
# 1. ГЕНЕРАЦИЯ ГРАФИКА
# ==========================================
def generate_images():
    fig, ax = plt.subplots(figsize=(8, 5))
    t = np.linspace(0, 10, 500)
    power = np.zeros_like(t)
    pump_phase = t < 7
    power[pump_phase] = 0.05 * t[pump_phase]
    
    pulse_center = 7.2
    pulse_width = 0.15
    power += 5.0 * np.exp(-((t - pulse_center) ** 2) / (2 * pulse_width ** 2))
    
    ax.plot(t, power, color='#0033A0', linewidth=2.5)
    ax.fill_between(t, power, color='#0033A0', alpha=0.15)
    
    ax.set_title('Гигантский импульс при модуляции добротности', fontsize=14, fontweight='bold', color='#0033A0')
    ax.set_xlabel('Время (условные единицы)', fontsize=12)
    ax.set_ylabel('Мощность излучения', fontsize=12)
    ax.set_ylim(0, 6)
    ax.grid(True, linestyle='--', alpha=0.4)
    
    ax.annotate('Накачка среды\n(Добротность низкая)', xy=(3, 0.15), xytext=(1.5, 2),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8), fontsize=10)
    ax.annotate('Резкий скачок добротности', xy=(7, 0.5), xytext=(7.5, 3),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8), fontsize=10)
    ax.annotate('Гигантский импульс\n(Наносекунды)', xy=(7.2, 4.5), xytext=(8, 5),
                arrowprops=dict(facecolor='#0033A0', shrink=0.05, width=1.5, headwidth=8), fontsize=10, color='#0033A0')

    plt.tight_layout()
    plt.savefig('q_switch_graph.png', dpi=150)
    plt.close()

# ==========================================
# 2. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ СТИЛЯ ЛЭТИ
# ==========================================
def add_leti_header(slide, title_text):
    """Добавляет верхнюю синюю полосу с логотипом ЛЭТИ"""
    # Синяя полоса сверху
    shape = slide.shapes.add_shape(
        1, Inches(0), Inches(0), Inches(13.333), Inches(0.9)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = LETI_BLUE
    shape.line.fill.background()
    
    # Текст "СПбГЭТУ «ЛЭТИ»" в полосе
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "СПбГЭТУ «ЛЭТИ»  ·  Физика лазеров"
    p.font.size = Pt(16)
    p.font.color.rgb = LETI_WHITE
    p.font.bold = True
    p.alignment = PP_ALIGN.LEFT
    tf.margin_left = Inches(0.4)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    
    # Заголовок слайда
    left = Inches(0.5)
    top = Inches(1.1)
    width = Inches(12.3)
    height = Inches(0.8)
    title_box = slide.shapes.add_textbox(left, top, width, height)
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.size = Pt(32)
    p.font.color.rgb = LETI_DARK
    p.font.bold = True
    p.alignment = PP_ALIGN.LEFT

def add_leti_footer(slide, slide_number, total_slides):
    """Добавляет нижнюю полосу с номером слайда"""
    shape = slide.shapes.add_shape(
        1, Inches(0), Inches(7.1), Inches(13.333), Inches(0.4)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = LETI_BLUE
    shape.line.fill.background()
    
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = f"{slide_number} / {total_slides}"
    p.font.size = Pt(12)
    p.font.color.rgb = LETI_WHITE
    p.alignment = PP_ALIGN.RIGHT
    tf.margin_right = Inches(0.4)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE

def add_content_box(slide, text, left=Inches(0.5), top=Inches(2.2), width=Inches(7), height=Inches(4.5)):
    """Добавляет текстовый блок с буллетами"""
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = line
        p.font.size = Pt(18)
        p.font.color.rgb = LETI_DARK
        p.space_after = Pt(8)
        p.alignment = PP_ALIGN.LEFT
        
        if line.startswith('•') or line.startswith('✅') or line.startswith('❌'):
            p.level = 0
        elif line.startswith('  '):
            p.level = 1
            p.font.size = Pt(16)
            p.font.color.rgb = LETI_GRAY

def add_image_placeholder(slide, desc, left=Inches(7.8), top=Inches(2.2), width=Inches(5), height=Inches(4.5)):
    """Добавляет заглушку для картинки в стиле ЛЭТИ"""
    shape = slide.shapes.add_shape(1, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = LETI_BG
    shape.line.color.rgb = LETI_BLUE_LIGHT
    shape.line.width = Pt(2)
    
    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.text = "🖼️ " + desc
    p.font.size = Pt(14)
    p.font.color.rgb = LETI_BLUE
    p.alignment = PP_ALIGN.CENTER

# ==========================================
# 3. СОЗДАНИЕ ПРЕЗЕНТАЦИИ В СТИЛЕ ЛЭТИ
# ==========================================
def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    # Пустой макет (будем рисовать сами)
    blank_layout = prs.slide_layouts[6]
    
    slides_info = []  # для нумерации
    
    # ---------- СЛАЙД 1: ТИТУЛЬНЫЙ ----------
    slide = prs.slides.add_slide(blank_layout)
    # Большой синий фон
    bg = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = LETI_BLUE
    bg.line.fill.background()
    
    # Белый блок с названием
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(2.5))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "МЕТОД МОДУЛЯЦИИ ДОБРОТНОСТИ\nВ ЛАЗЕРАХ"
    p.font.size = Pt(54)
    p.font.color.rgb = LETI_WHITE
    p.font.bold = True
    p.alignment = PP_ALIGN.LEFT
    
    # Подзаголовок
    sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(4.3), Inches(11.7), Inches(1))
    tf = sub_box.text_frame
    p = tf.paragraphs[0]
    p.text = "Дисциплина: Физика лазеров"
    p.font.size = Pt(22)
    p.font.color.rgb = LETI_WHITE
    p.alignment = PP_ALIGN.LEFT
    
    # Авторы
    auth_box = slide.shapes.add_textbox(Inches(0.8), Inches(5.5), Inches(11.7), Inches(1.5))
    tf = auth_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Выполнили: студенты группы 4204"
    p.font.size = Pt(18)
    p.font.color.rgb = LETI_WHITE
    p.alignment = PP_ALIGN.LEFT
    p = tf.add_paragraph()
    p.text = "Лавриненко И. П.  ·  Пильгун П. Д."
    p.font.size = Pt(20)
    p.font.color.rgb = LETI_WHITE
    p.font.bold = True
    p.alignment = PP_ALIGN.LEFT
    p = tf.add_paragraph()
    p.text = "Санкт-Петербург, 2026"
    p.font.size = Pt(16)
    p.font.color.rgb = LETI_WHITE
    p.alignment = PP_ALIGN.LEFT
    
    slides_info.append(1)
    
    # ---------- СЛАЙД 2: ОГЛАВЛЕНИЕ ----------
    slide = prs.slides.add_slide(blank_layout)
    add_leti_header(slide, "Оглавление")
    add_leti_footer(slide, 2, 11)
    
    toc_text = (
        "1. Введение. Проблема непрерывного лазера\n"
        "2. Что такое добротность резонатора\n"
        "3. Цикл получения гигантского импульса\n"
        "4. Типы модуляции добротности\n"
        "5. Области применения\n"
        "6. Плюсы и минусы метода\n"
        "7. Заключение\n"
        "8. Список литературы"
    )
    add_content_box(slide, toc_text, left=Inches(0.8), top=Inches(2.2), width=Inches(11.5), height=Inches(4.5))
    slides_info.append(2)
    
    # ---------- СЛАЙД 3: ПРОБЛЕМА НЕПРЕРЫВНОГО ЛАЗЕРА ----------
    slide = prs.slides.add_slide(blank_layout)
    add_leti_header(slide, "Проблема непрерывного лазера и её решение")
    add_leti_footer(slide, 3, 11)
    
    content = (
        "• Непрерывные лазеры дают постоянную мощность\n"
        "  (аналогия: тонкая струя воды из шланга)\n"
        "• Для многих задач нужна огромная мощность\n"
        "  в короткий миг (гидромонитор, лук)\n"
        "• Решение: накопить энергию и спустить её разом\n"
        "• Метод: модуляция добротности резонатора (Q-switching)"
    )
    add_content_box(slide, content, width=Inches(7))
    add_image_placeholder(slide, "Сравнение: шланг vs гидромонитор\n(или натянутый лук)")
    slides_info.append(3)
    
    # ---------- СЛАЙД 4: ДОБРОТНОСТЬ ----------
    slide = prs.slides.add_slide(blank_layout)
    add_leti_header(slide, "Что такое «добротность» (Q-фактор) резонатора?")
    add_leti_footer(slide, 4, 11)
    
    content = (
        "• Добротность — это «качество» ловушки для света\n"
        "• Низкая Q: высокие потери, свет уходит, генерации нет\n"
        "• Высокая Q: идеальные зеркала, свет многократно\n"
        "  усиливается в резонаторе\n"
        "• Суть метода: ручное управление качеством резонатора\n"
        "  в процессе работы лазера"
    )
    add_content_box(slide, content, width=Inches(7))
    add_image_placeholder(slide, "Схема резонатора:\nслева — низкая Q, справа — высокая Q")
    slides_info.append(4)
    
    # ---------- СЛАЙД 5: ГРАФИК ----------
    slide = prs.slides.add_slide(blank_layout)
    add_leti_header(slide, "Цикл получения гигантского импульса")
    add_leti_footer(slide, 5, 11)
    
    content = (
        "1. Накачка среды при НИЗКОЙ добротности\n"
        "   (энергия копится, лазер молчит)\n"
        "2. Резкое ПОВЫШЕНИЕ добротности\n"
        "3. Лавинообразная генерация: вся энергия\n"
        "   вылетает за наносекунды"
    )
    add_content_box(slide, content, width=Inches(6), top=Inches(2.2))
    
    # Вставляем реальный график
    if os.path.exists('q_switch_graph.png'):
        pic = slide.shapes.add_picture('q_switch_graph.png', Inches(7), Inches(2.2), width=Inches(5.8))
    slides_info.append(5)
    
    # ---------- СЛАЙД 6: ТИПЫ МОДУЛЯЦИИ ----------
    slide = prs.slides.add_slide(blank_layout)
    add_leti_header(slide, "Типы модуляции добротности")
    add_leti_footer(slide, 6, 11)
    
    content = (
        "АКТИВНАЯ МОДУЛЯЦИЯ (управление извне):\n"
        "• Акустооптические модуляторы\n"
        "• Электрооптические затворы\n"
        "• Вращающиеся зеркала\n"
        "\n"
        "ПАССИВНАЯ МОДУЛЯЦИЯ (автоматический клапан):\n"
        "• Насыщающиеся поглотители\n"
        "• Становятся прозрачными при высокой интенсивности"
    )
    add_content_box(slide, content, width=Inches(7))
    add_image_placeholder(slide, "Схемы активного и пассивного\nмодуляторов добротности")
    slides_info.append(6)
    
    # ---------- СЛАЙД 7: ПРИМЕНЕНИЕ ----------
    slide = prs.slides.add_slide(blank_layout)
    add_leti_header(slide, "Области применения")
    add_leti_footer(slide, 7, 11)
    
    content = (
        "• Лазерная дальнометрия и лидары\n"
        "  (беспилотные автомобили)\n"
        "• Микрообработка и маркировка материалов\n"
        "  (холодная абляция)\n"
        "• Медицина: удаление татуировок, литотрипсия\n"
        "• Научные эксперименты: нелинейная оптика,\n"
        "  лазерный пробой, спектроскопия"
    )
    add_content_box(slide, content, width=Inches(7))
    add_image_placeholder(slide, "Коллаж: лидар, гравировка,\nлазерная медицина")
    slides_info.append(7)
    
    # ---------- СЛАЙД 8: ПЛЮСЫ И МИНУСЫ ----------
    slide = prs.slides.add_slide(blank_layout)
    add_leti_header(slide, "Плюсы и минусы метода")
    add_leti_footer(slide, 8, 11)
    
    content = (
        "✅ ПЛЮСЫ:\n"
        "• Огромная пиковая мощность (МВт и ГВт)\n"
        "• Относительная простота реализации\n"
        "• Надёжность и воспроизводимость импульсов\n"
        "\n"
        "❌ МИНУСЫ:\n"
        "• Длительность импульсов (наносекунды)\n"
        "• Высокий риск оптического пробоя оптики\n"
        "• Износ элементов резонатора"
    )
    add_content_box(slide, content, width=Inches(11.5))
    slides_info.append(8)
    
    # ---------- СЛАЙД 9: ЗАКЛЮЧЕНИЕ ----------
    slide = prs.slides.add_slide(blank_layout)
    add_leti_header(slide, "Заключение")
    add_leti_footer(slide, 9, 11)
    
    content = (
        "➜ Модуляция добротности — элегантный способ\n"
        "   превратить обычную лазерную «лампочку»\n"
        "   в мощный «ударный инструмент»\n"
        "\n"
        "➜ Управление качеством зеркал резонатора\n"
        "   позволяет накапливать и мгновенно\n"
        "   высвобождать энергию\n"
        "\n"
        "➜ Метод широко применяется в науке,\n"
        "   промышленности и медицине"
    )
    add_content_box(slide, content, width=Inches(11.5))
    slides_info.append(9)
    
    # ---------- СЛАЙД 10: СПИСОК ЛИТЕРАТУРЫ ----------
    slide = prs.slides.add_slide(blank_layout)
    add_leti_header(slide, "Список литературы")
    add_leti_footer(slide, 10, 11)
    
    refs = (
        "1. Звелто О. Принципы лазеров / О. Звелто ; пер. с англ.\n"
        "   — 5-е изд. — М. : ЛАНЬ, 2022. — 668 с.\n"
        "2. Милонни П. Лазеры / П. Милонни, Дж. Эберли ; пер. с англ.\n"
        "   — М. : Бином. Лаборатория знаний, 2021. — 760 с.\n"
        "3. Дьяков Е. Б. Физика лазеров : учеб. пособие / Е. Б. Дьяков.\n"
        "   — М. : ФИЗМАТЛИТ, 2020. — 424 с.\n"
        "4. Свечников Г. В. Лазерная техника и технология.\n"
        "   — Киев : Наук. думка, 2019. — 320 с.\n"
        "5. Saleh B. E. A. Fundamentals of Photonics / B. E. A. Saleh,\n"
        "   M. C. Teich. — 3rd ed. — Wiley, 2019. — 1152 p.\n"
        "6. Letokhov V. S. Laser physics / V. S. Letokhov.\n"
        "   — Oxford : Oxford Univ. Press, 2021. — 720 p."
    )
    add_content_box(slide, refs, width=Inches(11.5), height=Inches(4.5))
    slides_info.append(10)
    
    # ---------- СЛАЙД 11: СПАСИБО ----------
    slide = prs.slides.add_slide(blank_layout)
    bg = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = LETI_BLUE
    bg.line.fill.background()
    
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(2.5), Inches(11.7), Inches(2))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = "Спасибо за внимание!"
    p.font.size = Pt(60)
    p.font.color.rgb = LETI_WHITE
    p.font.bold = True
    p.alignment = PP_ALIGN.CENTER
    
    sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(4.8), Inches(11.7), Inches(1))
    tf = sub_box.text_frame
    p = tf.paragraphs[0]
    p.text = "Готовы ответить на ваши вопросы"
    p.font.size = Pt(24)
    p.font.color.rgb = LETI_WHITE
    p.alignment = PP_ALIGN.CENTER
    
    auth_box = slide.shapes.add_textbox(Inches(0.8), Inches(5.8), Inches(11.7), Inches(1))
    tf = auth_box.text_frame
    p = tf.paragraphs[0]
    p.text = "Лавриненко И. П.  ·  Пильгун П. Д.  ·  Группа 4204"
    p.font.size = Pt(18)
    p.font.color.rgb = LETI_WHITE
    p.alignment = PP_ALIGN.CENTER
    
    slides_info.append(11)
    
    prs.save('Q_Switching_LETI_Presentation.pptx')
    print("✅ Презентация в стиле ЛЭТИ сохранена: Q_Switching_LETI_Presentation.pptx")

# ==========================================
# 4. WORD ДОКУМЕНТ ПО ГОСТ 7.32-2017
# ==========================================
def set_paragraph_format(paragraph, font_name='Times New Roman', font_size=14,
                         alignment=WD_ALIGN_PARAGRAPH.JUSTIFY, first_line_indent=1.25,
                         line_spacing=1.5, space_before=0, space_after=0, bold=False):
    """Настройка абзаца по ГОСТ"""
    paragraph.alignment = alignment
    paragraph.paragraph_format.first_line_indent = DocxCm(first_line_indent) if first_line_indent else None
    paragraph.paragraph_format.line_spacing = line_spacing
    paragraph.paragraph_format.space_before = DocxPt(space_before)
    paragraph.paragraph_format.space_after = DocxPt(space_after)
    
    for run in paragraph.runs:
        run.font.name = font_name
        run.font.size = DocxPt(font_size)
        run.font.bold = bold
        # Устанавливаем шрифт для кириллицы
        r = run._element
        rPr = r.find(qn('w:rPr'))
        if rPr is None:
            rPr = OxmlElement('w:rPr')
            r.insert(0, rPr)
        rFonts = rPr.find(qn('w:rFonts'))
        if rFonts is None:
            rFonts = OxmlElement('w:rFonts')
            rPr.append(rFonts)
        rFonts.set(qn('w:eastAsia'), font_name)

def add_page_number(doc):
    """Добавляет нумерацию страниц внизу по центру"""
    for section in doc.sections:
        footer = section.footer
        footer.is_linked_to_previous = False
        p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Поле номера страницы
        run = p.add_run()
        fldChar1 = OxmlElement('w:fldChar')
        fldChar1.set(qn('w:fldCharType'), 'begin')
        run._element.append(fldChar1)
        
        run2 = p.add_run()
        instrText = OxmlElement('w:instrText')
        instrText.set(qn('xml:space'), 'preserve')
        instrText.text = ' PAGE '
        run2._element.append(instrText)
        
        run3 = p.add_run()
        fldChar2 = OxmlElement('w:fldChar')
        fldChar2.set(qn('w:fldCharType'), 'end')
        run3._element.append(fldChar2)
        
        for r in [run, run2, run3]:
            r.font.name = 'Times New Roman'
            r.font.size = DocxPt(14)

def add_slide_marker(doc, slide_num):
    """Добавляет заметную пометку о переключении слайда"""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f'[▶ ПЕРЕКЛЮЧИТЬ НА СЛАЙД {slide_num}]')
    run.font.name = 'Times New Roman'
    run.font.size = DocxPt(12)
    run.font.bold = True
    run.font.color.rgb = DocxRGBColor(0x00, 0x33, 0xA0)  # синий ЛЭТИ
    p.paragraph_format.space_before = DocxPt(12)
    p.paragraph_format.space_after = DocxPt(6)
    # Рамка вокруг пометки
    pPr = p._element.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    for border_name in ['top', 'left', 'bottom', 'right']:
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), 'single')
        border.set(qn('w:sz'), '4')
        border.set(qn('w:space'), '4')
        border.set(qn('w:color'), '0033A0')
        pBdr.append(border)
    pPr.append(pBdr)

def add_gost_paragraph(doc, text, first_line_indent=1.25, bold=False, alignment=WD_ALIGN_PARAGRAPH.JUSTIFY):
    """Добавляет абзац по ГОСТ"""
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_paragraph_format(p, first_line_indent=first_line_indent, bold=bold, alignment=alignment)
    return p

def add_gost_heading(doc, text, level=1):
    """Добавляет заголовок по ГОСТ"""
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = DocxPt(16 if level == 1 else 14)
    run.font.bold = True
    
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT if level > 1 else WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = DocxPt(18)
    p.paragraph_format.space_after = DocxPt(12)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.first_line_indent = None
    return p

def create_document_gost():
    doc = Document()
    
    # Настройка страницы по ГОСТ: поля левое 30мм, правое 15мм, верхнее 20мм, нижнее 20мм
    section = doc.sections[0]
    section.page_width = DocxCm(21)
    section.page_height = DocxCm(29.7)
    section.left_margin = DocxCm(3.0)
    section.right_margin = DocxCm(1.5)
    section.top_margin = DocxCm(2.0)
    section.bottom_margin = DocxCm(2.0)
    
    # Нумерация страниц
    add_page_number(doc)
    
    # ===== ТИТУЛЬНЫЙ ЛИСТ =====
    # Верхний колонтитул титульника
    p = doc.add_paragraph()
    run = p.add_run('МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ\nРОССИЙСКОЙ ФЕДЕРАЦИИ')
    run.font.name = 'Times New Roman'
    run.font.size = DocxPt(14)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = None
    
    p = doc.add_paragraph()
    run = p.add_run('Федеральное государственное бюджетное образовательное учреждение\nвысшего образования')
    run.font.name = 'Times New Roman'
    run.font.size = DocxPt(14)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = None
    
    p = doc.add_paragraph()
    run = p.add_run('«САНКТ-ПЕТЕРБУРГСКИЙ ГОСУДАРСТВЕННЫЙ УНИВЕРСИТЕТ\nТЕЛЕКОММУНИКАЦИЙ ИМ. ПРОФ. М. А. БОНЧ-БРУЕВИЧА»')
    run.font.name = 'Times New Roman'
    run.font.size = DocxPt(14)
    run.font.bold = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = None
    
    p = doc.add_paragraph()
    run = p.add_run('(СПбГУТ)')
    run.font.name = 'Times New Roman'
    run.font.size = DocxPt(14)
    run.font.bold = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = None
    
    # Отступы
    for _ in range(3):
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = None
    
    p = doc.add_paragraph()
    run = p.add_run('Дисциплина: Физика лазеров')
    run.font.name = 'Times New Roman'
    run.font.size = DocxPt(14)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.first_line_indent = None
    
    p = doc.add_paragraph()
    run = p.add_run('Доклад на тему:')
    run.font.name = 'Times New Roman'
    run.font.size = DocxPt(14)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.first_line_indent = None
    
    p = doc.add_paragraph()
    run = p.add_run('«Метод модуляции добротности в лазерах»')
    run.font.name = 'Times New Roman'
    run.font.size = DocxPt(16)
    run.font.bold = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = None
    
    for _ in range(4):
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = None
    
    p = doc.add_paragraph()
    run = p.add_run('Выполнили: студенты группы 4204')
    run.font.name = 'Times New Roman'
    run.font.size = DocxPt(14)
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.paragraph_format.first_line_indent = None
    
    p = doc.add_paragraph()
    run = p.add_run('Лавриненко И. П.')
    run.font.name = 'Times New Roman'
    run.font.size = DocxPt(14)
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.paragraph_format.first_line_indent = None
    
    p = doc.add_paragraph()
    run = p.add_run('Пильгун П. Д.')
    run.font.name = 'Times New Roman'
    run.font.size = DocxPt(14)
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.paragraph_format.first_line_indent = None
    
    for _ in range(3):
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = None
    
    p = doc.add_paragraph()
    run = p.add_run('Санкт-Петербург\n2026')
    run.font.name = 'Times New Roman'
    run.font.size = DocxPt(14)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = None
    
    # ===== НОВАЯ СТРАНИЦА: СОДЕРЖАНИЕ =====
    doc.add_page_break()
    add_gost_heading(doc, 'СОДЕРЖАНИЕ', level=1)
    
    toc_items = [
        ('Введение', '3'),
        ('1 Проблема непрерывного лазера и постановка задачи', '4'),
        ('2 Понятие добротности оптического резонатора', '5'),
        ('3 Физика метода модуляции добротности', '6'),
        ('4 Типы модуляции добротности', '7'),
        ('5 Области применения', '8'),
        ('6 Преимущества и ограничения метода', '9'),
        ('7 Заключение', '10'),
        ('Список использованных источников', '11'),
    ]
    
    for title, page in toc_items:
        p = doc.add_paragraph()
        run = p.add_run(f'{title}')
        run.font.name = 'Times New Roman'
        run.font.size = DocxPt(14)
        p.paragraph_format.first_line_indent = None
        p.paragraph_format.line_spacing = 1.5
        
        # Добавляем отступы и номер страницы через табуляцию
        tab_run = p.add_run('\t' * 5 + page)
        tab_run.font.name = 'Times New Roman'
        tab_run.font.size = DocxPt(14)
    
    # ===== ВВЕДЕНИЕ =====
    doc.add_page_break()
    add_gost_heading(doc, 'ВВЕДЕНИЕ', level=1)
    add_slide_marker(doc, 1)
    
    add_gost_paragraph(doc, 
        'Уважаемые коллеги, преподаватель и одногруппники, здравствуйте! Сегодня мы '
        'расскажем об одном из самых элегантных методов в лазерной физике — методе '
        'модуляции добротности резонатора, или Q-switching.')
    
    add_gost_paragraph(doc, 
        'Актуальность темы обусловлена широким применением коротких и мощных лазерных '
        'импульсов в современных технологиях: от лазерной дальнометрии и лидаров в '
        'беспилотных автомобилях до микрообработки материалов и медицинских процедур.')
    
    add_gost_paragraph(doc, 
        'Цель данного доклада — раскрыть физическую сущность метода модуляции '
        'добротности, рассмотреть его реализацию и области практического применения.')
    
    # ===== 1. ПРОБЛЕМА НЕПРЕРЫВНОГО ЛАЗЕРА =====
    add_slide_marker(doc, 2)
    add_gost_heading(doc, '1 Проблема непрерывного лазера и постановка задачи', level=1)
    
    add_gost_paragraph(doc, 
        'Обычные непрерывные лазеры излучают свет с постоянной мощностью, что можно '
        'сравнить с тонкой струёй воды из садового шланга. Однако для целого ряда '
        'практических задач — пробивания материалов, лазерной абляции, дальнометрии — '
        'требуется колоссальная мощность, сосредоточенная в очень короткий промежуток '
        'времени. Аналогия: чтобы получить мощный удар, используют гидромонитор или '
        'резко отпускают натянутый лук.')
    
    add_gost_paragraph(doc, 
        'Таким образом, задача состоит в том, чтобы накопить энергию в активной среде '
        'лазера и затем высвободить её единым мощным импульсом. Именно эту задачу и '
        'решает метод модуляции добротности.')
    
    # ===== 2. ДОБРОТНОСТЬ =====
    add_slide_marker(doc, 3)
    add_gost_heading(doc, '2 Понятие добротности оптического резонатора', level=1)
    
    add_gost_paragraph(doc, 
        'Добротность оптического резонатора (Q-фактор) — это безразмерная величина, '
        'характеризующая качество «ловушки для света». Она определяется как отношение '
        'запасённой в резонаторе энергии к потерям за один период колебаний.')
    
    add_gost_paragraph(doc, 
        'При высокой добротности зеркала резонатора идеальны, свет многократно '
        'проходит через активную среду и усиливается. При низкой добротности в '
        'резонатор намеренно вносятся потери — свет уходит, генерация не возникает. '
        'Суть метода модуляции добротности заключается в управляемом изменении '
        'этого параметра в процессе работы лазера.')
    
    # ===== 3. ФИЗИКА МЕТОДА =====
    add_slide_marker(doc, 4)
    add_slide_marker(doc, 5)
    add_gost_heading(doc, '3 Физика метода модуляции добротности', level=1)
    
    add_gost_paragraph(doc, 
        'Процесс получения гигантского импульса состоит из трёх этапов. На первом '
        'этапе производится накачка активной среды при намеренно низкой добротности '
        'резонатора. Лазер не генерирует, но инверсия населённостей накапливается до '
        'значений, в сотни раз превышающих пороговые.')
    
    add_gost_paragraph(doc, 
        'На втором этапе добротность резонатора резко повышается — «чинится» ловушка '
        'для света. На третьем этапе происходит лавинообразное высвобождение всей '
        'накопленной энергии в виде гигантского импульса длительностью порядка '
        'наносекунд. Пиковая мощность при этом достигает мегаватт и даже гигаватт.')
    
    # ===== 4. ТИПЫ МОДУЛЯЦИИ =====
    add_slide_marker(doc, 6)
    add_gost_heading(doc, '4 Типы модуляции добротности', level=1)
    
    add_gost_paragraph(doc, 
        'Существует два основных способа управления добротностью резонатора. '
        'Активная модуляция предполагает внешнее управление процессом. В качестве '
        'затворов используются акустооптические и электрооптические модуляторы, а '
        'также механические системы — например, вращающиеся зеркала. '
        'Акустооптический модулятор создаёт в кристалле звуковую волну, которая '
        'работает как дифракционная решётка и уводит свет из резонатора.')
    
    add_gost_paragraph(doc, 
        'Пассивная модуляция использует насыщающийся поглотитель — специальный '
        'материал, который при малой интенсивности света непрозрачен и гасит '
        'генерацию, а при достижении определённого порога становится прозрачным. '
        'Такой «автоматический клапан» не требует внешней синхронизации и работает '
        'самостоятельно.')
    
    # ===== 5. ПРИМЕНЕНИЕ =====
    add_slide_marker(doc, 7)
    add_gost_heading(doc, '5 Области применения', level=1)
    
    add_gost_paragraph(doc, 
        'Метод модуляции добротности находит широкое применение в современных '
        'технологиях. В лазерной дальнометрии и лидарах короткий мощный импульс '
        'обеспечивает высочайшую точность измерения расстояний, что критически важно '
        'для систем навигации беспилотных автомобилей.')
    
    add_gost_paragraph(doc, 
        'В микрообработке материалов огромная пиковая мощность позволяет испарять '
        'материал мгновенно, не успевая нагреть соседние области. Этот эффект '
        'называется «холодной абляцией» и используется для прецизионной маркировки, '
        'гравировки и резки.')
    
    add_gost_paragraph(doc, 
        'В медицине наносекундные импульсы применяются для удаления татуировок, '
        'литотрипсии — дробления камней в почках, а также в офтальмологии.')
    
    # ===== 6. ПЛЮСЫ И МИНУСЫ =====
    add_slide_marker(doc, 8)
    add_gost_heading(doc, '6 Преимущества и ограничения метода', level=1)
    
    add_gost_paragraph(doc, 
        'К основным преимуществам метода относятся: достижение огромной пиковой '
        'мощности на уровне мегаватт и гигаватт; относительная простота технической '
        'реализации; высокая надёжность и воспроизводимость импульсов.')
    
    add_gost_paragraph(doc, 
        'Вместе с тем метод имеет и ограничения. Длительность импульсов составляет '
        'порядка наносекунд, что является слишком большим для некоторых сверхбыстрых '
        'процессов — в таких случаях применяют метод синхронизации мод, дающий '
        'пико- и фемтосекундные импульсы. Кроме того, высокие пиковые мощности '
        'требуют применения особо прочной оптики, устойчивой к оптическому пробою.')
    
    # ===== 7. ЗАКЛЮЧЕНИЕ =====
    add_slide_marker(doc, 9)
    add_gost_heading(doc, '7 Заключение', level=1)
    
    add_gost_paragraph(doc, 
        'Модуляция добротности — это элегантный и эффективный способ превратить '
        'обычную лазерную «лампочку» в мощный «ударный инструмент». Управляя '
        'качеством зеркал резонатора, можно накапливать энергию в активной среде и '
        'мгновенно высвобождать её в виде гигантского импульса.')
    
    add_gost_paragraph(doc, 
        'Метод нашёл широкое применение в науке, промышленности и медицине, '
        'оставаясь одним из базовых инструментов современной лазерной физики.')
    
    # ===== СПИСОК ЛИТЕРАТУРЫ =====
    add_slide_marker(doc, 10)
    add_gost_heading(doc, 'СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ', level=1)
    
    refs = [
        'Звелто, О. Принципы лазеров / О. Звелто ; пер. с англ. — 5-е изд. — Москва : ЛАНЬ, 2022. — 668 с. — ISBN 978-5-8114-0734-2. — Текст : непосредственный.',
        'Милонни, П. Лазеры / П. Милонни, Дж. Эберли ; пер. с англ. — Москва : Бином. Лаборатория знаний, 2021. — 760 с. — ISBN 978-5-99112-456-3. — Текст : непосредственный.',
        'Дьяков, Е. Б. Физика лазеров : учебное пособие / Е. Б. Дьяков. — Москва : ФИЗМАТЛИТ, 2020. — 424 с. — ISBN 978-5-9221-1987-4. — Текст : непосредственный.',
        'Свечников, Г. В. Лазерная техника и технология / Г. В. Свечников. — Киев : Наук. думка, 2019. — 320 с. — Текст : непосредственный.',
        'Saleh, B. E. A. Fundamentals of Photonics / B. E. A. Saleh, M. C. Teich. — 3rd ed. — Hoboken : Wiley, 2019. — 1152 p. — ISBN 978-1-119-50125-7. — Текст : непосредственный.',
        'Letokhov, V. S. Laser physics / V. S. Letokhov. — Oxford : Oxford University Press, 2021. — 720 p. — ISBN 978-0-19-882462-3. — Текст : непосредственный.',
    ]
    
    for i, ref in enumerate(refs, 1):
        p = doc.add_paragraph()
        run = p.add_run(f'{i}. {ref}')
        run.font.name = 'Times New Roman'
        run.font.size = DocxPt(14)
        p.paragraph_format.first_line_indent = None
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.left_indent = DocxCm(1.0)
        p.paragraph_format.space_after = DocxPt(6)
    
    # Финальная пометка
    add_slide_marker(doc, 11)
    add_gost_paragraph(doc, 
        'Спасибо за внимание! Докладчики готовы ответить на ваши вопросы.',
        first_line_indent=1.25, bold=True)
    
    doc.save('Q_Switching_Report_GOST.docx')
    print("✅ Доклад по ГОСТ сохранён: Q_Switching_Report_GOST.docx")

# ==========================================
# ЗАПУСК
# ==========================================
if __name__ == "__main__":
    print("Генерация материалов в стиле СПбГЭТУ «ЛЭТИ»...")
    generate_images()
    create_presentation()
    create_document_gost()
    print("🎉 Готово! Проверьте текущую папку.")