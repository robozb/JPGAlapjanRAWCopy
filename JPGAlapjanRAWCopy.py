import os
import shutil
import time

# Konfiguráció
jpg_dir = r'F:\\2024.06-OQS Orczy kert boulder\Pana1'
raw_dir = r'e:\\'
destination_subfolder = "raw"

def copy_file_with_progress(src, dst):
    """
    Egy fájl másolása forrásból célba, a másolási sebesség megjelenítésével.
    """
    buffer_size = 1024*1024  # Másoláshoz használt buffer mérete, 1MB.
    total_size = os.path.getsize(src)
    copied = 0
    start_time = time.time()

    with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
        while True:
            buf = fsrc.read(buffer_size)
            if not buf:
                break
            fdst.write(buf)
            copied += len(buf)
            elapsed_time = time.time() - start_time
            speed = copied / elapsed_time / (1024*1024)  # MB/s-ban.
            print(f"\rÁtmásoltuk: {copied}/{total_size} byte, Sebesség: {speed:.2f} MB/s", end='')

    print()  # Új sor a végén

def find_and_copy_raw_files(jpg_dir, raw_dir, destination_subfolder):
    try:
        raw_destination = os.path.join(jpg_dir, destination_subfolder)
        if not os.path.exists(raw_destination):
            os.makedirs(raw_destination)

        jpg_files = {}
        for file in os.listdir(jpg_dir):
            if file.lower().endswith('.jpg'):
                file_name_without_ext = os.path.splitext(file)[0]
                if file_name_without_ext in jpg_files:
                    raise ValueError(f"Duplikátum JPG fájl található: {file}")
                else:
                    jpg_files[file_name_without_ext] = file

        sorted_jpg_files = sorted(jpg_files.keys())
        total_jpg_count = len(sorted_jpg_files)  # A JPG fájlok teljes száma
        copied_files_count = 0
        processed_files_count = 0

        for jpg_file in sorted_jpg_files:
            for root, dirs, files in os.walk(raw_dir):
                for file in files:
                    if file.lower().endswith(('.raw', '.arw','.rw2')) and os.path.splitext(file)[0] == jpg_file:
                        source_file_path = os.path.join(root, file)
                        destination_file_path = os.path.join(raw_destination, file)
                        if not os.path.exists(destination_file_path):  # Ellenőrizzük, hogy a cél fájl létezik-e
                            print(f"\n\nFeldolgozott: {processed_files_count + 1}/ masolt: {copied_files_count + 1}/ total: {total_jpg_count}. Forrás JPG fájl: {jpg_file}.jpg, Átmásolásra kerülő RAW fájl: {file} ")
                            copy_file_with_progress(source_file_path, destination_file_path)
                            copied_files_count += 1
                        else:
                            print(f"A fájl már létezik: {destination_file_path}")
                        break
                        processed_files_count += 1

        print(f"A szkript sikeresen lefutott. Összesen {copied_files_count} RAW fájlt másoltunk át.")
    except Exception as e:
        print(f"Hiba történt: {e}")

# Futtatás
find_and_copy_raw_files(jpg_dir, raw_dir, destination_subfolder)
