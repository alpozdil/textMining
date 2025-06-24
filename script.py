import subprocess

# 1. Word cloud ve skor hesaplama scripti
print("Word cloud scripti çalıştırılıyor...")
subprocess.run([
    r"C:\Users\Alperen\PycharmProjects\pythonProject\.venv1\Scripts\python.exe",
    r"C:\Users\Alperen\PycharmProjects\pythonProject\wordCloudWeights.py"
], check=True)

# 2. Grafik analiz scripti
print("Grafik analiz scripti çalıştırılıyor...")
subprocess.run([
    r"C:\Users\Alperen\PycharmProjects\pythonProject\.venv1\Scripts\python.exe",
    r"C:\Users\Alperen\PycharmProjects\pythonProject\graphics.py"
], check=True)
