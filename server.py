
import os
import subprocess
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

PORT = int(os.environ.get("PORT", "10000"))
STREAM_URL = os.environ.get("STREAM_URL", "").strip()
OUTPUT_DIR = "/tmp/hls"

os.makedirs(OUTPUT_DIR, exist_ok=True)

if not STREAM_URL:
    raise RuntimeError("Missing STREAM_URL environment variable")

playlist = os.path.join(OUTPUT_DIR, "index.m3u8")
segment_pattern = os.path.join(OUTPUT_DIR, "index%d.ts")

ffmpeg_cmd = [
    "ffmpeg",
    "-hide_banner",
    "-loglevel", "warning",
    "-reconnect", "1",
    "-reconnect_streamed", "1",
    "-reconnect_delay_max", "5",
    "-i", STREAM_URL,
    "-map", "0:v:0?",
    "-map", "0:a:0?",
    "-c", "copy",
    "-f", "hls",
    "-hls_time", "4",
    "-hls_list_size", "6",
    "-hls_flags", "delete_segments+append_list",
    "-hls_segment_filename", segment_pattern,
    playlist,
]

subprocess.Popen(ffmpeg_cmd)

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=OUTPUT_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def guess_type(self, path):
        if path.endswith(".m3u8"):
            return "application/vnd.apple.mpegurl"
        if path.endswith(".ts"):
            return "video/mp2t"
        return super().guess_type(path)

server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
print(f"HLS server listening on port {PORT}", flush=True)
server.serve_forever()
