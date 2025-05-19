import time

class RPMCalculator:
    def __init__(self):
        self.last_round_time = None  # Zeitpunkt der letzten Umdrehung
        self.rpm = 0  # Aktuelle Kadenz (RPM)
        self.min_time_difference = 0.5  # Mindestzeitdifferenz in Sekunden (0.5 sekunden = 120 RPM )

    def increment_rounds(self):
        current_time = time.perf_counter()  # Aktueller Zeitpunkt

        if self.last_round_time is not None:
            # Berechne die Zeitdifferenz zur letzten Umdrehung
            time_difference = current_time - self.last_round_time

            if time_difference > 0:
                if time_difference >= self.min_time_difference:
                    self.rpm = 60 / time_difference
                    #print(f"✅ Valide: time_difference = {time_difference:.3f}, rpm = {self.rpm:.1f}")
                else:
                    print(f"⚠️ Ignoriert: time_difference zu kurz ({time_difference:.3f}s)")

        # Aktualisiere den Zeitpunkt der letzten Umdrehung
        self.last_round_time = current_time

    def get_rpm(self):
        return round(self.rpm)  # Gibt die Kadenz mit 0 Dezimalstellen zurück

