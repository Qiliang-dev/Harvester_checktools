# NameCheck 文件名比较工具

NameCheck是一个用于比较Excel文件和文件夹中文件名的工具，特别适用于检查测试文件的完整性。

## 功能特点

- 从Excel文件中提取符合特定格式的文件名
- 检查文件夹中文件的完整性（每个测试号是否有足够的文件）
- 比较Excel和文件夹中的文件名差异
- 检测Excel中的重复文件名
- 显示当前Excel文件中不同测试编号的数量
- 支持为结果添加后缀
- 支持复制结果为单行或保留换行格式

## 项目结构

```
NameCheck/
│
├── src/                    # 源代码目录
│   ├── __init__.py         # Python包标记文件
│   ├── main.py             # 主程序入口
│   ├── file_utils.py       # 文件处理相关功能
│   ├── excel_utils.py      # Excel处理相关功能
│   └── ui/                 # UI相关代码
│       ├── __init__.py     # Python包标记文件
│       ├── main_window.py  # 主窗口
│       └── result_window.py # 结果窗口
│
├── config/                 # 配置文件目录
│   └── settings.py         # 配置参数
│
├── tests/                  # 测试代码目录
│   └── __init__.py         # Python包标记文件
│
├── README.md               # 项目说明文档
└── namecheck.py            # 应用程序入口点
```

## 使用方法

1. 运行`namecheck.py`启动应用程序
2. 选择Excel文件和要比较的文件夹
3. 选择Excel中的sheet
4. 点击"开始比较"按钮
5. 查看比较结果，可以添加后缀或复制结果

## 开发环境

- Python 3.6+
- 依赖库：
  - pandas
  - tkinter
  - tkinterdnd2 (可选，用于拖放功能)

## 自定义配置

您可以在`config/settings.py`中修改以下配置：
- 文件名匹配模式
- 每个测试所需的最小文件数
- 界面设置

## 许可证

[MIT License](LICENSE)

if pandas lib not exist, then

```python
pip install pandas
```

if Missing optional dependency "openpyxl". Use pip or conda to install openpyxl.

```python
pip install openpyxl
```

