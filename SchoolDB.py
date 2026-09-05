# import the tkinter messagebox and simpledialog, Json and os
import sv_ttk
import json
import os
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

'''
=========================================
          STUDENT DATA MODEL
=========================================
'''
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

json_path = os.path.join(application_path, "Data.json")

class Student:
    def __init__(self, name, student_id, grades=None):
        self.name = name
        self.student_id = student_id

        # Safely isolate dictionaries for each unique instance
        if grades is None:
            self.grades = {'math': [], 'chemistry': [], 'biology': [], 'physics': []}
        else:
            self.grades = grades

    def update_existing_grade(self, subject, score):
        if subject not in self.grades:
            print(f"Error: Cannot add grade. '{subject}' is not an existing subject.")
            return False

        # Ensure the input score is a valid number
        if not isinstance(score, (int, float)):
            print(f"Error: Grade must be a number, not {type(score).__name__}.")
            return False

        # Ensure the score is within logical boundaries
        if not (0 <= score <= 100):
            print(f"Error: Grade {score} is out of bounds (must be between 0 and 100).")
            return False

        self.grades[subject].append(score)
        return True

    def remove_grade_by_index(self, subject, index):
        """Removes a specific grade score from a subject using its list position index."""
        if subject not in self.grades:
            print(f"Error: Subject '{subject}' does not exist.")
            return False

        try:
            idx = int(index)
            if idx < 0 or idx >= len(self.grades[subject]):
                print(f"Error: Index {idx} is out of bounds for subject '{subject}'.")
                return False

            self.grades[subject].pop(idx)
            return True
        except (ValueError, TypeError):
            print("Error: Index must be a valid integer.")
            return False

    def add_subject(self, subject):
        if subject not in self.grades:
            self.grades[subject] = []
        else:
            print(f"Error: Subject '{subject}' already exists.")

    def remove_subject(self, subject):
        if subject not in self.grades:
            print(f"Error: Subject '{subject}' does not exist.")
        else:
            del self.grades[subject]

    def get_student_id(self):
        return self.student_id

    def get_name(self):
        return self.name

    def get_average_grade(self, subject):
        if subject not in self.grades:
            print(f"Error: Subject '{subject}' does not exist.")
            return 0.0

        if len(self.grades[subject]) == 0:
            return 0.0
        else:
            return sum(self.grades[subject]) / len(self.grades[subject])

    def show_grades(self):
        # Constructs a readable multi-line summary string with visible list index IDs [0, 1, 2...]
        lines = [f"Grades for {self.name} (ID: {self.student_id}):"]
        for subject, scores in self.grades.items():
            avg = self.get_average_grade(subject)
            # Formats individual scores to clearly display their internal list positions
            score_strings = [f"[{i}]: {score}" for i, score in enumerate(scores)]
            scores_display = ", ".join(score_strings) if score_strings else "[]"
            lines.append(f"  {subject.capitalize()}: {scores_display} (Avg: {avg:.2f})")
        return "\n".join(lines)

    def to_dict(self):
        return {
            "name": self.name,
            "student_id": self.student_id,
            "grades": self.grades
        }

    # 5. UI/UX Addition: Print a readable profile string instead of a hex memory address
    def __str__(self):
        return f"Student Profile -> Name: {self.name} | ID: {self.student_id} | Tracked Courses: {len(self.grades)}"

    def __repr__(self):
        return "Creates student objects to be stored in GradeDatabase"

'''
=========================================
          DATABASE MANAGEMENT
=========================================
'''
class GradeDatabase:
    def __init__(self, filename=json_path):
        self.filename = filename
        self._student_cache = []  # Holds active Student objects in memory

        if not os.path.exists(self.filename):
            self._save_raw_data([])

        self._load_all_data_into_cache()

    def _load_all_data_into_cache(self):
        '''Loads raw data from file once and converts everything to Student objects'''
        try:
            with open(self.filename, 'r') as f:
                raw_data = json.load(f)
        except json.JSONDecodeError as e:
            raise IOError(f"Database file '{self.filename}' is corrupted: {e}")
        except FileNotFoundError:
            raw_data = []

        self._student_cache = []
        for index, data in enumerate(raw_data):
            try:
                student = Student(
                    name=data["name"],
                    student_id=data["student_id"],
                    grades=data.get("grades", {})
                )
                self._student_cache.append(student)
            except KeyError as e:
                print(f"[DATABASE WARNING] Skipping corrupt record at row {index}: Missing field {e}")

    def _save_cache_to_file(self):
        raw_list = [student.to_dict() for student in self._student_cache]
        self._save_raw_data(raw_list)

    def _save_raw_data(self, data):
        try:
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"[CRITICAL ERROR] Failed to write database file to storage disk: {e}")

    def add_new_student(self, name, student_id):
        if any(s.get_student_id() == student_id for s in self._student_cache):
            print(f"Database Error: ID {student_id} is already taken.")
            return False

        new_student = Student(name, student_id)
        self._student_cache.append(new_student)
        self._save_cache_to_file()
        return True

    def get_student_object(self, student_id):
        for student in self._student_cache:
            if student.get_student_id() == student_id:
                return student
        return None

    def save_student_object(self, student_obj):
        if any(s.get_student_id() == student_obj.get_student_id() for s in self._student_cache):
            self._save_cache_to_file()
            return True
        print(f"Database Error: Student ID {student_obj.get_student_id()} not found to update.")
        return False

    def delete_student(self, student_id):
        initial_count = len(self._student_cache)
        self._student_cache = [s for s in self._student_cache if s.get_student_id() != student_id]

        if len(self._student_cache) < initial_count:
            self._save_cache_to_file()
            return True
        print(f"Database Error: Delete failed. ID {student_id} does not exist.")
        return False

    def get_all_students(self):
        return self._student_cache

    def search_students_by_name(self, search_term):
        if not search_term:
            return []
        search_lower = search_term.lower()
        matches = []
        for student in self._student_cache:
            if search_lower in student.name.lower():
                matches.append(student)
        return matches


'''
=========================================
      MODERN UI FRAMEWORK (PART 1)
=========================================
'''


class GradeAppLayout:
    def __init__(self, root):
        self.root = root
        self.root.title("Grade Manager")
        self.root.geometry("850x550")
        self.root.minsize(700, 450)

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.db = GradeDatabase()

        self.selected_student_id = None
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_student_list())

        self._build_ui()
        self.refresh_student_list()

    def _build_ui(self):
        '''Creates a modern responsive layout using ttk grid panels'''
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=2)
        self.root.grid_rowconfigure(0, weight=1)

        # --- LEFT PANEL: Student Records Navigation ---
        left_frame = ttk.LabelFrame(self.root, text=" Student Profiles ", padding=12)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(15, 7), pady=15)
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=1)

        # Search Control Layout
        search_frame = ttk.Frame(left_frame)
        search_frame.grid(row=0, column=0, pady=(0, 12), sticky="ew")
        search_frame.grid_columnconfigure(1, weight=1)
        ttk.Label(search_frame, text="Filter Name:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        ttk.Entry(search_frame, textvariable=self.search_var).grid(row=0, column=1, sticky="ew")

        # Core Selector Listbox Container
        list_container = ttk.Frame(left_frame)
        list_container.grid(row=1, column=0, sticky="nsew")
        list_container.grid_columnconfigure(0, weight=1)
        list_container.grid_rowconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL)
        self.student_listbox = tk.Listbox(
            list_container,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 10),
            bd=1,
            highlightthickness=0,
            selectbackground="#007fff",
            selectforeground="white"
        )
        scrollbar.config(command=self.student_listbox.yview)
        self.student_listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.student_listbox.bind('<<ListboxSelect>>', self.on_student_select)

        # Record Actions Grid
        btn_frame = ttk.Frame(left_frame)
        btn_frame.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        ttk.Button(btn_frame, text="➕ Add Student", command=self.ui_add_student).grid(row=0, column=0, padx=(0, 4),
                                                                                      sticky="ew")
        ttk.Button(btn_frame, text="❌ Delete Profile", command=self.ui_delete_student).grid(row=0, column=1,
                                                                                            padx=(4, 0), sticky="ew")

        # --- RIGHT PANEL: Academic Dashboard Viewer ---
        right_frame = ttk.LabelFrame(self.root, text=" Performance Metrics Dashboard ", padding=12)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(7, 15), pady=15)
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(0, weight=1)

        # Dynamic Record Ledger Box
        self.display_text = tk.Text(
            right_frame, wrap=tk.WORD, font=("Consolas", 10), state=tk.DISABLED,
            bg="#fdfdfd", fg="#212529", bd=1, relief="solid", padx=8, pady=8
        )
        self.display_text.grid(row=0, column=0, sticky="nsew", pady=(0, 12))

        # Grade Management Actions Frame (3-Button Layout Design)
        grade_btn_frame = ttk.Frame(right_frame)
        grade_btn_frame.grid(row=1, column=0, sticky="ew")
        grade_btn_frame.grid_columnconfigure(0, weight=1)
        grade_btn_frame.grid_columnconfigure(1, weight=1)
        grade_btn_frame.grid_columnconfigure(2, weight=1)

        self.btn_add_grade = ttk.Button(grade_btn_frame, text="📝 Record Grade", command=self.ui_add_grade,
                                        state=tk.DISABLED)
        self.btn_add_grade.grid(row=0, column=0, padx=(0, 2), sticky="ew")

        self.btn_delete_grade = ttk.Button(grade_btn_frame, text="🗑️ Delete Grade", command=self.ui_delete_grade,
                                           state=tk.DISABLED)
        self.btn_delete_grade.grid(row=0, column=1, padx=2, sticky="ew")

        self.btn_manage_subs = ttk.Button(grade_btn_frame, text="⚙️ Manage Subjects", command=self.ui_manage_subjects,
                                          state=tk.DISABLED)
        self.btn_manage_subs.grid(row=0, column=2, padx=(2, 0), sticky="ew")


'''
=========================================
      MODERN UI FRAMEWORK (PART 2)
=========================================
'''

'''
=========================================
      MODERN UI FRAMEWORK (PART 2)
=========================================
'''


class GradeApp(GradeAppLayout):
    def refresh_student_list(self):
        '''Updates view elements safely while preserving current state anchors'''
        self.student_listbox.delete(0, tk.END)
        search_query = self.search_var.get().strip()

        if search_query:
            students = self.db.search_students_by_name(search_query)
        else:
            students = self.db.get_all_students()

        for student in students:
            display_string = f"{student.get_student_id():<12} | {student.get_name()}"
            self.student_listbox.insert(tk.END, display_string)

    def on_student_select(self, event):
        '''Extracts item identifiers safely to step application states forward'''
        selection = self.student_listbox.curselection()
        if not selection:
            return

        selected_text = self.student_listbox.get(selection)

        if "|" in selected_text:
            self.selected_student_id = selected_text.split('|')[0].strip()

            # Contextually toggle all dashboard management components
            self.btn_add_grade.config(state=tk.NORMAL)
            self.btn_delete_grade.config(state=tk.NORMAL)
            self.btn_manage_subs.config(state=tk.NORMAL)

            self.update_report_viewer()

    def update_report_viewer(self):
        '''Updates report metrics while fully insulating UI frameworks against errors'''
        self.display_text.config(state=tk.NORMAL)
        self.display_text.delete('1.0', tk.END)

        if self.selected_student_id:
            student = self.db.get_student_object(self.selected_student_id)
            if student:
                report_content = student.show_grades()
                self.display_text.insert(tk.END, str(report_content) if report_content else "Profile has no data logs.")
            else:
                self._clear_view_state()
        else:
            self.display_text.insert(tk.END, "Select an active student file from the registry panel.")

        self.display_text.config(state=tk.DISABLED)

    def _clear_view_state(self):
        '''Clears data variables and locks inputs when contexts drop out'''
        self.selected_student_id = None
        self.btn_add_grade.config(state=tk.DISABLED)
        self.btn_delete_grade.config(state=tk.DISABLED)
        self.btn_manage_subs.config(state=tk.DISABLED)
        self.update_report_viewer()

        # --- INPUT INTERFACES & SUB DIALOG POPUPS ---

    def ui_add_student(self):
        name = simpledialog.askstring("Profile Creation", "Enter Student Full Name:", parent=self.root)
        if not name or not name.strip(): return

        student_id = simpledialog.askstring("Profile Creation", "Assign Unique Identity Sequence / ID Key:",
                                            parent=self.root)
        if not student_id or not student_id.strip(): return

        if self.db.add_new_student(name.strip(), student_id.strip()):
            messagebox.showinfo("Success", f"Database entry initialized for '{name.strip()}'.")
            self.refresh_student_list()
        else:
            messagebox.showerror("Registry Conflict",
                                 f"The identity key '{student_id.strip()}' matches an existing system record.")

    def ui_delete_student(self):
        if not self.selected_student_id:
            messagebox.showwarning("Context Action Refused",
                                   "Highlight a profile node inside the registry listing first.")
            return

        confirm = messagebox.askyesno("Confirm Deletion",
                                      f"Permanently wipe student file tracking profile ID '{self.selected_student_id}'?")
        if confirm:
            self.db.delete_student(self.selected_student_id)
            self._clear_view_state()
            self.refresh_student_list()

    def ui_add_grade(self):
        student = self.db.get_student_object(self.selected_student_id)
        if not student: return

        subject = simpledialog.askstring("Grade Recording", "Target Subject / Assessment Course handle:",
                                         parent=self.root)
        if not subject: return
        subject = subject.strip().lower()

        score = simpledialog.askfloat("Grade Recording", f"Enter dynamic raw float score for '{subject}':",
                                      parent=self.root, minvalue=0.0, maxvalue=100.0)
        if score is None: return

        if student.update_existing_grade(subject, score):
            self.db.save_student_object(student)
            self.update_report_viewer()
        else:
            messagebox.showerror("Processing Halted",
                                 f"Subject '{subject}' does not exist on this tracking schema.\n\nInitialize subject using 'Manage Subjects' module configuration panel first.")

    def ui_delete_grade(self):
        student = self.db.get_student_object(self.selected_student_id)
        if not student: return

        subject = simpledialog.askstring("Delete Grade", "Target Subject / Assessment Course handle:",
                                         parent=self.root)
        if not subject: return
        subject = subject.strip().lower()

        if subject not in student.grades:
            messagebox.showerror("Error", f"Subject '{subject}' does not exist on this record profile.")
            return

        current_grades = student.grades[subject]
        if not current_grades:
            messagebox.showinfo("Empty Subject", f"There are no recorded grades under '{subject}' to remove.")
            return

        # Generates a clear view matching the dashboard index markers
        grade_list_string = "\n".join([f"[{i}]: Score -> {score}" for i, score in enumerate(current_grades)])
        prompt_message = f"Current grades for '{subject}':\n\n{grade_list_string}\n\nEnter the index number ([#]) to delete:"

        idx = simpledialog.askinteger("Select Grade Index", prompt_message, parent=self.root, minvalue=0,
                                      maxvalue=len(current_grades) - 1)
        if idx is None: return

        confirm = messagebox.askyesno("Confirm Deletion",
                                      f"Permanently wipe grade entry at index {idx} ({current_grades[idx]})?")
        if confirm:
            if student.remove_grade_by_index(subject, idx):
                self.db.save_student_object(student)
                self.update_report_viewer()
            else:
                messagebox.showerror("Error", "Failed to remove the requested grade entry.")

    def ui_manage_subjects(self):
        student = self.db.get_student_object(self.selected_student_id)
        if not student: return

        action = simpledialog.askstring("Course Setup Matrix",
                                        "Type 'add' to register new course tracking key\nType 'remove' to prune old courses:",
                                        parent=self.root)
        if not action: return
        action = action.strip().lower()

        if action == 'add':
            sub = simpledialog.askstring("Course Setup Matrix",
                                         "New unique alphabetical course catalog index name:", parent=self.root)
            if sub and sub.strip():
                student.add_subject(sub.strip().lower())
        elif action == 'remove':
            sub = simpledialog.askstring("Course Setup Matrix",
                                         "Enter target course tracking module name to delete:", parent=self.root)
            if sub and sub.strip():
                student.remove_subject(sub.strip().lower())
        else:
            messagebox.showwarning("Command Dropped", "Instruction payload string signature unrecognized.")
            return

        self.db.save_student_object(student)
        self.update_report_viewer()




if __name__ == "__main__":
    app_window = tk.Tk()
    app_engine = GradeApp(app_window)
    sv_ttk.use_dark_theme()
    app_window.mainloop()