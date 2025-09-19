# YAML Editor - YAML文件编辑器

## 软件介绍

YAML Editor 是一个专门用于编辑 YAML 文件的图形化工具，特别适用于编辑包含 TestCase 结构的 YAML 文件。该软件提供了直观的界面，让用户能够轻松地浏览和修改 YAML 文件中的各种属性值。

## 主要功能

### 1. 文件加载
- **文件夹选择**: 点击 "Choose Folder" 按钮选择包含 YAML 文件的文件夹
- **拖拽功能**: 直接将 YAML 文件拖拽到指定区域进行加载
- **多文件支持**: 同时加载多个 YAML 文件进行批量编辑

### 2. 层级导航
- **主分类选择**: 选择 YAML 文件中的主要分类（如 Name、Description、time、TestNotes、Vehicle 等）
- **子分类选择**: 对于复杂结构，可以选择子分类（如 Vehicle 下的各种组件）
- **属性选择**: 选择具体的属性进行编辑
- **Item 属性**: 对于包含 Item 结构的属性，可以进一步选择子属性

### 3. 特殊功能
- **Vehicle 类型过滤**: 当选择 Vehicle 主分类时，提供 All/Seat/Door 三种过滤选项
- **实时编辑**: 在文本框中直接编辑属性值
- **批量更新**: 同时更新所有已加载文件中的相同属性

## 安装和使用

### 方法一：使用可执行文件（推荐）

1. **下载**: 下载 `YAML_Editor_Complete.exe` 文件（包含所有依赖）
2. **运行**: 双击运行，无需安装 Python 环境
3. **开始使用**: 软件会打开一个图形界面窗口

**注意**: 请使用 `YAML_Editor_Complete.exe` 而不是 `YAML_Editor.exe`，因为完整版本包含了所有必要的依赖库。

### 方法二：从源代码运行

#### 环境要求
- Python 3.7 或更高版本
- 必要的 Python 包

#### 安装步骤
```bash
# 安装依赖包
pip install tkinterdnd2 ruamel.yaml pyyaml

# 运行程序
python YamlChange_noQT.py
```

## 使用指南

### 1. 加载 YAML 文件

#### 方法一：选择文件夹
1. 点击 "Choose Folder" 按钮
2. 选择包含 YAML 文件的文件夹
3. 软件会自动加载文件夹中所有的 .yaml 文件

#### 方法二：拖拽文件
1. 直接将 YAML 文件拖拽到 "Drag and drop YAML files here" 区域
2. 软件会自动加载拖拽的文件

### 2. 选择要编辑的属性

#### 步骤一：选择主分类
- 在 "Choose Main Category" 下拉菜单中选择要编辑的主分类
- 例如：Name、Description、time、TestNotes、Vehicle 等

#### 步骤二：选择子分类（如果需要）
- 如果主分类包含子结构，在 "Choose Subcategory" 中选择子分类
- 对于 Vehicle 类型，可以使用 All/Seat/Door 过滤选项

#### 步骤三：选择属性
- 在 "Choose Property" 中选择具体的属性
- 如果属性包含 Item 结构，还可以在 "Item property" 中选择子属性

### 3. 编辑属性值

1. **查看当前值**: 在 "Current value" 文本框中查看当前属性值
2. **编辑内容**: 直接在文本框中修改内容
3. **更新文件**: 点击 "Update value" 按钮保存修改

### 4. 查看状态

- 状态栏会显示操作结果，如 "Update successfully" 或错误信息
- 文件夹路径会显示在界面上方

## 支持的 YAML 结构

软件支持以下 YAML 结构：

### 1. 简单值
```yaml
TestCase:
  Name: "Test Case Name"
  Description: "Test Description"
  time: "2024-01-01"
```

### 2. 嵌套结构
```yaml
TestCase:
  Vehicle:
    FrontSeat:
      OccupancySeat: "Driver"
      OccupancyComment: "Driver seat"
    RearSeat:
      OccupancySeat: "Passenger"
      OccupancyComment: "Rear passenger seat"
```

### 3. Item 结构
```yaml
TestCase:
  Vehicle:
    FrontSeat:
      Item:
        OccupancySeat: "Driver"
        OccupancyComment: "Driver seat"
```

## 功能特点

### 1. 智能识别
- 自动识别 YAML 文件的层级结构
- 根据数据结构动态调整界面选项
- 支持简单值和复杂结构的编辑

### 2. 批量操作
- 同时加载多个 YAML 文件
- 一次性更新所有文件中的相同属性
- 保持文件格式和缩进

### 3. 用户友好
- 直观的图形界面
- 拖拽文件支持
- 实时状态反馈
- 错误处理和提示

## 注意事项

### 1. 文件格式
- 仅支持包含 "TestCase" 根节点的 YAML 文件
- 文件编码应为 UTF-8
- 建议在编辑前备份原始文件

### 2. 操作建议
- 编辑前先确认选择的属性是否正确
- 修改后检查文件内容是否符合预期
- 对于重要文件，建议先在小文件上测试

### 3. 限制
- 当前版本主要支持 TestCase 结构的 YAML 文件
- 不支持数组类型的属性编辑
- 不支持添加新的属性或删除现有属性

## 故障排除

### 常见问题

#### 1. 文件加载失败
- **问题**: 点击 "Choose Folder" 后没有加载到文件
- **解决**: 检查文件夹中是否包含 .yaml 文件，文件是否包含 "TestCase" 节点

#### 2. 属性无法选择
- **问题**: 某些属性在下拉菜单中不可选
- **解决**: 确认 YAML 文件结构是否正确，属性是否存在

#### 3. 更新失败
- **问题**: 点击 "Update value" 后显示错误
- **解决**: 检查文件是否被其他程序占用，是否有写入权限

#### 4. 界面显示异常
- **问题**: 界面元素显示不正确
- **解决**: 尝试重新启动程序，检查系统分辨率设置

#### 5. 程序无法启动
- **问题**: 双击可执行文件后出现 "No module named 'yaml'" 错误
- **解决**: 请使用 `YAML_Editor_Complete.exe` 而不是 `YAML_Editor.exe`

## 版本信息

- **当前版本**: 1.0
- **支持平台**: Windows 10/11
- **开发语言**: Python
- **界面框架**: Tkinter
- **推荐可执行文件**: YAML_Editor_Complete.exe

## 技术支持

如果遇到问题或需要功能改进，请联系开发团队。

---

**注意**: 使用本软件编辑 YAML 文件时，建议先备份原始文件，以防意外情况发生。 