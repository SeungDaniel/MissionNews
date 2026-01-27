import ffmpeg
import os
import uuid
from src.config_loader import settings

class MediaProcessor:
    def __init__(self):
        self.temp_dir = settings.paths['temp']
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    def extract_audio(self, video_path):
        """
        Extracts audio from video and saves as mp3 in temp dir.
        Returns path to audio file.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_path = os.path.join(self.temp_dir, f"{base_name}.mp3")

        print(f"Extracting audio: {video_path} -> {output_path}")
        
        try:
            (
                ffmpeg
                .input(video_path)
                .output(output_path, acodec='libmp3lame', qscale=2, loglevel="error")
                .overwrite_output()
                .run()
            )
            return output_path
        except ffmpeg.Error as e:
            print("FFmpeg Error:", e.stderr.decode() if e.stderr else str(e))
            raise RuntimeError("Audio extraction failed")

    def capture_frame(self, video_path, timestamp=0):
        """
        Captures a single frame at the given timestamp (seconds).
        Returns the path to the captured image.
        """
        base_name = os.path.splitext(os.path.basename(video_path))[0]

        # Use UUID for cache busting and explicit uniqueness
        unique_id = str(uuid.uuid4())[:8]
        ts_str = str(timestamp).replace('.', '_')
        output_path = os.path.join(self.temp_dir, f"{base_name}_params_{ts_str}_{unique_id}.jpg")
        
        try:
            (
                ffmpeg
                .input(video_path, ss=timestamp)
                .output(output_path, vframes=1, qscale=2, loglevel="error")
                .overwrite_output()
                .run()
            )
            return output_path
        except ffmpeg.Error:
            print(f"Failed to capture frame at {timestamp}s")
            return None

    def process_thumbnail_4_3(self, image_path, output_path):
        """
        Crops the image to 4:3 aspect ratio and removes the bottom 25% (subtitle area).
        1. Crop bottom 25% (h=ih*0.75)
        2. Crop to 4:3 center from the result
        """
        try:
            (
                ffmpeg
                .input(image_path)
                .filter('crop', 'iw', 'ih*0.75', '0', '0') # 1. Cut bottom 25% (Keep top 75%)
                .filter('crop', 'ih*(4/3)', 'ih', '(iw-ow)/2', '(ih-oh)/2') # 2. Center Crop to 4:3
                .output(output_path, qscale=2, loglevel="error")
                .overwrite_output()
                .run()
            )
            return output_path
        except ffmpeg.Error as e:
            print(f"Thumbnail processing failed: {e}")
            return None

    def create_thumbnail_candidates(self, video_path):
        """
        Extracts 8 thumbnails:
        - 5 from the first 30 seconds (Intro/Speaker)
        - 3 from the rest of the video (Body/Field)
        Returns a list of paths.
        """
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        duration = self._get_duration(video_path)
        
        candidates = []
        timestamps = []
        
        # 1. First 30 Seconds (5 frames)
        # Avoid 0s (black screen), start at 2s.
        # If video is shorter than 30s, just spread evenly across duration.
        if duration <= 30:
            step = duration / 6
            timestamps = [step * i for i in range(1, 7)]
        else:
            # 2, 8, 14, 20, 26 seconds
            timestamps = [2, 7, 9, 11, 13, 15]
            
            # 2. Rest of the video (3 frames)
            # From 30s to End. Spread at 25%, 50%, 75% of the remaining time.
            remaining = duration - 30
            timestamps += [30 + remaining * 0.25, 30 + remaining * 0.5, 30 + remaining * 0.75]
        
        print(f"Generating 8 thumbnail candidates for: {base_name}")
        
        for i, ts in enumerate(timestamps):
            unique_id = str(uuid.uuid4())[:8]
            output_path = os.path.join(self.temp_dir, f"{base_name}_thumb_{i+1}_{unique_id}.jpg")
            
            try:
                (
                    ffmpeg
                    .input(video_path, ss=ts)
                    .output(output_path, vframes=1, qscale=2, loglevel="error")
                    .overwrite_output()
                    .run()
                )
                candidates.append(output_path)
            except ffmpeg.Error:
                print(f"Failed to generate thumb at {ts}s")

        return candidates

    def _get_duration(self, video_path):
        try:
            probe = ffmpeg.probe(video_path)
            return float(probe['format']['duration'])
        except Exception:
            return 60.0 # Default fallback


