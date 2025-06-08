
# Based on Requirements

[Unity](https://unity.com/fr/download)
[RTLTMPro](https://github.com/pnarimani/RTLTMPro)
[UABEA](https://github.com/nesrak1/UABEA)

# SDF-Font-JSON-Editor
This tool describes the **SDF Font JSON Editor**, a desktop application designed to modify and update JSON files that represent Signed Distance Field (SDF) Font Assets. These files are commonly used in game development (e.g., with Unity's TextMesh Pro) and contain detailed information about a font's metrics, characters, and fallback options.

### Download tool SDF-Font-JSON-Editor

![a](https://github.com/user-attachments/assets/9da5aa1f-123c-49d3-b487-c1ec960fb42b)

**How to Use Each Tab:**

**Tab 1: Single File**

*   **Purpose:** To patch a single target SDF JSON file using data from a single source SDF JSON file.
*   **How to use:**
    1.  **Source File (Original):** Click "Browse File..." and select the SDF JSON file that contains the "correct" or "master" data.
        *   *Example:* `Alegreya-Regular SDF-resources.assets.json`
    2.  **Target File (To Patch):** Click "Browse File..." and select the SDF JSON file you want to modify.
        *   *Example:* `NotoSansArabic-Regular SDF-resources.assets.json`
    3.  **Process:** Click the "Process and Patch Single File" button.
    4.  **Save:** A "Save As" dialog will appear. Choose a name and location for the patched file. By default, it suggests a name like `[SourceFileName]_modified.json` (e.g., `Alegreya-Regular SDF-resources.assets_modified.json`).
*   **Log Area:** Will show "Updating 'key': from 'old_value' to 'new_value'" or "Adding missing key 'key'..." messages, and finally, a success or error message.

**Tab 2: Batch (One-style)**

*   **Purpose:** To patch multiple source SDF JSON files, applying the same *style* or *structure* from a single "template" target file to all of them. The values for keys like `m_Name`, `m_FileID`, etc., will still come from *each individual source file*.
*   **How to use:**
    1.  **Source Folder:** Click "Browse Folder..." and select a folder containing multiple source SDF JSON files you want to process.
        *   *Example folder contents:*
            *   `Alegreya-Regular SDF-resources.assets.json`
            *   `Alegreya-Medium SDF-resources.assets.json`
            *   `Alegreya-Italic SDF-resources.assets.json`
    2.  **Target Single File:** Click "Browse File..." and select a single SDF JSON file that will act as the template for the structure and for any target-specific data that isn't directly replaced from the source.
        *   *Example:* `NotoSansArabic-Regular SDF-resources.assets.json` (This template will be used for all files in the source folder).
    3.  **Process:** Click the "Process Batch Based On Single File" button.
    4.  **Select Output Folder:** A dialog will ask you to select a folder where the patched files will be saved.
*   **Output:** Each source file (e.g., `Alegreya-Regular SDF-resources.assets.json`) will be processed using a *copy* of the target template file, and the result will be saved in the chosen output folder with its original name (e.g., `Alegreya-Regular SDF-resources.assets.json` in the output folder).
*   **Log Area:** Will show progress for each file being processed.

**Tab 3: Batch (Multi-style)**

*   **Purpose:** To patch multiple target files, where each target file is matched with a corresponding source file. This is useful if you have, for example, a set of "old style" fonts and a corresponding set of "new style" fonts and want to update each old one with its new counterpart.
*   **How to use:**
    1.  **Source Folder:** Click "Browse Folder..." and select the folder containing your source SDF JSON files.
        *   *Example folder contents:*
            *   `Alegreya-Regular SDF-resources.assets.json`
            *   `Alegreya-Medium SDF-resources.assets.json`
            *   `Alegreya-Italic SDF-resources.assets.json`
    2.  **Target Folder:** Click "Browse Folder..." and select the folder containing the corresponding target SDF JSON files that you want to patch.
        *   *Example folder contents:*
            *   `NotoSansArabic-Regular SDF-resources.assets.json`
            *   `NotoSansArabic-Medium SDF-resources.assets.json`
            *   `NotoSansArabic-Italic SDF-resources.assets.json`
    3.  **IMPORTANT Matching:**
        *   Both folders **must have the same number of `.json` files.**
        *   The files are **matched based on their alphabetical order** within their respective folders. So, the first file in the source folder (alphabetically) will be matched with the first file in the target folder (alphabetically), and so on. Ensure your file naming allows for correct pairing when sorted.
    4.  **Process:** Click the "Process Matched Folders One By One" button.
    5.  **Select Output Folder:** A dialog will ask you to select a folder where the patched files will be saved.
*   **Output:** Each target file will be patched using its corresponding source file. The patched files will be saved in the output folder, and they will be named after their **corresponding source file name**.
    *   For example, if `SourceFolder/Alegreya-Regular.json` is matched with `TargetFolder/NotoSans-Regular.json`, the output will be `OutputFolder/Alegreya-Regular.json` (containing the patched data from `NotoSans-Regular.json`).
*   **Log Area:** Will show progress for each pair of files being matched and processed.

---

**General Tips:**

*   **Backup Your Files:** Before using the tool, especially on important files, it's always a good idea to back up your original target files.
*   **JSON Format:** The tool expects valid JSON files. If a file is not correctly formatted, you'll likely see an error in the log.
*   **Check the Log:** The log area provides valuable feedback on what the tool is doing. If something doesn't work as expected, the log is the first place to look for clues.

This tool should be very helpful for users who frequently work with these SDF Font Asset JSON files and need a consistent way to update or transfer specific information between them.
