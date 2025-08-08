\# Couses Player



\### A day project :  

Desktop video player application built with Python and Tkinter, specifically designed for managing and playing educational video courses that are already downloaded off the grid.



\- Why not use \*\*VLC\*\* , it does not track my progress and I should always open the playlist ......  



\## Features



\- \*\*Course Management\*\*: Hierarchical course organization with provider/course/video structure

\- \*\*Progress Tracking\*\*: Automatically saves and resumes video progress

\- \*\*Playback Controls\*\*: Speed adjustment, volume control, seeking, and more

\- \*\*Fullscreen Support\*\*: Toggle fullscreen mode and hide/show tree view

\- \*\*Dark Theme\*\*: Dark UI theme for comfortable viewing

\- \*\*Keyboard Shortcuts\*\*: Keyboard controls for efficient navigation

\- \*\*Database Persistence\*\*: SQLite database for storing progress and course information



\## Prerequisites



\### Required Software

\- \*\*Python 3.7+\*\*

\- \*\*VLC Media Player\*\* - Must be installed on your system

&nbsp; - Windows: Download from \[VLC](https://www.videolan.org/vlc/)

&nbsp; - macOS: `brew install --cask vlc`

&nbsp; - Linux: `sudo apt-get install vlc` (Ubuntu/Debian)



\### Required Python Packages

The application will automatically install missing packages, but you can install them manually:



```bash

pip install python-vlc natsort

```



\*\*Built-in packages that this app uses\*\* (included with Python):

\- `tkinter`

\- `sqlite3`

\- `json`

\- `os`

\- `subprocess`

\- `sys`

\- `time`

\- `threading`

\- `ctypes`



\## Installation



1\. \*\*Clone or download\*\* the application files

2\. \*\*Install VLC Media Player\*\* on your system

3\. \*\*Configure the application\*\* by editing `config.json` (created automatically on first run if not found but if cloned you'll find mock config)

4\. \*\*Run the application\*\*:   

&nbsp;  ### Option 1: Using Batch File (Windows)

&nbsp;  ```cmd

&nbsp;  courses\_player.bat

&nbsp;  ```

&nbsp;  You can use this like a normal application it will run with \*\*pythonw\*\*

&nbsp;  You can also make a shortcut to your desktop and use it



&nbsp;  ### Option 2: Direct Python Execution

&nbsp;  ```bash

&nbsp;  python courses\_player.py

&nbsp;  ```



\## Configuration



The application uses a `config.json` file for configuration:



```json

{

&nbsp;   "db\_file": "default.db",

&nbsp;   "root\_dir": "D:\\\\COURSES",

&nbsp;   "scanned": true,

&nbsp;   "playback\_speed": 1,

&nbsp;   "selected\_item": null

}

```



\### Configuration Options

\- \*\*`db\_file`\*\*: SQLite database file path

\- \*\*`root\_dir`\*\*: Root directory containing your course folders

\- \*\*`scanned`\*\*: Whether courses have been scanned (\*auto-managed\*)

\- \*\*`playback\_speed`\*\*: Default playback speed

\- \*\*`selected\_item`\*\*: Last selected video (\*auto-managed\*) 



\## Course Directory Structure



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

&nbsp;   └── Web Development/

&nbsp;       ├── HTML Basics/

&nbsp;       │   ├── 01-Introduction.mp4

&nbsp;       │   └── 02-Tags.mp4

&nbsp;       └── CSS Fundamentals/

&nbsp;           ├── 01-Selectors.mp4

&nbsp;           └── 02-Properties.mp4

```



\### Supported Video Formats

\- `.mp4`

\- `.mkv` 

\- `.avi`

\- `.mov`



\## Database Schema



The application uses SQLite with two main tables:



\### `course\_progress` Table

```sql

CREATE TABLE course\_progress (

&nbsp;   course\_id INTEGER PRIMARY KEY AUTOINCREMENT,

&nbsp;   course\_name TEXT UNIQUE,

&nbsp;   total\_length INTEGER,

&nbsp;   total\_progress INTEGER

);

```



\### `video\_progress` Table

```sql

CREATE TABLE video\_progress (

&nbsp;   course\_id INTEGER,

&nbsp;   video\_path TEXT PRIMARY KEY,

&nbsp;   video\_length INTEGER,

&nbsp;   progress INTEGER,

&nbsp;   FOREIGN KEY (course\_id) REFERENCES course\_progress (course\_id)

);

```



\## Keyboard Shortcuts



\### Playback Controls

\- \*\*Space\*\*: Play/Pause

\- \*\*X\*\*: Stop video

\- \*\*F\*\*: Next video

\- \*\*Q\*\*: Previous video

\- \*\*Left Arrow\*\*: Skip backward (10 seconds)

\- \*\*Right Arrow\*\*: Skip forward (10 seconds)



\### Speed Controls

\- \*\*D\*\*: Increase playback speed (+0.1x)

\- \*\*S\*\*: Decrease playback speed (-0.1x)



\### Volume Controls

\- \*\*Up Arrow\*\*: Increase volume (+10%)

\- \*\*Down Arrow\*\*: Decrease volume (-10%)



\### Display Controls

\- \*\*F11\*\*: Toggle fullscreen

\- \*\*H\*\*: Hide/Show tree view (\*This makes it fullscreen when you are spliting the workspace\*)

\- \*\*Escape\*\*: Exit fullscreen



\## Usage



1\. \*\*First Run\*\*: Configure your courses directory in the generated `config.json`

2\. \*\*Scan Courses\*\*: Right-click in the tree view to rescan your course folder

3\. \*\*Play Videos\*\*: Double-click any video to start playing

4\. \*\*Resume Progress\*\*: Videos automatically resume from where you left off

5\. \*\*Navigate\*\*: Use keyboard shortcuts or tree view to navigate between videos





\#



\## License



This project is provided as-is for educational and personal use.I'm not a Pthon developper thisis just a tool I made to help me watch courses when I'm off the grid 



\## Contributing



Feel free to submit issues, suggestions, or improvements to enhance the video player's functionality.

