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

        # Шаг 4: Конвейер обработки первых 10 файлов (ОСТАЛСЯ БЕЗ ИЗМЕНЕНИЙ)
        for i in range(1, 11):
            config_url = f"https://raw.githubusercontent.com/capitainblack/freetm3/refs/heads/main/configs/sub_{i}.txt"
            local_image_path = f"templates/pic_{i}.jpg"
            wiki_filename = f"{WIKI_FILE_PREFIX}_{i:02d}.jpg" 

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

        # ==========================================
        # НОВОЕ: ОБРАБОТКА 11-Й КАРТИНКИ (TOR BRIDGES)
        # ==========================================
        print("\n[*] Обработка специальной картинки №11 (Tor Bridges)...")
        local_image_path_11 = "templates/pic_11.jpg"
        wiki_filename_11 = f"{WIKI_FILE_PREFIX}_11.jpg"

        if not os.path.exists(local_image_path_11):
            print(f"[!] Ошибка: Локальный шаблон {local_image_path_11} не найден! Пропуск 11-й картинки.")
        else:
            bridge_urls = [
                "https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridge/webtunnel.txt",
                "https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridge/vanilla.txt",
                "https://raw.githubusercontent.com/Delta-Kronecker/Tor-Bridges-Collector/refs/heads/main/bridge/obfs4.txt"
            ]
            
            combined_bridges_content = b""
            download_success = True

            # Скачиваем данные со всех трех ссылок и объединяем их
            for url in bridge_urls:
                try:
                    resp = session.get(url, timeout=15)
                    resp.raise_for_status()
                    # Если в буфере уже что-то есть, добавляем перенос строки перед новыми данными
                    if combined_bridges_content and resp.content:
                        combined_bridges_content += b"\n"
                    combined_bridges_content += resp.content.strip()
                    print(f"[+] Успешно скачан файл: {url.split('/')[-1]}")
                except Exception as e:
                    print(f"[!] Ошибка при скачивании {url}: {e}")
                    download_success = False
                    break

            if download_success and len(combined_bridges_content) > 0:
                # Формируем payload для 11-й картинки
                secret_filename_11 = b"bridges.txt"
                payload_11 = MAGIC_MARKER + secret_filename_11 + SEPARATOR + combined_bridges_content

                # Читаем картинку pic_11.jpg
                with open(local_image_path_11, 'rb') as f:
                    image_bytes_11 = f.read()

                # Склеиваем донор №11 и новые данные мостов
                final_container_bytes_11 = image_bytes_11 + payload_11
                temp_output_11 = "temp_stego_upload_11.png"

                with open(temp_output_11, 'wb') as f:
                    f.write(final_container_bytes_11)

                # Загружаем на Википедию
                print(f"[*] Загрузка {wiki_filename_11} (Bridges) на Викисклад...")
                with open(temp_output_11, 'rb') as file_data:
                    upload_params_11 = {
                        "action": "upload",
                        "filename": wiki_filename_11,
                        "token": csrf_token,
                        "ignorewarnings": "1",
                        "comment": "Daily assets revision and compression optimization.",
                        "format": "json"
                    }
                    r4_11 = session.post(WIKI_API_URL, files={"file": file_data}, data=upload_params_11).json()
                    
                    result_11 = r4_11.get("upload", {}).get("result")
                    if result_11 == "Success":
                        print(f"[+] Успешно! Файл {wiki_filename_11} обновлен.")
                    else:
                        print(f"[-] Ошибка загрузки {wiki_filename_11}. Ответ API: {r4_11}")

                # Удаляем временный файл
                if os.path.exists(temp_output_11):
                    os.remove(temp_output_11)
            else:
                print("[-] Пропуск 11-й картинки из-за ошибок скачивания или пустых данных мостов.")

    except Exception as e:
        print(f"[!] Критическая ошибка в работе скрипта: {e}")

if __name__ == "__main__":
    main()
