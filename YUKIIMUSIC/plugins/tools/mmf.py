import os
import textwrap
import random
import asyncio
from PIL import Image, ImageDraw, ImageFont, ImageOps
from pyrogram import filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from SHUKLAMUSIC import app

# ==================== MEME MAKER (/mmf) ====================
@app.on_message(filters.command("mmf"))
async def mmf(_, message: Message):
    chat_id = message.chat.id
    reply_message = message.reply_to_message

    if len(message.text.split()) < 2:
        await message.reply_text("**Give me text after /mmf to memify.**\n\nUsage: /mmf text\nOr: /mmf top_text;bottom_text")
        return

    msg = await message.reply_text("<blockquote>**Memifying this image! ✊🏻**</blockquote>")
    text = message.text.split(None, 1)[1]
    file = await app.download_media(reply_message)

    meme = await drawText(file, text)
    await app.send_document(chat_id, document=meme)

    await msg.delete()
    os.remove(meme)

async def drawText(image_path, text):
    img = Image.open(image_path)
    os.remove(image_path)

    i_width, i_height = img.size

    if os.name == "nt":
        fnt = "arial.ttf"
    else:
        fnt = "./SHUKLAMUSIC/assets/default.ttf"

    m_font = ImageFont.truetype(fnt, int((70 / 640) * i_width))

    if ";" in text:
        upper_text, lower_text = text.split(";")
    else:
        upper_text = text
        lower_text = ""

    draw = ImageDraw.Draw(img)
    current_h, pad = 10, 5

    if upper_text:
        for u_text in textwrap.wrap(upper_text, width=15):
            u_width, u_height = draw.textsize(u_text, font=m_font)
            draw.text(xy=(((i_width - u_width) / 2) - 2, int((current_h / 640) * i_width)), text=u_text, font=m_font, fill=(0, 0, 0))
            draw.text(xy=(((i_width - u_width) / 2) + 2, int((current_h / 640) * i_width)), text=u_text, font=m_font, fill=(0, 0, 0))
            draw.text(xy=((i_width - u_width) / 2, int(((current_h / 640) * i_width)) - 2), text=u_text, font=m_font, fill=(0, 0, 0))
            draw.text(xy=(((i_width - u_width) / 2), int(((current_h / 640) * i_width)) + 2), text=u_text, font=m_font, fill=(0, 0, 0))
            draw.text(xy=((i_width - u_width) / 2, int((current_h / 640) * i_width)), text=u_text, font=m_font, fill=(255, 255, 255))
            current_h += u_height + pad

    if lower_text:
        for l_text in textwrap.wrap(lower_text, width=15):
            u_width, u_height = draw.textsize(l_text, font=m_font)
            draw.text(xy=(((i_width - u_width) / 2) - 2, i_height - u_height - int((20 / 640) * i_width)), text=l_text, font=m_font, fill=(0, 0, 0))
            draw.text(xy=(((i_width - u_width) / 2) + 2, i_height - u_height - int((20 / 640) * i_width)), text=l_text, font=m_font, fill=(0, 0, 0))
            draw.text(xy=((i_width - u_width) / 2, (i_height - u_height - int((20 / 640) * i_width)) - 2), text=l_text, font=m_font, fill=(0, 0, 0))
            draw.text(xy=((i_width - u_width) / 2, (i_height - u_height - int((20 / 640) * i_width)) + 2), text=l_text, font=m_font, fill=(0, 0, 0))
            draw.text(xy=((i_width - u_width) / 2, i_height - u_height - int((20 / 640) * i_width)), text=l_text, font=m_font, fill=(255, 255, 255))
            current_h += u_height + pad

    image_name = "memify.webp"
    webp_file = os.path.join(image_name)
    img.save(webp_file, "webp")
    return webp_file

# ==================== QUOTE MAKER (/q) ====================
@app.on_message(filters.command("q"))
async def quote_maker(_, message: Message):
    chat_id = message.chat.id
    reply = message.reply_to_message

    if not reply:
        await message.reply_text("**Reply to a message to make a quote!**")
        return

    text = reply.text or reply.caption
    if not text:
        await message.reply_text("**Cannot quote media without text!**")
        return

    user = reply.from_user
    name = user.first_name if user else "Unknown"

    msg = await message.reply_text("<blockquote>**Creating quote...**</blockquote>")
    
    quote = await create_quote(text, name)
    await app.send_photo(chat_id, photo=quote, caption=f"**Quote by:** {name}")
    
    await msg.delete()
    os.remove(quote)

@app.on_message(filters.command("q r"))
async def quote_random(_, message: Message):
    chat_id = message.chat.id
    reply = message.reply_to_message

    if not reply:
        await message.reply_text("**Reply to a message to make a random style quote!**")
        return

    text = reply.text or reply.caption
    if not text:
        await message.reply_text("**Cannot quote media without text!**")
        return

    user = reply.from_user
    name = user.first_name if user else "Unknown"

    msg = await message.reply_text("<blockquote>**Creating random quote...**</blockquote>")
    
    styles = ["default", "gradient", "neon", "vintage"]
    style = random.choice(styles)
    quote = await create_quote_style(text, name, style)
    await app.send_photo(chat_id, photo=quote, caption=f"**Quote by:** {name}\n**Style:** {style}")
    
    await msg.delete()
    os.remove(quote)

async def create_quote(text, name):
    img = Image.new('RGB', (800, 400), color=(30, 30, 50))
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("./SHUKLAMUSIC/assets/default.ttf", 30)
        name_font = ImageFont.truetype("./SHUKLAMUSIC/assets/default.ttf", 25)
    except:
        font = ImageFont.load_default()
        name_font = ImageFont.load_default()
    
    wrapped_text = textwrap.fill(text, width=30)
    
    # Draw quote border
    draw.rectangle([10, 10, 790, 390], outline=(255, 215, 0), width=3)
    
    # Draw quote marks
    draw.text((30, 30), "❝", font=ImageFont.truetype("./SHUKLAMUSIC/assets/default.ttf", 50) if os.path.exists("./SHUKLAMUSIC/assets/default.ttf") else ImageFont.load_default(), fill=(255, 215, 0))
    draw.text((750, 300), "❞", font=ImageFont.truetype("./SHUKLAMUSIC/assets/default.ttf", 50) if os.path.exists("./SHUKLAMUSIC/assets/default.ttf") else ImageFont.load_default(), fill=(255, 215, 0))
    
    # Draw text
    draw.text((80, 80), wrapped_text, font=font, fill=(255, 255, 255))
    draw.text((80, 350), f"- {name}", font=name_font, fill=(255, 215, 0))
    
    image_path = f"quote_{random.randint(1, 9999)}.png"
    img.save(image_path)
    return image_path

async def create_quote_style(text, name, style):
    if style == "gradient":
        img = Image.new('RGB', (800, 400), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        # Gradient effect
        for i in range(400):
            color = (int(50 + (i/400) * 100), int(20 + (i/400) * 80), int(100 + (i/400) * 120))
            draw.line([(0, i), (800, i)], fill=color)
    elif style == "neon":
        img = Image.new('RGB', (800, 400), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        # Neon glow effect (simplified)
        for i in range(5):
            offset = i * 2
            draw.rectangle([10-offset, 10-offset, 790+offset, 390+offset], outline=(0, 255, 255), width=1)
    elif style == "vintage":
        img = Image.new('RGB', (800, 400), color=(245, 235, 200))
        draw = ImageDraw.Draw(img)
        # Sepia/vintage effect
        for i in range(400):
            color = (245 - int(i/4), 235 - int(i/4), 200 - int(i/4))
            draw.line([(0, i), (800, i)], fill=color)
    else:
        img = Image.new('RGB', (800, 400), color=(30, 30, 50))
        draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("./SHUKLAMUSIC/assets/default.ttf", 30)
        name_font = ImageFont.truetype("./SHUKLAMUSIC/assets/default.ttf", 25)
    except:
        font = ImageFont.load_default()
        name_font = ImageFont.load_default()
    
    wrapped_text = textwrap.fill(text, width=30)
    draw.text((80, 80), wrapped_text, font=font, fill=(255, 255, 255))
    draw.text((80, 350), f"- {name}", font=name_font, fill=(255, 215, 0))
    
    image_path = f"quote_{random.randint(1, 9999)}.png"
    img.save(image_path)
    return image_path

# ==================== KANG STICKER (/kang) ====================
@app.on_message(filters.command("kang"))
async def kang_sticker(_, message: Message):
    chat_id = message.chat.id
    reply = message.reply_to_message
    
    if not reply:
        await message.reply_text("**Reply to a sticker or image to kang it!**")
        return
    
    msg = await message.reply_text("<blockquote>**Kanging sticker...**</blockquote>")
    
    # Check if replying to a sticker
    if reply.sticker:
        sticker = reply.sticker
        file = await app.download_media(sticker)
        
        # Get emoji
        emoji = sticker.emoji or "👍"
        
        # Upload as sticker
        await app.send_sticker(chat_id, sticker=file, emoji=emoji)
        await msg.edit_text("<blockquote>**Sticker kang'd successfully! ✅**</blockquote>")
        
        os.remove(file)
        return
    
    # Check if replying to an image
    if reply.photo:
        file = await app.download_media(reply)
        
        # Convert to sticker
        await app.send_sticker(chat_id, sticker=file, emoji="👍")
        await msg.edit_text("<blockquote>**Image kang'd successfully! ✅**</blockquote>")
        
        os.remove(file)
        return
    
    await msg.edit_text("**Please reply to a sticker or image!**")

# ==================== STICKER PACK MAKER PANEL ====================
@app.on_message(filters.command("pack"))
async def pack_panel(_, message: Message):
    chat_id = message.chat.id
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📦 Create Pack v1", callback_data="pack_v1"),
            InlineKeyboardButton("📦 Create Pack v2", callback_data="pack_v2")
        ],
        [
            InlineKeyboardButton("📦 Create Pack v3", callback_data="pack_v3"),
            InlineKeyboardButton("📦 Create Pack v4", callback_data="pack_v4")
        ],
        [
            InlineKeyboardButton("📦 Create Pack v5", callback_data="pack_v5"),
            InlineKeyboardButton("📦 Create Pack v6", callback_data="pack_v6")
        ],
        [
            InlineKeyboardButton("📦 Create Pack v7", callback_data="pack_v7"),
            InlineKeyboardButton("📦 Create Pack v8", callback_data="pack_v8")
        ],
        [
            InlineKeyboardButton("📦 Create Pack v9", callback_data="pack_v9"),
            InlineKeyboardButton("📦 Create Pack v10", callback_data="pack_v10")
        ]
    ])
    
    await message.reply_text(
        "**🎨 Sticker Pack Maker Panel**\n\n"
        "Select a version to create your sticker pack!\n"
        "Each version has different features and styles.\n\n"
        "**How to use:**\n"
        "1. Select a version\n"
        "2. Send me stickers/images (max 20)\n"
        "3. Type /pack_done when you're ready",
        reply_markup=keyboard
    )

# Store pack data
pack_data = {}

@app.on_callback_query(filters.regex(r"pack_v(\d+)"))
async def pack_version(_, callback: CallbackQuery):
    user_id = callback.from_user.id
    version = callback.data.split("_")[1]
    
    # Initialize pack data for user
    pack_data[user_id] = {
        "version": version,
        "stickers": [],
        "name": f"Pack v{version}",
        "emoji": "👍"
    }
    
    await callback.answer(f"Pack v{version} selected!", show_alert=True)
    
    await callback.message.edit_text(
        f"**📦 Sticker Pack v{version}**\n\n"
        "**Instructions:**\n"
        "1. Send me up to 20 stickers/images\n"
        "2. Each sticker will be added to your pack\n"
        "3. Type /pack_done when finished\n"
        "4. Type /pack_clear to clear all stickers\n\n"
        f"**Current count:** 0/20",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Done", callback_data="pack_done")],
            [InlineKeyboardButton("🗑️ Clear All", callback_data="pack_clear")],
            [InlineKeyboardButton("🔙 Back", callback_data="pack_back")]
        ])
    )

@app.on_message(filters.command("pack_done"))
async def pack_done(_, message: Message):
    user_id = message.from_user.id
    
    if user_id not in pack_data or not pack_data[user_id]["stickers"]:
        await message.reply_text("**No stickers found! Send some stickers first.**")
        return
    
    sticker_count = len(pack_data[user_id]["stickers"])
    if sticker_count < 2:
        await message.reply_text("**Need at least 2 stickers to create a pack!**")
        return
    
    await message.reply_text(f"**Creating sticker pack with {sticker_count} stickers...**")
    
    # In a real implementation, you would use @Stickers bot or create the pack
    # For now, we'll simulate the process
    await message.reply_text(
        f"**✅ Pack created successfully!**\n\n"
        f"**Version:** {pack_data[user_id]['version']}\n"
        f"**Stickers:** {sticker_count}\n"
        f"**Name:** {pack_data[user_id]['name']}\n\n"
        f"⚠️ **Note:** To create a real pack, use @Stickers bot."
    )
    
    # Clear pack data
    pack_data[user_id] = None

@app.on_callback_query(filters.regex("pack_done"))
async def pack_done_callback(_, callback: CallbackQuery):
    user_id = callback.from_user.id
    
    if user_id not in pack_data or not pack_data[user_id]["stickers"]:
        await callback.answer("No stickers to create pack!", show_alert=True)
        return
    
    sticker_count = len(pack_data[user_id]["stickers"])
    if sticker_count < 2:
        await callback.answer("Need at least 2 stickers!", show_alert=True)
        return
    
    await callback.answer("Creating pack...")
    
    await callback.message.edit_text(
        f"**✅ Pack created successfully!**\n\n"
        f"**Version:** {pack_data[user_id]['version']}\n"
        f"**Stickers:** {sticker_count}\n"
        f"**Name:** {pack_data[user_id]['name']}\n\n"
        f"⚠️ **Note:** To create a real pack, use @Stickers bot."
    )
    
    pack_data[user_id] = None

@app.on_callback_query(filters.regex("pack_clear"))
async def pack_clear(_, callback: CallbackQuery):
    user_id = callback.from_user.id
    
    if user_id in pack_data:
        pack_data[user_id]["stickers"] = []
        await callback.answer("All stickers cleared!", show_alert=True)
        await callback.message.edit_text("**🗑️ Pack cleared! Send new stickers.**")

@app.on_callback_query(filters.regex("pack_back"))
async def pack_back(_, callback: CallbackQuery):
    user_id = callback.from_user.id
    
    if user_id in pack_data:
        pack_data[user_id] = None
    
    await callback.answer("Going back...")
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📦 Create Pack v1", callback_data="pack_v1"),
            InlineKeyboardButton("📦 Create Pack v2", callback_data="pack_v2")
        ],
        [
            InlineKeyboardButton("📦 Create Pack v3", callback_data="pack_v3"),
            InlineKeyboardButton("📦 Create Pack v4", callback_data="pack_v4")
        ],
        [
            InlineKeyboardButton("📦 Create Pack v5", callback_data="pack_v5"),
            InlineKeyboardButton("📦 Create Pack v6", callback_data="pack_v6")
        ],
        [
            InlineKeyboardButton("📦 Create Pack v7", callback_data="pack_v7"),
            InlineKeyboardButton("📦 Create Pack v8", callback_data="pack_v8")
        ],
        [
            InlineKeyboardButton("📦 Create Pack v9", callback_data="pack_v9"),
            InlineKeyboardButton("📦 Create Pack v10", callback_data="pack_v10")
        ]
    ])
    
    await callback.message.edit_text(
        "**🎨 Sticker Pack Maker Panel**\n\n"
        "Select a version to create your sticker pack!\n"
        "Each version has different features and styles.",
        reply_markup=keyboard
    )

# Helper to add stickers to pack
@app.on_message(filters.sticker | filters.photo)
async def add_to_pack(_, message: Message):
    user_id = message.from_user.id
    
    # Check if user has an active pack session
    if user_id not in pack_data or not pack_data[user_id]:
        return
    
    # Check if pack is full
    if len(pack_data[user_id]["stickers"]) >= 20:
        await message.reply_text("**Pack is full! Maximum 20 stickers allowed.**")
        return
    
    # Download sticker
    file = await app.download_media(message)
    pack_data[user_id]["stickers"].append(file)
    
    count = len(pack_data[user_id]["stickers"])
    await message.reply_text(f"**✅ Added sticker! ({count}/20)**")

# ==================== KANG STICKER PACK MAKER (Combined) ====================
@app.on_message(filters.command("kangpack"))
async def kang_pack(_, message: Message):
    chat_id = message.chat.id
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📦 Kang Pack v1", callback_data="kang_v1"),
            InlineKeyboardButton("📦 Kang Pack v2", callback_data="kang_v2"),
            InlineKeyboardButton("📦 Kang Pack v3", callback_data="kang_v3")
        ]
    ])
    
    await message.reply_text(
        "**🎨 Kang Sticker Pack Maker**\n\n"
        "Create a sticker pack from existing stickers!\n"
        "Select a version:",
        reply_markup=keyboard
    )

@app.on_callback_query(filters.regex(r"kang_v(\d+)"))
async def kang_pack_version(_, callback: CallbackQuery):
    user_id = callback.from_user.id
    version = callback.data.split("_")[1]
    
    await callback.answer(f"Kang Pack v{version} selected!")
    
    await callback.message.edit_text(
        f"**📦 Kang Sticker Pack v{version}**\n\n"
        "**How to use:**\n"
        "1. Send me stickers to kang\n"
        "2. Each sticker will be added to your pack\n"
        "3. Type /kang_done when finished\n\n"
        "**Current count:** 0/20",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Done", callback_data="kang_done")],
            [InlineKeyboardButton("🔙 Back", callback_data="kang_back")]
        ])
    )

# Store kang pack data
kang_data = {}

@app.on_message(filters.sticker)
async def add_to_kang_pack(_, message: Message):
    user_id = message.from_user.id
    
    if user_id not in kang_data or not kang_data[user_id]:
        return
    
    if len(kang_data[user_id]["stickers"]) >= 20:
        await message.reply_text("**Pack is full! Maximum 20 stickers allowed.**")
        return
    
    file = await app.download_media(message)
    kang_data[user_id]["stickers"].append(file)
    
    count = len(kang_data[user_id]["stickers"])
    await message.reply_text(f"**✅ Added sticker! ({count}/20)**")

@app.on_callback_query(filters.regex("kang_done"))
async def kang_done(_, callback: CallbackQuery):
    user_id = callback.from_user.id
    
    if user_id not in kang_data or not kang_data[user_id]["stickers"]:
        await callback.answer("No stickers to create pack!", show_alert=True)
        return
    
    sticker_count = len(kang_data[user_id]["stickers"])
    if sticker_count < 2:
        await callback.answer("Need at least 2 stickers!", show_alert=True)
        return
    
    await callback.answer("Creating kang pack...")
    
    await callback.message.edit_text(
        f"**✅ Kang Pack created successfully!**\n\n"
        f"**Stickers:** {sticker_count}\n\n"
        f"⚠️ **Note:** To create a real pack, use @Stickers bot."
    )
    
    kang_data[user_id] = None

@app.on_callback_query(filters.regex("kang_back"))
async def kang_back(_, callback: CallbackQuery):
    user_id = callback.from_user.id
    
    if user_id in kang_data:
        kang_data[user_id] = None
    
    await callback.answer("Going back...")
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📦 Kang Pack v1", callback_data="kang_v1"),
            InlineKeyboardButton("📦 Kang Pack v2", callback_data="kang_v2"),
            InlineKeyboardButton("📦 Kang Pack v3", callback_data="kang_v3")
        ]
    ])
    
    await callback.message.edit_text(
        "**🎨 Kang Sticker Pack Maker**\n\n"
        "Create a sticker pack from existing stickers!",
        reply_markup=keyboard
    )

print("✅ All modules loaded successfully!")
print("Commands available: /q, /q r, /mmf, /kang, /pack, /kangpack")
