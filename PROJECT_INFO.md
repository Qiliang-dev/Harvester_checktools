# NameCheck 独立项目

本项目是从 Harvester_Checktools 项目中提取出来的独立 NameCheck 工具。

## 项目说明

NameCheck 是一个用于比较 Excel 文件和文件夹中文件名的工具，特别适用于检查测试文件的完整性。

## 项目结构

```
NameCheck_Standalone/
│
├── src/                      # 源代码目录
│   ├── __init__.py          # Python包标记文件
│   ├── main.py              # 主程序入口
│   ├── file_utils.py        # 文件处理相关功能
│   ├── excel_utils.py       # Excel处理相关功能
│   └── ui/                  # UI相关代码
│       ├── __init__.py      # Python包标记文件
│       ├── main_window.py   # 主窗口
│       └── result_window.py # 结果窗口
│
├── config/                  # 配置文件目录
│   └── settings.py          # 配置参数
│
├── tests/                   # 测试代码目录
│   └── __init__.py          # Python包标记文件
│
├── Namecheck.py             # 应用程序入口点（模块化版本）
├── NameCheck_original.py    # 原始单文件版本
├── requirements.txt         # 项目依赖
├── README.md               # 主要说明文档
├── README_original.md      # 原始说明文档
├── build_detailed.py       # 详细构建脚本
├── build_exe.bat          # 构建批处理文件
├── 快速打包Namechecker.bat  # 快速打包脚本
├── Namechecker_1.2.spec   # PyInstaller配置文件
└── 打包说明.txt            # 打包说明文档
```

## 功能特点

- 从Excel文件中提取符合特定格式的文件名
- 检查文件夹中文件的完整性（每个测试号是否有足够的文件）
- 比较Excel和文件夹中的文件名差异
- 检测Excel中的重复文件名
- 显示当前Excel文件中不同测试编号的数量
- 支持为结果添加后缀
- 支持复制结果为单行或保留换行格式

## 使用方法

### 运行模块化版本
```bash
python Namecheck.py
```

### 运行原始单文件版本
```bash
python NameCheck_original.py
```

## 依赖安装

```bash
pip install -r requirements.txt
```

## 构建可执行文件

使用提供的批处理文件：
```bash
# 快速构建
./快速打包Namechecker.bat

# 或使用详细构建脚本
python build_detailed.py
```

## 版本信息

- 当前版本：1.2
- 提取日期：2025年9月19日
- 原项目：Harvester_Checktools

## 许可证

本项目继承原项目的许可证条款。
