import os
import shutil
import time
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import threading
import configparser

CONFIG_FILE = 'config.ini'

def copy_file(src, dst):
    buffer_size = 1024*1024  # 1MB buffer méret

    with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
        while True:
            buf = fsrc.read(buffer_size)
            if not buf:
                break
            fdst.write(buf)

def find_and_copy_raw_files(jpg_dir, raw_dir, destination_subfolder, text_widget):
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
        total_jpg_count = len(sorted_jpg_files)  # JPG fájlok száma
        copied_files_count = 0
        processed_files_count = 0

        for jpg_file in sorted_jpg_files:
            for root, dirs, files in os.walk(raw_dir):
                for file in files:
                    if file.lower().endswith(('.raw', '.arw','.rw2')) and os.path.splitext(file)[0] == jpg_file:
                        source_file_path = os.path.join(root, file)
                        destination_file_path = os.path.join(raw_destination, file)
                        if not os.path.exists(destination_file_path):  # Ellenőrzés, hogy létezik-e a fájl
                            text_widget.insert(tk.END, f"Totál: {total_jpg_count}; Átmásolt: {copied_files_count + 1}; Forrás JPG fájl: {jpg_file}.jpg, Átmásolásra kerülő RAW fájl: {file}\n")
                            text_widget.see(tk.END)
                            text_widget.update_idletasks()
                            text_widget.insert(tk.END, "Másolás folyamatban...\n")
                            text_widget.see(tk.END)
                            text_widget.update_idletasks()
                            copy_file(source_file_path, destination_file_path)
                            copied_files_count += 1
                            text_widget.insert(tk.END, "Másolás befejeződött\n\n")
                            text_widget.see(tk.END)
                            text_widget.update_idletasks()
                        else:
                            text_widget.insert(tk.END, f"A fájl már létezik: {destination_file_path}\n")
                        processed_files_count += 1
                        break

        text_widget.insert(tk.END, f"A szkript sikeresen lefutott. Összesen {copied_files_count} RAW fájlt másoltunk át.\n")
    except Exception as e:
        text_widget.insert(tk.END, f"Hiba történt: {e}\n")

# GUI létrehozása
def start_gui():
    def load_config():
        config = configparser.ConfigParser()
        if os.path.exists(CONFIG_FILE):
            config.read(CONFIG_FILE)
            if 'Settings' in config:
                jpg_dir.set(config['Settings'].get('jpg_dir', ''))
                raw_dir.set(config['Settings'].get('raw_dir', ''))
            if 'Window' in config:
                win_geometry = config['Window'].get('geometry', '')
                if win_geometry:
                    root.geometry(win_geometry)

    def save_config():
        config = configparser.ConfigParser()
        config['Settings'] = {
            'jpg_dir': jpg_dir.get(),
            'raw_dir': raw_dir.get()
        }
        config['Window'] = {
            'geometry': root.winfo_geometry()
        }
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)

    def select_jpg_dir():
        selected_dir = filedialog.askdirectory()
        if selected_dir:
            jpg_dir.set(selected_dir)

    def select_raw_dir():
        selected_dir = filedialog.askdirectory()
        if selected_dir:
            raw_dir.set(selected_dir)

    def open_jpg_dir():
        path = jpg_dir.get()
        if os.path.exists(path):
            if os.name == 'nt':
                os.startfile(path)
            else:
                os.system(f'xdg-open "{path}"')

    def open_raw_dir():
        path = raw_dir.get()
        if os.path.exists(path):
            if os.name == 'nt':
                os.startfile(path)
            else:
                os.system(f'xdg-open "{path}"')

    def start_copy():
        text_widget.delete(1.0, tk.END)
        copy_thread = threading.Thread(target=find_and_copy_raw_files, args=(jpg_dir.get(), raw_dir.get(), "raw", text_widget))
        copy_thread.start()

    root = tk.Tk()
    root.title("RAW Fájl Másoló")

    jpg_dir = tk.StringVar()
    raw_dir = tk.StringVar()

    tk.Label(root, text="JPG könyvtár:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
    tk.Entry(root, textvariable=jpg_dir, width=50).grid(row=0, column=1, padx=10, pady=10, sticky='we')
    tk.Button(root, text="Tallózás", command=select_jpg_dir).grid(row=0, column=2, padx=10, pady=10)
    tk.Button(root, text="Megnyitás", command=open_jpg_dir).grid(row=0, column=3, padx=10, pady=10)

    tk.Label(root, text="RAW könyvtár:").grid(row=1, column=0, padx=10, pady=10, sticky='w')
    tk.Entry(root, textvariable=raw_dir, width=50).grid(row=1, column=1, padx=10, pady=10, sticky='we')
    tk.Button(root, text="Tallózás", command=select_raw_dir).grid(row=1, column=2, padx=10, pady=10)
    tk.Button(root, text="Megnyitás", command=open_raw_dir).grid(row=1, column=3, padx=10, pady=10)

    tk.Button(root, text="Másolás indítása", command=start_copy).grid(row=2, column=0, columnspan=4, pady=20)

    text_widget = scrolledtext.ScrolledText(root, width=80, height=20)
    text_widget.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky='nsew')

    root.grid_columnconfigure(1, weight=1)
    root.grid_rowconfigure(3, weight=1)

    load_config()
    root.protocol("WM_DELETE_WINDOW", lambda: [save_config(), root.destroy()])
    root.mainloop()

# GUI indítása
start_gui()
