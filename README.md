# 🎮 Xbox Audio Rumble Studio

<div align="center">

![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![XInput](https://img.shields.io/badge/Controller-XInput%20Compatible-107C10?style=for-the-badge&logo=xbox&logoColor=white)
![Flydigi](https://img.shields.io/badge/RGB%20Hardware-Flydigi%20Apex%20%2F%20Vader-FF6F00?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

**Biến toàn bộ âm thanh Windows thành phản hồi xúc giác Haptic chuẩn Sony DualSense trên mọi tay cầm XInput & Đồng bộ LED RGB phần cứng Flydigi.**

[Tính Năng](#-tính-năng-nổi-bật) •
[Yêu Cầu](#-yêu-cầu-hệ-thống) •
[Hướng Dẫn Sử Dụng](#-hướng-dẫn-sử-dụng) •
[Phím Tắt](#-phím-tắt-tiện-lợi) •
[Flydigi LED RGB](#-điều-khiển-led-rgb-tay-cầm-flydigi) •
[Khắc Phục Sự Cố](#-khắc-phục-sự-cố-thường-gặp)

</div>

---

## 📖 Giới Thiệu

**Xbox Audio Rumble Studio** là ứng dụng Windows cao cấp được thiết kế để nâng tầm trải nghiệm chơi game, xem phim và nghe nhạc. Ứng dụng bắt luồng âm thanh hệ thống thời gian thực thông qua công nghệ **WASAPI Loopback**, phân tích phổ tần số bằng **Fast Fourier Transform (FFT)**, và tái tạo cảm giác rung **phản hồi xúc giác (Haptic Feedback) chuẩn DualSense** trên các tay cầm Xbox và tay cầm chuẩn XInput.

Ngoài ra, ứng dụng tích hợp sẵn bộ giao tiếp phần cứng HID độc quyền, cho phép **đồng bộ hóa dải đèn LED RGB** trên các dòng tay cầm **Flydigi Apex (Apex 2, 3, 4, 5)** và **Flydigi Vader (Vader 3, 4 Pro)** theo nhịp rung hoặc tần số âm thanh thời gian thực.

---

## 🌟 Tính Năng Nổi Bật

### 1. Mô Phỏng Xúc Giác Chuẩn Sony DualSense (Haptic Emulation)
* **Tách 2 Motor phần cứng độc lập**:
  * **Motor Trái (Nặng - Sub-bass)**: Đảm nhận dải siêu trầm (20 - 380 Hz), mang lại chấn động uy lực, đầm chắc khi có tiếng nổ lớn, sấm sét hoặc gầm rú của động cơ xe.
  * **Motor Phải (Nhẹ - Treble/Crisp)**: Đảm nhận dải tần số cao giòn giã (1400 - 7500 Hz), tái tạo độ đanh thép của tiếng gõ cò súng, vỏ đạn rơi, tiếng va chạm kim loại, bước chân hay tiếng kính vỡ.
* **Công nghệ Overdrive Kick**: Triệt tiêu độ ì quán tính cơ học của motor rung truyền thống, tạo lực công kích tức thời (**Instant Attack 0 - 5ms**) giúp phản xạ chính xác theo từng phát bắn và va chạm dồn dập.
* **Active Braking (Phanh dứt khoát)**: Ngắt lực rung lập tức khi âm thanh kết thúc, loại bỏ hoàn toàn hiện tượng rung nhão hoặc đuôi rung kéo dài ngoài ý muốn.

### 2. Định Vị Âm Thanh Không Gian (Spatial Stereo Directional Rumble)
* Phân tích độc lập 2 kênh âm thanh **Trái / Phải**:
  * Tiếng súng nổ, bước chân kẻ địch hoặc xe vượt bên nào thì motor bên đó sẽ ưu tiên rung mạnh hơn tương ứng.
  * Tạo lợi thế chiến thuật cực lớn trong các tựa game bắn súng góc nhìn thứ nhất (FPS) hoặc game sinh tồn.

### 3. Tự Động Phân Loại Nội Dung (Smart Auto-Profile)
* Bộ nhận diện thời gian thực tự động chuyển đổi thuật toán theo nội dung đang phát:
  * **Game Haptic**: Tối ưu phản hồi sắc nét, dứt khoát cho hành động.
  * **Âm Nhạc (EDM / Rock)**: Bắt nhịp trống, tăng cường lực nảy của nhịp điệu (Rhythm Punch).
  * **ASMR / Giọng nói**: Rung vi mô tê mịn theo từng hơi thở và thì thầm.
  * **Phim ảnh**: Tối ưu kịch tính cho các đại cảnh cháy nổ.

### 4. Đồng Bộ Đèn LED RGB Phần Cứng Flydigi Độc Quyền
* Giao tiếp trực tiếp tầng phần cứng qua HID API (hỗ trợ cả **Cáp USB** và **Đầu thu USB Dongle 2.4GHz**).
* **Chế độ Đồng bộ âm thanh (Audio Reactive RGB)**:
  * *Tần số âm thanh*: Tự động chuyển đổi màu mượt mà từ Xanh ngọc Cyan (êm dịu) ➔ Tím / Magenta (giao tranh) ➔ Đỏ rực lửa (tiếng nổ lớn / Bass uy lực).
  * *Nhịp đập độ sáng (Pulse)*: Nhấp nháy cường độ sáng theo từng đợt rung.
* **Chế độ Màu tĩnh (Static Color)**: Chọn màu nhanh từ bảng 8 màu rực rỡ hoặc chọn mã màu RGB bất kỳ.

### 5. Chạy Ngầm Khay Hệ Thống (System Tray)
* Hỗ trợ thu nhỏ ứng dụng xuống khay hệ thống Windows (Taskbar Tray) khi nhấn nút đóng cửa sổ `[X]`.
* Menu chuột phải tiện lợi tại biểu tượng khay:
  * 🖥️ Mở bảng điều khiển
  * 🟢 Bật / Tắt độ rung tức thì (F9)
  * 🎛️ Chuyển nhanh giữa tất cả các cấu hình Preset
  * ❌ Thoát ứng dụng sạch sẽ

### 6. Tự Động Đổi Cấu Hình Theo Game (Auto Game Profile Switching)
* Tự động quét cửa sổ game đang hoạt động trên màn hình thời gian thực (Foreground Process Watcher).
* Tự động chuyển đổi sang cấu hình Haptic tương ứng ngay khi vào game (CS2, Valorant, Forza Horizon, Elden Ring, Black Myth: Wukong...).
* Tự động hoàn về cấu hình chuẩn khi thoát game về Desktop hoặc trình duyệt.
* Tích hợp **Hộp thoại Quản lý Game (Game Profile Manager)**:
  * ⚡ Thêm game 1-click trực tiếp từ danh sách các ứng dụng / game đang mở.
  * 📂 Duyệt file `.exe` tùy ý trên máy tính.
  * ⚙️ Tùy chỉnh Preset dự phòng khi thoát game.

### 7. Tách Riêng Nguồn Âm Thanh Theo Game (Per-Process Audio Isolation)
* Công nghệ **WASAPI Process Loopback** chuyên sâu: Cô lập 100% âm thanh từ tiến trình game đang chơi theo PID.
* Loại bỏ triệt để hiện tượng rung nhiễu do tiếng trò chuyện Discord, video YouTube chạy ngầm, hay nhạc trình duyệt web.
* **Cơ chế Fallback thông minh**: Khi game chưa có âm thanh (load màn hình, tạm dừng) hoặc khi Alt-Tab ra ngoài, ứng dụng tự động hoàn về âm thanh hệ thống để giữ nhịp rung liên tục; khi game phát tiếng trở lại, tự động tái kích hoạt cô lập.
* Dễ dàng chuyển đổi trực tiếp trên giao diện giữa `🎯 Tự động cô lập Game đang chơi` và `🔊 Toàn hệ thống Windows`.

### 8. Rung Độc Lập 2 Nút Cò LT/RT (Xbox Impulse & Flydigi Adaptive Triggers)
* **Điều khiển 4 mô tơ độc lập**: Tích hợp Windows Runtime `winrt-Windows.Gaming.Input` điều khiển trực tiếp 4 mô tơ (`LeftGrip`, `RightGrip`, `LeftTrigger`, `RightTrigger`) trên tay cầm Xbox One, Xbox Series X|S, Xbox Elite 2 với độ trễ < 2ms.
* **Giao thức HID cho Flydigi**: Tự động gửi gói tin cấu hình phản hồi lực cò servo cho các dòng tay cầm Flydigi Apex 3/4 và Vader 3/4 Pro.
* **Thuật toán DSP chuyên biệt**:
  - **Cò Phải (RT - Bắn/Ga)**: Phát xung giật đanh tức thì (Fast Impulse 20-35ms) theo tiếng súng và cú đấm/nổ.
  - **Cò Trái (LT - Phanh/Ngắm)**: Rung rần rãnh mịn theo phanh lốp rê trượt và tiếng gầm rú động cơ.
* **Cơ chế Auto-Blend**: Tự động hòa trộn lực rung của cò vào thân khi sử dụng tay cầm 2 mô tơ thông thường, không gây lỗi driver.

### 9. Luôn Rung Liên Tục Trong Background & Khi Alt-Tab (Win32 XInput Engine)
* Khắc phục triệt để chính sách ngắt rung của Windows: Sử dụng luồng Win32 `XInputSetState` hoạt động liên tục ở chế độ nền, đảm bảo tay cầm luôn rung mượt mà khi Alt-Tab, chuyển cửa sổ hoặc đang trong game.
* Tích hợp **Win32 Single-Instance Mutex** chống việc mở trùng lặp nhiều app ngầm gây xung đột tay cầm.

### 10. Giao Diện Người Dùng Hiện Đại (Dark Mode 100% Tiếng Việt)
* Thiết kế tối ưu hiển thị, trực quan với **9 phổ đo thời gian thực** (Tổng âm, Trầm/Nổ, Đanh/Súng, Nhịp điệu, Xung Kick, Motor Trái/Phải, Cò LT/RT).
* Nút bấm bật/tắt nguồn rung lớn trên Header chuyển màu Xanh/Đỏ trực quan.


---

## 🎛️ Bộ Cấu Hình Preset Sẵn Có

| Preset | Đặc điểm nổi bật | Phù hợp nhất cho |
| :--- | :--- | :--- |
| **✨ Chuẩn Xúc Giác Haptic DualSense** | Tách dải tần cân bằng, Overdrive Kick 0.8x, Active Braking dứt khoát. | Trải nghiệm toàn diện mọi tựa game |
| **🎮 Game Bắn Súng (FPS - Sắc Bén)** | Triệt tiêu tiếng gió nền, tăng âm đanh, phản hồi cò súng siêu tốc. | CS2, Valorant, COD, Apex Legends, Battlefield |
| **🏎️ Game Đua Xe (Racing - Tốc Độ)** | Motor trái gầm theo tua máy, motor phải tê giòn khi drift / lướt bánh. | Forza Horizon, Need for Speed, F1, Assetto Corsa |
| **⚔️ Game Nhập Vai & Hành Động (RPG)** | Đa lớp âm thanh cho bước chân, vung kiếm, kỹ năng và môi trường. | Elden Ring, Black Myth: Wukong, Cyberpunk 2077 |
| **🎵 Âm Nhạc Sôi Động (EDM / Rock)** | Bắt chặt nhịp trống (Beat Punch), dập Sub-bass cực sâu và uy lực. | Nghe nhạc điện tử, EDM, Rock, Pop |
| **🎙️ ASMR & Giọng Nói Thì Thầm** | Lọc bỏ tạp âm, rung vi mô siêu mịn màng theo hơi thở. | ASMR, Podcast, Livestream, Phim lãng mạn |
| **🎬 Phim Điện Ảnh & Bom Tấn** | Dải động rộng, tái hiện chấn động kịch tính như rạp chiếu phim. | Phim hành động, Marvel, bom tấn viễn tưởng |

---

## ⌨️ Phím Tắt Tiện Lợi

* **`F9` (Bàn phím)**: Bật / Tắt độ rung tức thì từ bất kỳ đâu.
* **`LB + RB` (Tay cầm)**: Bấm cùng lúc 2 nút vai trên tay cầm để Bật / Tắt rung ngay trong lúc chơi game mà không cần Alt+Tab ra màn hình ngoài.

---

## 💻 Yêu Cầu Hệ Thống

* **Hệ điều hành**: Windows 10 hoặc Windows 11 (64-bit).
* **Tay cầm hỗ trợ**:
  * Tất cả các dòng tay cầm **Xbox** (Xbox Series X/S, Xbox One, Xbox 360).
  * Mọi tay cầm bên thứ ba hỗ trợ chuẩn **XInput** (Flydigi, 8BitDo, Gamesir, Logitech, EasySMX...).
* **Phần cứng LED RGB (Tùy chọn)**:
  * Flydigi Apex 2, Apex 3, Apex 4, Apex 5.
  * Flydigi Vader 2, Vader 3, Vader 4 Pro.
  * Hỗ trợ kết nối qua **Cáp USB Type-C** hoặc **USB Wireless Dongle 2.4G**.
* **Thiết bị âm thanh**: Loa máy tính, tai nghe dây, tai nghe Bluetooth đang phát âm thanh trên Windows.

---

## 🚀 Hướng Dẫn Sử Dụng

### Cách 1: Sử dụng File Thực Thi (.exe) Tiện Lợi
1. Tải bản phát hành mới nhất.
2. Cắm tay cầm và thiết bị âm thanh vào máy tính.
3. Chạy trực tiếp file `XboxAudioRumbleStudio.exe` (chương trình dạng Portable, không cần cài đặt).
4. Chọn cấu hình Preset bạn mong muốn, bật âm thanh trong game/nhạc và tận hưởng độ rung Haptic!

### Cách 2: Chạy Từ Mã Nguồn Python
Yêu cầu đã cài đặt **Python 3.10+**:

```bash
# 1. Cài đặt các thư viện phụ thuộc
pip install numpy PyAudioWPatch psutil pyinstaller

# 2. Khởi chạy ứng dụng
python xbox6.py
```

### Cách 3: Tự Đóng Gói Lại File .exe
```bash
pyinstaller --noconfirm --onefile --windowed --icon=app.ico --name=XboxAudioRumbleStudio xbox6.py
```

---

## 💡 Điều Khiển LED RGB Tay Cầm Flydigi

Ứng dụng hỗ trợ nhận diện và điều khiển trực tiếp dải LED RGB của các dòng tay cầm Flydigi:
* **Hỗ trợ kết nối**: Tự động nhận diện cả khi cắm dây trực tiếp hoặc cắm qua USB Dongle 2.4GHz (`VID 04B4 / 37D7 / 2FD8`).
* **Lưu ý quan trọng**:
  * Để tránh xung đột cổng HID, vui lòng **Thoát phần mềm Flydigi Space Station** ở khay Taskbar trước khi bật đồng bộ LED trên Xbox Audio Rumble Studio.
  * Khi tay cầm được kết nối thành công, biểu tượng trạng thái sẽ hiển thị: `🟢 Đã kết nối Flydigi Apex`.

---

## ⚙️ Lưu Trữ Cấu Hình Tự Động

Mọi thông số bạn tùy chỉnh (Preset, Ngưỡng rung, Độ nhạy, Định vị Stereo, Màu sắc LED, Độ sáng) sẽ tự động lưu lại vào file `XboxAudioRumbleStudio.settings.json` ngay cạnh thư mục ứng dụng để áp dụng cho các lần khởi động tiếp theo.

---

## ❓ Khắc Phục Sự Cố Thường Gặp

<details>
<summary><b>1. Tay cầm không rung dù âm thanh đang phát?</b></summary>

* Kiểm tra nút nguồn lớn trên góc phải ứng dụng xem có đang ở trạng thái `🟢 RUNG: ĐANG BẬT` hay không (nhấn `F9` hoặc `LB+RB` để bật lại).
* Kiểm tra mục `Nguồn âm thanh`: đảm bảo đang chọn đúng thiết bị loa/tai nghe đang phát tiếng.
* Bấm nút `⚡ Tự động hiệu chuẩn` để ứng dụng tự đo mức nhiễu nền môi trường và thiết lập lại ngưỡng rung tối ưu.
* Bấm nút `🎮 Kiểm tra rung` để chắc chắn motor tay cầm hoạt động bình thường.
</details>

<details>
<summary><b>2. Đèn LED Flydigi báo "⚪ Đang quét tay cầm Apex / Dongle..."?</b></summary>

* Hãy chắc chắn rằng bạn đã **bật nguồn tay cầm** (tay cầm chưa đi vào chế độ ngủ).
* Kiểm tra đầu thu USB Dongle 2.4G hoặc cáp kết nối đã được cắm chắc chắn vào máy tính.
* Đảm bảo phần mềm **Flydigi Space Station** đã được tắt hoàn toàn để không chiếm quyền cổng HID độc quyền.
</details>

<details>
<summary><b>3. Rung bị rè hoặc rung liên tục không ngừng?</b></summary>

* Bật tùy chọn `Bộ lọc thích ứng ngưỡng nền` trong panel Chế độ.
* Tăng nhẹ thông số `Ngưỡng rung` lên (ví dụ từ 120 lên 180 - 220) hoặc bấm nút `⚡ Tự động hiệu chuẩn`.
</details>

---

## 📄 Bản Quyền & Tuyên Bố Miễn Trừ

* Phần mềm được phát hành theo giấy phép mã nguồn mở **MIT License**.
* DualSense là thương hiệu đã đăng ký của Sony Interactive Entertainment Inc. Xbox là thương hiệu của Microsoft Corp. Flydigi là thương hiệu của Shanghai Flydigi Electronics Technology Co., Ltd. Dự án này là công cụ độc lập của cộng đồng và không liên kết với các công ty trên.
