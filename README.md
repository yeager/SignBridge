# SignBridge

Realtids-teckenspråkstolkning via kamera. Filmar TAKK/TSS-tecken och visar resultatet som text.

*Real-time sign language interpretation via camera. Captures TAKK/TSS signs and displays the result as text.*

## Features

- Live camera feed with hand landmark visualization
- Hand gesture recognition using MediaPipe
- Maps gestures to Swedish TAKK/TSS signs
- Sign history with text output
- Accessible UI built with GTK4/Adwaita
- Swedish and English localization (gettext)
- ARASAAC-compatible design principles

## Supported Signs

| Gesture | Swedish Sign | Meaning |
|---------|-------------|---------|
| Open hand | Hej | Hello |
| Fist | Stopp | Stop |
| Thumb up | Bra | Good |
| Peace sign | Tack | Thanks |
| Pointing | Du | You |
| Three fingers | Jag | I/Me |
| Four fingers | Vi | We |
| Pinch | Liten | Small |

## Installation

### Requirements

- Python 3.10+
- GTK4 and libadwaita
- A webcam

### System dependencies (Debian/Ubuntu)

```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1
```

### System dependencies (Fedora)

```bash
sudo dnf install python3-gobject gtk4 libadwaita
```

### System dependencies (macOS)

```bash
brew install gtk4 libadwaita pygobject3
```

### Python dependencies

```bash
pip install -r requirements.txt
```

### Install the application

```bash
pip install .
```

## Usage

### Run directly

```bash
python -m signbridge.main
```

### Run after install

```bash
signbridge
```

## Building translations

Compile the Swedish translation:

```bash
mkdir -p po/locale/sv/LC_MESSAGES
msgfmt po/sv.po -o po/locale/sv/LC_MESSAGES/signbridge.mo
```

## Development

```bash
git clone https://github.com/yeager/SignBridge.git
cd SignBridge
pip install -e .
python -m signbridge.main
```

## License

GPL-3.0
