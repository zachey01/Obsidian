import ctypes

user32 = ctypes.WinDLL("user32")

class OBSBypass:
    def __init__(self):
        self.stream_proof_enabled = False

    def enable_stream_proof(self, window_handle):
        if window_handle and self.stream_proof_enabled:
            user32.SetWindowDisplayAffinity(window_handle, 0x00000011)

    def disable_stream_proof(self, window_handle):
        if window_handle:
            user32.SetWindowDisplayAffinity(window_handle, 0x00000000)

    def toggle_stream_proof(self, window_handle, enable):
        self.stream_proof_enabled = enable
        if enable:
            self.enable_stream_proof(window_handle)
        else:
            self.disable_stream_proof(window_handle)
