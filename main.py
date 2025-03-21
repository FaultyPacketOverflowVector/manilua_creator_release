import os
import re
import shutil
import requests
import socket
import customtkinter as ctk
from tkinter import filedialog, messagebox
import urllib.request
from tkinter import Text
import sys
import webbrowser
from pathlib import Path
import time
import threading
import zipfile
import ctypes
import winreg, string
import zlib
import random
import struct
from tkinter import PhotoImage
main_version = '3.2.0.4'
base_path = Path(__file__).parent
datas = [(str(base_path / 'ico'), 'ico')]

def anti_debug() -> None:
    if ctypes.windll.kernel32.IsDebuggerPresent()!= 0:
        sys.exit()
anti_debug()

def detect_vm():
    vm_files = ['/proc/scsi/scsi', '/system/lib/libc_malloc_debug_qemu.so']
    for file in vm_files:
        if os.path.exists(file):
            sys.exit()
detect_vm()

def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.abspath('.')
BASE_PATH = get_base_path()
icon_path = os.path.join(BASE_PATH, 'ico', 'steam_green.ico')

def log_message(console, message):
    console.config(state=ctk.NORMAL)
    console.insert(ctk.END, message + '\n')
    console.config(state=ctk.DISABLED)
    console.yview(ctk.END)

def check_internet_connection():
    try:
        urllib.request.urlopen('http://www.google.com', timeout=5)
        return True
    except (urllib.request.URLError, socket.timeout):
        return False
    else:  # inserted
        pass

def select_folder(title='Select Folder'):
    return filedialog.askdirectory(title=title)

def select_input_file(file_name):
    return filedialog.askopenfilename(title=f'Select {file_name} file', filetypes=[('Text files', '*.txt')])

def get_latest_manifest_files(manifest_folder):
    manifest_map = {}
    manifest_files = [f for f in os.listdir(manifest_folder) if f.endswith('.manifest')]
    for manifest_file in manifest_files:
        if '_' in manifest_file:
            key_id = manifest_file.split('_', 1)[0]
            file_path = os.path.join(manifest_folder, manifest_file)
            if key_id not in manifest_map or os.path.getmtime(file_path) > os.path.getmtime(manifest_map[key_id]):
                if key_id in manifest_map:
                    os.remove(manifest_map[key_id])
                manifest_map[key_id] = file_path
    return manifest_map

def delete_unused_manifest_files(console, manifest_folder, used_manifest_codes):
    try:
        manifest_files = [f for f in os.listdir(manifest_folder) for manifest_files in [f for f in os.listdir(manifest_folder) for manifest_file in manifest_files if '_' in manifest_file and manifest_file.split('_', 1)[1].replace('.manifest', '') and os.remove(os.path.join(manifest_folder, manifest_file)) and log_message(console, f'Deleted unused manifest file: {manifest_file}') and (not <Code311 code object create_steam_location_file at 0x7f03125bcc50, file main.py>, line 663.<Code311 code object Downloader at 0x7f03125bce90, file main.py>, line 668(<mask_23>, <Code311 code object fetch_manilua_update_link at 0x7f03125bf150, file main.py>, line 781))]]
    except Exception as e:
        log_message(console, f'Error deleting manifest files: {e}')

class CodeFileProcessor:
    def __init__(self, console, code_file_path, output_folder, app_id, manifest_map):
        self.console = console
        self.code_file_path = code_file_path
        self.output_folder = output_folder
        self.app_id = app_id
        self.manifest_map = manifest_map
        self.output_lines = [f'addappid({app_id})']
        self.used_manifest_codes = set()
        self.dlc_ids = []
        self.game_name = 'Unknown Game'

    def process(self):
        try:
            self._read_input_file()
            self._process_lines()
            self._fetch_additional_dlcs()
            self._add_dlc_info()
            self._add_metadata()
            self._write_output_file()
            return self._get_result()
        except Exception as e:
            log_message(self.console, f'Error creating Lua file: {e}')
            return (None, None) + (None, e) * e

    def _read_input_file(self):
        with open(self.code_file_path, 'r') as input_file:
            self.lines = input_file.readlines()

    def _process_lines(self):
        for line in self.lines:
            line = line.strip()
            if ';' in line:
                self._process_key_line(line)
            else:  # inserted
                log_message(self.console, f'Skipping invalid line: {line}')

    def _process_key_line(self, line):
        try:
            [item.strip() for item in line.split(';')]
        except Exception as e:
            log_message(self.console, f'Error processing line \'{line}\': {e}')

    def _add_manifest_info(self, key_id, key_code, manifest_file_path):
        manifest_code = os.path.basename(manifest_file_path).split('_', 1)[1].replace('.manifest', '')
        self.output_lines.append(f'addappid({key_id}, 1, \"{key_code}\")')
        self.output_lines.append(f'setManifestid({key_id}, \"{manifest_code}\", 0)')
        self.used_manifest_codes.add(manifest_code)
        log_message(self.console, f'Processed Key_ID: {key_id} with manifest {manifest_code}')

    def _fetch_additional_dlcs(self):
        self.dlc_ids = [line.split(';')[0] for line in self.lines if ';' in line and line.strip()]
        if self.app_id in self.dlc_ids:
            self.dlc_ids.remove(self.app_id)
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
            url = f'https://store.steampowered.com/api/appdetails?appids={self.app_id}&cc=us&l=en'
            response = requests.get(url, headers=headers)
            data = response.json()
            if str(self.app_id) in data and data[str(self.app_id)]['success']:
                api_dlcs = data[str(self.app_id)]['data'].get('dlc', [])
                self.game_name = ''.join((char for char in data[str(self.app_id)]['data']['name'] if char.isalnum() or char.isspace()))
            else:  # inserted
                api_dlcs = []
            if not api_dlcs:
                url2 = f'https://steamdb.info/app/{self.app_id}/'
                r2 = requests.get(url2, headers=headers)
                html = r2.text
                found = set(re.findall('/app/(\\d+)/', html))
                found.discard(str(self.app_id))
                api_dlcs = list(found)
            self.dlc_ids.extend([str(dlc_id) for dlc_id in api_dlcs if str(dlc_id) not in self.dlc_ids])
        except Exception as e:
            log_message(self.console, f'Error fetching additional DLCs: {e}')

    def _add_dlc_info(self):
        self.output_lines.append('\n-- DLC IDs found:')
        dlc_found = False
        for dlc_id in self.dlc_ids:
            if self._add_single_dlc_info(dlc_id):
                dlc_found = True
        if not dlc_found:
            self.output_lines.append(f'-- No DLC IDs found for {self.game_name}')

    def _add_single_dlc_info(self, dlc_id):
        try:
            dlc_url = f'https://store.steampowered.com/api/appdetails?appids={dlc_id}&cc=us&l=en'
            dlc_response = requests.get(dlc_url, headers={'User-Agent': 'Mozilla/5.0'})
            dlc_data = dlc_response.json()
            if dlc_data and str(dlc_id) in dlc_data and dlc_data[str(dlc_id)]['success']:
                dlc_name = ''.join((char for char in dlc_data[str(dlc_id)]['data']['name'] if char.isalnum() or char.isspace()))
                self.output_lines.append(f'addappid({dlc_id}) -- {dlc_name}')
                return True
        except Exception as e:
            pass  # postinserted
        else:  # inserted
            pass  # postinserted
        return False
            log_message(self.console, f'Error fetching DLC info for {dlc_id}: {e}')
            return False
        else:  # inserted
            pass

    def _add_metadata(self):
        def discord_link():
            url = 'https://toxichome-whoami.github.io/manilua_creator_release/info.json'
            try:
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                return data.get('dicord_link', [{}])[0].get('join_link')
            except requests.exceptions.RequestException as e:
                messagebox.showerror('Error', f'Failed to fetch Download link.\n{e}')
                return None
            else:  # inserted
                pass
        self.output_lines.append(f'\n-- Generated By [Manilua Creator v{main_version}] : Game_name = ({self.game_name})')
        self.output_lines.append(f'-- Join our discord server [Toxic Home]: {discord_link()}')

    def _write_output_file(self):
        output_file_path = os.path.join(self.output_folder, f'{self.app_id}.lua')
        with open(output_file_path, 'w') as output_file:
            output_file.write('\n'.join(self.output_lines))
        log_message(self.console, f'Lua file created at: {output_file_path}')

    def _get_result(self):
        return (os.path.join(self.output_folder, f'{self.app_id}.lua'), self.used_manifest_codes)

def create_lua_file(console, app_id, manifest_folder, code_file, output_folder):
    try:
        app_id = ctk.CTk()
        app_id.geometry('300x100')
        app_id.title('Creating Lua File')
        app_id.resizable(False, False)
        if os.path.exists(icon_path):
            pass  # postinserted
    except Exception as e:
        else:  # inserted
            try:
                app_id.iconbitmap(icon_path)
            except Exception as icon_error:
                pass  # postinserted
    else:  # inserted
        code_file = ctk.CTkLabel(app_id, text='Processing...', text_color='white', font=('Segoe UI Normal', 12))
        code_file.pack(pady=(15, 0))
        console = ctk.CTkProgressBar(app_id, width=250, progress_color='#0093b3')
        console.pack(pady=10)
        console.set(0)

        def smooth_progress(start, end, duration=0.5):
            steps = 50
            step_time = duration / steps
            diff = end - start
            for i in range(steps + 1):
                t = i / steps
                t = t * t * (3 - 2 * t)
                current = start + diff * t
                progress_bar.set(current)
                progress_window.update()
                time.sleep(step_time)

        def process_file():
            try:
                manifest_map = get_latest_manifest_files(manifest_folder)
                status_label.configure(text='Getting manifest files...')
                smooth_progress(0, 0.2)
                processor = CodeFileProcessor(console, code_file, output_folder, app_id, manifest_map)
                status_label.configure(text='Processing code file...')
                smooth_progress(0.2, 0.4)
                lua_file_path, used_manifest_codes = processor.process()
                status_label.configure(text='Creating Lua file...')
                smooth_progress(0.4, 0.6)
                if not lua_file_path:
                    log_message(console, 'Error processing the input file. Exiting.')
                    progress_window.destroy()
                    return
                log_message(console, '\n')
                delete_unused_manifest_files(console, manifest_folder, used_manifest_codes)
                status_label.configure(text='Cleaning up...')
                smooth_progress(0.6, 0.8)
            except Exception as e:
                pass  # postinserted
            else:  # inserted
                try:
                    os.remove(code_file)
                    log_message(console, f'Successfully deleted code.txt file: {os.path.basename(code_file)}')
                except Exception as e:
                    pass  # postinserted
                else:  # inserted
                    status_label.configure(text='Complete!')
                    smooth_progress(0.8, 1.0)
                    progress_window.after(1000, progress_window.destroy)
                    messagebox.showinfo('Success', f'Lua file created at: {lua_file_path}')
                    log_message(console, f'Error deleting code.txt file: {e}')
                    log_message(console, f'Unexpected error occurred: {e}')
                    progress_window.destroy()
        threading.Thread(target=process_file, daemon=True).start()
        app_id.mainloop()
                log_message(console, f'Failed to set icon for progress window: {icon_error}')
                log_message(console, f'Unexpected error occurred: {e}')

class ManifestGrabber:
    def __init__(self, console):
        self.console = console
        self.steam_location_file = 'steam_location.txt'
        self.steam_location = ''
        self.app_id = ''
        self.destination_folder = ''
        self.depot_ids = set()
        self.library_folders = set()

    def grab_manifest_files(self):
        if not self._check_steam_location():
            return
        if not self._get_app_id():
            return
        self._create_destination_folder()
        self._get_library_folders()
        self._process_manifest_files()
        self._process_depotcache()
        self._copy_achievement_and_stats_files()
        self._create_code_txt()
        if not self.depot_ids:
            log_message(self.console, 'No depot IDs found.')
            messagebox.showwarning('Warning', 'No depot IDs found for this APP ID.')
        log_message(self.console, '\nOperation completed.')

    def _check_steam_location(self):
        if not os.path.exists(self.steam_location_file):
            log_message(self.console, f'{self.steam_location_file} not found. Exiting.')
            messagebox.showerror('Error', f'Create {self.steam_location_file} first to start the process. Exiting.')
            return False
        with open(self.steam_location_file, 'r') as file:
            self.steam_location = file.read().strip()
            return True
            return True

    def _get_app_id(self):
        self.app_id = app_id_entry.get().strip()
        if not self.app_id.isdigit():
            log_message(self.console, 'Please enter a valid APP ID.')
            messagebox.showerror('Error', 'Please enter a valid APP ID.')
            return False
        return True

    def _create_destination_folder(self):
        self.destination_folder = os.path.join(select_folder(title='Select Destination Folder'), self.app_id)
        os.makedirs(self.destination_folder, exist_ok=True)
        log_message(self.console, f'Created folder: {self.destination_folder}')

    def _get_library_folders(self):
        self.library_folders.add(Path(self.steam_location) / 'steamapps')
        vdf_paths = [Path(self.steam_location) / 'steamapps' / 'libraryfolders.vdf', Path(self.steam_location) / 'config' / 'libraryfolders.vdf']
        for vdf_path in vdf_paths:
            if not vdf_path.exists():
                continue
            try:
                with vdf_path.open('r', encoding='utf-8') as f:
                    pass  # postinserted
            except Exception as e:
                    content = f.read()
                    blocks = re.findall('\"\\d+\"\\s*{(.*?)}', content, re.DOTALL)
                    for block in blocks:
                        m = re.search('\"path\"\\s*\"([^\"]+)\"', block)
                        if m:
                            self.library_folders.add(Path(m.group(1)) / 'steamapps')
            log_message(self.console, f'Error reading library folders VDF: {e}')

    def _process_manifest_files(self):
        manifest_found = False
        for library in self.library_folders:
            manifest_file = library / f'appmanifest_{self.app_id}.acf'
            if not manifest_file.exists():
                continue
            manifest_found = True
            try:
                with manifest_file.open('r', encoding='utf-8') as f:
                    pass  # postinserted
            except Exception as e:
                    content = f.read()
                    depot_matches = re.finditer('\"depots\"\\s*{([^}]*)}', content, re.DOTALL)
                    for match in depot_matches:
                        depot_block = match.group(1)
                        depot_ids = re.findall('\"(\\d+)\"\\s*{', depot_block)
                        self.depot_ids.update(depot_ids)

                    def extract_block(text, keyword):
                        pattern = re.compile(f'\"{keyword}\"\\s*{')
                        match = pattern.search(text)
                        if not match:
                            return ''
                        start = match.end()
                        depth = 1
                        i = start
                        while i < len(text) and depth:
                            if text[i] == '{':
                                depth += 1
                            else:  # inserted
                                if text[i] == '}':
                                    depth -= 1
                            i += 1
                        return text[start:i - 1]
                    dlc_block = extract_block(content, 'DlcDownloads')
                    if dlc_block:
                        dlc_ids = re.findall('\"(\\d+)\"\\s*{', dlc_block)
                        self.depot_ids.update(dlc_ids)
                    depot_block = extract_block(content, 'depotcontent')
                    if depot_block:
                        depot_ids = re.findall('\"(\\d+)\"\\s*{', depot_block)
                        self.depot_ids.update(depot_ids)
                        app_id_len = len(self.app_id)
                        base_prefix = ''
                        range_size = 0
                        if app_id_len == 4:
                            base_prefix = self.app_id[:2]
                            range_size = 100
                        else:  # inserted
                            if app_id_len == 5:
                                base_prefix = self.app_id[:2]
                                range_size = 1000
                            else:  # inserted
                                if app_id_len == 6:
                                    base_prefix = self.app_id[:3]
                                    range_size = 1000
                                else:  # inserted
                                    if app_id_len >= 7:
                                        base_prefix = self.app_id[:4]
                                        range_size = 1000
                        if base_prefix and range_size:
                            for i in range(range_size):
                                if app_id_len == 4:
                                    candidate = f'{base_prefix}{i:02d}'
                                else:  # inserted
                                    candidate = f'{base_prefix}{i:03d}'
                                if candidate!= self.app_id:
                                    self.depot_ids.add(candidate)
        else:  # inserted
            if not manifest_found:
                log_message(self.console, 'No manifest file found in Steam libraries. Please select game installation folder manually.')
                game_folder = select_folder('Select Game Installation Folder')
                if game_folder:
                    manifest_file = Path(game_folder) / 'steam_appid.txt'
                    if manifest_file.exists():
                        try:
                            with manifest_file.open('r') as f:
                                content = f.read().strip()
                                if content == self.app_id:
                                    log_message(self.console, 'Found matching game folder')
                                    self.depot_ids.add(self.app_id)
                                    base_val = int(self.app_id)
                                    for offset in range(1, 10):
                                        self.depot_ids.add(str(base_val + offset))
                                else:  # inserted
                                    log_message(self.console, 'Selected folder does not match the APP ID')
                    else:  # inserted
                        log_message(self.console, 'No steam_appid.txt found in selected folder')
                else:  # inserted
                    log_message(self.console, 'No folder selected')
            log_message(self.console, f'Error processing manifest file: {e}')

    def _process_depotcache(self):
        depotcache_path = Path(self.steam_location) / 'depotcache'
        if depotcache_path.exists():
            for manifest in os.listdir(depotcache_path):
                if not manifest.endswith('.manifest'):
                    continue
                depot_id = manifest.split('_')[0]
                if depot_id in self.depot_ids or depot_id == self.app_id:
                    source = depotcache_path / manifest
                    destination = Path(self.destination_folder) / manifest
                    try:
                        shutil.copy2(source, destination)
                        log_message(self.console, f'Copied manifest: {manifest}')
                    except Exception as e:
                        pass  # postinserted
            log_message(self.console, f'Error copying manifest {manifest}: {e}')

    def _copy_achievement_and_stats_files(self):
        paths_to_check = [(Path(self.steam_location) / 'appcache' / 'stats', ['bin', 'stats.bin', 'lstats.bin']), (Path(self.steam_location) / 'appcache' / 'achievements', ['bin'])]
        for base_path, extensions in paths_to_check:
            if not base_path.exists():
                continue
            for ext in extensions:
                filename = f'{self.app_id}.{ext}'
                source = base_path / filename
                if source.exists():
                    try:
                        shutil.copy2(source, Path(self.destination_folder) / filename)
                        log_message(self.console, f'Copied {filename}')
                    except Exception as e:
                        pass  # postinserted
            log_message(self.console, f'Error copying {filename}: {e}')

    def _create_code_txt(self):
        config_path = Path(self.steam_location) / 'config' / 'config.vdf'
        if not config_path.exists():
            log_message(self.console, 'Config.vdf not found. Skipping code.txt creation.')
            return
        try:
            with config_path.open('r', encoding='utf-8') as f:
                pass  # postinserted
        except Exception as e:
                config_content = f.read()
                    output_lines = []
                    for manifest in os.listdir(self.destination_folder):
                        if manifest.endswith('.manifest'):
                            depot_id = manifest.split('_')[0]
                            pattern = f'\"{depot_id}\"\\s*\\{\\s*\"DecryptionKey\"\\s*\"([a-f0-9]+)\"'
                            match = re.search(pattern, config_content)
                            if match:
                                pass  # postinserted
                            else:  # inserted
                                decryption_key = match.group(1)
                                output_lines.append(f'{depot_id};{decryption_key}')
                                log_message(self.console, f'Found key for depot {depot_id}')
                    else:  # inserted
                        if output_lines:
                            output_path = Path(self.destination_folder) / 'code.txt'
                            with output_path.open('w', encoding='utf-8') as f:
                                f.write('\n'.join(output_lines))
                                    log_message(self.console, 'Created code.txt with decryption keys')
                        else:  # inserted
                            log_message(self.console, 'No decryption keys found')
                log_message(self.console, f'Error creating code.txt: {e}')

def grab_manifest_files(console):
    grabber = ManifestGrabber(console)
    try:
        grabber.grab_manifest_files()
    except Exception as e:
        log_message(console, f'Error during operation: {e}')
        messagebox.showerror('Error', f'An error occurred: {e}')
        return None
    else:  # inserted
        pass

class SteamLocationDetector:
    def __init__(self, console):
        self.console = console
        self.file_path = os.path.join(os.path.dirname(sys.argv[0]), 'steam_location.txt')
        self.steam_path = None

    def detect_and_save(self):
        self._detect_steam_path()
        if self.steam_path:
            self._save_steam_path()
        else:  # inserted
            self._handle_manual_selection()

    def _detect_steam_path(self):
        self._try_registry()
        if not self.steam_path:
            self._try_common_paths()

    def _try_registry(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\WOW6432Node\\Valve\\Steam')
            self.steam_path = winreg.QueryValueEx(key, 'InstallPath')[0]
            winreg.CloseKey(key)
        except:
            return

    def _try_common_paths(self):
        possible_paths = ['C:\\Program Files (x86)\\Steam', 'C:\\Program Files\\Steam', 'D:\\Program Files (x86)\\Steam', 'D:\\Steam', os.path.join(os.getenv('ProgramFiles(x86)', ''), 'Steam'), os.path.join(os.getenv('ProgramFiles', ''), 'Steam')]
        for path in possible_paths:
            if os.path.exists(path) and os.path.exists(os.path.join(path, 'steam.exe')):
                self.steam_path = path
                break

    def _save_steam_path(self):
        try:
            with open(self.file_path, 'w') as file:
                pass  # postinserted
        except Exception as e:
                file.write(self.steam_path)
                    messagebox.showinfo('Success', f'Steam location automatically detected at: {self.steam_path}')
                    log_message(self.console, f'Steam location automatically detected at: {self.steam_path}')
                messagebox.showerror('Error', f'Error saving Steam location: {e}')
                log_message(self.console, f'Error saving Steam location: {e}')

    def _handle_manual_selection(self):
        messagebox.showerror('Error', 'Unable to automatically detect Steam location. Please select manually.')
        log_message(self.console, 'Unable to automatically detect Steam location. Please select manually.')
        try:
            location = filedialog.askdirectory(title='Select Steam Installation Folder')
            if location:
                with open(self.file_path, 'w') as file:
                    pass  # postinserted
        except Exception as e:
                    file.write(location)
                        messagebox.showinfo('Success', 'Steam location saved successfully.')
                        log_message(self.console, 'Steam location saved successfully.')
            else:  # inserted
                messagebox.showwarning('No Selection', 'No location selected. Steam location remains unchanged.')
                log_message(self.console, 'No location selected. Steam location remains unchanged.')
                messagebox.showerror('Error', f'An error occurred while trying to save the Steam location: {e}')
                log_message(self.console, f'Error saving Steam location: {e}')

def create_steam_location_file(console):
    detector = SteamLocationDetector(console)
    detector.detect_and_save()

class Downloader:
    def __init__(self):
        self.download_speed = '0 KB/s'
        self.download_complete = False
        self.stop_download = False
        self.download_thread = None

    def download_file(self, url, file_name, output_folder, progress_bar, speed_label, app):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            start_time = time.time()
            if not os.path.exists(output_folder):
                os.makedirs(output_folder, exist_ok=True)
            file_path = os.path.join(output_folder, file_name)
            with open(file_path, 'wb') as file:
                pass  # postinserted
        except Exception as e:
                for chunk in response.iter_content(chunk_size=8192):
                    if self.stop_download:
                        break
                    file.write(chunk)
                    downloaded_size += len(chunk)
                    elapsed_time = time.time() - start_time
                    current_speed = downloaded_size / (max(elapsed_time, 1e-09) * 1024)
                    self.download_speed = f'{current_speed:.2f} KB/s'
                    progress = downloaded_size / total_size * 100 if total_size > 0 else 0
                    progress_bar.set(progress / 100)
                    speed_label.configure(text=f'Speed: {self.download_speed}')
                    app.update()
                    if not self.stop_download:
                        self.download_complete = True
                        if not file_name.endswith('.zip'):
                            messagebox.showinfo('Success', 'Download completed!')
                        else:  # inserted
                            if file_name == 'Manilua_Creator.zip':
                                self.unzip_file(file_path, app, output_folder)
                    else:  # inserted
                        os.remove(file_path)
                        messagebox.showinfo('Cancelled', 'Download cancelled and file deleted.')
                messagebox.showerror('Error', f'An error occurred: {e}')
                if os.path.exists(file_path):
                    os.remove(file_path)

    def unzip_file(self, zip_path, app, output_folder):
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                pass  # postinserted
        except Exception as e:
                zip_ref.extractall(output_folder)
                    os.remove(zip_path)
                    app.quit()
                messagebox.showerror('Error', f'Failed to unzip file: {e}')
                return None

    def on_closing(self, app, file_name, output_folder):
        self.stop_download = True
        if self.download_thread and self.download_thread.is_alive():
            app.after(500, lambda: self.on_closing(app, file_name, output_folder))
            return
        file_path = os.path.join(output_folder, file_name)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except PermissionError:
            pass  # postinserted
        else:  # inserted
            app.destroy()
            pass
        else:  # inserted
            pass

    def start_download(self, url, file_name, output_folder):
        self.download_speed = '0 KB/s'
        self.download_complete = False
        self.stop_download = False
        self = ctk.CTk()
        self.geometry('300x100')
        popup_window_icon = icon_path
        if os.path.exists(popup_window_icon):
            try:
                self.iconbitmap(popup_window_icon)
            except Exception as e:
                pass  # postinserted
        else:  # inserted
            messagebox.showerror('Error', f'Icon file not found: {popup_window_icon}')
        self.resizable(False, False)
        self.title('Downloader')
        speed_label = ctk.CTkLabel(self, text='Speed: 0 KB/s')
        speed_label.pack(pady=(15, 0))
        progress_bar = ctk.CTkProgressBar(self, width=250, progress_color='#0093b3')
        progress_bar.pack(pady=10)
        progress_bar.set(0)

        def check_download_complete():
            if self.download_complete:
                app.quit()
            else:  # inserted
                app.after(100, check_download_complete)
        self.download_thread = threading.Thread(target=self.download_file, args=(url, file_name, output_folder, progress_bar, speed_label, self))
        self.download_thread.start()
        self.protocol('WM_DELETE_WINDOW', lambda: self.on_closing(app, file_name, output_folder))
        self.after(100, file_name)
        self.mainloop()
            messagebox.showerror('Error', f'Error loading icon: {e}')

def fetch_manilua_update_link():
    url = 'https://toxichome-whoami.github.io/manilua_creator_release/info.json'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('links', [{}])[0].get('manilua_update_link')
    except requests.exceptions.RequestException as e:
        messagebox.showerror('Error', f'Failed to fetch Download link.\n{e}')
        return None
    else:  # inserted
        pass

def download_updated_version():
    download_url = fetch_manilua_update_link()
    if download_url:
        output_folder = select_folder(title='Select a folder to save the file')
        if output_folder:
            file_name = download_url.split('/')[(-1)]
            downloader = Downloader()
            downloader.start_download(download_url, file_name, output_folder)
        else:  # inserted
            messagebox.showinfo('Info', 'Download cancelled because no output folder was selected.')

class FolderZipper:
    def __init__(self, console):
        self.console = console

    def zip_folder(self, folder_path, zip_path):
        """\n        Zips the contents of a folder into a zip file.\n        """  # inserted
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, start=folder_path)
                    zipf.write(file_path, arcname)

    def delete_folder_zip(self, folder_path):
        """\n        Deletes a folder and its contents.\n        """  # inserted
        try:
            shutil.rmtree(folder_path)
            log_message(self.console, f'Deleted: {folder_path}')
        except Exception as e:
            log_message(self.console, f'Error deleting {folder_path}: {e}')

    def select_folder_to_zip(self):
        """\n        Opens a folder selection dialog and processes the selected folder.\n        """  # inserted
        selected_folder = ctk.filedialog.askdirectory(title='Select a folder to zip')
        if not selected_folder:
            messagebox.showinfo('Info', 'No folder selected. Exiting...')
            return
        subfolders = [f.path for f in os.scandir(selected_folder) if f.is_dir()]
        successfully_zipped = []
        skipped_folders = []
        if not subfolders:
            self._process_single_folder(selected_folder)
        else:  # inserted
            self._process_multiple_folders(subfolders, successfully_zipped, skipped_folders)

    def _process_single_folder(self, folder):
        contains_lua = any((f.endswith('.lua') for f in os.listdir(folder)))
        contains_manifest = any((f.endswith('.manifest') for f in os.listdir(folder)))
        contains_st = any((f.endswith('.st') for f in os.listdir(folder)))
        if (contains_lua or contains_st) and contains_manifest:
            zip_path = f'{folder}.zip'
            if os.path.exists(zip_path):
                confirm = messagebox.askyesno('Confirmation', f'Zip file already exists: {zip_path}. Do you want to delete it?')
                if confirm:
                    os.remove(zip_path)
                    self.zip_folder(folder, zip_path)
                    messagebox.showinfo('Success', f'Zipped: {folder}')
                    confirm_delete = messagebox.askyesno('Confirmation', f'Do you want to delete the folder \'{folder}\'?')
                    if confirm_delete:
                        self.delete_folder_zip(folder)
                        log_message(self.console, 'Main folder deleted.')
                    else:  # inserted
                        log_message(self.console, 'Main folder was not deleted.')
            else:  # inserted
                self.zip_folder(folder, zip_path)
                messagebox.showinfo('Success', f'Zipped: {folder}')
                confirm = messagebox.askyesno('Confirmation', f'Do you want to delete the folder \'{folder}\'?')
                if confirm:
                    self.delete_folder_zip(folder)
                    log_message(self.console, 'Main folder deleted.')
                else:  # inserted
                    log_message(self.console, 'Main folder was not deleted.')
        else:  # inserted
            messagebox.showinfo('Info', 'The folder must contain both .lua or .st and .manifest files. Exiting...')

    def _process_multiple_folders(self, subfolders, successfully_zipped, skipped_folders):
        for folder in subfolders:
            contains_lua = any((f.endswith('.lua') for f in os.listdir(folder)))
            contains_manifest = any((f.endswith('.manifest') for f in os.listdir(folder)))
            if contains_lua and contains_manifest:
                zip_path = f'{folder}.zip'
                if os.path.exists(zip_path):
                    log_message(self.console, f'Zip file already exists: {zip_path}')
                else:  # inserted
                    self.zip_folder(folder, zip_path)
                    successfully_zipped.append(folder)
                    log_message(self.console, f'Zipped: {folder}')
            else:  # inserted
                skipped_folders.append(folder)
                log_message(self.console, f'Skipping folder without both .lua and .manifest files: {folder}')
        if skipped_folders:
            log_message(self.console, f"Some folders did not contain .lua and .manifest files and were skipped: {', '.join(skipped_folders)}")
        if successfully_zipped:
            confirm = messagebox.askyesno('Confirmation', 'Do you want to delete only the successfully zipped subfolders?')
            if confirm:
                for folder in successfully_zipped:
                    self.delete_folder_zip(folder)
                log_message(self.console, 'Successfully zipped subfolders deleted.')
            else:  # inserted
                log_message(self.console, 'Subfolders were not deleted.')

class LuaStConverter:
    def __init__(self):
        self.selected_path = filedialog.askopenfilename(title='Select a .st or .lua file', filetypes=[('ST and Lua files', '*.st *.lua')])
        if self.selected_path:
            self.process_file(self.selected_path)

    def process_file(self, file_path):
        self.file_path = file_path
        self.folder = os.path.dirname(file_path)
        self.file_name = os.path.basename(file_path)
        self.app_id = self._extract_app_id(self.file_name)
        if not self.app_id:
            messagebox.showerror('Error', f'Filename does not contain a valid APP ID: {self.file_name}')
            return
        if file_path.lower().endswith('.st'):
            self._st_to_lua()
        else:  # inserted
            if file_path.lower().endswith('.lua'):
                self._lua_to_st()
            else:  # inserted
                messagebox.showerror('Error', 'Unsupported file type.')
                return
        messagebox.showinfo('Success', f'Conversion completed for: {self.file_name}')
        self._ask_delete_original()

    def _extract_app_id(self, filename):
        base = os.path.splitext(os.path.basename(filename))[0]
        return base if base.isdigit() else None

    def _ask_delete_original(self):
        delete_original = messagebox.askyesno('Delete Original', f'Do you want to delete the original file?\n{self.file_path}')
        if delete_original:
            try:
                os.remove(self.file_path)
            except Exception as e:
                pass  # postinserted
            messagebox.showerror('Error', f'Failed to delete original file:\n{e}')
        else:  # inserted
            pass

    def _st_to_lua(self):
        try:
            with open(self.file_path, 'rb') as f:
                pass  # postinserted
        except Exception as e:
                content = f.read()
                    if len(content) < 12:
                        messagebox.showerror('Error', 'ST file too small.')
                        return
                    raw_xor, size = struct.unpack('<II', content[:8])
                    xorkey = (raw_xor ^ 4294878408) & 255
                    data = bytearray(content[12:])
                    for i in range(size):
                        if i < len(data):
                            pass  # postinserted
                        else:  # inserted
                            data[i] ^= xorkey
                    decompressed = zlib.decompress(bytes(data))
                    lua_data = decompressed[512:]
                    lua_content = lua_data.decode('utf-8', errors='ignore').strip()
                    output_path = os.path.join(self.folder, f'{self.app_id}.lua')
                    with open(output_path, 'w', encoding='utf-8') as out_file:
                        out_file.write(lua_content)
                messagebox.showerror('Error', f'Failed to convert ST to Lua:\n{e}')

    def _lua_to_st(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                pass  # postinserted
        except Exception as e:
                lua_content = f.read()
                    padded_data = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' + lua_content.encode('utf-8')
                    compressed = zlib.compress(padded_data)
                    xorkey = random.randint(0, 255)
                    size = len(compressed)
                    header = struct.pack('<II', xorkey ^ 4294878408, size)
                    data = bytearray(compressed)
                    for i in range(size):
                        data[i] ^= xorkey
                    output_path = os.path.join(self.folder, f'{self.app_id}.st')
                    with open(output_path, 'wb') as out_file:
                        out_file.write(header + b'\x00\x00\x00\x00' + data)
                messagebox.showerror('Error', f'Failed to convert Lua to ST:\n{e}')
            else:  # inserted
                pass

def main():
    global app_id_entry  # inserted
    root = ctk.CTk()
    root.title('Manilua Creator')
    root.resizable(False, False)
    root.geometry('365x680')
    root._set_appearance_mode('dark')
    root.configure(fg_color='#232323')
    main_icon_path = icon_path
    if os.path.exists(main_icon_path):
        try:
            root.iconbitmap(main_icon_path)
        except Exception as e:
            pass  # postinserted
    else:  # inserted
        messagebox.showerror('Error', f'Icon file not found: {main_icon_path}')
    if not check_internet_connection():
        messagebox.showerror('No Internet', 'No internet connection. Exiting.')
        sys.exit()

    def on_create_steam_location_file():
        create_steam_location_file(console)

    def on_grab_manifest_files():
        grab_manifest_files(console)

    def on_create_lua_file():
        app_id = app_id_entry.get().strip()
        if not app_id.isdigit():
            messagebox.showwarning('Missing Information', 'Please provide a valid numeric APP ID.')
            return
        manifest_folder = select_folder(title='Select Folder with Manifest Files')
        output_folder = manifest_folder
        if not manifest_folder:
            messagebox.showwarning('Missing Information', 'Please select the folder for further steps.')
            return
        code_file = os.path.join(manifest_folder, 'code.txt')
        if not os.path.exists(code_file):
            messagebox.showerror('Missing Code File', 'code.txt file not found in the selected manifest folder.')
            return
        create_lua_file(console, int(app_id), manifest_folder, code_file, output_folder)
        try:
            if app_id_entry.winfo_exists():
                app_id_entry.delete(0, ctk.END)
        except Exception:
            return None
        else:  # inserted
            pass

    def on_select_folder_to_zip():
        zipper = FolderZipper(console)
        zipper.select_folder_to_zip()

    def open_help_link():
        url = 'https://toxichome-whoami.github.io/manilua_creator_release/manilua_tutorial.html'
        webbrowser.open(url)

    def on_download_updated_version():
        download_updated_version()

    def fetch_version():
        url = 'https://toxichome-whoami.github.io/manilua_creator_release/info.json'
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get('version', [{}])[0].get('main_version')
        except requests.exceptions.RequestException as e:
            messagebox.showerror('Error', f'Failed to fetch version.\n{e}')
            return None
        else:  # inserted
            pass

    def format_decimal(version: str) -> str:
        if not version:
            return '0'
        parts = version.split('.')
        if len(parts) > 1:
            return f"{parts[0]}.{''.join(parts[1:])}"
        return version

    def get_version_formanilua():
        while True:
            try:
                if not current_version.winfo_exists():
                    return
                version_text_fromweb = fetch_version()
                if version_text_fromweb:
                    web_version = float(format_decimal(version_text_fromweb))
                    local_version = float(format_decimal(main_version))
                    if web_version > local_version:
                        current_version.configure(text=f'Update Available: v{version_text_fromweb}')
                    else:  # inserted
                        if web_version == local_version:
                            current_version.configure(text=f'Current: v{main_version}')
                        else:  # inserted
                            current_version.configure(text='Error occurred!!')
                time.sleep(5)
        except Exception:
            return None
        else:  # inserted
            pass

    def start_fetching_formanilua():
        threading.Thread(target=get_version_formanilua, daemon=True).start()

    def start_fetching_formanilua() -> None:
        thread = threading.Thread(target=get_version_formanilua, daemon=True)
        thread.start()
    try:
        button_font = ctk.CTkFont(family='Segoe UI Semibold', size=12)
    except Exception as e:
        pass  # postinserted
    else:  # inserted
        try:
            branding_label = ctk.CTkLabel(root, text='Manilua Creator  for Steam Games', text_color='white', font=('Segoe UI Semibold', 21))
            branding_label.pack(pady=(10, 0))
            dev_label = ctk.CTkLabel(root, text='Developed by Toxic Home', text_color='white', font=('Segoe UI', 15))
            dev_label.pack(pady=(0, 15))
    except Exception as e:
        else:  # inserted
            global_hover_color = '#2D2D2D'
            global_border_color = '#4E4E4E'
            global_fg_color = '#232323'
            global_corner_radius = 8
            ctk.CTkButton(root, text='Setup Steam Location'.upper(), command=on_create_steam_location_file, font=button_font, width=258, height=39, corner_radius=global_corner_radius, text_color='white', anchor='center', border_width=1, hover_color=global_hover_color, border_color=global_border_color, fg_color=global_fg_color).pack(pady=(0, 12))
            ctk.CTkFrame(root, width=326, height=3, fg_color='#4D4D4D', corner_radius=8).pack(pady=(4, 16))
            app_id_entry = ctk.CTkEntry(root, placeholder_text='Enter APP ID'.capitalize(), corner_radius=global_corner_radius, font=button_font, text_color='white', width=258, height=39, border_width=1, border_color=global_border_color, fg_color=global_fg_color)
            app_id_entry.pack(pady=(0, 12))
            ctk.CTkButton(root, text='Create Manifest'.upper(), command=on_grab_manifest_files, font=button_font, width=258, height=39, corner_radius=global_corner_radius, text_color='white', anchor='center', border_width=1, hover_color=global_hover_color, border_color=global_border_color, fg_color=global_fg_color).pack(pady=(0, 12))
            ctk.CTkButton(root, text='Create Lua'.upper(), command=on_create_lua_file, font=button_font, width=258, height=39, corner_radius=global_corner_radius, text_color='white', anchor='center', border_width=1, hover_color=global_hover_color, border_color=global_border_color, fg_color=global_fg_color).pack(pady=(0, 12))
            ctk.CTkFrame(root, width=326, height=3, fg_color='#4D4D4D', corner_radius=8).pack(pady=(4, 16))
            ctk.CTkButton(root, text='Lua and st converter'.upper(), command=LuaStConverter, font=button_font, width=258, height=39, corner_radius=global_corner_radius, text_color='white', anchor='center', border_width=1, hover_color=global_hover_color, border_color=global_border_color, fg_color=global_fg_color).pack(pady=(0, 12))
            ctk.CTkButton(root, text='Folder to zip'.upper(), command=on_select_folder_to_zip, font=button_font, width=258, height=39, corner_radius=global_corner_radius, text_color='white', anchor='center', border_width=1, hover_color=global_hover_color, border_color=global_border_color, fg_color=global_fg_color).pack(pady=(0, 12))
            ctk.CTkFrame(root, width=326, height=3, fg_color='#4D4D4D', corner_radius=8).pack(pady=(4, 16))
            button_frame_help_program_update = ctk.CTkFrame(root, fg_color='#232323', width=258, height=39)
            button_frame_help_program_update.pack(pady=(0, 5))
            ctk.CTkButton(button_frame_help_program_update, text='Tutorial'.upper(), command=open_help_link, font=button_font, width=127, height=39, corner_radius=global_corner_radius, text_color='white', anchor='center', border_width=1, hover_color=global_hover_color, border_color=global_border_color, fg_color=global_fg_color).pack(padx=(0, 2.5), side='left')
            ctk.CTkButton(button_frame_help_program_update, text='Update'.upper(), command=on_download_updated_version, font=button_font, width=126, height=39, corner_radius=global_corner_radius, text_color='white', anchor='center', border_width=1, hover_color=global_hover_color, border_color=global_border_color, fg_color=global_fg_color).pack(padx=(2.5, 0), side='right')
            current_version = ctk.CTkLabel(root, text='Fetching version...', text_color='white', font=button_font)
            current_version.pack(pady=(0, 5))
            start_fetching_formanilua()
            rounded_frame = ctk.CTkFrame(root, corner_radius=6, fg_color='#444444', border_width=1, border_color='#707070')
            rounded_frame.pack(pady=(0, 19), padx=19, fill='both', expand=True)
            console = Text(rounded_frame, width=40, height=10, bg='#444444', fg='white', bd=0, relief='flat', highlightthickness=0)
            console.pack(pady=10, padx=10, fill='both', expand=True)
            console.configure(font=('Segoe UI Medium', 8))
            console.configure(state='disabled')
            root.mainloop()
        messagebox.showerror('Error', f'Error loading icon: {e}')
            messagebox.showerror('Error', f'Failed to create font: {e}')
            button_font = None
            messagebox.showerror('Error', f'Error creating branding widgets: {e}')
if __name__ == '__main__':
    main()
