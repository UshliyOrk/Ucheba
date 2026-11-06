import matplotlib.pyplot as plt
import numpy as np

# Данные из таблиц
data = [
    ("XX₁", 1.59, 0.35, "14.09 ГГц"),
    ("Согл₁", 1.03, -0.03, "14.09 ГГц"),
    ("ШЩ₁", 1.15, -0.07, "14.09 ГГц"),
    ("УЩ₁", 0.95, -0.91, "14.09 ГГц"),
    
    ("XX₂", 0.49, -0.23, "13.57 ГГц"),
    ("Согл₂", 1.01, 0.04, "13.57 ГГц"),
    ("ШЩ₂", 0.97, 0.26, "13.57 ГГц"),
    ("УЩ₂", 0.42, -0.16, "13.57 ГГц"),
    
    ("XX₃", 0.53, 0.05, "12.57 ГГц"),
    ("Согл₃", 1.03, -0.10, "12.57 ГГц"),
    ("ШЩ₃", 1.25, -0.30, "12.57 ГГц"),
    ("УЩ₃", 2.22, -0.14, "12.57 ГГц"),
]

colors = {
    "14.09 ГГц": "red",
    "13.57 ГГц": "blue",
    "12.57 ГГц": "green"
}

def z_to_gamma(r, x):
    z = complex(r, x)
    gamma = (z - 1) / (z + 1)
    return gamma.real, gamma.imag

fig, ax = plt.subplots(1, 1, figsize=(12, 12))
ax.set_aspect('equal')
ax.axis('off')
ax.set_xlim(-1.15, 1.15)
ax.set_ylim(-1.15, 1.15)

# Внешняя окружность
outer_circle = plt.Circle((0, 0), 1, fill=False, color='black', linewidth=2)
ax.add_patch(outer_circle)

# Окружности постоянного r с подписями
r_values = [0.2, 0.5, 1, 2, 5]
for r in r_values:
    center_x = r / (r + 1)
    radius = 1 / (r + 1)
    circle = plt.Circle((center_x, 0), radius, fill=False, color='gray', linewidth=1.2, alpha=0.7)
    ax.add_patch(circle)
    
    # Подпись r - ставим в верхней части каждой окружности
    # Для r=1: центр (0.5, 0), радиус 0.5 -> верхняя точка (0.5, 0.5)
    # Ставим чуть ниже верхней точки, чтобы было видно
    label_y = radius * 0.75  # 75% от радиуса вверх от центра
    ax.text(center_x, label_y, f'r={r}', fontsize=10, color='gray', 
           ha='center', va='center', fontweight='bold')

# Дуги постоянного x с подписями
x_values = [0.2, 0.5, 1, 2, 5]
for x in x_values:
    for sign in [1, -1]:
        center_y = sign / x
        radius = 1 / abs(x)
        
        theta = np.linspace(0, 2*np.pi, 200)
        arc_x = 1 + radius * np.cos(theta)
        arc_y = center_y + radius * np.sin(theta)
        
        mask = (arc_x**2 + arc_y**2) <= 1.01
        ax.plot(arc_x[mask], arc_y[mask], 'gray', linewidth=1.2, alpha=0.7)
        
        # Подпись x - ставим вдоль внешнего края диаграммы
        # Точка пересечения дуги x с единичной окружностью:
        # Для дуги с центром (1, sign/x) и радиусом 1/x
        # Пересечение: cos(θ) = 1 - 1/(1+x²), sin(θ) = ±x/(1+x²)
        # Угол от центра единичной окружности:
        angle = np.arctan2(sign * x / (1 + x**2), 1 - 1/(1 + x**2))
        label_r = 1.06  # чуть за пределами диаграммы
        label_x = label_r * np.cos(angle)
        label_y = label_r * np.sin(angle)
        
        x_label = f'x={x}' if sign == 1 else f'x=-{x}'
        rotation = np.degrees(angle)
        # Поворачиваем текст вдоль окружности
        if 90 < rotation < 270 or -270 < rotation < -90:
            rotation += 180
        ax.text(label_x, label_y, x_label, fontsize=9, color='gray', 
               ha='center', va='center', fontweight='bold',
               rotation=rotation)

# Горизонтальная линия
ax.plot([-1, 1], [0, 0], 'gray', linewidth=1.2, alpha=0.7)

# Точки
for name, r, x, freq in data:
    color = colors[freq]
    gamma_real, gamma_imag = z_to_gamma(r, x)
    ax.plot(gamma_real, gamma_imag, 'o', color=color, markersize=12, 
            markeredgecolor='black', markeredgewidth=1.5, alpha=0.9)

# Легенда
legend_elements = [
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', 
               markersize=12, label='14.09 ГГц', markeredgecolor='black'),
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', 
               markersize=12, label='13.57 ГГц', markeredgecolor='black'),
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='green', 
               markersize=12, label='12.57 ГГц', markeredgecolor='black')
]
ax.legend(handles=legend_elements, loc='upper right', fontsize=12, framealpha=0.9)

ax.set_title('Диаграмма Смита — Полные сопротивления нагрузок', fontsize=16, pad=20, fontweight='bold')

plt.tight_layout()
plt.savefig('smith_chart_final_v3.png', dpi=300, bbox_inches='tight')
plt.show()

print("✓ Диаграмма Смита сохранена в файл 'smith_chart_final_v3.png'")