 yt-dlp --write-auto-sub --sub-lang en --skip-download -o "file.%(ext)s" $1
 python3 vtt_to_text.py
#  python3 vtt_to_text.py > video.txt
