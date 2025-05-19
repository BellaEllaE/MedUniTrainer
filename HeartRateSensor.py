from openant.easy.node import Node
from openant.devices import ANTPLUS_NETWORK_KEY
from openant.devices.heart_rate import HeartRate, HeartRateData

import threading


class HeartRateSensor:
    def __init__(self):
        self.current_heart_rate = 0
        self.node = Node()
        self.node.set_network_key(0x00, ANTPLUS_NETWORK_KEY)
        self.device = HeartRate(self.node, device_id=0)

        # Set up callbacks
        self.device.on_found = self._on_found
        self.device.on_device_data = self._on_device_data

        # Start the node in a separate thread
        self.thread = threading.Thread(target=self._run_node)
        self.thread.daemon = True
        self.thread.start()

    def _on_found(self):
        print(f"Heart rate device found and receiving")

    def _on_device_data(self, page: int, page_name: str, data):
        if isinstance(data, HeartRateData):
            self.current_heart_rate = data.heart_rate

    def _run_node(self):
        try:
            self.node.start()
        except Exception as e:
            print(f"Error in heart rate sensor: {e}")

    def get_heart_rate(self):
        return self.current_heart_rate

    def stop(self):
        try:
            self.device.close_channel()
            self.node.stop()
        except:
            pass
