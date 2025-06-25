#!/usr/bin/env python3

import argparse
import os
import pandas as pd
from moviepy.editor import VideoFileClip
from tqdm import tqdm
import re
from datetime import datetime

def parse_timecode(timecode):
    """Convert timecode string to seconds."""
    # Handle both HH:MM:SS.mmm and MM:SS.mmm formats
    pattern = r'(?:(\d{2}):)?(\d{2}):(\d{2})(?:\.(\d{3}))?'
    match = re.match(pattern, timecode)
    if not match:
        raise ValueError(f"Invalid timecode format: {timecode}")
    
    hours, minutes, seconds, milliseconds = match.groups()
    total_seconds = int(minutes) * 60 + int(seconds)
    if hours:
        total_seconds += int(hours) * 3600
    if milliseconds:
        total_seconds += int(milliseconds) / 1000
    return total_seconds

def create_clips(video_path, csv_path, output_dir):
    """Create video clips based on timecodes in CSV file."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Read CSV file
    df = pd.read_csv(csv_path)
    
    # Normalize column names to title case
    df.columns = [col.title() for col in df.columns]
    
    # Validate CSV columns
    required_columns = ['Start', 'End']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"CSV must contain columns: {', '.join(required_columns)}")
    
    # Load video file
    print(f"Loading video file: {video_path}")
    video = VideoFileClip(video_path)
    
    # Process each clip
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Creating clips"):
        try:
            # Parse timecodes
            start_time = parse_timecode(row['Start'])
            end_time = parse_timecode(row['End'])
            
            # Validate timecodes
            if start_time >= end_time:
                print(f"Warning: Invalid timecode range in row {index + 1}: {row['Start']} - {row['End']}")
                continue
            
            if end_time > video.duration:
                print(f"Warning: End timecode exceeds video duration in row {index + 1}")
                continue
            
            # Create clip
            clip = video.subclip(start_time, end_time)
            
            # Generate output filename
            if 'Outputname' in df.columns and pd.notna(row['Outputname']):
                output_name = row['Outputname']
            else:
                output_name = f"clip_{index + 1:03d}"
            
            # Ensure output filename has video extension
            if not output_name.lower().endswith(('.mp4', '.avi', '.mov')):
                output_name += '.mp4'
            
            output_path = os.path.join(output_dir, output_name)
            
            # Write clip to file
            clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
            clip.close()
            
            # Clean up temporary files
            temp_files = [f for f in os.listdir(output_dir) if f.startswith('temp_')]
            for temp_file in temp_files:
                try:
                    os.remove(os.path.join(output_dir, temp_file))
                except Exception as e:
                    print(f"Warning: Could not remove temporary file {temp_file}: {str(e)}")
            
        except Exception as e:
            print(f"Error processing row {index + 1}: {str(e)}")
    
    # Clean up
    video.close()
    print("Processing complete!")

def main():
    parser = argparse.ArgumentParser(description='Create video clips from timecodes in CSV file')
    parser.add_argument('--video', required=True, help='Path to input video file')
    parser.add_argument('--csv', required=True, help='Path to CSV file with timecodes')
    parser.add_argument('--output', required=True, help='Output directory for clips')
    
    args = parser.parse_args()
    
    # Validate input files
    if not os.path.exists(args.video):
        raise FileNotFoundError(f"Video file not found: {args.video}")
    if not os.path.exists(args.csv):
        raise FileNotFoundError(f"CSV file not found: {args.csv}")
    
    create_clips(args.video, args.csv, args.output)

if __name__ == '__main__':
    main() 