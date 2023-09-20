import tkinter as tk
from tkinter import scrolledtext
from tkinter import filedialog
import tkinter.messagebox as tk_mb
import os


class Main:
    def __init__(self):
        self.root = tk.Tk()

        main_label = tk.Label(self.root, text="Sphinx Autodoc Text Automator", font=("Arial", 18))
        main_label.grid(row=0, column=0, columnspan=2, pady=10)

        self.avoid_files_frame = tk.Frame(self.root)
        self.avoid_files_frame.grid(row=1, column=0,padx = 5)

        avoid_files_label = tk.Label(self.avoid_files_frame, text="Files to not\nbe included")
        avoid_files_label.grid(row=0)

        self.avoid_files_field = tk.scrolledtext.ScrolledText(self.avoid_files_frame, wrap=tk.WORD, width=20, height=5)
        self.avoid_files_field.grid(row=1)
        self.avoid_files_field.insert(tk.END, self.read_avoid_file())
        self.avoid_files_field.update()

        avoid_files_save_button = tk.Button(self.avoid_files_frame, text="Update avoid.txt",
                                            command=self.update_files_to_avoid)
        avoid_files_save_button.grid(row=2,pady=5)

        self.chosen_folder = ""
        choose_folder_frame = tk.Frame(self.root)
        choose_folder_frame.grid(row=1, column=1)
        choose_folder_button = tk.Button(choose_folder_frame, text="Choose base folder",
                                         command=self.select_folder_dialog)
        choose_folder_button.grid(row=0)

        self.chosen_folder_label = tk.Label(choose_folder_frame, text="No folder chosen")
        self.chosen_folder_label.grid(row=1)

        populate_button = tk.Button(self.root, text="Populate Files", command=self.populate_files)
        populate_button.grid(row=3, column=0,columnspan=2,pady=10)

        self.files_field = tk.scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=50, height=15)
        self.files_field.grid(row=2, column=0,columnspan=2)

        self.root.mainloop()

    def check_if_exists(self):
        print("Dir:")
        print(os.listdir())
        print(os.path.exists("RST Output Files"))
    def read_avoid_file(self):
        files = ""
        with open("avoid.txt","r") as file:
            for line in file:
                files += f"{line}"

        return files

    def update_files_to_avoid(self):
        with open("avoid.txt", "r+") as file:
            user_input = self.avoid_files_field.get("1.0",tk.END).strip()
            file_contents = file.read().strip()

            if file_contents != user_input:

                file.write(user_input)
                tk_mb.showinfo(message="Updated avoid.txt")

    def get_avoid_field_contents(self):
        return list(filter(None, self.avoid_files_field.get("1.0",tk.END).split("\n")))

    def select_folder_dialog(self):
        self.folder_output = ""

        self.chosen_folder = filedialog.askdirectory(initialdir="/")
        self.chosen_folder_label.configure(text=f"Folder chosen: {self.chosen_folder}")

        self.files_field.delete("1.0", tk.END)
        # Scan for only the folders
        has_folders = False
        other_folder_contents = ""
        avoid = self.get_avoid_field_contents()
        for entry in os.scandir(self.chosen_folder):
            if entry.name not in avoid:
                if entry.is_dir():
                    self.folder_output += entry.name + "\n"
                    for file in os.listdir(entry):
                        if file[-3:] == ".py" and file not in avoid:
                            self.folder_output += file + "\n"
                            has_folders = True

                elif entry.is_file():
                    if entry.name[-3:] == ".py":
                        other_folder_contents += f"{entry.name}\n"

        if has_folders:
            if other_folder_contents != "":
                self.folder_output += f"Other\n{other_folder_contents}"

        else:
            self.folder_output = other_folder_contents

        self.files_field.insert(tk.END, self.folder_output)
        self.files_field.update()

    def populate_files(self):
        if self.chosen_folder == "":
            tk_mb.showinfo(message="Error: no source folder chosen")

        else:
            if not os.path.exists("RST Output Files"):
                os.mkdir(f"{os.getcwd()}/RST Output Files")

            current_folder = ""
            current_output = ""
            file_name = ""
            chosen_folder_final_dirs = self.chosen_folder.split("/")[-2:]
            prefix = f"{chosen_folder_final_dirs[0]}.{chosen_folder_final_dirs[1]}"

            for line in self.files_field.get("1.0", tk.END).split("\n"):
                if line != "":
                    if line[-3:] == ".py":
                        if current_folder == "Other":
                            current_output += f"{line}\n{'#' * len(line)}\n.. automodule:: {prefix}.{line[0:-3]}"
                            current_output += "\n    :members:\n    :private-members:\n    :special-members:\n\n"
                        else:
                            current_output += f"{line}\n{'#' * len(line)}\n.. automodule:: {prefix}.{current_folder}.{line[0:-3]}"
                            current_output += "\n    :members:\n    :private-members:\n    :special-members:\n\n"

                    else:
                        if file_name != "":
                            # Write to file
                            with open(f"RST Output Files/{file_name}", "w+") as file:
                                file.write(current_output)

                        file_name = f"{line}.rst"
                        current_folder = line
                        current_output = f".. _{file_name[0:-4]}:\n\n{line}\n{'-' * len(line)}\n"

            #Write last set of output to file
            with open(f"RST Output Files/{file_name}", "w+") as file:
                file.write(current_output)

            tk_mb.showinfo(message="Files Populated")


main = Main()
main.check_if_exists()
