"""
Quick start script for testing the API locally
"""

import subprocess
import sys
import os
import time

def main():
    print("\n" + "="*70)
    print("🏥 OPD Token Allocation Engine - Quick Start")
    print("="*70)
    
    # Check if in virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("\n⚠️  WARNING: Not in a virtual environment!")
        print("It's recommended to create one:")
        print("  python -m venv venv")
        print("  venv\\Scripts\\activate  (Windows)")
        print("  source venv/bin/activate  (Linux/Mac)")
        
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Check if dependencies are installed
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        print("\n✓ Dependencies found")
    except ImportError:
        print("\n⚠️  Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Create .env if not exists
    if not os.path.exists('.env'):
        print("\n📝 Creating .env file...")
        with open('.env', 'w') as f:
            f.write("DATABASE_URL=sqlite+aiosqlite:///./opd_tokens.db\n")
            f.write("ENVIRONMENT=development\n")
            f.write("API_HOST=0.0.0.0\n")
            f.write("API_PORT=8000\n")
        print("✓ Created .env")
    
    print("\n🚀 Starting API server...")
    print("="*70)
    print("\n📍 API will be available at:")
    print("   - Main: http://localhost:8000")
    print("   - Docs: http://localhost:8000/docs")
    print("   - ReDoc: http://localhost:8000/redoc")
    print("\n💡 To run simulation (in another terminal):")
    print("   python simulation.py --run")
    print("\n" + "="*70)
    print("\nPress Ctrl+C to stop the server\n")
    
    # Start the server
    try:
        subprocess.run([sys.executable, "-m", "app.main"])
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped")

if __name__ == "__main__":
    main()
