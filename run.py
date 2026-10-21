# run.py
import sys
import uvicorn

import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    print("=" * 65)
    print("🚀 ĐANG KHỞI CHẠY HỆ THỐNG ITICK TESTING PLATFORM...")
    print(f"📍 URL Giao diện Web:   http://127.0.0.1:{port}")
    print(f"📍 URL Swagger Docs:    http://127.0.0.1:{port}/docs")
    print(f"📍 URL OpenAPI Specs:   http://127.0.0.1:{port}/openapi.json")
    print("=" * 65)
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)
