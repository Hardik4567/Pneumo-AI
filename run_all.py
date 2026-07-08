#!/usr/bin/env python
"""
PneumoAI - Complete Application Startup Script
Runs both Backend (FastAPI) and Frontend (Flask) servers
"""

import os
import sys
import subprocess
import time
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Get configuration from environment
    backend_port = os.getenv('BACKEND_PORT', '8000')
    frontend_port = os.getenv('FRONTEND_PORT', '5000')
    backend_host = os.getenv('BACKEND_HOST', '0.0.0.0')
    frontend_host = os.getenv('FRONTEND_HOST', '0.0.0.0')
    
    print("=" * 60)
    print("[Lungs] PneumoAI - Pneumonia Detection System")
    print("=" * 60)
    print("\n[Settings] Configuration:")
    print(f"  Backend:  {backend_host}:{backend_port}")
    print(f"  Frontend: {frontend_host}:{frontend_port}")
    print("\n[Start] Starting services...\n")
    
    processes = []
    
    try:
        # Start Backend Server (FastAPI)
        print("[>] Starting Backend Server (FastAPI)...")
        backend_process = subprocess.Popen(
            [sys.executable, 'startup.py'],
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        processes.append(('Backend', backend_process))
        print(f"   * Backend PID: {backend_process.pid}")
        
        # Give backend time to start
        time.sleep(3)
        
        # Start Frontend Server (Flask)
        print("\n[>] Starting Frontend Server (Flask)...")
        frontend_process = subprocess.Popen(
            [sys.executable, '-m', 'flask', 'run', '--host', frontend_host, '--port', frontend_port],
            cwd=os.path.join(os.getcwd(), 'frontend'),
            env={**os.environ, 'FLASK_APP': 'app.py', 'FLASK_ENV': 'development'},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        processes.append(('Frontend', frontend_process))
        print(f"   * Frontend PID: {frontend_process.pid}")
        
        print("\n" + "=" * 60)
        print("[OK] All services started successfully!")
        print("=" * 60)
        print("\nAccess URLs:")
        print(f"   Frontend:  http://localhost:{frontend_port}")
        print(f"   Backend:   http://localhost:{backend_port}/docs")
        print("\nPress Ctrl+C to stop all services...\n")
        
        # Wait for all processes
        for name, process in processes:
            returncode = process.wait()
            if returncode != 0:
                print(f"\n[Error] {name} server stopped with code {returncode}")
                
    except KeyboardInterrupt:
        print("\n\n[Shutdown] Shutdown signal received. Stopping all services...\n")
        for name, process in processes:
            try:
                print(f"   Stopping {name}...")
                process.terminate()
                process.wait(timeout=5)
                print(f"   * {name} stopped")
            except subprocess.TimeoutExpired:
                print(f"   [Alert] Force killing {name}...")
                process.kill()
                print(f"   * {name} killed")
            except Exception as e:
                print(f"   [Error] Error stopping {name}: {e}")
        
        print("\n[OK] All services stopped.")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n[Error] Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
