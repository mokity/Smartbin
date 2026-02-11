# 🧠 SmartBin — 智能桌面归档箱

> 拖拽即整理！像扔垃圾一样简单，却让桌面焕然一新。

![demo-gif](assets/demo.gif) <!-- 放一个动图演示 -->

## ✨ 特性
- 🖱️ **拖拽交互**：将文件拖到悬浮图标，自动分类
- 🔍 **多级识别**：后缀名 + 文件头 + 内容分析
- 📁 **自动建文件夹**：在桌面创建“照片”、“文档”等目录
- ↩️ **一键撤销**：误操作？立刻还原！

## 🛠️ 技术栈
- 前端：Electron + React
- 识别引擎：`file-type` + 自定义规则
- 平台：Windows / macOS

## ▶️ 快速开始
```bash
git clone https://github.com/yourname/smartbin.git
cd smartbin
npm install
npm start
