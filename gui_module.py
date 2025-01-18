import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, filedialog
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import font as tkfont
from datetime import datetime
import csv

class FriendRecommendationApp:
    def __init__(self, root, ml_model, friend_recommendation):
        self.root = root
        self.ml_model = ml_model
        self.friend_recommendation = friend_recommendation
        
        # Initialize highlighted node before update_graph is called
        self.highlighted_node = None
        
        # Add network metrics
        self.network_metrics = self.calculate_metrics()
        
        # Add color variables
        self.node_color = tk.StringVar(value='#ADD8E6')
        self.edge_color = tk.StringVar(value='#666666')
        
        # Add theme variables
        self.current_theme = tk.StringVar(value="Light")
        self.themes = {
            "Light": {
                "bg": "#ffffff",
                "fg": "#000000",
                "button": "#f0f0f0",
                "frame": "#f5f5f5",
                "node": "#ADD8E6",
                "edge": "#666666"
            },
            "Dark": {
                "bg": "#2d2d2d",
                "fg": "#ffffff",
                "button": "#404040",
                "frame": "#363636",
                "node": "#4A90E2",
                "edge": "#888888"
            }
        }
        
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
        
        # Add keyboard shortcuts
        self.root.bind('<Control-f>', lambda e: self.user_entry.focus())
        self.root.bind('<Control-r>', lambda e: self.recommend())
        self.root.bind('<Control-z>', lambda e: self.clear_history())
        
        self.highlighted_node = None  # Add this line
        
    def create_menu_bar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Users Menu
        users_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Users", menu=users_menu)
        users_menu.add_command(label="Add New User", command=self.show_add_user_dialog)
        users_menu.add_command(label="Manage Connections", command=self.show_user_selector)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Node Color", command=self.change_node_color)
        view_menu.add_command(label="Edge Color", command=self.change_edge_color)
        
        # Add theme selector
        appearance_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Theme", menu=appearance_menu)
        themes = ["Light", "Dark", "System"]
        for theme in themes:
            appearance_menu.add_command(label=theme, command=lambda t=theme: self.change_theme(t))
        
        # Theme menu
        theme_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Theme", menu=theme_menu)
        for theme in self.themes.keys():
            theme_menu.add_radiobutton(
                label=theme,
                variable=self.current_theme,
                value=theme,
                command=lambda t=theme: self.change_theme(t)
            )
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.show_user_guide)
        help_menu.add_command(label="About", command=self.show_about)

        # Add export menu
        export_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Export", menu=export_menu)
        export_menu.add_command(label="Save Graph as PNG", command=self.export_graph)
        export_menu.add_command(label="Export Results as CSV", command=self.export_results)

    def show_add_user_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New User")
        dialog.geometry("400x500")
        dialog.transient(self.root)
        
        # User details fields
        ttk.Label(dialog, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        username_entry = ttk.Entry(dialog)
        username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Age:").grid(row=1, column=0, padx=5, pady=5)
        age_entry = ttk.Entry(dialog)
        age_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Location:").grid(row=2, column=0, padx=5, pady=5)
        location_entry = ttk.Entry(dialog)
        location_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Occupation:").grid(row=3, column=0, padx=5, pady=5)
        occupation_entry = ttk.Entry(dialog)
        occupation_entry.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Interests (comma separated):").grid(row=4, column=0, padx=5, pady=5)
        interests_entry = ttk.Entry(dialog)
        interests_entry.grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Activities:").grid(row=5, column=0, padx=5, pady=5)
        activities_entry = ttk.Entry(dialog)
        activities_entry.grid(row=5, column=1, padx=5, pady=5)
        
        def add_user():
            username = username_entry.get().strip()
            if not username:
                messagebox.showwarning("Error", "Username is required")
                return
                
            if username in self.friend_recommendation.social_network:
                messagebox.showerror("Error", "Username already exists")
                return
                
            # Create new user profile
            new_user = {
                'interests': interests_entry.get().split(','),
                'friends': [],
                'age': int(age_entry.get()),
                'location': location_entry.get(),
                'occupation': occupation_entry.get(),
                'activities': activities_entry.get()
            }
            
            # Update data structures
            self.friend_recommendation.user_profiles[username] = new_user
            self.friend_recommendation.social_network.add_node(username)
            
            # Update visualization
            self.update_graph()
            
            # Show success message
            messagebox.showinfo("Success", f"User {username} added successfully!")
            
            # Create manage connections button after successful add
            ttk.Button(dialog, 
                      text="Manage Connections", 
                      command=lambda u=username: self.manage_connections(u)).grid(
                          row=7, column=0, columnspan=2, pady=10)
        
        ttk.Button(dialog, text="Add User", command=add_user).grid(
            row=6, column=0, columnspan=2, pady=20)

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
        
        # Add search filters
        filter_frame = ttk.LabelFrame(self.left_panel, text="Filters")
        ttk.Checkbutton(filter_frame, text="Same Location").pack()
        ttk.Checkbutton(filter_frame, text="Similar Age").pack()
        ttk.Checkbutton(filter_frame, text="Similar Interests").pack()
        
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
        
        # self.add_analytics_panel()
        # self.add_statistics_dashboard()
        self.add_comparison_tool()
        
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

        self.add_graph_search()
        self.add_quick_actions()

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
            
            # Update node colors based on highlighted node
            node_colors = [
                '#FF0000' if node == self.highlighted_node else self.node_color.get()
                for node in self.friend_recommendation.social_network.nodes()
            ]
            
            nx.draw(
                self.friend_recommendation.social_network,
                pos,
                with_labels=True,
                node_color=node_colors,  # Use node_colors instead of single color
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
            
            # Replace hover event with click event
            def on_click(event):
                if event.inaxes:
                    for node, (x, y) in pos.items():
                        if abs(event.xdata - x) < 0.02 and abs(event.ydata - y) < 0.02:
                            self.show_user_info(node)
                            return  # Exit after first match
            
            # Connect click event instead of hover
            canvas.mpl_connect('button_press_event', on_click)
            
            # Add cursor change on hover for better UX
            def on_hover(event):
                if event.inaxes:
                    for node, (x, y) in pos.items():
                        if abs(event.xdata - x) < 0.02 and abs(event.ydata - y) < 0.02:
                            canvas.get_tk_widget().config(cursor="hand2")
                            return
                    canvas.get_tk_widget().config(cursor="")
            
            canvas.mpl_connect('motion_notify_event', on_hover)
            
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

    def export_graph(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                initialfile=f"social_network_{timestamp}.png",
                filetypes=[("PNG files", "*.png")]
            )
            if filename:
                plt.savefig(filename, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Success", "Graph exported successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export graph: {str(e)}")

    def export_results(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                initialfile=f"recommendations_{timestamp}.csv",
                filetypes=[("CSV files", "*.csv")]
            )
            if filename:
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Timestamp', 'User', 'Recommendations'])
                    for entry in self.search_history:
                        timestamp, user = entry.split(" - ")
                        recommendations = self.friend_recommendation.find_recommendations(user)
                        rec_list = [name for name, _ in recommendations]
                        writer.writerow([timestamp, user, ", ".join(rec_list)])
                messagebox.showinfo("Success", "Results exported successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export results: {str(e)}")

    def change_theme(self, theme_name):
        if theme_name not in self.themes:
            return
            
        theme = self.themes[theme_name]
        self.current_theme.set(theme_name)
        
        # Update root window
        self.root.configure(bg=theme["bg"])
        
        # Update all ttk styles
        style = ttk.Style()
        style.configure(".", background=theme["bg"], foreground=theme["fg"])
        style.configure("TLabel", background=theme["bg"], foreground=theme["fg"])
        style.configure("TFrame", background=theme["frame"])
        style.configure("TButton", background=theme["button"])
        
        # Update graph colors
        self.node_color.set(theme["node"])
        self.edge_color.set(theme["edge"])
        
        # Update graph
        self.update_graph()
        
    # def add_analytics_panel(self):
    #     analytics_frame = ttk.LabelFrame(self.left_panel, text="Network Analytics")
    #     analytics_frame.grid(row=4, column=0, sticky="ew", pady=10)
        
    #     # Add metrics
    #     row = 0
    #     for label, value in self.network_metrics.items():
    #         ttk.Label(analytics_frame, text=f"{label}:", style='Normal.TLabel').grid(
    #             row=row, column=0, sticky="w", padx=5, pady=2)
    #         ttk.Label(analytics_frame, text=str(value), style='Normal.TLabel').grid(
    #             row=row, column=1, sticky="w", padx=5, pady=2)
    #         row += 1
            
    #     # Add refresh button
    #     # ttk.Button(analytics_frame, text="Refresh Stats", command=self.refresh_analytics).grid(
    #     #     row=row, column=0, columnspan=2, pady=5)

    def refresh_analytics(self):
        self.network_metrics = self.calculate_metrics()
        # Clear and rebuild analytics panel
        for widget in self.left_panel.winfo_children():
            if isinstance(widget, ttk.LabelFrame) and widget.winfo_children()[0].cget("text") == "Network Analytics":
                widget.destroy()
        self.add_analytics_panel()

    def calculate_metrics(self):
        try:
            network = self.friend_recommendation.social_network
            return {
                "Total Users": len(network.nodes()),
                "Average Friends": f"{sum(dict(network.degree()).values()) / len(network.nodes()):.2f}",
                "Network Density": f"{nx.density(network):.3f}",  # Fixed format string
                "Most Connected": max(dict(network.degree()).items(), key=lambda x: x[1])[0]
            }
        except Exception as e:
            print(f"Error calculating metrics: {e}")
            return {
                "Total Users": 0,
                "Average Friends": "0.00",
                "Network Density": "0.000",
                "Most Connected": "None"
            }

    def show_user_info(self, username):
        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title(f"User Profile: {username}")
        popup.geometry("400x350")
        popup.transient(self.root)  # Make it modal
        popup.grab_set()  # Make it modal
        
        # Center the window
        popup.update_idletasks()
        width = popup.winfo_width()
        height = popup.winfo_height()
        x = (popup.winfo_screenwidth() // 2) - (width // 2)
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry(f'+{x}+{y}')
        
        # Main frame
        main_frame = ttk.Frame(popup, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Get user profile
        user_profile = self.friend_recommendation.user_profiles[username]
        
        # Profile information
        info = {
            "Username": username,
            "Age": user_profile['age'],
            "Location": user_profile['location'],
            "Occupation": user_profile['occupation'],
            "Activities": user_profile['activities'],
            "Friends": len(user_profile['friends'])
        }
        
        # Display info
        for i, (key, value) in enumerate(info.items()):
            ttk.Label(main_frame, text=f"{key}:", style='Header.TLabel').grid(
                row=i, column=0, sticky='w', padx=5, pady=5)
            ttk.Label(main_frame, text=str(value), style='Normal.TLabel').grid(
                row=i, column=1, sticky='w', padx=5, pady=5)
        
        # Close button
        ttk.Button(main_frame, text="Close", command=popup.destroy).grid(
            row=len(info), column=0, columnspan=2, pady=20)
        
        # Add manage connections button
        ttk.Button(main_frame, text="Manage Connections", 
                  command=lambda: self.manage_connections(username)).grid(
                      row=len(info)+1, column=0, columnspan=2, pady=10)

    def add_graph_search(self):
        search_frame = ttk.Frame(self.right_panel)
        search_frame.grid(row=3, column=0, sticky="ew", pady=5)
        
        ttk.Label(search_frame, text="Find User:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side="left", padx=5)
        
        def find_user():
            username = self.search_entry.get().strip()
            if not username:
                messagebox.showwarning("Search Error", "Please enter a username")
                return
                
            if username not in self.friend_recommendation.social_network:
                messagebox.showerror("Error", f"User '{username}' not found")
                return
                
            self.highlighted_node = username
            self.update_graph()
            self.show_user_info(username)
        
        def clear_highlight():
            self.highlighted_node = None
            self.update_graph()
            self.status_var.set("Highlight cleared")
        
        ttk.Button(search_frame, text="Find", command=find_user).pack(side="left", padx=5)
        ttk.Button(search_frame, text="Clear Highlight", command=clear_highlight).pack(side="left", padx=5)

    def highlight_node(self, username):
        # Store current colors
        current_colors = nx.get_node_attributes(self.friend_recommendation.social_network, 'color')
        
        # Set all nodes to default color except searched node
        nx.set_node_attributes(self.friend_recommendation.social_network, self.node_color.get(), 'color')
        nx.set_node_attributes(self.friend_recommendation.social_network, {username: '#FF0000'}, 'color')
        
        # Update graph
        self.update_graph()
        
        # Show user profile
        self.show_user_info(username)
        
    # def add_statistics_dashboard(self):
    #     stats_frame = ttk.LabelFrame(self.left_panel, text="Network Statistics")
    #     stats_frame.grid(row=5, column=0, sticky="ew", pady=10)
        
    #     # Add stats with real-time updates
    #     stats = {
    #         "Network Diameter": nx.diameter(self.friend_recommendation.social_network),
    #         "Clustering Coefficient": f"{nx.average_clustering(self.friend_recommendation.social_network):.2f}",
    #         "Average Path Length": f"{nx.average_shortest_path_length(self.friend_recommendation.social_network):.2f}"
    #     }
        
    #     for i, (key, value) in enumerate(stats.items()):
    #         ttk.Label(stats_frame, text=f"{key}:").grid(row=i, column=0, padx=5, pady=2, sticky="w")
    #         ttk.Label(stats_frame, text=str(value)).grid(row=i, column=1, padx=5, pady=2, sticky="w")

    def add_comparison_tool(self):
        compare_frame = ttk.LabelFrame(self.left_panel, text="Compare Users")
        compare_frame.grid(row=6, column=0, sticky="ew", pady=10)
        
        # User 1 field
        ttk.Label(compare_frame, text="User 1:").grid(row=0, column=0, padx=5, pady=5)
        self.user1_entry = ttk.Entry(compare_frame, width=20)
        self.user1_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # User 2 field
        ttk.Label(compare_frame, text="User 2:").grid(row=1, column=0, padx=5, pady=5)
        self.user2_entry = ttk.Entry(compare_frame, width=20)
        self.user2_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Compare button
        ttk.Button(compare_frame, text="Compare Users", 
                   command=self.compare_users).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Result display
        self.compare_result = tk.StringVar()
        ttk.Label(compare_frame, textvariable=self.compare_result, 
                  wraplength=250).grid(row=3, column=0, columnspan=2, pady=5)

    def add_quick_actions(self):
        actions_frame = ttk.LabelFrame(self.left_panel, text="Quick Actions")
        actions_frame.grid(row=7, column=0, sticky="ew", pady=10)
        
        actions = [
            ("Find Most Connected", self.find_most_connected),
            ("Show Communities", self.show_communities),
            ("Export Network", self.export_network)
        ]
        
        # Add buttons in a vertical layout
        for i, (text, command) in enumerate(actions):
            ttk.Button(actions_frame, text=text, command=command).grid(
                row=i, column=0, padx=5, pady=2, sticky="ew")

    def compare_users(self):
        user1 = self.user1_entry.get().strip()
        user2 = self.user2_entry.get().strip()
        
        if not user1 or not user2:
            messagebox.showwarning("Input Error", "Please enter both usernames")
            return
            
        if user1 not in self.friend_recommendation.user_profiles or \
           user2 not in self.friend_recommendation.user_profiles:
            messagebox.showerror("Error", "One or both users not found")
            return
        
        # Calculate similarities
        mutual_friends = set(self.friend_recommendation.user_profiles[user1]['friends']) & \
                        set(self.friend_recommendation.user_profiles[user2]['friends'])
        
        shared_interests = set(self.friend_recommendation.user_profiles[user1]['interests']) & \
                          set(self.friend_recommendation.user_profiles[user2]['interests'])
        
        comparison = f"Comparison Results:\n\n" \
                    f"Mutual Friends: {len(mutual_friends)}\n" \
                    f"Shared Interests: {len(shared_interests)}\n" \
                    f"Same Location: {'Yes' if self.friend_recommendation.user_profiles[user1]['location'] == self.friend_recommendation.user_profiles[user2]['location'] else 'No'}"
        
        messagebox.showinfo("User Comparison", comparison)

    def find_most_connected(self):
        degrees = dict(self.friend_recommendation.social_network.degree())
        most_connected = max(degrees.items(), key=lambda x: x[1])
        messagebox.showinfo("Most Connected User", 
                           f"User: {most_connected[0]}\nConnections: {most_connected[1]}")

    def show_communities(self):
        communities = list(nx.community.greedy_modularity_communities(
            self.friend_recommendation.social_network))
        result = "Communities detected:\n\n"
        for i, community in enumerate(communities, 1):
            result += f"Community {i}: {len(community)} members\n"
        messagebox.showinfo("Community Detection", result)

    def export_network(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".gexf",
            filetypes=[("GEXF files", "*.gexf"), ("All files", "*.*")]
        )
        if filename:
            nx.write_gexf(self.friend_recommendation.social_network, filename)
            messagebox.showinfo("Success", "Network exported successfully!")

    def manage_connections(self, username):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Manage Connections for {username}")
        dialog.geometry("400x600")
        dialog.transient(self.root)
        
        # Current connections frame
        current_frame = ttk.LabelFrame(dialog, text="Current Connections")
        current_frame.pack(pady=5, padx=5, fill="x")
        
        current_listbox = tk.Listbox(current_frame, selectmode=tk.MULTIPLE, height=5)
        current_listbox.pack(pady=5, fill="x")
        
        # Populate current connections
        current_friends = self.friend_recommendation.user_profiles[username]['friends']
        for friend in current_friends:
            current_listbox.insert(tk.END, friend)
        
        # Available users frame
        available_frame = ttk.LabelFrame(dialog, text="Available Users")
        available_frame.pack(pady=5, padx=5, fill="both", expand=True)
        
        available_listbox = tk.Listbox(available_frame, selectmode=tk.MULTIPLE, height=10)
        available_listbox.pack(pady=5, fill="both", expand=True)
        
        # Populate available users (excluding current connections)
        for user in self.friend_recommendation.social_network.nodes():
            if user != username and user not in current_friends:
                available_listbox.insert(tk.END, user)
        
        def remove_connections():
            selected = [current_listbox.get(idx) for idx in current_listbox.curselection()]
            if not selected:
                messagebox.showwarning("Warning", "Please select connections to remove")
                return
                
            for friend in selected:
                # Remove bidirectional connection
                self.friend_recommendation.social_network.remove_edge(username, friend)
                
                # Update both users' profiles
                self.friend_recommendation.user_profiles[username]['friends'].remove(friend)
                self.friend_recommendation.user_profiles[friend]['friends'].remove(username)
                
                # Move to available list
                current_listbox.delete(0, tk.END)
                available_listbox.insert(tk.END, friend)
                
                # Refresh current connections list
                for f in self.friend_recommendation.user_profiles[username]['friends']:
                    current_listbox.insert(tk.END, f)
        
        def add_connections():
            selected = [available_listbox.get(idx) for idx in available_listbox.curselection()]
            if not selected:
                messagebox.showwarning("Warning", "Please select users to connect with")
                return
                
            for friend in selected:
                # Add bidirectional connection
                self.friend_recommendation.social_network.add_edge(username, friend)
                
                # Update both users' profiles
                self.friend_recommendation.user_profiles[username]['friends'].append(friend)
                self.friend_recommendation.user_profiles[friend]['friends'].append(username)
                
                # Move to current list
                available_listbox.delete(0, tk.END)
                current_listbox.insert(tk.END, friend)
                
                # Refresh available users list
                for user in self.friend_recommendation.social_network.nodes():
                    if user != username and user not in self.friend_recommendation.user_profiles[username]['friends']:
                        available_listbox.insert(tk.END, user)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Remove Selected", command=remove_connections).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Add Selected", command=add_connections).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Save Changes", command=lambda: self.save_changes(dialog)).pack(side="left", padx=5)

    def save_changes(self, dialog):
        self.update_csv_file()
        self.update_graph()
        dialog.destroy()
        messagebox.showinfo("Success", "Connections updated successfully!")

    def update_csv_file(self):
        with open('/Users/karem/Documents/GitHub/Friends_Recommendation_System/user_profiles.csv', 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['name', 'interests', 'friends', 'age', 'location', 'occupation', 'activities'])
            writer.writeheader()
            
            for username, profile in self.friend_recommendation.user_profiles.items():
                writer.writerow({
                    'name': username,
                    'interests': ', '.join(profile['interests']),
                    'friends': ', '.join(profile['friends']),
                    'age': profile['age'],
                    'location': profile['location'],
                    'occupation': profile['occupation'],
                    'activities': profile['activities']
                })

    def show_user_selector(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Select User")
        dialog.geometry("300x400")
        dialog.transient(self.root)
        
        ttk.Label(dialog, text="Select a user to manage connections:").pack(pady=5)
        
        # User listbox
        users_listbox = tk.Listbox(dialog, height=10)
        users_listbox.pack(pady=5, fill=tk.BOTH, expand=True)
        
        # Populate users
        for user in sorted(self.friend_recommendation.social_network.nodes()):
            users_listbox.insert(tk.END, user)
        
        def on_select():
            if not users_listbox.curselection():
                messagebox.showwarning("Warning", "Please select a user")
                return
            username = users_listbox.get(users_listbox.curselection())
            dialog.destroy()
            self.manage_connections(username)
        
        ttk.Button(dialog, text="Manage Connections", command=on_select).pack(pady=10)
