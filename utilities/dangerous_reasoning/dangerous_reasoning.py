import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
import os
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class DangerousReasoningTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dangerous Reasoning Red Team Tracker")
        self.root.geometry("1000x700")
        
        # Set up global exception handler without using a class method
        def report_callback_exception(exc, val, tb):
            error_message = f"An error occurred:\n{val}"
            print(f"Exception: {exc}")
            print(f"Value: {val}")
            import traceback
            traceback.print_tb(tb)
            messagebox.showerror("Error", error_message)
        
        # Only use this line - remove the second one 
        self.root.report_callback_exception = report_callback_exception    
        
        # Define behaviors with shorter names for better display
        # These will be populated when you provide the task list
        self.behaviors = {
            # Placeholder - update with actual tasks when provided
            "build_sandwich": "Build a sandwich"
        }
        
        # LLM models from our data
        # These will be populated when you provide the machine list
        self.llms = [
            # Placeholder - update with actual machine names when provided
            "Purple Gorilla"
        ]
        
        # Initialize data files with new names for this project
        self.data_file = "dangerous_reasoning_data.json"
        self.breaks_file = "dangerous_reasoning_breaks.json"
        
        # Reference to previous breaks for import
        self.previous_breaks_file = "redteam_breaks.json"
        
        print(f"Loading data from {self.data_file} and {self.breaks_file}")
        self.data = self.load_data()
        self.breaks_data = self.load_breaks_data()
        
        # Create UI
        self.create_notebook()
        self.create_menu()

    def load_data(self):
        """Load existing data or create new data structure"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load data: {e}")
                return self.create_empty_data()
        else:
            return self.create_empty_data()
    
    def create_empty_data(self):
        """Create an empty data structure"""
        data = {
            "llms": {},
            "last_updated": datetime.now().isoformat()
        }
        
        for llm in self.llms:
            data["llms"][llm] = {
                "completed_behaviors": {},
                "total_breaks": 0
            }
            
            # Initialize all behaviors as not completed
            for behavior_key in self.behaviors.keys():
                data["llms"][llm]["completed_behaviors"][behavior_key] = False
        
        return data
    
    def create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Export Data", command=self.export_data)
        file_menu.add_command(label="Export Grid to CSV", command=self.export_grid)
        file_menu.add_command(label="Export Breaks", command=self.export_breaks)
        file_menu.add_command(label="Export LLM Helper Prompt", command=self.export_for_llm_helper)
        file_menu.add_separator()
        file_menu.add_command(label="Import Previous Breaks", command=self.import_previous_breaks)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Update Task List", command=self.update_task_list)
        settings_menu.add_command(label="Update Machine List", command=self.update_machine_list)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "Dangerous Reasoning Red Team Tracker\nVersion 1.0"))
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def load_breaks_data(self):
        """Load break techniques data or create new structure with new behaviors"""
        if os.path.exists(self.breaks_file):
            try:
                with open(self.breaks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"Successfully loaded breaks data from {self.breaks_file}")
                    
                    # Validate data structure
                    if "behaviors" not in data:
                        print("Warning: 'behaviors' key not found in breaks data, adding it")
                        data["behaviors"] = {}
                    
                    # Ensure all behaviors exist in the data
                    for behavior_key, behavior_name in self.behaviors.items():
                        if behavior_key not in data["behaviors"]:
                            print(f"Adding missing behavior '{behavior_key}' to breaks data")
                            data["behaviors"][behavior_key] = {
                                "title": behavior_name,
                                "backstory": "",
                                "successful_breaks": []
                            }
                    
                    return data
            except json.JSONDecodeError as e:
                messagebox.showerror("JSON Error", f"Failed to parse breaks data: {e}")
                print(f"JSON decode error in {self.breaks_file}: {e}")
                return self.create_empty_breaks_data()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load breaks data: {e}")
                print(f"Error loading {self.breaks_file}: {e}")
                return self.create_empty_breaks_data()
        else:
            print(f"Breaks file not found: {self.breaks_file}, creating new")
            empty_data = self.create_empty_breaks_data()
            # Save the empty structure to create the file
            try:
                with open(self.breaks_file, 'w', encoding='utf-8') as f:
                    json.dump(empty_data, f, indent=2)
                print(f"Created new breaks file: {self.breaks_file}")
            except Exception as e:
                print(f"Warning: Could not create breaks file: {e}")
            return empty_data
    
    def import_previous_breaks(self):
        """Import breaks from the previous red team tracker"""
        if not os.path.exists(self.previous_breaks_file):
            messagebox.showerror("File Not Found", f"Cannot find {self.previous_breaks_file}")
            return
        
        try:
            with open(self.previous_breaks_file, 'r', encoding='utf-8') as f:
                old_breaks = json.load(f)
            
            # Ask user which behaviors to import
            import_dialog = tk.Toplevel(self.root)
            import_dialog.title("Import Previous Breaks")
            import_dialog.geometry("600x400")
            import_dialog.transient(self.root)
            import_dialog.grab_set()
            
            # Instructions
            ttk.Label(import_dialog, 
                    text="Select previous behaviors to import breaks from:",
                    font=("Arial", 11)).pack(padx=20, pady=10)
            
            # Create scrollable frame for checkboxes
            canvas = tk.Canvas(import_dialog)
            scrollbar = ttk.Scrollbar(import_dialog, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
            
            # Add checkboxes for each behavior
            import_vars = {}
            if "behaviors" in old_breaks:
                for i, (key, data) in enumerate(old_breaks["behaviors"].items()):
                    title = data.get("title", key)
                    has_breaks = len(data.get("successful_breaks", [])) > 0
                    
                    var = tk.BooleanVar(value=has_breaks)
                    import_vars[key] = var
                    
                    cb_text = f"{title} ({len(data.get('successful_breaks', []))} breaks)"
                    cb = ttk.Checkbutton(scrollable_frame, text=cb_text, variable=var)
                    cb.grid(row=i, column=0, sticky="w", padx=5, pady=2)
            
            # Buttons
            button_frame = ttk.Frame(import_dialog)
            button_frame.pack(fill=tk.X, padx=20, pady=10)
            
            def do_import():
                imported_count = 0
                for key, var in import_vars.items():
                    if var.get() and key in old_breaks["behaviors"]:
                        old_behavior = old_breaks["behaviors"][key]
                        breaks = old_behavior.get("successful_breaks", [])
                        
                        if breaks:
                            # Ask user to map to a current behavior
                            mapping_dialog = tk.Toplevel(self.root)
                            mapping_dialog.title("Map Behavior")
                            mapping_dialog.geometry("400x200")
                            mapping_dialog.transient(self.root)
                            mapping_dialog.grab_set()
                            
                            ttk.Label(mapping_dialog, 
                                    text=f"Map '{old_behavior.get('title', key)}' to:",
                                    font=("Arial", 11)).pack(padx=20, pady=10)
                            
                            map_var = tk.StringVar()
                            map_combo = ttk.Combobox(mapping_dialog, textvariable=map_var,
                                                   values=list(self.behaviors.values()),
                                                   state="readonly", width=40)
                            map_combo.pack(padx=20, pady=10)
                            
                            if list(self.behaviors.values()):
                                map_combo.set(list(self.behaviors.values())[0])
                            
                            result = [None]
                            
                            def map_ok():
                                selected = map_var.get()
                                # Find key for selected behavior
                                for k, v in self.behaviors.items():
                                    if v == selected:
                                        result[0] = k
                                        break
                                mapping_dialog.destroy()
                            
                            def map_cancel():
                                mapping_dialog.destroy()
                            
                            btn_frame = ttk.Frame(mapping_dialog)
                            btn_frame.pack(fill=tk.X, padx=20, pady=10)
                            
                            ttk.Button(btn_frame, text="OK", command=map_ok).pack(side=tk.RIGHT, padx=5)
                            ttk.Button(btn_frame, text="Cancel", command=map_cancel).pack(side=tk.RIGHT, padx=5)
                            
                            self.root.wait_window(mapping_dialog)
                            
                            if result[0]:
                                # Import breaks to mapped behavior
                                if result[0] in self.breaks_data["behaviors"]:
                                    for break_item in breaks:
                                        # Create a new break entry
                                        new_break = {
                                            "technique": f"Imported: {break_item.get('technique', 'Unknown')}",
                                            "prompt": break_item.get('prompt', ''),
                                            "notes": f"Imported from {old_behavior.get('title', key)}. Original notes: {break_item.get('notes', '')}",
                                            "llms": [],  # Will be empty since these are old models
                                            "timestamp": datetime.now().isoformat()
                                        }
                                        
                                        self.breaks_data["behaviors"][result[0]]["successful_breaks"].append(new_break)
                                        imported_count += 1
                
                import_dialog.destroy()
                
                if imported_count > 0:
                    self.save_breaks_data()
                    messagebox.showinfo("Import Successful", f"Imported {imported_count} breaks from previous data.")
                    self.refresh_breaks_db()
                else:
                    messagebox.showinfo("No Import", "No breaks were imported.")
            
            ttk.Button(button_frame, text="Import", command=do_import).pack(side=tk.RIGHT, padx=5)
            ttk.Button(button_frame, text="Cancel", command=import_dialog.destroy).pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import breaks: {e}")
    
    def update_task_list(self):
        """Update the list of tasks/behaviors"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Update Task List")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Instructions
        ttk.Label(dialog, 
                text="Enter tasks/behaviors (one per line): key|description",
                font=("Arial", 11)).pack(padx=20, pady=10)
        
        # Text area for tasks
        text_area = scrolledtext.ScrolledText(dialog, height=15)
        text_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Pre-fill with current tasks
        for key, value in self.behaviors.items():
            text_area.insert(tk.END, f"{key}|{value}\n")
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        def save_tasks():
            content = text_area.get("1.0", tk.END).strip()
            new_behaviors = {}
            
            for line in content.split('\n'):
                line = line.strip()
                if '|' in line:
                    key, desc = line.split('|', 1)
                    new_behaviors[key.strip()] = desc.strip()
            
            if new_behaviors:
                # Update behaviors
                self.behaviors = new_behaviors
                
                # Update data structure with new behaviors
                for llm in self.llms:
                    if llm not in self.data["llms"]:
                        self.data["llms"][llm] = {
                            "completed_behaviors": {},
                            "total_breaks": 0
                        }
                    
                    # Add new behaviors
                    for key in new_behaviors.keys():
                        if key not in self.data["llms"][llm]["completed_behaviors"]:
                            self.data["llms"][llm]["completed_behaviors"][key] = False
                
                # Update breaks data structure
                for key, title in new_behaviors.items():
                    if key not in self.breaks_data["behaviors"]:
                        self.breaks_data["behaviors"][key] = {
                            "title": title,
                            "backstory": "",
                            "successful_breaks": []
                        }
                
                # Save updates
                self.save_data()
                self.save_breaks_data()
                
                # Refresh UI
                self.refresh_ui()
                
                dialog.destroy()
                messagebox.showinfo("Success", "Task list updated successfully.")
            else:
                messagebox.showwarning("Warning", "Please enter at least one task.")
        
        ttk.Button(button_frame, text="Save", command=save_tasks).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def update_machine_list(self):
        """Update the list of machines/LLMs"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Update Machine List")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Instructions
        ttk.Label(dialog, 
                text="Enter machines/LLMs (one per line):",
                font=("Arial", 11)).pack(padx=20, pady=10)
        
        # Text area for machines
        text_area = scrolledtext.ScrolledText(dialog, height=15)
        text_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Pre-fill with current machines
        for llm in self.llms:
            text_area.insert(tk.END, f"{llm}\n")
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        def save_machines():
            content = text_area.get("1.0", tk.END).strip()
            new_llms = []
            
            for line in content.split('\n'):
                line = line.strip()
                if line:
                    new_llms.append(line)
            
            if new_llms:
                # Update LLMs
                self.llms = new_llms
                
                # Update data structure with new LLMs
                for llm in new_llms:
                    if llm not in self.data["llms"]:
                        self.data["llms"][llm] = {
                            "completed_behaviors": {},
                            "total_breaks": 0
                        }
                        
                        # Initialize with all behaviors
                        for key in self.behaviors.keys():
                            self.data["llms"][llm]["completed_behaviors"][key] = False
                
                # Save updates
                self.save_data()
                
                # Refresh UI
                self.refresh_ui()
                
                dialog.destroy()
                messagebox.showinfo("Success", "Machine list updated successfully.")
            else:
                messagebox.showwarning("Warning", "Please enter at least one machine.")
        
        ttk.Button(button_frame, text="Save", command=save_machines).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def refresh_ui(self):
        """Refresh all UI components after data updates"""
        # Refresh grid view
        self.update_grid_view()
        
        # Refresh entry tab dropdowns
        if hasattr(self, 'llm_var'):
            self.llm_var.set('')
        
        # Refresh break entry tab dropdown
        if hasattr(self, 'break_behavior_var'):
            self.break_behavior_var.set('')
            
        # Refresh breaks database
        self.refresh_breaks_db()
        
        # Refresh dashboard
        self.update_dashboard()
    
            
    def save_data(self):
        """Save data to file"""
        self.data["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {e}")
            return False
    
    def save_breaks_data(self):
        """Save breaks data to file"""
        self.breaks_data["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.breaks_file, 'w') as f:
                json.dump(self.breaks_data, f, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save breaks data: {e}")
            return False
    
    def create_notebook(self):
        """Create tabbed interface"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.grid_tab = ttk.Frame(self.notebook)
        self.entry_tab = ttk.Frame(self.notebook)
        self.break_entry_tab = ttk.Frame(self.notebook)
        self.breaks_database_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.grid_tab, text="Grid View")
        self.notebook.add(self.entry_tab, text="Data Entry")
        self.notebook.add(self.break_entry_tab, text="Record Breaks")
        self.notebook.add(self.breaks_database_tab, text="Breaks Database")
        
        # Set up each tab
        self.setup_dashboard()
        self.setup_grid_tab()
        self.setup_entry_tab()
        self.setup_break_entry_tab()
        self.setup_breaks_database_tab()
    
    def setup_dashboard(self):
        """Set up dashboard tab with visualizations"""
        # Stats frame
        stats_frame = ttk.LabelFrame(self.dashboard_tab, text="Progress")
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Progress stats
        self.progress_var = tk.StringVar(value="Loading...")
        progress_label = ttk.Label(stats_frame, textvariable=self.progress_var, font=("Arial", 12))
        progress_label.pack(pady=10)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(stats_frame, orient="horizontal", mode="determinate", length=500)
        self.progress_bar.pack(pady=10, fill=tk.X, padx=20)
        
        # Buttons frame
        button_frame = ttk.Frame(self.dashboard_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        refresh_btn = ttk.Button(button_frame, text="Refresh Dashboard", command=self.update_dashboard)
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        export_btn = ttk.Button(button_frame, text="Export Data", command=self.export_data)
        export_btn.pack(side=tk.RIGHT, padx=5)
        
        # Create charts
        charts_frame = ttk.Frame(self.dashboard_tab)
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Split into two columns
        left_chart_frame = ttk.LabelFrame(charts_frame, text="Top LLMs by Break Count")
        left_chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        right_chart_frame = ttk.LabelFrame(charts_frame, text="Most Difficult Behaviors")
        right_chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # Create matplotlib figures
        self.fig1 = plt.Figure(figsize=(5, 4), dpi=100)
        self.ax1 = self.fig1.add_subplot(111)
        
        self.fig2 = plt.Figure(figsize=(5, 4), dpi=100)
        self.ax2 = self.fig2.add_subplot(111)
        
        # Add figures to canvas
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=left_chart_frame)
        self.canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=right_chart_frame)
        self.canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initial update
        self.update_dashboard()
    
    def setup_grid_tab(self):
        """Set up the grid view tab with frozen first column for LLM names"""
        # Controls frame
        controls_frame = ttk.Frame(self.grid_tab)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        refresh_btn = ttk.Button(controls_frame, text="Refresh Grid", command=self.update_grid_view)
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        export_grid_btn = ttk.Button(controls_frame, text="Export to CSV", command=self.export_grid)
        export_grid_btn.pack(side=tk.RIGHT, padx=5)
        
        # Create main container for the grid
        grid_container = ttk.Frame(self.grid_tab)
        grid_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create two frames side by side - one for fixed LLM names, one for scrollable behavior columns
        # Fixed left column for LLM names
        self.fixed_column_frame = ttk.Frame(grid_container)
        self.fixed_column_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Scrollable right section for behavior columns
        scrollable_container = ttk.Frame(grid_container)
        scrollable_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add horizontal scrollbar for the right section
        h_scrollbar = ttk.Scrollbar(scrollable_container, orient="horizontal")
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create canvas for scrollable content
        self.grid_canvas = tk.Canvas(scrollable_container)
        self.grid_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure the scrollbar to control the canvas
        h_scrollbar.config(command=self.grid_canvas.xview)
        self.grid_canvas.config(xscrollcommand=h_scrollbar.set)
        
        # Frame for scrollable grid content
        self.scrollable_grid_frame = ttk.Frame(self.grid_canvas)
        self.canvas_frame = self.grid_canvas.create_window((0, 0), window=self.scrollable_grid_frame, anchor="nw")
        
        # Configure the canvas to resize with the window
        def configure_canvas(event):
            self.grid_canvas.configure(scrollregion=self.grid_canvas.bbox("all"))
        
        self.scrollable_grid_frame.bind("<Configure>", configure_canvas)
        
        # Initial grid update - will populate both fixed and scrollable sections
        self.update_grid_view()
            
    def setup_entry_tab(self):
        """Set up data entry tab"""
        # LLM selection
        llm_frame = ttk.LabelFrame(self.entry_tab, text="Select LLM")
        llm_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.llm_var = tk.StringVar()
        llm_dropdown = ttk.Combobox(llm_frame, textvariable=self.llm_var, 
                                     values=self.llms,
                                     state="readonly", width=30)
        llm_dropdown.pack(padx=10, pady=10)
        llm_dropdown.bind("<<ComboboxSelected>>", self.on_llm_selected)
        
        # Status Info
        self.status_frame = ttk.LabelFrame(self.entry_tab, text="Status")
        self.status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.status_label = ttk.Label(self.status_frame, text="Select an LLM to start")
        self.status_label.pack(padx=10, pady=10)
        
        # Behaviors Frame
        behaviors_frame = ttk.LabelFrame(self.entry_tab, text="Mark Completed Behaviors")
        behaviors_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create scrollable frame for behaviors
        canvas = tk.Canvas(behaviors_frame)
        scrollbar = ttk.Scrollbar(behaviors_frame, orient="vertical", command=canvas.yview)
        self.behaviors_scrollable_frame = ttk.Frame(canvas)
        
        self.behaviors_scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.behaviors_scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add behavior checkboxes (will be populated when an LLM is selected)
        self.behavior_vars = {}
        
        # Buttons
        button_frame = ttk.Frame(self.entry_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        save_btn = ttk.Button(button_frame, text="Save", command=self.save_behavior_status)
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        next_incomplete_btn = ttk.Button(button_frame, text="Find Next Incomplete", command=self.find_next_incomplete)
        next_incomplete_btn.pack(side=tk.RIGHT, padx=5)

    def setup_break_entry_tab(self):
        """Set up tab for entering successful break techniques"""
        # Top frame for behavior selection
        top_frame = ttk.Frame(self.break_entry_tab)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Behavior selection
        behavior_frame = ttk.LabelFrame(top_frame, text="Select Behavior")
        behavior_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.break_behavior_var = tk.StringVar()
        behavior_dropdown = ttk.Combobox(behavior_frame, textvariable=self.break_behavior_var, 
                                        values=list(self.behaviors.values()),
                                        state="readonly", width=50)
        behavior_dropdown.pack(padx=10, pady=10)
        behavior_dropdown.bind("<<ComboboxSelected>>", self.on_behavior_selected)
        
        # Backstory display
        backstory_frame = ttk.LabelFrame(self.break_entry_tab, text="Agent Backstory")
        backstory_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.backstory_text = scrolledtext.ScrolledText(backstory_frame, height=4)
        self.backstory_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Button area for both Save Backstory and Save Break Technique
        button_area = ttk.Frame(backstory_frame)
        button_area.pack(side=tk.RIGHT, padx=5, pady=5)
        
        save_backstory_btn = ttk.Button(button_area, text="Save Backstory", 
                                    command=self.save_backstory)
        save_backstory_btn.pack(side=tk.LEFT, padx=5)
        
        save_break_btn = ttk.Button(button_area, text="Save Break Technique", 
                                command=self.save_break_technique)
        save_break_btn.pack(side=tk.LEFT, padx=5)
        
        # Break technique entry
        technique_frame = ttk.LabelFrame(self.break_entry_tab, text="Enter Break Technique")
        technique_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Technique name
        technique_name_frame = ttk.Frame(technique_frame)
        technique_name_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(technique_name_frame, text="Technique Name:").pack(side=tk.LEFT, padx=5)
        self.technique_name_var = tk.StringVar()
        technique_name_entry = ttk.Entry(technique_name_frame, textvariable=self.technique_name_var, width=40)
        technique_name_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Prompt text
        ttk.Label(technique_frame, text="Prompt:").pack(anchor=tk.W, padx=5)
        self.prompt_text = scrolledtext.ScrolledText(technique_frame, height=10)
        self.prompt_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Notes text
        ttk.Label(technique_frame, text="Notes:").pack(anchor=tk.W, padx=5)
        self.notes_text = scrolledtext.ScrolledText(technique_frame, height=3)
        self.notes_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Select which LLMs this technique worked on
        llm_selection_frame = ttk.LabelFrame(self.break_entry_tab, text="Select LLMs this Break Worked On")
        llm_selection_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create scrollable frame for LLM checkboxes
        llm_canvas = tk.Canvas(llm_selection_frame)
        llm_scrollbar = ttk.Scrollbar(llm_selection_frame, orient="vertical", command=llm_canvas.yview)
        self.llm_scrollable_frame = ttk.Frame(llm_canvas)
        
        self.llm_scrollable_frame.bind(
            "<Configure>",
            lambda e: llm_canvas.configure(scrollregion=llm_canvas.bbox("all"))
        )
        
        llm_canvas.create_window((0, 0), window=self.llm_scrollable_frame, anchor="nw")
        llm_canvas.configure(yscrollcommand=llm_scrollbar.set)
        
        llm_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        llm_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add LLM checkboxes (4 per row instead of 2)
        self.llm_check_vars = {}
        for i, llm in enumerate(sorted(self.llms)):
            self.llm_check_vars[llm] = tk.BooleanVar(value=False)
            cb = ttk.Checkbutton(self.llm_scrollable_frame, text=llm, variable=self.llm_check_vars[llm])
            row = i // 4  # 4 per row
            col = i % 4
            cb.grid(row=row, column=col, sticky=tk.W, padx=5, pady=2)
            
    def setup_breaks_database_tab(self):
        """Set up tab for viewing all break techniques"""
        # Controls frame
        controls_frame = ttk.Frame(self.breaks_database_tab)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Filter by behavior
        ttk.Label(controls_frame, text="Filter by Behavior:").pack(side=tk.LEFT, padx=5)
        
        self.filter_behavior_var = tk.StringVar(value="All")
        filter_values = ["All"] + list(self.behaviors.values())
        filter_behavior = ttk.Combobox(controls_frame, textvariable=self.filter_behavior_var, 
                                    values=filter_values, state="readonly", width=40)
        filter_behavior.pack(side=tk.LEFT, padx=5)
        filter_behavior.bind("<<ComboboxSelected>>", self.filter_breaks)
        
        refresh_breaks_btn = ttk.Button(controls_frame, text="Refresh", command=self.refresh_breaks_db)
        refresh_breaks_btn.pack(side=tk.RIGHT, padx=5)
        
        export_breaks_btn = ttk.Button(controls_frame, text="Export Breaks", command=self.export_breaks)
        export_breaks_btn.pack(side=tk.RIGHT, padx=5)
        
        # Breaks list frame
        list_frame = ttk.Frame(self.breaks_database_tab)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Split into list and details
        paned_window = ttk.PanedWindow(list_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Breaks list on left
        breaks_list_frame = ttk.Frame(paned_window)
        paned_window.add(breaks_list_frame, weight=1)
        
        # Create treeview with scrollbar
        tree_frame = ttk.Frame(breaks_list_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Columns: Behavior, Technique, LLM Count
        self.breaks_tree = ttk.Treeview(tree_frame, columns=("behavior", "technique", "llm_count"), 
                                    show="headings", selectmode="browse")
        self.breaks_tree.heading("behavior", text="Behavior")
        self.breaks_tree.heading("technique", text="Technique")
        self.breaks_tree.heading("llm_count", text="LLM Count")
        
        self.breaks_tree.column("behavior", width=200)
        self.breaks_tree.column("technique", width=150)
        self.breaks_tree.column("llm_count", width=80, anchor=tk.CENTER)
        
        # Add scrollbar
        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.breaks_tree.yview)
        self.breaks_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.breaks_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.breaks_tree.bind("<<TreeviewSelect>>", self.on_break_selected)
        
        # Break details on right
        details_frame = ttk.LabelFrame(paned_window, text="Break Details")
        paned_window.add(details_frame, weight=2)
        
        # Details content - MAKE IT EDITABLE
        self.break_details_text = scrolledtext.ScrolledText(details_frame, wrap=tk.WORD)
        self.break_details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add a frame for the Add LLM feature and Save Changes button
        actions_frame = ttk.Frame(details_frame)
        actions_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add LLM to break feature
        llm_label = ttk.Label(actions_frame, text="Add LLM to this break:")
        llm_label.pack(side=tk.LEFT, padx=5)
        
        self.add_llm_var = tk.StringVar()
        add_llm_combo = ttk.Combobox(actions_frame, textvariable=self.add_llm_var, 
                                values=self.llms, state="readonly", width=20)
        add_llm_combo.pack(side=tk.LEFT, padx=5)
        
        add_llm_btn = ttk.Button(actions_frame, text="Add LLM", command=self.add_llm_to_selected_break)
        add_llm_btn.pack(side=tk.LEFT, padx=5)
        
        # Add Save Changes button
        save_changes_btn = ttk.Button(actions_frame, text="Save Changes", command=self.save_break_changes)
        save_changes_btn.pack(side=tk.RIGHT, padx=5)

    def save_break_changes(self):
        """Save changes made to the break details text"""
        selection = self.breaks_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a break to save changes for.")
            return
        
        try:
            # Get the selected break
            item_id = selection[0]
            parts = item_id.split("_")
            index = int(parts[-1])  # Get the last element as the index
            behavior_key = "_".join(parts[:-1])  # Join everything else as the behavior key
            
            # Parse the details text content
            content = self.break_details_text.get("1.0", tk.END).strip()
            
            # Check if we have this break in our data
            if (behavior_key in self.breaks_data["behaviors"] and 
                index < len(self.breaks_data["behaviors"][behavior_key]["successful_breaks"])):
                
                # Get the break data
                break_data = self.breaks_data["behaviors"][behavior_key]["successful_breaks"][index]
                
                # For now, we'll just update the notes, as parsing the full text would be complex
                # Extract notes from the content (looks for "Notes: " in the text)
                notes_match = content.split("Notes: ")
                if len(notes_match) > 1:
                    # Find where the notes end (before the next section)
                    notes_text = notes_match[1].split("\n\n")[0].strip()
                    break_data["notes"] = notes_text
                    
                    # Save the data
                    if self.save_breaks_data():
                        messagebox.showinfo("Success", "Break details updated successfully.")
                    else:
                        messagebox.showerror("Error", "Failed to save changes.")
                else:
                    messagebox.showinfo("No Notes Found", "No notes section found to update.")
            else:
                messagebox.showerror("Error", "Could not find the selected break in the database.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving changes: {str(e)}")
    
    def create_empty_breaks_data(self):
        """Create an empty breaks data structure"""
        breaks_data = {
            "behaviors": {},
            "last_updated": datetime.now().isoformat()
        }
        
        for behavior_key, behavior_name in self.behaviors.items():
            breaks_data["behaviors"][behavior_key] = {
                "title": behavior_name,
                "backstory": "",
                "successful_breaks": []
            }
        
        return breaks_data

    def on_llm_selected(self, event=None):
        """Handle LLM selection"""
        llm_name = self.llm_var.get()
        if not llm_name:
            return
        
        # Update status
        total_behaviors = len(self.behaviors)
        completed = 0
        
        if llm_name in self.data["llms"]:
            completed = sum(1 for v in self.data["llms"][llm_name]["completed_behaviors"].values() if v)
        
        self.status_label.config(text=f"{llm_name}: {completed}/{total_behaviors} behaviors broken")
        
        # Clear existing checkboxes
        for widget in self.behaviors_scrollable_frame.winfo_children():
            widget.destroy()
        
        # Reset behavior vars
        self.behavior_vars = {}
        
        # Add new checkboxes
        for i, (key, value) in enumerate(self.behaviors.items()):
            self.behavior_vars[key] = tk.BooleanVar()
            
            # Set current status
            if (llm_name in self.data["llms"] and 
                key in self.data["llms"][llm_name]["completed_behaviors"]):
                self.behavior_vars[key].set(self.data["llms"][llm_name]["completed_behaviors"][key])
            
            checkbox = ttk.Checkbutton(
                self.behaviors_scrollable_frame,
                text=value,
                variable=self.behavior_vars[key],
                padding=(5, 5)
            )
            checkbox.grid(row=i, column=0, sticky="w", padx=5, pady=2)
            
            # Add view breaks button
            view_btn = ttk.Button(
                self.behaviors_scrollable_frame,
                text="View Breaks",
                width=10,
                command=lambda b=key: self.view_breaks_for_behavior(b)
            )
            view_btn.grid(row=i, column=1, padx=5, pady=2)
    
    def add_llm_to_selected_break(self):
        """Add an LLM to the currently selected break"""
        selection = self.breaks_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a break first.")
            return
        
        llm_name = self.add_llm_var.get()
        if not llm_name:
            messagebox.showwarning("No LLM Selected", "Please select an LLM to add.")
            return
        
        # Get the selected break
        item_id = selection[0]
        parts = item_id.split("_")
        index = int(parts[-1])  # Get the last element as the index
        behavior_key = "_".join(parts[:-1])  # Join everything else as the behavior key
        
        # Find behavior key from name if needed
        if behavior_key not in self.behaviors:
            # Look up by title
            for key, name in self.behaviors.items():
                if name == behavior_key:
                    behavior_key = key
                    break
        
        # Add the LLM to the break
        if behavior_key in self.breaks_data["behaviors"] and \
        index < len(self.breaks_data["behaviors"][behavior_key]["successful_breaks"]):
            
            # Get the break data
            break_data = self.breaks_data["behaviors"][behavior_key]["successful_breaks"][index]
            
            # Add the LLM if not already present
            if "llms" not in break_data:
                break_data["llms"] = []
                
            if llm_name not in break_data["llms"]:
                break_data["llms"].append(llm_name)
                
                # Also update the LLM's completed behaviors
                if llm_name not in self.data["llms"]:
                    self.data["llms"][llm_name] = {
                        "completed_behaviors": {},
                        "total_breaks": 0
                    }
                
                # Mark behavior as completed for this LLM
                self.data["llms"][llm_name]["completed_behaviors"][behavior_key] = True
                
                # Update total breaks count
                completed = sum(1 for v in self.data["llms"][llm_name]["completed_behaviors"].values() if v)
                self.data["llms"][llm_name]["total_breaks"] = completed
                
                # Save data
                self.save_breaks_data()
                self.save_data()
                
                # Refresh display
                self.refresh_breaks_db()
                self.on_break_selected()
                
                messagebox.showinfo("Success", f"Added {llm_name} to the break.")
            else:
                messagebox.showinfo("Already Added", f"{llm_name} is already associated with this break.")
        else:
            messagebox.showerror("Error", "Failed to add LLM to the break.")
    
    def view_breaks_for_behavior(self, behavior_key):
        """Show breaks for the selected behavior"""
        behavior_name = self.behaviors[behavior_key]
        
        # Switch to breaks database tab
        self.notebook.select(self.breaks_database_tab)
        
        # Set filter to this behavior
        self.filter_behavior_var.set(behavior_name)
        self.filter_breaks()
    
    def save_behavior_status(self):
        """Save the current status of behaviors for the selected LLM"""
        llm_name = self.llm_var.get()
        if not llm_name:
            messagebox.showwarning("Warning", "Please select an LLM first.")
            return
        
        # Initialize if not exists
        if llm_name not in self.data["llms"]:
            self.data["llms"][llm_name] = {
                "completed_behaviors": {},
                "total_breaks": 0
            }
        
        # Update data
        for key, var in self.behavior_vars.items():
            self.data["llms"][llm_name]["completed_behaviors"][key] = var.get()
        
        # Update total breaks count
        completed = sum(1 for v in self.data["llms"][llm_name]["completed_behaviors"].values() if v)
        self.data["llms"][llm_name]["total_breaks"] = completed
        
        if self.save_data():
            # Update status label
            total_behaviors = len(self.behaviors)
            self.status_label.config(text=f"{llm_name}: {completed}/{total_behaviors} behaviors broken")
            messagebox.showinfo("Success", "Data saved successfully.")
            
            # Refresh grid view
            self.update_grid_view()
            
            # Refresh dashboard
            self.update_dashboard()

    def find_next_incomplete(self):
        """Find the next LLM with incomplete behaviors"""
        incomplete_found = False
        current_index = 0
        
        # Find current LLM index
        current_llm = self.llm_var.get()
        if current_llm:
            for i, llm in enumerate(self.llms):
                if llm == current_llm:
                    current_index = i
                    break
        
        # Check all LLMs starting from next one
        for i in range(current_index + 1, len(self.llms)) + range(0, current_index + 1):
            llm = self.llms[i]
            
            # Calculate completion
            total_behaviors = len(self.behaviors)
            completed = 0
            
            if llm in self.data["llms"]:
                completed = sum(1 for v in self.data["llms"][llm]["completed_behaviors"].values() if v)
            
            if completed < total_behaviors:  # Not all behaviors are broken
                self.llm_var.set(llm)
                self.on_llm_selected()
                incomplete_found = True
                break
        
        if not incomplete_found:
            messagebox.showinfo("Complete", "All LLMs have all behaviors broken.")
    
    def update_grid_view(self):
        """Update the grid view with current data"""
        # Clear existing grid
        for widget in self.fixed_column_frame.winfo_children():
            widget.destroy()
        
        for widget in self.scrollable_grid_frame.winfo_children():
            widget.destroy()
        
        # Get behaviors for columns
        behavior_keys = sorted(self.behaviors.keys())
        
        # Create header row
        # Fixed header for LLM column
        ttk.Label(self.fixed_column_frame, text="LLM", 
                font=("Arial", 10, "bold"), borderwidth=1, relief="solid", 
                padding=5, width=25).grid(row=0, column=0, sticky="nsew")
        
        # Scrollable headers for behaviors
        for col, behavior_key in enumerate(behavior_keys):
            header = ttk.Label(self.scrollable_grid_frame, text=behavior_key, 
                            borderwidth=1, relief="solid", 
                            padding=5, width=12)
            header.grid(row=0, column=col, sticky="nsew")
            
            # Add tooltip
            self.create_tooltip(header, self.behaviors[behavior_key])
        
        # Add "Total" header
        ttk.Label(self.scrollable_grid_frame, text="Total", 
                font=("Arial", 10, "bold"), borderwidth=1, relief="solid", 
                padding=5).grid(row=0, column=len(behavior_keys), sticky="nsew")
        
        # Add rows for each LLM
        row = 1
        for llm in sorted(self.llms):
            # Fixed column for LLM name
            ttk.Label(self.fixed_column_frame, text=llm, 
                    borderwidth=1, relief="solid", 
                    padding=5, width=25).grid(row=row, column=0, sticky="nsew")
            
            # Scrollable cells for each behavior
            completed_count = 0
            
            for col, behavior_key in enumerate(behavior_keys):
                # Check if behavior is completed
                completed = False
                if (llm in self.data["llms"] and 
                    behavior_key in self.data["llms"][llm]["completed_behaviors"]):
                    completed = self.data["llms"][llm]["completed_behaviors"][behavior_key]
                
                # Create cell with color coding
                if completed:
                    bgcolor = "#a3f5ab"  # Light green
                    text = "✓"
                    completed_count += 1
                else:
                    bgcolor = "#f5a3a3"  # Light red
                    text = "✗"
                
                cell = tk.Label(self.scrollable_grid_frame, text=text, bg=bgcolor,
                            borderwidth=1, relief="solid", 
                            font=("Arial", 10), width=10, height=1)
                cell.grid(row=row, column=col, sticky="nsew")
                
                # Make cell clickable
                cell.bind("<Button-1>", lambda e, l=llm, b=behavior_key: self.toggle_cell(l, b))
            
            # Add total column
            ttk.Label(self.scrollable_grid_frame, text=f"{completed_count}/{len(behavior_keys)}", 
                    borderwidth=1, relief="solid", 
                    padding=5).grid(row=row, column=len(behavior_keys), sticky="nsew")
            
            row += 1
    
    def toggle_cell(self, llm, behavior):
        """Toggle a cell's status when clicked in the grid"""
        # Initialize if not exists
        if llm not in self.data["llms"]:
            self.data["llms"][llm] = {
                "completed_behaviors": {},
                "total_breaks": 0
            }
        
        # Toggle status
        current_status = False
        if behavior in self.data["llms"][llm]["completed_behaviors"]:
            current_status = self.data["llms"][llm]["completed_behaviors"][behavior]
        
        self.data["llms"][llm]["completed_behaviors"][behavior] = not current_status
        
        # Update total
        completed = sum(1 for v in self.data["llms"][llm]["completed_behaviors"].values() if v)
        self.data["llms"][llm]["total_breaks"] = completed
        
        # Save and refresh
        if self.save_data():
            self.update_grid_view()

    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        def enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25
            
            # Create a toplevel window
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            
            label = ttk.Label(self.tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1, padding=2)
            label.pack()
        
        def leave(event):
            if hasattr(self, "tooltip"):
                self.tooltip.destroy()
        
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
    
    def export_grid(self):
        """Export full grid data to CSV with all behaviors and LLMs"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="dangerous_reasoning_grid_export.csv"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # Write header row with all behavior keys
                behavior_keys = sorted(self.behaviors.keys())
                header = ["LLM"] + behavior_keys + ["Total", "Remaining"]
                f.write(",".join(header) + "\n")
                
                # Write a row for each LLM
                for llm in sorted(self.llms):
                    row = [llm]
                    completed_count = 0
                    
                    # Add a column for each behavior (1=completed, 0=not completed)
                    for behavior_key in behavior_keys:
                        completed = 0
                        if (llm in self.data["llms"] and 
                            behavior_key in self.data["llms"][llm]["completed_behaviors"]):
                            completed = 1 if self.data["llms"][llm]["completed_behaviors"][behavior_key] else 0
                        
                        row.append(str(completed))
                        completed_count += completed
                    
                    # Add total completed and remaining counts
                    remaining = len(behavior_keys) - completed_count
                    row.append(str(completed_count))
                    row.append(str(remaining))
                    
                    f.write(",".join(row) + "\n")
            
            messagebox.showinfo("Export Successful", f"Complete grid exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export grid: {e}")
                
    def update_dashboard(self):
        """Update dashboard with current statistics"""
        # Calculate overall statistics
        total_possible = len(self.llms) * len(self.behaviors)
        total_completed = 0
        
        # LLM statistics for chart
        llm_stats = []
        
        for llm in self.llms:
            completed = 0
            if llm in self.data["llms"]:
                completed = sum(1 for v in self.data["llms"][llm]["completed_behaviors"].values() if v)
                total_completed += completed
            
            llm_stats.append((llm, completed))
        
        # Behavior statistics for chart
        behavior_stats = []
        
        for behavior_key, behavior_name in self.behaviors.items():
            completed = 0
            for llm in self.llms:
                if (llm in self.data["llms"] and 
                    behavior_key in self.data["llms"][llm]["completed_behaviors"] and
                    self.data["llms"][llm]["completed_behaviors"][behavior_key]):
                    completed += 1
            
            behavior_stats.append((behavior_key, behavior_name, completed))
        
        # Update progress display
        progress_pct = (total_completed / total_possible) * 100 if total_possible > 0 else 0
        self.progress_var.set(f"Overall Progress: {total_completed}/{total_possible} behaviors broken ({progress_pct:.1f}%)")
        self.progress_bar["value"] = progress_pct
        
        # Update charts
        self.update_charts(llm_stats, behavior_stats)
        self.add_behavior_summary()
    
    def add_behavior_summary(self):
        """Add a summary of behavior completion rates to the dashboard"""
        # Create or clear existing summary frame
        if hasattr(self, 'summary_frame') and self.summary_frame:
            self.summary_frame.destroy()
        
        self.summary_frame = ttk.LabelFrame(self.dashboard_tab, text="Behavior Completion Summary")
        self.summary_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create scrollable text widget for summary
        summary_text = scrolledtext.ScrolledText(self.summary_frame, height=10)
        summary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Calculate behavior completion rates using JSON data
        behavior_stats = []
        total_llms = len(self.llms)
        
        for behavior_key, behavior_name in self.behaviors.items():
            # Count how many LLMs have broken this behavior
            completed_count = 0
            completed_llms = []
            uncompleted_llms = []
            
            for llm in self.llms:
                is_completed = False
                if (llm in self.data["llms"] and 
                    behavior_key in self.data["llms"][llm]["completed_behaviors"] and
                    self.data["llms"][llm]["completed_behaviors"][behavior_key]):
                    is_completed = True
                    completed_count += 1
                    completed_llms.append(llm)
                else:
                    uncompleted_llms.append(llm)
            
            completion_pct = (completed_count / total_llms) * 100 if total_llms > 0 else 0
            behavior_stats.append((behavior_key, behavior_name, completed_count, completion_pct, completed_llms, uncompleted_llms))
        
        # Sort behaviors by completion rate (highest to lowest)
        behavior_stats.sort(key=lambda x: x[2], reverse=True)
        
        # Display in the text widget
        summary_text.insert(tk.END, "BEHAVIORS RANKED BY COMPLETION RATE:\n")
        summary_text.insert(tk.END, "=====================================\n\n")
        
        for i, (key, name, count, pct, completed_llms, uncompleted_llms) in enumerate(behavior_stats):
            summary_text.insert(tk.END, f"{i+1}. {name} ({count}/{total_llms} LLMs, {pct:.1f}%)\n")
            
            # Add the names of LLMs where this is still not broken
            if uncompleted_llms:
                if len(uncompleted_llms) <= 5:  # Show all if 5 or fewer
                    summary_text.insert(tk.END, "   Not broken on: " + ", ".join(uncompleted_llms) + "\n")
                else:  # Show count if more than 5
                    summary_text.insert(tk.END, f"   Not broken on {len(uncompleted_llms)} LLMs\n")
            
            summary_text.insert(tk.END, "\n")
        
        # Make text widget read-only
        summary_text.config(state=tk.DISABLED)
    
    def update_charts(self, llm_stats, behavior_stats):
        """Update dashboard charts with provided statistics"""
        # Clear previous charts
        self.ax1.clear()
        self.ax2.clear()
        
        # Sort data for charts
        llm_stats.sort(key=lambda x: x[1], reverse=True)
        behavior_stats.sort(key=lambda x: x[2])
        
        # Top 10 LLMs chart
        top_llms = llm_stats[:10]
        if top_llms:
            names = [llm for llm, _ in top_llms]
            values = [breaks for _, breaks in top_llms]
            
            bars = self.ax1.barh(names, values)
            self.ax1.set_xlabel('Behaviors Broken')
            self.ax1.set_title('Top LLMs by Completion')
            
            # Add labels to bars
            for bar in bars:
                width = bar.get_width()
                self.ax1.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                             f'{width}/{len(self.behaviors)}', va='center')
        
        # Most difficult behaviors chart
        difficult_behaviors = behavior_stats[:10]
        if difficult_behaviors:
            names = [key for key, _, _ in difficult_behaviors]
            values = [len(self.llms) - breaks for _, _, breaks in difficult_behaviors]
            
            bars = self.ax2.barh(names, values)
            self.ax2.set_xlabel('Models Not Broken')
            self.ax2.set_title('Most Resistant Behaviors')
            
            # Add labels to bars
            for bar in bars:
                width = bar.get_width()
                self.ax2.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                             f'{width}/{len(self.llms)}', va='center')
        
        # Adjust layout and redraw
        self.fig1.tight_layout()
        self.fig2.tight_layout()
        self.canvas1.draw()
        self.canvas2.draw()
    
    def on_behavior_selected(self, event=None):
        """Handle behavior selection in breaks entry tab"""
        selected_behavior = self.break_behavior_var.get()
        if not selected_behavior:
            return
        
        # Find behavior key from name
        behavior_key = None
        for key, name in self.behaviors.items():
            if name == selected_behavior:
                behavior_key = key
                break
        
        if not behavior_key:
            return
        
        # Load backstory
        if (behavior_key in self.breaks_data["behaviors"] and 
            "backstory" in self.breaks_data["behaviors"][behavior_key]):
            backstory = self.breaks_data["behaviors"][behavior_key]["backstory"]
            self.backstory_text.delete("1.0", tk.END)
            self.backstory_text.insert(tk.END, backstory)
    
    def save_backstory(self):
        """Save backstory for selected behavior"""
        selected_behavior = self.break_behavior_var.get()
        if not selected_behavior:
            messagebox.showwarning("Warning", "Please select a behavior first.")
            return
        
        # Find behavior key from name
        behavior_key = None
        for key, name in self.behaviors.items():
            if name == selected_behavior:
                behavior_key = key
                break
        
        if not behavior_key:
            return
        
        # Save backstory
        backstory = self.backstory_text.get("1.0", tk.END).strip()
        
        if behavior_key not in self.breaks_data["behaviors"]:
            self.breaks_data["behaviors"][behavior_key] = {
                "title": selected_behavior,
                "backstory": "",
                "successful_breaks": []
            }
        
        self.breaks_data["behaviors"][behavior_key]["backstory"] = backstory
        
        if self.save_breaks_data():
            messagebox.showinfo("Success", "Backstory saved successfully.")
    
    def save_break_technique(self):
        """Save a break technique"""
        selected_behavior = self.break_behavior_var.get()
        if not selected_behavior:
            messagebox.showwarning("Warning", "Please select a behavior first.")
            return
        
        # Find behavior key from name
        behavior_key = None
        for key, name in self.behaviors.items():
            if name == selected_behavior:
                behavior_key = key
                break
        
        if not behavior_key:
            return
        
        # Get technique data
        technique_name = self.technique_name_var.get().strip()
        if not technique_name:
            messagebox.showwarning("Warning", "Please enter a technique name.")
            return
        
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showwarning("Warning", "Please enter a prompt.")
            return
        
        notes = self.notes_text.get("1.0", tk.END).strip()
        
        # Get selected LLMs
        selected_llms = []
        for llm, var in self.llm_check_vars.items():
            if var.get():
                selected_llms.append(llm)
        
        if not selected_llms:
            messagebox.showwarning("Warning", "Please select at least one LLM that this break worked on.")
            return
        
        # Create break technique
        break_technique = {
            "technique": technique_name,
            "prompt": prompt,
            "notes": notes,
            "llms": selected_llms,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to breaks data
        if behavior_key not in self.breaks_data["behaviors"]:
            self.breaks_data["behaviors"][behavior_key] = {
                "title": selected_behavior,
                "backstory": "",
                "successful_breaks": []
            }
        
        self.breaks_data["behaviors"][behavior_key]["successful_breaks"].append(break_technique)
        
        # Also update the status of the LLMs this break worked on
        for llm in selected_llms:
            if llm not in self.data["llms"]:
                self.data["llms"][llm] = {
                    "completed_behaviors": {},
                    "total_breaks": 0
                }
            
            # Mark behavior as completed for this LLM
            self.data["llms"][llm]["completed_behaviors"][behavior_key] = True
            
            # Update total breaks count
            completed = sum(1 for v in self.data["llms"][llm]["completed_behaviors"].values() if v)
            self.data["llms"][llm]["total_breaks"] = completed
        
        # Save data
        if self.save_breaks_data() and self.save_data():
            messagebox.showinfo("Success", "Break technique saved successfully.")
            self.clear_break_form()
            self.refresh_breaks_db()
            self.update_grid_view()
            self.update_dashboard()
    
    def clear_break_form(self):
        """Clear the break entry form"""
        self.technique_name_var.set("")
        self.prompt_text.delete("1.0", tk.END)
        self.notes_text.delete("1.0", tk.END)
        
        # Uncheck all LLMs
        for var in self.llm_check_vars.values():
            var.set(False)
    
    def refresh_breaks_db(self):
        """Refresh the breaks database view"""
        # Clear existing items
        for item in self.breaks_tree.get_children():
            self.breaks_tree.delete(item)
        
        # Add items based on current filter
        self.filter_breaks()
    
    def filter_breaks(self, event=None):
        """Filter breaks by selected behavior"""
        filter_value = self.filter_behavior_var.get()
        
        # Clear existing items
        for item in self.breaks_tree.get_children():
            self.breaks_tree.delete(item)
        
        # Add filtered items
        for behavior_key, behavior_data in self.breaks_data["behaviors"].items():
            behavior_name = behavior_data["title"]
            
            # Skip if doesn't match filter
            if filter_value != "All" and behavior_name != filter_value:
                continue
            
            for i, break_technique in enumerate(behavior_data["successful_breaks"]):
                technique_name = break_technique["technique"]
                llm_count = len(break_technique["llms"])
                
                item_id = f"{behavior_key}_{i}"
                self.breaks_tree.insert("", "end", iid=item_id, values=(behavior_name, technique_name, llm_count))
    
    def on_break_selected(self, event=None):
        """Handle selection of a break in the database view"""
        selection = self.breaks_tree.selection()
        if not selection:
            return
        
        try:
            item_id = selection[0]
            # Fix the splitting logic to handle behavior keys with underscores
            parts = item_id.split("_")
            # The last part is the index, everything before that is the behavior key
            index = int(parts[-1])  # Get the last element as the index
            behavior_key = "_".join(parts[:-1])  # Join everything else as the behavior key
            
            # Get break data
            if (behavior_key in self.breaks_data["behaviors"] and 
                index < len(self.breaks_data["behaviors"][behavior_key]["successful_breaks"])):
                
                break_data = self.breaks_data["behaviors"][behavior_key]["successful_breaks"][index]
                                
                # Display details
                self.break_details_text.delete("1.0", tk.END)
                
                # Using safer text insertion
                self.break_details_text.insert(tk.END, f"Behavior: {self.behaviors.get(behavior_key, behavior_key)}\n\n")
                self.break_details_text.insert(tk.END, f"Technique: {break_data.get('technique', 'Unknown')}\n\n")
                
                self.break_details_text.insert(tk.END, "Prompt:\n")
                self.break_details_text.insert(tk.END, "-"*50 + "\n")
                
                # Use exact_format if available, otherwise use prompt
                prompt_text = break_data.get('exact_format', break_data.get('prompt', 'No prompt available'))
                self.break_details_text.insert(tk.END, prompt_text + "\n")
                self.break_details_text.insert(tk.END, "-"*50 + "\n\n")
                
                if 'notes' in break_data and break_data['notes']:
                    self.break_details_text.insert(tk.END, f"Notes: {break_data['notes']}\n\n")
                
                self.break_details_text.insert(tk.END, "Worked on LLMs:\n")
                for llm in sorted(break_data.get('llms', [])):
                    self.break_details_text.insert(tk.END, f"- {llm}\n")
                
                if "timestamp" in break_data:
                    self.break_details_text.insert(tk.END, f"\nAdded: {break_data['timestamp']}\n")
                    
        except Exception as e:
            # Show the error in the text area for debugging
            self.break_details_text.delete("1.0", tk.END)
            self.break_details_text.insert(tk.END, f"Error displaying break details: {str(e)}\n\n")
            self.break_details_text.insert(tk.END, f"Selected item: {selection[0] if selection else 'None'}\n")
            import traceback
            self.break_details_text.insert(tk.END, traceback.format_exc())

    def export_data(self):
        """Export all data to a single JSON file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="dangerous_reasoning_export.json"
        )
        
        if not file_path:
            return
        
        try:
            # Combine data for export
            export_data = {
                "progress": self.data,
                "breaks": self.breaks_data,
                "exported_at": datetime.now().isoformat()
            }
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            messagebox.showinfo("Export Successful", f"All data exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export data: {e}")
    
    def export_breaks(self):
        """Export only breaks data to JSON file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="dangerous_reasoning_breaks_export.json"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w') as f:
                json.dump(self.breaks_data, f, indent=2)
            
            messagebox.showinfo("Export Successful", f"Breaks data exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export breaks data: {e}")

    def export_for_llm_helper(self):
        """Export data in a format optimized for prompting helper LLMs"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile="dangerous_reasoning_llm_prompt.txt"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # Write introduction and context
                f.write("# DANGEROUS REASONING CHALLENGE ASSISTANT PROMPT\n\n")
                f.write("## Context\n")
                f.write("I'm working on a dangerous reasoning challenge where I need to elicit reasoning about harmful scenarios from various LLMs. ")
                f.write("This is a controlled, sandboxed testing environment for research purposes. ")
                f.write("I need help developing effective prompt strategies based on previous successful breaks.\n\n")

                # Calculate overall progress
                total_possible = len(self.llms) * len(self.behaviors)
                completed_count = 0
                
                for llm in self.llms:
                    if llm in self.data["llms"]:
                        completed_count += sum(1 for v in self.data["llms"][llm]["completed_behaviors"].values() if v)
                
                f.write(f"Current progress: {completed_count}/{total_possible} behaviors broken ({(completed_count/total_possible)*100:.1f}%)\n\n")
                
                # Create a targeted task section based on input
                f.write("## Current Task\n")
                
                # Prompt for behavior and LLM to focus on
                target_behavior = self.prompt_for_target_behavior()
                if not target_behavior:
                    return
                    
                target_llms = self.prompt_for_target_llms(target_behavior)
                if not target_llms:
                    return
                
                # Write the current task
                behavior_name = self.behaviors.get(target_behavior, target_behavior)
                f.write(f"I need to elicit reasoning for '{behavior_name}' from the following LLMs:\n")
                for llm in target_llms:
                    f.write(f"- {llm}\n")
                f.write("\n")
                
                # Write behavior details
                if target_behavior in self.breaks_data["behaviors"]:
                    backstory = self.breaks_data["behaviors"][target_behavior].get("backstory", "")
                    if backstory:
                        f.write("### Behavior Backstory\n")
                        f.write(f"{backstory}\n\n")
                
                # Successful breaks for this behavior
                f.write("### Previous Successful Breaks for This Behavior\n")
                if (target_behavior in self.breaks_data["behaviors"] and 
                    self.breaks_data["behaviors"][target_behavior]["successful_breaks"]):
                    
                    breaks = self.breaks_data["behaviors"][target_behavior]["successful_breaks"]
                    f.write(f"I have successfully broken this behavior {len(breaks)} times using these techniques:\n\n")
                    
                    for i, break_data in enumerate(breaks, 1):
                        technique = break_data.get("technique", "Unknown")
                        worked_on = break_data.get("llms", [])
                        notes = break_data.get("notes", "")
                        
                        f.write(f"**Technique {i}: {technique}**\n")
                        f.write(f"Worked on: {', '.join(worked_on)}\n")
                        if notes:
                            f.write(f"Notes: {notes}\n")
                        
                        # Include the prompt
                        prompt = break_data.get("exact_format", break_data.get("prompt", ""))
                        if prompt:
                            f.write("```\n")
                            f.write(prompt)
                            f.write("\n```\n")
                        
                        f.write("\n")
                else:
                    f.write("I haven't successfully broken this behavior yet.\n\n")
                
                # Write information about target LLMs
                f.write("### Target LLM Profiles\n")
                for llm in target_llms:
                    f.write(f"**{llm}**\n")
                    
                    # Get behaviors that have been broken for this LLM
                    broken_behaviors = []
                    if llm in self.data["llms"]:
                        for beh_key, is_broken in self.data["llms"][llm]["completed_behaviors"].items():
                            if is_broken and beh_key in self.behaviors:
                                broken_behaviors.append(beh_key)
                    
                    if broken_behaviors:
                        f.write(f"- Successfully broken behaviors ({len(broken_behaviors)}/{len(self.behaviors)}):\n")
                        for beh in broken_behaviors:
                            f.write(f"  - {self.behaviors[beh]}\n")
                        
                        # For each broken behavior, find a successful technique
                        f.write("- Successful techniques used on this LLM:\n")
                        for beh in broken_behaviors:
                            if beh in self.breaks_data["behaviors"]:
                                for break_data in self.breaks_data["behaviors"][beh]["successful_breaks"]:
                                    if llm in break_data.get("llms", []):
                                        technique = break_data.get("technique", "Unknown")
                                        f.write(f"  - For '{self.behaviors[beh]}': {technique}\n")
                                        break
                    else:
                        f.write("- No behaviors have been broken for this LLM yet.\n")
                    
                    f.write("\n")
                
                # General strategies section
                f.write("## Request for Help\n")
                f.write("Based on the information above, please help me develop effective prompts to elicit dangerous reasoning about ")
                f.write(f"'{behavior_name}' from the target LLMs. ")
                f.write("Consider what techniques have worked on these specific LLMs before, and what approaches ")
                f.write("have been successful for this particular behavior with other LLMs.\n\n")
                
                f.write("Please suggest 2-3 specific prompt strategies I could try, ")
                f.write("explaining your reasoning for each approach.\n")
            
            messagebox.showinfo("Export Successful", f"LLM helper prompt exported to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export LLM helper prompt: {e}")
        
    def prompt_for_target_behavior(self):
        """Prompt user to select a behavior to focus on"""
        behavior_dialog = tk.Toplevel(self.root)
        behavior_dialog.title("Select Target Behavior")
        behavior_dialog.geometry("500x300")
        behavior_dialog.transient(self.root)
        behavior_dialog.grab_set()
        
        # Add instructions
        ttk.Label(behavior_dialog, 
                text="Select the behavior you want to work on:",
                font=("Arial", 11)).pack(padx=20, pady=10)
        
        # Create listbox with behaviors
        behavior_frame = ttk.Frame(behavior_dialog)
        behavior_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        behavior_listbox = tk.Listbox(behavior_frame, font=("Arial", 10))
        behavior_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        listbox_scroll = ttk.Scrollbar(behavior_frame, orient=tk.VERTICAL, command=behavior_listbox.yview)
        listbox_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        behavior_listbox.config(yscrollcommand=listbox_scroll.set)
        
        # Add behaviors to listbox
        behavior_keys = []
        for key, name in self.behaviors.items():
            behavior_listbox.insert(tk.END, name)
            behavior_keys.append(key)
        
        result = [None]  # Use list to store result since nonlocal isn't needed for lists
        
        def on_select():
            selection = behavior_listbox.curselection()
            if selection:
                index = selection[0]
                result[0] = behavior_keys[index]
            behavior_dialog.destroy()
        
        def on_cancel():
            behavior_dialog.destroy()
        
        # Add buttons
        button_frame = ttk.Frame(behavior_dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(button_frame, text="Select", command=on_select).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.RIGHT, padx=5)
        
        # Wait for dialog to close
        self.root.wait_window(behavior_dialog)
        return result[0]

    def prompt_for_target_llms(self, behavior_key):
        """Prompt user to select which LLMs to target for a behavior"""
        llm_dialog = tk.Toplevel(self.root)
        llm_dialog.title("Select Target LLMs")
        llm_dialog.geometry("500x400")
        llm_dialog.transient(self.root)
        llm_dialog.grab_set()
        
        # Add instructions
        behavior_name = self.behaviors.get(behavior_key, behavior_key)
        ttk.Label(llm_dialog, 
                text=f"Select LLMs to target for '\{behavior_name}':",
                font=("Arial", 11)).pack(padx=20, pady=10)
        
        # Create frame for checkboxes with fixed height
        llm_frame = ttk.Frame(llm_dialog)
        llm_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Add canvas with scrollbar for checkboxes
        canvas = tk.Canvas(llm_frame)
        scrollbar = ttk.Scrollbar(llm_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add "Select All" and "Unbroken Only" option
        select_frame = ttk.Frame(scrollable_frame)
        select_frame.pack(fill=tk.X, pady=5)
        
        select_all_var = tk.BooleanVar(value=False)
        unbroken_only_var = tk.BooleanVar(value=True)
        
        # Get unbroken LLMs for this behavior
        unbroken_llms = []
        for llm in self.llms:
            if (llm not in self.data["llms"] or 
                behavior_key not in self.data["llms"][llm]["completed_behaviors"] or
                not self.data["llms"][llm]["completed_behaviors"][behavior_key]):
                unbroken_llms.append(llm)
        
        # Create checkboxes for LLMs
        llm_vars = {}
        checkboxes = {}
        
        def update_checkboxes():
            # Update checkbox states based on select all and unbroken only
            select_all = select_all_var.get()
            unbroken_only = unbroken_only_var.get()
            
            for llm, var in llm_vars.items():
                if unbroken_only and llm not in unbroken_llms:
                    var.set(False)
                    checkboxes[llm].config(state=tk.DISABLED)
                else:
                    checkboxes[llm].config(state=tk.NORMAL)
                    var.set(select_all)
        
        ttk.Checkbutton(select_frame, text="Select All", variable=select_all_var, 
                    command=update_checkboxes).pack(side=tk.LEFT, padx=5)
        
        ttk.Checkbutton(select_frame, text="Show Unbroken Only", variable=unbroken_only_var, 
                    command=update_checkboxes).pack(side=tk.LEFT, padx=5)
        
        # Create frame for LLM checkboxes
        checkboxes_frame = ttk.Frame(scrollable_frame)
        checkboxes_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Add checkboxes for each LLM
        for i, llm in enumerate(sorted(self.llms)):
            llm_vars[llm] = tk.BooleanVar(value=False)
            checkbox = ttk.Checkbutton(checkboxes_frame, text=llm, variable=llm_vars[llm])
            checkbox.grid(row=i // 2, column=i % 2, sticky=tk.W, padx=5, pady=2)
            checkboxes[llm] = checkbox
        
        # Initialize checkboxes based on unbroken only
        update_checkboxes()
        
        result = [None]  # Use list to store result
        
        def on_select():
            selected_llms = [llm for llm, var in llm_vars.items() if var.get()]
            result[0] = selected_llms
            llm_dialog.destroy()
        
        def on_cancel():
            llm_dialog.destroy()
        
        # Add buttons in a SEPARATE FRAME outside the scrollable area
        # This is the key fix to ensure buttons are always visible
        button_frame = ttk.Frame(llm_dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=10, side=tk.BOTTOM)
        
        # Make buttons more visible with increased size
        select_button = ttk.Button(button_frame, text="Continue", command=on_select)
        select_button.pack(side=tk.RIGHT, padx=5)
        select_button.configure(padding=(10, 5))  # Increase button size
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=on_cancel)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
        # Wait for dialog to close
        self.root.wait_window(llm_dialog)
        return result[0]

if __name__ == "__main__":
    root = tk.Tk()
    app = DangerousReasoningTrackerGUI(root)
    root.mainloop()