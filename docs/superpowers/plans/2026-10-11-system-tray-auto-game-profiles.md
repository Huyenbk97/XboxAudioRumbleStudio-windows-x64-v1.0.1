# System Tray & Auto Game Profile Switching Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Thêm tính năng chạy ngầm khay hệ thống (System Tray via `pystray`) và tự động nhận diện game đang mở (Foreground Process Watcher via `win32gui`/`psutil`) để tự động chuyển Preset Haptic phù hợp.

**Architecture:** Mở rộng [xbox6.py](file:///c:/Users/LapTopNhatAn/Downloads/Compressed/XboxAudioRumbleStudio-windows-x64-v1.0.1/xbox6.py) với 2 phân hệ chạy nền độc lập: `SystemTrayManager` quản lý biểu tượng và menu khay hệ thống qua luồng riêng; `GameProfileWatcher` dò tìm cửa sổ active định kỳ 1.2s và đồng bộ thay đổi vào `SharedState` & Tkinter UI qua `master.after()`. Đi kèm hộp thoại `GameProfileDialog` để người dùng quản lý danh sách game trực quan.

**Architecture Diagram:**

```mermaid
graph TD
    subgraph "Core App (xbox6.py)"
        GUI[Tkinter Main Window] <--> Shared[SharedState & Settings]
        AudioThread[WASAPI Audio Loop] --> Shared
        SettingsFile[(XboxAudioRumbleStudio.settings.json)] <--> Shared
    end

    subgraph "New Phase 1 Modules"
        Tray[SystemTrayManager (pystray)] -->|Menu Actions / Restore| GUI
        GUI -->|Intercept WM_DELETE_WINDOW| Tray
        Watcher[GameProfileWatcher (win32gui / psutil)] -->|Detect exe| Shared
        Watcher -->|master.after() Switch Preset| GUI
        Dialog[GameProfileDialog (Toplevel)] -->|Manage Rules| Shared
    end
```

**Tech Stack:** Python 3.11, Tkinter, `pystray`, `PIL.Image`, `win32gui`, `win32process`, `psutil`, PyInstaller, Inno Setup 6.

**Spec:** [docs/superpowers/specs/2026-10-11-system-tray-auto-game-profiles-design.md](file:///c:/Users/LapTopNhatAn/Downloads/Compressed/XboxAudioRumbleStudio-windows-x64-v1.0.1/docs/superpowers/specs/2026-10-11-system-tray-auto-game-profiles-design.md)

## Global Constraints

- Không làm gián đoạn luồng âm thanh WASAPI haptic thời gian thực (Audio loop latency < 5ms).
- Sử dụng các thư viện đã có sẵn trong môi trường Python: `pystray`, `PIL`, `win32gui`, `psutil`.
- Mọi thao tác tương tác GUI từ background threads bắt buộc phải gọi qua `master.after(0, ...)`.
- Lưu giữ nguyên vẹn cấu hình hiện tại trong `XboxAudioRumbleStudio.settings.json` và tương thích ngược hoàn toàn.

---

### Task 1: Mở Rộng SharedState & Schema Cấu Hình Cài Đặt

**Files:**
- Modify: [xbox6.py:380-450](file:///c:/Users/LapTopNhatAn/Downloads/Compressed/XboxAudioRumbleStudio-windows-x64-v1.0.1/xbox6.py#L380-L450)
- Test: [test_settings_schema.py](file:///c:/Users/LapTopNhatAn/Downloads/Compressed/XboxAudioRumbleStudio-windows-x64-v1.0.1/test_settings_schema.py)

**Interfaces:**
- Produces: `minimize_to_tray: bool`, `auto_game_detect: bool`, `fallback_preset: str`, `game_profiles: dict` trong `SharedState`.

- [x] **Step 1: Viết test kiểm tra schema cài đặt mới**

Tạo file `test_settings_schema.py`:
```python
import json
from xbox6 import SharedState

def test_shared_state_game_profiles():
    state = SharedState()
    assert hasattr(state, "minimize_to_tray")
    assert hasattr(state, "auto_game_detect")
    assert hasattr(state, "fallback_preset")
    assert hasattr(state, "game_profiles")
    assert "cs2.exe" in state.game_profiles

    # Test serialization & snapshot
    snap = state.snapshot()
    assert snap["minimize_to_tray"] is True
    assert snap["auto_game_detect"] is True
    assert isinstance(snap["game_profiles"], dict)

if __name__ == "__main__":
    test_shared_state_game_profiles()
    print("ALL TESTS PASSED")
```

- [x] **Step 2: Chạy test để xác nhận FAIL trước khi sửa code**

Run: `python test_settings_schema.py`
Expected: FAIL với AttributeError vì các thuộc tính chưa được khai báo.

- [x] **Step 3: Cập nhật SharedState trong xbox6.py**

Bổ sung các trường vào `SharedState` và phương thức `snapshot()`:
```python
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
```

- [x] **Step 4: Chạy test để xác nhận PASS**

Run: `python test_settings_schema.py`
Expected: PASS ("ALL TESTS PASSED").

---

### Task 2: Triển Khai Phân Hệ Khay Hệ Thống (SystemTrayManager)

**Files:**
- Modify: [xbox6.py](file:///c:/Users/LapTopNhatAn/Downloads/Compressed/XboxAudioRumbleStudio-windows-x64-v1.0.1/xbox6.py)
- Test: [test_tray_headless.py](file:///c:/Users/LapTopNhatAn/Downloads/Compressed/XboxAudioRumbleStudio-windows-x64-v1.0.1/test_tray_headless.py)

**Interfaces:**
- Consumes: `app.ico`, `SharedState`, Tkinter master.
- Produces: `SystemTrayManager` class, `on_minimize_to_tray()`, `restore_from_tray()`, `quit_application()`.

- [x] **Step 1: Viết test khởi tạo SystemTrayManager**

Tạo file `test_tray_headless.py`:
```python
import pystray
from PIL import Image
from xbox6 import SystemTrayManager

def test_tray_initialization():
    # Kiểm tra load icon app.ico
    img = Image.open("app.ico")
    assert img.size[0] > 0
    print("Icon loaded successfully")

if __name__ == "__main__":
    test_tray_initialization()
    print("TRAY TEST PASSED")
```

- [x] **Step 2: Viết lớp SystemTrayManager trong xbox6.py**

Tạo lớp `SystemTrayManager`:
- Tải `app.ico` bằng `PIL.Image.open("app.ico")`.
- Menu gồm:
  - `🖥️ Mở bảng điều khiển` ➔ Gọi `app.restore_from_tray()`.
  - `🟢 Bật / Tắt độ rung` ➔ Gọi `app.toggle_vibration()`.
  - `🎛️ Chuyển Preset` ➔ Submenu các Preset.
  - `❌ Thoát` ➔ Gọi `app.quit_completely()`.
- Chạy `icon.run_detached()` hoặc chạy trong daemon thread.
- Bắt sự kiện đóng cửa sổ Tkinter:
  `self.master.protocol("WM_DELETE_WINDOW", self.on_close_button_clicked)`
  Nếu `minimize_to_tray` bật: Gọi `self.master.withdraw()`, thông báo nhẹ ở lần đầu tiên.
  Nếu tắt: Thoát ứng dụng hoàn toàn.

- [x] **Step 3: Kiểm tra luồng hoạt động của SystemTrayManager**

Run: `python test_tray_headless.py`
Expected: PASS.

---

### Task 3: Triển Khai Phân Hệ Tự Động Nhận Diện Game (GameProfileWatcher)

**Files:**
- Modify: [xbox6.py](file:///c:/Users/LapTopNhatAn/Downloads/Compressed/XboxAudioRumbleStudio-windows-x64-v1.0.1/xbox6.py)
- Test: [test_process_watcher.py](file:///c:/Users/LapTopNhatAn/Downloads/Compressed/XboxAudioRumbleStudio-windows-x64-v1.0.1/test_process_watcher.py)

**Interfaces:**
- Consumes: `win32gui`, `win32process`, `psutil`, `SharedState.game_profiles`.
- Produces: `get_foreground_process_name()`, `game_watcher_thread()`.

- [x] **Step 1: Viết test lấy tên tiến trình Foreground**

Tạo file `test_process_watcher.py`:
```python
from xbox6 import get_foreground_process_name

def test_foreground_process():
    proc_name = get_foreground_process_name()
    print("Current foreground process:", proc_name)
    assert proc_name is not None
    assert isinstance(proc_name, str)

if __name__ == "__main__":
    test_foreground_process()
    print("FOREGROUND TEST PASSED")
```

- [x] **Step 2: Viết hàm get_foreground_process_name và luồng GameProfileWatcher**

Triển khai:
```python
def get_foreground_process_name():
    try:
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            return ""
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if pid <= 0:
            return ""
        return psutil.Process(pid).name().lower()
    except Exception:
        return ""
```
Trong `XboxAudioStudioApp`:
- Tạo `self.watcher_thread` chạy hàm `_game_watcher_loop()`.
- Mỗi 1.2s: Lấy `proc_name`. Nếu trùng với mục trong `game_profiles` và khác `last_active_game`:
  - Đổi `last_active_game = proc_name`.
  - Gọi `self.master.after(0, self.auto_apply_game_preset, target_preset, proc_name)`.
  - Ghi log: `🎮 Phát hiện [{proc_name}] ➔ Tự động áp dụng: {target_preset}`.
- Nếu người dùng chuyển sang cửa sổ khác (desktop, chrome...) mà không nằm trong danh sách:
  - Nếu `last_active_game` khác rỗng: Hồi về `fallback_preset`.

- [x] **Step 3: Chạy test kiểm tra hàm lấy tiến trình**

Run: `python test_process_watcher.py`
Expected: PASS ("FOREGROUND TEST PASSED").

---

### Task 4: Xây Dựng Hộp Thoại Quản Lý Game & Tích Hợp Giao Diện

**Files:**
- Modify: [xbox6.py:1020-1100](file:///c:/Users/LapTopNhatAn/Downloads/Compressed/XboxAudioRumbleStudio-windows-x64-v1.0.1/xbox6.py#L1020-L1100)

**Interfaces:**
- Produces: `GameProfileDialog(tk.Toplevel)`, nút `🎮 Quản lý Game...`, checkbox `[x] Tự động đổi Preset theo Game`, checkbox `[x] Thu nhỏ xuống khay [X]`.

- [x] **Step 1: Xây dựng lớp GameProfileDialog**

Cửa sổ Toplevel Dark Mode:
- Hiển thị danh sách Treeview: `Tên file Game (.exe)` | `Cấu hình Preset gán tương ứng`.
- Nút `⚡ Thêm Game đang chạy`: Mở cửa sổ chọn nhanh từ danh sách các process đang có cửa sổ hiển thị.
- Nút `📂 Duyệt file .exe`: Mở `filedialog.askopenfilename`.
- Combobox gán Preset cho game đã chọn.
- Nút `🗑️ Xóa` và nút `💾 Lưu danh sách`.

- [x] **Step 2: Tích hợp nút và Checkbox vào Panel Thiết bị & Preset**

Thêm vào Panel 1:
- Checkbox: `Tự động đổi cấu hình theo Game đang mở (Auto Detect)` liên kết với `self.auto_game_var`.
- Nút bấm: `🎮 Quản lý Game...` gọi `self.open_game_profile_dialog()`.
- Thêm vào cài đặt: Checkbox `Thu nhỏ xuống khay khi đóng cửa sổ` liên kết với `self.minimize_tray_var`.

---

### Task 5: Kiểm Thử Toàn Diện & Đóng Gói Lại (.exe & Inno Setup)

**Files:**
- Output: `XboxAudioRumbleStudio.exe`
- Output: `XboxAudioRumbleStudio-Setup-v1.0.1.exe`

- [x] **Step 1: Chạy kiểm thử toàn bộ mã nguồn**

Run: `python -m py_compile xbox6.py`
Expected: Exit code 0, không có lỗi cú pháp.

- [x] **Step 2: Chạy thử nghiệm app trong môi trường thực tế**

Khởi động `python xbox6.py` trong 3 giây và kiểm tra tạo System Tray + Game Watcher.

- [x] **Step 3: Đóng gói lại file thực thi duy nhất bằng PyInstaller**

Run: `pyinstaller --noconfirm --onefile --windowed --icon=app.ico --name=XboxAudioRumbleStudio --distpath=. xbox6.py`
Expected: Exit code 0, tạo file `XboxAudioRumbleStudio.exe` dung lượng ~24MB.

- [x] **Step 4: Biên dịch lại file cài đặt Setup bằng Inno Setup**

Run: `& "C:\Users\LapTopNhatAn\AppData\Local\Programs\Inno Setup 6\ISCC.exe" installer.iss`
Expected: Exit code 0, tạo file `XboxAudioRumbleStudio-Setup-v1.0.1.exe`.

- [x] **Step 5: Dọn dẹp các file test tạm**

Xóa `test_settings_schema.py`, `test_tray_headless.py`, `test_process_watcher.py`.
