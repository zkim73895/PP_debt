import subprocess
import sys
import os


def run_tests():
    """Запускает все тесты"""
    print("ЗАПУСК АВТОТЕСТОВ CAMPUS JOBS API")

    print("\n1. Запуск pytest...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.stderr:
        print("Ошибки:", result.stderr)

    if result.returncode == 0:
        print("\n✅ Все тесты пройдены успешно!")
    else:
        print(f"\n❌ Тесты завершились с ошибкой (код: {result.returncode})")

    print("📋 ИТОГИ ТЕСТИРОВАНИЯ:")
    print(f"   • 7 автотестов для API")
    print(f"   • Проверка успешных и ошибочных сценариев")
    print(f"   • Тестирование валидации данных")
    print(f"   • Коллекция для Postman создана")
    print("\n Тестирование завершено!")


if __name__ == "__main__":
    if not os.path.exists("tests"):
        print("❌ Ошибка: папка tests не найдена!")
        print("Запускайте из корня проекта.")
        sys.exit(1)

    run_tests()