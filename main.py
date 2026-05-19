from PIL import Image, ImageDraw, ImageFilter, ImageFont

WIDTH, HEIGHT = 1140, 780
SKIN_PATH = "reqwai.png"
SWORD_ICON_PATH = "Diamond_Sword_JE3_BE3.png"
TESTER_AVATAR_PATH = "tirtester.png"
FONT_PATH = "Inter_24pt-Bold.ttf"
OUTPUT_PATH = "reqwai_result.png"

PLAYER_NAME = "reqwai"
TIER_RESULT = "High Tier 1"
PREV_TIER = "Low Tier 4"
TESTER_NAME = "Sahakyan"
DATE_TEXT = "19 мая 2026 г."

WHITE = (255, 255, 255, 255)
LIGHT_GRAY = (200, 215, 240, 160)
CARD_BG = (10, 22, 70, 210)

def mix(c1, c2, t):
    return tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3))

def load_f(size, bold=False):
    try:
        if "arial" in FONT_PATH.lower() and bold:
            return ImageFont.truetype("arialbd.ttf", size)
        return ImageFont.truetype(FONT_PATH, size)
    except:
        try:
            return ImageFont.truetype("arialbd.ttf" if bold else "arial.ttf", size)
        except:
            return ImageFont.load_default()

top_color    = (4,  12,  65)
mid_color    = (10, 35, 130)
bottom_color = (25, 85, 200)

gradient = Image.new("RGB", (1, HEIGHT))
for y in range(HEIGHT):
    t = y / (HEIGHT - 1)
    if t < 0.55:
        color = mix(top_color, mid_color, t / 0.55)
    else:
        color = mix(mid_color, bottom_color, (t - 0.55) / 0.45)
    gradient.putpixel((0, y), color)

result = gradient.resize((WIDTH, HEIGHT)).convert("RGBA")

glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
draw_g = ImageDraw.Draw(glow)
draw_g.ellipse([int(WIDTH*0.1), int(HEIGHT*0.4), int(WIDTH*0.95), int(HEIGHT*1.2)], fill=(60, 120, 245, 75))
glow = glow.filter(ImageFilter.GaussianBlur(130))
result = Image.alpha_composite(result, glow)

draw = ImageDraw.Draw(result)

f_small        = load_f(16, bold=False)
f_name         = load_f(56, bold=True)
f_med          = load_f(28, bold=True)
f_tier         = load_f(62, bold=True)
f_card         = load_f(20, bold=True)
f_card_sm      = load_f(14, bold=False)
f_tester_title = load_f(13, bold=False)
f_tester_name  = load_f(16, bold=True)

pad = 55

draw.text((pad, 35), "Результат тиртеста", font=f_small, fill=LIGHT_GRAY)
draw.text((pad, 60), PLAYER_NAME, font=f_name, fill=WHITE)

card_x, card_y = pad, 155
card_w, card_h = 250, 85
card_bg = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
draw_c = ImageDraw.Draw(card_bg)
draw_c.rounded_rectangle([0, 0, card_w, card_h], radius=16, fill=CARD_BG)

try:
    sword_img = Image.open(SWORD_ICON_PATH).convert("RGBA")
    sword_img = sword_img.resize((50, 50), Image.Resampling.LANCZOS)
    card_bg.alpha_composite(sword_img, (18, 18))
except:
    draw_c.text((18, 18), "⚔", font=load_f(30), fill=WHITE)

draw_c.text((85, 20), "Sword Tierlist", font=f_card, fill=WHITE)
draw_c.text((85, 46), DATE_TEXT, font=f_card_sm, fill=LIGHT_GRAY)

result.alpha_composite(card_bg, (card_x, card_y))

cx = 500
draw.text((cx, 35), "Предыдущий тир", font=f_small, fill=LIGHT_GRAY)
draw.text((cx, 65), PREV_TIER, font=f_med, fill=WHITE)

draw.text((cx, 130), "Приобретённый тир", font=f_small, fill=LIGHT_GRAY)
draw.text((cx, 160), TIER_RESULT, font=f_tier, fill=WHITE)

tx = WIDTH - 275
ty = 35
tw, th = 220, 55

tester_bg_layer = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
draw_t = ImageDraw.Draw(tester_bg_layer)
draw_t.rounded_rectangle([0, 0, tw, th], radius=12, fill=CARD_BG)
result.alpha_composite(tester_bg_layer, (tx, ty))

draw.text((tx + 15, ty + 8), "Тиртестер", font=f_tester_title, fill=LIGHT_GRAY)
draw.text((tx + 15, ty + 26), TESTER_NAME, font=f_tester_name, fill=WHITE)

try:
    trainer_head = Image.open(TESTER_AVATAR_PATH).convert("RGBA")
    target_h = 36
    
    scale_y = target_h / trainer_head.height
    new_size_y = (int(trainer_head.width * scale_y), target_h)
    trainer_head = trainer_head.resize(new_size_y, Image.Resampling.LANCZOS)
    
    hx = tx + tw - (trainer_head.width + 12)
    hy = ty + (th - trainer_head.height) // 2
    
    head_layer = Image.new("RGBA", result.size, (0, 0, 0, 0))
    head_layer.paste(trainer_head, (hx, hy))
    result = Image.alpha_composite(result, head_layer)
    draw = ImageDraw.Draw(result)
except:
    pass

try:
    skin = Image.open(SKIN_PATH).convert("RGBA")
    
    max_w = int(WIDTH * 0.32)
    max_h = int(HEIGHT * 0.60)
    scale = min(max_w / skin.width, max_h / skin.height)
    new_size = (int(skin.width * scale), int(skin.height * scale))
    skin = skin.resize(new_size, Image.Resampling.LANCZOS)

    sx = 55
    sy = HEIGHT - skin.height + 5

    shadow_layer = Image.new("RGBA", skin.size, (0, 0, 0, 140))
    shadow_layer.putalpha(skin.getchannel("A"))
    
    shadow = Image.new("RGBA", (skin.width + 100, skin.height + 100), (0,0,0,0))
    shadow.paste(shadow_layer, (50, 50))
    shadow = shadow.filter(ImageFilter.GaussianBlur(35))
    
    result.alpha_composite(shadow, (sx - 50 + 10, sy - 50 + 15))
    result.alpha_composite(skin, (sx, sy))
except:
    pass

result = result.convert("RGB")
result.save(OUTPUT_PATH, quality=95)