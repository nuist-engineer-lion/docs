import { defineConfig } from "vitepress";

const repairoSidebar = () => [
  {
    text: "重装系统",
    collapsible: true,
    items: [
      { text: "重装系统1", link: "/repair/windows-setup-1" },
      { text: "重装系统2", link: "/repair/windows-setup-2" },
      { text: "修复引导", link: "/repair/bootload-fix" },
      { text: "PE系统", link: "/repair/pe" },
    ],
  },
  {
    text: "系统维护",
    collapsible: true,
    items: [{ text: "安装软件", link: "/repair/installing-app" }],
  },
  // {
  //   text: "硬件故障排除",
  // },
];
const Nav = () => [
  {
    text: "修机",
    link: "/repair/index",
    activeMatch: "/repair",
  },
  {
    text: "PSPR",
    activeMatch: "/pspr",
    link: "/pspr",
  },
  {
    text: "摄影",
    link: "/shotting",
  },
];
export default defineConfig({
  lang: "zh-CN",
  title: "修机参考",
  description: "修机参考",
  themeConfig: {
    nav: Nav(),
    sidebar: {
      "/repair": repairoSidebar(),
    },
  },
});
