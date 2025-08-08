# Couses Player

### A day project :  
Desktop video player application built with Python and Tkinter, specifically designed for managing and playing educational video courses that are already downloaded off the grid.

- Why not use **VLC** , it does not track my progress and I should always open the playlist ......  

## Features

- **Course Management**: Hierarchical course organization with provider/course/video structure
- **Progress Tracking**: Automatically saves and resumes video progress
- **Playback Controls**: Speed adjustment, volume control, seeking, and more
- **Fullscreen Support**: Toggle fullscreen mode and hide/show tree view
- **Dark Theme**: Dark UI theme for comfortable viewing
- **Keyboard Shortcuts**: Keyboard controls for efficient navigation
- **Database Persistence**: SQLite database for storing progress and course information

## Prerequisites

### Required Software
- **Python 3.7+**
- **VLC Media Player** - Must be installed on your system
  - Windows: Download from [VLC](https://www.videolan.org/vlc/)
  - macOS: `brew install --cask vlc`
  - Linux: `sudo apt-get install vlc` (Ubuntu/Debian)

### Required Python Packages
The application will automatically install missing packages, but you can install them manually:

```bash
pip install python-vlc natsort
```

**Built-in packages that this app uses** (included with Python):
- `tkinter`
- `sqlite3`
- `json`
- `os`
- `subprocess`
- `sys`
- `time`
- `threading`
- `ctypes`

## Installation

1. **Clone or download** the application files
2. **Install VLC Media Player** on your system
3. **Configure the application** by editing `config.json` (created automatically on first run if not found but if cloned you'll find mock config)
4. **Run the application**:   
   ### Option 1: Using Batch File (Windows)
   ```cmd
   courses_player.bat
   ```
   You can use this like a normal application it will run with **pythonw**
   You can also make a shortcut to your desktop and use it

   ### Option 2: Direct Python Execution
   ```bash
   python courses_player.py
   ```

## Configuration

The application uses a `config.json` file for configuration:

```json
{
    "db_file": "default.db",
    "root_dir": "D:\\COURSES",
    "scanned": true,
    "playback_speed": 1,
    "selected_item": null
}
```

### Configuration Options
- **`db_file`**: SQLite database file path
- **`root_dir`**: Root directory containing your course folders
- **`scanned`**: Whether courses have been scanned (*auto-managed*)
- **`playback_speed`**: Default playback speed
- **`selected_item`**: Last selected video (*auto-managed*) 

## Course Directory Structure

The application expects a specific directory structure for optimal organization:

```
COURSES/
├── AAA/
│   ├── Course1/
│   │   ├── 01-Introduction.mp4
│   │   ├── 02-Getting Started.mp4
│   │   ├── Module1/
│   │   │   ├── 01-Basics.mp4
│   │   │   └── 02-Advanced.mp4
│   │   └── 03-Conclusion.mp4
│   └── Course2/
│       ├── Lesson1.mp4
│       └── Lesson2.mp4
├── BBB/
│   └── Python Masterclass/
│       ├── Section1/
│       │   ├── 01-Variables.mp4
│       │   └── 02-Functions.mp4
│       └── Section2/
│           ├── 01-Classes.mp4
│           └── 02-Modules.mp4
└── XXX/
    └── Web Development/
        ├── HTML Basics/
        │   ├── 01-Introduction.mp4
        │   └── 02-Tags.mp4
        └── CSS Fundamentals/
            ├── 01-Selectors.mp4
            └── 02-Properties.mp4
```

### Supported Video Formats
- `.mp4`
- `.mkv` 
- `.avi`
- `.mov`

## Database Schema

The application uses SQLite with two main tables:

### `course_progress` Table
```sql
CREATE TABLE course_progress (
    course_id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_name TEXT UNIQUE,
    total_length INTEGER,
    total_progress INTEGER
);
```

### `video_progress` Table
```sql
CREATE TABLE video_progress (
    course_id INTEGER,
    video_path TEXT PRIMARY KEY,
    video_length INTEGER,
    progress INTEGER,
    FOREIGN KEY (course_id) REFERENCES course_progress (course_id)
);
```

## Keyboard Shortcuts

### Playback Controls
- **Space**: Play/Pause
- **X**: Stop video
- **F**: Next video
- **Q**: Previous video
- **Left Arrow**: Skip backward (10 seconds)
- **Right Arrow**: Skip forward (10 seconds)

### Speed Controls
- **D**: Increase playback speed (+0.1x)
- **S**: Decrease playback speed (-0.1x)

### Volume Controls
- **Up Arrow**: Increase volume (+10%)
- **Down Arrow**: Decrease volume (-10%)

### Display Controls
- **F11**: Toggle fullscreen
- **H**: Hide/Show tree view (*This makes it fullscreen when you are spliting the workspace*)
- **Escape**: Exit fullscreen

## Usage

1. **First Run**: Configure your courses directory in the generated `config.json`
2. **Scan Courses**: Right-click in the tree view to rescan your course folder
3. **Play Videos**: Double-click any video to start playing
4. **Resume Progress**: Videos automatically resume from where you left off
5. **Navigate**: Use keyboard shortcuts or tree view to navigate between videos


#

## License

This project is provided as-is for educational and personal use.I'm not a Pthon developper thisis just a tool I made to help me watch courses when I'm off the grid 

## Contributing

Feel free to submit issues, suggestions, or improvements to enhance the video player's functionality.
