import os
import shutil
import zipfile

def build():
    addon_dir = "jiggle_physics_addon"
    rust_bin_src = os.path.join("jiggle_rust_core", "target", "release", "jiggle_rust_core.dll")
    rust_bin_dest = os.path.join(addon_dir, "jiggle_rust_core.pyd")
    output_zip = "jiggle_physics_addon.zip"

    print(f"--- Building Jiggle Physics Add-on ---")

    # 1. Copy Rust binary
    if os.path.exists(rust_bin_src):
        print(f"Copying {rust_bin_src} -> {rust_bin_dest}")
        shutil.copy2(rust_bin_src, rust_bin_dest)
    else:
        print(f"WARNING: Rust binary not found at {rust_bin_src}. Using existing .pyd if available.")

    # 2. Clean up old zip
    if os.path.exists(output_zip):
        print(f"Removing old {output_zip}")
        os.remove(output_zip)

    # 3. Create ZIP
    print(f"Creating {output_zip}...")
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(addon_dir):
            for file in files:
                # Skip python cache
                if "__pycache__" in root:
                    continue
                
                file_path = os.path.join(root, file)
                # The path inside the zip should start with the folder name
                arcname = os.path.relpath(file_path, os.path.dirname(addon_dir))
                zf.write(file_path, arcname)
                print(f"  + {arcname}")

    print(f"\nSUCCESS: {output_zip} generated correctly.")

if __name__ == "__main__":
    build()
