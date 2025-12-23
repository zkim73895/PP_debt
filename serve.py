#!/usr/bin/env python3
"""
Простой сервер для разработки фронтенда
"""

import http.server
import socketserver
import os
import sys

PORT = 3000
FRONTEND_DIR = "frontend"


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def log_message(self, format, *args):
        # Убираем стандартное логирование
        pass


def serve_frontend():
    """Запуск отдельного сервера для фронтенда"""
    print(f"🌐 Запуск фронтенд сервера на http://localhost:{PORT}")
    print(f"📁 Обслуживаемая папка: {os.path.abspath(FRONTEND_DIR)}")
    print("\n📋 Доступные файлы:")

    # Показываем доступные файлы
    for file in os.listdir(FRONTEND_DIR):
        if file.endswith('.html'):
            print(f"   • http://localhost:{PORT}/{file}")

    print("\n⚡ Сервер запущен. Ctrl+C для остановки.")

    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Сервер остановлен")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Порт {PORT} уже занят. Используйте другой порт.")
        else:
            raise


if __name__ == "__main__":
    # Проверяем существование папки фронтенда
    if not os.path.exists(FRONTEND_DIR):
        print(f"❌ Папка '{FRONTEND_DIR}' не найдена!")
        print("Создайте папку frontend и добавьте туда HTML файлы.")
        sys.exit(1)

    serve_frontend()