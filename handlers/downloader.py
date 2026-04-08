import os
import asyncio
import re
import time
import yt_dlp
from aiogram import Router, types
from aiogram.filters import Command

router = Router()

# 1. Helper: Visual Progress Bar
def get_prog_bar(percent):
    done = int(percent / 10)
    return "█" * done + "░" * (10 - done)

@router.message(Command("dl"))
async def god_downloader(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.answer("❌ <b>Link missing!</b>\nUsage: <code>/dl [Link/Magnet]</code>", parse_mode="HTML")
    
    link = args[1]
    status_msg = await message.answer("🛰️ <b>Analyzing link...</b>", parse_mode="HTML")
    last_edit_time = 0
    filename = ""

    # 2. Progress Updater Function
    async def update_status(percent, speed, eta):
        nonlocal last_edit_time
        curr_time = time.time()
        if curr_time - last_edit_time < 2.5: # Telegram limit check
            return
        
        bar = get_prog_bar(percent)
        text = (f"📥 <b>Downloading...</b>\n\n"
                f"<code>[{bar}] {percent}%</code>\n"
                f"🚀 Speed: <b>{speed}</b>\n"
                f"⏳ ETA: <b>{eta}</b>")
        try:
            await status_msg.edit_text(text, parse_mode="HTML")
            last_edit_time = curr_time
        except: pass

    # --- PHASE 1: DOWNLOAD ---
    try:
        # A. MAGNETS & DIRECT LINKS (aria2c)
        if link.startswith("magnet:") or any(x in link.lower() for x in [".mkv", ".mp4", ".zip", ".pdf", ".rar"]):
            await status_msg.edit_text("🧲 <b>Aria2 Engine:</b> Starting...")
            cmd = ["aria2c", "--allow-overwrite=true", "--summary-interval=1", link]
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
            )

            while True:
                line = await process.stdout.readline()
                if not line: break
                line_str = line.decode().strip()
                match = re.search(r'\((\d+)%\).*SPD:([\w./]+).*ETA:([\w]+)', line_str)
                if match:
                    pc, spd, et = match.groups()
                    await update_status(int(pc), spd, et)
            await process.wait()

        # B. SOCIAL MEDIA (yt-dlp)
        else:
            await status_msg.edit_text("🎬 <b>yt-dlp Engine:</b> Extracting...")
            def yt_hook(d):
                if d['status'] == 'downloading':
                    p = d.get('_percent_str', '0%').replace('%','').strip()
                    spd = d.get('_speed_str', 'N/A')
                    et = d.get('_eta_str', 'N/A')
                    asyncio.get_event_loop().create_task(update_status(float(p), spd, et))

            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'outtmpl': f'dl_{message.from_user.id}_%(id)s.%(ext)s',
                'progress_hooks': [yt_hook],
                'quiet': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                loop = asyncio.get_event_loop()
                info = await loop.run_in_executor(None, lambda: ydl.extract_info(link, download=True))
                filename = ydl.prepare_filename(info)

        # --- PHASE 2: FILE DETECTION ---
        # Agar filename yt-dlp se nahi mila (Aria2 case), toh folder scan karo
        if not filename or not os.path.exists(filename):
            files = [f for f in os.listdir('.') if not f.startswith(('temp', 'main', 'config', 'Dockerfile')) and os.path.isfile(f) and f.endswith(('.mp4', '.mkv', '.zip', '.pdf', '.rar', '.mp3'))]
            if not files:
                return await status_msg.edit_text("❌ <b>Error:</b> File download failed or not found.")
            filename = files[0]

        size_mb = os.path.getsize(filename) / (1024 * 1024)

        # --- PHASE 3: UPLOAD / SPLIT ---
        if size_mb <= 49:
            await status_msg.edit_text("📤 <b>Uploading...</b>")
            await message.answer_document(types.FSInputFile(filename), caption=f"✨ <b>Downloaded!</b>\n🎬 {filename}\n👤 @AkMovieVerse")
        else:
            await status_msg.edit_text(f"✂️ <b>Large File ({size_mb:.1f}MB). Splitting into 49MB parts...</b>")
            
            # Numeric suffixes for easy joining (part.01, part.02)
            prefix = f"{filename}.part"
            split_cmd = ["split", "-b", "49M", "--numeric-suffixes=1", filename, prefix]
            
            proc_split = await asyncio.create_subprocess_exec(*split_cmd)
            await proc_split.wait()

            parts = sorted([f for f in os.listdir('.') if f.startswith(prefix)])
            await status_msg.edit_text(f"📦 <b>Sending {len(parts)} parts...</b>")

            for i, part in enumerate(parts):
                await message.answer_document(
                    types.FSInputFile(part), 
                    caption=f"📦 Part {i+1} of {len(parts)}\n🎬 {filename}\n👤 @AkMovieVerse"
                )
                os.remove(part)
                await asyncio.sleep(1.5) # Flood protection

        # Final Cleanup
        if os.path.exists(filename):
            os.remove(filename)
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ <b>Error:</b> {str(e)[:150]}")
        # Cleanup on failure
        if filename and os.path.exists(filename):
            os.remove(filename)