# Video Clip Creator

This application creates video clips from a source video file based on timecodes specified in a CSV file.

## Requirements

- Python 3.8 or higher
- Required Python packages (install using `pip install -r requirements.txt`):
  - moviepy
  - pandas
  - tqdm
  - tkinter (usually comes with Python)

## CSV File Format

The CSV file should have the following columns:
- `Start`: Start timecode in format HH:MM:SS or HH:MM:SS.mmm
- `End`: End timecode in format HH:MM:SS or HH:MM:SS.mmm
- `OutputName` (optional): Name for the output clip (if not provided, will be auto-generated)

Example CSV format:
```
Start,End,OutputName
00:00:10,00:00:20,clip1
00:01:30,00:02:00,clip2
```

## Usage

### GUI Version

1. Run the GUI application:
   ```
   python video_clip_creator_gui.py
   ```
2. Use the "Browse" buttons to select:
   - Input video file
   - CSV file with timecodes
   - Output directory
3. The CSV preview will show the timecodes that will be processed
4. Click "Create Clips" to start processing

### Command Line Version

1. Place your source video file in the same directory as the script
2. Create a CSV file with the timecodes
3. Run the script:
   ```
   python video_clip_creator.py --video your_video.mp4 --csv your_timecodes.csv --output clips_folder
   ```

## Output

The script will create individual video clips in the specified output folder, named according to the CSV file or auto-generated names if not specified. 