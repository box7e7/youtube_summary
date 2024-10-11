import re

def clean_timestamp(timestamp):
    # Extract only the time range using regex
    match = re.search(r'(\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3})', timestamp)
    return match.group(1) if match else timestamp

def read_vtt_clean_timestamps(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    subtitles = {}
    text_to_time = {}
    current_time = None

    for line in lines:
        line = line.strip()
        if '-->' in line:
            current_time = clean_timestamp(line)
        elif line and current_time:
            if line not in text_to_time:
                # New text, add it to both dictionaries
                subtitles[current_time] = line
                text_to_time[line] = current_time
            else:
                # Text is a duplicate, update the timestamp
                old_time = text_to_time[line]
                del subtitles[old_time]
                subtitles[current_time] = line
                text_to_time[line] = current_time
            current_time = None

    return subtitles

# Example usage
file_path = 'file.en.vtt'
subtitles = read_vtt_clean_timestamps(file_path)

for time, text in subtitles.items():
    print(f"Time: {time}")
    print(f"Text: {text}")
    print()
