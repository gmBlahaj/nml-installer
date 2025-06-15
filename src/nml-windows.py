import os
import requests
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from colorama import init, Fore, Style

GH_REPO = "https://api.github.com/repos/WorldBoxOpenMods/ModLoader/releases/latest"

class NeoModLoaderInstaller:
    def __init__(self, root):
        self.root = root
        self.root.title("NeoModLoader Installer")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('Red.TButton', foreground='red')
        self.style.configure('Green.TButton', foreground='green')
        
        self.create_widgets()
        init(autoreset=True)
    
    def create_widgets(self):
        
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        
        title_label = ttk.Label(main_frame, text="NeoModLoader Setup", style='Title.TLabel')
        title_label.pack(pady=(0, 10))
        
        
        prereq_frame = ttk.LabelFrame(main_frame, text="Before proceeding, please ensure:", padding="10")
        prereq_frame.pack(fill=tk.X, pady=5)
        
        prerequisites = [
            "✓ Verify you have the latest version of WorldBox",
            "✓ Closed WorldBox",
            "✓ Enabled Experimental Mode in the game",
            "✓ Backed up your game files (recommended)",
            "✓ Disabled or removed NCMS if previously installed"
        ]
        
        for p in prerequisites:
            ttk.Label(prereq_frame, text=p).pack(anchor=tk.W)
        
        
        dir_frame = ttk.LabelFrame(main_frame, text="WorldBox Directory", padding="10")
        dir_frame.pack(fill=tk.X, pady=5)
        
        self.dir_var = tk.StringVar()
        ttk.Entry(dir_frame, textvariable=self.dir_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(dir_frame, text="Browse", command=self.browse_directory).pack(side=tk.LEFT)
        ttk.Button(dir_frame, text="Auto-detect", command=self.auto_detect).pack(side=tk.LEFT, padx=(5, 0))
        
        
        log_frame = ttk.LabelFrame(main_frame, text="Installation Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(button_frame, text="Install", command=self.install, style='Green.TButton').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Update", command=self.update, style='Green.TButton').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Exit", command=self.root.quit, style='Red.TButton').pack(side=tk.RIGHT)
    
    def browse_directory(self):
        directory = filedialog.askdirectory(title="Select WorldBox Directory")
        if directory:
            self.dir_var.set(directory)
            self.validate_wb(directory)
    
    def auto_detect(self):
        gamepath = self.find_worldbox()
        if gamepath:
            self.dir_var.set(gamepath)
            self.log(f"Auto-detected WorldBox directory: {gamepath}", "success")
            self.validate_wb(gamepath)
        else:
            self.log("Could not auto-detect WorldBox directory.", "warning")
    
    def find_worldbox(self):
       
        steam_common = r"C:\Program Files (x86)\Steam\steamapps\common"
        worldbox = os.path.join(steam_common, "WorldBox")
        if os.path.exists(worldbox):
            return worldbox
        
        
        steam_libraries = [
            os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Steam", "steamapps", "common"),
            os.path.join(os.environ.get("ProgramFiles", ""), "Steam", "steamapps", "common"),
            os.path.join(os.environ.get("SystemDrive", "C:"), "SteamLibrary", "steamapps", "common")
        ]
        
        for lib in steam_libraries:
            worldbox = os.path.join(lib, "WorldBox")
            if os.path.exists(worldbox):
                return worldbox
        
        return None
    
    def validate_wb(self, path):
       
        required_folders = [
            "worldbox_Data",
            os.path.join("worldbox_Data", "StreamingAssets")
        ]
        
        missing = []
        for folder in required_folders:
            if not os.path.exists(os.path.join(path, folder)):
                missing.append(folder)
        
        if missing:
            self.log(f"Warning: Missing required folders: {', '.join(missing)}", "warning")
            return False
        else:
            self.log("Valid WorldBox directory detected", "success")
            return True
    
    def log(self, message, level="info"):
        
        colors = {
            "info": "blue",
            "success": "green",
            "warning": "orange",
            "error": "red"
        }
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n", level)
        self.log_text.tag_config("info", foreground=colors["info"])
        self.log_text.tag_config("success", foreground=colors["success"])
        self.log_text.tag_config("warning", foreground=colors["warning"])
        self.log_text.tag_config("error", foreground=colors["error"])
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def dl_stuff(self, url, directory):
       
        local_file = os.path.join(directory, os.path.basename(url))
        self.log(f"Downloading {os.path.basename(url)} to {local_file}")
        
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(local_file, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        self.log(f"Progress: {progress:.1f}%", "info")
            
            self.log(f"Successfully downloaded {os.path.basename(url)}", "success")
            return True
        except Exception as e:
            self.log(f"Error downloading {os.path.basename(url)}: {str(e)}", "error")
            return False
    
    def check_ncms(self, mods_dir):
        ncms_file = os.path.join(mods_dir, "NCMS_memload.dll")
        if os.path.exists(ncms_file):
            self.log("NCMS_memload.dll found - it will be removed during installation", "warning")
            return True
        else:
            self.log("No NCMS installation detected", "success")
            return False
    
    def install(self):
        gamepath = self.dir_var.get().strip()
        if not gamepath:
            messagebox.showerror("Error", "Please select a WorldBox directory")
            return
        
        if not os.path.exists(gamepath):
            messagebox.showerror("Error", "The specified directory does not exist")
            return
        
        
        if not self.validate_wb(gamepath):
            if not messagebox.askyesno("Warning", 
                                      "The selected directory appears to be missing required WorldBox folders.\n"
                                      "Are you sure this is the correct directory?"):
                return
        
        mods_dir = os.path.join(gamepath, "worldbox_Data", "StreamingAssets", "mods")
        os.makedirs(mods_dir, exist_ok=True)
        
        self.check_ncms(mods_dir)
        
        try:
            response = requests.get(GH_REPO)
            response.raise_for_status()
            release = response.json()
            assets = release["assets"]
            dll = next((a for a in assets if a["name"].endswith("NeoModLoader.dll")), None)
            pdb = next((a for a in assets if a["name"].endswith("NeoModLoader.pdb")), None)

            if not dll or not pdb:
                self.log("Could not find NeoModLoader files in the latest release", "error")
                return

            if not self.dl_stuff(dll["browser_download_url"], mods_dir):
                return
            if not self.dl_stuff(pdb["browser_download_url"], mods_dir):
                return

            
            ncms_file = os.path.join(mods_dir, "NCMS_memload.dll")
            if os.path.exists(ncms_file):
                os.remove(ncms_file)
                self.log("Removed NCMS_memload.dll", "success")
            
            self.log("Installation complete!", "success")
            self.log("Tip: Subscribe to NML on Steam Workshop for automatic updates.", "info")
            
        except Exception as e:
            self.log(f"Error during installation: {str(e)}", "error")
    
    def update(self):
        gamepath = self.dir_var.get().strip()
        if not gamepath:
            messagebox.showerror("Error", "Please select a WorldBox directory")
            return
        
        if not os.path.exists(gamepath):
            messagebox.showerror("Error", "The specified directory does not exist")
            return
        
        
        if not self.validate_wb(gamepath):
            if not messagebox.askyesno("Warning", 
                                      "The selected directory appears to be missing required WorldBox folders.\n"
                                      "Are you sure this is the correct directory?"):
                return
        
        mods_dir = os.path.join(gamepath, "worldbox_Data", "StreamingAssets", "mods")
        if not os.path.exists(mods_dir):
            self.log("Mods directory not found - performing fresh install", "warning")
            self.install()
            return
        
        try:
            response = requests.get(GH_REPO)
            response.raise_for_status()
            release = response.json()
            assets = release["assets"]
            dll = next((a for a in assets if a["name"].endswith("NeoModLoader.dll")), None)
            pdb = next((a for a in assets if a["name"].endswith("NeoModLoader.pdb")), None)

            if not dll or not pdb:
                self.log("Could not find NeoModLoader files in the latest release", "error")
                return

            
            local_dll = os.path.join(mods_dir, os.path.basename(dll["browser_download_url"]))
            local_pdb = os.path.join(mods_dir, os.path.basename(pdb["browser_download_url"]))
            
            if os.path.exists(local_dll) and os.path.exists(local_pdb):
                self.log("Found existing NeoModLoader installation - updating...", "info")
            else:
                self.log("Performing fresh installation...", "info")
            
            if not self.dl_stuff(dll["browser_download_url"], mods_dir):
                return
            if not self.dl_stuff(pdb["browser_download_url"], mods_dir):
                return
            
            self.log("Update complete!", "success")
            
        except Exception as e:
            self.log(f"Error during update: {str(e)}", "error")

if __name__ == "__main__":
    root = tk.Tk()
    app = NeoModLoaderInstaller(root)
    root.mainloop()