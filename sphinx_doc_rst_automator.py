import tkinter as tk
from tkinter import scrolledtext
from tkinter import filedialog
import tkinter.messagebox as tk_mb
import os

class Main:
    def __init__(self):
        self.root = tk.Tk()

        main_label = tk.Label(self.root, text="Sphinx RST File Automator", font=("Arial", 18))
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

        self.chosen_source_folder = ""
        self.chosen_destination_folder = ""

        choose_folder_frame = tk.Frame(self.root)
        choose_folder_frame.grid(row=1, column=1)
        
        python_folder_choice_button = tk.Button(choose_folder_frame,text="Select Python Folder",
                                                command=self.select_python_folder_dialog)
        python_folder_choice_button.grid(row=0)

        self.chosen_python_folder_label = tk.Label(choose_folder_frame,text="No Python folder chosen")
        self.chosen_python_folder_label.grid(row=1)

        choose_source_folder_button = tk.Button(choose_folder_frame, text="Choose source folder",
                                         command=self.select_source_folder_dialog)
        choose_source_folder_button.grid(row=2)

        self.chosen_source_folder_label = tk.Label(choose_folder_frame, text="No folder chosen")
        self.chosen_source_folder_label.grid(row=3)

        chosen_destination_folder_button = tk.Button(choose_folder_frame, text="Choose destination folder",
                                                          command=self.select_destination_folder_dialog)
        chosen_destination_folder_button.grid(row=4)

        self.chosen_destination_label = tk.Label(choose_folder_frame, text="No folder chosen")
        self.chosen_destination_label.grid(row=5)

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

    def select_destination_folder_dialog(self):
        folder_output = ""

        self.chosen_destination_folder = filedialog.askdirectory(initialdir="/")
        self.chosen_destination_label.configure(text=f"Folder chosen: {self.chosen_destination_folder}")


    def select_source_folder_dialog(self):
        folder_output = ""

        self.chosen_source_folder = filedialog.askdirectory(initialdir="/")
        self.chosen_source_folder_label.configure(text=f"Folder chosen: {self.chosen_source_folder}")

        self.files_field.delete("1.0", tk.END)
        # Scan for only the folders
        has_folders = False
        other_folder_contents = ""
        avoid = self.get_avoid_field_contents()
        for entry in os.scandir(self.chosen_source_folder):
            if entry.name not in avoid:
                if entry.is_dir():
                    folder_output += entry.name + "\n"
                    for file in os.listdir(entry):
                        if file[-3:] == ".py" and file not in avoid:
                            folder_output += file + "\n"
                            has_folders = True

                elif entry.is_file():
                    if entry.name[-3:] == ".py":
                        other_folder_contents += f"{entry.name}\n"

        if has_folders:
            if other_folder_contents != "":
                folder_output += f"Other\n{other_folder_contents}"

        else:
            folder_output = other_folder_contents

        self.files_field.insert(tk.END, folder_output)
        self.files_field.update()

    def select_python_folder_dialog(self):
        self.chosen_python_folder = filedialog.askdirectory(initialdir="/")
        self.chosen_python_folder_label.configure(text=f"Folder chosen: {self.chosen_python_folder}")
        

    def populate_files(self):
        if self.chosen_source_folder == "":
            tk_mb.showinfo(message="Error: no source folder chosen")

        else:
            current_folder = ""
            current_output = ""
            file_name = ""
            self.rst_files = []
            chosen_folder_final_dirs = self.chosen_source_folder.split("/")[-2:]
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
                            with open(f"{self.chosen_destination_folder}/{file_name}", "w+") as file:
                                file.write(current_output)

                        file_name = f"{line}.rst"
                        self.rst_files.append(file_name)
                        current_folder = line
                        current_output = f".. _{file_name[0:-4]}:\n\n{line}\n{'-' * len(line)}\n"

            #Write last set of output to file
            if file_name == "":
                file_name = "documentation.rst"
                self.rst_files.append(file_name)
                current_output = (f"Documentation\n-------------\n{current_output}")

            with open(f"{self.chosen_destination_folder}/{file_name}", "w+") as file:
                file.write(current_output)

            with open("index_contents.txt", "r") as index_source_file:
                with open(f"{self.chosen_destination_folder}/index.rst", "w+") as file:
                    file.write(index_source_file.read())

            with open("getting_started_contents.txt", "r+") as getting_started_source_file:
                with open(f"{self.chosen_destination_folder}/getting_started.rst", "w+") as file:
                    file.write(getting_started_source_file.read())

            with open(f"{self.chosen_destination_folder}/generate.bat", "w+") as file:
                directory = os.path.dirname(self.chosen_source_folder)
                #directory = f"../{str(directory).split('/')[-1]}"
                file.write(f"{self.chosen_python_folder}\scripts\sphinx-autobuild source build/html --watch {directory}\npause")


            with open(f"{self.chosen_destination_folder}/index.rst", 'r') as index_file:
                with open("temp_file.rst","w") as temp_file:
                    for line in index_file:
                        temp_file.write(line)
                        if ":caption: Getting Started" in line:
                            temp_file.write("\n\n   getting_started.rst\n")

                            for file_name in self.rst_files:
                                print(file_name)
                                temp_file.write(f"   {file_name}\n")

            os.replace("temp_file.rst", f"{self.chosen_destination_folder}/index.rst")

            tk_mb.showinfo(message="Files Populated")


main = Main()
main.check_if_exists()
