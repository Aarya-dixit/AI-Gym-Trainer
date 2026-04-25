"""
Verify Training Setup
Check that all dependencies and directories are ready
"""
import sys
from pathlib import Path

def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor} (need 3.8+)")
        return False

def check_dependencies():
    """Check required packages"""
    print("\nChecking dependencies...")
    
    dependencies = {
        'torch': 'PyTorch',
        'numpy': 'NumPy',
        'cv2': 'OpenCV',
        'mediapipe': 'MediaPipe'
    }
    
    all_ok = True
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} (not installed)")
            all_ok = False
    
    return all_ok

def check_directories():
    """Check required directories"""
    print("\nChecking directories...")
    
    dirs = [
        'data/videos',
        'data/processed',
        '../../models'
    ]
    
    all_ok = True
    for dir_path in dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"  ✓ {dir_path}")
        else:
            print(f"  ✗ {dir_path} (creating...)")
            path.mkdir(parents=True, exist_ok=True)
            print(f"    ✓ Created")
    
    return all_ok

def check_videos():
    """Check for video files"""
    print("\nChecking for videos...")
    
    video_dir = Path('data/videos')
    video_files = list(video_dir.glob("*.mp4")) + \
                  list(video_dir.glob("*.avi")) + \
                  list(video_dir.glob("*.mov"))
    
    if video_files:
        print(f"  ✓ Found {len(video_files)} videos:")
        for video in video_files:
            print(f"    - {video.name}")
        return True
    else:
        print(f"  ⚠ No videos found in data/videos/")
        print(f"    Please record and place videos there")
        return False

def check_modules():
    """Check if training modules exist"""
    print("\nChecking training modules...")
    
    modules = [
        'auto_label_videos.py',
        'dataset_builder.py',
        'train.py',
        'train_complete.py'
    ]
    
    all_ok = True
    for module in modules:
        path = Path(module)
        if path.exists():
            print(f"  ✓ {module}")
        else:
            print(f"  ✗ {module} (missing)")
            all_ok = False
    
    return all_ok

def main():
    """Run all checks"""
    print("="*60)
    print("TRAINING SETUP VERIFICATION")
    print("="*60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Directories", check_directories),
        ("Training Modules", check_modules),
        ("Videos", check_videos),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    all_ok = True
    for name, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {name}")
        if not result:
            all_ok = False
    
    print("\n" + "="*60)
    
    if all_ok:
        print("✅ Setup is ready! You can start training.")
        print("\nNext steps:")
        print("1. Record exercise videos")
        print("2. Place in: data/videos/")
        print("3. Run: python train_complete.py")
    else:
        print("⚠️  Some checks failed. Please fix issues above.")
        print("\nTo install dependencies:")
        print("  pip install -r ../requirements.txt")
    
    print("="*60)

if __name__ == "__main__":
    main()
