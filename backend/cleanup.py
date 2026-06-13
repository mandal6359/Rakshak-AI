import os
import glob
import time

ALERT_FOLDER = "alerts"
MAX_IMAGES = 200

def purge_old_snapshots():
    """Maintains a bounded storage footprint by keeping only the 200 newest screenshots."""
    if not os.path.exists(ALERT_FOLDER):
        return

    # Find all file paths ending in .jpg inside the directory
    all_snapshots = glob.glob(os.path.join(ALERT_FOLDER, "*.jpg"))
    
    # Filter out volatile temporary system streaming images from deletion calculation
    evidence_images = [img for img in all_snapshots if "live_cam" not in img and "latest_heatmap" not in img]
    
    # Sort files by creation modification time (Oldest files first)
    evidence_images.sort(key=os.path.getmtime)
    
    total_count = len(evidence_images)
    
    if total_count > MAX_IMAGES:
        excess_count = total_count - MAX_IMAGES
        print(f"🧹 Storage Threshold Breached: {total_count} images found (Limit: {MAX_IMAGES}).")
        print(f"⏳ Purging the oldest {excess_count} visual asset files from disk storage...")
        
        # Loop and drop excess files
        for i in range(excess_count):
            try:
                os.remove(evidence_images[i])
            except Exception as e:
                print(f"Failed to remove file asset {evidence_images[i]}: {e}")
        print("✅ Disk storage footprint successfully bounded and stabilized!")
    else:
        print(f"📊 Storage footprint stable: {total_count}/{MAX_IMAGES} evidence images online.")

if __name__ == "__main__":
    while True:
        print("\n⏱️ Initializing scheduled storage volume maintenance scan...")
        purge_old_snapshots()
        # Sleep for 60 seconds before executing the next storage verification sweep
        time.sleep(60)