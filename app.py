# File: app.py
from flask import Flask, request, send_file
import os
import subprocess
import tempfile
import shutil

app = Flask(__name__)

ANDROID_HOME = "/path/to/your/android/sdk"
BUILD_TOOLS_VERSION = "30.0.3"

@app.route('/generate-apk', methods=['POST'])
def generate_apk():
    app_name = request.form['appName']
    logo = request.files['logo']
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save logo
        logo_path = os.path.join(tmpdir, "app_logo.png")
        logo.save(logo_path)
        
        # Create basic Android project structure
        create_android_project(tmpdir, app_name)
        
        # Customize the app
        customize_app(tmpdir, app_name, logo_path)
        
        # Build APK
        apk_path = build_apk(tmpdir)
        
        # Send APK file
        return send_file(apk_path, as_attachment=True, attachment_filename=f"{app_name}.apk")

def create_android_project(project_dir, app_name):
    subprocess.run([
        f"{ANDROID_HOME}/tools/bin/sdkmanager", "build-tools;{BUILD_TOOLS_VERSION}"
    ], check=True)
    
    subprocess.run([
        f"{ANDROID_HOME}/tools/bin/avdmanager", "create", "avd",
        "-n", "test", "-k", "system-images;android-30;google_apis;x86"
    ], check=True)
    
    subprocess.run([
        f"{ANDROID_HOME}/tools/bin/sdkmanager", "--licenses"
    ], check=True)
    
    subprocess.run([
        f"{ANDROID_HOME}/tools/bin/flutter", "create",
        "--org", "com.example", project_dir
    ], check=True)

def customize_app(project_dir, app_name, logo_path):
    # Update app name in AndroidManifest.xml
    manifest_path = os.path.join(project_dir, "android/app/src/main/AndroidManifest.xml")
    with open(manifest_path, 'r+') as f:
        content = f.read()
        content = content.replace("android:label=\"myapp\"", f"android:label=\"{app_name}\"")
        f.seek(0)
        f.write(content)
        f.truncate()
    
    # Copy logo to mipmap directories
    mipmap_dirs = [
        "android/app/src/main/res/mipmap-hdpi",
        "android/app/src/main/res/mipmap-mdpi",
        "android/app/src/main/res/mipmap-xhdpi",
        "android/app/src/main/res/mipmap-xxhdpi",
        "android/app/src/main/res/mipmap-xxxhdpi"
    ]
    for mipmap_dir in mipmap_dirs:
        shutil.copy(logo_path, os.path.join(project_dir, mipmap_dir, "ic_launcher.png"))

def build_apk(project_dir):
    subprocess.run([
        "flutter", "build", "apk"
    ], cwd=project_dir, check=True)
    
    return os.path.join(project_dir, "build/app/outputs/flutter-apk/app-release.apk")

if __name__ == '__main__':
    app.run(debug=True)

# File: requirements.txt
Flask==2.0.1
