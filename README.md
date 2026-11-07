# 🎵 Discord Music Bot (Lavalink v4 + discord.py + Wavelink 3.x)

Discord Music Bot hiệu năng cao, âm thanh mượt mà, hỗ trợ phát nhạc từ **YouTube** và **SoundCloud**. 

Hỗ trợ 2 phương thức khởi chạy linh hoạt: **Docker Compose** (đóng gói tiện lợi) và **Native Mode** (siêu tiết kiệm RAM, lý tưởng cho máy yếu).

---

## 🚀 Tính năng nổi bật
* **Kiến trúc Lavalink v4**: Xử lý giải mã và stream âm thanh Opus trực tiếp qua UDP, không gây nghẽn tiến trình bot, không giật lag.
* **Hỗ trợ 2 chế độ vận hành**:
  * 🐳 **Docker Mode**: Quản lý đa container gọn gàng, cách ly môi trường.
  * ⚡ **Native Mode**: Tiêu thụ vỏn vẹn **~300 MB RAM**, không cần bật máy ảo WSL 2, tiết kiệm hơn **2.5 GB RAM** cho máy tính
* **YouTube Playback Ổn định**: Tích hợp Plugin YouTube cập nhật mới nhất (hỗ trợ client iOS & TV), vượt qua các rào cản bot-detection của YouTube.
* **Đa máy chủ (Multi-guild)**: Chạy độc lập trên nhiều server Discord cùng lúc với hàng đợi (Queue) riêng biệt.
* **Giao diện Slash Commands trực quan**: Đầy đủ thanh tiến trình bài hát, ảnh bìa, âm lượng, chế độ lặp lại.
* **Tự động dọn dẹp**: Tự động rời phòng thoại và xóa hàng đợi sau 30 giây khi không còn người nghe trong phòng.

---

## 📋 Danh sách Lệnh (Slash Commands)

| Lệnh | Mô tả |
| :--- | :--- |
| `/play <query>` | Phát nhạc từ liên kết hoặc tìm kiếm tên bài hát (mặc định tìm YouTube Music/YouTube) |
| `/loop [mode]`   | Chế độ lặp lại: Lặp bài hiện tại (Track), lặp cả danh sách (Queue) hoặc Tắt lặp (Off) |
| `/pause` | Tạm dừng bài hát đang phát |
| `/resume` | Tiếp tục phát bài hát |
| `/skip` | Bỏ qua bài hát hiện tại |
| `/stop` | Dừng phát nhạc, xóa sạch hàng đợi và rời khỏi kênh thoại |
| `/queue [page]` | Xem danh sách hàng đợi (hỗ trợ phân trang) |
| `/nowplaying` | Xem chi tiết bài hát đang phát cùng thanh tiến trình trực quan |
| `/volume <1-100>`| Tùy chỉnh mức âm lượng phát nhạc |
| `/ping` | Kiểm tra độ trễ mạng (Gateway, REST API, Voice Latency) để đánh giá độ mượt |
| `/join` | Mời bot vào kênh thoại của bạn |
| `/leave` | Cho bot rời khỏi kênh thoại |

---

## 🛠️ Hướng dẫn Cài đặt & Cấu hình

### Bước 1: Tạo Bot trên Discord Developer Portal
1. Truy cập [Discord Developer Portal](https://discord.com/developers/applications) ➔ Chọn **New Application** ➔ Đặt tên cho bot.
2. Vào mục **Bot** ở thanh menu bên trái:
   * Nhấn **Reset Token** ➔ Sao chép chuỗi Token này.
   * Tại mục **Privileged Gateway Intents**: Bật **Server Members Intent** (nếu cần).
3. Vào mục **OAuth2** ➔ **URL Generator**:
   * Tích chọn Scopes: `bot`, `applications.commands`.
   * Tích chọn Bot Permissions: `Send Messages`, `Embed Links`, `Connect`, `Speak`, `Use Voice Activity`.
   * Sao chép đường link invite ở cuối trang, dán vào trình duyệt để thêm bot vào server Discord của bạn.

---

### Bước 2: Cấu hình File `.env`
Sao chép file `.env.example` thành `.env` và điền Token của bạn:
```env
DISCORD_TOKEN=dien_token_cua_ban_vao_day
LAVALINK_PASSWORD=youshallnotpass

# Nếu chạy bằng Docker:
LAVALINK_URI=http://lavalink:2333

# Nếu chạy Native trực tiếp trên máy:
# LAVALINK_URI=http://localhost:2333
```

---

## 🚀 Lựa chọn Phương thức Khởi chạy

Tùy vào nhu cầu sử dụng phần cứng của bạn, hãy chọn **1 trong 2** phương án dưới đây:

### ⚡ Phương án 1: Chạy Native (Khuyên dùng - Siêu nhẹ ~300 MB RAM)

#### Yêu cầu:
* **Java 17 trở lên** (khuyên dùng [Java 21 LTS](https://www.oracle.com/java/technologies/downloads/)).
* **Python 3.10 trở lên** (đã tích hợp `pip`).

#### Các bước cài đặt:
1. **Cài đặt thư viện Python**:
   ```powershell
   pip install -r requirements.txt
   ```
2. **Tải file `Lavalink.jar`**:
   * Tải bản phát hành mới nhất `Lavalink.jar` từ [Lavalink Releases](https://github.com/lavalink-devs/Lavalink/releases) và đặt vào thư mục gốc của bot.
3. **Khởi chạy Bot (1-Click)**:
   * Nhấp đúp chuột vào file **`run_native.bat`**.
   * Script sẽ tự động khởi động Lavalink Server chạy ngầm và mở Discord Music Bot.
4. **Tắt Bot**:
   * Nhấp đúp chuột vào file **`stop_native.bat`** để tắt sạch toàn bộ tiến trình.

---

### 🐳 Phương án 2: Chạy bằng Docker Compose (Đóng gói tiện lợi)
> Phù hợp nếu bạn đã dùng quen Docker, muốn môi trường chạy hoàn toàn độc lập và tự khởi động cùng máy tính.

#### Yêu cầu:
* Đã cài đặt và đang bật **Docker Desktop**.

#### Các bước khởi chạy:
1. **Khởi chạy toàn bộ hệ thống**:
   * Nhấp đúp chuột vào file **`manage.bat`** ➔ Chọn phím **1** (*Start All*).
   * Hoặc mở terminal gõ:
     ```powershell
     docker compose up -d --build
     ```
2. **Xem logs kiểm tra**:
   ```powershell
   docker compose logs -f bot
   ```
3. **Tắt Bot**:
   ```powershell
   docker compose down
   ```

---

## 🔑 Xác thực YouTube OAuth (Tùy chọn)
Nếu YouTube tại khu vực mạng của bạn kích hoạt kiểm tra bot nghiêm ngặt:
1. Mở file `application.yml`, kiểm tra dòng `plugins.youtube.oauth.enabled: true`.
2. Trong lần đầu khởi chạy Lavalink, xem log bạn sẽ thấy thông báo:
   ```text
   Go to https://www.google.com/device and enter code XXXX-XXXX
   ```
3. Truy cập liên kết trên, đăng nhập một tài khoản Google phụ và nhập mã để liên kết thiết bị. Token xác thực sẽ được ghi nhớ vĩnh viễn.

---

## 📄 Bản quyền
Mã nguồn phát hành theo giấy phép MIT. Mọi đóng góp (Pull Request, Issue) đều được hoan nghênh!
