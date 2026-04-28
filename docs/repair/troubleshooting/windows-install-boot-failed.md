---
title: "重装系统后 Boot failed 排查"
author: "海上修机师"
source: "旧 GitHub 文档站"
tags:
  - 修机
  - 故障排查
---

## 现象
1. 部分设备在 U 盘启动后会保留 Windows Boot 优先级，重装完成重启时建议先拔出 U 盘。

2. 可尝试使用 Dism++ 或 PE 自带的引导修复工具修复，但实际成功率不高。

3. 在 PE 中右键装载 ISO，运行安装程序并跳过输入密钥，通常可以继续安装。

4. 联网验证后设置 PIN 时，如果需要使用字母，必须勾选包含字母的选项，避免后续重新设置。

5. 第三点的方法通常也能带上网卡驱动，可作为后续优先方案。


> 补充链接：[应知必懂的两种磁盘分区类型：MBR 和 GPT](https://zhuanlan.zhihu.com/p/541733200)

> 其实关于Legacy+MBR和UEFI+GPT，以及WindowsNT Setup还有不少可说，但没空写，先挖个坑吧。
