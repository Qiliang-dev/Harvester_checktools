# NameCheck 文件名检查工具 - 原始单文件版本

## 项目说明

这是一个文件名检查工具，用于比较Excel文件中的文件名与文件夹中的文件，检查文件完整性。

## 功能特性

- 选择Excel文件和文件夹进行比较
- 支持Excel多Sheet选择
- 检查文件完整性（每个测试编号应有4个文件）
- 检测重复文件名
- 显示比较结果
- 支持为文件名添加后缀
- 支持复制结果（保留换行或单行格式）

## 文件结构

```
NameCheck/
├── NameCheck_original.py    # 还原后的单文件版本
├── requirements.txt         # Python依赖包
└── README_original.md      # 本说明文档
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

1. 直接运行Python文件：
   ```bash
   python NameCheck_original.py
   ```

2. 在程序界面中：
   - 选择Excel文件（.xlsx格式）
   - 选择要比较的Sheet
   - 选择要比较的文件夹
   - 点击"开始比较"按钮

## 文件名格式要求

程序会识别符合以下格式的文件名：
- 格式：`20xx_xx_xx_xxxxxx`
- 示例：`2024_01_15_123456`

## 系统要求

- Python 3.6+
- tkinter（通常随Python安装）
- pandas
- openpyxl

## 注意事项

- 确保Excel文件格式为.xlsx
- 文件夹中应包含要比较的文件
- 每个测试编号通常需要4个相关文件
