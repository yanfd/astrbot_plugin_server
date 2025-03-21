# astrbot_plugin_server
# AstrBot 服务器状态监控插件

[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![AstrBot](https://img.shields.io/badge/AstrBot-3.4%2B-orange.svg)](https://github.com/Soulter/AstrBot)

实时监控服务器资源使用情况，支持多平台运行，提供清晰的系统状态报告。

从Meg的文本式报告升级而来⬇️

[![USER](https://img.shields.io/badge/user-Meguminlove-blue)](https://github.com/Meguminlove)



## 📦 安装

```bash
# 克隆仓库到插件目录
cd /AstrBot/data/plugins
git clone https://github.com/yanfd/astrbot_plugin_server.git

# 控制台重启AstrBot
```

## 🛠️ 功能特性
- 图像化实时 CPU/内存/磁盘/网络监控

## ⌨️ 使用命令

### 基础命令
```plaintext
/状态查询  或  /status
```
**示例输出：**

![](https://p.ipic.vip/u7el21.png)

![](https://p.ipic.vip/l0xwq2.png)


## 📌 注意事项
1. Linux 系统需安装基础工具：
```bash
sudo apt-get install procps sysstat jinja2 psutil jinja2 PIL requests matplotlib
#或者使用pip
pip install psutil jinja2 PIL requests matplotlib
```
2. 首次使用需授予执行权限
3. 推荐监控间隔 ≥ 60 秒

## 🤝 参与贡献
1. Fork 本仓库
2. 创建新分支 (`git checkout -b feature/awesome-feature`)
3. 提交修改 (`git commit -m 'Add some feature'`)
4. 推送更改 (`git push origin feature/awesome-feature`)
5. 创建 Pull Request

## 📜 开源协议
本项目采用 [MIT License](LICENSE)
