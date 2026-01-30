"""
Project Setup Verification Script
Checks if everything is properly configured before running the application
"""

import sys
import os
from pathlib import Path


def check_python_version():
    """Verify Python version is 3.8 or higher."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detected")
        print(f"   Required: Python 3.8 or higher")
        print(f"   Download from: https://www.python.org/downloads/")
        return False
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True


def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pydantic',
        'aiosqlite'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Not installed")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print(f"   Install with: pip install -r requirements.txt")
        return False
    
    return True


def check_project_structure():
    """Verify project files exist."""
    required_files = [
        'app/__init__.py',
        'app/main.py',
        'app/api.py',
        'app/models.py',
        'app/schemas.py',
        'app/database.py',
        'app/config.py',
        'app/allocation_engine.py',
        'requirements.txt',
        'README.md'
    ]
    
    project_root = Path(__file__).parent
    all_exist = True
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing")
            all_exist = False
    
    return all_exist


def check_environment():
    """Check if .env file exists."""
    env_file = Path(__file__).parent / '.env'
    env_example = Path(__file__).parent / '.env.example'
    
    if env_file.exists():
        print(f"✅ .env file exists")
        return True
    elif env_example.exists():
        print(f"⚠️  .env file not found")
        print(f"   Creating from .env.example...")
        try:
            with open(env_example, 'r') as src:
                content = src.read()
            with open(env_file, 'w') as dst:
                dst.write(content)
            print(f"✅ Created .env file")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env: {e}")
            return False
    else:
        print(f"⚠️  .env and .env.example not found")
        print(f"   Creating default .env...")
        try:
            with open(env_file, 'w') as f:
                f.write("DATABASE_URL=sqlite+aiosqlite:///./opd_tokens.db\n")
                f.write("ENVIRONMENT=development\n")
                f.write("API_HOST=0.0.0.0\n")
                f.write("API_PORT=8000\n")
            print(f"✅ Created default .env file")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env: {e}")
            return False


def check_port_availability():
    """Check if port 8000 is available."""
    import socket
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8000))
    sock.close()
    
    if result == 0:
        print(f"⚠️  Port 8000 is already in use")
        print(f"   The server might already be running, or another application is using this port")
        print(f"   To find the process: netstat -ano | findstr :8000 (Windows)")
        return False
    else:
        print(f"✅ Port 8000 is available")
        return True


def main():
    """Run all verification checks."""
    print("\n" + "="*70)
    print("🔍 OPD Token Allocation Engine - Setup Verification")
    print("="*70)
    
    checks = {
        "Python Version": check_python_version,
        "Project Structure": check_project_structure,
        "Dependencies": check_dependencies,
        "Environment Config": check_environment,
        "Port Availability": check_port_availability
    }
    
    results = {}
    
    for check_name, check_func in checks.items():
        print(f"\n📋 Checking {check_name}...")
        print("-" * 70)
        results[check_name] = check_func()
    
    print("\n" + "="*70)
    print("📊 VERIFICATION SUMMARY")
    print("="*70)
    
    all_passed = True
    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {check_name}")
        if not passed:
            all_passed = False
    
    print("="*70)
    
    if all_passed:
        print("\n🎉 All checks passed! You're ready to go!")
        print("\nNext steps:")
        print("  1. Start the server:")
        print("     python start.py")
        print("\n  2. Visit the API documentation:")
        print("     http://localhost:8000/docs")
        print("\n  3. Run the simulation (in another terminal):")
        print("     python simulation.py --run")
        print("\n  4. Read the documentation:")
        print("     - QUICKSTART.md - Quick reference")
        print("     - README.md - Full documentation")
        print("     - API_TESTING.md - API examples")
        print("     - DEPLOYMENT.md - Deploy to production")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above before running the application.")
        print("\nCommon fixes:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Verify Python version: python --version")
        print("  - Check project structure is complete")
    
    print("\n" + "="*70 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
