from __future__ import annotations

import html
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
OLD_ROOT = ROOT.parent / "old-docs"
DOCS_DIR = ROOT / "docs"


SECTION_INFO = {
    "start": ("入门", "给新成员和普通读者的基础说明、提问规范和常用软件认知。"),
    "repair": ("修机", "装机、PE、引导、清理、蓝屏、黑屏和常见维修流程。"),
    "software": ("软件", "Windows 常用软件、开发环境、虚拟化和远程工具。"),
    "hardware": ("硬件", "硬件基础、接口、维修工具、DIY 配置和硬件专题。"),
    "networking": ("网络", "IP、DNS、内网穿透、虚拟网络和家庭网络。"),
    "advanced": ("进阶", "NAS、Linux、开发工具链、科学计算和全栈技术栈。"),
    "operations": ("运营", "社团/团队运维、规范性文件、资源清单和预约流程。"),
    "archive": ("归档", "旧站、历史资料、摘录和已过时但仍有参考价值的内容。"),
}

SECTION_ORDER = [
    "start",
    "repair",
    "software",
    "hardware",
    "networking",
    "advanced",
    "operations",
    "archive",
]

TAG_DEFINITIONS = [
    ("入门", "start"),
    ("修机", "repair"),
    ("软件", "software"),
    ("硬件", "hardware"),
    ("网络", "networking"),
    ("进阶", "advanced"),
    ("运营", "operations"),
    ("归档", "archive"),
    ("历史资料", "history"),
    ("装机", "install"),
    ("引导", "boot"),
    ("系统清理", "cleanup"),
    ("SOP", "sop"),
    ("维修工具", "repair-tools"),
    ("故障排查", "troubleshooting"),
    ("软件激活", "activation"),
    ("网络专题", "network-topics"),
    ("NAS", "nas"),
    ("AI", "ai"),
    ("全栈", "fullstack"),
    ("Linux", "linux"),
    ("科学计算", "python-science"),
    ("工具链", "tooling"),
    ("规范", "policies"),
    ("旧站", "legacy"),
    ("团队历史", "team-history"),
    ("历史选购", "buying-guide"),
    ("历史专题", "historical-topics"),
    ("摘录", "excerpts"),
]

SUBSECTION_TAGS = {
    ("repair", "install"): "装机",
    ("repair", "boot"): "引导",
    ("repair", "cleanup"): "系统清理",
    ("repair", "sop"): "SOP",
    ("repair", "tools"): "维修工具",
    ("repair", "troubleshooting"): "故障排查",
    ("software", "activation"): "软件激活",
    ("networking", "advanced-networking"): "网络专题",
    ("advanced", "nas"): "NAS",
    ("advanced", "ai"): "AI",
    ("advanced", "fullstack"): "全栈",
    ("advanced", "lab"): "Linux",
    ("advanced", "python-science"): "科学计算",
    ("advanced", "tooling"): "工具链",
    ("operations", "policies"): "规范",
    ("archive", "legacy"): "旧站",
    ("archive", "team"): "团队历史",
    ("archive", "buying-guide"): "历史选购",
    ("archive", "black-magic"): "历史专题",
    ("archive", "excerpts"): "摘录",
}

TAG_ICONS = {
    "start": "material/book-open",
    "repair": "material/wrench",
    "software": "lucide/app-window",
    "hardware": "lucide/cpu",
    "networking": "material/network",
    "advanced": "lucide/chart-no-axes-combined",
    "operations": "lucide/settings-2",
    "archive": "material/archive",
    "history": "material/history",
    "install": "material/package",
    "boot": "material/play-circle",
    "cleanup": "material/broom",
    "sop": "material/file-cog",
    "repair-tools": "material/tools",
    "troubleshooting": "material/alert-circle",
    "activation": "material/key",
    "network-topics": "material/router",
    "nas": "material/server",
    "ai": "lucide/bot",
    "fullstack": "lucide/code-xml",
    "linux": "lucide/terminal",
    "python-science": "material/language-python",
    "tooling": "lucide/git-branch",
    "policies": "lucide/scroll-text",
    "legacy": "lucide/folder-git-2",
    "team-history": "lucide/users",
    "buying-guide": "material/clipboard-list",
    "historical-topics": "material/newspaper",
    "excerpts": "material/notebook",
}

TITLE_OVERRIDES = {
    "github/docs/FileSystem.md": "文件系统与分区基础",
    "github/docs/OSI七层模型简单介绍.md": "OSI 七层模型",
    "github/docs/PCFixing-HuaweiShare-Network-Error.md": "Windows IP/DNS 配置异常导致无法联网",
    "github/docs/PCFixing-WhiteScreen-Bug.md": "Win11 白屏闪烁排查",
    "github/docs/jerry修机经验.md": "常见机型故障经验",
    "github/docs/windows的安装.md": "Windows 安装流程",
    "github/docs/zzh10月16.md": "硬件故障案例：荣耀猎人黑屏与傲腾硬盘",
    "github/docs/清灰流程.md": "笔记本清灰流程",
    "github/docs/联想小新锁频问题.md": "联想小新锁频问题",
    "github/docs/重装系统失败时.md": "重装系统后 Boot failed 排查",
}

PRESERVE_ORIGINAL_H1_OVERRIDES = {
    "github/docs/zzh10月16.md",
}

PUBLIC_TEXT_REPLACEMENTS = {
    "据客户描述": "据用户描述",
    "面对客户我们": "面对用户我们",
    "下次买个副屏用来检测叭": "后续建议准备外接显示器用于交叉验证。",
    "PS：顺便再买俩硬盘盒叭": "后续建议准备备用硬盘盒用于交叉验证。",
    "机主怎么忍得了的？": "已严重影响使用。",
    "有一说一这感觉像是过热": "该现象初步看更接近过热或功耗策略问题",
    "蛮搞笑的": "表现较不稳定",
    "不戳": "可作为后续优先方案",
    "反正我没修好过": "实际成功率不高",
    "（哎，微软）": "，避免后续重新设置",
    "要干坨锡": "可能需要补焊",
    "别把卡扣都给扬了": "避免损坏卡扣",
    "寄，看看主板有没有烧坏": "需要重点怀疑主板故障，检查主板是否有烧坏痕迹",
    "## 针对重装系统后出现boot failed": "## 现象",
    "1.部分机主电脑windows boot优先级在u盘启动后，推荐重装完启动时拔出u盘": "1. 部分设备在 U 盘启动后会保留 Windows Boot 优先级，重装完成重启时建议先拔出 U 盘。",
    "3.在pe里直接用直接右键装载iso，后跳过输入密钥，然后就可以正常装啦。": "3. 在 PE 中右键装载 ISO，运行安装程序并跳过输入密钥，通常可以继续安装。",
    "5.第三点中的方法好像还会把网卡驱动打上？感觉以后就用这个不戳。": "5. 第三点的方法通常也能带上网卡驱动，可作为后续优先方案。",
    "5.第三点中的方法好像还会把网卡驱动打上？感觉以后就用这个可作为后续优先方案。": "5. 第三点的方法通常也能带上网卡驱动，可作为后续优先方案。",
    "2.失败后可尝试使用dism++或者pe盘自带的引导修复软件修复，但大概率失败诶（实际成功率不高）": "2. 可尝试使用 Dism++ 或 PE 自带的引导修复工具修复，但实际成功率不高。",
    "4.要注意使用联网验证后机主设置pin时，如果他要用含字母的pin一定要让他把含字母选项勾上，不然还得重设，避免后续重新设置": "4. 联网验证后设置 PIN 时，如果需要使用字母，必须勾选包含字母的选项，避免后续重新设置。",
    "进无论哪个系统都转弯圈瞬间黑屏": "进入任意系统时，在加载转圈阶段瞬间黑屏",
    "但秒进pe": "但可以快速进入 PE",
    "后在pe中dg和hdtune检测": "随后在 PE 中使用 DiskGenius 和 HD Tune 检测",
    "pe读不出S.M.A.R.T": "PE 无法读取 S.M.A.R.T.",
    "看到就不能重装系统咯": "遇到这类配置时不要直接重装系统",
    "直接抬走": "基本可判断硬盘异常",
}

SPECIAL_ROUTES = {
    "feishu/01-首页.md": None,
    "feishu/02-修机教程编写项目.md": "operations/repair-writing-project.md",
    "feishu/03-撰写目录.md": "operations/writing-directory.md",
    "feishu/04-摘录.md": "archive/excerpts/overview.md",
    "feishu/04-摘录/01-摘录自msdn的教程文章.md": "repair/install/windows-install-excerpt.md",
    "feishu/05-黑魔法.md": "archive/black-magic/overview.md",
    "feishu/06-工具.md": "repair/tools/overview.md",
    "feishu/06-工具/01-HEU_KMS_Activator.md": "software/activation/heu-kms-activator.md",
    "feishu/06-工具/02-PE盘的制作与使用.md": "repair/install/pe-drive.md",
    "feishu/06-工具/03-图吧工具箱.md": "repair/tools/tubatool.md",
    "feishu/06-工具/04-万用表检修.md": "hardware/multimeter.md",
    "feishu/07-理论知识.md": "repair/theory/overview.md",
    "feishu/07-理论知识/01-ipv4和ipv6.md": "networking/ipv4-ipv6.md",
    "feishu/07-理论知识/02-MBR和GPT.md": "repair/boot/mbr-gpt.md",
    "feishu/07-理论知识/03-计算机启动过程.md": "repair/boot/startup-process.md",
    "feishu/07-理论知识/04-引导修复.md": "repair/boot/boot-repair.md",
    "feishu/08-软件部分.md": "software/overview.md",
    "feishu/08-软件部分/01-office的安装.md": "software/office-installation.md",
    "feishu/08-软件部分/02-虚拟机.md": "software/virtual-machines.md",
    "feishu/08-软件部分/03-conda安装与使用.md": "software/conda.md",
    "feishu/08-软件部分/04-VSCode及环境配置.md": "software/vscode.md",
    "feishu/08-软件部分/05-清C盘流程.md": "repair/cleanup/clean-c-drive.md",
    "feishu/08-软件部分/06-SSD加速HDD.md": "hardware/ssd-cache-hdd.md",
    "feishu/08-软件部分/07-Apt镜像服务器构建.md": "software/apt-mirror.md",
    "feishu/08-软件部分/08-WSL的安装和使用.md": "software/wsl.md",
    "feishu/08-软件部分/09-远程控制.md": "software/remote-control.md",
    "feishu/08-软件部分/10-JupyterLab.md": "software/jupyterlab.md",
    "feishu/08-软件部分/11-软件面试题.md": "software/software-interview.md",
    "feishu/09-硬件部分.md": "hardware/overview.md",
    "feishu/09-硬件部分/01-手柄维修.md": "hardware/game-controller-repair.md",
    "feishu/09-硬件部分/02-硬件面试题.md": "hardware/hardware-interview.md",
    "feishu/09-硬件部分/03-超频指导（施工中.md": "hardware/overclocking.md",
    "feishu/09-硬件部分/04-笔记本接口.md": "hardware/laptop-ports.md",
    "feishu/10-附录.md": "repair/reference/overview.md",
    "feishu/10-附录/01-常见蓝屏代码.md": "repair/troubleshooting/blue-screen-codes.md",
    "feishu/11-进阶技能.md": "advanced/overview.md",
    "feishu/11-进阶技能/01-好玩的网络.md": "networking/advanced-networking/overview.md",
    "feishu/11-进阶技能/01-好玩的网络/01-【第一期】内网穿透 [施工中].md": "networking/advanced-networking/frp.md",
    "feishu/11-进阶技能/01-好玩的网络/02-【第二期】多拨.md": "networking/advanced-networking/multi-wan.md",
    "feishu/11-进阶技能/01-好玩的网络/03-【第三期】虚拟网络 [施工中].md": "networking/advanced-networking/virtual-network.md",
    "feishu/11-进阶技能/01-好玩的网络/04-【第四期】DNS [施工中].md": "networking/advanced-networking/dns.md",
    "feishu/11-进阶技能/02-NAS：垃圾佬的终极归宿.md": "advanced/nas/index.md",
    "feishu/11-进阶技能/02-NAS：垃圾佬的终极归宿/01-基于windows的NAS.md": "advanced/nas/windows-nas.md",
    "feishu/11-进阶技能/02-NAS：垃圾佬的终极归宿/02-OpenMediaVault.md": "advanced/nas/openmediavault.md",
    "feishu/11-进阶技能/03-一些最佳实践的工具流.md": "advanced/tooling/overview.md",
    "feishu/11-进阶技能/03-一些最佳实践的工具流/01-Git从原理到实践.md": "advanced/tooling/git.md",
    "feishu/11-进阶技能/03-一些最佳实践的工具流/02-Markdown从基础到进阶.md": "advanced/tooling/markdown.md",
    "feishu/11-进阶技能/04-有趣的整活栏目.md": "advanced/lab/overview.md",
    "feishu/11-进阶技能/04-有趣的整活栏目/01-archlinux的安装.md": "advanced/lab/archlinux.md",
    "feishu/11-进阶技能/05-Python科学计算.md": "advanced/python-science/index.md",
    "feishu/11-进阶技能/05-Python科学计算/01-【Matplotlib】三剑客之图表绘制.md": "advanced/python-science/matplotlib.md",
    "feishu/11-进阶技能/05-Python科学计算/01-【Matplotlib】三剑客之图表绘制/01-【第一期】Pyplot还是OO？.md": "advanced/python-science/pyplot-or-oo.md",
    "feishu/12-(开发组)全栈开发：前后端技术栈.md": "advanced/fullstack/index.md",
    "feishu/12-(开发组)全栈开发：前后端技术栈/01-后端.md": "advanced/fullstack/backend.md",
    "feishu/12-(开发组)全栈开发：前后端技术栈/02-前端.md": "advanced/fullstack/frontend.md",
    "feishu/13-小白知识科普内容.md": "start/overview.md",
    "feishu/13-小白知识科普内容/01-用户需要知道的电脑组成.md": "start/computer-basics.md",
    "feishu/13-小白知识科普内容/02-用户需要学会的软件使用.md": "start/software-basics.md",
    "feishu/13-小白知识科普内容/03-常见笔记本品牌及其各系列常见问.md": "start/laptop-brands.md",
    "feishu/13-小白知识科普内容/04-如何提问.md": "start/how-to-ask.md",
    "feishu/13-小白知识科普内容/05-硬件DIY配置询问指导.md": "hardware/diy-build-guidance.md",
    "feishu/13-小白知识科普内容/06-新机推荐.md": "archive/buying-guide/index.md",
    "feishu/13-小白知识科普内容/06-新机推荐/01-2024新机推荐.md": "archive/buying-guide/2024-laptops.md",
    "feishu/13-小白知识科普内容/06-新机推荐/02-2023新机推荐.md": "archive/buying-guide/2023-laptops.md",
    "feishu/13-小白知识科普内容/07-全屋WIFI覆盖方案分享.md": "networking/home-wifi.md",
    "feishu/14-规范性文件.md": "operations/policies/index.md",
    "feishu/14-规范性文件/01-公众号管理和对外宣传.md": "operations/policies/public-account.md",
    "feishu/14-规范性文件/02-修机SOP流程文件.md": "repair/sop/repair-sop.md",
    "feishu/14-规范性文件/03-人员管理.md": "operations/policies/people-management.md",
    "feishu/14-规范性文件/04-海上修机师-标准化操作流程（编辑版）.md": "repair/sop/standard-process.md",
    "feishu/14-规范性文件/04-海上修机师-标准化操作流程（编辑版）/01-撰写记录.md": "operations/policies/sop-writing-record.md",
    "feishu/14-规范性文件/05-黑屏SOP.md": "repair/troubleshooting/black-screen-sop.md",
    "feishu/15-已有资源列表.md": "operations/resources.md",
    "feishu/16-预约单收集表.md": "operations/appointment-form.md",
    "feishu/17-Codex及第三方GPT站点入门简述.md": "advanced/ai/codex-and-gpt-sites.md",
    "github/index.md": None,
    "github/docs/index.md": None,
    "github/store/index.md": "archive/legacy/store.md",
    "github/README.md": "archive/legacy/readme.md",
    "github/docs/2023年新机推荐.md": None,
    "github/docs/FileSystem.md": "repair/theory/file-system.md",
    "github/docs/JupyterLab.md": None,
    "github/docs/MBR和GPT.md": None,
    "github/docs/OSI七层模型简单介绍.md": "networking/osi-model.md",
    "github/docs/PCFixing-HuaweiShare-Network-Error.md": "repair/troubleshooting/windows-ip-dns-network-error.md",
    "github/docs/PCFixing-WhiteScreen-Bug.md": "repair/troubleshooting/win11-white-screen-flicker.md",
    "github/docs/PE盘的制作与使用.md": None,
    "github/docs/SSD加速HDD.md": None,
    "github/docs/VSCode及环境配置.md": None,
    "github/docs/WSL的安装和使用.md": None,
    "github/docs/conda安装与使用.md": None,
    "github/docs/ipv4和ipv6.md": None,
    "github/docs/jerry修机经验.md": "repair/troubleshooting/model-failure-notes.md",
    "github/docs/joycon手柄维修.md": None,
    "github/docs/office的安装.md": None,
    "github/docs/windows的安装.md": "repair/install/windows-install-process.md",
    "github/docs/zzh10月16.md": "repair/troubleshooting/hardware-case-notes.md",
    "github/docs/图吧工具箱.md": None,
    "github/docs/清C盘流程.md": None,
    "github/docs/清灰流程.md": "repair/cleanup/dust-cleaning.md",
    "github/docs/用户需要学会的软件使用.md": None,
    "github/docs/联想小新锁频问题.md": "repair/troubleshooting/lenovo-xiaoxin-throttling.md",
    "github/docs/计算机启动过程.md": None,
    "github/docs/远程控制.md": None,
    "github/docs/重装系统失败时.md": "repair/troubleshooting/windows-install-boot-failed.md",
}

SHEET_ROUTES = {
    "0bmM4V": ("repair/boot/mbr-gpt-compatibility-table.md", "MBR 与 GPT 兼容性表"),
    "sIwOac": ("repair/install/windows-pe-version-table.md", "Windows PE 版本表"),
    "Dy28v9": ("repair/install/windows-11-requirements.md", "Windows 11 硬件要求"),
    "VXRoR1": ("repair/install/boot-menu-keys.md", "常见设备启动菜单按键"),
    "rOf773": ("advanced/ai/codex-sandbox-modes.md", "Codex 沙盒模式速查"),
    "eD1tGI": ("networking/ip-address-blocks-table.md", "常见 IP 地址块速查"),
}

HISTORICAL_PREFIXES = (
    "archive/",
)

SKIP_FILENAMES = {"README.md", "EXPORT_ERRORS.md", "EXPORT_INDEX.md"}


@dataclass(frozen=True)
class Page:
    source: Path
    dest: Path
    title: str
    section: str
    historical: bool = False


def strip_order(name: str) -> str:
    return re.sub(r"^\d+[-_ ]*", "", name).strip()


def safe_filename(name: str) -> str:
    name = strip_order(name)
    name = re.sub(r"[\\/:*?\"<>|#%{}^~\[\]`]+", "-", name)
    name = re.sub(r"\s+", "-", name)
    name = re.sub(r"-{2,}", "-", name).strip("-. ")
    return name or "page"


def posix(path: Path) -> str:
    return path.as_posix()


def rel_old(path: Path) -> str:
    return posix(path.relative_to(OLD_ROOT))


def extract_title(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    match = re.search(r"<title>(.*?)</title>", text, flags=re.S)
    if match:
        return html.unescape(match.group(1).strip())
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return strip_order(path.stem)


def page_title(path: Path) -> str:
    return TITLE_OVERRIDES.get(rel_old(path), extract_title(path))


def section_for(dest: Path) -> str:
    top = dest.parts[0]
    if top not in SECTION_INFO:
        raise ValueError(f"Unknown section for {dest}")
    return top


def route_sheet(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"Sheet ID：`([^`]+)`", text)
    if not match:
        return None
    item = SHEET_ROUTES.get(match.group(1))
    return item[0] if item else None


def route_github(path: Path) -> str | None:
    rel = rel_old(path)
    if rel in SPECIAL_ROUTES:
        return SPECIAL_ROUTES[rel]
    if rel.startswith("github/team/"):
        return f"archive/team/{path.stem}.md"
    if rel.startswith("github/docs/"):
        return f"archive/legacy/{safe_filename(path.stem)}.md"
    return f"archive/legacy/{safe_filename(path.stem)}.md"


def route_feishu(path: Path) -> str | None:
    rel = rel_old(path)
    if rel in SPECIAL_ROUTES:
        return SPECIAL_ROUTES[rel]
    if rel.startswith("feishu/_embedded/sheets/"):
        return route_sheet(path)
    if path.name in SKIP_FILENAMES or "/_" in rel:
        return None

    parts = rel.split("/")
    top = parts[1] if parts[0] == "feishu" and len(parts) > 1 else path.name
    title = safe_filename(path.stem)

    if top.startswith("04-摘录"):
        return f"archive/excerpts/{title}.md"
    if top.startswith("05-黑魔法"):
        return f"archive/black-magic/{title}.md"
    if top.startswith("08-软件部分"):
        return f"software/{title}.md"
    if top.startswith("09-硬件部分"):
        return f"hardware/{title}.md"
    if top.startswith("13-小白知识科普内容"):
        return f"start/{title}.md"
    if top.startswith("14-规范性文件"):
        return f"operations/policies/{title}.md"
    return f"archive/imported/{title}.md"


def discover_pages() -> list[Page]:
    pages: list[Page] = []
    for path in sorted((OLD_ROOT / "feishu").rglob("*.md")):
        route = route_feishu(path)
        if route is None:
            continue
        title = SHEET_ROUTES.get(extract_sheet_id(path), (None, page_title(path)))[1]
        dest = Path(route)
        pages.append(Page(path, dest, title, section_for(dest), str(dest).startswith(HISTORICAL_PREFIXES)))

    for path in sorted((OLD_ROOT / "github").rglob("*.md")):
        if path.name in {"EXPORT_INDEX.md"}:
            continue
        route = route_github(path)
        if route is None:
            continue
        dest = Path(route)
        title = page_title(path)
        pages.append(Page(path, dest, title, section_for(dest), str(dest).startswith(HISTORICAL_PREFIXES)))

    seen: dict[Path, Page] = {}
    for page in pages:
        if page.dest in seen:
            raise RuntimeError(f"Duplicate output path: {page.dest} from {page.source} and {seen[page.dest].source}")
        seen[page.dest] = page
    return pages


def extract_sheet_id(path: Path) -> str | None:
    if "_embedded/sheets" not in posix(path):
        return None
    text = path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"Sheet ID：`([^`]+)`", text)
    return match.group(1) if match else None


def clean_output() -> None:
    if DOCS_DIR.exists():
        shutil.rmtree(DOCS_DIR)
    DOCS_DIR.mkdir(parents=True)


def copy_assets() -> None:
    targets = [
        (OLD_ROOT / "feishu" / "_assets", DOCS_DIR / "assets" / "feishu"),
        (OLD_ROOT / "github" / "assets", DOCS_DIR / "assets" / "legacy" / "assets"),
        (OLD_ROOT / "github" / "_assets", DOCS_DIR / "assets" / "legacy" / "_assets"),
        (OLD_ROOT / "github" / "docs" / "images", DOCS_DIR / "assets" / "legacy" / "images"),
    ]
    for src, dest in targets:
        if src.exists():
            shutil.copytree(src, dest, dirs_exist_ok=True)
    scrub_html_assets()


def scrub_html_assets() -> None:
    placeholder = """<!doctype html>
<html lang="zh-CN">
<meta charset="utf-8">
<title>嵌入素材已移除</title>
<p>这个 HTML 嵌入来自旧知识库导出，包含登录态页面或内部字段。公开版已移除原始内容。</p>
</html>
"""
    for path in (DOCS_DIR / "assets").rglob("*.html"):
        path.write_text(placeholder, encoding="utf-8")


def is_external(link: str) -> bool:
    if link.startswith(("#", "mailto:", "tel:", "data:", "//")):
        return True
    parsed = urlparse(link)
    return bool(parsed.scheme and parsed.scheme not in {"file"})


def split_anchor(link: str) -> tuple[str, str]:
    if "#" not in link:
        return link, ""
    path, anchor = link.split("#", 1)
    return path, f"#{anchor}"


def resolve_old_link(link: str, source: Path) -> Path | None:
    raw, _ = split_anchor(link)
    if not raw or is_external(raw):
        return None
    if raw.startswith("/assets/") and "/github/" in posix(source):
        return (OLD_ROOT / "github" / raw.lstrip("/")).resolve()
    if raw.startswith("/"):
        return None
    return (source.parent / raw).resolve()


def asset_dest_for(resolved: Path) -> Path | None:
    roots = [
        (OLD_ROOT / "feishu" / "_assets", DOCS_DIR / "assets" / "feishu"),
        (OLD_ROOT / "github" / "assets", DOCS_DIR / "assets" / "legacy" / "assets"),
        (OLD_ROOT / "github" / "_assets", DOCS_DIR / "assets" / "legacy" / "_assets"),
        (OLD_ROOT / "github" / "docs" / "images", DOCS_DIR / "assets" / "legacy" / "images"),
    ]
    for old_base, new_base in roots:
        try:
            rel = resolved.relative_to(old_base.resolve())
        except ValueError:
            continue
        return new_base / rel
    return None


def make_relative(target: Path, output_page: Path) -> str:
    return Path(os.path.relpath(target, output_page.parent)).as_posix()


def rewrite_link(link: str, source: Path, output_page: Path, source_to_dest: dict[Path, Path]) -> str:
    path_part, anchor = split_anchor(link)
    if is_external(path_part) or not path_part:
        return link

    resolved = resolve_old_link(path_part, source)
    if resolved is None:
        return link

    if resolved in source_to_dest:
        target = DOCS_DIR / source_to_dest[resolved]
        return make_relative(target, output_page) + anchor

    asset_dest = asset_dest_for(resolved)
    if asset_dest is not None:
        return make_relative(asset_dest, output_page) + anchor

    return link


def rewrite_markdown_links(text: str, source: Path, output_page: Path, source_to_dest: dict[Path, Path]) -> str:
    def repl(match: re.Match[str]) -> str:
        prefix, label, link = match.groups()
        if link.startswith("<") and link.endswith(">"):
            link = link[1:-1]
            wrapped = True
        else:
            wrapped = False
        new_link = rewrite_link(link, source, output_page, source_to_dest)
        if wrapped:
            new_link = f"<{new_link}>"
        return f"{prefix}[{label}]({new_link})"

    return re.sub(r"(!?)\[([^\]]*)\]\(([^)]+)\)", repl, text)


def rewrite_html_links(text: str, source: Path, output_page: Path, source_to_dest: dict[Path, Path]) -> str:
    def repl(match: re.Match[str]) -> str:
        attr, quote, link = match.groups()
        new_link = rewrite_link(link, source, output_page, source_to_dest)
        return f'{attr}={quote}{new_link}{quote}'

    return re.sub(r"\b(src|href)=(['\"])([^'\"]+)\2", repl, text)


def indent_block(text: str) -> str:
    cleaned = html_to_plain_markdown(text).strip()
    if not cleaned:
        cleaned = "原始提示块内容为空。"
    return "\n".join(f"    {line}" if line else "" for line in cleaned.splitlines())


def html_to_plain_markdown(text: str) -> str:
    text = html.unescape(text)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"</p>\s*<p[^>]*>", "\n\n", text, flags=re.I)
    text = re.sub(r"</?p[^>]*>", "", text, flags=re.I)
    text = re.sub(r"<h([1-6])[^>]*>(.*?)</h\1>", lambda m: f"\n{'#' * int(m.group(1))} {re.sub(r'<[^>]+>', '', m.group(2)).strip()}\n", text, flags=re.I | re.S)
    text = re.sub(r"<a[^>]*href=['\"]([^'\"]+)['\"][^>]*>(.*?)</a>", lambda m: f"[{re.sub(r'<[^>]+>', '', m.group(2)).strip()}]({m.group(1)})", text, flags=re.I | re.S)
    text = re.sub(r"<(strong|b)>(.*?)</\1>", r"**\2**", text, flags=re.I | re.S)
    text = re.sub(r"<(em|i)>(.*?)</\1>", r"*\2*", text, flags=re.I | re.S)
    text = re.sub(r"<del>(.*?)</del>", r"~~\1~~", text, flags=re.I | re.S)
    return text


def parse_attrs(tag: str) -> dict[str, str]:
    return {key: html.unescape(value) for key, _, value in re.findall(r"([\w-]+)=(['\"])(.*?)\2", tag)}


def convert_figure(match: re.Match[str], source: Path, output_page: Path, source_to_dest: dict[Path, Path]) -> str:
    body = match.group(1)
    source_match = re.search(r"<source\b([^>]*)/?>", body, flags=re.I)
    if not source_match:
        return ""
    attrs = parse_attrs(source_match.group(1))
    href = attrs.get("href", "")
    mime = attrs.get("mime", "")
    new_href = rewrite_link(href, source, output_page, source_to_dest)
    if mime.startswith("video/") or new_href.lower().endswith((".mp4", ".webm", ".mov")):
        return f'\n<video controls src="{new_href}"></video>\n'
    if mime.startswith("image/") or new_href.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg")):
        return f"\n![嵌入素材]({new_href})\n"
    return f"\n[查看嵌入素材]({new_href})\n"


def convert_cite(match: re.Match[str], output_page: Path, title_to_dest: dict[str, Path]) -> str:
    attrs = parse_attrs(match.group(1))
    if attrs.get("type") == "user":
        return ""
    title = attrs.get("title", "相关文档").strip()
    target = title_to_dest.get(title)
    if target is None:
        return f"《{title}》"
    return f"[{title}]({make_relative(DOCS_DIR / target, output_page)})"


def convert_sheet(match: re.Match[str], output_page: Path) -> str:
    attrs = parse_attrs(match.group(1))
    sheet_id = attrs.get("sheet-id")
    item = SHEET_ROUTES.get(sheet_id or "")
    if not item:
        return "\n> 原始嵌入表格已移除。\n"
    target, title = item
    link = make_relative(DOCS_DIR / target, output_page)
    return f"\n> 嵌入表格已整理为 [{title}]({link})。\n"


def normalize_frontmatter(text: str) -> str:
    return re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S).lstrip()


def sanitize_sheet_text(text: str, title: str) -> str:
    lines = []
    for line in text.splitlines():
        if line.startswith("# "):
            lines.append(f"# {title}")
            continue
        if any(marker in line for marker in ("Spreadsheet token", "Sheet ID", "读取范围")):
            continue
        if line.startswith("来源：嵌入电子表格"):
            continue
        lines.append(line)
    return "\n".join(lines).strip() + "\n"


def normalize_text(
    text: str,
    page: Page,
    output_page: Path,
    source_to_dest: dict[Path, Path],
    title_to_dest: dict[str, Path],
) -> str:
    text = normalize_frontmatter(text)
    if "_embedded/sheets" in posix(page.source):
        text = sanitize_sheet_text(text, page.title)

    text = re.sub(r"<title>(.*?)</title>", lambda m: f"# {html.unescape(m.group(1).strip())}\n", text, flags=re.S)
    text = re.sub(r"<bookmark\b([^>]*)>\s*</bookmark>", lambda m: f"[{parse_attrs(m.group(1)).get('name', '外部链接')}]({parse_attrs(m.group(1)).get('href', '#')})", text)
    text = re.sub(r"<cite\b([^>]*)>\s*</cite>", lambda m: convert_cite(m, output_page, title_to_dest), text)
    text = re.sub(r"<sheet\b([^>]*)>\s*</sheet>", lambda m: convert_sheet(m, output_page), text)
    text = re.sub(r"<figure\b[^>]*>(.*?)</figure>", lambda m: convert_figure(m, page.source, output_page, source_to_dest), text, flags=re.S | re.I)

    def callout_repl(match: re.Match[str]) -> str:
        attrs = parse_attrs(match.group(1))
        emoji = attrs.get("emoji", "")
        title = "提示" if not emoji else f"{emoji} 提示"
        return f'\n!!! note "{title}"\n{indent_block(match.group(2))}\n'

    text = re.sub(r"<callout\b([^>]*)>(.*?)</callout>", callout_repl, text, flags=re.S | re.I)
    text = re.sub(r"</?synced-source>", "", text)
    text = re.sub(r"<synced_reference\b[^>]*>\s*</synced_reference>", "\n> 同步块引用已在公开版中移除。\n", text)
    text = re.sub(r"<base_refer\b[^>]*>\s*</base_refer>", "\n> 原始飞书多维表格嵌入已移除，公开版仅保留已导出的 Markdown 内容。\n", text)
    text = re.sub(r"<wiki_recent_update>\s*</wiki_recent_update>", "", text)
    text = re.sub(r"<folder_manager>\s*</folder_manager>", "", text)
    text = re.sub(r"<readonly-block\b[^>]*>\s*</readonly-block>", "", text)
    text = re.sub(r"</?(grid|column)\b[^>]*>", "", text)
    text = re.sub(r"<([a-z]+-[a-z0-9_-]+)\b[^>]*>\s*</\1>", "", text)
    text = re.sub(r"<([a-z]+-[a-z0-9_-]+)\b[^>]*/>", "", text)

    text = rewrite_markdown_links(text, page.source, output_page, source_to_dest)
    text = rewrite_html_links(text, page.source, output_page, source_to_dest)

    text = html.unescape(text)
    text = text.replace("老东西", "成员")
    text = text.replace("死🐴人", "争议较大")
    for old, new in PUBLIC_TEXT_REPLACEMENTS.items():
        text = text.replace(old, new)
    text = re.sub(r"（[^）]*(?:旁边评论|看看有没有推荐|user-id)[^）]*）", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    source_rel = rel_old(page.source)
    if source_rel in TITLE_OVERRIDES:
        if source_rel not in PRESERVE_ORIGINAL_H1_OVERRIDES:
            text = re.sub(r"^#\s+.*\n?", "", text, count=1, flags=re.M)
        text = re.sub(r"^#\s+", "## ", text, flags=re.M)
        text = f"# {page.title}\n\n{text.lstrip()}"
    elif not re.search(r"^#\s+", text, flags=re.M):
        text = f"# {page.title}\n\n{text}"
    if page.historical:
        note = (
            '!!! info "历史资料"\n'
            "    本页来自旧知识库或旧站归档，已做公开发布前的格式清理和去敏处理。"
            "其中涉及时间、价格、推荐和组织状态的内容，请按历史资料理解。\n\n"
        )
        text = note + text
    return text + "\n"


def write_page(page: Page, source_to_dest: dict[Path, Path], title_to_dest: dict[str, Path]) -> None:
    output_page = DOCS_DIR / page.dest
    output_page.parent.mkdir(parents=True, exist_ok=True)
    text = page.source.read_text(encoding="utf-8", errors="ignore")
    normalized = normalize_text(text, page, output_page, source_to_dest, title_to_dest)
    output_page.write_text(add_frontmatter(normalized, page), encoding="utf-8")


def page_tags(page: Page) -> list[str]:
    tags = [SECTION_INFO[page.section][0]]
    parts = page.dest.parts
    if len(parts) > 1:
        subsection_tag = SUBSECTION_TAGS.get((page.section, parts[1]))
        if subsection_tag:
            tags.append(subsection_tag)
    if page.historical:
        tags.append("历史资料")
    return list(dict.fromkeys(tags))


def add_frontmatter(text: str, page: Page) -> str:
    tag_lines = "\n".join(f"  - {tag}" for tag in page_tags(page))
    frontmatter = f"tags:\n{tag_lines}\n"

    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            existing = text[4:end].strip()
            body = text[end + 5 :].lstrip("\n")
            merged = frontmatter + (existing + "\n" if existing else "")
            return f"---\n{merged}---\n\n{body}"

    return f"---\n{frontmatter}---\n\n{text}"


def sort_key(page: Page) -> tuple[int, str, str]:
    return (SECTION_ORDER.index(page.section), posix(page.dest), page.title)


def write_section_indexes(pages: list[Page]) -> None:
    by_section: dict[str, list[Page]] = {section: [] for section in SECTION_ORDER}
    for page in sorted(pages, key=sort_key):
        if page.dest.name == "index.md":
            continue
        by_section[page.section].append(page)

    for section in SECTION_ORDER:
        title, description = SECTION_INFO[section]
        section_dir = DOCS_DIR / section
        section_dir.mkdir(parents=True, exist_ok=True)
        lines = [
            f"# {title}",
            "",
            description,
            "",
            "## 页面索引",
            "",
        ]
        for page in by_section[section]:
            link = make_relative(DOCS_DIR / page.dest, section_dir / "index.md")
            lines.append(f"- [{page.title}]({link})")
        lines.append("")
        (section_dir / "index.md").write_text("\n".join(lines), encoding="utf-8")


def write_home() -> None:
    lines = [
        "# 海上修机师知识库",
        "",
        "这里整理电脑维修、软件配置、网络基础、硬件实践、团队运维和历史档案。内容由旧飞书知识库和旧 GitHub 文档站迁移而来，公开版已经剥离内部标识并重新组织目录。",
        "",
        "## 快速入口",
        "",
    ]
    for section in SECTION_ORDER:
        title, description = SECTION_INFO[section]
        lines.append(f"- [{title}]({section}/index.md)：{description}")
    lines.extend(
        [
            "",
            "## 使用提示",
            "",
            "- 涉及价格、产品推荐和时间敏感信息的页面优先按历史资料理解。",
            "- 维修和装机操作有数据丢失风险，执行前先备份重要文件。",
            "- 公开站不包含飞书 token、用户 open_id、表格 token 等内部标识。",
            "",
        ]
    )
    (DOCS_DIR / "index.md").write_text("\n".join(lines), encoding="utf-8")


def toml_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def write_config(pages: list[Page]) -> None:
    lines = [
        "[project]",
        'site_name = "海上修机师知识库"',
        'site_description = "面向南信大学生和新成员的电脑维修、软件配置、网络与社团运维知识库。"',
        'site_author = "NUIST Engineer Lion"',
        'site_url = "https://wiki.nuist.link/"',
        'repo_url = "https://github.com/nuist-engineer-lion/docs"',
        'repo_name = "nuist-engineer-lion/docs"',
        'edit_uri = "edit/main/docs"',
        'copyright = "Copyright &copy; 2026 NUIST Engineer Lion"',
        'docs_dir = "docs"',
        'site_dir = "site"',
        "use_directory_urls = true",
        "",
        "nav = [",
        '  {"首页" = "index.md"},',
    ]

    by_section: dict[str, list[Page]] = {section: [] for section in SECTION_ORDER}
    for page in sorted(pages, key=sort_key):
        if page.dest.name != "index.md":
            by_section[page.section].append(page)

    for section in SECTION_ORDER:
        label, _ = SECTION_INFO[section]
        lines.append(f"  {{{toml_string(label)} = [")
        lines.append(f'    "{section}/index.md",')
        for page in by_section[section]:
            lines.append(f"    {{{toml_string(page.title)} = {toml_string(posix(page.dest))}}},")
        lines.append("  ]},")
    lines.extend(
        [
            "]",
            "",
            "[project.theme]",
            'variant = "classic"',
            'language = "zh"',
            "features = [",
            '  "content.action.edit",',
            '  "content.action.view",',
            '  "content.code.copy",',
            '  "content.code.select",',
            '  "content.tabs.link",',
            '  "navigation.footer",',
            '  "navigation.indexes",',
            '  "navigation.instant",',
            '  "navigation.instant.prefetch",',
            '  "navigation.instant.progress",',
            '  "navigation.path",',
            '  "navigation.sections",',
            '  "navigation.tabs",',
            '  "navigation.tabs.sticky",',
            '  "navigation.top",',
            '  "navigation.tracking",',
            '  "search.highlight",',
            '  "toc.follow",',
            "]",
            "font = false",
            'logo = "assets/legacy/assets/logo.svg"',
            'favicon = "assets/legacy/assets/logo.svg"',
            "",
            "[project.theme.icon]",
            'repo = "fontawesome/brands/github"',
            'edit = "material/pencil"',
            'view = "material/eye"',
            "",
            "[project.theme.icon.tag]",
            *[f'{identifier} = "{icon}"' for identifier, icon in TAG_ICONS.items()],
            "",
            "[[project.theme.palette]]",
            'media = "(prefers-color-scheme)"',
            'toggle.icon = "lucide/sun-moon"',
            'toggle.name = "跟随系统配色"',
            "",
            "[[project.theme.palette]]",
            'media = "(prefers-color-scheme: light)"',
            'scheme = "default"',
            'toggle.icon = "lucide/sun"',
            'toggle.name = "切换到深色模式"',
            "",
            "[[project.theme.palette]]",
            'media = "(prefers-color-scheme: dark)"',
            'scheme = "slate"',
            'toggle.icon = "lucide/moon"',
            'toggle.name = "切换到系统配色"',
            "",
            "[project.extra.tags]",
            *[f'{toml_string(tag)} = "{identifier}"' for tag, identifier in TAG_DEFINITIONS],
            "",
            "[[project.extra.social]]",
            'icon = "fontawesome/brands/github"',
            'link = "https://github.com/nuist-engineer-lion/docs"',
            'name = "GitHub 仓库"',
            "",
            "[project.markdown_extensions.abbr]",
            "[project.markdown_extensions.admonition]",
            "[project.markdown_extensions.attr_list]",
            "[project.markdown_extensions.def_list]",
            "[project.markdown_extensions.footnotes]",
            "[project.markdown_extensions.md_in_html]",
            "[project.markdown_extensions.toc]",
            "permalink = true",
            "[project.markdown_extensions.pymdownx.betterem]",
            "[project.markdown_extensions.pymdownx.caret]",
            "[project.markdown_extensions.pymdownx.details]",
            "[project.markdown_extensions.pymdownx.highlight]",
            "anchor_linenums = true",
            'line_spans = "__span"',
            "pygments_lang_class = true",
            "[project.markdown_extensions.pymdownx.inlinehilite]",
            "[project.markdown_extensions.pymdownx.keys]",
            "[project.markdown_extensions.pymdownx.mark]",
            "[project.markdown_extensions.pymdownx.smartsymbols]",
            "[project.markdown_extensions.pymdownx.superfences]",
            "[project.markdown_extensions.pymdownx.tabbed]",
            "alternate_style = true",
            "combine_header_slug = true",
            "[project.markdown_extensions.pymdownx.tasklist]",
            "custom_checkbox = true",
            "[project.markdown_extensions.pymdownx.tilde]",
            "",
        ]
    )
    (ROOT / "zensical.toml").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not OLD_ROOT.exists():
        raise SystemExit(f"old docs directory not found: {OLD_ROOT}")
    pages = discover_pages()
    source_to_dest = {page.source.resolve(): page.dest for page in pages}
    title_to_dest = {page.title: page.dest for page in pages}

    clean_output()
    copy_assets()
    for page in sorted(pages, key=sort_key):
        write_page(page, source_to_dest, title_to_dest)
    write_section_indexes(pages)
    write_home()
    write_config(pages)
    print(f"Generated {len(pages)} pages in {DOCS_DIR}")


if __name__ == "__main__":
    main()
