from PIL import Image, ImageDraw, ImageFilter, ImageFont
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

WIDTH, HEIGHT = 1140, 780

SKIN_PATH          = "reqwai.png"
SWORD_ICON_PATH    = "Diamond_Sword_JE3_BE3.png"
TESTER_AVATAR_PATH = "tirtester.png"
FONT_PATH          = "Inter_24pt-Bold.ttf"
FONT_PATH_REGULAR  = "Inter_24pt-Regular.ttf"
OUTPUT_PATH        = "reqwai_result.png"

PLAYER_NAME = "reqwai"
TIER_RESULT = "High Tier 1"
PREV_TIER   = "Low Tier 4"
TESTER_NAME = "Sahakyan"
DATE_TEXT   = "19 мая 2026 г."

WHITE      = (255, 255, 255, 255)
LIGHT_GRAY = (200, 215, 240, 160)
CARD_BG    = (10, 22, 70, 210)

TOP_COLOR    = (4,  12,  65)
MID_COLOR    = (10, 35, 130)
BOTTOM_COLOR = (25, 85, 200)

PAD = 55


def mix(c1, c2, t):
    return tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3))


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        FONT_PATH if bold else FONT_PATH_REGULAR,
        FONT_PATH,
        "arialbd.ttf" if bold else "arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (IOError, OSError):
            continue
    log.warning("Не удалось загрузить TrueType-шрифт, используется встроенный.")
    return ImageFont.load_default()


def build_gradient() -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        if t < 0.55:
            color = mix(TOP_COLOR, MID_COLOR, t / 0.55)
        else:
            color = mix(MID_COLOR, BOTTOM_COLOR, (t - 0.55) / 0.45)
        draw.line([(0, y), (WIDTH, y)], fill=color)
    return img


def build_tierlist_card(f_card, f_card_sm) -> Image.Image:
    card_w, card_h = 250, 85
    card = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle([0, 0, card_w, card_h], radius=16, fill=CARD_BG)

    try:
        sword = Image.open(SWORD_ICON_PATH).convert("RGBA")
        sword = sword.resize((50, 50), Image.Resampling.LANCZOS)
        card.alpha_composite(sword, (18, 18))
    except Exception as e:
        log.warning("Не удалось загрузить иконку меча: %s", e)
        draw.text((18, 18), "⚔", font=load_font(30), fill=WHITE)

    draw.text((85, 20), "Sword Tierlist", font=f_card,    fill=WHITE)
    draw.text((85, 46), DATE_TEXT,        font=f_card_sm, fill=LIGHT_GRAY)
    return card


def paste_tester_badge(result: Image.Image, f_title, f_name) -> Image.Image:
    tw, th = 220, 55
    tx = WIDTH - tw - PAD
    ty = 35

    badge = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    draw  = ImageDraw.Draw(badge)
    draw.rounded_rectangle([0, 0, tw, th], radius=12, fill=CARD_BG)
    draw.text((15,  8), "Тиртестер", font=f_title, fill=LIGHT_GRAY)
    draw.text((15, 26), TESTER_NAME, font=f_name,  fill=WHITE)
    result.alpha_composite(badge, (tx, ty))

    try:
        avatar = Image.open(TESTER_AVATAR_PATH).convert("RGBA")
        target_h = 36
        scale    = target_h / avatar.height
        avatar   = avatar.resize(
            (int(avatar.width * scale), target_h),
            Image.Resampling.LANCZOS,
        )
        hx = tx + tw - avatar.width - 12
        hy = ty + (th - avatar.height) // 2
        layer = Image.new("RGBA", result.size, (0, 0, 0, 0))
        layer.paste(avatar, (hx, hy))
        result = Image.alpha_composite(result, layer)
    except Exception as e:
        log.warning("Не удалось загрузить аватар тестера: %s", e)

    return result


def paste_skin(result: Image.Image) -> Image.Image:
    try:
        skin  = Image.open(SKIN_PATH).convert("RGBA")
        max_w = int(WIDTH  * 0.32)
        max_h = int(HEIGHT * 0.60)
        scale = min(max_w / skin.width, max_h / skin.height)
        skin  = skin.resize(
            (int(skin.width * scale), int(skin.height * scale)),
            Image.Resampling.LANCZOS,
        )

        sx = PAD
        sy = HEIGHT - skin.height + 5

        shadow_layer = Image.new("RGBA", skin.size, (0, 0, 0, 0))
        shadow_layer.putalpha(skin.getchannel("A"))

        shadow_canvas = Image.new("RGBA", (skin.width + 100, skin.height + 100), (0, 0, 0, 0))
        shadow_canvas.paste(shadow_layer, (50, 50))
        shadow_canvas = shadow_canvas.filter(ImageFilter.GaussianBlur(35))

        result.alpha_composite(shadow_canvas, (sx - 50 + 10, sy - 50 + 15))
        result.alpha_composite(skin, (sx, sy))
    except Exception as e:
        log.warning("Не удалось загрузить скин: %s", e)
    return result


def render() -> None:
    result = build_gradient().convert("RGBA")

    glow   = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw_g = ImageDraw.Draw(glow)
    draw_g.ellipse(
        [int(WIDTH * 0.1), int(HEIGHT * 0.4), int(WIDTH * 0.95), int(HEIGHT * 1.2)],
        fill=(60, 120, 245, 75),
    )
    glow   = glow.filter(ImageFilter.GaussianBlur(130))
    result = Image.alpha_composite(result, glow)

    draw = ImageDraw.Draw(result)

    f_small        = load_font(16)
    f_name         = load_font(56, bold=True)
    f_med          = load_font(28, bold=True)
    f_tier         = load_font(62, bold=True)
    f_card         = load_font(20, bold=True)
    f_card_sm      = load_font(14)
    f_tester_title = load_font(13)
    f_tester_name  = load_font(16, bold=True)

    draw.text((PAD, 35), "Результат тиртеста", font=f_small, fill=LIGHT_GRAY)
    draw.text((PAD, 60), PLAYER_NAME,          font=f_name,  fill=WHITE)

    card = build_tierlist_card(f_card, f_card_sm)
    result.alpha_composite(card, (PAD, 155))

    cx = int(WIDTH * 0.44)
    draw.text((cx, 35),  "Предыдущий тир",   font=f_small, fill=LIGHT_GRAY)
    draw.text((cx, 65),  PREV_TIER,           font=f_med,   fill=WHITE)
    draw.text((cx, 130), "Приобретённый тир", font=f_small, fill=LIGHT_GRAY)
    draw.text((cx, 160), TIER_RESULT,         font=f_tier,  fill=WHITE)

    result = paste_tester_badge(result, f_tester_title, f_tester_name)
    draw   = ImageDraw.Draw(result)

    result = paste_skin(result)

    result.convert("RGB").save(OUTPUT_PATH, quality=95)
    log.info("Сохранено: %s", OUTPUT_PATH)


if __name__ == "__main__":
    render()