import os
import textwrap
import random
import asyncio
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from pyrogram import filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from SHUKLAMUSIC import app

# ==================== QUOTE MIRROR SYSTEM ====================

# Store user preferences
user_quote_prefs = {}

@app.on_message(filters.command("q"))
async def quote_mirror(_, message: Message):
    """Create a mirrored quote from replied message"""
    chat_id = message.chat.id
    reply = message.reply_to_message

    if not reply:
        await message.reply_text(
            "**📝 Quote Mirror System**\n\n"
            "Reply to a message with:\n"
            "• `/q` - Default mirrored quote\n"
            "• `/q r` - Random style mirrored quote\n"
            "• `/q style` - Choose specific style\n\n"
            "**Styles available:**\n"
            "🔹 mirror - Reflection effect\n"
            "🔹 glass - Glass reflection\n"
            "🔹 water - Water ripple\n"
            "🔹 neon - Neon glow\n"
            "🔹 vintage - Vintage style"
        )
        return

    text = reply.text or reply.caption
    if not text:
        await message.reply_text("**Cannot quote media without text!**")
        return

    user = reply.from_user
    name = user.first_name if user else "Unknown"
    user_id = user.id if user else None

    # Check if user has style preference
    style = "mirror"  # default
    if user_id and user_id in user_quote_prefs:
        style = user_quote_prefs[user_id].get("style", "mirror")

    msg = await message.reply_text("<blockquote>🔄 Creating mirrored quote...</blockquote>")
    
    quote = await create_mirror_quote(text, name, style)
    await app.send_photo(chat_id, photo=quote, caption=f"**✨ Mirrored Quote**\n\n**Style:** {style.upper()}\n**By:** {name}")
    
    await msg.delete()
    os.remove(quote)

@app.on_message(filters.command("q r"))
async def quote_random(_, message: Message):
    """Create a random styled mirrored quote"""
    chat_id = message.chat.id
    reply = message.reply_to_message

    if not reply:
        await message.reply_text("**Reply to a message for a random mirrored quote!**")
        return

    text = reply.text or reply.caption
    if not text:
        await message.reply_text("**Cannot quote media without text!**")
        return

    user = reply.from_user
    name = user.first_name if user else "Unknown"

    msg = await message.reply_text("<blockquote>🎲 Creating random mirrored quote...</blockquote>")
    
    styles = ["mirror", "glass", "water", "neon", "vintage"]
    style = random.choice(styles)
    quote = await create_mirror_quote(text, name, style)
    await app.send_photo(chat_id, photo=quote, caption=f"**✨ Random Mirrored Quote**\n\n**Style:** {style.upper()}\n**By:** {name}")
    
    await msg.delete()
    os.remove(quote)

@app.on_message(filters.command("q style"))
async def quote_style(_, message: Message):
    """Set preferred quote style"""
    user_id = message.from_user.id
    
    if len(message.text.split()) < 2:
        await message.reply_text(
            "**🎨 Quote Styles**\n\n"
            "Choose your preferred style:\n"
            "• `mirror` - Classic mirror reflection\n"
            "• `glass` - Glass reflection effect\n"
            "• `water` - Water ripple effect\n"
            "• `neon` - Neon glow effect\n"
            "• `vintage` - Vintage sepia effect\n\n"
            "Usage: `/q style [style_name]`"
        )
        return
    
    style = message.text.split(None, 1)[1].lower()
    valid_styles = ["mirror", "glass", "water", "neon", "vintage"]
    
    if style not in valid_styles:
        await message.reply_text(f"**Invalid style!** Choose from: {', '.join(valid_styles)}")
        return
    
    if user_id not in user_quote_prefs:
        user_quote_prefs[user_id] = {}
    
    user_quote_prefs[user_id]["style"] = style
    await message.reply_text(f"**✅ Quote style set to:** {style.upper()}")

# ==================== MIRROR QUOTE CREATION FUNCTIONS ====================

async def create_mirror_quote(text, name, style="mirror"):
    """Create a mirrored quote with various styles"""
    
    # Create base image
    width, height = 800, 500
    img = Image.new('RGB', (width, height), color=(20, 20, 35))
    draw = ImageDraw.Draw(img)
    
    # Load font
    try:
        font_path = "./SHUKLAMUSIC/assets/default.ttf"
        if not os.path.exists(font_path):
            font_path = "arial.ttf" if os.name == "nt" else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        font = ImageFont.truetype(font_path, 28)
        name_font = ImageFont.truetype(font_path, 22)
        big_font = ImageFont.truetype(font_path, 60)
    except:
        font = ImageFont.load_default()
        name_font = ImageFont.load_default()
        big_font = ImageFont.load_default()
    
    # Wrap text
    wrapped_text = textwrap.fill(text, width=35)
    lines = wrapped_text.split('\n')
    
    # Calculate text height
    line_height = 40
    total_text_height = len(lines) * line_height
    
    # Draw mirror effect based on style
    if style == "mirror":
        img = await create_mirror_effect(img, draw, lines, name, font, name_font, big_font, width, height)
    elif style == "glass":
        img = await create_glass_effect(img, draw, lines, name, font, name_font, big_font, width, height)
    elif style == "water":
        img = await create_water_effect(img, draw, lines, name, font, name_font, big_font, width, height)
    elif style == "neon":
        img = await create_neon_effect(img, draw, lines, name, font, name_font, big_font, width, height)
    elif style == "vintage":
        img = await create_vintage_effect(img, draw, lines, name, font, name_font, big_font, width, height)
    else:
        # Default mirror
        img = await create_mirror_effect(img, draw, lines, name, font, name_font, big_font, width, height)
    
    # Save image
    image_path = f"quote_{random.randint(1, 99999)}.png"
    img.save(image_path, "PNG")
    return image_path

async def create_mirror_effect(img, draw, lines, name, font, name_font, big_font, width, height):
    """Classic mirror reflection effect"""
    
    # Draw background gradient
    for i in range(height):
        color = (int(20 + (i/height) * 30), int(20 + (i/height) * 20), int(35 + (i/height) * 40))
        draw.line([(0, i), (width, i)], fill=color)
    
    # Draw decorative border
    draw.rectangle([20, 20, width-20, height-20], outline=(255, 215, 0), width=2)
    
    # Draw mirror line
    mirror_y = height // 2 + 20
    draw.line([(30, mirror_y), (width-30, mirror_y)], fill=(255, 215, 0), width=1)
    
    # Draw quote marks
    draw.text((40, 40), "❝", font=big_font, fill=(255, 215, 0, 100))
    draw.text((width-80, height-100), "❞", font=big_font, fill=(255, 215, 0, 100))
    
    # Draw text
    y_pos = 80
    for line in lines:
        # Main text
        draw.text((50, y_pos), line, font=font, fill=(255, 255, 255))
        # Mirror text (below the line)
        mirror_y_pos = height - y_pos - 20
        if mirror_y_pos > mirror_y + 20:
            # Semi-transparent mirror text
            draw.text((50, mirror_y_pos), line, font=font, fill=(255, 255, 255, 50))
        y_pos += line_height
    
    # Draw name at bottom
    draw.text((50, height-60), f"— {name}", font=name_font, fill=(255, 215, 0))
    
    return img

async def create_glass_effect(img, draw, lines, name, font, name_font, big_font, width, height):
    """Glass reflection effect"""
    
    # Glass background
    for i in range(height):
        color = (int(40 + (i/height) * 20), int(50 + (i/height) * 30), int(70 + (i/height) * 40))
        draw.line([(0, i), (width, i)], fill=color)
    
    # Glass shine effect
    for i in range(50, 200, 3):
        alpha = int(20 - (i-50) / 150 * 20)
        draw.line([(i, 0), (i+100, height)], fill=(255, 255, 255, alpha))
    
    # Draw glass border
    draw.rectangle([25, 25, width-25, height-25], outline=(200, 230, 255), width=2)
    
    # Draw quote
    y_pos = 80
    for line in lines:
        draw.text((50, y_pos), line, font=font, fill=(220, 240, 255))
        y_pos += line_height
    
    draw.text((50, height-60), f"— {name}", font=name_font, fill=(200, 230, 255))
    
    # Add glass reflection overlay
    overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    for i in range(0, 200, 5):
        overlay_draw.line([(i, 0), (i+50, height)], fill=(255, 255, 255, 15))
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    
    return img

async def create_water_effect(img, draw, lines, name, font, name_font, big_font, width, height):
    """Water ripple effect"""
    
    # Water background
    for i in range(height):
        color = (int(0 + (i/height) * 30), int(30 + (i/height) * 50), int(80 + (i/height) * 100))
        draw.line([(0, i), (width, i)], fill=color)
    
    # Draw water ripples
    for i in range(0, height, 30):
        offset = 10 * (i/height)
        for x in range(0, width, 5):
            y_ripple = i + 5 * (x/width)
            draw.point((x, int(y_ripple)), fill=(100, 180, 255, 50))
    
    # Draw text with water effect
    y_pos = 80
    for line in lines:
        # Slightly distorted text
        for char_idx, char in enumerate(line):
            x_offset = char_idx * 15 + 50
            y_offset = y_pos + 3 * (char_idx/len(line))
            draw.text((x_offset, y_offset), char, font=font, fill=(180, 220, 255))
        y_pos += line_height
    
    draw.text((50, height-60), f"— {name}", font=name_font, fill=(100, 200, 255))
    
    return img

async def create_neon_effect(img, draw, lines, name, font, name_font, big_font, width, height):
    """Neon glow effect"""
    
    # Dark background
    for i in range(height):
        color = (int(5 + (i/height) * 10), int(5 + (i/height) * 10), int(15 + (i/height) * 20))
        draw.line([(0, i), (width, i)], fill=color)
    
    # Neon border
    draw.rectangle([15, 15, width-15, height-15], outline=(0, 255, 255), width=3)
    draw.rectangle([20, 20, width-20, height-20], outline=(255, 0, 255), width=1)
    
    # Neon text glow effect
    y_pos = 80
    for line in lines:
        # Multiple layers for glow
        for offset in range(5, 0, -1):
            color_value = 255 - offset * 20
            draw.text((50 + offset, y_pos + offset), line, font=font, fill=(0, color_value, color_value, 20))
        
        # Main text
        draw.text((50, y_pos), line, font=font, fill=(0, 255, 255))
        y_pos += line_height
    
    # Neon name
    draw.text((50, height-60), f"— {name}", font=name_font, fill=(255, 0, 255))
    
    return img

async def create_vintage_effect(img, draw, lines, name, font, name_font, big_font, width, height):
    """Vintage sepia effect"""
    
    # Vintage background
    for i in range(height):
        color = (int(200 - (i/height) * 60), int(180 - (i/height) * 50), int(150 - (i/height) * 40))
        draw.line([(0, i), (width, i)], fill=color)
    
    # Vintage border
    draw.rectangle([25, 25, width-25, height-25], outline=(139, 90, 43), width=3)
    draw.rectangle([30, 30, width-30, height-30], outline=(160, 120, 70), width=1)
    
    # Vintage text
    y_pos = 80
    for line in lines:
        # Text shadow
        draw.text((52, y_pos + 2), line, font=font, fill=(100, 70, 40))
        # Main text
        draw.text((50, y_pos), line, font=font, fill=(60, 40, 20))
        y_pos += line_height
    
    draw.text((52, height-58), f"— {name}", font=name_font, fill=(100, 70, 40))
    draw.text((50, height-60), f"— {name}", font=name_font, fill=(60, 40, 20))
    
    # Add vintage texture
    for i in range(0, height, 2):
        for j in range(0, width, 2):
            if random.random() < 0.01:
                draw.point((j, i), fill=(139, 90, 43, 20))
    
    return img

# ==================== QUOTE STYLE COMMAND ====================

@app.on_message(filters.command("qstyles"))
async def list_styles(_, message: Message):
    """List all available quote styles"""
    styles_info = """
**🎨 Available Quote Styles**

**1. mirror** 🔄
Classic mirror reflection effect with mirrored text below

**2. glass** 🪟
Glass reflection effect with shine

**3. water** 💧
Water ripple effect with distorted text

**4. neon** 💫
Neon glow effect with bright colors

**5. vintage** 📜
Vintage sepia effect with old-style look

**How to use:**
• `/q style [style_name]` - Set your preferred style
• `/q` - Create quote with your preferred style
• `/q r` - Create quote with random style

**Set default style:**
`/q style mirror`
    """
    await message.reply_text(styles_info)

# ==================== PREVIEW COMMAND ====================

@app.on_message(filters.command("qpreview"))
async def preview_styles(_, message: Message):
    """Preview all quote styles with a sample text"""
    msg = await message.reply_text("<blockquote>🔄 Generating style previews...</blockquote>")
    
    sample_text = "This is a sample quote to show all available styles."
    sample_name = "Style Preview"
    styles = ["mirror", "glass", "water", "neon", "vintage"]
    
    for style in styles:
        quote = await create_mirror_quote(sample_text, sample_name, style)
        await message.reply_photo(photo=quote, caption=f"**Style:** {style.upper()}")
        os.remove(quote)
    
    await msg.delete()
    await message.reply_text("**✅ All styles previewed above!**")

# ==================== QUOTE STATS ====================

@app.on_message(filters.command("qstats"))
async def quote_stats(_, message: Message):
    """Show quote statistics"""
    total_users = len(user_quote_prefs)
    style_counts = {}
    
    for user_id, prefs in user_quote_prefs.items():
        style = prefs.get("style", "mirror")
        style_counts[style] = style_counts.get(style, 0) + 1
    
    stats_text = f"""
**📊 Quote System Statistics**

**Total Users:** {total_users}

**Style Distribution:**
"""
    for style, count in style_counts.items():
        stats_text += f"• {style.upper()}: {count} users\n"
    
    if not style_counts:
        stats_text += "No styles set yet!\n"
    
    await message.reply_text(stats_text)

print("✅ Quote Mirror System loaded successfully!")
print("Commands: /q, /q r, /q style, /qstyles, /qpreview, /qstats")
        reply_markup=keyboard
    )

print("✅ All modules loaded successfully!")
print("Commands available: /q, /q r, /mmf, /kang, /pack, /kangpack")
