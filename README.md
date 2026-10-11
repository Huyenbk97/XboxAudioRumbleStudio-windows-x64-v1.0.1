# Xbox Audio Rumble Studio - Chuẩn Xúc Giác Haptic DualSense

**Xbox Audio Rumble Studio** là ứng dụng Windows biến toàn bộ âm thanh hệ thống (game, phim, nhạc, ASMR) thành độ rung phản hồi xúc giác chân thực trên tay cầm chuẩn XInput (Xbox Series X/S, Xbox One, Xbox 360 và các tay cầm hỗ trợ XInput). 

Ứng dụng bắt luồng âm thanh thời gian thực thông qua WASAPI loopback, phân tích 4 dải tần số chuyên biệt và tái tạo cảm giác rung **chuẩn haptic như DualSense của Sony**.

---

## 🌟 Tính Năng Mới & Đột Phá Haptic

- **Mô phỏng Xúc Giác Chuẩn Sony DualSense (Haptic Emulation)**:
  - **Tách 2 Motor chuẩn phần cứng**: Motor Trái (nặng) đánh dải Sub-bass & chấn động lớn (tiếng nổ, động cơ xe); Motor Phải (nhẹ) rung tần số cao giòn giã (tiếng súng gõ, lách cách kim loại, bước chân, tiếng kính vỡ).
  - **Công nghệ Overdrive Kick**: Triệt tiêu độ ì quán tính của motor truyền thống, tạo phản hồi tức thì (instant attack 0-5ms) cho từng phát súng, va chạm và tiếng nổ dồn dập.
  - **Active Braking (Phanh dứt khoát)**: Ngắt rung lập tức khi dứt âm thanh, loại bỏ cảm giác rung nhũn hoặc đuôi rung kéo dài ngoài ý muốn.
- **Định vị không gian Stereo (Spatial Directional Rumble)**: Phân tích 2 kênh âm thanh Trái/Phải độc lập. Tiếng súng hoặc tiếng bước chân bên nào thì tay cầm bên đó rung phản hồi tương ứng.
- **Bộ Preset chuyên biệt cho từng thể loại Game & Trải nghiệm**:
  - `✨ Chuẩn Xúc Giác Haptic DualSense`: Tối ưu toàn diện, mô phỏng chân thật nhất dải tần số xúc giác.
  - `🎮 Game Bắn Súng (FPS - Sắc Bén)`: Phản hồi tức thì từng viên đạn, vỏ đạn rơi, lọc sạch tiếng gió nền.
  - `🏎️ Game Đua Xe (Racing - Tốc Độ)`: Motor trái gầm theo tua máy, motor phải rung tê khi lướt bánh / va quẹt.
  - `⚔️ Game Nhập Vai & Hành Động (RPG)`: Đa lớp âm thanh cho bước chân, vung kiếm và kỹ năng.
  - `🎵 Âm Nhạc Sôi Động (EDM/Rock)`: Dập nhịp trống và bass uy lực.
  - `🎙️ ASMR & Giọng Nói Thì Thầm`: Rung vi mô tê mịn theo hơi thở và âm thanh nhỏ.
  - `🎬 Phim Điện Ảnh & Bom Tấn`: Chấn động kịch tính và sống động.
- **Phổ đo thời gian thực trực quan**: Theo dõi trực quan Tổng âm lượng, Âm trầm (Trái), Âm đanh (Phải), Nhịp điệu, Xung Overdrive Kick và công suất 2 Motor.
- **Điều Khiển Đèn LED RGB Tay Cầm Flydigi Apex (Apex 2, 3, 4, 5)**:
  - Tự động nhận diện phần cứng Flydigi Apex không cần cài đặt phần mềm bên thứ ba.
  - Hỗ trợ chế độ **Đồng bộ âm thanh (Audio Reactive RGB)**: Đổi màu theo dải tần (Xanh -> Tím -> Đỏ khi có tiếng nổ lớn/bass) hoặc nhấp nháy độ sáng (Pulse) theo nhịp rung.
  - Chế độ **Màu tĩnh (Static Color)**: Chọn nhanh bảng màu rực rỡ hoặc chọn màu tùy ý qua bảng mã màu RGB.
  - Điều chỉnh thanh độ sáng LED và ô đèn LED ảo mô phỏng trực tiếp trên giao diện.
- **Giao diện Tiếng Việt 100%**: Thiết kế Dark Mode hiện đại, trực quan, có **Nút bấm Bật/Tắt rung lớn trên Header (đổi màu xanh/đỏ)**, hỗ trợ phím tắt bàn phím `F9` và phím tắt tay cầm `LB + RB`.

---

## 💻 Yêu Cầu Hệ Thống

- Hệ điều hành: Windows 10 / Windows 11 (64-bit)
- Tay cầm: Tay cầm Xbox (One, Series X/S, 360) hoặc bất kỳ tay cầm nào hỗ trợ XInput
- Thiết bị phát âm thanh: Loa hoặc tai nghe đang phát âm thanh trên Windows

---

## 🚀 Hướng Dẫn Sử Dụng

1. Kết nối tay cầm với máy tính.
2. Mở file `XboxAudioRumbleStudio.exe` (hoặc chạy lệnh `python xbox6.py`).
3. Chọn cấu hình preset phù hợp với tựa game hoặc nội dung bạn đang thưởng thức.
4. Bật âm thanh trong game / trình phát nhạc và cảm nhận độ rung chi tiết trên tay cầm!

---

## ⚙️ Lưu Trữ Cài Đặt

Mọi tinh chỉnh sẽ tự động lưu lại vào file `xbox6.settings.json` (hoặc `XboxAudioRumbleStudio.settings.json`) ngay cạnh ứng dụng để tự động áp dụng trong các lần mở sau.
