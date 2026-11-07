import asyncio
import logging
import os
import sys

# Đảm bảo in đúng ký tự tiếng Việt trên Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import discord
from discord.ext import commands
import dotenv
import wavelink

# Tải cấu hình từ file .env
dotenv.load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
LAVALINK_URI = os.getenv("LAVALINK_URI", "http://localhost:2333").strip()
LAVALINK_PASSWORD = os.getenv("LAVALINK_PASSWORD", "youshallnotpass").strip()

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("MusicBot")


class MusicBot(commands.Bot):
    """Lớp Bot chính quản lý kết nối Discord và Lavalink."""

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.guilds = True
        intents.voice_states = True

        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            intents=intents,
            help_command=None,
        )

    async def setup_hook(self) -> None:
        """Khởi tạo kết nối Wavelink và nạp các cogs trước khi bot online."""
        # 1. Kết nối tới Lavalink node
        logger.info(f"Đang kết nối tới Lavalink tại: {LAVALINK_URI}")
        node = wavelink.Node(
            uri=LAVALINK_URI,
            password=LAVALINK_PASSWORD,
            inactive_player_timeout=300,  # Tự động dọn dẹp player không hoạt động sau 5 phút
        )
        await wavelink.Pool.connect(nodes=[node], client=self, cache_capacity=100)

        # 2. Tải Cog Music
        await self.load_extension("cogs.music")
        logger.info("Đã tải cog cogs.music thành công.")

        # 3. Đồng bộ Slash Commands lên Discord
        try:
            synced = await self.tree.sync()
            logger.info(f"Đã đồng bộ {len(synced)} Slash commands lên Discord.")
        except Exception as e:
            logger.error(f"Lỗi khi đồng bộ Slash commands: {e}")

    async def on_ready(self) -> None:
        """Sự kiện khi Bot đã đăng nhập thành công vào Discord."""
        assert self.user is not None
        logger.info(f"==========================================")
        logger.info(f"Bot đã online: {self.user} (ID: {self.user.id})")
        logger.info(f"Số lượng Server (Guilds) tham gia: {len(self.guilds)}")
        logger.info(f"==========================================")

        # Đồng bộ lệnh trực tiếp cho từng Server (Guild) để lệnh hiện NGAY LẬP TỨC mà không phải chờ Discord duyệt toàn cầu (1 tiếng)
        for guild in self.guilds:
            try:
                self.tree.copy_global_to(guild=guild)
                synced = await self.tree.sync(guild=guild)
                logger.info(f"Đã đồng bộ {len(synced)} lệnh tức thì cho Server: {guild.name} (ID: {guild.id})")
            except Exception as e:
                logger.error(f"Lỗi sync guild {guild.name}: {e}")

        activity = discord.Activity(type=discord.ActivityType.listening, name="/play <tên_bài_hát>")
        await self.change_presence(status=discord.Status.online, activity=activity)


bot = MusicBot()


@bot.event
async def on_wavelink_node_ready(payload: wavelink.NodeReadyEventPayload) -> None:
    """Sự kiện khi Node Lavalink đã sẵn sàng tiếp nhận yêu cầu stream."""
    logger.info(f"Node Lavalink '{payload.node.identifier}' đã sẵn sàng (Session ID: {payload.session_id})")


@bot.event
async def on_wavelink_track_start(payload: wavelink.TrackStartEventPayload) -> None:
    """Thông báo bài hát mới bắt đầu phát vào kênh chat."""
    player: getattr(wavelink, "Player", None) = payload.player
    track: getattr(wavelink, "Playable", None) = payload.track
    if not player or not track:
        return

    home = getattr(player, "home", None)
    if home and isinstance(home, discord.abc.Messageable):
        try:
            embed = discord.Embed(
                title="🎶 Bắt đầu phát bài hát",
                description=f"**[{track.title}]({track.uri})**",
                color=discord.Color.blue(),
            )
            embed.add_field(name="Kênh / Tác giả", value=track.author or "Không rõ", inline=True)
            if track.artwork:
                embed.set_thumbnail(url=track.artwork)
            await home.send(embed=embed)
        except Exception as e:
            logger.warning(f"Không thể gửi thông báo track_start: {e}")


@bot.event
async def on_wavelink_track_exception(payload: wavelink.TrackExceptionEventPayload) -> None:
    """Bắt và thông báo khi bài hát gặp sự cố phát âm thanh."""
    player: getattr(wavelink, "Player", None) = payload.player
    track: getattr(wavelink, "Playable", None) = payload.track
    logger.error(f"Lỗi khi phát bài hát '{getattr(track, 'title', 'Unknown')}': {payload.exception}")
    if player:
        home = getattr(player, "home", None)
        if home and isinstance(home, discord.abc.Messageable):
            try:
                await home.send(f"⚠️ Không thể phát bài **{getattr(track, 'title', 'Unknown')}**: {payload.exception}")
            except Exception:
                pass


def main() -> None:
    """Hàm chạy bot chính."""
    if not DISCORD_TOKEN:
        logger.error(
            "DISCORD_TOKEN chưa được cấu hình! Vui lòng điền token vào file .env trước khi chạy bot."
        )
        sys.exit(1)

    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
