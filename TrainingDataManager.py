import os
import json
import time
from datetime import datetime

# ✅ Die Funktion muss vor `TrainingDataManager` stehen!
def parse_training_timestamp(timestamp):
    """Versucht, den Zeitstempel aus der Datei in ein `datetime`-Objekt zu konvertieren."""
    formats = ["%Y-%m-%d %H:%M:%S", "%d-%m-%Y %H:%M", "%Y%m%d_%H%M%S"]  # Mögliche Formate
    for fmt in formats:
        try:
            return datetime.strptime(timestamp, fmt)
        except ValueError:
            continue
    print(f"Fehler: Unbekanntes Zeitformat '{timestamp}', setze aktuelles Datum.")
    return datetime.now()

class TrainingDataManager:
    def __init__(self, directory="/home/pi/MedUniTrainer/training_sessions"):
        self.directory = directory
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        self.resistance_data = {}  # Widerstandsdaten sammeln
        self.current_training_data = []  # Einzelne Messwerte pro Sekunde
        self.training_name = ""
        self.timestamp = ""

    def add_measurement(self, measurement):
        """Fügt einen Messwert zur aktuellen Trainingssession hinzu."""
        #print(f"📏 DEBUG: add_measurement() wurde aufgerufen mit {measurement}")
        self.current_training_data.append(measurement)

    def get_resistance_summary(self):
        """Berechnet eine Zusammenfassung der Widerstandsdaten."""
        resistance_summary = []
        for level, data in self.resistance_data.items():
            if data['count'] > 0:
                avg_power = data['total_power'] / data['count']
                max_power = max(
                    entry['power'] for entry in self.current_training_data
                    if entry['resistance_level'] == level
                ) if data['count'] > 0 else 0

                resistance_summary.append({
                    'resistance_level': level,
                    'total_time': data['total_time'],
                    'avg_power': round(avg_power, 1),
                    'max_power': round(max_power, 1)
                })

        return sorted(resistance_summary, key=lambda x: x['resistance_level'])

    def reset_values(self):
        """Setzt die aktuellen Trainingsdaten zurück."""
        self.current_training_data.clear()
        self.resistance_data.clear()
        self.training_name = ""
        self.timestamp = ""

    def save_training_session(self):
        """Speichert die aktuelle Trainingssession als JSON-Datei."""
        if not self.current_training_data:
            #Hier wird überprüft, ob es aktuell Trainingsdaten (self.current_training_data) gibt. Wenn die Liste oder das Dictionary leer ist, wird die Funktion ohne eine Datei zu erstellen beendet.
            return None

        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.training_name = self.timestamp
        filename = f"training_{self.timestamp.replace(':', '').replace(' ', '_')}.json"              #Dateiname genereieren
        filepath = os.path.join(self.directory, filename)           #Dateipfad zusammenführen
        resistance_summary = self.get_resistance_summary()

        training_data = {                                           #Dictionary für training erstellen
            "training_name": self.training_name,                    #Name Trainingssession
            "timestamp": self.timestamp, # Aktuelle Uhrzeit und Datum lesbar
            "data": self.current_training_data,                         #aktuelle Trainingsmesswerte
            "resistance_summary": resistance_summary
        }

        with open(filepath, "w") as f:                              #Speichern der Daten in JSON file
            json.dump(training_data, f, indent=4)                   #indent für bessere lebarkeit


        self.reset_values()
        return filepath

    def get_next_training_name(self):
        """Generiert einen neuen, eindeutigen Trainingsnamen basierend auf Datum & Uhrzeit."""
        return time.strftime("%Y-%m-%d %H:%M:%S")

    def load_training_sessions(self):
        """Lädt alle Trainingssessions aus dem Verzeichnis und sortiert nach Datum (neuste zuerst)."""
        sessions = []

        for filename in os.listdir(self.directory):
            if filename.startswith("training_") and filename.endswith(".json"):
                filepath = os.path.join(self.directory, filename)
                try:
                    with open(filepath, "r") as f:
                        data = json.load(f)

                    # Wenn kein Zeitstempel vorhanden, aktuelles Datum setzen
                    if "timestamp" not in data:
                        data["training_date"] = datetime.now()
                    else:
                        data["training_date"] = parse_training_timestamp(data["timestamp"])

                    sessions.append(data)

                except json.JSONDecodeError as e:
                    print(f"Fehler beim Dekodieren von {filepath}: {e}")

        # Sessions nach Datum (neueste zuerst) sortieren
        sessions.sort(key=lambda x: parse_training_timestamp(x["timestamp"])) #, reverse=True (Soll in die klammer wenn man es braucht

        return sessions
