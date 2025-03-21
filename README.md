# 📱 Persistent Python Service on Android via Termux

This guide explains how to run a persistent Python script (e.g., an SMS responder, trading notifier, etc.) on your Android device using [Termux](https://f-droid.org/packages/com.termux/) with `termux-services`.

---

## ✅ Features

- Runs your Python script as a background service
- Automatically restarts on crash (supervised)
- Can be kept alive even when the screen is off
- Optionally runs at boot (with automation app)

---

## 🚀 Requirements

1. **Termux** (latest from [F-Droid](https://f-droid.org/packages/com.termux/))
2. **Termux:API** ([F-Droid](https://f-droid.org/packages/com.termux.api/))
3. Python script ready to run (e.g., `sms_notifier.py`)

Install required packages:

    pkg update
    pkg install python termux-services termux-api openssh

---

## 📂 Folder Structure

Your service must live inside:

    ~/.termux/services/<service-name>/run

For example, to run `~/scripts/sms_notifier.py` as a service named `sms`:

---

## 📦 Setup

### 1. Create the service folder and run script

    mkdir -p ~/.termux/services/sms
    nano ~/.termux/services/sms/run

Paste the following:

    #!/data/data/com.termux/files/usr/bin/sh
    termux-wake-lock
    python ~/scripts/sms_notifier.py

> 🔁 `termux-wake-lock` keeps the script alive even with the screen off.

Make it executable:

    chmod +x ~/.termux/services/sms/run

---

### 2. Enable and start the service

    sv-enable sms
    sv up sms

Check status:

    sv status sms

View logs (if redirected):

    tail -f ~/.termux/services/sms/log.txt

---

### 🛡 Keep Termux Alive in Background

To prevent Android from killing Termux:

- Go to **Settings** → **Battery** → find **Termux**
- Set battery optimization to: **Unrestricted / Not optimized**
- On some devices, "Lock" Termux in recent apps

---

### ⚡ Optional: Auto-start on Boot

Use an automation app like:

- [Tasker](https://play.google.com/store/apps/details?id=net.dinglisch.android.taskerm)
- [MacroDroid](https://play.google.com/store/apps/details?id=com.arlosoft.macrodroid)

Set it to run this shell command on boot:

    am startservice com.termux/.app.TermuxService

This will reopen Termux and resume your background services.

---

## 🔐 SSH Access (Optional)

You can enable SSH to remotely access your Termux shell:

    pkg install openssh
    sshd

Find your phone's IP:

    ip a

Then SSH in from your computer:

    ssh -p 8022 u0_aXXX@192.168.x.x

Public key login is supported — disable password auth by editing `~/.ssh/config`.

---

## 📚 Credits

Built using:

- [Termux](https://github.com/termux)
- [termux-services](https://github.com/termux/termux-services)
- [termux-api](https://github.com/termux/termux-api)

---

## 🐛 Troubleshooting

If `sv-enable` fails with "unable to change to service directory":

- Double-check your `run` script is in `~/.termux/services/sms/run`
- Make sure it's executable (`chmod +x`)
- Try removing old symlinks: `rm ~/.termux/sv/sms` and re-run `sv-enable sms`

---

## 🛠 Example Service Repo

Feel free to fork this repo and place your script at `~/scripts/sms_notifier.py`. Add config or logging as needed!
