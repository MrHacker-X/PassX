<h1 align="center">⃤ P A S S X ⃤</h1>

<p align="center">
  <strong>Strong local password generator  Termux &amp; Linux</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-2.0-blue?style=flat-square">
  <img src="https://img.shields.io/badge/python-3.8%2B-informational?style=flat-square">
  <img src="https://img.shields.io/badge/CSPRNG-secrets-success?style=flat-square">
  <img src="https://img.shields.io/badge/platform-Termux%20%7C%20Linux-lightgrey?style=flat-square">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square">
</p>

---

> 🎯 **Why PassX?** Because weak passwords are the #1 cause of account takeovers.
> PassX generates long, high-entropy passwords **on your device** with a real
> cryptographic generator (`secrets`)  nothing is uploaded, logged, or synced.

🧭 **Tool Purpose**  generate strong random passwords, passphrases and PINs locally,
with entropy feedback, clipboard copy and optional file export.

---

## 📋 Table of contents

- [✨ Features](#-features)
- [🚀 Quick start](#-quick-start)
- [📦 Installation](#-installation)
- [🧨 CLI usage](#-cli-usage)
- [🖥️ Preview](#️-preview)
- [🔐 Security notes](#-security-notes)
- [🖥️ Interactive menu](#️-interactive-menu)
- [🩺 Doctor](#-doctor)
- [⚠️ Disclaimer](#️-disclaimer)
- [📜 License](#-license)

---

## ✨ Features

| Feature | v1.0 | v2.0 |
|---|---|---|
| Random passwords | ✅ (insecure `random`) | ✅ **`secrets` CSPRNG** |
| Passphrases | ❌ | ✅ 1029-word wordlist |
| PIN mode | ❌ | ✅ 4–24 digits |
| Entropy meter | ❌ | ✅ live bits + label |
| Strength feedback | ❌ | ✅ per password |
| Custom charsets | ❌ | ✅ per-set toggles |
| Look-alike exclusion (Il1O0) | ❌ | ✅ `--no-ambiguous` |
| Clipboard copy | ❌ | ✅ termux/wl-copy/xclip/pbcopy |
| Save to file | ❌ | ✅ `chmod 600` |
| One-shot CLI | ❌ | ✅ `-m -l -c …` |
| Self-check | ❌ | ✅ `--doctor` |
| Ctrl+C handling | basic | ✅ clean safe-exit |

**Modes at a glance**

| Mode | What you get | Typical use |
|---|---|---|
| `random` | letters + digits + symbols | most accounts |
| `phrase` | memorable words + number | phones, master passwords |
| `pin` | numeric only | SIM, devices, gates |

---

## 🚀 Quick start

```bash
git clone https://github.com/MrHacker-X/PassX.git
cd PassX
python3 passx.py
```

That's it  the interactive menu walks you through mode, length and count.

---

## 📦 Installation

| System | Supported |
|---|---|
| Termux (Android) | ✅ |
| Linux (any distro) | ✅ |
| macOS | ✅ (unofficial) |
| Windows / WSL | ✅ (unofficial) |

**Requirements:** Python 3.8+  no pip packages needed.

```bash
apt-get update -y && apt-get upgrade -y
apt-get install git python -y
git clone https://github.com/MrHacker-X/PassX.git
cd PassX
```

**Single-line:**

```bash
apt-get update -y;apt-get upgrade -y;apt install git python -y;git clone https://github.com/MrHacker-X/PassX.git;cd PassX;python3 passx.py
```

---

## 🧨 CLI usage

```bash
# 5 passwords, 24 chars, with entropy meter
python3 passx.py -m random -l 24 -c 5 --strength

# 6-word passphrase
python3 passx.py -m phrase -w 6

# 8-digit PIN
python3 passx.py -m pin -l 8

# letters only (no symbols), avoid look-alike chars
python3 passx.py --only-alpha --no-ambiguous -l 32

# copy the first result to clipboard
python3 passx.py -m random -l 20 --copy

# save results to a chmod-600 file
python3 passx.py -l 24 -c 3 --save
```

| Flag | Meaning |
|---|---|
| `-m` | `random` / `phrase` / `pin` |
| `-l` | length (random, pin) |
| `-w` | words per phrase |
| `-c` | how many passwords |
| `--no-symbols` | letters + digits only |
| `--only-alpha` | letters only |
| `--no-ambiguous` | drop `Il1O0` look-alikes |
| `--strength` | entropy meter |
| `--copy` | clipboard the first password |
| `--save` | write a `passx-*.txt` (600) |
| `--doctor` | environment self-check |

---

## 🖥️ Preview

<div align="center">
<img src="https://i.ibb.co/s92hz3Lb/image.png" alt="PassX main menu" width="760">
</div>

---

## 🔐 Security notes

- **Generator:** Python [`secrets`](https://docs.python.org/3/library/secrets.html) 
  the OS entropy pool, not a PRNG. On Python < 3.6 the tool warns loudly.
- **Entropy math:** `log2(charset) × length`  a 20-char random password here is
  ~129 bits; a 5-word passphrase ~50 bits (still far beyond offline cracking).
- **Network:** none. The tool never opens a socket.
- **Storage:** only if you pass `--save` / accept the save prompt  and the file
  is created `chmod 600` with a reminder to delete it after use.

---

## 🖥️ Interactive menu

| Option | What it does |
|---|---|
| `[1] Generate` | pick a mode → length → count, results with meters |
| `[2] About` | security notes and usage guidance |
| `[0] Exit` | clean exit (Ctrl+C exits safely too) |

---

## 🩺 Doctor

```bash
python3 passx.py --doctor
```

Checks Python version, CSPRNG availability, wordlist integrity, entropy math
and clipboard helper  prints an OK/FAIL table.

---

## ⚠️ Disclaimer

This tool is provided for **educational and personal security use**.
The authors are not responsible for misuse or for any password you lose.
You are responsible for backing up your credentials safely.

---

## 📜 License

Released under the MIT License  see [LICENSE](LICENSE).
