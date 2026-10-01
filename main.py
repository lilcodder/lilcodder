# generate_clock.py
from datetime import datetime, timezone, timedelta
from PIL import Image, ImageDraw, ImageFont

WEEKS = 53
DAYS = 7
CELL_SIZE = 10
GAP = 3
STEP = CELL_SIZE + GAP

START_X = 65
START_Y = 62
CANVAS_WIDTH = START_X + (WEEKS * STEP) + 30
CANVAS_HEIGHT = 185

THEMES = {
    "light": {
        "bg": "#FFFFFF",
        "border": "#D0D7DE",
        "text": "#24292F",
        "sub_text": "#57604A",
        "empty": "#EBEDF0",
        "active": "#216E39",
        "levels": ["#EBEDF0", "#9BE9A8", "#40C463", "#30A14E", "#216E39"],
    },
    "dark": {
        "bg": "#0D1117",
        "border": "#30363D",
        "text": "#E6EDF3",
        "sub_text": "#7D8590",
        "empty": "#161B22",
        "active": "#39D353",
        "levels": ["#161B22", "#0E4429", "#006D32", "#26A641", "#39D353"],
    },
}

MONTHS = ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"]
DAY_LABELS = [(1, "Mon"), (3, "Wed"), (5, "Fri")]

# Матрицы шрифта 3x5 для цифр (индексы по Y: 0..4, по X: 0..2)
DIGITS = {
    "0": ["111", "101", "101", "101", "111"],
    "1": ["010", "110", "010", "010", "111"],
    "2": ["111", "001", "111", "100", "111"],
    "3": ["111", "001", "111", "001", "111"],
    "4": ["101", "101", "111", "001", "001"],
    "5": ["111", "100", "111", "001", "111"],
    "6": ["111", "100", "111", "101", "111"],
    "7": ["111", "001", "010", "010", "010"],
    "8": ["111", "101", "111", "101", "111"],
    "9": ["111", "101", "111", "001", "111"],
}


def build_clock_grid(time_str, colon_visible=True):
    # Пустая матрица 53x7
    grid = [[0 for _ in range(DAYS)] for _ in range(WEEKS)]
    
    # Центрируем цифры по высоте (смещение по Y = 1)
    y_offset = 1
    
    # Разметка по X (всего ширина блока цифр ~ 23 колонки, ставим по центру сетки)
    # Позиции колонок для H1, H2, :, M1, M2
    cursor_x = 16

    # Цифра 1
    for row_idx, row in enumerate(DIGITS[time_str[0]]):
        for col_idx, ch in enumerate(row):
            if ch == "1":
                grid[cursor_x + col_idx][y_offset + row_idx] = 4
    cursor_x += 4

    # Цифра 2
    for row_idx, row in enumerate(DIGITS[time_str[1]]):
        for col_idx, ch in enumerate(row):
            if ch == "1":
                grid[cursor_x + col_idx][y_offset + row_idx] = 4
    cursor_x += 4

    # Двоеточие (мигает)
    if colon_visible:
        grid[cursor_x][y_offset + 1] = 4
        grid[cursor_x][y_offset + 3] = 4
    cursor_x += 2

    # Цифра 3
    for row_idx, row in enumerate(DIGITS[time_str[3]]):
        for col_idx, ch in enumerate(row):
            if ch == "1":
                grid[cursor_x + col_idx][y_offset + row_idx] = 4
    cursor_x += 4

    # Цифра 4
    for row_idx, row in enumerate(DIGITS[time_str[4]]):
        for col_idx, ch in enumerate(row):
            if ch == "1":
                grid[cursor_x + col_idx][y_offset + row_idx] = 4

    return grid


def render_frame(grid, theme_name, time_str, font):
    cfg = THEMES[theme_name]
    img = Image.new("RGBA", (CANVAS_WIDTH, CANVAS_HEIGHT), cfg["bg"])
    draw = ImageDraw.Draw(img)

    # Рамка
    draw.rounded_rectangle([15, 35, CANVAS_WIDTH - 15, CANVAS_HEIGHT - 15], radius=6, outline=cfg["border"], width=1)
    draw.text((15, 12), f"Moscow Time: {time_str} MSK", fill=cfg["text"], font=font)
    draw.text((CANVAS_WIDTH - 145, 14), "Contribution settings ▾", fill=cfg["sub_text"], font=font)

    # Месяцы
    month_step = (WEEKS * STEP) / 12
    for idx, month in enumerate(MONTHS):
        x = int(START_X + idx * month_step)
        draw.text((x, 42), month, fill=cfg["sub_text"], font=font)

    # Дни
    for day_idx, label in DAY_LABELS:
        y = START_Y + day_idx * STEP - 1
        draw.text((30, y), label, fill=cfg["sub_text"], font=font)

    # Точки
    for w in range(WEEKS):
        for d in range(DAYS):
            val = grid[w][d]
            color = cfg["active"] if val == 4 else cfg["empty"]
            x0 = START_X + w * STEP
            y0 = START_Y + d * STEP
            draw.rounded_rectangle([x0, y0, x0 + CELL_SIZE, y0 + CELL_SIZE], radius=2, fill=color)

    # Легенда
    legend_x = CANVAS_WIDTH - 135
    legend_y = CANVAS_HEIGHT - 28
    draw.text((legend_x - 30, legend_y), "Less", fill=cfg["sub_text"], font=font)
    for i, col in enumerate(cfg["levels"]):
        lx = legend_x + i * 12
        draw.rounded_rectangle([lx, legend_y + 1, lx + 9, legend_y + 10], radius=2, fill=col)
    draw.text((legend_x + 65, legend_y), "More", fill=cfg["sub_text"], font=font)

    return img


def generate_gifs_for_theme(theme_name, time_str, font, output_file):
    # Кадр 1: точки горят
    grid_on = build_clock_grid(time_str, colon_visible=True)
    frame_on = render_frame(grid_on, theme_name, time_str, font)

    # Кадр 2: точки погасли
    grid_off = build_clock_grid(time_str, colon_visible=False)
    frame_off = render_frame(grid_off, theme_name, time_str, font)

    # 1000 мс на кадр = ровно 1 секунда горит, 1 секунда не горит
    frame_on.save(
        output_file,
        save_all=True,
        append_images=[frame_off],
        duration=[1000, 1000],
        loop=0
    )


def main():
    # Текущее время по МСК (UTC+3)
    msk_time = datetime.now(timezone.utc) + timedelta(hours=3)
    time_str = msk_time.strftime("%H:%M")

    try:
        font = ImageFont.truetype("arial.ttf", 11)
    except IOError:
        font = ImageFont.load_default()

    generate_gifs_for_theme("light", time_str, font, "commit_clock_light.gif")
    generate_gifs_for_theme("dark", time_str, font, "commit_clock_dark.gif")
    print(f"Часы сгенерированы: {time_str} MSK")


if __name__ == "__main__":
    main()