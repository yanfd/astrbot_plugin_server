from astrbot.api.event.filter import command
from astrbot.api.star import Context, Star, register
import psutil
import platform
import datetime
import asyncio
import os
from typing import Optional
import matplotlib.pyplot as plt
import io
import base64
from jinja2 import Template
from PIL import Image
import requests
from io import BytesIO

@register("状态监控", "YANFD&Meguminlove", "监控插件", "1.0.0", "https://github.com/yanfd/astrbot_plugin_server")
class ServerMonitor(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.config = getattr(context, 'config', {})
        self._monitor_task: Optional[asyncio.Task] = None

    def _get_uptime(self) -> str:
        """获取系统运行时间"""
        boot_time = psutil.boot_time()
        now = datetime.datetime.now().timestamp()
        uptime_seconds = int(now - boot_time)
        
        # 转换为可读格式
        days, remainder = divmod(uptime_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        time_units = []
        if days > 0:
            time_units.append(f"{days}天")
        if hours > 0:
            time_units.append(f"{hours}小时")
        if minutes > 0:
            time_units.append(f"{minutes}分")
        #time_units.append(f"{seconds}秒")
        
        return " ".join(time_units)

    def _get_load_avg(self) -> str:
        """获取系统负载信息"""
        try:
            load = os.getloadavg()
            return f"{load[0]:.2f}, {load[1]:.2f}, {load[2]:.2f}"
        except AttributeError:
            return "不可用（Windows系统）"

    @command("状态查询", alias=["status"])
    async def server_status(self, event):
        try:
            # 获取系统信息
            cpu_usage = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net = psutil.net_io_counters()

            # 生成饼状图
            cpu_image_base64 = self._create_pie_chart(cpu_usage, '')
            mem_image_base64 = self._create_pie_chart(mem.percent, '')
            disk_image_base64 = self._create_pie_chart(disk.percent, '')

            # Jinja2 模板
            TMPL = """
            <!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>服务器状态报告</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500&display=swap" rel="stylesheet">
       <style>
        body {
            font-family: 'Roboto', sans-serif;
            background-color: #2a2a2a;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .container {
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 1.5rem;
            max-width: 800px;
            width: 100%;
            display: flex;
        }
        .info {
            flex: 1;
        }
        .info h2 {
            padding-top: 0.2rem;
            padding-left: 2rem;
            font-size: 1.2rem;
            color: #4a5568;
            margin: 0.75rem 0;
        }
        .charts-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .banner {
            display: flex;
            justify-content: space-around;
            margin-bottom: 1px;
            width: 100%;
        }
        .banner h1 {
            font-size: 1.5rem;
            color: #333;
        }
        .charts {
            display: flex;
            justify-content: space-around;
            width: 100%;
            align-items: center; /* 垂直居中 */
        }
        .chart img {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="info">
            <h2>系统信息: {{ system_info }}</h2>
            <h2>运行时间: {{ uptime }}</h2>
            <h2>系统负载: {{ load_avg }}</h2>
            <h2>网络流量: ↑{{ net_sent }}MB ↓{{ net_recv }}MB</h2>
            <h2>当前时间: {{ current_time }}</h2>
        </div>
        <div class="charts-container">
            <div class="banner">
                <h1>CPU</h1>
                <h1>MEM</h1>
                <h1>DISK</h1>
            </div>
            <div class="charts">
                <div class="chart">
                    <img src="data:image/png;base64,{{ cpu_image }}" alt="CPU使用率">
                </div>
                <div class="chart">
                    <img src="data:image/png;base64,{{ mem_image }}" alt="内存使用率">
                </div>
                <div class="chart">
                    <img src="data:image/png;base64,{{ disk_image }}" alt="磁盘使用率">
                </div>
            </div>
        </div>
    </div>
</body>
</html>
            """

            # 渲染 HTML
            template = Template(TMPL)
            html = template.render(
                cpu_image=cpu_image_base64,
                mem_image=mem_image_base64,
                disk_image=disk_image_base64,
                system_info=f"{platform.system()} {platform.release()}",
                uptime=self._get_uptime(),
                load_avg=self._get_load_avg(),
                net_sent=self._bytes_to_mb(net.bytes_sent),
                net_recv=self._bytes_to_mb(net.bytes_recv),
                current_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )

            # 生成图片
            url = await self.html_render(html, {})

            # 从 URL 加载图片
            response = requests.get(url)
            response.raise_for_status()
            pic = Image.open(BytesIO(response.content))

            width, height = pic.size
            crop_width = int(width * 0.7)
            crop_height = int(height * 0.4)

            left = (width - crop_width) // 2
            top = (height - crop_height) // 2
            right = left + crop_width
            bottom = top + crop_height

            # 边界检查
            left = max(0, left)
            top = max(0, top)
            right = min(width, right)
            bottom = min(height, bottom)

            if left < right and top < bottom:
                pic = pic.crop((left, top, right, bottom))
                pic.save("status.png")
                yield event.image_result("status.png")
            else:
                yield event.plain_result(f"⚠️ 裁剪区域无效")

        except Exception as e:
            yield event.plain_result(f"⚠️ 状态获取失败: {str(e)}")



    def _create_pie_chart(self, value: float, label: str) -> str:
        """创建饼状图"""
        buffer = io.BytesIO()
        plt.figure(figsize=(4, 4))
        labels = [label, '']
        sizes = [value, 100 - value]
        colors = ['#4c51bf', '#e2e8f0']
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor': 'white', 'linewidth': 2})
        plt.axis('equal')
        plt.savefig(buffer, format='png', bbox_inches='tight', transparent=True)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.clf()
        return image_base64

    @staticmethod
    def _bytes_to_gb(bytes_num: int) -> float:
        return round(bytes_num / 1024**3, 1)
    
    @staticmethod
    def _bytes_to_mb(bytes_num: int) -> float:
        return round(bytes_num / 1024**2, 1)

    async def terminate(self):
        if self._monitor_task and not self._monitor_task.cancelled():
            self._monitor_task.cancel()
        await super().terminate()