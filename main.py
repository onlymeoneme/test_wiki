import os
import requests

# ==========================================
# НАСТРОЙКИ СТЕГАНОГРАФИИ (ТВОИ СТАНДАРТЫ)
# ==========================================
MAGIC_MARKER = b'__VTEAM_DATA__'
SEPARATOR = b'|||'
WIKI_API_URL = "https://commons.wikimedia.org/w/api.php"

# Данные авторизации Википедии (из Secrets твоего репозитория)
USERNAME = os.getenv("WIKI_USER")
PASSWORD = os.getenv("WIKI_PASS")

# Название, под которым файлы будут жить на Википедии.
# Можешь изменить префикс на любой другой, но номер (01-10) выставится автоматически.
WIKI_FILE_PREFIX = "Procedural_grunge_texture"

def main():
    if not USERNAME or not PASSWORD:
        print("[!] Ошибка: Не заданы переменные окружения WIKI_USER или WIKI_PASS")
        return

    # Инициализируем сессию requests
    session = requests.Session()
    session.headers.update({'User-Agent': 'VTeamBypassBot/1.0 (Contact via GitHub)'})

    try:
        # Шаг 1: Логин на Википедии (Получаем Login Token)
        r1 = session.get(url=WIKI_API_URL, params={"action": "query", "meta": "tokens", "type": "login", "format": "json"}).json()
        login_token = r1["query"]["tokens"]["logintoken"]

        # Шаг 2: Авторизация
        r2 = session.post(WIKI_API_URL, data={
            "action": "login",
            "lgname": USERNAME,
            "lgpassword": PASSWORD,
            "lgtoken": login_token,
            "format": "json"
        }).json()
        
        if r2["login"]["result"] != "Success":
            print(f"[!] Ошибка авторизации: {r2['login'].get('reason', 'Неизвестная ошибка')}")
            return
        print("[+] Авторизация на МедиаВики успешна.")

        # Шаг 3: Получаем CSRF-токен для последующей загрузки
        r3 = session.get(url=WIKI_API_URL, params={"action": "query", "meta": "tokens", "type": "csrf", "format": "json"}).json()
        csrf_token = r3["query"]["tokens"]["csrftoken"]

        # Шаг 4: Конвейер обработки 10 файлов
        for i in range(1, 11):
            config_url = f"https://raw.githubusercontent.com/capitainblack/freetm3/refs/heads/main/configs/sub_{i}.txt"
            local_image_path = f"templates/black_{i}.png"
            wiki_filename = f"{WIKI_FILE_PREFIX}_{i:02d}.png" # Имя на Вики: префикс_01.png, префикс_02.png...

            print(f"\n[*] Обработка пары №{i}...")
            
            # Проверяем, есть ли локальная картинка-шаблон
            if not os.path.exists(local_image_path):
                print(f"[!] Ошибка: Локальный шаблон {local_image_path} не найден! Пропуск.")
                continue

            # 4.1 Скачиваем свежий конфиг по ссылке
            try:
                config_resp = session.get(config_url, timeout=15)
                config_resp.raise_for_status()
                secret_bytes = config_resp.content.strip()
                print(f"[+] Скачан конфиг sub_{i}.txt ({len(secret_bytes)} байт)")
            except Exception as e:
                print(f"[!] Не удалось скачать конфиг с гитхаба: {e}. Пропуск.")
                continue

            # 4.2 Собираем payload по твоему методу
            secret_filename = f"sub_{i}.txt".encode('utf-8')
            payload = MAGIC_MARKER + secret_filename + SEPARATOR + secret_bytes

            # 4.3 Читаем картинку-донор
            with open(local_image_path, 'rb') as f:
                image_bytes = f.read()

            # Склеиваем оригинал и payload
            final_container_bytes = image_bytes + payload
            temp_output = "temp_stego_upload.png"

            with open(temp_output, 'wb') as f:
                f.write(final_container_bytes)

            # 4.4 Отправляем в API Википедии с перезаписью (ignorewarnings=1)
            print(f"[*] Загрузка {wiki_filename} на Викисклад...")
            with open(temp_output, 'rb') as file_data:
                upload_params = {
                    "action": "upload",
                    "filename": wiki_filename,
                    "token": csrf_token,
                    "ignorewarnings": "1",
                    "comment": "Daily assets revision and compression optimization.",
                    "format": "json"
                }
                r4 = session.post(WIKI_API_URL, files={"file": file_data}, data=upload_params).json()
                
                result = r4.get("upload", {}).get("result")
                if result == "Success":
                    print(f"[+] Успешно! Файл {wiki_filename} обновлен.")
                else:
                    print(f"[-] Ошибка загрузки {wiki_filename}. Ответ API: {r4}")

            # Удаляем временный файл
            if os.path.exists(temp_output):
                os.remove(temp_output)

    except Exception as e:
        print(f"[!] Критическая ошибка в работе скрипта: {e}")

if __name__ == "__main__":
    main()
