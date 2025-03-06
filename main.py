global download_complete  # inserted
global stop_download  # inserted
global download_thread  # inserted
global download_speed  # inserted
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
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import threading
from bs4 import BeautifulSoup
import zipfile
import ctypes
main_version = '3.1.9.0'
base_path = Path(__file__).parent
datas = [(str(base_path / 'ico'), 'ico'), (str(base_path / 'Scripts'), 'Scripts')]

def anti_debug() -> None:
    if ctypes.windll.kernel32.IsDebuggerPresent()!= 0:
        sys.exit()

def detect_vm():
    vm_files = ['/proc/scsi/scsi', '/system/lib/libc_malloc_debug_qemu.so']
    for file in vm_files:
        if os.path.exists(file):
            sys.exit()

def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.abspath('.')
BASE_PATH = get_base_path()
icon_path = os.path.join(BASE_PATH, 'ico', 'steam_green.ico')
script_manifest_ID_graber_path = os.path.join(BASE_PATH, 'Scripts', 'manifest_ID_graber.txt')
script_only_dlc_grabber_path = os.path.join(BASE_PATH, 'Scripts', 'only_dlc_grabber.txt')

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
        manifest_files = [f for f in os.listdir(manifest_folder) if f.endswith('.manifest')]
        for manifest_file in manifest_files:
            if '_' in manifest_file:
                try:
                    manifest_code = manifest_file.split('_', 1)[1].replace('.manifest', '')
                    if manifest_code not in used_manifest_codes:
                        os.remove(os.path.join(manifest_folder, manifest_file))
                        log_message(console, f'Deleted unused manifest file: {manifest_file}')
                except Exception as e:
                    log_message(console, f'Error processing {manifest_file}: {str(e)}')
    except Exception as e:
        log_message(console, f'Error deleting manifest files: {str(e)}')

def process_code_file(console, code_file_path, output_folder, app_id, game_name, manifest_map):
    output_file_path = os.path.join(output_folder, f"{app_id}.lua")
    used_manifest_codes = set()
    
    try:
        # Read input code file
        with open(code_file_path, 'r') as input_file:
            lines = input_file.readlines()

        output_lines = [f'addappid({app_id})']

        # Process each line in the code file
        for line in lines:
            line = line.strip()
            if not line:
                continue

            try:
                if ';' in line:
                    # Split key ID and key code
                    key_id, key_code = [part.strip() for part in line.split(';', 1)]
                    
                    # Get matching manifest file
                    manifest_file_path = manifest_map.get(key_id)
                    if not manifest_file_path:
                        log_message(console, f"No matching manifest file found for Key_ID: {key_id}")
                        continue

                    # Extract manifest code from filename
                    manifest_filename = os.path.basename(manifest_file_path)
                    manifest_code = manifest_filename.split('_', 1)[1].replace('.manifest', '')
                    
                    # Add to output lines
                    output_lines.append(f'addappid({key_id}, 1, "{key_code}")')
                    output_lines.append(f'setManifestid({key_id}, "{manifest_code}", 0)')
                    used_manifest_codes.add(manifest_code)
                    
                    log_message(console, f"Processed Key_ID: {key_id} with manifest {manifest_code}")
                else:
                    log_message(console, f"Skipping invalid line: {line}")
                    
            except Exception as e:
                log_message(console, f"Error processing line '{line}': {str(e)}")

        # Add footer comments
        output_lines.append(f'\n-- Generated By "Manilua Creator" Game name = ({game_name})')
        output_lines.append('-- Join our discord server (Toxic Home): https://discord.gg/3ShGjfj6je')

        # Write output file
        with open(output_file_path, 'w') as output_file:
            output_file.write('\n'.join(output_lines))
        
        log_message(console, f"Lua file created at: {output_file_path}")
        return output_file_path, used_manifest_codes

    except Exception as e:
        log_message(console, f"Error creating Lua file: {str(e)}")
        return None, None

def grab_manifest_files(console):
    steam_location_file = 'steam_location.txt'
    if not os.path.exists(steam_location_file):
        log_message(console, f'{steam_location_file} not found. Exiting.')
        return messagebox.showerror('Error', f'Create {steam_location_file} first to start the prosess. Exiting.')
    with open(steam_location_file, 'r') as file:
        steam_location = file.read().strip()
    depotcache_path = os.path.join(steam_location, 'depotcache')
    if not os.path.exists(depotcache_path):
        log_message(console, f'Depotcache folder not found at {depotcache_path}. Exiting.')
        return messagebox.showwarning('Worning', f'Depotcache folder not found at {depotcache_path}. Exiting.')
    manifest_file = select_input_file('grab_manifest.txt')
    if not manifest_file:
        log_message(console, 'No grab_manifest.txt file selected. Exiting.')
        return messagebox.showwarning('Worning', 'No grab_manifest.txt file selected. Exiting.')
    with open(manifest_file, 'r') as file:
        manifest_ids = [line.strip() for line in file if line.strip()]
    if not manifest_ids:
        log_message(console, 'No manifest IDs found in grab_manifest.txt. Please add manifest IDs.')
        return
    destination_folder = select_folder(title='Select Destination Folder for Manifest Files')
    if not destination_folder:
        log_message(console, 'No destination folder selected. Exiting.')
        return messagebox.showwarning('Worning', 'No destination folder selected. Exiting.')
    for manifest_id in manifest_ids:
        matching_files = [f for f in os.listdir(depotcache_path) if not f.startswith(manifest_id + '_') or not f.endswith('.manifest')]
        if not matching_files:
            log_message(console, f'No manifest files found for ID {manifest_id} in {depotcache_path}.')
            continue
        for manifest_filename in matching_files:
            source_path = os.path.join(depotcache_path, manifest_filename)
            destination_path = os.path.join(destination_folder, manifest_filename)
            shutil.copy2(source_path, destination_path)
            log_message(console, f'Copied {manifest_filename} to {destination_folder}.')
    try:
        os.remove(manifest_file)
        log_message(console, f'Successfully deleted grab_manifest.txt file: {os.path.basename(manifest_file)}')
    except Exception as e:
        pass  # postinserted
    else:  # inserted
        log_message(console, '\nManifest files have been grabbed.')
        log_message(console, f'Error deleting grab_manifest.txt file: {e}')

def create_code_txt(console):
    steam_location_file = 'steam_location.txt'
    if not os.path.exists(steam_location_file):
        log_message(console, f'{steam_location_file} not found. Exiting.')
        return messagebox.showerror('Error', f'Create {steam_location_file} first to start the prosess. Exiting.')
    folder_path = select_folder(title='Select Folder with Manifest Files')
    if not folder_path:
        log_message(console, 'No folder selected. Exiting.')
        return messagebox.showwarning('Worning', 'No folder selected. Exiting.')
    with open(steam_location_file, 'r') as file:
        steam_location = file.read().strip()
    config_path = os.path.join(steam_location, 'config', 'config.vdf')
    if not os.path.exists(config_path):
        log_message(console, f'Config file not found at {config_path}. Exiting.')
        return messagebox.showerror('Error', f'Config file not found at {config_path}. Exiting.')
    with open(config_path, 'r') as config_file:
        config_content = config_file.read()
    output_lines = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.manifest'):
            manifest_id = file_name.split('_')[0]
            pattern = re.compile(f'\"{manifest_id}\"\\s*\\{\\s*\"DecryptionKey\"\\s*\"([a-f0-9]+)\"')
            match = pattern.search(config_content)
            if match:
                decryption_key = match.group(1)
                output_lines.append(f'{manifest_id};{decryption_key}')
    output_path = os.path.join(folder_path, 'code.txt')
    with open(output_path, 'w') as output_file:
        output_file.write('\n'.join(output_lines))
    log_message(console, f'Decryption keys extracted and saved to {output_path}')

def create_lua_file(console, app_id, game_name, manifest_folder, code_file, output_folder):
    try:
        manifest_map = get_latest_manifest_files(manifest_folder)
        lua_file_path, used_manifest_codes = process_code_file(console, code_file, output_folder, app_id, game_name, manifest_map)
        if not lua_file_path:
            log_message(console, 'Error processing the input file. Exiting.')
            return
        log_message(console, '\n')
        delete_unused_manifest_files(console, manifest_folder, used_manifest_codes)
    except Exception as e:
        pass  # postinserted
    else:  # inserted
        try:
            os.remove(code_file)
            log_message(console, f'Successfully deleted code.txt file: {os.path.basename(code_file)}')
        except Exception as e:
            log_message(console, f'Error deleting code.txt file: {e}')
            log_message(console, f'Unexpected error occurred: {e}')

def create_steam_location_file(console):
    """Create or update the Steam installation location file"""
    try:
        # Determine file path relative to executable
        base_dir = os.path.dirname(sys.argv[0]) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
        file_path = os.path.join(base_dir, 'steam_location.txt')
        
        # Check for existing installation
        current_location = None
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    current_location = f.read().strip()
                    if current_location and os.path.exists(current_location):
                        response = messagebox.askyesno(
                            "Update Location",
                            f"Current Steam location:\n{current_location}\n\nUpdate to new location?",
                            parent=console.master
                        )
                        if not response:
                            return
            except Exception as e:
                log_message(console, f"Error reading existing location: {str(e)}")

        # Get new location from user
        new_location = filedialog.askdirectory(
            title="Select Steam Installation Folder",
            mustexist=True,
            parent=console.master
        )
        
        if not new_location:
            log_message(console, "Location selection cancelled")
            return

        # Validate Steam installation
        steam_exe = os.path.join(new_location, 'steam.exe')
        if not os.path.exists(steam_exe):
            messagebox.showerror(
                "Invalid Location",
                "Steam.exe not found in selected directory!\nPlease select valid Steam installation folder.",
                parent=console.master
            )
            return

        # Save new location
        try:
            with open(file_path, 'w') as f:
                f.write(new_location)
            
            log_message(console, f"Steam location saved: {new_location}")
            messagebox.showinfo(
                "Success",
                f"Steam location updated successfully:\n{new_location}",
                parent=console.master
            )
            
            # Verify write operation
            with open(file_path, 'r') as f:
                verify_location = f.read().strip()
                if verify_location != new_location:
                    raise IOError("File verification failed - written content doesn't match")

        except Exception as e:
            log_message(console, f"Error saving location: {str(e)}")
            messagebox.showerror(
                "Save Error",
                f"Failed to save Steam location:\n{str(e)}",
                parent=console.master
            )
            if os.path.exists(file_path):
                os.remove(file_path)

    except Exception as e:
        log_message(console, f"Critical error in location setup: {str(e)}")
        messagebox.showerror(
            "Fatal Error",
            f"Critical failure in Steam location configuration:\n{str(e)}",
            parent=console.master
        )

def depots_grabber_function():
    """\n    Grabs all depot IDs from SteamDB for a given Steam APP ID and saves them to a text file.\n\n    :param app_id: The Steam APP ID.\n    :type app_id: str\n    :param destination_folder: The destination folder path to save the text file.\n    :type destination_folder: str\n\n    """  # inserted
    app_id = app_id_entry.get().strip()
    if not app_id.isdigit():
        messagebox.showerror('Invalid Input', 'Please enter a valid integer APP ID.')
        return
    destination_folder = select_folder(title='Select Destination to create folder')
    if not destination_folder:
        messagebox.showwarning('No Selection', 'No destination selected. Exiting.')
        return
    app_id_folder = os.path.join(destination_folder, app_id)
    os.makedirs(app_id_folder, exist_ok=True)
    try:
        driver = webdriver.Chrome()
    except WebDriverException as e:
        pass  # postinserted
    else:  # inserted
        url = f'https://steamdb.info/app/{app_id}/depots/'
        driver.get(url)
        time.sleep(5)
        script_path = script_manifest_ID_graber_path
        if not os.path.exists(script_path):
            messagebox.showerror('Error', f'JavaScript file not found: {script_path}')
            driver.quit()
            return
        with open(script_path) as file:
            js_code = file.read()
        try:
            driver.execute_script(js_code)
        except Exception as e:
            pass  # postinserted
        else:  # inserted
            time.sleep(2)
            driver.quit()
        messagebox.showerror('Error', f'Error initializing WebDriver: {e}')
        return
        messagebox.showerror('Error', f'Error executing JavaScript: {e}')
        driver.quit()

def depots_grabber():
    threading.Thread(target=depots_grabber_function).start()

def only_dlc_grabber_code():
    """\n    Grabs all DLC IDs from the given SteamDB app page and\n    saves them to a text file.\n\n    :param app_id: The Steam App ID to grab DLCs from\n    :type app_id: str\n    """  # inserted
    app_id = app_id_entry.get().strip()
    if not app_id.isdigit():
        messagebox.showerror('Invalid Input', 'Please enter a valid integer APP ID.')
        return
    try:
        driver = webdriver.Chrome()
    except WebDriverException as e:
        pass  # postinserted
    else:  # inserted
        url = f'https://steamdb.info/app/{app_id}/dlc/'
        driver.get(url)
        time.sleep(5)
        script_path = script_only_dlc_grabber_path
        if not os.path.exists(script_path):
            messagebox.showerror('Error', f'JavaScript file not found: {script_path}')
            driver.quit()
            return
        with open(script_path) as file:
            js_code = file.read()
        try:
            driver.execute_script(js_code)
        except Exception as e:
            pass  # postinserted
        else:  # inserted
            time.sleep(2)
            driver.quit()
        messagebox.showerror('Error', f'Error initializing WebDriver: {e}')
        return None
    else:  # inserted
        pass
        messagebox.showerror('Error', f'Error executing JavaScript: {e}')
        driver.quit()

def dlc_grabber():
    threading.Thread(target=only_dlc_grabber_code).start()
download_speed = '0 KB/s'
download_complete = False
stop_download = False
download_thread = None
manilua_update_link = 'https://nothinghome.pythonanywhere.com/manilua_update_link'

def get_download_link():
    url = manilua_update_link
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        link_div = soup.find('div', class_='manilia_update_link')
        if link_div:
            return link_div.text.strip()
        raise ValueError('Download link not found on the page.')
    except Exception as e:
        messagebox.showerror('Error', f'Failed to fetch download link: {e}')

def download_file(url, file_name, output_folder, progress_bar, speed_label, app):
    global download_speed  # inserted
    global download_complete  # inserted
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
                if stop_download:
                    break
                file.write(chunk)
                downloaded_size += len(chunk)
                elapsed_time = time.time() - start_time
                if elapsed_time < 1e-09:
                    current_speed = 0.0
                else:  # inserted
                    current_speed = downloaded_size / (elapsed_time * 1024)
                download_speed = f'{current_speed:.2f} KB/s'
                progress = downloaded_size / total_size * 100 if total_size > 0 else 0
                progress_bar.set(progress / 100)
                speed_label.configure(text=f'Speed: {download_speed}')
                app.update()
                if not stop_download:
                    download_complete = True
                    if not file_name.endswith('.zip'):
                        messagebox.showinfo('Success', 'Download completed!')
                    if file_name.endswith('.zip'):
                        unzip_file(file_path, app, output_folder)
                else:  # inserted
                    os.remove(file_path)
                    messagebox.showinfo('Cancelled', 'Download cancelled and file deleted.')
            messagebox.showerror('Error', f'An error occurred: {e}')
            if os.path.exists(file_path):
                os.remove(file_path)

def unzip_file(zip_path, app, output_folder):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            pass  # postinserted
    except Exception as e:
            zip_ref.extractall(output_folder)
                os.remove(zip_path)
                app.quit()
            messagebox.showerror('Error', f'Failed to unzip file: {e}')

def on_closing(app, file_name, output_folder):
    global stop_download  # inserted
    stop_download = True
    if download_thread and download_thread.is_alive():
        app.after(500, lambda: on_closing(app, file_name, output_folder))
    else:  # inserted
        file_path = os.path.join(output_folder, file_name)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except PermissionError:
            pass  # postinserted
        else:  # inserted
            app.destroy()
            pass

def start_download(url, file_name, output_folder):
    global download_speed  # inserted
    global download_thread  # inserted
    global stop_download  # inserted
    global download_complete  # inserted
    download_speed = '0 KB/s'
    download_complete = False
    stop_download = False
    file_name = ctk.CTk()
    file_name.geometry('300x100')
    popup_window_icon = icon_path
    if os.path.exists(popup_window_icon):
        try:
            file_name.iconbitmap(popup_window_icon)
        except Exception as e:
            pass  # postinserted
    else:  # inserted
        messagebox.showerror('Error', f'Icon file not found: {popup_window_icon}')
    file_name.resizable(False, False)
    file_name.title('Downloader')
    speed_label = ctk.CTkLabel(file_name, text='Speed: 0 KB/s')
    speed_label.pack(pady=(15, 0))
    progress_bar = ctk.CTkProgressBar(file_name, width=250, progress_color='#005d70')
    progress_bar.pack(pady=10)
    progress_bar.set(0)

    def check_download_complete():
        if download_complete:
            app.quit()
        else:  # inserted
            app.after(100, check_download_complete)
    download_thread = threading.Thread(target=download_file, args=(url, file_name, output_folder, progress_bar, speed_label, file_name))
    download_thread.start()
    file_name.protocol('WM_DELETE_WINDOW', lambda: on_closing(app, file_name, output_folder))
    file_name.after(100, output_folder)
    file_name.mainloop()
        messagebox.showerror('Error', f'Error loading icon: {e}')

def select_output_folder():
    folder_selected = filedialog.askdirectory()
    return folder_selected if folder_selected else None

def download_updated_version():
    download_url = get_download_link()
    if download_url:
        output_folder = select_output_folder()
        if output_folder:
            file_name = download_url.split('/')[(-1)]
            start_download(download_url, file_name, output_folder)
        else:  # inserted
            messagebox.showinfo('Info', 'Download cancelled because no output folder was selected.')

def zip_folder(folder_path, zip_path):
    """\n    Zips the contents of a folder into a zip file.\n    """  # inserted
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=folder_path)
                zipf.write(file_path, arcname)

def delete_folder_zip(folder_path, console):
    """\n    Deletes a folder and its contents.\n    """  # inserted
    try:
        shutil.rmtree(folder_path)
        log_message(console, f'Deleted: {folder_path}')
        return
    except Exception as e:
        log_message(console, f'Error deleting {folder_path}: {e}')
    else:  # inserted
        pass

def select_folder_to_zip(console):
    """\n    Opens a folder selection dialog and processes the selected folder.\n    """  # inserted
    selected_folder = ctk.filedialog.askdirectory(title='Select a folder to zip')
    if not selected_folder:
        messagebox.showinfo('Info', 'No folder selected. Exiting...')
        return
    subfolders = [f.path for f in os.scandir(selected_folder) if f.is_dir()]
    successfully_zipped = []
    skipped_folders = []
    if not subfolders:
        contains_lua = any((f.endswith('.lua') for f in os.listdir(selected_folder)))
        contains_manifest = any((f.endswith('.manifest') for f in os.listdir(selected_folder)))
        if contains_lua and contains_manifest:
            zip_path = f'{selected_folder}.zip'
            if os.path.exists(zip_path):
                messagebox.showinfo('Info', f'Zip file already exists: {zip_path}')
                return
            zip_folder(selected_folder, zip_path)
            messagebox.showinfo('Success', f'Zipped: {selected_folder}')
            confirm = messagebox.askyesno('Confirmation', f'Do you want to delete the folder \'{selected_folder}\'?')
            if confirm:
                delete_folder_zip(selected_folder, console)
                log_message(console, 'Main folder deleted.')
            else:  # inserted
                log_message(console, 'Main folder was not deleted.')
        else:  # inserted
            messagebox.showinfo('Info', 'The folder must contain both .lua and .manifest files. Exiting...')
    else:  # inserted
        for folder in subfolders:
            contains_lua = any((f.endswith('.lua') for f in os.listdir(folder)))
            contains_manifest = any((f.endswith('.manifest') for f in os.listdir(folder)))
            if contains_lua and contains_manifest:
                zip_path = f'{folder}.zip'
                if os.path.exists(zip_path):
                    log_message(console, f'Zip file already exists: {zip_path}')
                else:  # inserted
                    zip_folder(folder, zip_path)
                    successfully_zipped.append(folder)
                    log_message(console, f'Zipped: {folder}')
            else:  # inserted
                skipped_folders.append(folder)
                log_message(console, f'Skipping folder without both .lua and .manifest files: {folder}')
        if skipped_folders:
            log_message(console, f"Some folders did not contain .lua and .manifest files and were skipped: {', '.join(skipped_folders)}")
        if successfully_zipped:
            confirm = messagebox.askyesno('Confirmation', 'Do you want to delete only the successfully zipped subfolders?')
            if confirm:
                for folder in successfully_zipped:
                    delete_folder_zip(folder, console)
                log_message(console, 'Successfully zipped subfolders deleted.')
            else:  # inserted
                log_message(console, 'Subfolders were not deleted.')

def add_dlc_data(console):
    try:
        text_file = filedialog.askopenfilename(title='Select a Text File', filetypes=[('Text files', '*.txt')])
        if not text_file:
            log_message(console, 'No text file selected. Exiting.\n')
            messagebox.showwarning('Warning', 'No text file selected. Exiting.\n')
            return
        folder_path = filedialog.askdirectory(title='Select Folder with Lua File')
        if not folder_path:
            log_message(console, 'No folder selected. Exiting.\n')
            messagebox.showwarning('Warning', 'No folder selected. Exiting.\n')
            return
    except Exception as e:
        pass  # postinserted
    else:  # inserted
        lua_files = [f for f in os.listdir(folder_path) if f.endswith('.lua')]
            if not lua_files:
                log_message(console, 'No Lua file found in the selected folder. Exiting.\n')
                return
            lua_file = os.path.join(folder_path, lua_files[0])
            if not text_file or not text_file.endswith('.txt'):
                log_message(console, 'Only .txt file is acceptable to complete the operation. Exiting.\n')
                return
        else:  # inserted
            with open(text_file, 'r', encoding='utf-8') as txt:
                text_content = txt.read()
                    with open(lua_file, 'r', encoding='utf-8') as lua:
                        lua_content = lua.readlines()
                            if text_content in ''.join(lua_content):
                                messagebox.showerror('Error', 'The DLC data is already added.\n')
                                return
                            insert_position = next((i for i, line in enumerate(lua_content) if line.strip().startswith('--')), len(lua_content))
                            lua_content.insert(insert_position, text_content + '\n\n' if not text_content.endswith('\n') else text_content + '\n')
                            with open(lua_file, 'w', encoding='utf-8') as lua, lua.writelines(lua_content):
                                pass  # postinserted
            log_message(console, f'Error: {e}\n')

def main():
    global game_name_entry  # inserted
    global app_id_entry  # inserted
    root = ctk.CTk()
    root.title('Manilua Creator')
    root.resizable(False, True)
    root.geometry('385x664')
    root.minsize(385, 664)
    root.maxsize(385, 819)
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
    anti_debug()
    detect_vm()

    def on_create_steam_location_file():
        create_steam_location_file(console)

    def on_grab_manifest_files():
        grab_manifest_files(console)

    def on_create_code_txt():
        create_code_txt(console)

    def on_create_lua_file():
        app_id = app_id_entry.get().strip()
        game_name = game_name_entry.get().strip()
        if not app_id.isdigit() or not game_name:
            messagebox.showwarning('Missing Information', 'Please provide a valid numeric APP ID and Game Name first.')
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
        create_lua_file(console, int(app_id), game_name, manifest_folder, code_file, output_folder)
        log_message(console, 'Lua file has been created.')
        app_id_entry.delete(0, ctk.END)
        game_name_entry.delete(0, ctk.END)

    def on_add_dlc_data():
        add_dlc_data(console)

    def on_select_folder_to_zip():
        select_folder_to_zip(console)

    def open_help_link():
        url = 'https://nothinghome.pythonanywhere.com/help_manilua'
        webbrowser.open(url)

    def on_download_updated_version():
        download_updated_version()

    def get_version_formanilua() -> None:
        while True:
            url = 'https://toxichome-whoami.github.io/manilua_creator_release/manilua_current_version.html'
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                version_text_fromweb = soup.find('div', class_='version').text.strip()

                def format_decimal(input_string: str) -> str:
                    parts = input_string.split('.')
                    if len(parts) < 2:
                        return input_string
                    integer_part = parts[0]
                    decimal_part = ''.join(parts[1:])
                    return f'{integer_part}.{decimal_part}'
                if float(format_decimal(version_text_fromweb)) > float(format_decimal(main_version)):
                    current_version.configure(text=f'Update Available: v{version_text_fromweb}')
                else:  # inserted
                    if float(format_decimal(version_text_fromweb)) == float(format_decimal(main_version)):
                        current_version.configure(text=f'Current: v{main_version}')
                    else:  # inserted
                        current_version.configure(text='Error occurred!!')
            else:  # inserted
                current_version.configure(text='Failed to fetch version')
            time.sleep(5)

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
            button_frame_depots_grabber_and_help = ctk.CTkFrame(root, fg_color='#232323', width=258, height=39)
            button_frame_depots_grabber_and_help.pack(pady=(0, 12))
            ctk.CTkButton(button_frame_depots_grabber_and_help, text='Game Depots'.upper(), command=depots_grabber, font=button_font, width=127, height=39, corner_radius=global_corner_radius, text_color='white', anchor='center', border_width=1, hover_color=global_hover_color, border_color=global_border_color, fg_color=global_fg_color).pack(padx=(0, 2.5), side='left')
            ctk.CTkButton(button_frame_depots_grabber_and_help, text='DLC Grabber'.upper(), command=dlc_grabber, font=button_font, width=126, height=39, corner_radius=global_corner_radius, text_color='white', anchor='center', border_width=1, hover_color=global_hover_color, border_color=global_border_color, fg_color=global_fg_color).pack(padx=(2.5, 0), side='right')
            ctk.CTkButton(root, text='Copy Manifest'.upper(), command=on_grab_manifest_files, font=button_font, width=258, height=39, corner_radius=global_corner_radius, text_color='white', anchor='center', border_width=1, hover_color=global_hover_color, border_color=global_border_color, fg_color=global_fg_color).pack(pady=(0, 12))
            ctk.CTkButton(root, text='Create Key'.upper(), command=on_create_code_txt, font=button_font, width=258, height=39, corner_radius=global_corner_radius, text_color='white', anchor='center', border_width=1, hover_color=global_hover_color, border_color=global_border_color, fg_color=global_fg_color).pack(pady=(0, 12))
            ctk.CTkFrame(root, width=326, height=3, fg_color='#4D4D4D', corner_radius=8).pack(pady=(4, 16))
            game_name_entry = ctk.CTkEntry(root, placeholder_text='Enter the game name'.capitalize(), corner_radius=global_corner_radius, font=button_font, width=258, height=39, border_width=1, border_color=global_border_color, fg_color=global_fg_color)
            game_name_entry.pack(pady=(0, 12))
            app_id_entry = ctk.CTkEntry(root, placeholder_text='Enter APP ID'.capitalize(), corner_radius=global_corner_radius, font=button_font, width=258, height=39, border_width=1, border_color=global_border_color, fg_color=global_fg_color)
            app_id_entry.pack(pady=(0, 12))
            ctk.CTkButton(root, text='Create Lua'.upper(), command=on_create_lua_file, font=button_font, width=258, height=39, corner_radius=global_corner_radius, text_color='white', anchor='center', border_width=1, hover_color=global_hover_color, border_color=global_border_color, fg_color=global_fg_color).pack(pady=(0, 12))
            ctk.CTkButton(root, text='Add Dlc Data'.upper(), command=on_add_dlc_data, font=button_font, width=258, height=39, corner_radius=global_corner_radius, text_color='white', anchor='center', border_width=1, hover_color=global_hover_color, border_color=global_border_color, fg_color=global_fg_color).pack(pady=(0, 12))
            ctk.CTkFrame(root, width=326, height=3, fg_color='#4D4D4D', corner_radius=8).pack(pady=(4, 16))
            ctk.CTkButton(root, text='Folder to zip'.upper(), command=on_select_folder_to_zip, font=button_font, width=258, height=39, corner_radius=global_corner_radius, text_color='white', anchor='center', border_width=1, hover_color=global_hover_color, border_color=global_border_color, fg_color=global_fg_color).pack(pady=(0, 12))
            button_frame_help_program_update = ctk.CTkFrame(root, fg_color='#232323', width=258, height=39)
            button_frame_help_program_update.pack(pady=(0, 5))
            ctk.CTkButton(button_frame_help_program_update, text='Help'.upper(), command=open_help_link, font=button_font, width=127, height=39, corner_radius=global_corner_radius, text_color='white', anchor='center', border_width=1, hover_color=global_hover_color, border_color=global_border_color, fg_color=global_fg_color).pack(padx=(0, 2.5), side='left')
            ctk.CTkButton(button_frame_help_program_update, text='Update'.upper(), command=on_download_updated_version, font=button_font, width=126, height=39, corner_radius=global_corner_radius, text_color='white', anchor='center', border_width=1, hover_color=global_hover_color, border_color=global_border_color, fg_color=global_fg_color).pack(padx=(2.5, 0), side='right')
            current_version = ctk.CTkLabel(root, text='Fetching version...', text_color='white', font=button_font)
            current_version.pack(pady=(0, 5))
            start_fetching_formanilua()
            rounded_frame = ctk.CTkFrame(root, corner_radius=8, fg_color='#444444', border_width=1, border_color='#707070')
            rounded_frame.pack(pady=(0, 15), padx=29, fill='both', expand=True)
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
