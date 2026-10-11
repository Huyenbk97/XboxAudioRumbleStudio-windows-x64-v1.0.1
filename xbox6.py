import ctypes
import json
import math
import queue
import threading
import time
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from tkinter import colorchooser, filedialog, messagebox, scrolledtext, ttk
import tkinter as tk
from ctypes import wintypes

import numpy as np
import pyaudiowpatch as pyaudio
import proctap
from PIL import Image
import pystray
import psutil
import win32gui
import win32process



APP_TITLE = "Xbox Audio Rumble Studio - Chuẩn Haptic DualSense & LED Apex"
APP_PATH = Path(sys.executable if getattr(sys, "frozen", False) else __file__)
CONFIG_FILE = APP_PATH.with_suffix(".settings.json")
XINPUT_SUCCESS = 0
XINPUT_ERROR_DEVICE_NOT_CONNECTED = 1167


class XInputGamepad(ctypes.Structure):
    _fields_ = [
        ("wButtons", wintypes.WORD),
        ("bLeftTrigger", ctypes.c_ubyte),
        ("bRightTrigger", ctypes.c_ubyte),
        ("sThumbLX", ctypes.c_short),
        ("sThumbLY", ctypes.c_short),
        ("sThumbRX", ctypes.c_short),
        ("sThumbRY", ctypes.c_short),
    ]


class XInputState(ctypes.Structure):
    _fields_ = [
        ("dwPacketNumber", wintypes.DWORD),
        ("Gamepad", XInputGamepad),
    ]


class XInputVibration(ctypes.Structure):
    _fields_ = [
        ("wLeftMotorSpeed", wintypes.WORD),
        ("wRightMotorSpeed", wintypes.WORD),
    ]


try:
    xinput = ctypes.WinDLL("xinput1_4")
except OSError:
    xinput = ctypes.WinDLL("xinput9_1_0")

XInputSetState = xinput.XInputSetState
XInputSetState.argtypes = [wintypes.DWORD, ctypes.POINTER(XInputVibration)]
XInputSetState.restype = wintypes.DWORD

XInputGetState = xinput.XInputGetState
XInputGetState.argtypes = [wintypes.DWORD, ctypes.POINTER(XInputState)]
XInputGetState.restype = wintypes.DWORD

XINPUT_GAMEPAD_LEFT_SHOULDER = 0x0100
XINPUT_GAMEPAD_RIGHT_SHOULDER = 0x0200


PRESETS = {
    "✨ Chuẩn Xúc Giác Haptic DualSense": {
        "dual_motor_mode": True,
        "vocal_only_mode": False,
        "adaptive_threshold": True,
        "stereo_panning": True,
        "overdrive_boost": 0.80,
        "intensity": 0.85,
        "rhythm_punch": 0.70,
        "texture_amount": 0.65,
        "vibration_threshold": 190.0,
        "map_in_max": 4600.0,
        "gamma_correction": 1.10,
        "attack_rate": 0.70,
        "release_rate": 0.30,
        "dead_zone": 0.025,
        "vocal_low": 350,
        "vocal_high": 5500,
        "bass_high": 380,
    },
    "🎮 Game Bắn Súng (FPS - Sắc Bén)": {
        "dual_motor_mode": True,
        "vocal_only_mode": False,
        "adaptive_threshold": True,
        "stereo_panning": True,
        "overdrive_boost": 0.90,
        "intensity": 0.88,
        "rhythm_punch": 0.80,
        "texture_amount": 0.50,
        "vibration_threshold": 210.0,
        "map_in_max": 4800.0,
        "gamma_correction": 1.00,
        "attack_rate": 0.85,
        "release_rate": 0.35,
        "dead_zone": 0.03,
        "vocal_low": 400,
        "vocal_high": 6500,
        "bass_high": 380,
    },
    "🏎️ Game Đua Xe (Racing - Tốc Độ)": {
        "dual_motor_mode": True,
        "vocal_only_mode": False,
        "adaptive_threshold": True,
        "stereo_panning": True,
        "overdrive_boost": 0.60,
        "intensity": 0.85,
        "rhythm_punch": 0.65,
        "texture_amount": 0.70,
        "vibration_threshold": 170.0,
        "map_in_max": 5200.0,
        "gamma_correction": 0.95,
        "attack_rate": 0.55,
        "release_rate": 0.20,
        "dead_zone": 0.035,
        "vocal_low": 300,
        "vocal_high": 5000,
        "bass_high": 420,
    },
    "⚔️ Game Nhập Vai & Hành Động (RPG)": {
        "dual_motor_mode": True,
        "vocal_only_mode": False,
        "adaptive_threshold": True,
        "stereo_panning": True,
        "overdrive_boost": 0.75,
        "intensity": 0.82,
        "rhythm_punch": 0.75,
        "texture_amount": 0.60,
        "vibration_threshold": 200.0,
        "map_in_max": 5000.0,
        "gamma_correction": 1.05,
        "attack_rate": 0.65,
        "release_rate": 0.25,
        "dead_zone": 0.035,
        "vocal_low": 350,
        "vocal_high": 5500,
        "bass_high": 380,
    },
    "🎵 Âm Nhạc Sôi Động (EDM/Rock)": {
        "dual_motor_mode": True,
        "vocal_only_mode": False,
        "adaptive_threshold": True,
        "stereo_panning": False,
        "overdrive_boost": 0.45,
        "intensity": 0.86,
        "rhythm_punch": 0.85,
        "texture_amount": 0.45,
        "vibration_threshold": 220.0,
        "map_in_max": 5400.0,
        "gamma_correction": 1.00,
        "attack_rate": 0.60,
        "release_rate": 0.18,
        "dead_zone": 0.04,
        "vocal_low": 500,
        "vocal_high": 4500,
        "bass_high": 550,
    },
    "🎙️ ASMR & Giọng Nói Thì Thầm": {
        "dual_motor_mode": False,
        "vocal_only_mode": True,
        "adaptive_threshold": True,
        "stereo_panning": False,
        "overdrive_boost": 0.10,
        "intensity": 0.52,
        "rhythm_punch": 0.15,
        "texture_amount": 0.85,
        "vibration_threshold": 80.0,
        "map_in_max": 2400.0,
        "gamma_correction": 1.65,
        "attack_rate": 0.22,
        "release_rate": 0.05,
        "dead_zone": 0.015,
        "vocal_low": 450,
        "vocal_high": 3800,
        "bass_high": 300,
    },
    "🎬 Phim Điện Ảnh & Bom Tấn": {
        "dual_motor_mode": True,
        "vocal_only_mode": False,
        "adaptive_threshold": True,
        "stereo_panning": True,
        "overdrive_boost": 0.75,
        "intensity": 0.90,
        "rhythm_punch": 0.70,
        "texture_amount": 0.55,
        "vibration_threshold": 210.0,
        "map_in_max": 5600.0,
        "gamma_correction": 1.05,
        "attack_rate": 0.58,
        "release_rate": 0.22,
        "dead_zone": 0.035,
        "vocal_low": 350,
        "vocal_high": 4800,
        "bass_high": 500,
    },
}

# Tương thích ngược với preset cũ
PRESETS["Âm trầm đắm chìm"] = PRESETS["🏎️ Game Đua Xe (Racing - Tốc Độ)"]
PRESETS["Giọng hát rõ ràng"] = PRESETS["🎙️ ASMR & Giọng Nói Thì Thầm"]
PRESETS["Toàn dải uy lực"] = PRESETS["✨ Chuẩn Xúc Giác Haptic DualSense"]
PRESETS["Nhẹ nhàng tinh tế"] = PRESETS["🎙️ ASMR & Giọng Nói Thì Thầm"]
PRESETS["人声清晰"] = PRESETS["Giọng hát rõ ràng"]
PRESETS["低频沉浸"] = PRESETS["Âm trầm đắm chìm"]
PRESETS["轻柔细腻"] = PRESETS["Nhẹ nhàng tinh tế"]
PRESETS["全频强劲"] = PRESETS["Toàn dải uy lực"]


def hex_to_rgb(hex_str):
    hex_clean = hex_str.strip().lstrip("#")
    if len(hex_clean) == 6:
        try:
            return (
                int(hex_clean[0:2], 16),
                int(hex_clean[2:4], 16),
                int(hex_clean[4:6], 16),
            )
        except ValueError:
            pass
    return (0, 180, 255)


def rgb_to_hex(r, g, b):
    return f"#{int(clamp(r, 0, 255)):02x}{int(clamp(g, 0, 255)):02x}{int(clamp(b, 0, 255)):02x}"


FLYDIGI_VIDS = ("04b4", "37d7", "2fd8", "0483")
FLYDIGI_VENDOR_USAGE_PAGES = (0xFFA0, 0xFF00, 0xFF12, 0xFF68)


class FlydigiApexController:
    """Điều khiển trực tiếp phần cứng đèn LED của dòng tay cầm Flydigi Apex (Apex 2, 3, 4, 5) và Vader (Vader 3, 4 Pro)."""

    def __init__(self):
        self.handle = None
        self.device_path = None
        self.is_connected = False
        self.last_color = None
        self.last_send_time = 0.0
        self.last_scan_time = 0.0
        self.report_length = 32
        self.lock = threading.Lock()
        self.kernel32 = ctypes.WinDLL("kernel32")
        self.hid = ctypes.WinDLL("hid")
        self.setupapi = ctypes.WinDLL("setupapi")
        self.connect()

    def connect(self):
        with self.lock:
            now = time.monotonic()
            self.last_scan_time = now

            if self.handle:
                try:
                    self.kernel32.CloseHandle(self.handle)
                except Exception:
                    pass
                self.handle = None
                self.is_connected = False

            class GUID(ctypes.Structure):
                _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD), ("Data3", wintypes.WORD), ("Data4", ctypes.c_ubyte * 8)]

            class HIDP_CAPS(ctypes.Structure):
                _fields_ = [
                    ("Usage", wintypes.WORD), ("UsagePage", wintypes.WORD),
                    ("InputReportByteLength", wintypes.WORD), ("OutputReportByteLength", wintypes.WORD), ("FeatureReportByteLength", wintypes.WORD),
                    ("Reserved", wintypes.WORD * 17),
                    ("NumberLinkCollectionNodes", wintypes.WORD), ("NumberInputButtonCaps", wintypes.WORD), ("NumberInputValueCaps", wintypes.WORD),
                    ("NumberInputDataIndices", wintypes.WORD), ("NumberOutputButtonCaps", wintypes.WORD), ("NumberOutputValueCaps", wintypes.WORD),
                    ("NumberOutputDataIndices", wintypes.WORD), ("NumberFeatureButtonCaps", wintypes.WORD), ("NumberFeatureValueCaps", wintypes.WORD),
                    ("NumberFeatureDataIndices", wintypes.WORD)
                ]

            hid_guid = GUID()
            self.hid.HidD_GetHidGuid(ctypes.byref(hid_guid))
            hdevinfo = self.setupapi.SetupDiGetClassDevsW(ctypes.byref(hid_guid), None, None, 0x12)

            class SP_DEVICE_INTERFACE_DATA(ctypes.Structure):
                _fields_ = [("cbSize", wintypes.DWORD), ("InterfaceClassGuid", GUID), ("Flags", wintypes.DWORD), ("Reserved", ctypes.c_void_p)]

            class SP_DEVICE_INTERFACE_DETAIL_DATA_W(ctypes.Structure):
                _fields_ = [("cbSize", wintypes.DWORD), ("DevicePath", ctypes.c_wchar * 512)]

            ifda = SP_DEVICE_INTERFACE_DATA()
            ifda.cbSize = ctypes.sizeof(ifda)
            index = 0
            candidate_handles = []

            while self.setupapi.SetupDiEnumDeviceInterfaces(hdevinfo, None, ctypes.byref(hid_guid), index, ctypes.byref(ifda)):
                detail = SP_DEVICE_INTERFACE_DETAIL_DATA_W()
                detail.cbSize = 8 if ctypes.sizeof(ctypes.c_void_p) == 8 else 5
                req = wintypes.DWORD()
                if self.setupapi.SetupDiGetDeviceInterfaceDetailW(hdevinfo, ctypes.byref(ifda), ctypes.byref(detail), ctypes.sizeof(detail), ctypes.byref(req), None):
                    p = detail.DevicePath.lower()
                    if any(vid in p for vid in FLYDIGI_VIDS):
                        # Thử mở quyền đọc/ghi chia sẻ (0xC0000000), nếu bị khóa chia sẻ thì thử quyền chỉ ghi (0x40000000)
                        h = self.kernel32.CreateFileW(detail.DevicePath, 0xC0000000, 3, None, 3, 0, None)
                        if h == -1 or h == 0xFFFFFFFFFFFFFFFF:
                            h = self.kernel32.CreateFileW(detail.DevicePath, 0x40000000, 3, None, 3, 0, None)

                        if h != -1 and h != 0xFFFFFFFFFFFFFFFF:
                            preparsed = ctypes.c_void_p()
                            self.hid.HidD_GetPreparsedData(h, ctypes.byref(preparsed))
                            caps = HIDP_CAPS()
                            self.hid.HidP_GetCaps(preparsed, ctypes.byref(caps))
                            self.hid.HidD_FreePreparsedData(preparsed)

                            is_vendor_page = (caps.UsagePage in FLYDIGI_VENDOR_USAGE_PAGES) or (caps.UsagePage >= 0xFF00)
                            out_len = caps.OutputReportByteLength

                            if is_vendor_page:
                                self.handle = h
                                self.device_path = detail.DevicePath
                                self.report_length = out_len if out_len > 0 else 32
                                self.is_connected = True
                                break
                            elif out_len >= 32:
                                candidate_handles.append((h, detail.DevicePath, out_len))
                            else:
                                self.kernel32.CloseHandle(h)
                index += 1
            self.setupapi.SetupDiDestroyDeviceInfoList(hdevinfo)

            # Nếu chưa có interface vendor chính xác, thử interface dự phòng có output report >= 32
            if not self.is_connected and candidate_handles:
                h, dev_path, out_len = candidate_handles[0]
                self.handle = h
                self.device_path = dev_path
                self.report_length = out_len if out_len > 0 else 32
                self.is_connected = True
                for other_h, _, _ in candidate_handles[1:]:
                    try:
                        self.kernel32.CloseHandle(other_h)
                    except Exception:
                        pass

            return self.is_connected

    def set_led(self, r, g, b, brightness=1.0):
        with self.lock:
            now = time.monotonic()
            if not self.is_connected or not self.handle:
                # Quét lại ngầm tối đa 1 lần mỗi 1.5 giây để tránh giật lag luồng âm thanh
                if (now - self.last_scan_time) < 1.5:
                    return False
                if not self.connect():
                    return False

            r_val = max(0, min(255, int(r * brightness)))
            g_val = max(0, min(255, int(g * brightness)))
            b_val = max(0, min(255, int(b * brightness)))
            current = (r_val, g_val, b_val)
            if self.last_color == current and (now - self.last_send_time) < 0.25:
                return True
            if (now - self.last_send_time) < 0.030:
                return True

            cmd = [0x5A, 0xA5, 0xF5, 0x05, r_val, g_val, b_val]
            checksum = sum(cmd[2:]) & 0xFF
            cmd.append(checksum)
            
            # Gói tin Output Report với Report ID 0x03
            target_len = max(32, self.report_length)
            report = bytes([0x03]) + bytes(cmd).ljust(target_len - 1, b"\x00")
            
            success = False
            # 1. Thử gửi trực tiếp qua WriteFile
            written = wintypes.DWORD()
            res = self.kernel32.WriteFile(self.handle, report, len(report), ctypes.byref(written), None)
            if res and written.value > 0:
                success = True
            else:
                # 2. Dự phòng: Dùng HidD_SetOutputReport nếu WriteFile bị Windows chặn
                try:
                    res_hid = self.hid.HidD_SetOutputReport(self.handle, report, len(report))
                    if res_hid:
                        success = True
                    else:
                        # 3. Dự phòng 2: Thử HidD_SetFeature
                        res_feat = self.hid.HidD_SetFeature(self.handle, report, len(report))
                        if res_feat:
                            success = True
                except Exception:
                    pass

            if not success:
                self.is_connected = False
                return False

            self.last_color = current
            self.last_send_time = now
            return True

    def set_triggers(self, left_force: float, right_force: float, mode: int = 1) -> bool:
        """Gửi gói tin cấu hình rung phản hồi xúc giác cho 2 nút cò Flydigi Apex 3/4 & Vader 3/4 Pro."""
        with self.lock:
            now = time.monotonic()
            if not self.is_connected or not self.handle:
                if (now - self.last_scan_time) < 1.5:
                    return False
                if not self.connect():
                    return False

            lf = int(clamp(left_force) * 255)
            rf = int(clamp(right_force) * 255)

            cmd = [0x5A, 0xA5, 0xF6, 0x06, mode, lf, mode, rf]
            checksum = sum(cmd[2:]) & 0xFF
            cmd.append(checksum)

            target_len = max(32, self.report_length)
            report = bytes([0x03]) + bytes(cmd).ljust(target_len - 1, b"\x00")

            written = wintypes.DWORD()
            res = self.kernel32.WriteFile(self.handle, report, len(report), ctypes.byref(written), None)
            if res and written.value > 0:
                return True
            try:
                if self.hid.HidD_SetOutputReport(self.handle, report, len(report)):
                    return True
            except Exception:
                pass
            return False

    def close(self):
        with self.lock:
            if self.handle:
                try:
                    self.kernel32.CloseHandle(self.handle)
                except Exception:
                    pass
                self.handle = None
                self.is_connected = False


FlydigiController = FlydigiApexController


@dataclass
class RuntimeStats:
    total_rms: float = 0.0
    vocal_rms: float = 0.0
    bass_rms: float = 0.0
    crisp_rms: float = 0.0
    left_output: float = 0.0
    right_output: float = 0.0
    noise_floor: float = 0.0
    effective_threshold: float = 0.0
    device_name: str = "Đang khởi tạo..."
    controller_connected: bool = False
    peak_left: float = 0.0
    peak_right: float = 0.0
    detected_mode: str = "Đang nhận diện"
    beat_strength: float = 0.0
    texture_level: float = 0.0
    overdrive_kick: float = 0.0
    stereo_pan: float = 0.0
    apex_connected: bool = False
    current_led_hex: str = "#00b4d8"
    peak_left_trigger: float = 0.0
    peak_right_trigger: float = 0.0
    trigger_haptics_active: bool = False


@dataclass
class SharedVibrationParams:
    lock: threading.Lock = field(default_factory=threading.Lock, repr=False, compare=False)
    enabled: bool = True
    controller_index: int = 0
    auto_profile: bool = True
    stereo_panning: bool = True
    overdrive_boost: float = 0.80
    rhythm_punch: float = 0.70
    texture_amount: float = 0.65
    dual_motor_mode: bool = True
    vocal_only_mode: bool = False
    adaptive_threshold: bool = True
    auto_calibrating: bool = False
    intensity: float = 0.85
    vibration_threshold: float = 190.0
    dead_zone: float = 0.025
    attack_rate: float = 0.70
    release_rate: float = 0.30
    map_in_max: float = 4600.0
    gamma_correction: float = 1.10
    vocal_low: int = 350
    vocal_high: int = 5500
    bass_high: int = 380

    # Cài đặt LED Apex
    apex_led_enabled: bool = True
    apex_led_mode: str = "Đồng bộ âm thanh"
    apex_reactive_type: str = "Tần số âm thanh (Xanh->Tím->Đỏ)"
    apex_static_color: str = "#00b4d8"
    apex_brightness: float = 1.0

    # Cài đặt Khay Hệ Thống & Tự Động Nhận Diện Game
    minimize_to_tray: bool = True
    auto_game_detect: bool = True
    fallback_preset: str = "✨ Chuẩn Xúc Giác Haptic DualSense"
    game_profiles: dict = field(
        default_factory=lambda: {
            "cs2.exe": "🎮 Game Bắn Súng (FPS - Sắc Bén)",
            "valorant-win64-shipping.exe": "🎮 Game Bắn Súng (FPS - Sắc Bén)",
            "forzahorizon5.exe": "🏎️ Game Đua Xe (Racing - Tốc Độ)",
            "eldenring.exe": "⚔️ Game Nhập Vai & Hành Động (RPG)",
            "blackmythwukong.exe": "⚔️ Game Nhập Vai & Hành Động (RPG)",
            "spotify.exe": "🎵 Âm Nhạc Sôi Động (EDM/Rock)",
        }
    )

    # Cài đặt Nguồn Thu Âm Thanh & Cô Lập Tiến Trình (Phase 2)
    audio_capture_mode: str = "auto_game_process"
    auto_process_fallback: bool = True
    current_game_pid: int = 0

    # Cài đặt Rung Độc Lập 2 Nút Cò LT/RT - Xbox Impulse & Flydigi Triggers (Phase 3)
    trigger_haptics_enabled: bool = True
    trigger_left_gain: float = 0.70
    trigger_right_gain: float = 0.85
    trigger_mode: str = "adaptive_gun_brake"
    trigger_threshold: float = 0.04

    stats: RuntimeStats = field(default_factory=RuntimeStats)

    def snapshot(self):
        with self.lock:
            return {
                "enabled": self.enabled,
                "controller_index": self.controller_index,
                "auto_profile": self.auto_profile,
                "stereo_panning": self.stereo_panning,
                "overdrive_boost": self.overdrive_boost,
                "rhythm_punch": self.rhythm_punch,
                "texture_amount": self.texture_amount,
                "dual_motor_mode": self.dual_motor_mode,
                "vocal_only_mode": self.vocal_only_mode,
                "adaptive_threshold": self.adaptive_threshold,
                "auto_calibrating": self.auto_calibrating,
                "intensity": self.intensity,
                "vibration_threshold": self.vibration_threshold,
                "dead_zone": self.dead_zone,
                "attack_rate": self.attack_rate,
                "release_rate": self.release_rate,
                "map_in_max": self.map_in_max,
                "gamma_correction": self.gamma_correction,
                "vocal_low": self.vocal_low,
                "vocal_high": self.vocal_high,
                "bass_high": self.bass_high,
                "apex_led_enabled": self.apex_led_enabled,
                "apex_led_mode": self.apex_led_mode,
                "apex_reactive_type": self.apex_reactive_type,
                "apex_static_color": self.apex_static_color,
                "apex_brightness": self.apex_brightness,
                "minimize_to_tray": self.minimize_to_tray,
                "auto_game_detect": self.auto_game_detect,
                "fallback_preset": self.fallback_preset,
                "game_profiles": dict(self.game_profiles),
                "audio_capture_mode": self.audio_capture_mode,
                "auto_process_fallback": self.auto_process_fallback,
                "current_game_pid": self.current_game_pid,
                "trigger_haptics_enabled": self.trigger_haptics_enabled,
                "trigger_left_gain": self.trigger_left_gain,
                "trigger_right_gain": self.trigger_right_gain,
                "trigger_mode": self.trigger_mode,
                "trigger_threshold": self.trigger_threshold,
                "stats": asdict(self.stats),
            }

    def apply(self, values):
        with self.lock:
            for key, value in values.items():
                if hasattr(self, key) and key not in {"lock", "stats"}:
                    setattr(self, key, value)


def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def set_vibration(user_index, left_motor, right_motor):
    vibration = XInputVibration(
        int(clamp(left_motor) * 65535),
        int(clamp(right_motor) * 65535),
    )
    return XInputSetState(int(user_index), ctypes.byref(vibration))


class Unified4ChannelDispatcher:
    """Điều khiển 4 kênh rung độc lập: 2 mô tơ thân (Left/Right Grip) + 2 mô tơ cò (Left/Right Trigger)

    Sử dụng Windows.Gaming.Input (WinRT) cho tay cầm Xbox One/Series X|S/Elite,
    và tự động hòa trộn dự phòng (Graceful Blend) sang XInput cho tay cầm 2 mô tơ thông thường.
    """
    def __init__(self):
        self.wgi = None
        self.wgi_available = False
        try:
            import winrt.windows.gaming.input as wgi
            import winrt.windows.foundation.collections  # Cần cho IVectorView duyệt Gamepad.gamepads
            self.wgi = wgi
            self.wgi_available = True
        except Exception:
            self.wgi = None
            self.wgi_available = False
        self._last_gamepads = []
        self._last_scan_time = 0.0

    def get_wgi_gamepad(self, index: int):
        if not self.wgi_available or not self.wgi:
            return None
        now = time.monotonic()
        if (now - self._last_scan_time) > 1.0 or not self._last_gamepads:
            try:
                self._last_gamepads = list(self.wgi.Gamepad.gamepads)
                self._last_scan_time = now
            except Exception:
                self._last_gamepads = []
        if 0 <= index < len(self._last_gamepads):
            return self._last_gamepads[index]
        return None

    def set_vibration_4ch(self, user_index: int, left_grip: float, right_grip: float, left_trigger: float = 0.0, right_trigger: float = 0.0) -> bool:
        lg = clamp(left_grip)
        rg = clamp(right_grip)
        lt = clamp(left_trigger)
        rt = clamp(right_trigger)

        gp = self.get_wgi_gamepad(int(user_index))
        if gp:
            try:
                vib = self.wgi.GamepadVibration(
                    left_motor=float(lg),
                    right_motor=float(rg),
                    left_trigger=float(lt),
                    right_trigger=float(rt),
                )
                gp.vibration = vib
                return True
            except Exception:
                pass

        # Fallback sang XInput: Hòa trộn lực cò vào 2 mô tơ thân
        blended_left = clamp(lg + lt * 0.4)
        blended_right = clamp(rg + rt * 0.4)
        set_vibration(user_index, blended_left, blended_right)
        return False

    def stop_all(self):
        try:
            if self.wgi_available and self._last_gamepads:
                zero_vib = self.wgi.GamepadVibration(0.0, 0.0, 0.0, 0.0)
                for gp in self._last_gamepads:
                    try:
                        gp.vibration = zero_vib
                    except Exception:
                        pass
        except Exception:
            pass
        for i in range(4):
            set_vibration(i, 0.0, 0.0)


def is_controller_connected(index):
    state = XInputState()
    return XInputGetState(int(index), ctypes.byref(state)) == XINPUT_SUCCESS


def smooth_signal(current, target, attack, release):
    rate = attack if target > current else release
    return current + (target - current) * clamp(rate)


def map_value_gamma(value, threshold, in_max, gamma):
    if value <= threshold:
        return 0.0
    span = max(1.0, in_max - threshold)
    normalized = clamp((value - threshold) / span)
    return normalized ** max(0.1, gamma)


def band_rms(fft_data, freqs, low, high, n):
    mask = (freqs >= low) & (freqs <= high)
    if not np.any(mask):
        return 0.0
    band_fft = np.zeros_like(fft_data)
    band_fft[mask] = fft_data[mask]
    return float(np.sqrt(np.mean(np.square(np.fft.irfft(band_fft, n=n))) + 1e-10))


def classify_content(total_rms, vocal_rms, bass_rms, crisp_rms, transient, previous_mode):
    if total_rms < 50:
        return "Yên tĩnh"

    total = max(total_rms, 1.0)
    bass_ratio = bass_rms / total
    vocal_ratio = vocal_rms / total
    crisp_ratio = crisp_rms / total

    game_score = transient * 2.2 + crisp_ratio * 1.5 + bass_ratio * 1.2
    music_score = bass_ratio * 1.4 + transient * 1.1 + vocal_ratio * 0.4
    asmr_score = vocal_ratio * 1.6 + (1.0 - min(transient * 2.5, 1.0)) * 0.7 - bass_ratio * 0.6

    if previous_mode == "Game Haptic":
        game_score += 0.15
    elif previous_mode in {"Nhạc", "音乐"}:
        music_score += 0.12
    elif previous_mode == "ASMR":
        asmr_score += 0.12

    if game_score > music_score + 0.25 and game_score > asmr_score + 0.25:
        return "Game Haptic"
    if music_score > asmr_score + 0.15:
        return "Nhạc"
    if asmr_score > music_score + 0.10:
        return "ASMR"
    return previous_mode if previous_mode in {"Game Haptic", "Nhạc", "ASMR"} else "Game Haptic"


def calculate_trigger_haptics(bands: dict, mode: str = "adaptive_gun_brake", gain_l: float = 0.70, gain_r: float = 0.85, threshold: float = 0.04) -> tuple[float, float]:
    """Tính toán độ rung haptic cho 2 nút cò LT và RT dựa trên phổ âm thanh."""
    punch_r = bands.get("punch_r", 0.0)
    highmid_r = bands.get("highmid_r", 0.0)
    lowmid_l = bands.get("lowmid_l", 0.0)
    sub_l = bands.get("sub_l", 0.0)
    pan = bands.get("stereo_pan", 0.0)
    total = bands.get("total_rms", 0.0)

    if mode == "directional_stereo":
        base_l = (lowmid_l + sub_l) * 0.5
        base_r = (punch_r + highmid_r) * 0.5
        if pan < -0.1:
            lt_raw = base_l * (1.0 + abs(pan) * 0.5)
            rt_raw = base_r * max(0.1, 1.0 - abs(pan) * 0.7)
        elif pan > 0.1:
            rt_raw = base_r * (1.0 + abs(pan) * 0.5)
            lt_raw = base_l * max(0.1, 1.0 - abs(pan) * 0.7)
        else:
            lt_raw = base_l
            rt_raw = base_r
    elif mode == "linked_body":
        lt_raw = rt_raw = total
    else:
        # Mặc định: adaptive_gun_brake (RT Bắn súng / LT Phanh & Ngắm)
        rt_raw = 0.6 * punch_r + 0.4 * highmid_r
        lt_raw = 0.5 * lowmid_l + 0.5 * sub_l

    rt_val = 0.0 if rt_raw < threshold else clamp((rt_raw - threshold) / max(1e-5, 1.0 - threshold)) * gain_r
    lt_val = 0.0 if lt_raw < threshold else clamp((lt_raw - threshold) / max(1e-5, 1.0 - threshold)) * gain_l

    return clamp(lt_val), clamp(rt_val)


def find_loopback_device(audio, log_queue):
    loopback_devices = []
    for i in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(i)
        if info.get("isLoopbackDevice", False):
            loopback_devices.append(info)

    try:
        wasapi_info = audio.get_host_api_info_by_type(pyaudio.paWASAPI)
        default_speakers = audio.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
        for dev in loopback_devices:
            if dev["name"].startswith(default_speakers["name"]):
                return dev
    except Exception as exc:
        log_queue.put(f"Lỗi khi tìm thiết bị loopback mặc định: {exc}")

    if loopback_devices:
        return loopback_devices[0]

    for i in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(i)
        if info.get("maxInputChannels", 0) > 0:
            return info
    return None


def audio_vibration_thread(shared, log_queue, stop_event):
    audio = pyaudio.PyAudio()
    stream = None
    chunk = 1024

    left_vib = 0.0
    right_vib = 0.0
    left_trigger_vib = 0.0
    right_trigger_vib = 0.0
    prev_target_left = 0.0
    prev_target_right = 0.0
    energy_avg = 100.0
    transient_avg = 0.0
    noise_floor = 40.0
    calibration_until = 0.0
    last_hotkey_pressed = False
    detected_mode = "Game Haptic"
    dispatcher = Unified4ChannelDispatcher()

    apex_ctrl = FlydigiApexController()
    last_apex_state = apex_ctrl.is_connected
    if apex_ctrl.is_connected:
        log_queue.put("🟢 Đã phát hiện và kết nối thành công tay cầm Flydigi Apex (Hỗ trợ LED RGB)")
    else:
        log_queue.put("⚪ Đang quét tìm tay cầm Flydigi Apex / Dongle USB...")

    try:
        loopback_device = find_loopback_device(audio, log_queue)
        if not loopback_device:
            log_queue.put("Không tìm thấy thiết bị âm thanh phù hợp để thu âm.")
            return

        channels = int(loopback_device["maxInputChannels"])
        rate = int(loopback_device["defaultSampleRate"])
        with shared.lock:
            shared.stats.device_name = loopback_device["name"]
            shared.stats.effective_threshold = shared.vibration_threshold

        stream = audio.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=rate,
            input=True,
            input_device_index=loopback_device["index"],
            frames_per_buffer=chunk,
        )
        log_queue.put(f"Đã bắt đầu thu âm: {loopback_device['name']} / {rate} Hz / {channels} kênh (Haptic Ready)")

        active_proc_cap = None
        active_cap_pid = 0
        active_audio_source_desc = loopback_device["name"]

        while not stop_event.is_set():
            snap = shared.snapshot()
            controller_index = snap["controller_index"]
            state = XInputState()
            connected = XInputGetState(controller_index, ctypes.byref(state)) == XINPUT_SUCCESS

            if connected:
                hotkey_pressed = bool(
                    state.Gamepad.wButtons & XINPUT_GAMEPAD_LEFT_SHOULDER
                    and state.Gamepad.wButtons & XINPUT_GAMEPAD_RIGHT_SHOULDER
                )
                if hotkey_pressed and not last_hotkey_pressed:
                    with shared.lock:
                        shared.enabled = not shared.enabled
                        snap["enabled"] = shared.enabled
                    log_queue.put(f"Phím tắt tay cầm LB+RB: Độ rung {'BẬT' if snap['enabled'] else 'TẠM DỪNG'}")
                last_hotkey_pressed = hotkey_pressed
            else:
                last_hotkey_pressed = False

            if snap["auto_calibrating"] and calibration_until == 0:
                calibration_until = time.monotonic() + 3.0
                noise_floor = 0.0
                log_queue.put("Bắt đầu tự động hiệu chuẩn: Vui lòng giữ âm lượng nền ổn định trong 3 giây.")

            # Quản lý Hybrid Stream: Process Loopback (proctap) vs System Loopback (PyAudioWPatch)
            req_mode = snap.get("audio_capture_mode", "auto_game_process")
            target_pid = snap.get("current_game_pid", 0)

            raw_samples = None
            using_proc_loopback = False

            if req_mode == "auto_game_process" and target_pid > 0:
                if active_cap_pid != target_pid:
                    if active_proc_cap is not None:
                        try:
                            active_proc_cap.stop()
                        except Exception:
                            pass
                        active_proc_cap = None
                    try:
                        active_proc_cap = proctap.ProcessAudioCapture(target_pid)
                        active_proc_cap.start()
                        active_cap_pid = target_pid
                        log_queue.put(f"🎯 Bắt đầu cô lập âm thanh cho Game (PID {target_pid})")
                    except Exception as exc:
                        log_queue.put(f"Chưa thể kết nối âm thanh PID {target_pid}: {exc}. Dùng âm thanh hệ thống.")
                        active_proc_cap = None
                        active_cap_pid = 0

                if active_proc_cap is not None and active_proc_cap.is_running:
                    try:
                        raw_proc = active_proc_cap.read(timeout=0.012)
                        if raw_proc is not None and len(raw_proc) > 0:
                            raw_samples = np.frombuffer(raw_proc, dtype=np.float32) * 32767.0
                            using_proc_loopback = True
                    except Exception:
                        pass
            else:
                if active_proc_cap is not None:
                    try:
                        active_proc_cap.stop()
                    except Exception:
                        pass
                    active_proc_cap = None
                    active_cap_pid = 0

            # Fallback về System Loopback nếu chưa có dữ liệu từ Process Capture
            if raw_samples is None:
                try:
                    raw = stream.read(chunk, exception_on_overflow=False)
                    raw_samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
                except Exception as exc:
                    log_queue.put(f"Lỗi đọc luồng âm thanh, đang thử lại: {exc}")
                    time.sleep(0.05)
                    continue

            # Cập nhật mô tả nguồn âm thanh
            if using_proc_loopback:
                active_audio_source_desc = f"🎯 Đang cô lập Game (PID {active_cap_pid})"
            elif req_mode == "auto_game_process" and target_pid > 0:
                active_audio_source_desc = f"🔄 Chờ âm thanh PID {target_pid} (Tạm dùng Hệ thống)"
            else:
                active_audio_source_desc = f"🔊 Toàn hệ thống: {loopback_device['name']}"

            # Xử lý Stereo không gian
            stereo_pan = 0.0
            if channels >= 2:
                samples_2d = raw_samples.reshape(-1, channels)
                ch_left = samples_2d[:, 0]
                ch_right = samples_2d[:, 1]
                samples_mono = (ch_left + ch_right) * 0.5

                rms_l = float(np.sqrt(np.mean(np.square(ch_left)) + 1e-10))
                rms_r = float(np.sqrt(np.mean(np.square(ch_right)) + 1e-10))
                total_stereo = rms_l + rms_r
                if total_stereo > 35.0:
                    stereo_pan = float(np.clip((rms_r - rms_l) / total_stereo, -1.0, 1.0))
            else:
                samples_mono = raw_samples

            n = len(samples_mono)
            fft_data = np.fft.rfft(samples_mono)
            freqs = np.fft.rfftfreq(n, 1 / rate)

            # 3 Dải tần âm thanh trọng tâm cho Haptics
            bass_rms = band_rms(fft_data, freqs, 20, snap["bass_high"], n)
            vocal_rms = band_rms(fft_data, freqs, snap["vocal_low"], snap["vocal_high"], n)
            crisp_rms = band_rms(fft_data, freqs, 1400, min(7500, rate / 2), n)

            total_rms = float(np.sqrt(np.mean(np.square(samples_mono)) + 1e-10))
            energy_avg = energy_avg * 0.95 + total_rms * 0.05
            transient = clamp((total_rms - energy_avg) / max(energy_avg, 70.0), 0.0, 1.0)
            transient_avg = transient_avg * 0.78 + transient * 0.22

            if snap["auto_calibrating"]:
                noise_floor = max(noise_floor * 0.97, total_rms, vocal_rms)
                if time.monotonic() >= calibration_until:
                    calibrated = max(110.0, noise_floor * 1.65)
                    with shared.lock:
                        shared.vibration_threshold = calibrated
                        shared.auto_calibrating = False
                    calibration_until = 0.0
                    log_queue.put(f"Tự động hiệu chuẩn hoàn tất: Ngưỡng kích hoạt {calibrated:.1f}")
            else:
                calibration_until = 0.0
                noise_floor = noise_floor * 0.995 + min(total_rms, vocal_rms) * 0.005

            detected_mode = classify_content(total_rms, vocal_rms, bass_rms, crisp_rms, transient_avg, detected_mode)

            effective = {
                "dual_motor_mode": snap["dual_motor_mode"],
                "vocal_only_mode": snap["vocal_only_mode"],
                "adaptive_threshold": snap["adaptive_threshold"],
                "stereo_panning": snap["stereo_panning"],
                "overdrive_boost": snap["overdrive_boost"],
                "intensity": snap["intensity"],
                "vibration_threshold": snap["vibration_threshold"],
                "dead_zone": snap["dead_zone"],
                "attack_rate": snap["attack_rate"],
                "release_rate": snap["release_rate"],
                "map_in_max": snap["map_in_max"],
                "gamma_correction": snap["gamma_correction"],
            }

            adaptive_floor = noise_floor * 1.5 if effective["adaptive_threshold"] else 0.0
            threshold = max(effective["vibration_threshold"], adaptive_floor)

            def calc_vibration(rms):
                value = map_value_gamma(rms, threshold, effective["map_in_max"], effective["gamma_correction"])
                return clamp(value * effective["intensity"])

            # Motor Trái = Nặng (Trầm), Motor Phải = Nhẹ (Đanh/Súng)
            if effective["dual_motor_mode"]:
                target_left = calc_vibration(bass_rms * 1.15)
                target_right = calc_vibration(crisp_rms * 1.25 + vocal_rms * 0.55)
            else:
                source = vocal_rms if effective["vocal_only_mode"] else total_rms
                target_left = target_right = calc_vibration(source)

            beat_pulse = 0.0
            texture_level = 0.0
            now = time.monotonic()

            if snap["auto_profile"] and detected_mode in {"Game Haptic", "Nhạc", "音乐"}:
                beat_pulse = transient_avg * snap["rhythm_punch"] * snap["intensity"]
                target_left = clamp(target_left + beat_pulse * 0.65)
                target_right = clamp(target_right + beat_pulse * 0.40)
            elif snap["auto_profile"] and detected_mode == "ASMR":
                breath_envelope = clamp((vocal_rms - noise_floor * 0.85) / max(900.0, threshold * 4.0))
                micro_wave = 0.55 + 0.45 * math.sin(now * 2 * math.pi * 34.0)
                texture_level = breath_envelope * snap["texture_amount"] * 0.075 * micro_wave
                target_left = clamp(target_left + texture_level * 0.5)
                target_right = clamp(target_right + texture_level * 1.0)

            # Định vị Stereo
            if effective["stereo_panning"] and abs(stereo_pan) > 0.08:
                pan_mag = abs(stereo_pan)
                if stereo_pan < 0:
                    target_left = clamp(target_left * (1.0 + pan_mag * 0.40))
                    target_right = clamp(target_right * max(0.20, 1.0 - pan_mag * 0.70))
                else:
                    target_right = clamp(target_right * (1.0 + pan_mag * 0.40))
                    target_left = clamp(target_left * max(0.20, 1.0 - pan_mag * 0.70))

            # Overdrive Kick
            overdrive_kick_val = 0.0
            if effective["overdrive_boost"] > 0:
                delta_l = target_left - prev_target_left
                delta_r = target_right - prev_target_right
                boost = effective["overdrive_boost"] * 1.35
                if delta_l > 0.10:
                    kick_l = delta_l * boost
                    target_left = clamp(target_left + kick_l)
                    overdrive_kick_val = max(overdrive_kick_val, kick_l)
                if delta_r > 0.10:
                    kick_r = delta_r * boost
                    target_right = clamp(target_right + kick_r)
                    overdrive_kick_val = max(overdrive_kick_val, kick_r)

            prev_target_left = target_left
            prev_target_right = target_right

            # Active Braking
            rel_l = effective["release_rate"]
            rel_r = effective["release_rate"]
            if target_left < left_vib * 0.55:
                rel_l = max(rel_l, 0.38)
            if target_right < right_vib * 0.55:
                rel_r = max(rel_r, 0.38)

            left_vib = smooth_signal(left_vib, target_left, effective["attack_rate"], rel_l)
            right_vib = smooth_signal(right_vib, target_right, effective["attack_rate"], rel_r)

            if left_vib < effective["dead_zone"]:
                left_vib = 0.0
            if right_vib < effective["dead_zone"]:
                right_vib = 0.0

            # Xử lý Rung 2 Nút Cò LT/RT (Phase 3: Trigger Haptics)
            if snap.get("trigger_haptics_enabled", True):
                norm_punch = clamp(band_rms(fft_data, freqs, 90, 260, n) / max(effective["map_in_max"] * 0.6, 1.0))
                norm_highmid = clamp(band_rms(fft_data, freqs, 900, 2800, n) / max(effective["map_in_max"] * 0.5, 1.0))
                norm_lowmid = clamp(band_rms(fft_data, freqs, 160, 600, n) / max(effective["map_in_max"] * 0.7, 1.0))
                norm_sub = clamp(band_rms(fft_data, freqs, 20, 110, n) / max(effective["map_in_max"] * 0.8, 1.0))

                pan_val = stereo_pan if effective["stereo_panning"] else 0.0
                punch_r_val = norm_punch * (1.0 + max(0.0, pan_val) * 0.45)
                highmid_r_val = norm_highmid * (1.0 + max(0.0, pan_val) * 0.45)
                lowmid_l_val = norm_lowmid * (1.0 + max(0.0, -pan_val) * 0.45)
                sub_l_val = norm_sub * (1.0 + max(0.0, -pan_val) * 0.45)

                trigger_bands = {
                    "punch_r": punch_r_val,
                    "highmid_r": highmid_r_val,
                    "lowmid_l": lowmid_l_val,
                    "sub_l": sub_l_val,
                    "stereo_pan": pan_val,
                    "total_rms": clamp(total_rms / max(effective["map_in_max"], 1.0)),
                }
                raw_lt, raw_rt = calculate_trigger_haptics(
                    trigger_bands,
                    mode=snap.get("trigger_mode", "adaptive_gun_brake"),
                    gain_l=snap.get("trigger_left_gain", 0.70),
                    gain_r=snap.get("trigger_right_gain", 0.85),
                    threshold=snap.get("trigger_threshold", 0.04),
                )
                left_trigger_vib = smooth_signal(left_trigger_vib, raw_lt, 0.85, 0.35)
                right_trigger_vib = smooth_signal(right_trigger_vib, raw_rt, 0.90, 0.35)
            else:
                left_trigger_vib = 0.0
                right_trigger_vib = 0.0

            if left_trigger_vib < effective["dead_zone"]:
                left_trigger_vib = 0.0
            if right_trigger_vib < effective["dead_zone"]:
                right_trigger_vib = 0.0

            if snap["enabled"] and connected:
                dispatcher.set_vibration_4ch(controller_index, left_vib, right_vib, left_trigger_vib, right_trigger_vib)
                if apex_ctrl.is_connected and snap.get("trigger_haptics_enabled", True):
                    apex_ctrl.set_triggers(left_trigger_vib, right_trigger_vib)
            else:
                dispatcher.set_vibration_4ch(controller_index, 0.0, 0.0, 0.0, 0.0)
                if apex_ctrl.is_connected:
                    apex_ctrl.set_triggers(0.0, 0.0)
                if not snap["enabled"]:
                    left_vib = right_vib = left_trigger_vib = right_trigger_vib = 0.0

            # Xử lý màu Đèn LED Apex
            cur_led_hex = "#151b24"
            if snap["apex_led_enabled"]:
                mode = snap["apex_led_mode"]
                bright = snap["apex_brightness"]
                if mode == "Màu tĩnh":
                    br, bg, bb = hex_to_rgb(snap["apex_static_color"])
                    r = int(clamp(br * bright, 0, 255))
                    g = int(clamp(bg * bright, 0, 255))
                    b = int(clamp(bb * bright, 0, 255))
                else:
                    # Đồng bộ âm thanh (Audio Reactive)
                    if snap["apex_reactive_type"] == "Nhịp đập độ sáng (Pulse)":
                        br, bg, bb = hex_to_rgb(snap["apex_static_color"])
                        vib_level = max(left_vib, right_vib, beat_pulse)
                        dyn_bright = clamp(max(0.12, vib_level) * bright)
                        r = int(br * dyn_bright)
                        g = int(bg * dyn_bright)
                        b = int(bb * dyn_bright)
                    else:
                        # Tần số âm thanh (Xanh -> Tím -> Đỏ)
                        impact = clamp(max(left_vib, beat_pulse))
                        energy = clamp(total_rms / 3200.0)
                        crisp_act = clamp(right_vib)
                        if impact > 0.40:
                            # Chấn động mạnh / Nổ lớn / Bass -> Đỏ rực rỡ / Cam cháy
                            blend = clamp((impact - 0.40) / 0.60)
                            r = int(210 + 45 * blend)
                            g = int(50 * (1 - blend))
                            b = int(220 * (1 - blend))
                        elif energy > 0.15 or crisp_act > 0.20:
                            # Nhịp vừa / Súng bắn / Bước chân -> Tím / Magenta
                            blend = clamp(max(energy, crisp_act))
                            r = int(10 + 190 * blend)
                            g = int(170 * (1 - blend * 0.7))
                            b = 255
                        else:
                            # Âm thanh êm dịu -> Xanh ngọc Cyan
                            r = 0
                            g = int(160 * max(0.18, energy))
                            b = int(230 * max(0.25, energy))

                        r = int(clamp(r * bright, 0, 255))
                        g = int(clamp(g * bright, 0, 255))
                        b = int(clamp(b * bright, 0, 255))

                apex_ctrl.set_led(r, g, b)
                cur_led_hex = rgb_to_hex(r, g, b)

            if apex_ctrl.is_connected != last_apex_state:
                last_apex_state = apex_ctrl.is_connected
                if last_apex_state:
                    log_queue.put("🟢 Đã kết nối thành công tay cầm Flydigi Apex (Đèn LED RGB sẵn sàng)")
                else:
                    log_queue.put("⚪ Tay cầm Flydigi Apex đã ngắt kết nối. Đang tiếp tục quét...")

            with shared.lock:
                shared.stats.total_rms = total_rms
                shared.stats.vocal_rms = vocal_rms
                shared.stats.bass_rms = bass_rms
                shared.stats.crisp_rms = crisp_rms
                shared.stats.left_output = left_vib
                shared.stats.right_output = right_vib
                shared.stats.noise_floor = noise_floor
                shared.stats.effective_threshold = threshold
                shared.stats.controller_connected = connected
                shared.stats.peak_left = max(shared.stats.peak_left * 0.985, left_vib)
                shared.stats.peak_right = max(shared.stats.peak_right * 0.985, right_vib)
                shared.stats.peak_left_trigger = max(shared.stats.peak_left_trigger * 0.985, left_trigger_vib)
                shared.stats.peak_right_trigger = max(shared.stats.peak_right_trigger * 0.985, right_trigger_vib)
                shared.stats.trigger_haptics_active = (left_trigger_vib > 0.04 or right_trigger_vib > 0.04)
                shared.stats.detected_mode = detected_mode
                shared.stats.beat_strength = beat_pulse
                shared.stats.texture_level = texture_level
                shared.stats.overdrive_kick = overdrive_kick_val
                shared.stats.stereo_pan = stereo_pan
                shared.stats.apex_connected = apex_ctrl.is_connected
                shared.stats.current_led_hex = cur_led_hex
                shared.stats.device_name = active_audio_source_desc

            time.sleep(0.002)
    except Exception as exc:
        log_queue.put(f"Lỗi runtime: {exc}")
    finally:
        if active_proc_cap is not None:
            try:
                active_proc_cap.stop()
            except Exception:
                pass
        snap = shared.snapshot()
        dispatcher.stop_all()
        apex_ctrl.close()
        if stream is not None:
            stream.close()
        audio.terminate()
        log_queue.put("Đã dừng luồng âm thanh, độ rung tay cầm đã tắt.")


class VerticalMeter(tk.Frame):
    def __init__(
        self,
        parent,
        label,
        color,
        max_value,
        value_format="{:.0f}",
        width=82,
        height=260,
        **kwargs,
    ):
        super().__init__(parent, bg="#151b24", **kwargs)
        self.max_value = max_value
        self.color = color
        self.value_format = value_format
        self.height = height
        self.width = width

        self.value_label = tk.Label(
            self,
            text=value_format.format(0),
            bg="#151b24",
            fg="#f8fafc",
            font=("Consolas", 12, "bold"),
        )
        self.value_label.pack(fill="x", pady=(0, 8))

        self.canvas = tk.Canvas(
            self,
            width=width,
            height=height,
            bg="#0d1118",
            bd=0,
            highlightthickness=1,
            highlightbackground="#293241",
        )
        self.canvas.pack()
        self.track = self.canvas.create_rectangle(18, 12, width - 18, height - 12, fill="#202938", outline="")
        self.fill = self.canvas.create_rectangle(18, height - 12, width - 18, height - 12, fill=color, outline="")
        self.peak = self.canvas.create_line(13, height - 12, width - 13, height - 12, fill="#f8fafc", width=2)
        for i in range(1, 5):
            y = 12 + (height - 24) * i / 5
            self.canvas.create_line(18, y, width - 18, y, fill="#2c3748")

        tk.Label(
            self,
            text=label,
            bg="#151b24",
            fg="#cbd5e1",
            font=("Segoe UI", 9, "bold"),
        ).pack(fill="x", pady=(9, 0))

    def set(self, value, peak=None):
        ratio = clamp(value / max(1e-6, self.max_value))
        top = 12 + (self.height - 24) * (1 - ratio)
        bottom = self.height - 12
        self.canvas.coords(self.fill, 18, top, self.width - 18, bottom)
        if peak is not None:
            peak_ratio = clamp(peak / max(1e-6, self.max_value))
            peak_y = 12 + (self.height - 24) * (1 - peak_ratio)
            self.canvas.coords(self.peak, 13, peak_y, self.width - 13, peak_y)
        self.value_label.config(text=self.value_format.format(value))


def get_foreground_process_info():
    try:
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            return "", 0
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if pid <= 0:
            return "", 0
        return psutil.Process(pid).name().lower(), pid
    except Exception:
        return "", 0


def get_foreground_process_name():
    name, _ = get_foreground_process_info()
    return name


def get_running_window_processes():
    procs = {}

    def enum_windows_callback(hwnd, _):
        try:
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd).strip()
                if title:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    if pid > 0:
                        name = psutil.Process(pid).name().lower()
                        if name not in {
                            "explorer.exe",
                            "taskmgr.exe",
                            "applicationframehost.exe",
                            "shellexperiencehost.exe",
                        }:
                            if name not in procs:
                                procs[name] = title
        except Exception:
            pass

    try:
        win32gui.EnumWindows(enum_windows_callback, None)
    except Exception:
        pass
    return procs


class SystemTrayManager:
    def __init__(self, app):
        self.app = app
        self.icon = None
        self._thread = None
        self._setup_tray()

    def _setup_tray(self):
        try:
            icon_path = Path("app.ico")
            if not icon_path.exists():
                icon_path = APP_PATH.parent / "app.ico"
            if icon_path.exists():
                image = Image.open(icon_path)
            else:
                image = Image.new("RGBA", (64, 64), (37, 99, 235, 255))

            display_presets = [
                "✨ Chuẩn Xúc Giác Haptic DualSense",
                "🎮 Game Bắn Súng (FPS - Sắc Bén)",
                "🏎️ Game Đua Xe (Racing - Tốc Độ)",
                "⚔️ Game Nhập Vai & Hành Động (RPG)",
                "🎵 Âm Nhạc Sôi Động (EDM/Rock)",
                "🎙️ ASMR & Giọng Nói Thì Thầm",
                "🎬 Phim Điện Ảnh & Bom Tấn",
            ]
            preset_items = [
                pystray.MenuItem(p_name, self._make_preset_action(p_name))
                for p_name in display_presets
            ]

            menu = pystray.Menu(
                pystray.MenuItem("🖥️ Mở bảng điều khiển", self.on_open_clicked, default=True),
                pystray.MenuItem("🟢 Bật / Tắt độ rung (F9)", self.on_toggle_vibration_clicked),
                pystray.MenuItem("🎛️ Chuyển Cấu Hình (Preset)", pystray.Menu(*preset_items)),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("❌ Thoát ứng dụng", self.on_exit_clicked),
            )

            self.icon = pystray.Icon("XboxAudioRumbleStudio", image, APP_TITLE, menu=menu)
        except Exception as exc:
            self.app.log_queue.put(f"Lỗi khởi tạo System Tray: {exc}")

    def _make_preset_action(self, preset_name):
        def action(icon, item):
            self.app.apply_preset_by_name(preset_name)
        return action

    def start(self):
        if self.icon:
            self._thread = threading.Thread(target=self.icon.run, daemon=True)
            self._thread.start()

    def stop(self):
        if self.icon:
            try:
                self.icon.stop()
            except Exception:
                pass

    def on_open_clicked(self, icon=None, item=None):
        self.app.restore_from_tray()

    def on_toggle_vibration_clicked(self, icon=None, item=None):
        self.app.master.after(0, self.app.toggle_vibration)

    def on_exit_clicked(self, icon=None, item=None):
        self.app.quit_completely()


class GameProfileDialog(tk.Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.title("🎮 Quản Lý Cấu Hình Game (Auto Game Profiles)")
        self.geometry("740x520")
        self.minsize(680, 460)
        self.configure(bg="#0b0f16")
        self.transient(parent)
        self.grab_set()

        snap = self.app.shared.snapshot()
        self.profiles = dict(snap.get("game_profiles", {}))
        self.fallback_preset = snap.get("fallback_preset", "✨ Chuẩn Xúc Giác Haptic DualSense")

        self.preset_list = [
            "✨ Chuẩn Xúc Giác Haptic DualSense",
            "🎮 Game Bắn Súng (FPS - Sắc Bén)",
            "🏎️ Game Đua Xe (Racing - Tốc Độ)",
            "⚔️ Game Nhập Vai & Hành Động (RPG)",
            "🎵 Âm Nhạc Sôi Động (EDM/Rock)",
            "🎙️ ASMR & Giọng Nói Thì Thầm",
            "🎬 Phim Điện Ảnh & Bom Tấn",
        ]

        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        header = tk.Frame(self, bg="#151b24", padx=16, pady=12)
        header.pack(fill="x")
        tk.Label(
            header,
            text="🎮 Quản Lý Cấu Hình Game Tự Động (Auto Game Profiles)",
            bg="#151b24",
            fg="#f8fafc",
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w")
        tk.Label(
            header,
            text="Tự động chuyển cấu hình Haptic phù hợp ngay khi bạn mở hoặc chuyển sang cửa sổ Game tương ứng.",
            bg="#151b24",
            fg="#94a3b8",
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(3, 0))

        content = tk.Frame(self, bg="#0b0f16", padx=16, pady=12)
        content.pack(fill="both", expand=True)

        table_frame = tk.Frame(content, bg="#151b24", highlightthickness=1, highlightbackground="#293241")
        table_frame.pack(fill="both", expand=True)

        columns = ("process", "preset")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=8,
        )
        self.tree.heading("process", text="Tên Tiến Trình Game (.exe)")
        self.tree.heading("preset", text="Cấu Hình Haptic (Preset) Gán")
        self.tree.column("process", width=240, anchor="w")
        self.tree.column("preset", width=380, anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        edit_frame = tk.Frame(content, bg="#151b24", highlightthickness=1, highlightbackground="#293241", padx=12, pady=10)
        edit_frame.pack(fill="x", pady=(10, 0))
        edit_frame.columnconfigure(1, weight=1)

        ttk.Label(edit_frame, text="File Game:").grid(row=0, column=0, sticky="w", pady=4)
        proc_row = tk.Frame(edit_frame, bg="#151b24")
        proc_row.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=4)
        proc_row.columnconfigure(0, weight=1)

        self.proc_var = tk.StringVar()
        self.proc_entry = tk.Entry(
            proc_row,
            textvariable=self.proc_var,
            bg="#0d1118",
            fg="#f8fafc",
            insertbackground="#ffffff",
            relief="solid",
            bd=1,
            font=("Segoe UI", 9),
        )
        self.proc_entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        tk.Button(
            proc_row,
            text="📂 Duyệt File...",
            command=self.browse_exe,
            bg="#233044",
            activebackground="#314158",
            fg="#f8fafc",
            relief="flat",
            padx=8,
            pady=3,
            cursor="hand2",
            font=("Segoe UI", 9),
        ).grid(row=0, column=1, padx=(0, 6))

        tk.Button(
            proc_row,
            text="⚡ Chọn Game Đang Chạy...",
            command=self.pick_running_process,
            bg="#1e3a8a",
            activebackground="#2563eb",
            fg="#f8fafc",
            relief="flat",
            padx=8,
            pady=3,
            cursor="hand2",
            font=("Segoe UI", 9),
        ).grid(row=0, column=2)

        ttk.Label(edit_frame, text="Cấu Hình:").grid(row=1, column=0, sticky="w", pady=4)
        self.selected_preset_var = tk.StringVar(value=self.preset_list[0])
        self.preset_combo = ttk.Combobox(
            edit_frame,
            textvariable=self.selected_preset_var,
            values=self.preset_list,
            state="readonly",
        )
        self.preset_combo.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=4)

        btn_action_row = tk.Frame(edit_frame, bg="#151b24")
        btn_action_row.grid(row=2, column=0, columnspan=2, sticky="e", pady=(8, 0))

        tk.Button(
            btn_action_row,
            text="➕ Thêm / Cập Nhật Game",
            command=self.add_or_update_game,
            bg="#2563eb",
            activebackground="#1d4ed8",
            fg="#ffffff",
            relief="flat",
            padx=12,
            pady=5,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            btn_action_row,
            text="🗑️ Xóa Game Chọn",
            command=self.delete_selected_game,
            bg="#991b1b",
            activebackground="#b91c1c",
            fg="#ffffff",
            relief="flat",
            padx=12,
            pady=5,
            cursor="hand2",
            font=("Segoe UI", 9),
        ).pack(side="left")

        bottom_frame = tk.Frame(self, bg="#0b0f16", padx=16, pady=10)
        bottom_frame.pack(fill="x", side="bottom")

        fallback_frame = tk.Frame(bottom_frame, bg="#0b0f16")
        fallback_frame.pack(side="left", fill="x")
        tk.Label(
            fallback_frame,
            text="Cấu hình khi thoát Game:",
            bg="#0b0f16",
            fg="#cbd5e1",
            font=("Segoe UI", 9),
        ).pack(side="left", padx=(0, 6))

        self.fallback_var = tk.StringVar(value=self.fallback_preset)
        self.fallback_combo = ttk.Combobox(
            fallback_frame,
            textvariable=self.fallback_var,
            values=self.preset_list,
            state="readonly",
            width=30,
        )
        self.fallback_combo.pack(side="left")

        tk.Button(
            bottom_frame,
            text="💾 Lưu & Áp Dụng",
            command=self.save_and_close,
            bg="#16a34a",
            activebackground="#15803d",
            fg="#ffffff",
            relief="flat",
            padx=16,
            pady=6,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
        ).pack(side="right", padx=(8, 0))

        tk.Button(
            bottom_frame,
            text="Đóng",
            command=self.destroy,
            bg="#374151",
            activebackground="#4b5563",
            fg="#f8fafc",
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
            font=("Segoe UI", 9),
        ).pack(side="right")

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for proc, preset in sorted(self.profiles.items()):
            self.tree.insert("", "end", values=(proc, preset))

    def on_tree_select(self, _event):
        selected = self.tree.selection()
        if selected:
            vals = self.tree.item(selected[0], "values")
            if vals:
                self.proc_var.set(vals[0])
                self.selected_preset_var.set(vals[1])

    def browse_exe(self):
        file_path = filedialog.askopenfilename(
            parent=self,
            title="Chọn file thực thi của Game (.exe)",
            filetypes=[("Chương trình thực thi", "*.exe"), ("Tất cả tập tin", "*.*")],
        )
        if file_path:
            exe_name = Path(file_path).name.lower()
            self.proc_var.set(exe_name)

    def pick_running_process(self):
        running = get_running_window_processes()
        if not running:
            messagebox.showinfo("Thông báo", "Không tìm thấy cửa sổ ứng dụng đang chạy nào.", parent=self)
            return

        popup = tk.Toplevel(self)
        popup.title("Chọn Game hoặc Cửa Sổ Đang Mở")
        popup.geometry("540x400")
        popup.configure(bg="#0b0f16")
        popup.transient(self)
        popup.grab_set()

        tk.Label(
            popup,
            text="Nhấp chọn ứng dụng / Game đang mở:",
            bg="#0b0f16",
            fg="#f8fafc",
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=8,
        ).pack(anchor="w")

        p_frame = tk.Frame(popup, bg="#151b24")
        p_frame.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        p_tree = ttk.Treeview(p_frame, columns=("proc", "title"), show="headings", selectmode="browse")
        p_tree.heading("proc", text="Tiến trình (.exe)")
        p_tree.heading("title", text="Tiêu đề cửa sổ")
        p_tree.column("proc", width=160)
        p_tree.column("title", width=340)
        p_scroll = ttk.Scrollbar(p_frame, orient="vertical", command=p_tree.yview)
        p_tree.configure(yscrollcommand=p_scroll.set)
        p_tree.pack(side="left", fill="both", expand=True)
        p_scroll.pack(side="right", fill="y")

        for p_name, p_title in sorted(running.items()):
            p_tree.insert("", "end", values=(p_name, p_title))

        def select_and_close():
            sel = p_tree.selection()
            if sel:
                v = p_tree.item(sel[0], "values")
                if v:
                    self.proc_var.set(v[0])
            popup.destroy()

        p_tree.bind("<Double-1>", lambda _e: select_and_close())

        btn_row = tk.Frame(popup, bg="#0b0f16", padx=12, pady=8)
        btn_row.pack(fill="x")
        tk.Button(
            btn_row,
            text="Chọn",
            command=select_and_close,
            bg="#2563eb",
            fg="#ffffff",
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2",
        ).pack(side="right")
        tk.Button(
            btn_row,
            text="Hủy",
            command=popup.destroy,
            bg="#374151",
            fg="#f8fafc",
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2",
        ).pack(side="right", padx=(0, 6))

    def add_or_update_game(self):
        raw_proc = self.proc_var.get().strip().lower()
        if not raw_proc:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập hoặc chọn file game (.exe).", parent=self)
            return
        if not raw_proc.endswith(".exe"):
            raw_proc += ".exe"
        preset = self.selected_preset_var.get()
        self.profiles[raw_proc] = preset
        self.refresh_table()

    def delete_selected_game(self):
        selected = self.tree.selection()
        if not selected:
            return
        vals = self.tree.item(selected[0], "values")
        if vals and vals[0] in self.profiles:
            del self.profiles[vals[0]]
            self.refresh_table()

    def save_and_close(self):
        with self.app.shared.lock:
            self.app.shared.game_profiles = dict(self.profiles)
            self.app.shared.fallback_preset = self.fallback_var.get()
        self.app.save_settings()
        self.app.log_queue.put(f"Đã cập nhật danh sách {len(self.profiles)} game tự động nhận diện.")
        self.destroy()


class VibrationApp:
    def __init__(self, master):
        self.master = master
        self.shared = SharedVibrationParams()
        self.log_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.audio_thread = None
        self.test_thread = None
        self.watcher_thread = None
        self.tray_manager = None
        self.profile_dialog = None
        self.last_active_game = ""

        self.configure_window()
        self.load_settings()
        self.create_widgets()
        self.sync_controls_from_params()
        self.start_engine()
        self.start_tray()
        self.start_game_watcher()
        self.master.protocol("WM_DELETE_WINDOW", self.on_window_close_clicked)
        self.master.bind_all("<F9>", lambda _e: self.toggle_vibration())
        self.update_gui()

    def configure_window(self):
        self.master.title(APP_TITLE)
        self.master.geometry("1120x800")
        self.master.minsize(1020, 720)
        try:
            self.master.state("zoomed")
        except Exception:
            pass
        self.master.configure(bg="#0b0f16")
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(".", font=("Segoe UI", 9), background="#111827", foreground="#dbe4ef")
        style.configure("Dark.TFrame", background="#0b0f16")
        style.configure("Panel.TFrame", background="#151b24")
        style.configure("TLabel", background="#151b24", foreground="#dbe4ef")
        style.configure("Muted.TLabel", background="#151b24", foreground="#8fa3b8")
        style.configure("Value.TLabel", background="#151b24", foreground="#f8fafc", font=("Consolas", 10, "bold"))
        style.configure("TCheckbutton", background="#151b24", foreground="#dbe4ef")
        style.map("TCheckbutton", background=[("active", "#151b24")], foreground=[("active", "#ffffff")])
        style.configure("TButton", background="#233044", foreground="#f8fafc", borderwidth=0, padding=(12, 7))
        style.map("TButton", background=[("active", "#314158"), ("pressed", "#1f2937")])
        style.configure("Accent.TButton", background="#2563eb", foreground="#ffffff", font=("Segoe UI", 9, "bold"))
        style.map("Accent.TButton", background=[("active", "#1d4ed8"), ("pressed", "#1e40af")])
        style.configure("TCombobox", fieldbackground="#0f1622", background="#233044", foreground="#f8fafc", arrowcolor="#f8fafc")
        style.configure("Horizontal.TScale", background="#151b24", troughcolor="#293241")

    def load_settings(self):
        if not CONFIG_FILE.exists():
            return
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            self.shared.apply(data)
        except Exception as exc:
            self.log_queue.put(f"Không thể đọc cài đặt, đã dùng giá trị mặc định: {exc}")

    def save_settings(self):
        snap = self.shared.snapshot()
        data = {k: v for k, v in snap.items() if k != "stats"}
        try:
            CONFIG_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as exc:
            self.log_queue.put(f"Không thể lưu cài đặt: {exc}")

    def create_widgets(self):
        shell = tk.Frame(self.master, bg="#0b0f16")
        shell.pack(fill="both", expand=True, padx=16, pady=16)
        shell.columnconfigure(0, minsize=430)
        shell.columnconfigure(1, weight=1)
        shell.rowconfigure(1, weight=1)

        header = tk.Frame(shell, bg="#0b0f16")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        tk.Label(
            header,
            text="🎮 Bảng Điều Khiển Xúc Giác Haptic DualSense & LED Apex",
            bg="#0b0f16",
            fg="#f8fafc",
            font=("Segoe UI", 18, "bold"),
        ).pack(side="left")
        self.status_label = tk.Label(
            header,
            text="Đang khởi động...",
            bg="#122037",
            fg="#c7d2fe",
            font=("Segoe UI", 10, "bold"),
            padx=14,
            pady=8,
        )
        self.status_label.pack(side="right")

        self.master_power_btn = tk.Button(
            header,
            text="🟢 RUNG: ĐANG BẬT (F9)",
            bg="#15803d",
            activebackground="#16a34a",
            fg="#ffffff",
            activeforeground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            padx=16,
            pady=6,
            relief="flat",
            cursor="hand2",
            command=self.toggle_vibration,
        )
        self.master_power_btn.pack(side="right", padx=(0, 10))

        left = tk.Frame(shell, bg="#0b0f16")
        left.grid(row=1, column=0, sticky="nsew", padx=(0, 14))
        left.columnconfigure(0, weight=1)

        right = tk.Frame(shell, bg="#151b24", highlightthickness=1, highlightbackground="#293241")
        right.grid(row=1, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        # 1. Panel Thiết bị & Cấu hình Preset
        device_box, device_panel = self.make_panel(left, "Thiết bị & Cấu hình Preset")
        device_box.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        device_panel.columnconfigure(1, weight=1)

        ttk.Label(device_panel, text="Tay cầm").grid(row=0, column=0, sticky="w")
        self.controller_var = tk.StringVar(value="0")
        self.controller_box = ttk.Combobox(
            device_panel,
            textvariable=self.controller_var,
            values=["0", "1", "2", "3"],
            width=8,
            state="readonly",
        )
        self.controller_box.grid(row=0, column=1, sticky="w", padx=(10, 0))
        self.controller_box.bind("<<ComboboxSelected>>", lambda _e: self.set_controller())

        ttk.Label(device_panel, text="Cấu hình").grid(row=1, column=0, sticky="w", pady=(8, 0))
        preset_row = tk.Frame(device_panel, bg="#151b24")
        preset_row.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(8, 0))
        preset_row.columnconfigure(0, weight=1)

        self.preset_var = tk.StringVar(value="✨ Chuẩn Xúc Giác Haptic DualSense")
        preset_keys = [k for k in PRESETS.keys() if not any(c in k for c in ["人声", "低频", "轻柔", "全频"])]
        self.preset_combo = ttk.Combobox(
            preset_row,
            textvariable=self.preset_var,
            values=preset_keys,
            state="readonly",
        )
        self.preset_combo.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.preset_combo.bind("<<ComboboxSelected>>", lambda _e: self.apply_preset())
        ttk.Button(preset_row, text="Áp dụng", command=self.apply_preset, width=8).grid(row=0, column=1)

        ttk.Label(device_panel, text="Nguồn thu").grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.audio_mode_var = tk.StringVar(value="🎯 Tự động cô lập Game đang chơi")
        self.audio_mode_combo = ttk.Combobox(
            device_panel,
            textvariable=self.audio_mode_var,
            values=[
                "🎯 Tự động cô lập Game đang chơi",
                "🔊 Toàn hệ thống Windows (Mặc định)",
            ],
            state="readonly",
        )
        self.audio_mode_combo.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=(8, 0))
        self.audio_mode_combo.bind("<<ComboboxSelected>>", lambda _e: self.set_audio_capture_mode())

        ttk.Label(device_panel, text="Chiến lược").grid(row=3, column=0, sticky="w", pady=(8, 0))
        self.profile_label = ttk.Label(device_panel, text="Tự động nhận diện Haptic", style="Value.TLabel")
        self.profile_label.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=(8, 0))

        button_row = tk.Frame(device_panel, bg="#151b24")
        button_row.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        button_row.columnconfigure((0, 1), weight=1)
        ttk.Button(button_row, text="⚡ Tự động hiệu chuẩn", command=self.start_calibration, style="Accent.TButton").grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(button_row, text="🎮 Kiểm tra rung", command=self.test_vibration).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self.device_label = ttk.Label(device_panel, text="Nguồn âm thanh: Đang khởi tạo...", style="Muted.TLabel", wraplength=380)
        self.device_label.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        # Cấu hình tự động theo game & Khay hệ thống
        auto_game_row = tk.Frame(device_panel, bg="#151b24")
        auto_game_row.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        auto_game_row.columnconfigure(0, weight=1)

        self.auto_game_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            auto_game_row,
            text="Tự động đổi cấu hình theo Game (Auto Detect)",
            variable=self.auto_game_var,
            command=self.set_auto_game_detect,
        ).grid(row=0, column=0, sticky="w")

        tk.Button(
            auto_game_row,
            text="🎮 Quản lý Game...",
            command=self.open_game_profile_dialog,
            bg="#233044",
            activebackground="#314158",
            fg="#f8fafc",
            relief="flat",
            padx=10,
            pady=3,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
        ).grid(row=0, column=1, sticky="e")

        self.minimize_tray_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            auto_game_row,
            text="Thu nhỏ xuống khay hệ thống khi đóng [X]",
            variable=self.minimize_tray_var,
            command=self.set_minimize_to_tray,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))

        # 2. Panel Chế độ & Xử lý Nâng cao
        mode_box, mode = self.make_panel(left, "Chế độ & Xử lý Âm thanh Không gian")
        mode_box.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        mode.columnconfigure(0, weight=1)

        self.enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(mode, text="Bật phản hồi xúc giác rung (Master)", variable=self.enabled_var, command=self.set_enabled).grid(row=0, column=0, sticky="w")

        self.auto_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(mode, text="Chế độ tự động nhận diện (Game / Nhạc / ASMR)", variable=self.auto_var, command=self.set_auto_profile).grid(row=1, column=0, sticky="w", pady=(6, 0))

        self.stereo_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(mode, text="Định vị Stereo không gian (Tiếng súng/nổ bên nào rung bên đó)", variable=self.stereo_var, command=self.set_stereo).grid(row=2, column=0, sticky="w", pady=(6, 0))

        self.dual_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(mode, text="Tách 2 Motor chuẩn phần cứng (Trái: Trầm/Nổ - Phải: Súng/Đanh)", variable=self.dual_var, command=self.set_dual_motor).grid(row=3, column=0, sticky="w", pady=(6, 0))

        # 🎯 Phase 3: Trigger Haptics
        self.trigger_haptics_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(mode, text="🎯 Rung 2 nút cò LT/RT (Xbox Impulse & Flydigi Triggers)", variable=self.trigger_haptics_var, command=self.set_trigger_haptics).grid(row=4, column=0, sticky="w", pady=(6, 0))

        trig_row = tk.Frame(mode, bg="#151b24")
        trig_row.grid(row=5, column=0, sticky="ew", pady=(4, 0))
        ttk.Label(trig_row, text="Kiểu rung cò:").pack(side="left")
        self.trigger_mode_var = tk.StringVar(value="🎯 Tự động tối ưu: RT Bắn / LT Phanh")
        self.trigger_mode_combo = ttk.Combobox(
            trig_row,
            textvariable=self.trigger_mode_var,
            values=[
                "🎯 Tự động tối ưu: RT Bắn / LT Phanh",
                "🔊 Định hướng Stereo: Trái/Phải theo âm",
                "⚡ Đồng bộ toàn dải cùng 2 motor thân",
            ],
            state="readonly",
            width=32,
        )
        self.trigger_mode_combo.pack(side="right", fill="x", expand=True, padx=(8, 0))
        self.trigger_mode_combo.bind("<<ComboboxSelected>>", lambda _e: self.set_trigger_mode())

        # 3. Panel Đèn LED RGB Apex (Flydigi)
        apex_box, apex_panel = self.make_panel(left, "Đèn LED RGB Tay Cầm Apex (Flydigi)")
        apex_box.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        apex_panel.columnconfigure(1, weight=1)

        # Hàng 0: Bật/tắt LED Apex & Trạng thái kết nối
        led_header = tk.Frame(apex_panel, bg="#151b24")
        led_header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        led_header.columnconfigure(1, weight=1)

        self.apex_enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(led_header, text="Bật LED Apex", variable=self.apex_enabled_var, command=self.set_apex_params).grid(row=0, column=0, sticky="w")
        self.apex_status_label = tk.Label(
            led_header,
            text="Đang quét tay cầm Apex...",
            bg="#151b24",
            fg="#38bdf8",
            font=("Segoe UI", 9, "bold"),
        )
        self.apex_status_label.grid(row=0, column=1, sticky="e")

        # Hàng 1: Chế độ LED
        ttk.Label(apex_panel, text="Chế độ").grid(row=1, column=0, sticky="w", pady=(4, 0))
        self.apex_mode_var = tk.StringVar(value="Đồng bộ âm thanh")
        self.apex_mode_combo = ttk.Combobox(
            apex_panel,
            textvariable=self.apex_mode_var,
            values=["Đồng bộ âm thanh", "Màu tĩnh"],
            state="readonly",
        )
        self.apex_mode_combo.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(4, 0))
        self.apex_mode_combo.bind("<<ComboboxSelected>>", lambda _e: self.set_apex_params())

        # Hàng 2: Kiểu hiệu ứng Audio Reactive
        ttk.Label(apex_panel, text="Hiệu ứng").grid(row=2, column=0, sticky="w", pady=(6, 0))
        self.apex_style_var = tk.StringVar(value="Tần số âm thanh (Xanh->Tím->Đỏ)")
        self.apex_style_combo = ttk.Combobox(
            apex_panel,
            textvariable=self.apex_style_var,
            values=["Tần số âm thanh (Xanh->Tím->Đỏ)", "Nhịp đập độ sáng (Pulse)"],
            state="readonly",
        )
        self.apex_style_combo.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=(6, 0))
        self.apex_style_combo.bind("<<ComboboxSelected>>", lambda _e: self.set_apex_params())

        # Hàng 3: Bảng màu nhanh
        ttk.Label(apex_panel, text="Bảng màu").grid(row=3, column=0, sticky="w", pady=(8, 0))
        palette_frame = tk.Frame(apex_panel, bg="#151b24")
        palette_frame.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=(8, 0))
        palette_colors = [
            ("#ef4444", "Đỏ"),
            ("#f97316", "Cam"),
            ("#eab308", "Vàng"),
            ("#22c55e", "Lục"),
            ("#06b6d4", "Lam"),
            ("#a855f7", "Tím"),
            ("#ec4899", "Hồng"),
            ("#f8fafc", "Trắng"),
        ]
        for c_hex, c_name in palette_colors:
            btn = tk.Button(
                palette_frame,
                bg=c_hex,
                activebackground=c_hex,
                width=2,
                height=1,
                relief="flat",
                bd=0,
                cursor="hand2",
                command=lambda col=c_hex: self.select_palette_color(col),
            )
            btn.pack(side="left", padx=2)

        ttk.Button(palette_frame, text="🎨 Khác...", command=self.pick_custom_color, width=7).pack(side="left", padx=(6, 0))

        # Hàng 4: Thanh trượt độ sáng LED
        ttk.Label(apex_panel, text="Độ sáng", style="Muted.TLabel").grid(row=4, column=0, sticky="w", pady=(8, 0))
        self.apex_bright_label = ttk.Label(apex_panel, text="100%", width=8, style="Value.TLabel")
        self.apex_bright_label.grid(row=4, column=2, sticky="e", padx=(6, 0), pady=(8, 0))
        self.apex_bright_scale = ttk.Scale(
            apex_panel,
            from_=0.1,
            to=1.0,
            orient="horizontal",
            command=self.set_apex_brightness_scale,
        )
        self.apex_bright_scale.grid(row=4, column=1, sticky="ew", padx=(10, 8), pady=(8, 0))

        # Hàng 5: Ô đèn LED ảo trực quan (Preview)
        preview_frame = tk.Frame(apex_panel, bg="#0d1118", bd=1, relief="solid")
        preview_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        preview_frame.columnconfigure(1, weight=1)

        tk.Label(
            preview_frame,
            text="Đèn LED tay cầm thực tế:",
            bg="#0d1118",
            fg="#94a3b8",
            font=("Segoe UI", 9),
            padx=8,
            pady=4,
        ).grid(row=0, column=0, sticky="w")
        self.led_preview_canvas = tk.Canvas(
            preview_frame,
            height=20,
            width=180,
            bg="#0d1118",
            highlightthickness=0,
        )
        self.led_preview_canvas.grid(row=0, column=1, sticky="e", padx=8, pady=4)
        self.led_preview_bar = self.led_preview_canvas.create_rectangle(4, 3, 176, 17, fill="#00b4d8", outline="#f8fafc", width=1)

        # 4. Panel Độ rung & Cảm giác
        controls_box, controls = self.make_panel(left, "Độ rung & Tinh chỉnh Xúc giác")
        controls_box.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        controls.columnconfigure(1, weight=1)

        self.sliders = {}
        slider_specs = [
            ("Cường độ tổng thể", "intensity", 0.1, 1.0, "{:.2f}", False, "Giới hạn lực rung tối đa của tay cầm."),
            ("Overdrive Kick (Triệt trễ)", "overdrive_boost", 0.0, 1.0, "{:.2f}", False, "Xung kích tốc tức thì khi có tiếng súng/nổ, khắc phục độ ì của motor."),
            ("Lực nhịp điệu (Punch)", "rhythm_punch", 0.0, 1.0, "{:.2f}", False, "Độ nảy uy lực theo tiếng trống, tiếng nổ và dập cơ học."),
            ("Độ tê chi tiết (Texture)", "texture_amount", 0.0, 1.0, "{:.2f}", False, "Độ tê mịn tần số cao (bước chân, cạ kim loại, hơi thở)."),
            ("Lực Cò Trái (LT - Phanh/Ngắm)", "trigger_left_gain", 0.0, 1.0, "{:.2f}", False, "Cường độ rung nút cò LT (Xbox Impulse / Flydigi)."),
            ("Lực Cò Phải (RT - Bắn/Ga)", "trigger_right_gain", 0.0, 1.0, "{:.2f}", False, "Cường độ rung nút cò RT (Xbox Impulse / Flydigi)."),
        ]
        for row, spec in enumerate(slider_specs):
            self.add_slider(controls, row, *spec)

        # Phần hiển thị bên phải: Các thanh đo thời gian thực
        monitor_header = tk.Frame(right, bg="#151b24")
        monitor_header.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 4))
        tk.Label(
            monitor_header,
            text="Phổ Đo Xúc Giác & Motor Thời Gian Thực",
            bg="#151b24",
            fg="#f8fafc",
            font=("Segoe UI", 16, "bold"),
        ).pack(side="left")
        self.noise_label = tk.Label(
            monitor_header,
            text="Nhiễu nền: 0.0",
            bg="#151b24",
            fg="#8fa3b8",
            font=("Consolas", 10, "bold"),
        )
        self.noise_label.pack(side="right")

        monitor = tk.Frame(right, bg="#151b24")
        monitor.grid(row=1, column=0, sticky="nsew", padx=18, pady=(8, 14))
        for column in range(9):
            monitor.columnconfigure(column, weight=1)
        monitor.rowconfigure(0, weight=1)

        self.meters = {
            "total": VerticalMeter(monitor, "Tổng âm", "#94a3b8", 6000, width=68),
            "bass": VerticalMeter(monitor, "Trầm / Nổ", "#38bdf8", 6000, width=68),
            "crisp": VerticalMeter(monitor, "Đanh / Súng", "#a855f7", 4000, width=68),
            "beat": VerticalMeter(monitor, "Nhịp điệu", "#f59e0b", 1.0, "{:.3f}", width=68),
            "overdrive": VerticalMeter(monitor, "Xung Kick", "#ef4444", 0.6, "{:.3f}", width=68),
            "left": VerticalMeter(monitor, "Motor Trái", "#34d399", 1.0, "{:.3f}", width=74, height=300),
            "right": VerticalMeter(monitor, "Motor Phải", "#60a5fa", 1.0, "{:.3f}", width=74, height=300),
            "lt": VerticalMeter(monitor, "Cò LT (Phanh)", "#10b981", 1.0, "{:.3f}", width=74, height=300),
            "rt": VerticalMeter(monitor, "Cò RT (Bắn)", "#f43f5e", 1.0, "{:.3f}", width=74, height=300),
        }
        for col, meter in enumerate(self.meters.values()):
            meter.grid(row=0, column=col, sticky="nsew", padx=4)

        log_frame = tk.Frame(right, bg="#0d1118", highlightthickness=1, highlightbackground="#293241")
        log_frame.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 18))
        tk.Label(
            log_frame,
            text="Nhật ký hoạt động",
            bg="#0d1118",
            fg="#cbd5e1",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=10, pady=(8, 0))
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=6,
            state="disabled",
            bg="#0d1118",
            fg="#d8e0ea",
            insertbackground="#ffffff",
            relief="flat",
            font=("Consolas", 9),
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=(6, 10))

    def make_panel(self, parent, title):
        outer = tk.Frame(parent, bg="#151b24", highlightthickness=1, highlightbackground="#293241")
        tk.Label(
            outer,
            text=title,
            bg="#151b24",
            fg="#f8fafc",
            font=("Segoe UI", 11, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 6))
        body = tk.Frame(outer, bg="#151b24")
        body.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 12))
        body.columnconfigure(0, weight=0)
        body.columnconfigure(1, weight=1)
        outer.columnconfigure(0, weight=1)
        return outer, body

    def add_hint(self, parent, row, text):
        tk.Label(
            parent,
            text=text,
            bg="#151b24",
            fg="#8fa3b8",
            wraplength=380,
            justify="left",
            anchor="w",
            font=("Segoe UI", 8),
        ).grid(row=row, column=0, columnspan=3, sticky="ew", pady=(2, 4))

    def add_slider(self, parent, row, label, attr, from_, to, fmt, is_int=False, help_text=""):
        base_row = row * 2
        ttk.Label(parent, text=label, style="Muted.TLabel").grid(row=base_row, column=0, sticky="w", pady=(5, 0))
        value_label = ttk.Label(parent, width=8, style="Value.TLabel")
        value_label.grid(row=base_row, column=2, sticky="e", padx=(8, 0), pady=(5, 0))
        scale = ttk.Scale(
            parent,
            from_=from_,
            to=to,
            orient="horizontal",
            command=lambda value, a=attr, f=fmt, i=is_int, l=value_label: self.set_numeric(a, value, f, i, l),
        )
        scale.grid(row=base_row, column=1, sticky="ew", padx=(10, 8), pady=(5, 0))
        if help_text:
            self.add_hint(parent, base_row + 1, help_text)
        self.sliders[attr] = (scale, value_label, fmt, is_int)

    def select_palette_color(self, hex_color):
        with self.shared.lock:
            self.shared.apex_static_color = hex_color
            if self.shared.apex_led_mode == "Màu tĩnh":
                self.shared.apex_static_color = hex_color
        self.log_queue.put(f"Đã chọn màu LED Apex: {hex_color}")
        self.led_preview_canvas.itemconfig(self.led_preview_bar, fill=hex_color)
        self.save_settings()

    def pick_custom_color(self):
        snap = self.shared.snapshot()
        color = colorchooser.askcolor(initialcolor=snap["apex_static_color"], title="Chọn màu LED Apex tùy chỉnh")
        if color and color[1]:
            hex_col = color[1]
            self.select_palette_color(hex_col)

    def set_apex_params(self):
        with self.shared.lock:
            self.shared.apex_led_enabled = self.apex_enabled_var.get()
            self.shared.apex_led_mode = self.apex_mode_var.get()
            self.shared.apex_reactive_type = self.apex_style_var.get()
        self.log_queue.put(f"Cập nhật LED Apex: {'BẬT' if self.apex_enabled_var.get() else 'TẮT'} | {self.apex_mode_var.get()} | {self.apex_style_var.get()}")
        self.save_settings()

    def set_apex_brightness_scale(self, val):
        b = float(val)
        with self.shared.lock:
            self.shared.apex_brightness = b
        if hasattr(self, "apex_bright_label"):
            self.apex_bright_label.config(text=f"{int(b*100)}%")
        self.save_settings()

    def sync_controls_from_params(self):
        snap = self.shared.snapshot()
        self.enabled_var.set(snap["enabled"])
        self.sync_power_button(snap["enabled"])
        self.controller_var.set(str(snap["controller_index"]))
        if hasattr(self, "auto_var"):
            self.auto_var.set(snap["auto_profile"])
        if hasattr(self, "stereo_var"):
            self.stereo_var.set(snap["stereo_panning"])
        if hasattr(self, "dual_var"):
            self.dual_var.set(snap["dual_motor_mode"])
        if hasattr(self, "auto_game_var"):
            self.auto_game_var.set(snap.get("auto_game_detect", True))
        if hasattr(self, "minimize_tray_var"):
            self.minimize_tray_var.set(snap.get("minimize_to_tray", True))
        if hasattr(self, "audio_mode_var"):
            curr_mode = snap.get("audio_capture_mode", "auto_game_process")
            self.audio_mode_var.set(
                "🎯 Tự động cô lập Game đang chơi"
                if curr_mode == "auto_game_process"
                else "🔊 Toàn hệ thống Windows (Mặc định)"
            )

        if hasattr(self, "trigger_haptics_var"):
            self.trigger_haptics_var.set(snap.get("trigger_haptics_enabled", True))
        if hasattr(self, "trigger_mode_var"):
            t_mode = snap.get("trigger_mode", "adaptive_gun_brake")
            if t_mode == "directional_stereo":
                self.trigger_mode_var.set("🔊 Định hướng Stereo: Trái/Phải theo âm")
            elif t_mode == "linked_body":
                self.trigger_mode_var.set("⚡ Đồng bộ toàn dải cùng 2 motor thân")
            else:
                self.trigger_mode_var.set("🎯 Tự động tối ưu: RT Bắn / LT Phanh")

        if hasattr(self, "apex_enabled_var"):
            self.apex_enabled_var.set(snap["apex_led_enabled"])
            self.apex_mode_var.set(snap["apex_led_mode"])
            self.apex_style_var.set(snap["apex_reactive_type"])
            self.apex_bright_scale.set(snap["apex_brightness"])
            self.apex_bright_label.config(text=f"{int(snap['apex_brightness']*100)}%")
            self.led_preview_canvas.itemconfig(self.led_preview_bar, fill=snap["apex_static_color"])

        for attr, (scale, label, fmt, _is_int) in self.sliders.items():
            if attr in snap:
                scale.set(snap[attr])
                label.config(text=fmt.format(snap[attr]))

    def start_engine(self):
        if self.audio_thread and self.audio_thread.is_alive():
            return
        self.stop_event.clear()
        self.audio_thread = threading.Thread(
            target=audio_vibration_thread,
            args=(self.shared, self.log_queue, self.stop_event),
            daemon=True,
        )
        self.audio_thread.start()

    def set_numeric(self, attr, value, fmt, is_int, label):
        value = int(float(value)) if is_int else float(value)
        with self.shared.lock:
            setattr(self.shared, attr, value)
        label.config(text=fmt.format(value))

    def toggle_vibration(self):
        with self.shared.lock:
            self.shared.enabled = not self.shared.enabled
            enabled = self.shared.enabled
        if hasattr(self, "enabled_var"):
            self.enabled_var.set(enabled)
        if not enabled:
            snap = self.shared.snapshot()
            set_vibration(snap["controller_index"], 0, 0)
        self.sync_power_button(enabled)
        self.log_queue.put(f"Chuyển đổi trạng thái rung: {'🟢 ĐANG BẬT' if enabled else '🔴 ĐÃ TẮT'}")

    def sync_power_button(self, enabled):
        if not hasattr(self, "master_power_btn"):
            return
        if enabled:
            self.master_power_btn.config(
                text="🟢 RUNG: ĐANG BẬT (F9)",
                bg="#15803d",
                activebackground="#16a34a",
                fg="#ffffff",
            )
        else:
            self.master_power_btn.config(
                text="🔴 RUNG: ĐÃ TẮT (F9)",
                bg="#b91c1c",
                activebackground="#dc2626",
                fg="#ffffff",
            )

    def set_enabled(self):
        with self.shared.lock:
            self.shared.enabled = self.enabled_var.get()
            enabled = self.shared.enabled
        if not enabled:
            snap = self.shared.snapshot()
            set_vibration(snap["controller_index"], 0, 0)
        self.sync_power_button(enabled)
        self.log_queue.put(f"Trạng thái rung: {'🟢 BẬT' if enabled else '🔴 TẮT'}")

    def set_auto_profile(self):
        with self.shared.lock:
            self.shared.auto_profile = self.auto_var.get()
        self.profile_label.config(text="Tự động nhận diện Haptic" if self.auto_var.get() else "Cố định thủ công")

    def set_stereo(self):
        with self.shared.lock:
            self.shared.stereo_panning = self.stereo_var.get()
        self.log_queue.put(f"Định vị không gian Stereo: {'BẬT' if self.stereo_var.get() else 'TẮT'}")

    def set_dual_motor(self):
        with self.shared.lock:
            self.shared.dual_motor_mode = self.dual_var.get()
        self.log_queue.put(f"Tách 2 Motor phần cứng: {'BẬT' if self.dual_var.get() else 'TẮT'}")

    def set_controller(self):
        with self.shared.lock:
            old_index = self.shared.controller_index
            self.shared.controller_index = int(self.controller_var.get())
        set_vibration(old_index, 0, 0)
        self.log_queue.put(f"Đã chuyển sang tay cầm số {self.controller_var.get()}.")

    def apply_preset(self):
        name = self.preset_var.get()
        if name in PRESETS:
            preset = PRESETS[name]
            self.shared.apply(preset)
            self.sync_controls_from_params()
            self.log_queue.put(f"Đã kích hoạt cấu hình: {name}")

    def start_calibration(self):
        with self.shared.lock:
            self.shared.auto_calibrating = True

    def test_vibration(self):
        if self.test_thread and self.test_thread.is_alive():
            return

        def run():
            snap = self.shared.snapshot()
            index = snap["controller_index"]
            if not is_controller_connected(index):
                self.log_queue.put("Kiểm tra thất bại: Tay cầm chưa được kết nối.")
                return
            disp = Unified4ChannelDispatcher()
            self.log_queue.put("Bắt đầu kiểm tra rung: Thân Trái -> Thân Phải -> Cò Phanh LT -> Cò Bắn RT -> Cả 4 Motor")
            pattern = [
                (0.60, 0.0, 0.0, 0.0, 0.22),
                (0.0, 0.60, 0.0, 0.0, 0.22),
                (0.0, 0.0, 0.85, 0.0, 0.25),
                (0.0, 0.0, 0.0, 0.85, 0.25),
                (0.85, 0.85, 0.85, 0.85, 0.35),
                (0.0, 0.0, 0.0, 0.0, 0.05),
            ]
            for left, right, lt, rt, duration in pattern:
                if self.stop_event.is_set():
                    break
                disp.set_vibration_4ch(index, left, right, lt, rt)
                time.sleep(duration)
            disp.stop_all()
            self.log_queue.put("Kiểm tra rung 4 kênh hoàn tất.")

        self.test_thread = threading.Thread(target=run, daemon=True)
        self.test_thread.start()

    def update_gui(self):
        snap = self.shared.snapshot()
        stats = snap["stats"]
        connected = "Đã kết nối" if stats["controller_connected"] else "Chưa kết nối"
        running = self.audio_thread is not None and self.audio_thread.is_alive()
        auto_text = stats["detected_mode"] if snap["auto_profile"] else "Thủ công"

        pan = stats.get("stereo_pan", 0.0)
        if abs(pan) < 0.12:
            pan_str = "Cân bằng"
        elif pan < 0:
            pan_str = f"Lệch Trái ({abs(pan)*100:.0f}%)"
        else:
            pan_str = f"Lệch Phải ({abs(pan)*100:.0f}%)"

        self.status_label.config(text=f"Tay cầm {snap['controller_index']}: {connected} | {auto_text} | {'Đang chạy' if running else 'Đã dừng'}")
        self.device_label.config(text=f"Nguồn âm thanh: {stats['device_name']}")
        self.noise_label.config(text=f"Định vị: {pan_str}  |  Nhiễu nền: {stats['noise_floor']:.1f}")
        self.profile_label.config(text="Tự động nhận diện Haptic" if snap["auto_profile"] else "Cố định thủ công")

        # Cập nhật hiển thị trạng thái LED Apex
        if hasattr(self, "apex_status_label"):
            if stats.get("apex_connected", False):
                self.apex_status_label.config(text="🟢 Đã kết nối Flydigi Apex", fg="#22c55e")
            else:
                self.apex_status_label.config(text="⚪ Đang quét tay cầm Apex / Dongle...", fg="#94a3b8")

        # Cập nhật ô đèn LED ảo (Preview)
        if hasattr(self, "led_preview_canvas"):
            current_color = stats.get("current_led_hex", "#00b4d8")
            self.led_preview_canvas.itemconfig(self.led_preview_bar, fill=current_color)

        self.meters["total"].set(stats["total_rms"])
        self.meters["bass"].set(stats["bass_rms"])
        self.meters["crisp"].set(stats.get("crisp_rms", stats["vocal_rms"]))
        self.meters["beat"].set(stats["beat_strength"])
        self.meters["overdrive"].set(stats.get("overdrive_kick", 0.0))
        self.meters["left"].set(stats["left_output"], stats["peak_left"])
        self.meters["right"].set(stats["right_output"], stats["peak_right"])
        if "lt" in self.meters:
            self.meters["lt"].set(stats.get("peak_left_trigger", 0.0), stats.get("peak_left_trigger", 0.0))
        if "rt" in self.meters:
            self.meters["rt"].set(stats.get("peak_right_trigger", 0.0), stats.get("peak_right_trigger", 0.0))

        while True:
            try:
                msg = self.log_queue.get_nowait()
            except queue.Empty:
                break
            self.append_log(msg)

        self.sync_power_button(snap["enabled"])
        if hasattr(self, "enabled_var") and self.enabled_var.get() != snap["enabled"]:
            self.enabled_var.set(snap["enabled"])

        if snap["auto_calibrating"]:
            self.status_label.config(text=f"Tay cầm {snap['controller_index']}: {connected} | Đang hiệu chuẩn...")

        self.master.after(50, self.update_gui)

    def append_log(self, msg):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, f"[{timestamp}] {msg}\n")
        self.log_text.see(tk.END)
        lines = int(self.log_text.index("end-1c").split(".")[0])
        if lines > 300:
            self.log_text.delete("1.0", "80.0")
        self.log_text.config(state="disabled")

    def start_tray(self):
        try:
            self.tray_manager = SystemTrayManager(self)
            self.tray_manager.start()
        except Exception as exc:
            self.log_queue.put(f"Lỗi khởi động System Tray: {exc}")

    def start_game_watcher(self):
        self.watcher_thread = threading.Thread(target=self._game_watcher_loop, daemon=True)
        self.watcher_thread.start()

    def _game_watcher_loop(self):
        while not self.stop_event.is_set():
            time.sleep(1.2)
            snap = self.shared.snapshot()
            if not snap.get("auto_game_detect", True):
                continue

            proc, proc_pid = get_foreground_process_info()
            if not proc:
                continue

            profiles = snap.get("game_profiles", {})
            if proc in profiles:
                target_preset = profiles[proc]
                if proc != self.last_active_game:
                    self.last_active_game = proc
                    with self.shared.lock:
                        self.shared.current_game_pid = proc_pid
                    self.master.after(0, self.auto_apply_game_preset, target_preset, proc)
            else:
                if self.last_active_game != "":
                    current_exe = Path(sys.executable).name.lower()
                    if proc != current_exe and "python" not in proc:
                        self.last_active_game = ""
                        with self.shared.lock:
                            self.shared.current_game_pid = 0
                        fallback = snap.get("fallback_preset", "✨ Chuẩn Xúc Giác Haptic DualSense")
                        self.master.after(0, self.auto_apply_fallback_preset, fallback)

    def auto_apply_game_preset(self, target_preset, proc_name):
        if target_preset in PRESETS:
            self.preset_var.set(target_preset)
            self.apply_preset()
            self.log_queue.put(f"🎮 Phát hiện [{proc_name}] ➔ Tự động áp dụng: {target_preset}")

    def auto_apply_fallback_preset(self, fallback_preset):
        if fallback_preset in PRESETS:
            self.preset_var.set(fallback_preset)
            self.apply_preset()
            self.log_queue.put(f"🔄 Thoát game ➔ Hoàn về cấu hình chuẩn: {fallback_preset}")

    def apply_preset_by_name(self, name):
        def _do():
            if name in PRESETS:
                self.preset_var.set(name)
                self.apply_preset()
        self.master.after(0, _do)

    def set_auto_game_detect(self):
        with self.shared.lock:
            self.shared.auto_game_detect = self.auto_game_var.get()
        self.log_queue.put(f"Tự động nhận diện Game: {'BẬT' if self.auto_game_var.get() else 'TẮT'}")
        self.save_settings()

    def set_minimize_to_tray(self):
        with self.shared.lock:
            self.shared.minimize_to_tray = self.minimize_tray_var.get()
        self.log_queue.put(f"Thu nhỏ xuống khay khi đóng: {'BẬT' if self.minimize_tray_var.get() else 'TẮT'}")
        self.save_settings()

    def set_audio_capture_mode(self):
        val = "auto_game_process" if "Tự động cô lập" in self.audio_mode_var.get() else "system"
        with self.shared.lock:
            self.shared.audio_capture_mode = val
        self.log_queue.put(f"Chế độ nguồn thu âm: {self.audio_mode_var.get()}")
        self.save_settings()

    def set_trigger_haptics(self):
        with self.shared.lock:
            self.shared.trigger_haptics_enabled = bool(self.trigger_haptics_var.get())
        self.log_queue.put(f"Rung 2 nút cò LT/RT: {'🟢 BẬT' if self.trigger_haptics_var.get() else '🔴 TẮT'}")
        self.save_settings()

    def set_trigger_mode(self):
        sel = self.trigger_mode_var.get()
        if "Định hướng Stereo" in sel:
            val = "directional_stereo"
        elif "Đồng bộ" in sel:
            val = "linked_body"
        else:
            val = "adaptive_gun_brake"
        with self.shared.lock:
            self.shared.trigger_mode = val
        self.log_queue.put(f"Chế độ rung cò: {sel}")
        self.save_settings()

    def open_game_profile_dialog(self):
        if self.profile_dialog and self.profile_dialog.winfo_exists():
            self.profile_dialog.lift()
            self.profile_dialog.focus_force()
        else:
            self.profile_dialog = GameProfileDialog(self.master, self)

    def on_window_close_clicked(self):
        snap = self.shared.snapshot()
        if snap.get("minimize_to_tray", True):
            self.master.withdraw()
            self.log_queue.put("Ứng dụng đang chạy ngầm dưới khay hệ thống (System Tray).")
        else:
            self.quit_completely()

    def restore_from_tray(self):
        def _do_restore():
            self.master.deiconify()
            self.master.lift()
            self.master.focus_force()
        self.master.after(0, _do_restore)

    def quit_completely(self):
        def _do_quit():
            self.save_settings()
            self.stop_event.set()
            if self.tray_manager:
                self.tray_manager.stop()
            snap = self.shared.snapshot()
            set_vibration(snap["controller_index"], 0, 0)
            self.master.destroy()
        self.master.after(0, _do_quit)

    def on_closing(self):
        self.on_window_close_clicked()


if __name__ == "__main__":
    root = tk.Tk()
    app = VibrationApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
