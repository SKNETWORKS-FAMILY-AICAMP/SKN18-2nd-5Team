#!/usr/bin/env python3
"""
호텔 예약 예측 서비스 서버 시작 스크립트
"""
import os
import sys
from pathlib import Path

def main():
    # 현재 디렉토리를 backend로 변경
    backend_dir = Path(__file__).parent / "backend"
    
    if not backend_dir.exists():
        print("❌ backend 디렉토리를 찾을 수 없습니다.")
        sys.exit(1)
    
    os.chdir(backend_dir)
    
    # 가상환경 확인
    venv_path = backend_dir / "venv"
    if venv_path.exists():
        print("✅ 가상환경을 찾았습니다.")
        if os.name == 'nt':  # Windows
            python_exe = venv_path / "Scripts" / "python.exe"
        else:  # Linux/Mac
            python_exe = venv_path / "bin" / "python"
    else:
        print("⚠️  가상환경을 찾을 수 없습니다. 시스템 Python을 사용합니다.")
        python_exe = "python"
    
    # 필요한 파일들 확인
    required_files = ["main.py", "database.py", "ml_model.py"]
    for file in required_files:
        if not (backend_dir / file).exists():
            print(f"❌ {file}을 찾을 수 없습니다.")
            sys.exit(1)
    
    print("🚀 서버를 시작합니다...")
    print("📍 URL: http://localhost:8000")
    print("📖 API 문서: http://localhost:8000/docs")
    print("🛑 서버를 중단하려면 Ctrl+C를 누르세요.")
    print("-" * 50)
    
    # 서버 실행
    os.system(f"{python_exe} main.py")

if __name__ == "__main__":
    main()
