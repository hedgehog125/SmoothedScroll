# <img src='./assets/icon.png' alt='🖱️' width='30' height='30'/> Smoothed Scroll

**Smoothed Scroll** is an open-source program written in Python that brings smooth scrolling to all Windows applications. It serves as a free alternative to the proprietary SmoothScroll Windows. With **Smoothed Scroll**, you can enjoy smooth scrolling with complete control over the settings, automatic startup, and smart game detection that disables smooth scrolling when you launch Steam games. You can also add custom exclusions for specific applications.

## 📝 Features

- 🖱️ **Smooth scrolling** for all Windows applications.
- ⚙️ **Full customization** of scroll behavior.
- 🚀 **Auto-start** with Windows.
- 🎮 **Auto-disable for Steam games** and customizable exclusions for other apps.
- 🔧 **Open-source** and free to use under the GNU General Public License.

## 🚀 Installation

### 📥 Download from GitHub Releases

1. Head over to the [GitHub Releases](https://github.com/zachey01/SmoothedScroll/releases) page.
2. Download the latest version of Smoothed Scroll as an executable.
3. Run the executable and follow the installation prompts.

### 🔧 Building from Source

If you'd like to build **Smoothed Scroll** from source, follow these steps:

#### Prerequisites:

- Python 3.x installed.
- `git` installed.

#### Clone the Repository

```bash
git clone https://github.com/zachey01/SmoothedScroll.git
cd SmoothedScroll
```

#### Install Dependencies

You can install all required dependencies via `pip`:

```bash
pip install -r requirements.txt
```

#### Build the Executable with Nuitka

After installing the dependencies, use **Nuitka** to build the standalone executable:

```bash
nuitka --onefile main.py --enable-plugin=tk-inter --jobs=4 --static-libpython=no --remove-output --standalone --windows-disable-console --windows-icon-from-ico=./assets/icon.ico --output-filename=SmoothedScroll
```

This command will create a standalone executable for Windows.

## 📜 License

Smoothed Scroll is licensed under the **GNU General Public License**. For more information, see the `LICENSE` file in the repository.

## 🤝 Contributions

Contributions are welcome! Feel free to open issues, submit pull requests, or suggest features.

---

Enjoy smoother scrolling on Windows! 🌟
