# Thiết Kế Kỹ Thuật: Phase 1 - Khay Hệ Thống & Tự Động Nhận Diện Game

- **Dự án**: Xbox Audio Rumble Studio
- **Phiên bản mục tiêu**: v1.1.0 (Phase 1)
- **Tác giả**: Huyenbk97 & Antigravity
- **Ngày lập**: 11/10/2026
- **Trạng thái**: Đã phê duyệt ý tưởng (Approved Design)

---

## 1. Mục Tiêu & Phạm Vi (Goals & Scope)

### 1.1. Mục tiêu
1. **Chạy ngầm tiện lợi (System Tray)**: Cho phép thu nhỏ ứng dụng xuống khay hệ thống Windows (Taskbar Tray), giải phóng không gian màn hình khi chơi game, hỗ trợ menu chuột phải điều khiển nhanh.
2. **Tự động hóa thông minh (Auto Game Profile)**: Tự động phát hiện game đang mở ở cửa sổ chính (Foreground) và chuyển đổi sang cấu hình Haptic Preset tối ưu nhất cho game đó mà không cần người dùng thao tác thủ công.

### 1.2. Ngoài phạm vi Phase 1 (Sẽ làm ở Phase sau)
- Lọc âm thanh riêng từng tiến trình (Per-Process WASAPI loopback - Phase 2).
- Rung cò LT/RT Xbox & Flydigi Force feedback (Phase 3).
- Bộ chỉnh Visual Equalizer (Phase 4).

---

## 2. Kiến Trúc & Thiết Kế Thành Phần (Component Architecture)

### 2.1. Phân hệ Khay Hệ Thống (`SystemTrayManager`)
* **Thư viện sử dụng**: `pystray` + `PIL.Image`.
* **Luồng hoạt động**:
  * Chạy trên một background thread chuyên biệt (`tray_thread`).
  * Sử dụng icon `app.ico` có sẵn trong thư mục ứng dụng.
  * Lắng nghe sự kiện click trái / double click để khôi phục cửa sổ (`self.master.deiconify()`).
* **Menu chuột phải (Context Menu)**:
  * `🖥️ Mở bảng điều khiển`: Gọi `deiconify()` và đưa cửa sổ lên đầu (`lift()`).
  * `🟢 / 🔴 Độ rung: Đang Bật / Tắt`: Đổi trạng thái rung của app thời gian thực.
  * `🎛️ Chuyển Preset`: Menu con liệt kê tất cả các Preset hiện có.
  * `❌ Thoát ứng dụng`: Dừng toàn bộ tiến trình và thoát sạch sẽ.
* **Xử lý sự kiện cửa sổ (Window Interception)**:
  * Bắt sự kiện `WM_DELETE_WINDOW` (khi bấm nút X): Nếu bật cài đặt `minimize_to_tray`, gọi `self.master.withdraw()` thay vì thoát chương trình.
  * Thêm nút hoặc tùy chọn trong cài đặt: `[x] Thu nhỏ xuống khay hệ thống khi đóng cửa sổ`.

### 2.2. Phân hệ Tự Động Nhận Diện Game (`GameProfileWatcher`)
* **Thư viện sử dụng**: `win32gui`, `win32process`, `psutil`.
* **Luồng quét**:
  * Chạy trong một background daemon thread định kỳ mỗi `1.2 giây`.
  * Lấy handle cửa sổ active qua `GetForegroundWindow()`.
  * Lấy Process ID qua `GetWindowThreadProcessId(hwnd)`.
  * Lấy tên file thực thi qua `psutil.Process(pid).name().lower()`.
* **Cơ chế so khớp và chuyển đổi**:
  * Kiểm tra tên file `.exe` trong từ điển cấu hình `game_profiles`.
  * Nếu trùng khớp và khác với game hiện tại:
    1. Cập nhật `active_game_process = exe_name`.
    2. Chuyển đổi preset hiện tại sang preset được gán cho game đó.
    3. Gửi thông báo vào nhật ký hoạt động (`log_queue`).
    4. Cập nhật giao diện Tkinter qua `master.after(...)`.
  * Nếu rời khỏi game về Desktop/trình duyệt: Tự động chuyển về `fallback_preset` (mặc định là `✨ Chuẩn Xúc Giác Haptic DualSense`).

### 2.3. Cửa Sổ Quản Lý Cấu Hình Game (`GameProfileDialog`)
* Cửa sổ phụ (`tk.Toplevel`) gồm:
  * Bảng hiển thị danh sách Game (.exe) ➔ Preset.
  * Nút `➕ Thêm Game đang chạy`: Mở popup liệt kê các tiến trình có cửa sổ đang chạy để người dùng click chọn ngay lập tức.
  * Nút `📂 Duyệt file .exe`: Mở `filedialog.askopenfilename(filetypes=[("Executable", "*.exe")])`.
  * Combobox chọn Preset muốn gán cho game đó.
  * Nút `🗑️ Xóa` và nút `💾 Lưu cài đặt`.

---

## 3. Cấu Trúc Dữ Liệu Cài Đặt (Configuration Schema)

Cập nhật trong file `XboxAudioRumbleStudio.settings.json`:

```json
{
  "minimize_to_tray": true,
  "auto_game_detect": true,
  "fallback_preset": "✨ Chuẩn Xúc Giác Haptic DualSense",
  "game_profiles": {
    "cs2.exe": "🎮 Game Bắn Súng (FPS - Sắc Bén)",
    "valorant-win64-shipping.exe": "🎮 Game Bắn Súng (FPS - Sắc Bén)",
    "forzahorizon5.exe": "🏎️ Game Đua Xe (Racing - Tốc Độ)",
    "eldenring.exe": "⚔️ Game Nhập Vai & Hành Động (RPG)",
    "blackmythwukong.exe": "⚔️ Game Nhập Vai & Hành Động (RPG)",
    "spotify.exe": "🎵 Âm Nhạc Sôi Động (EDM/Rock)"
  }
}
```

---

## 4. Xử Lý Ngoại Lệ & An Toàn Luồng (Error Handling & Concurrency)

1. **An toàn tiến trình bị tắt đột ngột**: Khi lấy process name từ `psutil`, bọc trong khối `try ... except (psutil.NoSuchProcess, psutil.AccessDenied): continue`.
2. **Đảm bảo không xung đột giao diện**: Mọi thao tác từ `GameProfileWatcher` và `SystemTrayManager` tác động lên Tkinter GUI đều gọi qua `master.after(0, ...)`.
3. **Thoát an toàn (Graceful Shutdown)**: Khi người dùng chọn thoát ứng dụng từ Tray Menu, gọi cờ `stop_event.set()`, đóng tray icon bằng `icon.stop()`, tắt luồng watcher, dừng luồng âm thanh rồi mới gọi `master.destroy()`.

---

## 5. Kế Hoạch Kiểm Thử & Xác Minh (Verification Plan)

1. **Kiểm thử System Tray**:
   - Khởi động app ➔ Thu nhỏ bằng nút `X` ➔ Kiểm tra cửa sổ biến mất và icon xuất hiện ở góc Tray.
   - Click chuột phải ➔ Bấm Bật/Tắt rung ➔ Kiểm tra phản hồi trong app.
   - Click đúp vào icon ➔ Kiểm tra cửa sổ chính phục hồi nguyên vẹn.
2. **Kiểm thử Nhận diện Game**:
   - Thêm `notepad.exe` gán với Preset `🎵 Âm Nhạc Sôi Động (EDM/Rock)`.
   - Mở Notepad và click vào Notepad ➔ Kiểm tra log app tự động chuyển sang Preset EDM/Rock.
   - Click ra Desktop ➔ Kiểm tra app tự động hồi về Preset mặc định DualSense.
3. **Kiểm thử đóng gói lại (.exe và Inno Setup)**:
   - Chạy PyInstaller kiểm tra không lỗi import `pystray`, `PIL`, `psutil`.
   - Biên dịch lại bộ cài `XboxAudioRumbleStudio-Setup-v1.0.1.exe`.
