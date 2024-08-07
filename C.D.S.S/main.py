import os
import hashlib
import customtkinter as ctk
from tkinter import messagebox, ttk
from concurrent.futures import ThreadPoolExecutor
from threading import Thread

# Heuristic checks (example: executable files in non-standard directories and metadata checks)
def is_suspicious(file_path):
    suspicious_extensions = ['.exe', '.dll', '.bat', '.vbs', '.scr']
    non_standard_dirs = ['Documents', 'Downloads', 'Desktop']
    legitimate_apps_dirs = ['Program Files', 'Program Files (x86)', 'Windows']

    # Check file extension
    if any(file_path.endswith(ext) for ext in suspicious_extensions):
        # Check if it's in a non-standard directory
        if any(dir in file_path for dir in non_standard_dirs):
            return True
        # Exclude legitimate application directories
        if not any(dir in file_path for dir in legitimate_apps_dirs):
            return True
    
    # Check file size
    file_size = os.path.getsize(file_path)
    if file_size < 1024 or file_size > 100 * 1024 * 1024:  # less than 1KB or more than 100MB
        return True

    # Check if the file is hidden
    if os.path.basename(file_path).startswith('.'):
        return True
    
    # Check for suspicious file names
    suspicious_names = ['keygen', 'crack', 'patch', 'hack']
    if any(name in file_path.lower() for name in suspicious_names):
        return True

    return False

# Scan file and return result
def scan_file(file_path):
    if is_suspicious(file_path):
        return file_path
    return None

# Scan directory for suspicious files with multithreading
def scan_directory(directory, progress_callback):
    suspicious_files = []
    total_files = 0
    scanned_files = 0

    # First count the total number of files for progress calculation
    for root, dirs, files in os.walk(directory):
        total_files += len(files)

    # Function to scan a single file
    def scan_and_report(file_path):
        nonlocal scanned_files
        result = scan_file(file_path)
        scanned_files += 1
        progress_callback(scanned_files, total_files)
        return result

    # Using ThreadPoolExecutor for concurrent scanning
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                futures.append(executor.submit(scan_and_report, file_path))
        
        for future in futures:
            result = future.result()
            if result:
                suspicious_files.append(result)

    return suspicious_files

# Create GUI
class SuspiciousFileScanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Crimson System Scanner")
        self.root.geometry("700x500")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.create_widgets()
        
    def create_widgets(self):
        self.label = ctk.CTkLabel(self.root, text="Directory to scan:")
        self.label.pack(pady=5)
        
        self.entry = ctk.CTkEntry(self.root, width=400)
        self.entry.insert(0, "C:\\")
        self.entry.pack(pady=5)
        
        self.scan_button = ctk.CTkButton(self.root, text="Scan", command=self.start_scan)
        self.scan_button.pack(pady=5)
        
        self.progress = ctk.CTkProgressBar(self.root, width=400)
        self.progress.pack(pady=5)
        
        self.tree = ttk.Treeview(self.root, columns=("filepath", "details"), show="headings")
        self.tree.heading("filepath", text="File Path")
        self.tree.heading("details", text="Details")
        self.tree.column("filepath", stretch=True, width=400)
        self.tree.column("details", stretch=True, width=200)
        self.tree.pack(pady=20, padx=10, fill="both", expand=True)

    def update_progress(self, scanned_files, total_files):
        progress_value = scanned_files / total_files
        self.progress.set(progress_value)

    def start_scan(self):
        directory = self.entry.get()
        if not os.path.isdir(directory):
            messagebox.showerror("Error", "Invalid directory")
            return
        
        # Start the scan in a new thread to keep the GUI responsive
        Thread(target=self.scan, args=(directory,)).start()
    
    def scan(self, directory):
        suspicious_files = scan_directory(directory, self.update_progress)
        self.display_results(suspicious_files)
    
    def display_results(self, files):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        for file in files:
            details = "Suspicious file detected"
            self.tree.insert("", "end", values=(file, details))
        
        if not files:
            messagebox.showinfo("Result", "No suspicious files found")
        else:
            messagebox.showwarning("Result", f"{len(files)} suspicious files found")

if __name__ == "__main__":
    root = ctk.CTk()
    app = SuspiciousFileScanner(root)
    root.mainloop()
