# OneDrive Redirect Manager☁️🔗

**OneDrive Redirect Manager** 是一款面向 Windows 桌面用户的轻量级 OneDrive 目录重定向管理工具。软件通过 Windows `junction` 链接，将本地软件、游戏或工具原本使用的数据目录重定向到 OneDrive 工作目录中，使原软件仍然访问原路径，而真实数据保存在 OneDrive 中。

当前稳定版本为 **v0.1.0**，主要面向游戏存档、软件配置、轻量数据目录和个人常用文件夹的 OneDrive 同步场景。软件以“本地源文件夹 → OneDrive 目标文件夹”的映射管理为核心，提供图形化的新建、编辑、删除、恢复和冲突处理流程。

---

## 🚀 下载与运行


---

## ✨ 主要功能

### 1. OneDrive 工作目录设置

用户可以在设置页面中选择一个 OneDrive 内部文件夹作为本工具的工作目录，例如：

```text
D:\RyanC\OneDrive\应用\Saved\ODR
```

软件会在该目录下维护：

```text
ODR
├─ config.json
├─ data
└─ backups
```

其中：

* `config.json` 用于保存项目配置
* `data` 用于保存真实同步数据
* `backups` 用于保存冲突处理时产生的本地备份

---

### 2. 新建目录重定向项目

用户可以通过图形界面创建一条新的目录重定向关系：

```text
本地源文件夹 → OneDrive 目标文件夹
```

例如：

```text
D:\Games\ExampleSave
        ↓ junction
D:\RyanC\OneDrive\应用\Saved\ODR\data\example-save
```

创建完成后，原软件仍然访问：

```text
D:\Games\ExampleSave
```

但真实数据将保存在 OneDrive 工作目录中，并由 OneDrive 客户端负责同步。

---

### 3. 自动状态处理

软件会根据本地目录和 OneDrive 目标目录的实际状态自动选择处理方式：

| 本地目录状态 | OneDrive 目标状态 | 软件行为 |
| --- | --- | --- |
| 本地有数据 | 云端不存在或为空 | 将本地数据迁移到 OneDrive，并创建 junction |
| 本地为空 | 云端有数据 | 删除本地空入口，并创建指向云端的 junction |
| 本地为空 | 云端为空 | 直接创建 junction |
| 本地不存在 | 云端已存在 | 直接创建 junction |
| 本地和云端都有数据 | 两边都有内容 | 进入冲突处理流程 |

如果本地路径已经是错误 junction、坏 junction 或危险路径，软件会拒绝自动处理，避免误删数据。

---

### 4. 冲突处理

当本地目录和 OneDrive 目标目录中都存在数据时，软件不会直接覆盖任何一边，而是会弹出冲突提示。

当前支持的处理方式包括：

* 取消操作，保持当前状态不变
* 备份本地目录，并使用 OneDrive 中的数据

该设计优先保证数据安全，避免用户在未确认的情况下覆盖已有目录。

---

### 5. 删除项目

删除项目时，用户可以分别决定是否删除 OneDrive 目标目录和本地 junction 链接。

| 删除选项 | 实际效果 |
| --- | --- |
| 不勾选任何选项 | 只删除项目配置，不删除本地链接和云端数据 |
| 只删除 OneDrive 目标文件夹 | 删除云端真实数据，保留本地链接入口 |
| 只删除本地链接 | 删除本地 junction 入口，保留云端数据 |
| 两个都勾选 | 先删除本地 junction，再删除云端目标目录，最后删除配置 |

推荐在彻底删除某个项目时，同时勾选：

```text
删除 OneDrive 中的目标文件夹
删除本地链接
```

这样可以避免留下指向已删除目录的坏 junction。

---

### 6. 恢复到本地并取消同步

如果不想继续使用 OneDrive 同步某个项目，可以使用“恢复到本地并取消同步”。

软件会执行以下操作：

1. 删除本地 junction 链接
2. 重新创建真实本地目录
3. 将 OneDrive 中的数据复制回本地
4. 删除项目配置记录
5. 默认保留 OneDrive 中的原始数据目录

---

### 7. 操作中提示

对于新建、删除、恢复等可能耗时的文件操作，软件会显示全局操作中提示，并使用不确定进度条表示当前正在处理。

该功能主要用于避免真实 OneDrive 同步目录在删除、复制或刷新时造成界面卡顿。

---

## 📌 基本使用流程

建议按以下流程使用：

```text
设置 OneDrive 工作目录 → 新建项目 → 选择本地目录与 OneDrive 路径 → 创建 junction → 由 OneDrive 同步数据
```

### 1. 设置 OneDrive 工作目录

首次启动软件后，进入设置页面，选择一个 OneDrive 内部目录作为工作目录。

推荐示例：

```text
D:\RyanC\OneDrive\应用\Saved\ODR
```

### 2. 新建项目

点击“新建”，填写项目 ID、显示名称、本地源文件夹和 OneDrive 相对路径。

示例：

```text
ID：game-save
名称：游戏存档
本地源文件夹：D:\Games\ExampleSave
OneDrive 路径：data/game-save
```

### 3. 确认创建

软件会根据目录状态自动完成数据迁移、空目录处理或冲突提示。

### 4. 使用原软件

创建完成后，原软件无需修改设置，继续访问原路径即可。真实数据会通过 junction 保存到 OneDrive 中。

### 5. 管理或删除项目

后续可以在主界面中刷新状态、编辑项目、删除项目或恢复到本地。

---

## 🧪 使用示例

### 游戏存档同步

某游戏默认将存档保存在：

```text
D:\Games\FireAxe\SaveData
```

用户希望将存档保存到 OneDrive 中进行同步，可以在 OneDrive Redirect Manager 中新建项目：

```text
ID：fireaxe-save
名称：FireAxe 存档
本地源文件夹：D:\Games\FireAxe\SaveData
OneDrive 路径：data/fireaxe-save
```

创建完成后：

* 游戏仍然读取 `D:\Games\FireAxe\SaveData`
* 真实存档保存在 OneDrive 工作目录中
* OneDrive 客户端负责同步这些真实数据

该案例适合展示软件从本地固定路径到 OneDrive 目录同步的完整流程。

---

## ⚠️ 使用注意事项

当前版本会进行真实文件系统操作，使用前请注意：

* 不要将磁盘根目录作为本地源文件夹
* 不要将系统目录作为本地源文件夹
* 不要将用户主目录作为本地源文件夹
* 不要将 OneDrive 根目录本身作为本地源文件夹
* 不要将本地源路径设置在 OneDrive 工作目录内部
* 删除 OneDrive 目标目录前，请确认其中数据不再需要
* 如果 OneDrive 正在同步，删除或迁移目录可能需要几秒钟
* 建议首次使用时先用测试目录熟悉流程

软件会尽量阻止危险路径，并在删除 junction 时只删除链接入口，不递归删除链接目标。

---

## 🧹 卸载方式

OneDrive Redirect Manager 当前以绿色版形式发布。

卸载软件本体时，直接删除解压后的软件文件夹即可。

如果需要彻底清理本机配置和日志，可以删除：

```text
%APPDATA%\OneDriveRedirector
```

如果需要清理 OneDrive 工作目录，需要手动删除用户曾经选择的工作目录，例如：

```text
D:\RyanC\OneDrive\应用\Saved\ODR
```

请注意：删除 OneDrive 工作目录会删除其中保存的数据，请确认后再操作。

---

## 🛠️ 技术栈

| 模块 | 技术 |
| --- | --- |
| 开发语言 | Python |
| 桌面界面 | PySide6 + QML |
| 链接机制 | Windows junction |
| 配置格式 | JSON |
| 后台任务 | QThreadPool + QRunnable |
| 测试工具 | pytest |
| 打包工具 | PyInstaller |
| 运行平台 | Windows 10 / Windows 11 |

---

## 🧱 软件架构

OneDrive Redirect Manager 采用轻量分层设计，主要包括：

```text
OneDriveRedirectManager/
├─ run.py                              # 程序入口
├─ assets/                             # 软件图标资源
├─ src/
│  └─ onedrive_redirector/
│     ├─ app.py                        # 应用启动逻辑
│     ├─ core/                         # 文件操作、配置、状态判断、junction 逻辑
│     └─ ui/                           # Controller 与 QML 界面
├─ tests/                              # 自动化测试
├─ docs/                               # 文档与截图
└─ dist/                               # 打包输出目录
```

软件内部将文件系统操作、状态判断、项目配置和 QML 界面分离，便于后续扩展错误修复建议、状态详情页和日志查看器等功能。

---

## ⚡ 从源码运行

本教程面向开发者。

克隆项目：

```bash
git clone https://github.com/ryancyx/OneDriveRedirectManager.git
cd OneDriveRedirectManager
```

创建并激活虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

安装依赖：

```powershell
pip install -r requirements.txt
```

运行软件：

```powershell
python run.py
```

---

## 🧪 测试与验证

运行自动化测试：

```powershell
python -m compileall run.py src tests
python -m pytest
```

当前版本已完成以下关键验收：

* 本地有数据，云端为空
* 本地为空，云端有数据
* 本地为空，云端为空
* 本地不存在，云端存在
* 冲突取消
* 冲突时备份本地并使用云端
* 恢复到本地并取消同步
* 四种删除组合
* 中文项目名与中文路径
* 真实 OneDrive 目录删除
* 操作中 busy overlay 提示
* PyInstaller one-dir 绿色版打包

---

## 📦 打包绿色版

```powershell
python -m PyInstaller run.py `
  --name OneDriveRedirectManager `
  --windowed `
  --noconfirm `
  --clean `
  --paths src `
  --collect-submodules onedrive_redirector `
  --icon assets\OneDriveRedirectManager.ico `
  --add-data "assets\OneDriveRedirectManager.ico;assets" `
  --add-data "src\onedrive_redirector\ui\qml;onedrive_redirector\ui\qml"
```

打包完成后发布整个目录：

```text
dist\OneDriveRedirectManager
```

不要只发布单个 `.exe` 文件。

---

## 📦 当前版本

当前稳定版本：**v0.1.0**

### v0.1.0 已完成功能

* 单 OneDrive 工作目录管理
* 多项目目录重定向管理
* 本地路径到 OneDrive 路径的 junction 创建
* 本地数据迁移到 OneDrive
* 云端数据链接到本地原路径
* 空目录状态自动处理
* 冲突检测与本地备份
* 恢复到本地并取消同步
* 四种删除策略
* 中文路径与中文项目名支持
* 真实 OneDrive 目录删除 fallback
* 操作中 busy overlay
* Windows 绿色版封装

---

## ⚠️ 当前限制

当前版本仍处于轻量级桌面工具阶段，主要限制包括：

* 当前仅面向 Windows 平台
* 当前主要使用 Windows junction，不支持 Linux/macOS
* 当前不提供跨设备自动合并冲突
* 当前不内置 OneDrive 账号登录或同步能力
* 当前不替代 OneDrive 客户端，只负责目录重定向管理
* 当前不建议管理超大型目录或系统关键目录

---

## 🗺️ 后续计划

后续版本计划继续扩展：

* 更清晰的错误修复建议
* 项目状态详情页
* 日志查看器
* 坏 junction 检测
* 一键清理失效项目
* 更完善的新手引导
* 更正式的安装包
* 更完整的项目导入与导出

---

## 📚 项目用途

本项目可用于：

* 游戏存档同步
* 软件配置同步
* OneDrive 目录重定向管理
* Windows junction 图形化管理实践
* Python + QML 桌面软件开发实践
* 个人轻量工具软件开发展示
* 软件著作权材料支撑

---

## 👤 开发相关

* 开发者：Developed by Ryan Cheung [@ryancyx](https://github.com/ryancyx)
* 项目类型：个人轻量级 Windows 桌面工具
* 主要技术：Python + PySide6 + QML + PyInstaller

---

## 📄 License

MIT License

