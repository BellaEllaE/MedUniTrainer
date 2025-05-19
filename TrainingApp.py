# Standard library imports
import tkinter as tk
from tkinter import ttk
from tkinter import Label
import time
import sys
from math import pi
from random import randint
import json
import threading
import tkinter.messagebox as messagebox
import os
from datetime import datetime


# Third-party library imports
import usb.util
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

# Local application imports
from HeartRateSensor import HeartRateSensor
from rpm_calculator import RPMCalculator
from cadence_sensor_manager import CadenceSensorManager
#from CalculationEngine import CalculationEngine
from TrainingDataManager import TrainingDataManager


class TrainingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Training App")
        self.geometry("480x800")
        self.attributes('-fullscreen', True)
        self.configure(bg="#111d4e")
        style = ttk.Style()
        style.configure('TFrame', background='#111d4e')
        style.configure('TLabel', background='#111d4e')
        style.configure('Navigation.TButton', background='#111d4e')
        style.configure('Light.TButton', background='#e0e0e0', foreground='black')

        # Initialize class variables
        self.frames = {}
        self.resistance_level = 1
        self.cadence = 0
        self.power_values = []  # To store power values for average calculation
        self.total_distance = 0.0  # Initialize total distance

        # Initialize training manager
        self.training_manager = TrainingDataManager()
        self.training_sessions = self.training_manager.load_training_sessions()  # gets data from saved files

        # Initialize the sensors
        self.sensor_manager = CadenceSensorManager()
        self.sensor_manager.start_SensorRead()
        self.heart_rate_sensor = HeartRateSensor()

        # Create top navigation bar first (will stay on top)
        top_nav = ttk.Frame(self)
        top_nav.pack(side="top", fill="x")
        self.create_navigation()

        # Create bottom navigation bar next
        bottom_nav = ttk.Frame(self)
        bottom_nav.pack(side="bottom", fill="x", pady=(0, 3))  # Add padding at bottom
        self.create_bottom_navigation_fixed(bottom_nav)

        # Create main content container between nav bars
        # Main container
        main_container = ttk.Frame(self)
        main_container.pack(fill="both", expand=True)

        # Create container for pages
        container = ttk.Frame(main_container)
        container.pack(fill="both", expand=True, padx=3, pady=(10, 20))  # Only pack()
        #container.grid_columnconfigure(0, weight=1)


        # Create and pack frames
        for F in (StartPage, TrainingPage, StatisticsPage, GraphsPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.pack(fill="both", expand=True)  # Change grid() to pack()

        # Show initial frame
        self.show_frame("TrainingPage")

    def get_next_training_name(self):
        """Gibt den nächsten Trainingsnamen basierend auf Datum & Uhrzeit zurück."""
        return time.strftime("%Y-%m-%d %H:%M:%S")

    def show_frame(self, page_name):
        #print(f"DEBUG: show_frame({page_name}) wird aufgerufen.")

        if page_name not in self.frames:
            print(f"ERROR: Frame {page_name} not found!")
            return

        # Verstecke alle Frames
        for frame in self.frames.values():
            frame.pack_forget()  # Entfernt das aktuelle Frame aus der Ansicht

        # Zeige das gewünschte Frame
        frame = self.frames[page_name]
        frame.pack(fill="both", expand=True)
        #print(f"DEBUG: {page_name} wurde sichtbar gemacht.")

        # Falls Statistiken aktualisiert werden sollen
        if page_name == "StatisticsPage":
            frame.update_stats()
        if page_name == "StartPage":
            frame.update_all_stats()

    def create_navigation(self):
        top_nav_frame = ttk.Frame(self)
        top_nav_frame.pack(side="top", fill="x")

        logo_image = tk.PhotoImage(file="/home/pi/MedUniTrainer/images/MedUniWienLogo.png")
        logo_label = ttk.Label(top_nav_frame, image=logo_image)
        logo_label.image = logo_image
        logo_label.pack(side="left")

        exit_image = tk.PhotoImage(file="/home/pi/MedUniTrainer/images/exit.png")
        exit_button = ttk.Button(top_nav_frame, image=exit_image, style='Navigation.TButton', command=self.confirm_exit)
        exit_button.image = exit_image
        exit_button.pack(side="right", padx=10, pady=10)

    def confirm_exit(self):
        self.show_custom_yesno_dialog(
            title="Confirm Exit",
            message="Are you sure you want to exit the program?",
            callback_yes=self.quit_app
        )

    def create_bottom_navigation_fixed(self, nav_frame):
        # Create a style for the bottom navigation
        style = ttk.Style()
        style.configure('Bottom.TFrame', background='#111d4e',foreground='white')
        nav_frame.configure(style='Bottom.TFrame')

        # Load images
        home_icon = tk.PhotoImage(file="/home/pi/MedUniTrainer/images/DetailStats.png")
        training_icon = tk.PhotoImage(file="/home/pi/MedUniTrainer/images/bike.png")
        stats_icon = tk.PhotoImage(file="/home/pi/MedUniTrainer/images/AllStats.png")

        # Create buttons with some padding

        training_button = ttk.Button(nav_frame, image=training_icon, style='Navigation.TButton',command=lambda: self.show_frame("TrainingPage"))
        training_button.image = training_icon
        training_button.pack(side="left", fill="x", expand=True, pady=2)

        stats_button = ttk.Button(nav_frame, image=stats_icon, style='Navigation.TButton',command=lambda: self.show_frame("StatisticsPage"))
        stats_button.image = stats_icon
        stats_button.pack(side="left", fill="x", expand=True, pady=2)

        home_button = ttk.Button(nav_frame, image=home_icon, style='Navigation.TButton',command=lambda: self.show_frame("StartPage"))
        home_button.image = home_icon
        home_button.pack(side="left", fill="x", expand=True, pady=2)

    def show_custom_yesno_dialog(self, title, message, callback_yes, callback_no=None):
        popup = tk.Toplevel(self)
        popup.title(title)
        popup.geometry("360x180")
        popup.configure(bg="#111d4e")
        popup.transient(self)
        popup.grab_set()

        ttk.Label(popup, text=message,font=("Helvetica", 13, "bold"), style="White.TLabel", wraplength=320, anchor="center"
        ).pack(pady=(30, 20))

        button_frame = ttk.Frame(popup, style='TFrame')
        button_frame.pack()

        ttk.Button(button_frame, text="Yes", style='Light.TButton',command=lambda: [popup.destroy(), callback_yes()]
        ).pack(side="left", padx=10)

        ttk.Button( button_frame, text="No", style='Light.TButton',command=lambda: [popup.destroy()] if not callback_no else [popup.destroy(), callback_no()]
        ).pack(side="left", padx=10)

    def quit_app(self):
        # Stoppe alle Threads und führe eine saubere Beendigung durch
        if self.sensor_manager:
            self.sensor_manager.stop()  # Stoppt den Simulationsthread
        if self.heart_rate_sensor:
            self.heart_rate_sensor.stop()
        self.destroy()  # Schließt das Tkinter Fenster
        sys.exit()  # Beendet das Programm vollständig


class StartPage(ttk.Frame):
    # this was the AllStatisticsPage, it has been changed in it location
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Main container
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill='both', expand=True)

        # Create frames for different views
        self.graph_frame = ttk.Frame(self.main_container)
        self.stats_frame = ttk.Frame(self.main_container)

        # Initialize the graph view
        self.create_graph_view()

        # Initialize the stats view (your existing text view)
        self.create_stats_view()

        # Create button frame
        button_frame = ttk.Frame(self.main_container)
        button_frame.pack(pady=8, side='bottom')

        # Create buttons
        # self.back_button = ttk.Button(button_frame, text="Back", command=self.back_to_main)
        # self.back_button.pack(side=tk.LEFT, padx=5)

        self.toggle_view_button = ttk.Button(button_frame, text="Overview of Trainings", command=self.toggle_view)
        self.toggle_view_button.pack(side=tk.LEFT, padx=5)

        self.delete_all_button = ttk.Button(button_frame, text="Delete All Trainings",command=self.delete_all_trainings)
        self.delete_all_button.pack(side=tk.LEFT, padx=5)

        # Show graph view by default
        self.show_graph_view()
        self.update_graph()
        self.update_all_stats()  # Your existing stats update method

    def create_graph_view(self):
        # Add title label for the graph view
        title_label = ttk.Label(self.graph_frame, text="All Trainings - Overview Charts", font=("Helvetica", 16, "bold"), foreground='white')
        title_label.pack(pady=10)

        # Create Figure and Canvas for the graph
        self.fig = Figure(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # Update the graph
        self.update_graph()

    def shorten_name(self, name, max_length=5):
        """Zeigt Tag und Monat aus dem Timestamp (Format: 'YYYY-MM-DD HH:MM:SS') an."""
        try:
            date_part = name[:10]  # Beispiel: '2025-02-11'
            date_obj = datetime.strptime(date_part, "%Y-%m-%d")
            return date_obj.strftime("%d.%m.")
        except Exception as e:
            print(f"Fehler beim Kürzen des Namens ({name}): {e}")
            return name

    def update_graph(self):
        self.fig.clear()

        # ------------------- Daten extrahieren -------------------
        if not self.controller.training_sessions:
            ax = self.fig.add_subplot(111)
            ax.text(0.5, 0.5, "No training data available", ha='center', va='center')
            self.canvas.draw()
            return

        training_names = []
        max_heartrates = []
        avg_powers = []
        resistance_levels_per_training = []
        all_resistance_levels = set()

        for training in self.controller.training_sessions:
            training_name = training.get('training_name', 'Unknown')
            shortened_name = self.shorten_name(training_name)
            training_names.append(shortened_name)

            # Max HR
            max_heartrates.append(
                max(entry['heartrate'] for entry in training['data']) if training['data'] else 0
            )

            # Avg Power
            avg_power = sum(entry['power'] for entry in training['data']) / len(training['data']) if training[
                'data'] else 0
            avg_powers.append(avg_power)

            # Resistance Times
            resistance_summary = training.get('resistance_summary', [])
            if not isinstance(resistance_summary, list):
                resistance_summary = []

            time_in_levels = {}
            for entry in resistance_summary:
                level = entry['resistance_level']
                time_in_levels[level] = entry['total_time'] / 60  # Minuten
                all_resistance_levels.add(level)

            resistance_levels_per_training.append(time_in_levels)

        # ------------------- Plot: Max HR & Avg Power (Linien) -------------------
        ax1 = self.fig.add_subplot(211)

        x = np.arange(len(training_names))

        # Max HR als Linie
        ax1.plot(x, max_heartrates, 'r-o', label='Max Heart Rate', linewidth=2, alpha=0.7)
        ax1.set_ylabel('Max HR (BPM)', color='r')
        ax1.tick_params(axis='y', labelcolor='r')
        ax1.set_ylim(bottom=0)

        # Avg Power als Linie (zweite Y-Achse)
        ax2 = ax1.twinx()
        ax2.plot(x, avg_powers, 'b-s', label='Avg Power', linewidth=2, alpha=0.7)
        ax2.set_ylabel('Avg Power (W)', color='b')
        ax2.tick_params(axis='y', labelcolor='b')
        ax2.set_ylim(bottom=0)

        # X-Achsen-Ticks & Label
        ax1.set_xticks(x)
        ax1.set_xticklabels(training_names, rotation=45, ha="right", fontsize=7)

        # Legende kombinieren
        ax1_lines, ax1_labels = ax1.get_legend_handles_labels()
        ax2_lines, ax2_labels = ax2.get_legend_handles_labels()
        ax1.legend(ax1_lines + ax2_lines, ax1_labels + ax2_labels, loc='lower center', bbox_to_anchor=(0.5, 1.05), ncol=2,  handletextpad=0.5)

        ax1.grid(True, linestyle='--', alpha=0.5)

        # ------------------- Plot: Resistance Level Time (Bars) -------------------
        ax3 = self.fig.add_subplot(212)

        colors = ['#343cca', '#e29531', '#e6e446', '#a746e6', '#4be646', '#46c8e6', '#dc2727', '#180808']
        cumulative_time = np.zeros(len(training_names))

        sorted_levels = sorted(set(all_resistance_levels)) if all_resistance_levels else []

        for i, level in enumerate(sorted_levels):
            level_times = [
                resistance_levels.get(level, 0) for resistance_levels in resistance_levels_per_training
            ]

            ax3.bar(
                x,
                level_times,
                bottom=cumulative_time,
                color=colors[i % len(colors)],
                label=f"{level}",
                alpha=0.7
            )

            cumulative_time += np.array(level_times)

        ax3.set_ylabel('Time in Resistance Levels (minutes)')
        ax3.set_xticks(x)
        ax3.set_xticklabels(training_names, rotation=45, ha="right", fontsize=7)
        ax3.legend(title="Level", loc='upper right', bbox_to_anchor=(1.2, 1), borderaxespad=0, fontsize='small', title_fontsize='small')
        ax3.grid(True, linestyle='--', alpha=0.5)

        # ------------------- Layout & Anzeige -------------------
        self.fig.tight_layout(h_pad=0.5)
        self.canvas.draw()

    def update_all_stats(self):
        """Aktualisiert die Anzeige der Statistiken, neueste Trainings zuerst."""
        self.stats_text.delete(1.0, tk.END)

        # ✅ Sortiere die Trainings (neueste zuerst)
        training_sessions = sorted(
            self.controller.training_sessions,
            key=lambda x: parse_training_timestamp(x["timestamp"]),
            reverse=True
        )

        if not training_sessions:
            self.stats_text.insert(tk.END, "No training data available.\n")
            return

        for training in training_sessions:
            training_name = training.get('training_name', 'Unknown Training')
            timestamp = training.get('timestamp', 'Unknown Time')

            total_time = max((entry['time_seconds'] for entry in training['data']), default=0)
            total_distance = max((entry['distance'] for entry in training['data']), default=0)
            avg_cadence = sum(
                entry['cadence'] for entry in training['data']
            ) / len(training['data']) if training['data'] else 0

            stats_summary = (
                f"--------------------------------------\n"
                f"Training Name: {training_name}\n"
                f"Timestamp: {timestamp}\n"
                f"Total Time: {total_time:.0f} sec\n"
                f"Total Distance: {total_distance:.0f} m\n"
                f"Avg. Cadence: {avg_cadence:.1f} RPM\n"
            )

            self.stats_text.insert(tk.END, stats_summary + "\n\n")

            btn = ttk.Button(
                self.stats_frame,
                text=f"View Training {training_name}",
                command=lambda t=training: self.show_training_details(t)
            )
            self.stats_text.window_create(tk.END, window=btn)
            self.stats_text.insert(tk.END, "\n\n")

    def show_training_details(self, training):
        details = f"Training Details for {training['training_name']}:\n"
        tk.messagebox.showinfo("Training Details", details)

    def create_stats_view(self):
        # Add title label for the stats view
        title_label = ttk.Label(self.stats_frame, text="All Trainings - Overview Details", font=("Helvetica", 16, "bold"), foreground='white')
        title_label.pack(pady=10)

        # Your existing stats view code
        self.stats_text = tk.Text(self.stats_frame, height=30, width=50)
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.stats_frame, orient="vertical", command=self.stats_text.yview, width=30)
        self.scrollbar.pack(side=tk.RIGHT, fill='y')

        self.stats_text.config(yscrollcommand=self.scrollbar.set)

    def show_graph_view(self):
        self.stats_frame.pack_forget()
        self.graph_frame.pack(fill='both', expand=True, padx=10, pady=10)
        self.toggle_view_button.config(text="Overview of Trainings")
        self.update_graph()

    def show_stats_view(self):
        self.graph_frame.pack_forget()
        self.stats_frame.pack(fill='both', expand=True)
        self.toggle_view_button.config(text="Show Charts")
        self.update_all_stats()  # Your existing stats update method

    def toggle_view(self):
        if self.graph_frame.winfo_ismapped():
            self.show_stats_view()
        else:
            self.show_graph_view()

    def back_to_main(self):
        self.controller.show_frame("StatisticsPage")

    def delete_all_trainings(self):
        def confirmed_delete():
            if self.controller.training_sessions:
                try:
                    for filename in os.listdir(self.controller.training_manager.directory):
                        if filename.startswith("training_") and filename.endswith(".json"):
                            os.remove(os.path.join(self.controller.training_manager.directory, filename))

                    self.controller.training_sessions.clear()
                    self.controller.frames["StatisticsPage"].update_stats()
                    self.controller.frames["StartPage"].update_all_stats()
                    self.controller.frames["StartPage"].update_graph()
                    self.controller.frames["GraphsPage"].update_graphs()

                    self.controller.show_message("All trainings have been deleted.")
                except Exception as e:
                    print(f"Error: {e}")
            else:
                print("Error: No training data available.")

        self.controller.show_custom_yesno_dialog(
            title="Confirm Deletion",
            message="Are you sure you want to delete all trainings?",
            callback_yes=confirmed_delete
        )

    def update_all_stats(self):
        if self.stats_text:
            try:
                self.stats_text.delete(1.0, tk.END)

                # Check for data availability
                if not self.controller.training_sessions:
                    self.stats_text.insert(tk.END, "No training data available.")
                    return

                # Display training statistics in reverse order (newest first)
                for training in reversed(self.controller.training_sessions):
                    training_name = training.get('training_name', 'Unknown Training')  # Use get to avoid KeyError
                    total_time = max(entry['time_seconds'] for entry in training['data']) if training['data'] else 0
                    total_time += 1  # erhöht die angefangene Sekunde in der statistic damit logik erhalten bleibt
                    moving_time = sum(1 for entry in training['data'] if entry['cadence'] > 0)
                    total_distance = max(entry['distance'] for entry in training['data']) if training['data'] else 0
                    avg_cadence = sum(entry['cadence'] for entry in training['data']) / len(training['data']) if training['data'] else 0
                    avg_power = sum(entry['power'] for entry in training['data']) / len(training['data']) if training['data'] else 0
                    max_power = max(entry['power'] for entry in training['data']) if training['data'] else 0
                    avg_speed = sum(entry['speed'] for entry in training['data']) / len(training['data']) if training['data'] else 0
                    max_speed = max(entry['speed'] for entry in training['data']) if training['data'] else 0
                    max_heartrate = max(entry['heartrate'] for entry in training['data']) if training['data'] else 0

                    stats_summary = (
                        f"{'-' * 50}\n"
                        f"Training: {training_name}\n"
                        f"Total Time: {int(total_time // 3600):02}:{int((total_time % 3600) // 60):02}:{int(total_time % 60):02}\n"
                        f"Moving Time: {int(moving_time // 3600):02}:{int((moving_time % 3600) // 60):02}:{int(moving_time % 60):02}\n"
                        f"Total Distance: {total_distance:.0f} m\n"
                        f"Avg. Cadence: {avg_cadence:.0f} RPM\n"
                        f"Avg. Power: {avg_power:.1f} W\n"
                        f"Max. Power: {max_power:.1f} W\n"
                        f"Avg. Speed: {avg_speed:.2f} km/h\n"
                        f"Max. Speed: {max_speed:.2f} km/h\n"
                        f"Max. Heartrate: {max_heartrate:.0f} BPM\n"
                    )

                    self.stats_text.insert(tk.END, stats_summary)

                    # Button for more details
                    btn = ttk.Button(self.stats_frame, text=f"Details for Training {training_name}",
                                     command=lambda t=training: self.show_training_details(t))
                    self.stats_text.window_create(tk.END, window=btn)
                    self.stats_text.insert(tk.END, "\n\n")

            except tk.TclError as e:
                print(f"Error updating stats_text: {e}")

    def show_training_details(self, training):
        details = f"Training Details for Training Number {training['training_name']}:\n"
        # Training Details vorbereiten
        training_name = training['training_name']
        total_time = max((entry['time_seconds'] for entry in training['data']), default=0)
        moving_time = sum(1 for entry in training['data'] if entry['cadence'] > 0)
        total_distance = max(entry['distance'] for entry in training['data']) if training['data'] else 0
        avg_cadence = sum(entry['cadence'] for entry in training['data']) / len(training['data']) if training['data'] else 0
        avg_power = sum(entry['power'] for entry in training['data']) / len(training['data']) if training['data'] else 0
        max_power = max(entry['power'] for entry in training['data']) if training['data'] else 0
        avg_speed = sum(entry['speed'] for entry in training['data']) / len(training['data']) if training['data'] else 0
        max_speed = max(entry['speed'] for entry in training['data']) if training['data'] else 0
        max_heartrate = max(entry['heartrate'] for entry in training['data']) if training['data'] else 0

        # Zusammenfassung der Widerstandsdaten (falls verfügbar)
        resistance_summary = training.get('resistance_summary', [])
        resistance_info = "Resistance Level Summary:\nLevel -- Avg. Power -- Max. Power -- Time\n"
        for entry in sorted(resistance_summary, key=lambda x: x['resistance_level']):
            level = entry['resistance_level']
            total_time_level = entry['total_time']
            avg_power_level = entry['avg_power']
            max_power_level = entry.get('max_power', 0)

            resistance_info += (
                f"{level} -- {avg_power_level:.1f} W"
                f" -- {max_power_level:.1f} W"
                f" -- {int(total_time_level // 3600):02}:{int((total_time_level % 3600) // 60):02}:{int(total_time_level % 60):02}\n"
            )

        # Details formatieren
        details = (
            f"Training Number: {training_name}\n"
            f"Total Time: {int(total_time // 3600):02}:{int((total_time % 3600) // 60):02}:{int(total_time % 60):02}\n"
            f"Moving Time: {int(moving_time // 3600):02}:{int((moving_time % 3600) // 60):02}:{int(moving_time % 60):02}\n"
            f"Total Distance: {total_distance:.0f} m\n"
            f"Avg. Cadence: {avg_cadence:.0f} RPM\n"
            f"Avg. Power: {avg_power:.1f} W\n"
            f"Avg. Speed: {avg_speed:.2f} km/h\n"
            f"Max. Speed: {max_speed:.2f} km/h\n"
            f"Max. Heartrate: {max_heartrate:.0f} BPM\n\n"
            f"{resistance_info}"
        )

        # Popup-Fenster mit den Details anzeigen
        # tk.messagebox.showinfo("Training Details", details)
        self.show_large_messagebox(details, training)

    def delete_training(self, training, window):
        def confirmed_delete():
            timestamp = training.get('timestamp')
            if not timestamp:
                messagebox.showerror("Error", "No timestamp found for this training.")
                return

            filename = f"training_{timestamp.replace(':', '').replace(' ', '_')}.json"
            filepath = os.path.join(self.controller.training_manager.directory, filename)

            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    self.controller.training_sessions.remove(training)
                    self.controller.training_sessions = self.controller.training_manager.load_training_sessions()

                    self.update_all_stats()
                    self.update_graph()
                    self.controller.frames["GraphsPage"].update_graphs()

                    window.destroy()

                    messagebox.showinfo("Success", "Training session deleted successfully.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete training session: {e}")
            else:
                messagebox.showerror("Error", f"Training file '{filename}' not found.")

        self.controller.show_custom_yesno_dialog(
            title="Confirm Deletion",
            message="Are you sure you want to delete this training session?",
            callback_yes=confirmed_delete
        )



    def show_large_messagebox(self, message,training):
        # Create a new window
        custom_window = tk.Toplevel(self)
        custom_window.geometry("500x400")  # Adjust the size as needed
        custom_window.title("Training Details")

        # Stelle sicher, dass es immer im Vordergrund bleibt
        custom_window.transient(self)
        custom_window.lift()

        # Create a label to display the message
        message_label = tk.Label(custom_window, text=message, justify="left", wraplength=450)
        message_label.pack(padx=20, pady=20)

        # Create a frame for the buttons
        button_frame = tk.Frame(custom_window)
        button_frame.pack(pady=10, padx=10, fill='x')

        #sicheres Schließen
        def safe_close():
            custom_window.grab_release()
            custom_window.destroy()

        # Create a "Okay" button to close the window
        close_button = tk.Button(custom_window, text="Okay", command=safe_close)
        close_button.pack(side=tk.LEFT, padx=10, pady=5, expand=True)

        # Create delete button to delete the training.
        delete_button = tk.Button(button_frame, text="Delete this Training", command=lambda:self.delete_training(training,custom_window))
        delete_button.pack(side=tk.LEFT, padx=10, pady=5, expand=True)

        # Focus on the new window
        custom_window.grab_set()
        custom_window.focus_force()
        custom_window.protocol("WM_DELETE_WINDOW", safe_close)



class TrainingPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.running = False
        self.paused = False # Add a paused flag
        self.elapsed_time = 0
        self.last_update_time = 0
        self.last_3s_update = 0  # Separate variable for 3s interval
        self.resistance_data = {}  # Initialize resistance_data attribute
        self.moving_time = 0  # Initialisiere moving_time hier
        self.training_sessions_manager = TrainingDataManager()
        #self.training_sessions_manager.training_name = self.controller.get_next_training_name()

        self.current_training_data = []  # array für trainingsdaten
        self.resistance_buttons = {}  # iwas für die buttons 1-8 beim training


        style = ttk.Style()
        style.configure('White.TLabel', foreground='white', background='#111d4e', borderwidth=0, relief="solid",anchor='center')# farbe sollte #111d4e sein
        style.configure('Header.TLabel',foreground='#111d4e', background='white', borderwidth=0, relief="solid",anchor='center')
        style.configure('Grey.TLabel',foreground='#111d4e', background='#E7F3FB', borderwidth=0, relief="solid",anchor='center')
        style.configure('Highlighted.TButton', background='#1f6d6d', foreground='white')
        style.map('Highlighted.TButton',background=[('active', '#1f6d6d')])  # Setzt die Hintergrundfarbe, wenn der Button aktiv ist
        style.configure('Navigation.TButton', background='#111d4e')

        grid_frame = ttk.Frame(self)
        grid_frame.pack(expand=True, fill='both')

        # Configure the grid to expand and fill space
        for i in range(14):
            grid_frame.grid_rowconfigure(i, weight=1)
        for i in range(4):
            grid_frame.grid_columnconfigure(i, weight=1)

        self.datetime_label = ttk.Label(grid_frame, text="", font=("Helvetica", 26), style='Header.TLabel')
        self.datetime_label.grid(row=0, column=0, columnspan=4, pady=5, sticky='s')

        self.cadence_label_text = ttk.Label(grid_frame, text="CADENCE", font=("Helvetica", 10, "normal"),foreground='darkgrey', anchor='center')
        self.cadence_label_text.grid(row=1, column=0, padx=10, columnspan=2, sticky='sew')
        self.cadence_label_value = ttk.Label(grid_frame, text='--', font=("Helvetica", 35, "bold"),style='White.TLabel', width=15)
        self.cadence_label_value.grid(row=2, column=0, padx=2, pady=5, sticky='ne')
        self.cadence_label = ttk.Label(grid_frame, text="RPM", font=("Helvetica", 14), style='White.TLabel', width=30)
        self.cadence_label.grid(row=2, column=1, padx=2, pady=5, sticky='sw')

        self.speed_label_text = ttk.Label(grid_frame, text="SPEED", font=("Helvetica", 10, "normal"), foreground='darkgrey', anchor='center')
        self.speed_label_text.grid(row=1, column=2, padx=10, columnspan=2, sticky='sew')
        self.speed_label_value = ttk.Label(grid_frame, text='--', font=("Helvetica", 35, "bold"), style='White.TLabel',
                                           width=15)
        self.speed_label_value.grid(row=2, column=2, padx=2, pady=5, sticky='ne')
        self.speed_label = ttk.Label(grid_frame, text="km/h", font=("Helvetica", 14), style='White.TLabel', width=30)
        self.speed_label.grid(row=2, column=3, padx=2, pady=5, sticky='sw')

        self.time_label_text = ttk.Label(grid_frame, text="TIME", font=("Helvetica", 10, "normal"),
                                         foreground='darkgrey', anchor='center')
        self.time_label_text.grid(row=3, column=0, padx=5, columnspan=4, sticky='sew')
        self.time_label = ttk.Label(grid_frame, text="00:00:00", font=("Helvetica", 35, "bold"), style='White.TLabel',
                                    width=30)
        self.time_label.grid(row=4, column=0, padx=2, pady=5, columnspan=4, sticky='n')

        self.distance_label_text = ttk.Label(grid_frame, text="DISTANCE", font=("Helvetica", 10, "normal"),
                                             foreground='darkgrey', anchor='center')
        self.distance_label_text.grid(row=5, column=0, padx=10, columnspan=2, sticky='sew')
        self.distance_label_value = ttk.Label(grid_frame, text='--', font=("Helvetica", 35, "bold"),
                                              style='White.TLabel', width=15)
        self.distance_label_value.grid(row=6, column=0, padx=2, pady=5, sticky='n')
        self.distance_label = ttk.Label(grid_frame, text="m", font=("Helvetica", 14), style='White.TLabel', width=30)
        self.distance_label.grid(row=6, column=1, padx=2, pady=5, sticky='sw')

        self.power_label_text = ttk.Label(grid_frame, text="POWER (3s)", font=("Helvetica", 10, "normal"),
                                          foreground='darkgrey', anchor='center')
        self.power_label_text.grid(row=5, column=2, padx=10, columnspan=2, sticky='sew')
        self.power_label_value = ttk.Label(grid_frame, text='--', font=("Helvetica", 35, "bold"), style='White.TLabel',
                                           width=15)
        self.power_label_value.grid(row=6, column=2, padx=2, pady=5, sticky='n')
        self.power_label = ttk.Label(grid_frame, text="W", font=("Helvetica", 14), style='White.TLabel', width=30)
        self.power_label.grid(row=6, column=3, padx=2, pady=5, sticky='sw')

        self.heartrate_label_text = ttk.Label(grid_frame, text="HEART RATE", font=("Helvetica", 10, "normal"),
                                              foreground='darkgrey', anchor='center')
        self.heartrate_label_text.grid(row=7, column=0, padx=10, columnspan=4, sticky='sew')
        self.heartrate_label_value = ttk.Label(grid_frame, text='--', font=("Helvetica", 35, "bold"),
                                               style='White.TLabel', width=15)
        self.heartrate_label_value.grid(row=8, column=0, padx=2, pady=5, columnspan=4, sticky='n')
        self.heartrate_label = ttk.Label(grid_frame, text="BPM", font=("Helvetica", 14), style='White.TLabel', width=30)
        self.heartrate_label.grid(row=8, column=3, padx=2, pady=5, columnspan=2, sticky='sw')

        self.resistance_label = ttk.Label(grid_frame, text=f"RESISTANCE LEVEL:", font=("Helvetica", 10, "normal"),
                                          foreground='darkgrey', anchor='center')
        self.resistance_label.grid(row=10, column=0, padx=10, pady=5, columnspan=4, sticky='nswe')

        button_frame = ttk.Frame(grid_frame)
        button_frame.grid(row=11, column=0, columnspan=4, sticky='nsew')

        # Configure button_frame grid to expand and fill space
        for i in range(2):
            button_frame.grid_rowconfigure(i, weight=1)
        for i in range(5):
            button_frame.grid_columnconfigure(i, weight=1)

        # neuer style für Buttons resistance
        style.configure('Large.TButton', font=('Helvetica', 40), padding=(10, 30))

        # Erstellen von Reisistance Level Buttons in zwei reihen mit je 4 Buttons
        for i in range(1, 5):
            button = ttk.Button(button_frame, text=f"{i}", command=lambda i=i: self.set_resistance(i),
                                style='Large.TButton')
            button.grid(row=0, column=i - 1, padx=5, pady=5)
            self.resistance_buttons[i] = button  # Speichern der Button-Referenz

        for i in range(5, 9):
            button = ttk.Button(button_frame, text=f"{i}", command=lambda i=i: self.set_resistance(i),
                                style='Large.TButton')
            button.grid(row=1, column=i - 5, padx=5, pady=5)
            self.resistance_buttons[i] = button  # Speichern der Button-Referenz

        # setzen des resistance Wertes zu beginn auf 1
        self.set_resistance(1)

        # Stil element für Buttons Stop und Pause
        style.configure('Input.TButton', background='#111d4e', padding=(5, 2))

        # Create the Start/Stop button
        self.training_button_frame = ttk.Frame(button_frame)
        self.training_button_frame.grid(row=4, column=0, columnspan=4, pady=(22, 2), sticky='nsew')

        # Create Start and Stop icons
        self.start_icon = tk.PhotoImage(file="/home/pi/MedUniTrainer/images/STARTTraining.png")
        self.stop_icon = tk.PhotoImage(file="/home/pi/MedUniTrainer/images/STOPTraining.png")

        # Create the training button
        self.training_button = ttk.Button(self.training_button_frame,
                                          image=self.start_icon,
                                          style='Input.TButton',
                                          command=self.handle_training_button)
        self.training_button.pack(pady=2, padx=10, fill='x')

        self.update_datetime_label()

    def get_next_training_name(self):
        """Holt den nächsten verfügbaren Trainingsnamen aus TrainingDataManager."""
        return self.training_manager.get_next_training_name()

    def handle_training_button(self):
        if not self.running:
            # Start training
            self.start_training()
            self.training_button.config(image=self.stop_icon)
        else:
            # Show popup when stopping
            self.pause_training()
            self.show_stop_popup()

    def pause_training(self):
        self.paused = True
        self.running = False

    def show_stop_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Training Paused")
        popup.geometry("400x300")  # Made window slightly larger
        popup.configure(bg="#111d4e")

        # Center the popup
        popup.transient(self)
        popup.grab_set()

        # Create a style for larger buttons
        style = ttk.Style()
        style.configure('Popup.TButton', font=('Helvetica', 12, 'bold'), padding=(20, 10))

        # Create buttons with more padding
        ttk.Label(popup,
                  text="The training is currently paused!\nWhat would you like to do?",
                  style='White.TLabel',
                  font=('Helvetica', 14, 'bold')).pack(pady=30)

        ttk.Button(popup,
                   text="Resume Training",
                   style='Popup.TButton',
                   command=lambda: self.handle_popup_choice("resume", popup)).pack(pady=10, padx=40, fill='x')

        ttk.Button(popup,
                   text="Save Training",
                   style='Popup.TButton',
                   command=lambda: self.handle_popup_choice("save", popup)).pack(pady=10, padx=40, fill='x')

        ttk.Button(popup,
                   text="Discard Training",
                   style='Popup.TButton',
                   command=lambda: self.handle_popup_choice("discard", popup)).pack(pady=10, padx=40, fill='x')

    def handle_popup_choice(self, choice, popup):
        popup.destroy()

        if choice == "resume":
            self.resume_training()
        elif choice == "save":
            self.stop_training()
        elif choice == "discard":
            self.discard_training()

    def resume_training(self):
        self.paused = False
        self.running = True
        self.last_update_time = time.time()
        self.last_3s_update = time.time()
        self.update_values()
        self.training_button.config(image=self.stop_icon)

    def discard_training(self):
        self.running = False
        self.paused = False
        self.training_sessions_manager.reset_values()
        self.controller.frames["TrainingPage"].reset_values()
        self.training_button.config(image=self.start_icon)
        self.controller.show_frame("TrainingPage")
        self.training_sessions_manager.training_name = self.training_sessions_manager.get_next_training_name()
        #training_page.update_idletasks()

    def set_resistance(self, level):
        # Hintergrundfarbe für alle Buttons zurücksetzen
        for button_level, button in self.resistance_buttons.items():
            button.config(style='White.TButton')

        # Hintergrundfarbe für den aktuell ausgewählten Button ändern
        if level in self.resistance_buttons:
            self.resistance_buttons[level].config(style='Highlighted.TButton')

        self.controller.resistance_level = level
        # self.resistance_label.config(text=f"RESISTANCE LEVEL {level}")

    def reset_values(self):
        self.cadence_label_value.config(text="--")
        self.speed_label_value.config(text="--")  # Korrektur für die Anzeige von Geschwindigkeit
        self.time_label.config(text="00:00:00")  # Setzt die Zeit auf 0
        self.distance_label_value.config(text="--")
        self.power_label_value.config(text="--")
        self.heartrate_label_value.config(text="--")

        self.set_resistance(1)  # setzte resistance level auf 1
        self.elapsed_time = 0  # Setze die vergangene Zeit zurück
        self.last_update_time = time.time()  # Setze den letzten Update-Zeitstempel zurück
        self.last_3s_update = time.time()  # Setze den 3-Sekunden-Update-Zeitstempel zurück
        self.moving_time = 0  # Setze moving_time zurück

        self.controller.total_distance = 0
        self.controller.power_values.clear()  # Reset the power values when resetting
        self.controller.sensor_manager.reset()  # Diese Zeile ruft den Reset im CadenceSensorManager auf

        # Setzt die im DataManager gespeicherten Daten zurück
        self.training_sessions_manager.reset_values()

        # Force UI refresh
        self.update_idletasks()


    def start_training(self):
        if not self.running:
            self.running = True
            self.training_sessions_manager.training_name = self.controller.get_next_training_name()
            self.reset_values()  # Reset values when starting new training
            self.start_timer()
            self.update_values()  # Startet das Speichern der Werte

    def stop_training(self):
        if self.running or self.paused:
            self.running = False
            self.paused = False

            filepath = self.training_sessions_manager.save_training_session()

            if not filepath:
                print("FEHLER: Kein Trainingsfile wurde gespeichert!")
                return

            self.training_sessions_manager.save_training_session()  # Nur EIN Aufruf
            self.controller.training_sessions = self.controller.training_manager.load_training_sessions()
            self.training_button.config(image=self.start_icon)
            self.reset_values()

            # Statistikseite aktualisieren und anzeigen
            self.controller.frames["StatisticsPage"].update_stats()
            self.controller.frames["StartPage"].update_all_stats()
            self.controller.frames["StartPage"].update_graph()
            self.controller.show_frame("StatisticsPage")

            #self.training_sessions_manager.reset_values()

    def start_timer(self):
        self.running = True
        self.last_update_time = time.time()
        self.last_3s_update = time.time()  # Initialize the last update time for pace and avg_power
        #self.update_values()

    def stop_timer(self):
        self.running = False
        self.save_training_data()  # Save training data when stopping
        self.controller.save_training_data()  # Save to JSON file
        self.controller.show_frame("StatisticsPage")  # Show statistics page after stopping

    def update_values(self):
        if not self.running:
            #print("⏸ DEBUG: Training pausiert, update_values() wird nicht ausgeführt.")
            return

        #current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #self.datetime_label.config(text=f"{current_datetime}")

        current_time = time.time()
        elapsed = current_time - self.last_update_time
        self.elapsed_time += elapsed
        self.last_update_time = current_time

        # Get real cadence value from SensorManager
        cadence = self.controller.sensor_manager.get_cadence() #für sensor diese zeile verwenden!!
        #cadence = randint(50, 55)

        # Get resistance level
        resistance_level = self.controller.resistance_level

        # Power calculation
        power = self.calculate_power(cadence, resistance_level)

        # Speed calculation
        speed = 0.2555 * power + (-0.0009104) * power ** 2 - 1.133 * 10 ** -6 * power ** 3
        speed = max(speed, 0)  # Stellt sicher, dass speed nicht negativ ist

        # Distance calculation
        distance_increment = speed * (elapsed / 3600) * 1000
        self.controller.total_distance += distance_increment

        # Get heart rate from sensor
        heart_rate = self.controller.heart_rate_sensor.get_heart_rate()
        if heart_rate == 0:  # If no heart rate is detected, use default value
            heart_rate = 0

        # Update display labels
        self.speed_label_value.config(text=f"{speed:.1f}")
        self.distance_label_value.config(text=f"{self.controller.total_distance:.0f}")
        self.time_label.config(text=f"{int(self.elapsed_time // 3600):02}:{int((self.elapsed_time % 3600) // 60):02}:{int(self.elapsed_time % 60):02}")
        # self.power_label_value.config(text=f"{power:.1f}")
        self.heartrate_label_value.config(text=f"{heart_rate}")
        self.cadence_label_value.config(text=f"{cadence}")
        # self.avg_power_label_value.config(text=f"{power:.1f}")

        # Speichere die Messwerte in den DataManager
        measurement = {
            "time_seconds": self.elapsed_time,
            "cadence": cadence,
            "resistance_level": resistance_level,
            "power": power,
            "speed": speed,
            "distance": self.controller.total_distance,
            "heartrate": heart_rate
        }


        self.training_sessions_manager.add_measurement(measurement)

        # Hier die Widerstandsdaten direkt speichern
        if cadence > 0:
            if resistance_level not in self.training_sessions_manager.resistance_data:
                self.training_sessions_manager.resistance_data[resistance_level] = {
                    'total_time': 0,
                    'total_power': 0,
                    'count': 0,
                }

            self.training_sessions_manager.resistance_data[resistance_level]['total_time'] += 1
            self.training_sessions_manager.resistance_data[resistance_level]['total_power'] += power
            self.training_sessions_manager.resistance_data[resistance_level]['count'] += 1

        #Speichern der Powerwerte für die 3 Sekunden Durchschnittsberechnung
        self.controller.power_values.append(power)

        # Check if 3 seconds have passed since the last pace and avg_power update
        if current_time - self.last_3s_update >= 3:
            self.update_3sek_interval(power, speed)
            self.last_3s_update = current_time

        if self.running:  # Verhindert Mehrfachaufruf
            self.after(1000, self.update_values)

    def update_3sek_interval(self, power, speed):

        # Prevent division by zero for pace calculation
        pace = 60 / speed if speed > 0 else float('inf')

        # avg. power calculation
        recent_powers = self.controller.power_values[-2:]  # get last 3 power values
        avg_power3 = sum(recent_powers) / len(recent_powers) if recent_powers else 0

        # self.pace_label.config(text=f"MIN/KM\n{pace:.2f} min")
        self.power_label_value.config(text=f"{avg_power3:.1f}")



    # werte der Hoetrainer messungen um Power zu berechnen
    def calculate_power(self, cadence, level):
        coefficients = {
            1: [-0.09886, 0.008774, -4.482e-5],
            2: [-0.0914, 0.01357, -6.128e-5],
            3: [0.03131, 0.014, -4.07e-5],
            4: [0.06623, 0.01848, -4.885e-5],
            5: [0.0339, 0.0255, -8.2e-5],
            6: [0.01525, 0.03527, -0.0001293],
            7: [0.08092, 0.04164, -0.0001593],
            8: [0.08516, 0.04835, -0.0001871]
        }

        a, b, c = coefficients[level]
        power = a * cadence + b * cadence ** 2 + c * cadence ** 3
        return max(0, power)  # Ensure power is non-negative

    def update_datetime_label(self):
        current_datetime = datetime.now().strftime("%d.%m.%Y %H:%M")
        self.datetime_label.config(text=f"  {current_datetime}  ")

        # Aktualisiere jede Sekunde
        self.after(3000, self.update_datetime_label)


class StatisticsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(expand=True, fill='both')

        # Create a heading label
        self.heading_label = ttk.Label(self.main_frame, text="Summary of last Training!", font=("Helvetica", 20), style='White.TLabel')
        self.heading_label.pack(pady=5)

        # Label für den Namen des Trainings
        self.training_name_label = ttk.Label(self.main_frame, text="", font=("Helvetica", 16, "italic"),style='White.TLabel')
        self.training_name_label.pack(pady=(0, 10))  # Etwas Abstand nach unten hinzufügen

        # Create a frame to hold the statistics
        self.stats_frame = ttk.Frame(self.main_frame)
        self.stats_frame.pack(expand=True, fill='both', padx=5, pady=10)

        # Configure the grid to expand and fill space
        for i in range(8):
            self.stats_frame.grid_rowconfigure(i, weight=1)
        for i in range(2):
            self.stats_frame.grid_columnconfigure(i, weight=1)

        # Create a label to display the total time
        self.total_time_label = ttk.Label(self.stats_frame, text="Total Time:", font=("Helvetica", 10),
                                          style='White.TLabel')
        self.total_time_label.grid(row=0, column=0, padx=5)
        # Create a label to display the total time value
        self.total_time_value_label = ttk.Label(self.stats_frame, text="", font=("Helvetica", 22), style='White.TLabel')
        self.total_time_value_label.grid(row=1, column=0, padx=5)

        self.moving_time_label = ttk.Label(self.stats_frame, text="Moving Time:", font=("Helvetica", 10),
                                           style='White.TLabel')
        self.moving_time_label.grid(row=0, column=1, padx=5)
        self.moving_time_value_label = ttk.Label(self.stats_frame, text="", font=("Helvetica", 22),
                                                 style='White.TLabel')
        self.moving_time_value_label.grid(row=1, column=1, padx=5)

        # Create a label to display the total distance
        self.total_distance_label = ttk.Label(self.stats_frame, text="Total Distance [m]", font=("Helvetica", 10),
                                              style='White.TLabel')
        self.total_distance_label.grid(row=2, column=0, padx=5)
        # Create a label to display the total distance value
        self.total_distance_value_label = ttk.Label(self.stats_frame, text="", font=("Helvetica", 22),
                                                    style='White.TLabel')
        self.total_distance_value_label.grid(row=3, column=0, padx=5)

        # Create a label to display the average cadence
        self.avg_cadence_label = ttk.Label(self.stats_frame, text="Avg. Cadence [RPM]", font=("Helvetica", 10),
                                           style='White.TLabel')
        self.avg_cadence_label.grid(row=2, column=1, padx=5)
        # Create a label to display the average cadence value
        self.avg_cadence_value_label = ttk.Label(self.stats_frame, text="", font=("Helvetica", 22),
                                                 style='White.TLabel')
        self.avg_cadence_value_label.grid(row=3, column=1, padx=5)

        # Create a label to display the average speed
        self.avg_speed_label = ttk.Label(self.stats_frame, text="Avg. Speed [km/h]", font=("Helvetica", 10),
                                         style='White.TLabel')
        self.avg_speed_label.grid(row=4, column=0, padx=5)
        # Create a label to display the average speed value
        self.avg_speed_value_label = ttk.Label(self.stats_frame, text="", font=("Helvetica", 22), style='White.TLabel')
        self.avg_speed_value_label.grid(row=5, column=0, padx=5)

        # Create a label to display the average power
        self.avg_power_label = ttk.Label(self.stats_frame, text="Avg. Power [W]:", font=("Helvetica", 10),
                                         style='White.TLabel')
        self.avg_power_label.grid(row=4, column=1, padx=5)
        # Create a label to display the average power value
        self.avg_power_value_label = ttk.Label(self.stats_frame, text="", font=("Helvetica", 22), style='White.TLabel')
        self.avg_power_value_label.grid(row=5, column=1, padx=5)

        # Create a label to display the maximum heartrate
        self.max_heartrate_label = ttk.Label(self.stats_frame, text="Max. Heartrate [BPM]:", font=("Helvetica", 10),
                                             style='White.TLabel')
        self.max_heartrate_label.grid(row=6, column=0, padx=5)
        # Create a label to display the maximum heartrate value
        self.max_heartrate_value_label = ttk.Label(self.stats_frame, text="", font=("Helvetica", 22),
                                                   style='White.TLabel')
        self.max_heartrate_value_label.grid(row=7, column=0, padx=5)

        # Create a label to display the peak power
        self.max_power_label = ttk.Label(self.stats_frame, text="Max Power [W]:", font=("Helvetica", 10),
                                         style='White.TLabel')
        self.max_power_label.grid(row=6, column=1, padx=5)
        # Create a label to display the moving time value
        self.max_power_value_label = ttk.Label(self.stats_frame, text="", font=("Helvetica", 22), style='White.TLabel')
        self.max_power_value_label.grid(row=7, column=1, padx=5)

        # Create a frame for resistance statistics
        self.resistance_frame = ttk.Frame(self.main_frame)
        self.resistance_frame.pack(expand=True, fill='both', padx=1, pady=1)

        # Configure the grid to expand and fill space
        for i in range(3):
            self.resistance_frame.grid_rowconfigure(i, weight=0)
        for i in range(1):
            self.resistance_frame.grid_columnconfigure(i, weight=1)

        # create header for resistance level overview
        self.resistance_header = ttk.Label(self.resistance_frame, text="Resistance Level Summary",
                                           font=("Helvetica", 16), style='White.TLabel', anchor='center')
        self.resistance_header.grid(row=0, padx=5)

        # row to show what will be displayed
        self.resistance_names = ttk.Label(self.resistance_frame,
                                          text="Level -- Avg. Power -- Max. Power -- Time per Level",
                                          font=("Helvetica", 12), style='White.TLabel', anchor='center')
        self.resistance_names.grid(row=1, padx=5)

        # label to show values of each resistance level
        self.resistance_value_label = ttk.Label(self.resistance_frame, text="", font=("Helvetica", 14),
                                                style='White.TLabel', anchor='center')
        self.resistance_value_label.grid(row=2, padx=1)

        # Create a single frame for the buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=(2, 2))  # Small padding around the row

        # Buttons on the same row
        self.show_graphs_button = ttk.Button(button_frame, text="Show Charts", command=self.show_graphs, width=20)
        self.show_graphs_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = ttk.Button(button_frame, text="Delete Training", command=self.delete_statistics,
                                        width=20)
        self.delete_button.pack(side=tk.LEFT, padx=5)

        # Initial statistics update
        self.update_stats()

    def back_to_main(self):
        self.controller.show_frame("StartPage")

    def delete_statistics(self):
        def confirmed_delete():
            if not self.controller.training_sessions:
                messagebox.showerror("Error", "No training sessions available to delete.")
                return

            last_training = self.controller.training_sessions[-1]
            timestamp = last_training.get('timestamp')
            if not timestamp:
                messagebox.showerror("Error", "Timestamp not found for the last training.")
                return

            filename = f"training_{timestamp.replace(':', '').replace(' ', '_')}.json"
            filepath = os.path.join(self.controller.training_manager.directory, filename)

            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    self.controller.training_sessions.pop()
                    self.controller.training_sessions = self.controller.training_manager.load_training_sessions()

                    self.update_stats()
                    self.controller.frames["StartPage"].update_all_stats()
                    self.controller.frames["StartPage"].update_graph()
                    self.controller.frames["GraphsPage"].update_graphs()

                    messagebox.showinfo("Success", "Last training session deleted successfully.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete training session: {e}")
            else:
                messagebox.showerror("Error", f"Training file '{filename}' not found.")

        self.controller.show_custom_yesno_dialog(
            title="Confirm Deletion",
            message="Are you sure you want to delete the last training session?",
            callback_yes=confirmed_delete
        )

    def show_all_trainings(self):
        self.controller.show_frame("StartPage")

    def update_stats(self):
        training_sessions = self.controller.training_sessions
        # Rufe get_resistance_summary() direkt vom Manager ab
        #resistance_summary = self.controller.training_sessions_manager.get_resistance_summary()

        if not training_sessions:
            self.total_time_value_label.config(text="No data")
            self.total_distance_value_label.config(text="")
            self.avg_cadence_value_label.config(text="")
            self.avg_power_value_label.config(text="")
            self.max_power_value_label.config(text="")
            self.avg_speed_value_label.config(text="")
            self.max_heartrate_value_label.config(text="")
            self.moving_time_value_label.config(text="")
            self.resistance_value_label.config(text="")
            return

        last_training = training_sessions[-1]  # Latest training session
        resistance_summary = last_training.get('resistance_summary', [])

        training_name = last_training.get('training_name', 'Unnamed Training')
        self.training_name_label.config(text=f"Training: {training_name}")

        # Format resistance level summary
        resistance_info = f"{'-' * 49}\n"  # Trennlinie aus 49 - erstellen Bsp: ------------------------------------------
        if not resistance_summary:
            resistance_info += "Keine Widerstandsdaten verfügbar.\n"
        else:
            for entry in sorted(resistance_summary, key=lambda x: x['resistance_level']):
                level = entry.get('resistance_level')
                total_time_level = entry.get('total_time')
                avg_power_level = entry.get('avg_power')
                max_power_level = entry.get('max_power',0)
                #Infos in die Schleife rein formatieren
                resistance_info += (
                    f"{level} -- {avg_power_level:.1f} W "
                    f"-- {max_power_level:.1f} W "
                    f"-- {int(total_time_level // 3600):02}:{int((total_time_level % 3600) // 60):02}:{int(total_time_level % 60):02}\n"
                )

        # Verwende die gespeicherten Widerstandsdaten, falls vorhanden
        total_time = max(entry['time_seconds'] for entry in last_training['data'])+1 if last_training['data'] else 0
        #total_time += 1  # erhöht die angefangene Sekunde in der statistic damit logik erhalten bleibt
        total_distance = max(entry['distance'] for entry in last_training['data']) if last_training['data'] else 0
        avg_cadence = sum(entry['cadence'] for entry in last_training['data']) / len(last_training['data']) if last_training['data'] else 0
        avg_power = sum(entry['power'] for entry in last_training['data']) / len(last_training['data']) if last_training['data'] else 0
        max_power = max(entry['power'] for entry in last_training['data']) if last_training['data'] else 0
        avg_speed = sum(entry['speed'] for entry in last_training['data']) / len(last_training['data']) if last_training['data'] else 0
        max_heartrate = max(entry['heartrate'] for entry in last_training['data']) if last_training['data'] else 0
        moving_time = sum(1 for entry in last_training['data'] if entry['cadence']-1 > 0)
        #moving_time = sum(entry['total_time'] for entry in resistance_summary) if resistance_summary else 0

        #Befüllen der Labels mit den Werten
        self.total_time_value_label.config(text=f"{int(total_time // 3600):02}:{int((total_time % 3600) // 60):02}:{int(total_time % 60):02}")
        self.total_distance_value_label.config(text=f"{total_distance:.0f}")
        self.avg_cadence_value_label.config(text=f"{avg_cadence:.0f}")
        self.avg_power_value_label.config(text=f"{avg_power:.1f}")
        self.max_power_value_label.config(text=f"{max_power:.1f}")
        self.avg_speed_value_label.config(text=f"{avg_speed:.1f}")
        self.max_heartrate_value_label.config(text=f"{max_heartrate:.0f}")
        self.moving_time_value_label.config(text=f"{int(moving_time // 3600):02}:{int((moving_time % 3600) // 60):02}:{int(moving_time % 60):02}")
        self.resistance_value_label.config(text=f"{resistance_info}")

        if not self.controller.training_sessions:
            print("❌ WARNUNG: Keine Trainingssessions gefunden!")
            return

        # Falls das letzte Training keine Daten enthält
        if not last_training.get("data"):
            print("❌ WARNUNG: Das letzte Training hat keine Daten oder ist None!")
            return

        if not training_sessions:
            self.total_time_value_label.config(text="No data")
            self.total_distance_value_label.config(text="")
            self.avg_cadence_value_label.config(text="")
            return

    def show_graphs(self):
        self.controller.frames["GraphsPage"].update_graphs()
        self.controller.show_frame("GraphsPage")

class GraphsPage(ttk.Frame):    #Graphs in StatisticsPage from LastTraining
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.graph_widgets = []  # Store graph widgets to manage updates

        # Main container
        main_container = ttk.Frame(self)
        main_container.pack(fill='both', expand=True)

        # Header with back button
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill='x', pady=5)

        back_button = ttk.Button(header_frame, text="Back",
                                 command=lambda: controller.show_frame("StatisticsPage"))
        back_button.pack(side='left', padx=5)

        # Canvas and scrollbar setup
        canvas_frame = ttk.Frame(main_container)
        canvas_frame.pack(fill='both', expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg='#111d4e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Scrollable frame inside canvas
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>",
                                   lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

    def update_graphs(self):
        """Clears old graphs and regenerates them with the latest data."""
        #for widget in self.graph_widgets:
        #   widget.get_tk_widget().destroy()
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.graph_widgets.clear()

        if not self.controller.training_sessions:
            ttk.Label(self.scrollable_frame, text="No training data available").pack()
            return

        # Get latest training data
        last_training_data = self.controller.training_sessions[-1]['data']
        times = [entry['time_seconds'] / 60 for entry in last_training_data]
        power_values = [entry['power'] for entry in last_training_data]
        heartrate_values = [entry['heartrate'] for entry in last_training_data]
        cadence_values = [entry['cadence'] for entry in last_training_data]
        speed_values = [entry['speed'] for entry in last_training_data]
        resistance_values = [entry['resistance_level'] for entry in last_training_data]

        if not times:  # Falls die Liste leer ist
            #print("WARNING: No training data available, cannot show graph.")
            ttk.Label(self.scrollable_frame, text="No valid training data available").pack()
            return  # Verlasse die Funktion ohne Fehler

        min_time, max_time = min(times), max(times)

        #Header to show which training you are looking at
        training_name = self.controller.training_sessions[-1].get('training_name', 'Unnamed Training')
        ttk.Label(self.scrollable_frame, text=f"Charts of last Training:\n{training_name}",font=('Arial', 14, 'bold'), foreground='white').pack(pady=(20, 5))
        # Power & Heart Rate Graph
        ttk.Label(self.scrollable_frame, text="Power and Heartrate", font=('Arial', 12, 'bold'), foreground='white').pack(pady=(15, 5))
        fig1, ax1 = self._create_dual_axis_graph(times, power_values, heartrate_values, 'Power (W)', 'Heart Rate (BPM)','b', 'r', min_time, max_time)
        canvas1 = FigureCanvasTkAgg(fig1, self.scrollable_frame)
        canvas1.draw()
        canvas1.get_tk_widget().pack(pady=10, padx=5, fill='x')
        self.graph_widgets.append(canvas1)

        # Cadence & Resistance Graph
        ttk.Label(self.scrollable_frame, text="Cadence and Resistance Level", font=('Arial', 12, 'bold'), foreground='white').pack(pady=(15, 5))
        fig2, ax2 = self._create_dual_axis_graph(times, cadence_values, resistance_values, 'Cadence (RPM)', 'Resistance Level', 'g', 'gray', min_time, max_time, resistance=True)
        canvas2 = FigureCanvasTkAgg(fig2, self.scrollable_frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(pady=10, padx=5, fill='x')
        self.graph_widgets.append(canvas2)

        # Speed & Resistance Graph
        ttk.Label(self.scrollable_frame, text="Speed and Resistance Level", font=('Arial', 12, 'bold'), foreground='white').pack(pady=(15, 5))
        fig3, ax3 = self._create_dual_axis_graph(times, speed_values, resistance_values, 'Speed (km/h)','Resistance Level', 'orange', 'gray', min_time, max_time,resistance=True)
        canvas3 = FigureCanvasTkAgg(fig3, self.scrollable_frame)
        canvas3.draw()
        canvas3.get_tk_widget().pack(pady=10, padx=5, fill='x')
        self.graph_widgets.append(canvas3)

    def _create_dual_axis_graph(self, times, primary_values, secondary_values, primary_label, secondary_label,primary_color, secondary_color, min_time, max_time, resistance=False):
        """Helper function to create dual-axis charts."""
        fig = Figure(figsize=(4.5, 3))
        ax1 = fig.add_subplot(111)

        ax1.plot(times, primary_values, color=primary_color, label=primary_label)
        ax1.set_xlabel('Time (min)')
        ax1.set_ylabel(primary_label, color=primary_color)
        ax1.tick_params(axis='y', labelcolor=primary_color)
        ax1.set_xlim(min_time, max_time)
        ax1.set_ylim(bottom=0)  # y-Achse beginnt bei 0
        #ax1.legend(loc='upper left')

        ax2 = ax1.twinx()
        ax2.plot(times, secondary_values, color=secondary_color, linestyle='--', label=secondary_label)
        ax2.set_ylabel(secondary_label, color=secondary_color)
        ax2.tick_params(axis='y', labelcolor=secondary_color)
        ax2.set_ylim(bottom=0)  # y-Achse beginnt bei 0
        #ax2.legend(loc='upper right')

        if resistance:
            ax2.set_ylim(0.5, 8.5)
            ax2.set_yticks(range(1, 9))
            ax2.grid(True, axis='y', linestyle=':', alpha=0.3)

        fig.tight_layout()
        return fig, ax1

    def show_graphs(self):
        """Switch to GraphsPage and update graphs."""
        self.controller.show_frame("GraphsPage")
        self.update_graphs()


if __name__ == "__main__":
    app = TrainingApp()
    app.mainloop()