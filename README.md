# YamlChanger

## 项目概述

YamlChanger是一个包含YAML文件编辑和Vehicle内容批量替换功能的工具集，专门用于处理包含TestCase结构的YAML文件。

## 主要功能

### 1. YAML Editor (YamlChange_noQT.py)
- **图形化编辑界面** - 直观的层级导航和属性编辑
- **多文件支持** - 同时加载和编辑多个YAML文件
- **拖拽功能** - 直接拖拽文件到界面进行加载
- **嵌套结构支持** - 支持复杂的嵌套属性编辑
- **实时预览** - 实时显示当前选中属性的值

### 2. YAML Block Replacer (vehicle_replacer.py)
- **批量替换** - 使用模板文件批量替换任意块（Vehicle、Catalog、Environment 等）
- **自动备份** - 在目标文件同级目录创建yaml_backup文件夹
- **字段同步** - 当块为Vehicle时，自动更新TestCase.Name和TestCase.Filename
- **进度跟踪** - 实时显示处理进度和结果

## 文件结构

```
YamlChanger/
├── YamlChange_noQT.py          # 主YAML编辑器
├── vehicle_replacer.py         # Vehicle批量替换工具
├── start_vehicle_replacer.py   # Vehicle替换工具启动器
├── Austauchen/                 # 测试数据文件夹
│   ├── *.yaml                  # YAML测试文件
│   └── yaml_backup/            # 备份文件
├── default_testcase.yaml       # 默认测试用例模板
├── README.md                   # 本文件
├── INSTALL.txt                 # 安装说明
└── RELEASE_NOTES.txt           # 版本更新记录
```

## 使用方法

### YAML编辑器
```bash
python YamlChange_noQT.py
```

### Vehicle批量替换器
```bash
python start_vehicle_replacer.py
```

## 安装要求

- Python 3.6+
- tkinter (通常随Python安装)
- pyyaml
- tkinterdnd2

## 安装依赖

```bash
pip install pyyaml tkinterdnd2
```

## 主要特性

### YAML编辑器特性
- 支持Vehicle、Sensors等主要分类
- 支持Seat、Door等子分类
- 支持嵌套属性编辑（如SeatPosition的BackrestTilt、Position）
- 支持Item属性的子属性编辑

### Vehicle替换器特性
- 模板驱动的批量处理
- 智能文件名验证
- 自动备份和错误恢复
- 详细的处理日志

## 注意事项

1. 所有YAML文件必须包含TestCase结构
2. Vehicle替换会修改原始文件，请确保有备份
3. 文件名必须符合特定格式：`YYYY_MM_DD_HHMMSS_VEHICLECODE_VERSION.yaml`
4. 备份文件保存在目标文件同级目录的yaml_backup文件夹中

## 版本历史

详见 RELEASE_NOTES.txt

## 技术支持

如有问题，请检查：
1. Python版本是否符合要求
2. 依赖包是否正确安装
3. YAML文件格式是否正确
4. 文件路径是否有效