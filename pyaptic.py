import subprocess
import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter.scrolledtext import ScrolledText
import os
import sys
import requests
from bs4 import BeautifulSoup

class ProgramInstaller(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Synaptic Clone")
        self.geometry("800x400")
        self.minsize(500, 300)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.installed_programs = self.get_installed_programs()
        self.search_cache = {}

        # Frame for the installed apps list
        self.installed_frame = tk.Frame(self)
        self.installed_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.installed_label = tk.Label(self.installed_frame, text="Installed Programs:")
        self.installed_label.pack(pady=10)

        self.installed_listbox = tk.Listbox(self.installed_frame, width=40, height=15)
        self.installed_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.installed_listbox.bind("<Button-3>", self.show_remove_menu)
        self.installed_listbox_scrollbar = tk.Scrollbar(self.installed_frame, command=self.installed_listbox.yview)
        self.installed_listbox.config(yscrollcommand=self.installed_listbox_scrollbar.set)
        self.installed_listbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame for the searched apps list
        self.searched_frame = tk.Frame(self)
        self.searched_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.search_label = tk.Label(self.searched_frame, text="Search for Programs:")
        self.search_label.pack(pady=10)

        self.search_entry = tk.Entry(self.searched_frame)
        self.search_entry.pack(fill=tk.X, padx=10)

        self.search_button = tk.Button(self.searched_frame, text="Search", command=self.search_programs)
        self.search_button.pack(pady=5)

        self.searched_label = tk.Label(self.searched_frame, text="Searched Programs:")
        self.searched_label.pack(pady=10)

        self.searched_listbox = tk.Listbox(self.searched_frame, width=40, height=15)
        self.searched_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.searched_listbox.bind("<Button-3>", self.show_install_menu)
        self.searched_listbox_scrollbar = tk.Scrollbar(self.searched_frame, command=self.searched_listbox.yview)
        self.searched_listbox.config(yscrollcommand=self.searched_listbox_scrollbar.set)
        self.searched_listbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.install_menu = tk.Menu(self, tearoff=0)
        self.install_menu.add_command(label="Install", command=self.install_selected)

        self.remove_menu = tk.Menu(self, tearoff=0)
        self.remove_menu.add_command(label="Remove", command=self.remove_selected)

        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Update Apt", command=self.update_apt)
        self.file_menu.add_command(label="Upgrade Apt", command=self.upgrade_apt)
        self.file_menu.add_command(label="Fix Apt Issues", command=self.fix_apt_issues)
        self.file_menu.add_command(label="Fix Pkg Issues", command=self.fix_pkg_issues)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Update Pip Packages", command=self.update_pip_packages)
        self.file_menu.add_command(label="Install Python", command=self.install_python_version)

        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        self.update_installed_list()

    def get_installed_programs(self):
        try:
            installed_programs = subprocess.check_output(["dpkg", "-l"])
            return installed_programs.decode("utf-8")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to fetch installed programs.")
            return ""

    def update_installed_list(self):
        self.installed_listbox.delete(0, tk.END)
        self.installed_listbox.insert(tk.END, *self.installed_programs.splitlines())

    def search_programs(self):
        query = self.search_entry.get()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search query.")
            return

        if query in self.search_cache:
            search_result = self.search_cache[query]
        else:
            search_result = self.perform_search(query)
            self.search_cache[query] = search_result

        self.searched_listbox.delete(0, tk.END)
        self.searched_listbox.insert(tk.END, *search_result.splitlines())

    def perform_search(self, query):
        try:
            search_result = subprocess.check_output(["apt", "search", query])
            return search_result.decode("utf-8")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to search for programs.")
            return ""

    def install_selected(self):
        selected_program = self.searched_listbox.get(tk.ACTIVE)
        if not selected_program:
            messagebox.showwarning("Warning", "Please select a program to install.")
            return

        try:
            subprocess.run(["sudo", "apt", "install", selected_program.split()[0]], check=True)
            messagebox.showinfo("Success", f"{selected_program.split()[0]} installed successfully.")
            self.installed_programs = self.get_installed_programs()
            self.update_installed_list()
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", f"Failed to install {selected_program.split()[0]}.")

    def remove_selected(self):
        selected_program = self.installed_listbox.get(tk.ACTIVE)
        if not selected_program:
            messagebox.showwarning("Warning", "Please select a program to remove.")
            return

        try:
            subprocess.run(["sudo", "apt", "remove", selected_program.split()[1]], check=True)
            messagebox.showinfo("Success", f"{selected_program.split()[1]} removed successfully.")
            self.installed_programs = self.get_installed_programs()
            self.update_installed_list()
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", f"Failed to remove {selected_program.split()[1]}.")

    def show_install_menu(self, event):
        self.install_menu.post(event.x_root, event.y_root)

    def show_remove_menu(self, event):
        self.remove_menu.post(event.x_root, event.y_root)

    def update_apt(self):
        try:
            subprocess.run(["sudo", "apt", "update"], check=True)
            messagebox.showinfo("Success", "Apt updated successfully.")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to update apt.")

    def upgrade_apt(self):
        try:
            subprocess.run(["sudo", "apt", "upgrade"], check=True)
            messagebox.showinfo("Success", "Apt upgraded successfully.")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to upgrade apt.")

    def fix_apt_issues(self):
        try:
            subprocess.run(["sudo", "apt", "--fix-broken", "install"], check=True)
            messagebox.showinfo("Success", "Apt issues fixed successfully.")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to fix apt issues.")

    def fix_pkg_issues(self):
        try:
            subprocess.run(["sudo", "dpkg", "--configure", "-a"], check=True)
            messagebox.showinfo("Success", "Package issues fixed successfully.")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to fix package issues.")

    def update_pip_packages(self):
        try:
            pip_commands = [sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip']
            result = subprocess.run(pip_commands, capture_output=True, text=True, check=True)
            if result.stdout or result.stderr:
                messagebox.showinfo("Pip Update", result.stdout + result.stderr)
            else:
                messagebox.showinfo("Pip Update", "No outdated packages found.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Pip Update Error", e.stderr)

    def get_python_versions(self):
        url = "https://www.python.org/downloads/"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        versions = []

        for link in soup.find_all('a'):
            href = link.get('href')
            if href and href.startswith("/downloads/release/python-"):
                version = href.split("-")[2]
                if version.startswith(("2", "3")):  # Filter out pre-releases and other versions
                    versions.append(version)

        return versions

    def install_python_version(self):
        python_versions = self.get_python_versions()
        if not python_versions:
            messagebox.showwarning("Warning", "No Python versions found.")
            return

        version = python_versions[-1]
        if len(python_versions) > 1:
            version = simpledialog.askstring("Install Python", "Enter Python version to install:", initialvalue=version)

        if version:
            try:
                url = f"https://www.python.org/ftp/python/{version}/python-{version}-amd64.exe" if sys.platform.startswith('win') else f"https://www.python.org/ftp/python/{version}/Python-{version}.tgz"
                response = requests.get(url)
                python_installer = os.path.basename(url)
                with open(python_installer, 'wb') as f:
                    f.write(response.content)

                if sys.platform.startswith('win'):
                    subprocess.run([python_installer, '/quiet', 'InstallAllUsers=1', 'PrependPath=1'])
                    os.remove(python_installer)
                else:
                    subprocess.run(['tar', 'xvf', python_installer])
                    os.chdir(f"Python-{version}")
                    subprocess.run(['./configure'])
                    subprocess.run(['make', 'install'])
                    os.chdir('..')
                    os.remove(python_installer)

                messagebox.showinfo("Success", f"Python {version} installed successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Error installing Python {version}: {e}")

if __name__ == "__main__":
    app = ProgramInstaller()
    app.mainloop()
