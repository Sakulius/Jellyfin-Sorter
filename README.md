# JellySorter 🎬

A lightweight, local Python GUI utility designed to instantly rename and organize raw video files into a clean, hierarchical structure that strictly follows the **Jellyfin Media Server** naming conventions.

No more manual renaming or mismatched metadata. Just load your folder, tweak the order, and let JellySorter handle the rest.

---

## ✨ Features

*   **Automated Structuring:** Creates a master series folder—complete with optional year and metadata IDs (TVDB/TMDB)—and places episodes into proper `Season XX` subdirectories.
*   **Drag & Drop Reordering:** Perfect for fixing messy files. Drag rows up or down in the UI to instantly change the chronological episode order (`E01`, `E02`, etc.) before processing.
*   **Batch Season Editing:** Select multiple files at once and increase/decrease their target season with a single click.
*   **Smart Guessing:** Automatically extracts the series name and release year directly from your source directory name upon loading.
*   **Wide Format Support:** Works flawlessly with `.mp4`, `.mkv`, `.avi`, and `.mov` files.
*   **Instant Visual Preview:** See exactly how your final path and filenames will look in real-time as you type or change seasons.

---

## 📁 How It Organizes Your Media

Simply dump your raw video files into a temporary folder, open it with JellySorter, and configure your settings. The tool transforms chaotic files into a pristine Jellyfin layout:

```text
📂 Your Selected Folder/
 ┗ 📂 Show Name (Year) [tmdb-12345]/
   ┣ 📂 Season 01/
   ┃ ┣ 📜 Show Name (Year) - S01E01.mkv
   ┃ ┣ 📜 Show Name (Year) - S01E02.mp4
   ┃ ┗ 📜 Show Name (Year) - S01E03.mkv
   ┗ 📂 Season 02/
     ┗ 📜 Show Name (Year) - S02E01.mkv
