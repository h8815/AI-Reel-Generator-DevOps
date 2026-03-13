import os
import time
import subprocess


def has_required_assets(folder: str) -> bool:
    base = f"user_uploads/{folder}"
    audio_path = os.path.join(base, "audio.mp3")
    input_path = os.path.join(base, "input.txt")

    if not os.path.exists(audio_path):
        print(f"Missing audio.mp3 for {folder}")
        return False
    if not os.path.exists(input_path):
        print(f"Missing input.txt for {folder}")
        return False

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if "file '" not in content:
            print(f"input.txt has no image entries for {folder}")
            return False
    except Exception as e:
        print(f"Error reading input.txt for {folder}: {e}")
        return False

    return True


def get_filter_string(filter_effect):
    """
    Return FFmpeg filter string based on selected effect
    """
    filters = {
        # Basic Filters
        "none": "",
        "grayscale": "hue=s=0",
        "sepia": "eq=gamma=1.0:saturation=1.2:contrast=1.0,colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131:0",
        # Color Adjustments
        "vibrant": "eq=saturation=1.6:contrast=1.2",
        "warm": "colorbalance=rs=.3:gs=.1:bs=-.3,eq=saturation=1.1",
        "cool": "colorbalance=rs=-.3:gs=-.1:bs=.3,eq=saturation=1.1",
        "vintage": "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131,vignette=angle=PI/3",
        # Dramatic Filters
        "noir": "hue=s=0,eq=contrast=1.5:brightness=-0.05",
        "dramatic": "eq=contrast=1.4:brightness=-0.1:saturation=0.8",
        "cinematic": "eq=contrast=1.3:brightness=-0.05:saturation=1.1,colorbalance=rs=.1:gs=-.05:bs=.15",
        # Bright & Light
        "bright": "eq=brightness=0.1:contrast=1.1:saturation=1.2",
        "soft": "eq=gamma=1.2:saturation=0.9,gblur=sigma=0.5",
        "dream": "eq=gamma=1.3:saturation=0.8,gblur=sigma=1",
        # Instagram-style Filters
        "nashville": "colorchannelmixer=.6:.4:.15:0:.45:.45:.3:0:.2:.2:.15,eq=contrast=1.2:brightness=0.05",
        "lofi": "eq=contrast=1.5:saturation=1.2,colorbalance=rs=.2:bs=-.1",
        "xpro": "eq=contrast=1.3:saturation=1.2,colorbalance=rs=-.1:gs=.05:bs=.2,curves=all='0/0.1 0.5/0.58 1/0.9'",
        # Modern Filters
        "fade": "eq=saturation=0.7:contrast=0.9:brightness=0.05",
        "sharp": "unsharp=5:5:1.0:5:5:0.0,eq=contrast=1.1",
        "vignette": "vignette=angle=PI/3",
        "blur_edges": "boxblur=luma_radius=3:luma_power=1,pad=iw:ih:0:0:color=black",
    }

    return filters.get(filter_effect, "")


def create_reel(
    folder, reel_name=None, text_overlay="", aspect_ratio="9:16", filter_effect="none"
):
    """
    Create a reel from the given folder with customization options
    """
    if reel_name is None:
        reel_name = folder

    # Get the absolute path to the output file
    original_dir = os.getcwd()
    output_dir = os.path.join(original_dir, "static", "reels")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{reel_name}.mp4")

    # Set dimensions based on aspect ratio
    if aspect_ratio == "9:16":
        width, height = 1080, 1920
    elif aspect_ratio == "16:9":
        width, height = 1920, 1080
    elif aspect_ratio == "1:1":
        width, height = 1080, 1080
    else:
        width, height = 1080, 1920

    # Build single filter string (combine all filters)
    vf_parts = [
        f"scale={width}:{height}:force_original_aspect_ratio=decrease",
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black",
    ]

    # Add video filter effect
    filter_string = get_filter_string(filter_effect)
    if filter_string:
        vf_parts.append(filter_string)

    # Add text overlay if provided
    if text_overlay:
        text_clean = text_overlay.replace("'", "'\\''").replace(":", "\\:")
        text_filter = f"drawtext=text='{text_clean}':fontsize=60:fontcolor=white:x=(w-text_w)/2:y=h-150:box=1:boxcolor=black@0.5:boxborderw=10"
        vf_parts.append(text_filter)

    vf_string = ",".join(vf_parts)

    # Build FFmpeg command
    command = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        "input.txt",
        "-i",
        "audio.mp3",
        "-vf",
        vf_string,
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        "-shortest",
        "-r",
        "30",
        "-pix_fmt",
        "yuv420p",
        output_path,
    ]

    # Change to target directory
    target_dir = os.path.join(original_dir, "user_uploads", folder)

    try:
        os.chdir(target_dir)

        result = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )

        if result.returncode != 0:
            print(f"FFmpeg Error for {folder}:")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            raise Exception(f"FFmpeg failed with return code {result.returncode}")

        print(f"Successfully created reel: {reel_name}")

    finally:
        os.chdir(original_dir)


if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("static/reels", exist_ok=True)

    while True:
        print("Processing queue...")

        done_file = "done.txt"
        if not os.path.exists(done_file):
            with open(done_file, "w", encoding="utf-8") as f:
                pass

        with open(done_file, "r", encoding="utf-8") as f:
            done_folders = f.readlines()

        done_folders = [f.strip() for f in done_folders]

        if not os.path.exists("user_uploads"):
            os.makedirs("user_uploads", exist_ok=True)

        folders = os.listdir("user_uploads")

        for folder in folders:
            if folder not in done_folders:
                if has_required_assets(folder):
                    try:
                        # Read settings if available
                        settings_path = f"user_uploads/{folder}/settings.txt"
                        text_overlay = ""
                        aspect_ratio = "9:16"
                        filter_effect = "none"

                        if os.path.exists(settings_path):
                            with open(settings_path, "r", encoding="utf-8") as f:
                                for line in f:
                                    if "=" in line:
                                        key, value = line.strip().split("=", 1)
                                        if key == "text_overlay":
                                            text_overlay = value
                                        elif key == "aspect_ratio":
                                            aspect_ratio = value
                                        elif key == "filter_effect":
                                            filter_effect = value
                        create_reel(
                            folder, folder, text_overlay, aspect_ratio, filter_effect
                        )
                        with open(done_file, "a", encoding="utf-8") as f:
                            f.write(folder + "\n")
                    except Exception as e:
                        print(f"Error creating reel for {folder}: {e}")
                        import traceback

                        traceback.print_exc()
                else:
                    print(
                        f"Skipping {folder} until audio.mp3 and input.txt with images are available"
                    )

        time.sleep(4)
