from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import uuid
from werkzeug.utils import secure_filename
import os
import subprocess
import json
from datetime import datetime
from auth import init_db, create_user, verify_user, login_required, get_user_folder, get_user_reels_folder, get_user_metadata_folder

UPLOAD_FOLDER = "user_uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB for images
MAX_AUDIO_SIZE = 50 * 1024 * 1024  # 50MB for audio

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100MB total

# Use environment variable for secret key in production
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(24)

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not email or not password:
            flash("All fields are required.", "error")
            return render_template("register.html")

        if len(username) < 3:
            flash("Username must be at least 3 characters long.", "error")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        if create_user(username, email, password):
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))
        else:
            flash("Username or email already exists.", "error")
            return render_template("register.html")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = verify_user(username, password)
        if user:
            session["user_id"] = user[0]
            session["username"] = user[1]
            flash(f"Welcome back, {user[1]}!", "success")
            return redirect(url_for("create"))
        else:
            flash("Invalid username or password.", "error")
            return render_template("login.html")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("home"))


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    myid = uuid.uuid1()
    if request.method == "POST":
        print("=== Starting Reel Creation ===")
        print("Form data:", request.form)
        print("Files:", list(request.files.keys()))

        rec_id = request.form.get("uuid")
        reel_name = request.form.get("reel_name", "").strip()

        # Get customization options
        image_duration = request.form.get("image_duration", "1")
        text_overlay = request.form.get("text_overlay", "").strip()
        aspect_ratio = request.form.get("aspect_ratio", "9:16")
        filter_effect = request.form.get("filter_effect", "none")

        input_files = []

        # Validate reel name
        if not reel_name:
            return render_template(
                "create.html", myid=myid, error="Please provide a name for your reel."
            )

        # Sanitize reel name
        reel_name = secure_filename(reel_name)
        if not reel_name:
            return render_template(
                "create.html",
                myid=myid,
                error="Invalid reel name. Please use only letters, numbers, and underscores.",
            )

        # Validate image duration
        try:
            duration = float(image_duration)
            if duration < 0.5 or duration > 10:
                return render_template(
                    "create.html",
                    myid=myid,
                    error="Image duration must be between 0.5 and 10 seconds.",
                )
        except ValueError:
            return render_template(
                "create.html", myid=myid, error="Invalid image duration value."
            )

        # Check if FFmpeg is installed
        if not check_ffmpeg():
            return render_template(
                "create.html",
                myid=myid,
                error="FFmpeg is not installed. Please install FFmpeg to create reels.",
            )

        # Create user-specific folder
        user_id = session.get("user_id")
        user_base_folder = get_user_folder(user_id)
        if not os.path.exists(user_base_folder):
            os.makedirs(user_base_folder, exist_ok=True)

        target_folder = os.path.join(user_base_folder, str(rec_id))
        if not os.path.exists(target_folder):
            os.makedirs(target_folder, exist_ok=True)

        # Process audio file
        audio_file = request.files.get("audio")
        has_audio = False
        if audio_file and audio_file.filename:
            audio_file.seek(0, os.SEEK_END)
            audio_size = audio_file.tell()
            audio_file.seek(0)

            if audio_size > MAX_AUDIO_SIZE:
                return render_template(
                    "create.html",
                    myid=myid,
                    error=f"Audio file is too large. Maximum size is {MAX_AUDIO_SIZE // (1024*1024)}MB.",
                )

            audio_filename = secure_filename(audio_file.filename)
            audio_ext = os.path.splitext(audio_filename)[1].lower()
            if audio_ext == ".mp3":
                audio_path = os.path.join(target_folder, "audio.mp3")
                audio_file.save(audio_path)
                has_audio = True
                print(f"Saved audio.mp3 at {audio_path}")
            else:
                return render_template(
                    "create.html",
                    myid=myid,
                    error="Invalid audio format. Only MP3 files are allowed.",
                )
        else:
            return render_template(
                "create.html", myid=myid, error="Please upload an audio file."
            )

        # Process image files - collect them in order
        file_keys = sorted(
            [key for key in request.files.keys() if key.startswith("file")]
        )
        print(f"Processing {len(file_keys)} image files")

        for key in file_keys:
            file = request.files[key]
            if file and file.filename:
                file.seek(0, os.SEEK_END)
                file_size = file.tell()
                file.seek(0)

                if file_size > MAX_FILE_SIZE:
                    return render_template(
                        "create.html",
                        myid=myid,
                        error=f"One or more images are too large. Maximum size per image is {MAX_FILE_SIZE // (1024*1024)}MB.",
                    )

                filename = secure_filename(file.filename)
                ext = os.path.splitext(filename)[1].lower().lstrip(".")
                if ext in ALLOWED_EXTENSIONS:
                    # Save with index to maintain order
                    new_filename = (
                        f"img_{len(input_files):03d}{os.path.splitext(filename)[1]}"
                    )
                    file_path = os.path.join(target_folder, new_filename)
                    file.save(file_path)
                    input_files.append(new_filename)
                    print(f"Saved image: {new_filename}")

        if not input_files:
            return render_template(
                "create.html",
                myid=myid,
                error="Please upload at least one image (JPG, JPEG, or PNG).",
            )

        print(f"Total images saved: {len(input_files)}")
        if has_audio and input_files:
            # Create input.txt for FFmpeg concat
            input_txt_path = os.path.join(target_folder, "input.txt")
            with open(input_txt_path, "w", encoding="utf-8") as f:
                for fl in input_files:
                    f.write(f"file '{fl}'\n")
                    f.write(f"duration {duration}\n")
                # Add the last file again without duration
                f.write(f"file '{input_files[-1]}'\n")

            print(f"Created input.txt with {len(input_files)} images")

            # Save customization settings
            settings_path = os.path.join(target_folder, "settings.txt")
            with open(settings_path, "w", encoding="utf-8") as f:
                f.write(f"text_overlay={text_overlay}\n")
                f.write(f"aspect_ratio={aspect_ratio}\n")
                f.write(f"filter_effect={filter_effect}\n")

            # Ensure user-specific reels directory exists
            reels_dir = get_user_reels_folder(user_id)
            if not os.path.exists(reels_dir):
                os.makedirs(reels_dir, exist_ok=True)

            # Create user-specific metadata directory
            metadata_dir = get_user_metadata_folder(user_id)
            if not os.path.exists(metadata_dir):
                os.makedirs(metadata_dir, exist_ok=True)

            # Create reel
            if has_required_assets(str(rec_id), user_id):
                try:
                    create_reel(
                        str(rec_id),
                        reel_name,
                        text_overlay,
                        aspect_ratio,
                        filter_effect,
                        user_id,
                    )

                    # Save metadata
                    metadata = {
                        "name": reel_name,
                        "created_at": datetime.now().isoformat(),
                        "image_count": len(input_files),
                        "duration": duration,
                        "text_overlay": text_overlay,
                        "aspect_ratio": aspect_ratio,
                        "filter_effect": filter_effect,
                    }
                    metadata_path = os.path.join(metadata_dir, f"{reel_name}.json")
                    with open(metadata_path, "w", encoding="utf-8") as f:
                        json.dump(metadata, f, indent=2)

                    return render_template(
                        "create.html",
                        myid=myid,
                        success=f"Reel '{reel_name}' created successfully with {len(input_files)} images! Go and watch it in the gallery section.",
                        show_gallery_link=True,
                    )
                except Exception as e:
                    print(f"Error creating reel: {e}")
                    import traceback

                    traceback.print_exc()
                    return render_template(
                        "create.html",
                        myid=myid,
                        error=f"Error creating reel: {str(e)}. Please check the console for details.",
                    )
            else:
                return render_template(
                    "create.html",
                    myid=myid,
                    error="Missing required assets for reel creation.",
                )
        else:
            return render_template(
                "create.html", myid=myid, error="Please provide both audio and images."
            )

    return render_template("create.html", myid=myid)


@app.route("/gallery")
@login_required
def gallery():
    user_id = session.get("user_id")
    reels_dir = get_user_reels_folder(user_id)
    metadata_dir = get_user_metadata_folder(user_id)

    if not os.path.exists(reels_dir):
        os.makedirs(reels_dir, exist_ok=True)
    if not os.path.exists(metadata_dir):
        os.makedirs(metadata_dir, exist_ok=True)

    reels = []
    for filename in os.listdir(reels_dir):
        if filename.endswith(".mp4"):
            reel_info = {
                "filename": filename,
                "name": os.path.splitext(filename)[0],
                "size": os.path.getsize(os.path.join(reels_dir, filename)),
                "created_at": datetime.fromtimestamp(
                    os.path.getctime(os.path.join(reels_dir, filename))
                ).strftime("%Y-%m-%d %H:%M"),
            }

            # Load metadata if exists
            metadata_path = os.path.join(
                metadata_dir, f"{os.path.splitext(filename)[0]}.json"
            )
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                        reel_info.update(metadata)
                except:
                    pass

            reels.append(reel_info)

    # Sort by creation date (newest first)
    reels.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    print("Gallery reels:", [r["filename"] for r in reels])
    return render_template("gallery.html", reels=reels)


@app.route("/delete/<reel_name>", methods=["POST"])
@login_required
def delete_reel(reel_name):
    try:
        user_id = session.get("user_id")
        reel_path = os.path.join(get_user_reels_folder(user_id), secure_filename(reel_name))
        metadata_path = os.path.join(
            get_user_metadata_folder(user_id),
            f"{os.path.splitext(secure_filename(reel_name))[0]}.json",
        )

        if os.path.exists(reel_path):
            os.remove(reel_path)

        if os.path.exists(metadata_path):
            os.remove(metadata_path)

        return jsonify({"success": True, "message": "Reel deleted successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/help")
def help():
    return render_template("help.html")


def has_required_assets(folder: str, user_id: int) -> bool:
    base = os.path.join(get_user_folder(user_id), folder)
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
    folder, reel_name, text_overlay="", aspect_ratio="9:16", filter_effect="none", user_id=None
):
    # Get the absolute path to the output file
    original_dir = os.getcwd()
    output_dir = os.path.join(original_dir, get_user_reels_folder(user_id))
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

    # Change working directory to process files correctly
    target_dir = os.path.join(original_dir, get_user_folder(user_id), folder)

    try:
        os.chdir(target_dir)
        print(f"Running FFmpeg command: {' '.join(command)}")

        result = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )

        if result.returncode != 0:
            print("FFmpeg STDOUT:", result.stdout)
            print("FFmpeg STDERR:", result.stderr)
            raise Exception(f"FFmpeg failed with return code {result.returncode}")

        print(f"Successfully created reel: {reel_name}")
    finally:
        os.chdir(original_dir)

if __name__ == "__main__":
    # Initialize database
    init_db()
    
    # Create necessary directories
    os.makedirs("user_uploads", exist_ok=True)
    os.makedirs("static/reels", exist_ok=True)
    os.makedirs("static/metadata", exist_ok=True)

    app.run(debug=True, host="0.0.0.0", port=5000)
