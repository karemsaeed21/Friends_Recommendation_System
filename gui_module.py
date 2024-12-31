import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import font as tkfont
from datetime import datetime

class FriendRecommendationApp:
    def __init__(self, root, ml_model, friend_recommendation):
        self.root = root
        self.ml_model = ml_model
        self.friend_recommendation = friend_recommendation
        
        # Add color variables
        self.node_color = tk.StringVar(value='#ADD8E6')
        self.edge_color = tk.StringVar(value='#666666')
        
        # Add menu bar before other UI elements
        self.create_menu_bar()
        
        self.root.title("Social Network Friend Recommendation System")
        self.root.geometry("1500x900")
        self.root.configure(bg='#f0f0f0')
        
        # Create custom fonts
        self.title_font = tkfont.Font(family="Helvetica", size=24, weight="bold")
        self.header_font = tkfont.Font(family="Helvetica", size=14, weight="bold")
        self.normal_font = tkfont.Font(family="Helvetica", size=12)
        
        # Initialize history
        self.search_history = []
        
        self.setup_styles()
        self.create_gui()
        self.update_graph()
        
    def create_menu_bar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Node Color", command=self.change_node_color)
        view_menu.add_command(label="Edge Color", command=self.change_edge_color)
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.show_user_guide)
        help_menu.add_command(label="About", command=self.show_about)

    def change_node_color(self):
        color = colorchooser.askcolor(color=self.node_color.get())[1]
        if color:
            self.node_color.set(color)
            self.update_graph()

    def change_edge_color(self):
        color = colorchooser.askcolor(color=self.edge_color.get())[1]
        if color:
            self.edge_color.set(color)
            self.update_graph()

    def show_user_guide(self):
        messagebox.showinfo("User Guide",
            "1. Enter a username in the search box\n"
            "2. Click 'Find Recommendations' to get friend suggestions\n"
            "3. Use graph controls to adjust the visualization\n"
            "4. Change colors and layouts from the View menu")

    def show_about(self):
        messagebox.showinfo("About",
            "Social Network Friend Recommendation System\n"
            "Version 5.1\n"
            "Developed by *ASTERISK")

    def setup_styles(self):
        # Configure ttk styles
        style = ttk.Style()
        style.configure('Title.TLabel', font=self.title_font, padding=10)
        style.configure('Header.TLabel', font=self.header_font)
        style.configure('Normal.TLabel', font=self.normal_font)
        
        # Custom button style
        style.configure('Action.TButton',
                       font=self.normal_font,
                       padding=(20, 10),
                       background='#4CAF50')
        
        # Custom frame style
        style.configure('Card.TFrame', background='white', relief='raised')
        
    def create_gui(self):
        # Main container
        self.main_container = ttk.Frame(self.root, padding="20")
        self.main_container.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Left panel (Input and Results)
        self.left_panel = ttk.Frame(self.main_container)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Right panel (Graph)
        self.right_panel = ttk.Frame(self.main_container)
        self.right_panel.grid(row=0, column=1, sticky="nsew")
        
        self.main_container.grid_columnconfigure(0, weight=2)
        self.main_container.grid_columnconfigure(1, weight=3)
        
        self.create_left_panel()
        self.create_right_panel()
        
    def create_left_panel(self):
        # Title
        title = ttk.Label(
            self.left_panel,
            text="Friend Recommendation",
            style='Title.TLabel'
        )
        title.grid(row=0, column=0, pady=20, sticky="w")
        
        # Search section
        search_frame = ttk.LabelFrame(
            self.left_panel,
            text="Search User",
            padding="10"
        )
        search_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        # Search input
        self.user_entry = ttk.Entry(
            search_frame,
            font=self.normal_font,
            width=30
        )
        self.user_entry.grid(row=0, column=0, padx=5, pady=8)
        
        # Search button
        self.search_btn = ttk.Button(
            search_frame,
            text="Find Recommendations",
            style='Action.TButton',
            command=self.recommend
        )
        self.search_btn.grid(row=0, column=1, padx=5, pady=8)
        
        # Results section
        results_frame = ttk.LabelFrame(
            self.left_panel,
            text="Recommendations",
            padding="10"
        )
        results_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        
        self.result_var = tk.StringVar()
        self.result_label = ttk.Label(
            results_frame,
            textvariable=self.result_var,
            style='Normal.TLabel',
            wraplength=400
        )
        self.result_label.grid(row=0, column=0, padx=5, pady=5)
        
        # History section
        history_frame = ttk.LabelFrame(
            self.left_panel,
            text="Search History",
            padding="10"
        )
        history_frame.grid(row=3, column=0, sticky="ew")
        
        self.history_listbox = tk.Listbox(
            history_frame,
            font=self.normal_font,
            height=6
        )
        self.history_listbox.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.history_listbox.bind('<<ListboxSelect>>', self.on_history_select)
        
        # Clear history button
        clear_btn = ttk.Button(
            history_frame,
            text="Clear History",
            command=self.clear_history
        )
        clear_btn.grid(row=1, column=0, pady=5)
        
    def create_right_panel(self):
        # Graph controls frame
        controls_frame = ttk.Frame(self.right_panel)
        controls_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Zoom controls with spinbox
        ttk.Label(
            controls_frame,
            text="Graph Size:",
            style='Normal.TLabel'
        ).pack(side="left", padx=5)
        
        self.zoom_var = tk.StringVar(value="0.6")
        self.zoom_spinbox = ttk.Spinbox(
            controls_frame,
            from_=0.5,
            to=2.0,
            increment=0.1,
            textvariable=self.zoom_var,
            width=5,
            command=self.update_graph,
            font=self.normal_font
        )
        self.zoom_spinbox.pack(side="left", padx=5)
        self.zoom_spinbox.bind('<Return>', lambda e: self.update_graph())
        
        # Node size control with spinbox (replacing node spacing)
        ttk.Label(
            controls_frame,
            text="Node Size:",
            style='Normal.TLabel'
        ).pack(side="left", padx=5)
        
        self.node_size_var = tk.StringVar(value="1500")
        self.node_size_spinbox = ttk.Spinbox(
            controls_frame,
            from_=500,
            to=5000,
            increment=100,
            textvariable=self.node_size_var,
            width=5,
            command=self.update_graph,
            font=self.normal_font
        )
        self.node_size_spinbox.pack(side="left", padx=5)
        self.node_size_spinbox.bind('<Return>', lambda e: self.update_graph())
        
        # Add +/- buttons for zoom
        zoom_buttons_frame = ttk.Frame(controls_frame)
        zoom_buttons_frame.pack(side="left", padx=5)
        
        ttk.Button(
            zoom_buttons_frame,
            text="+",
            width=3,
            command=lambda: self.adjust_zoom(0.1)
        ).pack(side="left", padx=3)
        
        ttk.Button(
            zoom_buttons_frame,
            text="-",
            width=3,
            command=lambda: self.adjust_zoom(-0.1)
        ).pack(side="left", padx=3)
        
        # Add +/- buttons for node size
        node_size_buttons_frame = ttk.Frame(controls_frame)
        node_size_buttons_frame.pack(side="left", padx=5)
        
        ttk.Button(
            node_size_buttons_frame,
            text="+",
            width=3,
            command=lambda: self.adjust_node_size(100)
        ).pack(side="left", padx=3)
        
        ttk.Button(
            node_size_buttons_frame,
            text="-",
            width=3,
            command=lambda: self.adjust_node_size(-100)
        ).pack(side="left", padx=3)
        
        # Layout selection
        ttk.Label(
            controls_frame,
            text="Layout:",
            style='Normal.TLabel'
        ).pack(side="left", padx=5)
        
        self.layout_var = tk.StringVar(value="spring")
        layout_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.layout_var,
            values=["spring", "circular", "random", "shell"],
            width=10,
            state="readonly"
        )
        layout_combo.pack(side="left", padx=5)
        layout_combo.bind('<<ComboboxSelected>>', self.update_graph)
        
        # Refresh button
        ttk.Button(
            controls_frame,
            text="Refresh Layout",
            command=self.update_graph,
            style='Action.TButton'
        ).pack(side="right", padx=5)

        # Graph frame
        self.graph_frame = ttk.LabelFrame(
            self.right_panel,
            text="Network Visualization",
            padding="10"
        )
        self.graph_frame.grid(row=1, column=0, sticky="nsew")
        
        # Make the graph frame expandable
        self.right_panel.grid_rowconfigure(1, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(
            self.right_panel,
            textvariable=self.status_var,
            style='Normal.TLabel'
        )
        status_label.grid(row=2, column=0, sticky="w", pady=(5, 0))

    def update_graph(self, *args):
        # Clear previous graph
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
            
        try:
            # Get current zoom and node size values
            zoom = float(self.zoom_var.get())
            
            # Show warning if manually entered value is above 0.6
            if zoom > 0.6 and not hasattr(self, '_warning_shown'):
                response = messagebox.askokcancel(
                    "Warning",
                    "Graph size above 0.6 may hide control buttons.\n"
                    "0.6 is the recommended size for best view.\n\n"
                    "Do you want to continue?"
                )
                if not response:
                    self.zoom_var.set("0.6")
                    return
                self._warning_shown = True
            
            node_size = float(self.node_size_var.get())
                
            # Get selected layout
            layout_type = self.layout_var.get()
            if layout_type == "spring":
                pos = nx.spring_layout(self.friend_recommendation.social_network, k=1.5, iterations=50)
            elif layout_type == "circular":
                pos = nx.circular_layout(self.friend_recommendation.social_network)
            elif layout_type == "random":
                pos = nx.random_layout(self.friend_recommendation.social_network)
            elif layout_type == "shell":
                pos = nx.shell_layout(self.friend_recommendation.social_network)
                
            # Create new graph with current size
            fig, ax = plt.subplots(figsize=(8 * zoom, 6 * zoom))
            
            nx.draw(
                self.friend_recommendation.social_network,
                pos,
                with_labels=True,
                node_color=self.node_color.get(),
                node_size=node_size * zoom,  # Use node_size variable
                font_size=8 * zoom,
                font_weight='bold',
                edge_color=self.edge_color.get(),
                width=1.5,
                ax=ax
            )
            
            plt.title("Social Network Graph", pad=20, fontsize=14)
            plt.tight_layout()
            
            # Create canvas with better size management
            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            
            # Pack canvas with expansion
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(fill=tk.BOTH, expand=True)
            
            # Add canvas resize handling
            def on_resize(event):
                w, h = event.width, event.height
                fig.set_size_inches(w/fig.dpi, h/fig.dpi)
                canvas.draw()
                
            canvas_widget.bind('<Configure>', on_resize)
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for Graph Size and Node Size")
            self.zoom_var.set("0.6")
            self.node_size_var.set("2000")

    def recommend(self):
        user = self.user_entry.get().strip()
        if not user:
            messagebox.showwarning("Input Error", "Please enter a username")
            return
            
        if user not in self.friend_recommendation.social_network:
            messagebox.showerror("Error", f"User '{user}' not found in the network")
            return
            
        # Add to history
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.search_history.append(f"{timestamp} - {user}")
        self.history_listbox.insert(0, f"{timestamp} - {user}")
        
        # Update status
        self.status_var.set(f"Finding recommendations for {user}...")
        
        # Find recommendations
        recommendations = self.friend_recommendation.find_recommendations(user)
        
        if recommendations:
            rec_list = [name for name, _ in recommendations]
            self.result_var.set(f"Recommendations for {user}:\n{', '.join(rec_list)}")
        else:
            self.result_var.set(f"No recommendations found for {user}")
            
        self.status_var.set("Ready")
        
    def on_history_select(self, event):
        selection = self.history_listbox.curselection()
        if selection:
            item = self.history_listbox.get(selection[0])
            user = item.split(" - ")[1]
            self.user_entry.delete(0, tk.END)
            self.user_entry.insert(0, user)
            
    def clear_history(self):
        self.search_history.clear()
        self.history_listbox.delete(0, tk.END)

    def adjust_zoom(self, delta):
        """Adjust zoom level by delta amount"""
        try:
            current = float(self.zoom_var.get())
            new_value = round(current + delta, 1)
            
            # Check if trying to increase beyond 0.6
            if new_value > 0.6 and current <= 0.6:
                response = messagebox.askokcancel(
                    "Warning",
                    "Increasing the graph size beyond 0.6 may hide control buttons.\n"
                    "0.6 is the recommended size for best view.\n\n"
                    "Do you want to continue?"
                )
                if not response:
                    return
                
            # Continue with the adjustment if within bounds
            if 0.5 <= new_value <= 2.0:
                self.zoom_var.set(f"{new_value:.1f}")
                self.update_graph()
        except ValueError:
            self.zoom_var.set("0.6")  # Changed default to 0.6

    def adjust_node_size(self, delta):
        """Adjust node size by delta amount"""
        try:
            current = float(self.node_size_var.get())
            new_value = round(current + delta)
            if 500 <= new_value <= 5000:
                self.node_size_var.set(str(new_value))
                self.update_graph()
        except ValueError:
            self.node_size_var.set("2000")
