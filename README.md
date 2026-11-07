# 🎵 Discord Music Bot (Lavalink v4 + discord.py + Wavelink)

Discord Music Bot hiệu năng cao, âm thanh mượt mà, hỗ trợ phát nhạc từ YouTube (với YouTube OAuth chống chặn IP/rate limit) và SoundCloud.

---

## 🚀 Tính năng nổi bật
* **Kiến trúc Lavalink v4**: Xử lý giải mã và stream âm thanh Opus trực tiếp qua UDP, không gây nghẽn tiến trình bot, không giật lag.
* **YouTube OAuth**: Tích hợp plugin YouTube với OAuth chống chặn IP và bot-detection từ YouTube.
* **Đa máy chủ (Multi-guild)**: Chạy độc lập trên nhiều Discord Server khác nhau với hàng đợi (Queue) riêng biệt.
* **Giao diện Slash Commands trực quan**: Đầy đủ thanh tiến trình bài hát, ảnh thumbnail, danh sách hàng đợi.
* **Tự động tiết kiệm tài nguyên**: Tự động dọn dẹp hàng đợi và rời kênh thoại khi không còn người nghe.
* **Đóng gói Docker hoàn chỉnh**: Chạy ngầm trong nền, tự khởi động lại khi máy tính bật, quản lý RAM/CPU nhẹ nhàng (< 1GB tổng thể).

---

## 📋 Danh sách Lệnh (Slash Commands)

| Lệnh | Mô tả |
| :--- | :--- |
| `/play <query>` | Phát nhạc từ URL hoặc tìm kiếm tên bài hát (mặc định tìm YouTube) |
| `/skip` | Bỏ qua bài hát đang phát |
| `/pause` | Tạm dừng bài hát |
| `/resume` | Tiếp tục phát bài hát |
| `/stop` | Dừng phát nhạc, xóa hàng đợi và rời khỏi kênh thoại |
| `/queue` | Xem danh sách bài hát đang chờ trong hàng đợi |
| `/nowplaying` | Xem chi tiết bài hát đang phát và thanh tiến trình |
| `/volume <1-100>`| Tùy chỉnh âm lượng |
| `/loop [mode]`   | Cài đặt lặp lại: bài hiện tại, toàn bộ hàng đợi hoặc tắt lặp |
| `/join` | Mời bot vào kênh thoại của bạn |
| `/leave` | Cho bot rời khỏi kênh thoại |

---

## 🛠️ Hướng dẫn Cài đặt & Khởi chạy

### Bước 1: Tạo Bot trên Discord Developer Portal
1. Truy cập [Discord Developer Portal](https://discord.com/developers/applications) -> Chọn **New Application** -> Đặt tên cho bot.
2. Vào mục **Bot** ở thanh bên trái:
   - Nhấn **Reset Token** -> Sao chép chuỗi Token này.
   - Tại mục **Privileged Gateway Intents**: Bật **Server Members Intent** (nếu cần).
3. Vào mục **OAuth2** -> **URL Generator**:
   - Tích chọn scopes: `bot`, `applications.commands`.
   - Tích chọn Bot Permissions: `Send Messages`, `Embed Links`, `Connect`, `Speak`, `Use Voice Activity`.
   - Sao chép đường link invite ở cuối trang và dán vào trình duyệt để thêm bot vào server Discord của bạn.

### Bước 2: Cấu hình File `.env`
Mở file `.env` trong thư mục dự án và điền Token của bạn:
```env
DISCORD_TOKEN=điền_token_vừa_lấy_ở_bước_1_vào_đây
LAVALINK_URI=http://lavalink:2333
LAVALINK_PASSWORD=youshallnotpass
```

### Bước 3: Khởi động Lavalink & Xác thực YouTube OAuth
1. Đảm bảo **Docker Desktop** đã được bật trên máy tính.
2. Mở file `manage.bat` (hoặc mở PowerShell) và chọn khởi động Lavalink:
   ```powershell
   docker compose up -d lavalink
   docker compose logs -f lavalink
   ```
3. Trong màn hình log, bạn sẽ thấy thông báo:
   ```text
   Go to https://www.google.com/device and enter code XXXX-XXXX
   ```
4. Truy cập liên kết trên, đăng nhập tài khoản Google của bạn và nhập mã để xác thực. Sau khi xong, token sẽ được lưu vĩnh viễn trong thư mục `plugins/`. Nhấn `Ctrl + C` để thoát màn hình log.

### Bước 4: Khởi chạy Toàn bộ Bot
Chỉ cần chạy lệnh sau (hoặc chọn mục **1** trong `manage.bat`):
```powershell
docker compose up -d --build
```
Kiểm tra log của Bot:
```powershell
docker compose logs -f bot
```
Khi thấy dòng log `Bot đã online: ...` và `Đã đồng bộ ... Slash commands lên Discord`, bot đã sẵn sàng để phát nhạc!

---

## ⚙️ Quản lý & Tắt Bot
* **Xem logs:** `docker compose logs -f`
* **Tắt bot hoàn toàn:** `docker compose down` (hoặc chọn mục 4 trong `manage.bat`)
* **Khởi động lại:** `docker compose restart`
