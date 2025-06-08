import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import os
import copy  # Important for batch processing (Tab 2)

# --- Core Definitions and Functions (Logic Modified) ---

# Keys whose values will be directly replaced if found in both source and target.
KEYS_TO_REPLACE_VALUES = [
    "m_FileID",
    "m_PathID",
    "m_Name",
    "m_SourceFontFileGUID",
    "m_FamilyName",
    "m_StyleName",
    "sourceFontFileGUID"
]

# Keys containing an "Array" that should have its entire content replaced.
# This handles nested structures.
KEYS_WITH_ARRAY_TO_REPLACE = {
    "m_FallbackFontAssetTable": "Array",
    "m_FontFeatureTable": {
        "m_GlyphPairAdjustmentRecords": "Array"
    }
}

# <<<--- NEW ADDITION ---<<<
# Keys to add to the target if they exist in the source but are missing in the target.
# This is useful for newer versions of the format that add fields.
# To solve your specific case, add "m_ClassDefinitionType" to this list.
KEYS_TO_ADD_IF_MISSING = [
    "m_UnitsPerEM",
    "m_ClassDefinitionType" # Added based on your request
]


def update_json_recursively(target_node, source_node, log_area):
    """
    Recursively updates the target_node based on the source_node.
    It follows the rules defined in the global KEY constants and adds missing keys.
    """
    if not isinstance(target_node, type(source_node)):
        return

    if isinstance(target_node, dict):
        # --- 1. Update existing keys ---
        for key in list(target_node.keys()): # Use list to avoid issues with dict size changing
            if key in source_node:
                source_value = source_node[key]
                target_value = target_node[key]

                if key in KEYS_TO_REPLACE_VALUES:
                    if target_node[key] != source_value:
                        log_area.insert(tk.END, f"Updating '{key}': from '{target_node[key]}' to '{source_value}'\n")
                        target_node[key] = source_value
                    else:
                        log_area.insert(tk.END, f"Key '{key}': Value already matches ('{source_value}'). No change.\n")

                elif key in KEYS_WITH_ARRAY_TO_REPLACE:
                    path_to_array = KEYS_WITH_ARRAY_TO_REPLACE[key]
                    current_target_level = target_value
                    current_source_level = source_value
                    valid_path = True

                    if isinstance(path_to_array, str): # Simple case: {"key": "Array"}
                        if isinstance(current_target_level, dict) and path_to_array in current_target_level and \
                           isinstance(current_source_level, dict) and path_to_array in current_source_level:
                            if current_target_level[path_to_array] != current_source_level[path_to_array]:
                                log_area.insert(tk.END, f"Updating nested Array in '{key}.{path_to_array}'\n")
                                current_target_level[path_to_array] = current_source_level[path_to_array]
                            else:
                                log_area.insert(tk.END, f"Nested Array in '{key}.{path_to_array}' already matches. No change.\n")
                        else:
                            valid_path = False

                    elif isinstance(path_to_array, dict): # Nested case: {"key": {"nested_key": "Array"}}
                        nested_key = list(path_to_array.keys())[0]
                        array_key_in_nested = path_to_array[nested_key]

                        if isinstance(current_target_level, dict) and nested_key in current_target_level and \
                           isinstance(current_target_level[nested_key], dict) and array_key_in_nested in current_target_level[nested_key] and \
                           isinstance(current_source_level, dict) and nested_key in current_source_level and \
                           isinstance(current_source_level[nested_key], dict) and array_key_in_nested in current_source_level[nested_key]:
                            if current_target_level[nested_key][array_key_in_nested] != current_source_level[nested_key][array_key_in_nested]:
                                log_area.insert(tk.END, f"Updating nested Array in '{key}.{nested_key}.{array_key_in_nested}'\n")
                                current_target_level[nested_key][array_key_in_nested] = current_source_level[nested_key][array_key_in_nested]
                            else:
                                log_area.insert(tk.END, f"Nested Array in '{key}.{nested_key}.{array_key_in_nested}' already matches. No change.\n")
                        else:
                            valid_path = False

                    if not valid_path:
                        log_area.insert(tk.END, f"Skipping '{key}': Structure for Array replacement not found or mismatched.\n")

                elif isinstance(target_value, (dict, list)):
                    # Continue recursion for other nested structures.
                    update_json_recursively(target_value, source_value, log_area)

        # <<<--- NEW LOGIC ---<<<
        # --- 2. Add missing keys from source (as defined in KEYS_TO_ADD_IF_MISSING) ---
        for key, source_value in source_node.items():
            if key in KEYS_TO_ADD_IF_MISSING and key not in target_node:
                log_area.insert(tk.END, f"Adding missing key '{key}' with value '{source_value}'\n")
                target_node[key] = source_value # Add the key-value pair to the target dictionary

    elif isinstance(target_node, list):
        # Recursively process items in a list.
        # This part remains the same, assuming list items are matched by index.
        for i in range(min(len(target_node), len(source_node))):
            if isinstance(target_node[i], (dict, list)) and isinstance(source_node[i], (dict, list)):
                update_json_recursively(target_node[i], source_node[i], log_area)

# --- Main Application Class (GUI code remains the same) ---
# ... (The rest of the GUI code is unchanged) ...

# ADDITION: Constants for help text
HELP_TEXT_SINGLE = """# Single File #

How to use:
1 - In 'Source File (Original)', select an SDF JSON file.
    (e.g., Alegreya-Regular SDF-resources.assets.json)

2 - In 'Target File (To Patch)', select the SDF JSON file you want to modify.
    (e.g., NotoSansArabic-Regular SDF-resources.assets.json)

3 - Click 'Process and Patch Single File' and choose where to save the new file.
    The saved file will be named based on the source file.
    (e.g., Alegreya-Regular SDF-resources.assets_modified.json)
"""

HELP_TEXT_BATCH_TEMPLATE = """# Batch (One-style) #

How to use:
1 - In 'Source Folder', select a folder containing multiple source SDF JSON files.
    Example folder contents:
    - Alegreya-Regular SDF-resources.assets.json
    - Alegreya-Medium SDF-resources.assets.json
    - Alegreya-Italic SDF-resources.assets.json

2 - In 'Target Single File', select one SDF JSON file to use as a same style for patching.
    (e.g., NotoSansArabic-Regular SDF-resources.assets.json)

3 - Click the process button and select an output folder.
    Each source file will be patched using the template and saved in the output folder with its original name.
"""

HELP_TEXT_BATCH_MAP = """# Batch (Multi-style) #

How to use:
1 - In 'Source Folder', select a folder with your source SDF JSON files.
    Example folder contents:
    - Alegreya-Regular SDF-resources.assets.json
    - Alegreya-Medium SDF-resources.assets.json
    - Alegreya-Italic SDF-resources.assets.json

2 - In 'Target Folder', select a folder with the corresponding target SDF JSON files to be patched.
    Example folder contents:
    - NotoSansArabic-Regular SDF-resources.assets.json
    - NotoSansArabic-Medium SDF-resources.assets.json
    - NotoSansArabic-Italic SDF-resources.assets.json

    IMPORTANT: Both folders must have the same number of .json files, and they must be sorted alphabetically to match correctly.

3 - Click the process button and select an output folder.
    Each patched file will be saved with the name of its corresponding source file.
"""


class SdfFontPatcherApp:
    """
    A GUI application for patching JSON-based SDF Font Asset files.
    """
    def __init__(self, master):
        self.master = master
        master.title("SDF Font JSON Editor By MrGamesKingPro")
        master.geometry("850x650")
        master.minsize(700, 500)

        # Main notebook for tabs
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Create frames for each tab
        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.tab3 = ttk.Frame(self.notebook)

        self.notebook.add(self.tab1, text='Single File')
        self.notebook.add(self.tab2, text='Batch (One-style)')
        self.notebook.add(self.tab3, text='Batch (Multi-style)')

        # Build the UI for each tab
        self.create_single_file_tab()
        self.create_batch_template_tab()
        self.create_folder_to_folder_tab()

        # ADDITION: Bind tab change event to update help text
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # ADDITION: Set initial help text for the first tab on launch
        self.on_tab_changed(None)


    # --- UI Creation ---

    def _create_path_selector(self, parent, row_index, label_text, string_var, is_folder=False):
        """Helper function to create a labeled path entry with a browse button using grid."""
        label = ttk.Label(parent, text=label_text)
        label.grid(row=row_index, column=0, sticky='w', padx=5, pady=5)

        entry = ttk.Entry(parent, textvariable=string_var)
        entry.grid(row=row_index, column=1, sticky='ew', padx=5, pady=5)

        if is_folder:
            command = lambda: self.select_folder(string_var, f"Select {label_text}")
            btn_text = "Browse Folder..."
        else:
            command = lambda: self.select_file(string_var, f"Select {label_text}")
            btn_text = "Browse File..."

        button = ttk.Button(parent, text=btn_text, command=command)
        button.grid(row=row_index, column=2, sticky='e', padx=5, pady=5)


    def _setup_tab_grid(self, tab_frame):
        """Helper to configure the main grid layout for a tab."""
        tab_frame.grid_columnconfigure(0, weight=1)
        tab_frame.grid_rowconfigure(1, weight=1)

    def _setup_input_frame(self, parent_tab):
        """Helper to create and configure the 'Inputs' frame."""
        frame = ttk.LabelFrame(parent_tab, text="Configuration")
        frame.grid(row=0, column=0, sticky='ew', padx=5, pady=(5, 10))
        frame.grid_columnconfigure(1, weight=1) # Allow the entry column to stretch
        return frame


    def create_single_file_tab(self):
        parent = self.tab1
        self._setup_tab_grid(parent)

        inputs_frame = self._setup_input_frame(parent)

        self.source_file_path_single = tk.StringVar()
        self.target_file_path_single = tk.StringVar()

        self._create_path_selector(inputs_frame, 0, "Source File (Original):", self.source_file_path_single)
        self._create_path_selector(inputs_frame, 1, "Target File (To Patch):", self.target_file_path_single)

        process_button = ttk.Button(inputs_frame, text="Process and Patch Single File", command=self.process_single_file, style='Accent.TButton')
        process_button.grid(row=2, column=0, columnspan=3, sticky='ew', pady=(10, 5), padx=5)

        log_frame = ttk.LabelFrame(parent, text="Log")
        log_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        self.log_area_single = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=10)
        self.log_area_single.pack(expand=True, fill='both', padx=5, pady=5)


    def create_batch_template_tab(self):
        parent = self.tab2
        self._setup_tab_grid(parent)

        inputs_frame = self._setup_input_frame(parent)

        self.source_folder_path_batch = tk.StringVar()
        self.target_template_file_path = tk.StringVar()

        self._create_path_selector(inputs_frame, 0, "Source Folder:", self.source_folder_path_batch, is_folder=True)
        self._create_path_selector(inputs_frame, 1, "Target Single File:", self.target_template_file_path)

        process_button = ttk.Button(inputs_frame, text="Process Batch Based On Single File", command=self.process_batch_template_mode, style='Accent.TButton')
        process_button.grid(row=2, column=0, columnspan=3, sticky='ew', pady=(10, 5), padx=5)

        log_frame = ttk.LabelFrame(parent, text="Log")
        log_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        self.log_area_batch_template = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=10)
        self.log_area_batch_template.pack(expand=True, fill='both', padx=5, pady=5)


    def create_folder_to_folder_tab(self):
        parent = self.tab3
        self._setup_tab_grid(parent)

        inputs_frame = self._setup_input_frame(parent)

        self.source_folder_path_map = tk.StringVar()
        self.target_folder_path_map = tk.StringVar()

        self._create_path_selector(inputs_frame, 0, "Source Folder:", self.source_folder_path_map, is_folder=True)
        self._create_path_selector(inputs_frame, 1, "Target Folder:", self.target_folder_path_map, is_folder=True)

        process_button = ttk.Button(inputs_frame, text="Process Matched Folders One By One", command=self.process_folder_to_folder, style='Accent.TButton')
        process_button.grid(row=2, column=0, columnspan=3, sticky='ew', pady=(10, 5), padx=5)

        log_frame = ttk.LabelFrame(parent, text="Log")
        log_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        self.log_area_map = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=10)
        self.log_area_map.pack(expand=True, fill='both', padx=5, pady=5)


    # --- Event Handlers ---

    def on_tab_changed(self, event):
        """Called when the user switches tabs. Clears and displays the relevant help text."""
        selected_tab_index = self.notebook.index(self.notebook.select())

        if selected_tab_index == 0:
            log_area = self.log_area_single
            help_text = HELP_TEXT_SINGLE
        elif selected_tab_index == 1:
            log_area = self.log_area_batch_template
            help_text = HELP_TEXT_BATCH_TEMPLATE
        elif selected_tab_index == 2:
            log_area = self.log_area_map
            help_text = HELP_TEXT_BATCH_MAP
        else:
            return # Should not happen

        log_area.delete('1.0', tk.END)
        log_area.insert('1.0', help_text)

    # --- File/Folder Selection Dialogs (Unchanged) ---

    def select_file(self, string_var, title):
        filepath = filedialog.askopenfilename(
            title=title,
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        if filepath:
            string_var.set(filepath)

    def select_folder(self, string_var, title):
        folderpath = filedialog.askdirectory(title=title)
        if folderpath:
            string_var.set(folderpath)


    # --- Processing Logic ---

    def process_single_file(self):
        log_area = self.log_area_single
        log_area.delete('1.0', tk.END)
        source_path = self.source_file_path_single.get()
        target_path = self.target_file_path_single.get()

        if not source_path or not target_path:
            messagebox.showerror("Error", "Please select both a source and a target file.")
            log_area.insert(tk.END, "Error: Missing file paths.\n")
            return

        try:
            with open(source_path, 'r', encoding='utf-8') as f: source_data = json.load(f)
            log_area.insert(tk.END, f"Loaded source file: {source_path}\n")
            with open(target_path, 'r', encoding='utf-8') as f: target_data = json.load(f)
            log_area.insert(tk.END, f"Loaded target file: {target_path}\n")
        except Exception as e:
            messagebox.showerror("File Read Error", f"Could not read or parse one of the JSON files:\n{e}")
            log_area.insert(tk.END, f"Error loading files: {e}\n")
            return

        log_area.insert(tk.END, "\n--- Starting update process ---\n")
        update_json_recursively(target_data, source_data, log_area)
        log_area.insert(tk.END, "--- Update process finished ---\n\n")

        try:
            source_base, source_ext = os.path.splitext(os.path.basename(source_path))
            save_path = filedialog.asksaveasfilename(
                title="Save Patched File As...",
                initialfile=f"{source_base}_modified{source_ext}",
                defaultextension=".json",
                filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
            )
            if save_path:
                with open(save_path, 'w', encoding='utf-8') as f:
                    json.dump(target_data, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Success", f"File successfully patched and saved to:\n{save_path}")
                log_area.insert(tk.END, f"Patched file saved to: {save_path}\n")
            else:
                log_area.insert(tk.END, "Save operation was cancelled.\n")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save the patched file:\n{e}")
            log_area.insert(tk.END, f"Error saving file: {e}\n")


    def process_batch_template_mode(self):
        log_area = self.log_area_batch_template
        log_area.delete('1.0', tk.END)

        source_folder = self.source_folder_path_batch.get()
        target_template_path = self.target_template_file_path.get()

        if not source_folder or not target_template_path:
            messagebox.showerror("Error", "Please select a source folder and a target template file.")
            log_area.insert(tk.END, "Error: Incomplete inputs.\n")
            return

        if not os.path.isdir(source_folder):
            messagebox.showerror("Error", "The specified source path is not a valid folder.")
            log_area.insert(tk.END, "Error: Source path is not a folder.\n")
            return

        output_folder = filedialog.askdirectory(title="Select a folder to save the patched files")
        if not output_folder:
            log_area.insert(tk.END, "Operation cancelled. No output folder was selected.\n")
            return

        try:
            with open(target_template_path, 'r', encoding='utf-8') as f:
                target_template_data = json.load(f)
            log_area.insert(tk.END, f"Loaded target template file: {target_template_path}\n\n")
        except Exception as e:
            messagebox.showerror("Target File Error", f"Could not read or parse the target template file:\n{e}")
            log_area.insert(tk.END, f"Error loading target template: {e}\n")
            return

        log_area.insert(tk.END, f"--- Starting batch process for folder: {source_folder} ---\n")
        processed_count = 0
        source_files = [f for f in os.listdir(source_folder) if f.lower().endswith('.json')]

        if not source_files:
            messagebox.showwarning("Warning", "The source folder contains no .json files.")
            log_area.insert(tk.END, "No .json files found in the source folder.\n")
            return

        for filename in source_files:
            source_path = os.path.join(source_folder, filename)
            log_area.insert(tk.END, f"\n--- Processing: {filename} ---\n")

            try:
                with open(source_path, 'r', encoding='utf-8') as f:
                    source_data = json.load(f)

                target_data_copy = copy.deepcopy(target_template_data)
                update_json_recursively(target_data_copy, source_data, log_area)

                output_path = os.path.join(output_folder, filename)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(target_data_copy, f, indent=2, ensure_ascii=False)

                log_area.insert(tk.END, f"Successfully saved to: {output_path}\n")
                processed_count += 1
            except Exception as e:
                log_area.insert(tk.END, f"!!! FAILED to process {filename}: {e}\n")

        log_area.insert(tk.END, f"\n--- Batch process finished. Processed {processed_count} of {len(source_files)} files. ---\n")
        messagebox.showinfo("Processing Complete", f"{processed_count} files were processed successfully.\nOutput saved to:\n{output_folder}")


    def process_folder_to_folder(self):
        log_area = self.log_area_map
        log_area.delete('1.0', tk.END)

        source_folder = self.source_folder_path_map.get()
        target_folder = self.target_folder_path_map.get()

        if not source_folder or not target_folder:
            messagebox.showerror("Error", "Please select both a source and a target folder.")
            log_area.insert(tk.END, "Error: Incomplete inputs.\n")
            return

        if not os.path.isdir(source_folder) or not os.path.isdir(target_folder):
            messagebox.showerror("Error", "One of the specified paths is not a valid folder.")
            log_area.insert(tk.END, "Error: Source or target path is not a folder.\n")
            return

        output_folder = filedialog.askdirectory(title="Select a folder to save the results")
        if not output_folder:
            log_area.insert(tk.END, "Operation cancelled. No output folder was selected.\n")
            return

        log_area.insert(tk.END, "Scanning for .json files in both folders...\n")
        source_files = sorted([f for f in os.listdir(source_folder) if f.lower().endswith('.json')])
        target_files = sorted([f for f in os.listdir(target_folder) if f.lower().endswith('.json')])

        if not source_files:
            messagebox.showwarning("Warning", "No .json files found in the source folder.")
            log_area.insert(tk.END, "No files found in source folder.\n")
            return

        if len(source_files) != len(target_files):
            messagebox.showerror("File Count Mismatch",
                f"The number of .json files does not match!\n\n"
                f"Source Folder: {len(source_files)} files\n"
                f"Target Folder: {len(target_files)} files\n\n"
                "Please ensure both folders contain the same number of JSON files to be matched.")
            log_area.insert(tk.END, f"Error: File count mismatch. Source: {len(source_files)}, Target: {len(target_files)}.\n")
            return

        log_area.insert(tk.END, f"Found {len(source_files)} files to match and process.\n\n--- Starting matched folder process ---\n")
        processed_count = 0

        for i in range(len(source_files)):
            source_filename = source_files[i]
            target_filename = target_files[i]
            source_path = os.path.join(source_folder, source_filename)
            target_path = os.path.join(target_folder, target_filename)

            log_area.insert(tk.END, f"\n--- Matching '{source_filename}'  ->  '{target_filename}' ---\n")

            try:
                with open(source_path, 'r', encoding='utf-8') as f:
                    source_data = json.load(f)
                with open(target_path, 'r', encoding='utf-8') as f:
                    target_data = json.load(f)

                update_json_recursively(target_data, source_data, log_area)

                output_path = os.path.join(output_folder, source_filename)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(target_data, f, indent=2, ensure_ascii=False)

                log_area.insert(tk.END, f"Successfully saved to: {output_path}\n")
                processed_count += 1

            except Exception as e:
                log_area.insert(tk.END, f"!!! FAILED to process pair ('{source_filename}', '{target_filename}'): {e}\n")

        log_area.insert(tk.END, f"\n--- Process finished. Processed {processed_count} of {len(source_files)} file pairs. ---\n")
        messagebox.showinfo("Processing Complete", f"{processed_count} file pairs were processed successfully.\nOutput saved to:\n{output_folder}")


if __name__ == "__main__":
    root = tk.Tk()

    style = ttk.Style(root)
    # Use a modern theme if available
    if 'clam' in style.theme_names():
        style.theme_use('clam')
    elif 'vista' in style.theme_names(): # Good fallback on Windows
        style.theme_use('vista')

    # Configure a custom style for the main action buttons
    style.configure('Accent.TButton', font=('Segoe UI', 10, 'bold'), relief="raised")
    # Tweak button color - this can be tricky with some themes, but we can try.
    try:
        style.map('Accent.TButton',
            foreground=[('!disabled', 'white')],
            background=[('!disabled', '#0078D7'), ('active', '#005a9e')])
    except tk.TclError:
        # Some themes don't allow background/foreground modification.
        # The bold font will still apply.
        pass

    app = SdfFontPatcherApp(root)
    root.mainloop()
