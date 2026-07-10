import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class JellyfinSorterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JellySorter")
        self.root.geometry("900x650")

        # Daten-Speicher
        self.source_dir = ""
        self.files_list = []
        self.season_mapping = {}

        self.create_widgets()

    def create_widgets(self):
        top_frame = ttk.LabelFrame(self.root, text=" 1. Infos ", padding=10)
        top_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(top_frame, text="name:").grid(row=0, column=0, sticky="w", pady=4)
        self.ent_series_name = ttk.Entry(top_frame, width=35)
        self.ent_series_name.grid(row=0, column=1, sticky="w", padx=5, pady=4)
        self.ent_series_name.insert(0, "")
        self.ent_series_name.bind("<KeyRelease>", lambda e: self.update_preview())

        ttk.Label(top_frame, text="Year (optional):").grid(row=0, column=2, sticky="w", pady=4, padx=(15, 0))
        self.ent_year = ttk.Entry(top_frame, width=10)
        self.ent_year.grid(row=0, column=3, sticky="w", padx=5, pady=4)
        self.ent_year.bind("<KeyRelease>", lambda e: self.update_preview())

        ttk.Label(top_frame, text="Metadata ID (optional):").grid(row=1, column=0, sticky="w", pady=4)
        self.ent_meta_id = ttk.Entry(top_frame, width=35)
        self.ent_meta_id.grid(row=1, column=1, sticky="w", padx=5, pady=4)
        self.ent_meta_id.insert(0, "")
        self.ent_meta_id.bind("<KeyRelease>", lambda e: self.update_preview())

        ttk.Label(top_frame, text="Format: tvdb-123456 or tmdb-12345", foreground="gray",
                  font=("Arial", 8)).grid(row=1, column=2, columnspan=2, sticky="w", padx=5, pady=4)

        ttk.Separator(top_frame, orient="horizontal").grid(row=2, column=0, columnspan=4, sticky="ew", pady=8)

        ttk.Label(top_frame, text="selected folder:").grid(row=3, column=0, sticky="w", pady=4)
        self.lbl_folder = ttk.Label(top_frame, text="No Folder Selected ?", foreground="gray")
        self.lbl_folder.grid(row=3, column=1, columnspan=2, sticky="w", padx=5, pady=4)

        btn_browse = ttk.Button(top_frame, text="Open Folder", command=self.browse_folder)
        btn_browse.grid(row=3, column=3, padx=5, pady=4, sticky="e")

        mid_frame = ttk.LabelFrame(self.root, text=" 2. Sort everything ", padding=10)
        mid_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("raw_file", "season", "preview")
        self.tree = ttk.Treeview(mid_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("raw_file", text="File")
        self.tree.heading("season", text="Season")
        self.tree.heading("preview", text="Preview")

        self.tree.column("raw_file", width=230)
        self.tree.column("season", width=100, anchor="center")
        self.tree.column("preview", width=450)
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(mid_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_file_select)

        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill="x", padx=10)

        self.lbl_selected_info = ttk.Label(control_frame, text="Select File...", font=("Arial", 10, "bold"))
        self.lbl_selected_info.pack(side="left", padx=5)

        btn_minus = ttk.Button(control_frame, text=" Season - ", width=10, command=lambda: self.change_season(-1))
        btn_minus.pack(side="right", padx=2)

        btn_plus = ttk.Button(control_frame, text=" Season + ", width=10, command=lambda: self.change_season(1))
        btn_plus.pack(side="right", padx=5)

        bottom_frame = ttk.Frame(self.root, padding=10)
        bottom_frame.pack(fill="x")

        btn_rename = ttk.Button(bottom_frame, text="Sort (renamefiles + sortfiles)",
                                command=self.start_processing)
        btn_rename.pack(fill="x", ipady=8)

    def browse_folder(self):
        directory = filedialog.askdirectory()
        if directory:
            self.source_dir = directory
            self.lbl_folder.config(text=directory, foreground="black")
            self.load_files()

    def load_files(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.season_mapping.clear()

        extensions = ('.mp4', '.mkv')
        self.files_list = sorted([f for f in os.listdir(self.source_dir) if f.lower().endswith(extensions)])

        if not self.files_list:
            messagebox.showinfo("Info", "No MP4 / MKV found in the folder")
            return

        for filename in self.files_list:
            self.season_mapping[filename] = 1

        self.update_tree_view()

    def update_preview(self):
        if not self.source_dir:
            return

        series_name = self.ent_series_name.get().strip()
        if not series_name:
            series_name = "Unbekannt"

        # Optionale Felder auslesen
        year = self.ent_year.get().strip()
        meta_id = self.ent_meta_id.get().strip()

        display_series_name = f"{series_name} ({year})" if year else series_name

        folder_suffix = f" [{meta_id}]" if meta_id else ""
        main_folder_preview = f"{display_series_name}{folder_suffix}"

        episode_counters = {}

        for item in self.tree.get_children():
            filename = self.tree.item(item, "values")[0]
            season = self.season_mapping[filename]
            ext = os.path.splitext(filename)[1]

            if season not in episode_counters:
                episode_counters[season] = 1
            else:
                episode_counters[season] += 1

            ep_num = episode_counters[season]

            new_filename = f"{display_series_name} - S{season:02d}E{ep_num:02d}{ext}"

            target_preview = f"{main_folder_preview} / Season {season:02d} / {new_filename}"

            self.tree.item(item, values=(filename, f"Season {season:02d}", target_preview))

    def update_tree_view(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for filename in self.files_list:
            self.tree.insert("", "end", values=(filename, "Season 01", ""))

        self.update_preview()

    def on_file_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            filename = self.tree.item(selected_item[0], "values")[0]
            current_season = self.season_mapping[filename]
            self.lbl_selected_info.config(text=f"Aktiv: {filename} (S{current_season:02d})")

    def change_season(self, delta):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warnung", "Please select a file out of the list")
            return

        filename = self.tree.item(selected_item[0], "values")[0]
        current_season = self.season_mapping[filename]

        new_season = current_season + delta
        if new_season < 1:
            new_season = 1

        self.season_mapping[filename] = new_season
        self.on_file_select(None)
        self.update_preview()

    def start_processing(self):
        if not self.source_dir:
            messagebox.showerror("Fehler", "Please select a folder first :)")
            return

        series_name = self.ent_series_name.get().strip()
        if not series_name:
            messagebox.showerror("Fehler", "Please put in a Name")
            return

        confirm = messagebox.askyesno("Fortfahren?",
                                      "Are you sure you want to start the process?")
        if not confirm:
            return

        year = self.ent_year.get().strip()
        meta_id = self.ent_meta_id.get().strip()

        display_series_name = f"{series_name} ({year})" if year else series_name
        folder_suffix = f" [{meta_id}]" if meta_id else ""

        main_folder_name = f"{display_series_name}{folder_suffix}"
        root_series_path = os.path.join(self.source_dir, main_folder_name)

        episode_counters = {}
        success_count = 0

        for filename in self.files_list:
            season = self.season_mapping[filename]
            ext = os.path.splitext(filename)[1]

            if season not in episode_counters:
                episode_counters[season] = 1
            else:
                episode_counters[season] += 1

            ep_num = episode_counters[season]

            season_folder_name = f"Season {season:02d}"
            target_folder_path = os.path.join(root_series_path, season_folder_name)

            if not os.path.exists(target_folder_path):
                os.makedirs(target_folder_path)

            # Neuer Dateiname
            new_filename = f"{display_series_name} - S{season:02d}E{ep_num:02d}{ext}"

            old_full_path = os.path.join(self.source_dir, filename)
            new_full_path = os.path.join(target_folder_path, new_filename)

            try:
                os.rename(old_full_path, new_full_path)
                success_count += 1
            except Exception as e:
                messagebox.showerror("Fehler", f"Error moving file {filename}:\n{str(e)}")

        messagebox.showinfo("Erfolgreich",
                            f"Done! {success_count} File are sorted '{main_folder_name}'")
        self.load_files()


if __name__ == "__main__":
    root = tk.Tk()
    app = JellyfinSorterApp(root)
    root.mainloop()
