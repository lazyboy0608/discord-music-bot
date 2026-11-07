import asyncio
import datetime
from typing import cast
import discord
from discord import app_commands
from discord.ext import commands
import wavelink


def format_duration(ms: int) -> str:
    """Chuyển đổi milliseconds sang định dạng mm:ss hoặc hh:mm:ss."""
    seconds = int(ms / 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def create_progress_bar(position: int, length: int, size: int = 15) -> str:
    """Tạo thanh tiến trình phát nhạc trực quan."""
    if length <= 0:
        return "🔘" + "▬" * (size - 1)
    ratio = min(max(position / length, 0.0), 1.0)
    dot_pos = int(ratio * (size - 1))
    bar = ["▬"] * size
    bar[dot_pos] = "🔘"
    return "".join(bar)


class Music(commands.Cog):
    """Cog quản lý toàn bộ các tính năng nghe nhạc của bot."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def cog_command_error(self, ctx: commands.Context, error: Exception) -> None:
        """Xử lý lỗi cấp cog."""
        await ctx.send(f"⚠️ Có lỗi xảy ra: `{error}`")

    @app_commands.command(name="join", description="Mời bot vào kênh thoại của bạn.")
    async def join(self, interaction: discord.Interaction) -> None:
        """Kết nối bot vào kênh thoại."""
        if not interaction.user or not isinstance(interaction.user, discord.Member) or not interaction.user.voice:
            await interaction.response.send_message("❌ Bạn cần vào một kênh thoại trước!", ephemeral=True)
            return

        channel = interaction.user.voice.channel
        if not channel:
            await interaction.response.send_message("❌ Không tìm thấy kênh thoại của bạn!", ephemeral=True)
            return

        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if player:
            if player.channel == channel:
                await interaction.response.send_message(f"ℹ️ Bot đã có mặt tại `{channel.name}` rồi.", ephemeral=True)
                return
            await player.move_to(channel)
        else:
            player = await channel.connect(cls=wavelink.Player)
            player.autoplay = wavelink.AutoPlayMode.partial

        player.home = interaction.channel
        await interaction.response.send_message(f"✅ Đã tham gia kênh thoại: `{channel.name}`")

    @app_commands.command(name="leave", description="Ngắt kết nối bot khỏi kênh thoại.")
    async def leave(self, interaction: discord.Interaction) -> None:
        """Rời khỏi kênh thoại."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            await interaction.response.send_message("❌ Bot hiện không ở trong kênh thoại nào.", ephemeral=True)
            return

        player.queue.clear()
        await player.disconnect()
        await interaction.response.send_message("👋 Đã rời khỏi kênh thoại.")

    @app_commands.command(name="play", description="Phát bài hát từ YouTube, SoundCloud hoặc theo tên tìm kiếm.")
    @app_commands.describe(query="Tên bài hát hoặc đường link (YouTube / SoundCloud)")
    async def play(self, interaction: discord.Interaction, query: str) -> None:
        """Tìm kiếm và phát nhạc."""
        if not interaction.user or not isinstance(interaction.user, discord.Member) or not interaction.user.voice:
            await interaction.response.send_message("❌ Bạn cần tham gia một kênh thoại trước!", ephemeral=True)
            return

        channel = interaction.user.voice.channel
        if not channel:
            await interaction.response.send_message("❌ Không xác định được kênh thoại!", ephemeral=True)
            return

        await interaction.response.defer()

        # Kết nối player nếu chưa kết nối
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            try:
                player = await channel.connect(cls=wavelink.Player)
                player.autoplay = wavelink.AutoPlayMode.partial
            except Exception as e:
                await interaction.followup.send(f"❌ Không thể kết nối kênh thoại: `{e}`")
                return

        # Lưu kênh chat gọi lệnh làm home channel để gửi thông báo phát bài
        player.home = interaction.channel

        # Tìm kiếm bài hát: mặc định tìm trên YouTube Music để lấy luồng âm thanh chuẩn và ổn định nhất
        try:
            tracks: wavelink.Search = await wavelink.Playable.search(query, source=wavelink.TrackSource.YouTubeMusic)
            if not tracks:
                # Nếu không thấy trên YouTube Music, thử tìm trên YouTube thường
                tracks = await wavelink.Playable.search(query, source=wavelink.TrackSource.YouTube)
        except Exception as e:
            await interaction.followup.send(f"❌ Đã xảy ra lỗi khi tìm kiếm bài hát: `{e}`")
            return

        if not tracks:
            await interaction.followup.send(f"❌ Không tìm thấy bài hát nào cho: `{query}`")
            return

        if isinstance(tracks, wavelink.Playlist):
            added: int = await player.queue.put_wait(tracks)
            embed = discord.Embed(
                title=" Đã thêm Playlist vào hàng đợi",
                description=f"**[{tracks.name}]({tracks.url or ''})**\nSố lượng: `{added}` bài hát",
                color=discord.Color.green(),
            )
            embed.set_footer(text=f"Yêu cầu bởi {interaction.user.display_name}")
            await interaction.followup.send(embed=embed)
        else:
            track: wavelink.Playable = tracks[0]
            await player.queue.put_wait(track)
            embed = discord.Embed(
                title=" Đã thêm vào hàng đợi",
                description=f"**[{track.title}]({track.uri})**",
                color=discord.Color.blurple(),
            )
            embed.add_field(name="Thời lượng", value=format_duration(track.length), inline=True)
            embed.add_field(name="Kênh / Tác giả", value=track.author or "Không rõ", inline=True)
            if track.artwork:
                embed.set_thumbnail(url=track.artwork)
            embed.set_footer(text=f"Yêu cầu bởi {interaction.user.display_name}")
            await interaction.followup.send(embed=embed)

        # Nếu player chưa phát bài nào thì bắt đầu phát ngay
        if not player.playing:
            await player.play(player.queue.get())

    @app_commands.command(name="skip", description="Bỏ qua bài hát đang phát.")
    async def skip(self, interaction: discord.Interaction) -> None:
        """Bỏ qua bài hát hiện tại."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player or not player.current:
            await interaction.response.send_message("❌ Hiện tại không có bài hát nào đang phát.", ephemeral=True)
            return

        current_title = player.current.title
        await player.skip(force=True)
        await interaction.response.send_message(f"⏭️ Đã bỏ qua bài hát: **{current_title}**")

    @app_commands.command(name="pause", description="Tạm dừng bài hát đang phát.")
    async def pause(self, interaction: discord.Interaction) -> None:
        """Tạm dừng phát nhạc."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player or not player.current:
            await interaction.response.send_message("❌ Hiện tại không có bài hát nào đang phát.", ephemeral=True)
            return

        if player.paused:
            await interaction.response.send_message("ℹ️ Nhạc đã ở trạng thái tạm dừng rồi.", ephemeral=True)
            return

        await player.pause(True)
        await interaction.response.send_message("⏸️ Đã tạm dừng phát nhạc.")

    @app_commands.command(name="resume", description="Tiếp tục phát bài hát đang tạm dừng.")
    async def resume(self, interaction: discord.Interaction) -> None:
        """Tiếp tục phát nhạc."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player or not player.current:
            await interaction.response.send_message("❌ Hiện tại không có bài hát nào.", ephemeral=True)
            return

        if not player.paused:
            await interaction.response.send_message("ℹ️ Nhạc đang phát bình thường.", ephemeral=True)
            return

        await player.pause(False)
        await interaction.response.send_message("▶️ Đã tiếp tục phát nhạc.")

    @app_commands.command(name="stop", description="Dừng phát, xóa hàng đợi và rời khỏi kênh thoại.")
    async def stop(self, interaction: discord.Interaction) -> None:
        """Dừng phát nhạc và dọn dẹp hàng đợi."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            await interaction.response.send_message("❌ Bot hiện không phát nhạc.", ephemeral=True)
            return

        player.queue.clear()
        await player.disconnect()
        await interaction.response.send_message("⏹️ Đã dừng phát nhạc, xóa hàng đợi và rời kênh thoại.")

    @app_commands.command(name="queue", description="Hiển thị danh sách hàng đợi các bài hát.")
    @app_commands.describe(page="Số trang danh sách bài hát (mặc định là trang 1)")
    async def queue(self, interaction: discord.Interaction, page: int = 1) -> None:
        """Xem danh sách hàng đợi với cơ chế phân trang an toàn."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player or (not player.current and player.queue.is_empty):
            await interaction.response.send_message("📭 Hàng đợi hiện đang trống.", ephemeral=True)
            return

        embed = discord.Embed(title="📋 Danh Sách Hàng Đợi", color=discord.Color.gold())

        # 1. Hiển thị bài hát đang phát
        if player.current:
            curr_title = player.current.title
            if len(curr_title) > 70:
                curr_title = curr_title[:67] + "..."
            pos = format_duration(player.position)
            length = format_duration(player.current.length)
            embed.add_field(
                name="▶️ Đang phát:",
                value=f"**[{curr_title}]({player.current.uri})** ({pos}/{length})",
                inline=False,
            )

        # 2. Hiển thị danh sách các bài tiếp theo
        if not player.queue.is_empty:
            queue_list_all = list(player.queue)
            total_tracks = len(queue_list_all)
            per_page = 10
            total_pages = max(1, (total_tracks + per_page - 1) // per_page)

            if page < 1 or page > total_pages:
                await interaction.response.send_message(
                    f"❌ Trang `{page}` không hợp lệ! Hàng đợi hiện có `{total_pages}` trang (từ 1 đến {total_pages}).",
                    ephemeral=True,
                )
                return

            start_idx = (page - 1) * per_page
            end_idx = min(start_idx + per_page, total_tracks)
            page_tracks = queue_list_all[start_idx:end_idx]

            queue_lines = []
            char_count = 0

            for i, track in enumerate(page_tracks, start=start_idx + 1):
                track_title = track.title
                # Cắt ngắn tiêu đề nếu quá dài để hiển thị gọn gàng, tránh tràn giao diện
                if len(track_title) > 55:
                    track_title = track_title[:52] + "..."
                duration = format_duration(track.length)
                line = f"`{i}.` **[{track_title}]({track.uri})** `[{duration}]`"

                # Bảo vệ giới hạn 1024 ký tự của Discord Embed Field (chặn ở 950 để có biên an toàn)
                if char_count + len(line) + 1 > 950:
                    queue_lines.append("`... và các bài khác trên trang này`")
                    break

                queue_lines.append(line)
                char_count += len(line) + 1

            embed.add_field(
                name=f"⏭️ Tiếp theo ({start_idx + 1} - {end_idx} / {total_tracks} bài):",
                value="\n".join(queue_lines),
                inline=False,
            )
            embed.set_footer(
                text=f"Trang {page}/{total_pages} • Tổng: {total_tracks} bài • Dùng /queue [số trang] để lật trang"
            )
        else:
            embed.add_field(name="⏭️ Tiếp theo:", value="Không còn bài hát nào trong hàng đợi.", inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="nowplaying", description="Hiển thị thông tin chi tiết bài hát đang phát.")
    async def nowplaying(self, interaction: discord.Interaction) -> None:
        """Xem thông tin bài hát hiện tại."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player or not player.current:
            await interaction.response.send_message("❌ Hiện không có bài hát nào đang phát.", ephemeral=True)
            return

        track = player.current
        pos = player.position
        total = track.length
        bar = create_progress_bar(pos, total)

        embed = discord.Embed(
            title="🎶 Đang Phát",
            description=f"**[{track.title}]({track.uri})**",
            color=discord.Color.teal(),
        )
        embed.add_field(name="Tác giả / Kênh", value=track.author or "Không rõ", inline=True)
        embed.add_field(name="Âm lượng", value=f"{player.volume}%", inline=True)
        embed.add_field(
            name="Tiến trình",
            value=f"`{format_duration(pos)}` {bar} `{format_duration(total)}`",
            inline=False,
        )
        if track.artwork:
            embed.set_thumbnail(url=track.artwork)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="volume", description="Điều chỉnh âm lượng phát nhạc (1 - 100).")
    @app_commands.describe(volume="Mức âm lượng từ 1 đến 100")
    async def volume(self, interaction: discord.Interaction, volume: app_commands.Range[int, 1, 100]) -> None:
        """Thay đổi âm lượng của player."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            await interaction.response.send_message("❌ Bot hiện không ở trong kênh thoại.", ephemeral=True)
            return

        await player.set_volume(volume)
        await interaction.response.send_message(f"🔊 Đã điều chỉnh âm lượng thành **{volume}%**.")

    @app_commands.command(name="loop", description="Cài đặt chế độ lặp lại bài hát hoặc hàng đợi.")
    @app_commands.describe(mode="Chế độ lặp: Bài hiện tại, Cả danh sách hoặc Tắt")
    @app_commands.choices(
        mode=[
            app_commands.Choice(name="🔂 Lặp lại bài hát hiện tại (Track)", value="track"),
            app_commands.Choice(name="🔁 Lặp lại cả danh sách (Queue)", value="queue"),
            app_commands.Choice(name="➡️ Tắt lặp lại (Off)", value="off"),
        ]
    )
    async def loop(
        self, interaction: discord.Interaction, mode: app_commands.Choice[str] | None = None
    ) -> None:
        """Cài đặt chế độ lặp lại bài hát hoặc hàng đợi."""
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player or not player.connected:
            await interaction.response.send_message("❌ Bot hiện không ở trong kênh thoại.", ephemeral=True)
            return

        if mode is None:
            # Nếu không chọn tham số: chuyển đổi bật/tắt lặp bài hiện tại
            if player.queue.mode == wavelink.QueueMode.loop:
                player.queue.mode = wavelink.QueueMode.normal
                await interaction.response.send_message("➡️ Đã **tắt** chế độ lặp lại.")
            else:
                player.queue.mode = wavelink.QueueMode.loop
                await interaction.response.send_message("🔂 Đã **bật lặp lại bài hát hiện tại**.")
            return

        if mode.value == "track":
            player.queue.mode = wavelink.QueueMode.loop
            await interaction.response.send_message("🔂 Đã cài đặt: **Lặp lại bài hát hiện tại**.")
        elif mode.value == "queue":
            player.queue.mode = wavelink.QueueMode.loop_all
            await interaction.response.send_message("🔁 Đã cài đặt: **Lặp lại toàn bộ hàng đợi**.")
        else:
            player.queue.mode = wavelink.QueueMode.normal
            await interaction.response.send_message("➡️ Đã **tắt** chế độ lặp lại.")

    @commands.Cog.listener()
    async def on_voice_state_update(
        self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState
    ) -> None:
        """Tự động rời phòng khi không còn người nghe trong kênh thoại."""
        if member.bot:
            return

        # Kiểm tra nếu ai đó vừa rời kênh thoại mà bot đang tham gia
        if before.channel and before.channel != after.channel:
            player: wavelink.Player = cast(wavelink.Player, before.channel.guild.voice_client)
            if player and player.channel == before.channel:
                # Đếm số người không phải bot trong kênh thoại
                listeners = [m for m in before.channel.members if not m.bot]
                if len(listeners) == 0:
                    # Chờ 30 giây xem có ai vào lại không
                    await asyncio.sleep(30)
                    listeners_recheck = [m for m in before.channel.members if not m.bot]
                    if len(listeners_recheck) == 0 and player.connected:
                        player.queue.clear()
                        await player.disconnect()
                        if hasattr(player, "home") and player.home:
                            try:
                                await player.home.send("👋 Đã tự động rời kênh thoại do không còn người nghe.")
                            except Exception:
                                pass


async def setup(bot: commands.Bot) -> None:
    """Đăng ký Cog vào Bot."""
    await bot.add_cog(Music(bot))
