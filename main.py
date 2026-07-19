import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class JellyfinSorterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JellySorter - Jellyfin Media Organizer")
        self.root.geometry("950x700")
        self.root.minsize(800, 600)

        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Data Storage
        self.source_dir = ""
        self.files_list = []
        self.season_mapping = {}

        self.create_widgets()

        self._drag_item = None

    def create_widgets(self):
        top_frame = ttk.LabelFrame(self.root, text=" 1. Series Metadata ", padding=12)
        top_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(top_frame, text="Series Name:").grid(row=0, column=0, sticky="w", pady=4)
        self.ent_series_name = ttk.Entry(top_frame, width=35)
        self.ent_series_name.grid(row=0, column=1, sticky="w", padx=5, pady=4)
        self.ent_series_name.bind("<KeyRelease>", lambda e: self.update_preview())

        ttk.Label(top_frame, text="Year (Optional):").grid(row=0, column=2, sticky="w", pady=4, padx=(15, 0))
        self.ent_year = ttk.Entry(top_frame, width=10)
        self.ent_year.grid(row=0, column=3, sticky="w", padx=5, pady=4)
        self.ent_year.bind("<KeyRelease>", lambda e: self.update_preview())

        ttk.Label(top_frame, text="Metadata ID (Optional):").grid(row=1, column=0, sticky="w", pady=4)
        self.ent_meta_id = ttk.Entry(top_frame, width=35)
        self.ent_meta_id.grid(row=1, column=1, sticky="w", padx=5, pady=4)
        self.ent_meta_id.bind("<KeyRelease>", lambda e: self.update_preview())

        ttk.Label(top_frame, text="Format: tvdb-123456 or tmdb-12345", foreground="gray",
                  font=("Arial", 8, "italic")).grid(row=1, column=2, columnspan=2, sticky="w", padx=5, pady=4)

        ttk.Separator(top_frame, orient="horizontal").grid(row=2, column=0, columnspan=4, sticky="ew", pady=8)

        ttk.Label(top_frame, text="Selected Folder:").grid(row=3, column=0, sticky="w", pady=4)
        self.lbl_folder = ttk.Label(top_frame, text="No folder selected yet", foreground="gray")
        self.lbl_folder.grid(row=3, column=1, columnspan=2, sticky="w", padx=5, pady=4)

        btn_browse = ttk.Button(top_frame, text="Browse Folder", command=self.browse_folder)
        btn_browse.grid(row=3, column=3, padx=5, pady=4, sticky="e")

        mid_frame = ttk.LabelFrame(self.root, text=" 2. Organize & Preview Order (Drag items to reorder) ", padding=12)
        mid_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("raw_file", "season", "preview")
        self.tree = ttk.Treeview(mid_frame, columns=columns, show="headings", selectmode="extended")
        self.tree.heading("raw_file", text="Original File Name")
        self.tree.heading("season", text="Target Season")
        self.tree.heading("preview", text="Jellyfin Target Path Preview")

        self.tree.column("raw_file", width=250, minwidth=150)
        self.tree.column("season", width=110, anchor="center", minwidth=80)
        self.tree.column("preview", width=500, minwidth=300)
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(mid_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_file_select)
        self.tree.bind("<ButtonPress-1>", self.on_drag_start)
        self.tree.bind("<B1-Motion>", self.on_drag_motion)

        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill="x", padx=10)

        self.lbl_selected_info = ttk.Label(control_frame, text="Select files to batch edit seasons...",
                                           font=("Arial", 9, "bold"))
        self.lbl_selected_info.pack(side="left", padx=5)

        btn_plus = ttk.Button(control_frame, text="Season +1", width=12, command=lambda: self.change_season(1))
        btn_plus.pack(side="right", padx=2)

        btn_minus = ttk.Button(control_frame, text="Season -1", width=12, command=lambda: self.change_season(-1))
        btn_minus.pack(side="right", padx=2)

        bottom_frame = ttk.Frame(self.root, padding=10)
        bottom_frame.pack(fill="x")

        btn_rename = ttk.Button(bottom_frame, text="Process Sorting & Rename Files",
                                command=self.start_processing, style="Accent.TButton")
        btn_rename.pack(fill="x", ipady=10)

    def browse_folder(self):
        directory = filedialog.askdirectory()
        if directory:
            self.source_dir = directory
            self.lbl_folder.config(text=directory, foreground="black")
            
            folder_name = os.path.basename(directory)
            match = re.search(r"^(.*?)\s*\((\d{4})\)$", folder_name)
            if match:
                guessed_name, guessed_year = match.groups()
                self.ent_series_name.delete(0, tk.END)
                self.ent_series_name.insert(0, guessed_name)
                self.ent_year.delete(0, tk.END)
                self.ent_year.insert(0, guessed_year)
            else:
                self.ent_series_name.delete(0, tk.END)
                self.ent_series_name.insert(0, folder_name)
                self.ent_year.delete(0, tk.END)

            self.load_files()

    def load_files(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.season_mapping.clear()

        extensions = ('.mp4', '.mkv', '.avi', '.mov')
        self.files_list = sorted([f for f in os.listdir(self.source_dir) if f.lower().endswith(extensions)])

        if not self.files_list:
            messagebox.showinfo("No Files Found",
                                "No valid video files (.mp4, .mkv, .avi, .mov) found in the selected folder.")
            return

        for filename in self.files_list:
            self.season_mapping[filename] = 1

        self.update_tree_view()

    def update_preview(self):
        if not self.source_dir:
            return

        series_name = self.ent_series_name.get().strip()
        if not series_name:
            series_name = "Unknown Series"

        year = self.ent_year.get().strip()
        meta_id = self.ent_meta_id.get().strip()

        display_series_name = f"{series_name} ({year})" if year else series_name
        folder_suffix = f" [{meta_id}]" if meta_id else ""
        main_folder_preview = f"{display_series_name}{folder_suffix}"

        episode_counters = {}

        for item in self.tree.get_children():
            filename = self.tree.item(item, "values")[0]
            season = self.season_mapping.get(filename, 1)
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
        selected_items = self.tree.selection()
        if not selected_items:
            self.lbl_selected_info.config(text="Select files to batch edit seasons...")
            return

        if len(selected_items) == 1:
            filename = self.tree.item(selected_items[0], "values")[0]
            current_season = self.season_mapping.get(filename, 1)
            self.lbl_selected_info.config(text=f"Selected: {filename} (S{current_season:02d})")
        else:
            self.lbl_selected_info.config(text=f"Selected {len(selected_items)} files for batch edit")

    def on_drag_start(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self._drag_item = item

    def on_drag_motion(self, event):
        if not self._drag_item:
            return

        target_item = self.tree.identify_row(event.y)
        if target_item and target_item != self._drag_item:
            
            self.tree.move(self._drag_item, self.tree.parent(target_item), self.tree.index(target_item))
            self.update_preview()

    def change_season(self, delta):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Selection Missing", "Please select one or multiple files from the list first.")
            return

        for item in selected_items:
            filename = self.tree.item(item, "values")[0]
            current_season = self.season_mapping.get(filename, 1)

            new_season = current_season + delta
            if new_season < 1:
                new_season = 1

            self.season_mapping[filename] = new_season

        self.on_file_select(None)
        self.update_preview()

    def start_processing(self):
        if not self.source_dir:
            messagebox.showerror("Error", "Please select a source folder first.")
            return

        series_name = self.ent_series_name.get().strip()
        if not series_name:
            messagebox.showerror("Error", "Please provide a Series Name.")
            return

        confirm = messagebox.askyesno("Confirm Action",
                                      "Are you sure you want to proceed? Files will be moved into structured subfolders.")
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

        ordered_items = self.tree.get_children()

        for item in ordered_items:
            filename = self.tree.item(item, "values")[0]
            season = self.season_mapping.get(filename, 1)
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

            new_filename = f"{display_series_name} - S{season:02d}E{ep_num:02d}{ext}"

            old_full_path = os.path.join(self.source_dir, filename)
            new_full_path = os.path.join(target_folder_path, new_filename)

            try:
                os.rename(old_full_path, new_full_path)
                success_count += 1
            except Exception as e:
                messagebox.showerror("File Error", f"Could not move/rename '{filename}':\n{str(e)}")

        messagebox.showinfo("Success",
                            f"Processing complete! {success_count} files successfully moved into '{main_folder_name}'.")

        self.load_files()


if __name__ == "__main__":
    root = tk.Tk()
    app = JellyfinSorterApp(root)
    root.mainloop()
