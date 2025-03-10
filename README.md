# **Solara RAT - Created by xsolara**

## **Disclaimer**
This project is strictly for **learning, research, and ethical security development**.
I strongly believe in **understanding technology to improve security, not to harm it**.
Solara RAT is **NOT meant for malicious use**. It is a tool for **educational purposes only**.

> **If you use this software for any illegal activities, you alone are responsible.**
> I do not take any responsibility for misuse. Be ethical, respect privacy, and always follow the law.
> By using this tool, you agree to act ethically and in accordance with all applicable laws.
> I will not be held accountable in court or otherwise, especially in the UK.

### **Knowledge should be used to build, not destroy.**

[Join the Discord](https://discord.gg/HThCETu2pv)

**Please leave a star on the repo and join up to the discord! Premium version releasing soon possibly, for advanced pen-testing!**

---

## **Features**

- Remote administration for **research and testing** purposes
- Uses **Discord** as a **C2 (command and control) system**
- Customizable settings via **config.py**
- **Lightweight** and **modular**

---

## **Installation**

### **Requirements**

- **Python 3.10.2 (Recommended)**
- Dependencies listed in **requirements.txt**

### **Setup Instructions**

#### **Clone the Repository**
```sh
git clone https://github.com/iciidev/solara-rat/solara-rat.git
cd solara-rat
```

#### **Install Dependencies**
```sh
pip install -r requirements.txt
```

#### **Configure the Tool**
Open **config.py** in any text editor and modify the settings as needed (**bot token & owner ID**).

#### **Run the Application**
```sh
python main.py
```

---

## **Commands List**

### **System Control**
- `!shell (cmd, run)` - Execute system command
- `!processes (ps)` - List running processes
- `!kill` - Terminate process
- `!blacklist` - Add process to blacklist
- `!whitelist` - Remove from blacklist
- `!blacklist-status` - View blacklist
- `!persist` - Enable persistence
- `!startup` - Add to startup
- `!status` - System resource usage
- `!info (system)` - System information
- `!services` - Manage Windows services
- `!windows` - Control windows
- `!block-input` - Block keyboard/mouse
- `!unblock-input` - Restore input
- `!timetraveler` - Manipulate system clock
- `!shutdown` - Shutdown system
- `!reboot` - Restart system
- `!logoff` - Log off user
- `!cancel` - Cancel shutdown/reboot
- `!destroy` - Remove all traces
- `!rootkit` - Install advanced persistence

### **File Operations**
- `!files (dir, ls)` - List directory contents
- `!browse` - File browser interface
- `!cd` - Change directory
- `!download (dl)` - Download target file
- `!install` - Download from URL
- `!wallpaper` - Set system wallpaper

### **Monitoring**
- `!screenshot (screen, sc)` - Take screenshot
- `!screenrec (record, rec)` - Record screen
- `!webcam` - Take webcam photo
- `!keylog (kl)` - Keyboard monitoring
- `!info` - System information
- `!locate` - Get geolocation
- `!network` - Network information
- `!status` - Resource usage
- `!ip` - IP address information
- `!advancedinfo (fullinfo, sysinfo)` - Comprehensive system info
- `!getdiscordinfo` - Get Discord info
- `!browserstuff` - Extract browser data
- `!getwifipass` - Get WiFi passwords
- `!passwords` - Get browser passwords
- `!minecraft` - Get Minecraft data
- `!roblox` - Get Roblox cookies

### **Visual Effects & Pranks**
- `!notepad` - Open notepad with text
- `!website` - Open website in browser
- `!snake` - Animate desktop icons
- `!tts` - Text-to-speech
- `!message` - Show message box
- `!say` - Advanced TTS voices
- `!volume` - Set system volume
- `!brightness` - Screen brightness
- `!rickroll` - Browser rickroll
- `!jumpscare` - Scare effect
- `!meltscreen` - Melting effect
- `!chaos` - Total chaos mode
- `!matrix` - Matrix rain effect
- `!invert` - Invert colors
- `!flash` - Flash screen
- `!glitch` - Glitch effect
- `!bonk` - Mouse dodge
- `!earthquake` - Screen shake
- `!drunk` - Drunk effect
- `!disco` - Disco party
- `!gravity` - Screen gravity
- `!dodge` - Dodging popup
- `!funmode` - Fun effects

### **Utilities**
- `!mouse` - Control mouse
- `!clipboard` - Clipboard access
- `!type` - Remote typing
- `!help` - Show this help
- `!detailedhelp (dhelp)` - Detailed command guide
- `!help_timetraveler` - Help for time traveler command

---

## **Legal Notice**

This software is provided **only for educational and research purposes**.
Misuse of this tool for **unethical or illegal activities** is **strictly prohibited**.
> The author will **not be responsible** for any misuse.
> Always get **proper authorization** before testing security systems.

---

## **Contribution**
Pull requests are welcome, but must align with **ethical security research**.
> Any discussions or contributions promoting unethical use will be **ignored and reported**.

---

## **License**
This project is released under an **open-source license**, only for **ethical purposes**.
Check the **LICENSE** file for details.

---

### **Author:** xsolara
### **Purpose:** Ethical security research and education

