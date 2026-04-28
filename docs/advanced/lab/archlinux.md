---
title: "archlinux的安装"
author: "海上修机师"
source: "飞书知识库"
tags:
  - 进阶
  - Linux
---

这个东西其实没必要写教程,archlinux的wiki写的很清楚...

参考:

- [arch的wiki(除了这个也没有其他的)](https://wiki.archlinux.org/)

## 前言:archlinux是一种邪教

有一种神奇的系统,他高度可定制,并有翔实的wiki手册,适合有很多时间折腾并且喜欢阅读手册的用户使用.他的原则是KISS(keep it simple stupid),将系统的复杂性暴露给用户,从而达到用户可以更稳健地使用系统目的.(当然他还有一些什么用户中心的鬼话,这个就不用信了)由于这些特点,导致一些学生(或曰小鬼),以为自己会装arch了就是高手了\~\~甚至给他心高气傲上\~\~,其实装完arch你对linux或者gnu仍然是一无所知的(只是对着手册装而不是根据理解装的话).在实际生产或者服务器环境中,应该不会有人用这个(

## 宗旨

> 万物皆文件 --Linux哲学

gnu/Linux系统的安装本质上是把系统文件从一个地方复制到另一个地方,并对其中的一些配置进行修改的过程.

是的,整个教程其实这里就可以结束了(但是你还什么都没有学到呢

当然,至少下面的教程会告诉你,gnu/linux安装的时候,系统做了什么

## 获取到镜像并启动安装镜像后

非常不幸,archlinux安装盘启用了`archinstall`这一安装脚本

> Arch Linux 发布 2022.05.01 的 iso 后，已经默认集成了 archinstall

从而允许你跟着这个脚本安装,而不是手动定制,但是你知道的,使用这个工具并不是今天教程的主要部分

进入安装引导系统之后,你可以用lynx文本浏览器来查看archlinux安装手册(当然只能看英文).

## 确认引导模式

如果你知道的话就可以跳过了,如果你不知道可以运行一下`cat /sys/firmware/efi/fw_platform_size`如果是64那你就是正常的UEFI 64位,如果是其他的,请参照其他安装方法

## 联网

你知道的,archlinux作为一个网络操作系统,安装包是从源分发的,如果要安装你只能从网络上获取,所以我们先要联网.默认已经运行了联网服务,如果需要无线的话可以用`iwctl`,如果驱动不支持请使用有线

## 时间同步

你知道的,现代https需要正确的时间来工作,(当然,系统按道理是会联网后自动同步时间的)可以用这个同步时间`timedatectl`

## 分区

选择你需要安装的盘,如`/dev/sda`,`/dev/nvme0n1`等,可以用`fdisk -l`命令查看你有哪些盘

分盘工具可以用`fdisk`,`parted`,`cfdisk`等工具,(`cfdisk`比较简单,有一个简单的图形化界面)请参考各自工具的manual.

你必需要的分区包括

- 根,用于挂载根目录(用linux的文件系统)
- EFI分区(用FAT32)

当然,还有一些可选的分区,包括home,var,swap之类的,想定制的话自行了解

### 格式化分区

在分区结束后(注意,你前面只是在硬盘里面划了空间,而没有初始化文件系统)

此处使用`mkfs`的一套命令,如果每个文件系统有一个命令如`mkfs.ext4`

### 挂载分区

用`mount`先将根挂载到一个目录下面,一般我们挂在`/mnt`下面,然后在挂载的分区内创建`boot`目录,把efi分区挂到boot下,如果你要swap的话,这个时候把swap打开

## 安装系统本体

如果高兴的话,你最好先换个源,这个是源的配置文件`/etc/pacman.d/mirrorlist`,你知道的,你的网络并不能跨越太多的长城...

接下来用` pacstrap -K /mnt`来指定安装系统到你要的根目录,一般你需要的软件包包括(注意不用在这里装太多,不然一卡你就要重来了,建议是先装一个基本系统,然后后面chroot进去操作)

重要

- base 基本工具,包括busybox,包管理器之类
- linux 内核文件
- linux-firmware 驱动

可能需要

- 特殊的驱动
- 网络管理器如networkmanager
- 文本编辑器如nano,vim
- 手册工具 如man
- 引导工具 如grub,efimanager,osprober

## 配置

### fstab

这个文件记录了要挂载哪些盘,生成一个配置的脚本是`genfstab -U /mnt >> /mnt/etc/fstab`

### chroot

用`arch-chroot /mnt`到装好的根目录里头(arch-chroot并不是一个单纯的chroot,他是一个的脚本,对挂载的目录会进行一些操作,从而使chroot能正确运行更多命令)

### 设置时区,本地化

用软链接把`/usr/share/zoneinfo/`下面的城市链接到`/etc/localtime`,东八是上海`ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime`

可以用一些工具在本地硬件时钟上使用rtc(本地时间)或者utc(格林日治世界)世界

当然,如果你也可以用ntp进行网络校时.

本地化在`/etc/locale.gen`中进行,建议不管怎么样都保留一个en的配置,需要的就把他的注释删了,完事运行`locale-gen`来完成本地化

可以在`/etc/locale.conf`下面设置默认的locale,如`LANG=en_US.UTF-8`

### 网络

hostname配置(没有这个用起来可能会遇到一些问题)在`/etc/hostname`里头直接输入主机名就可以了

### 生成内核

这里的内核要在启动时使用,当然pacman安装脚本帮你完成了这件事,arch的生成方式是`mkinitcpio -P`

### root密码

用`passwd`给root密码,你也不想下次开机对着不呢登录的root用户发呆吧

### 引导

grub一般在uefi的设备上是这么装的`grub-install --target=x86_64-efi --efi-directory=esp --bootloader-id=GRUB`其中esp是你boot的目录,这句是安装基本文件.然后是生成配置文件(如果你要用grub启动win的话,需要安装os-prober并修改`/etc/default/grub`,添加或修改出`GRUB_DISABLE_OS_PROBER=false`),用`grub-mkconfig -o /boot/grub/grub.cfg`即可.

如果你一定要搞什么安全启动或者什么特殊文件系统的话去参考手册吧(

### 用户管理

可以安装并配置sudo,给普通用户特权.

添加用户的命令是`adduser`,参数不多,可以直接`-h`看一下,注意是否给家目录之类的

### 重启计算机

至此,你以及完成了一个基本系统的安装,接下来的一些图形管理之类的东西就不在这篇的讨论范围内了.

(不过其他人貌似希望我再加点别的，那再说吧)
