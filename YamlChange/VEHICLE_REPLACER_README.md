# Vehicle Content Replacer 使用说明

## 功能概述

Vehicle Content Replacer 是一个专门用于替换YAML文件中Vehicle整块内容的工具。该工具可以将H022296文件的Vehicle内容完整地替换到DA00097文件中。

## 主要功能

1. **整块Vehicle内容替换** - 将源文件的Vehicle部分完整替换到目标文件
2. **自动备份** - 操作前自动创建目标文件的备份
3. **差异预览** - 显示两个文件Vehicle部分的主要差异
4. **智能文件检测** - 自动检测Austauchen文件夹中的相关文件
5. **操作日志** - 详细记录操作过程和结果

## 使用方法

### 方法一：独立启动Vehicle替换器

```bash
python start_vehicle_replacer.py
```

### 方法二：从主YAML编辑器启动

1. 运行主程序：`python YamlChange_noQT.py`
2. 点击界面中的 "Vehicle Content Replacer" 按钮

### 方法三：直接运行

```bash
python vehicle_replacer.py
```

## 操作步骤

### 自动模式（推荐）

1. 确保Austauchen文件夹中包含以下文件：
   - `*H022296*.yaml` (源文件)
   - `*DA00097*.yaml` (目标文件)

2. 点击 **"快速替换"** 按钮
   - 程序会自动检测文件
   - 自动执行替换操作

### 手动模式

1. 点击 **"选择"** 按钮选择源文件 (H022296)
2. 点击 **"选择"** 按钮选择目标文件 (DA00097)
3. (可选) 点击 **"预览差异"** 查看将要替换的内容
4. 点击 **"执行替换"** 完成操作

## 替换内容详情

Vehicle部分包含以下主要内容会被替换：

### CarModel
- Model: 车型
- Variant: 变体 (NA5 → NA0)
- VIN: 车辆识别号
- RHD: 右舵驾驶标识

### OptionalEquipment
- 完整的可选装备列表
- 从54项装备 → 41项装备
- 包含装备代码和描述

### Engine
- 引擎状态和类型

### 车门信息
- DriverDoor, PassengerDoor, DriverRearDoor, PassengerRearDoor
- Tailgate, Hood
- 包含门窗状态和Item属性

### 座椅信息
- SeatLeftRow1, SeatLeftRow2, SeatRightRow1, SeatRightRow2, SeatMidRow2
- Dashboard, Trunk
- 包含座椅位置、乘员状态、安全带状态等

**重要说明**：Sensors不属于Vehicle部分，它是TestCase下的独立节点，不会被此工具替换。如需替换Sensors内容，请使用主YAML编辑器的常规功能。

## 安全特性

1. **自动备份**: 每次操作前自动创建带时间戳的备份文件
2. **操作确认**: 执行替换前会弹出确认对话框
3. **错误回滚**: 如果操作失败，会自动恢复原文件
4. **详细日志**: 记录操作的每个步骤和结果

## 文件结构要求

- 源文件和目标文件必须包含 `TestCase` 根节点
- `TestCase` 下必须包含 `Vehicle` 节点
- 文件必须是有效的YAML格式
- 文件编码建议使用UTF-8

## 故障排除

### 常见问题

1. **"未找到Austauchen文件夹"**
   - 确保在正确的目录下运行程序
   - 检查Austauchen文件夹是否存在

2. **"未找到H022296或DA00097文件"**
   - 检查文件名是否包含正确的识别码
   - 确保文件扩展名为.yaml

3. **"文件格式不正确"**
   - 验证YAML文件语法是否正确
   - 确保文件包含TestCase和Vehicle节点

4. **"替换失败"**
   - 检查文件是否被其他程序占用
   - 确认是否有写入权限
   - 查看详细错误信息

### 备份文件

- 备份文件格式：`原文件名.backup_YYYYMMDD_HHMMSS`
- 位置：与原文件相同目录
- 如需恢复，将备份文件重命名为原文件名即可

## 测试功能

运行测试脚本验证功能是否正常：

```bash
python test_vehicle_replacer.py
```

测试包括：
- 文件加载测试
- Vehicle内容提取测试
- 差异比较测试
- 替换操作测试
- 结果验证测试

## 技术实现

- **语言**: Python 3.7+
- **界面框架**: Tkinter
- **YAML处理**: PyYAML
- **文件操作**: 原生Python文件操作
- **备份机制**: shutil.copy2

## 版本信息

- **版本**: 1.0
- **兼容性**: Python 3.7+
- **依赖库**: PyYAML, Tkinter
- **支持平台**: Windows, Linux, macOS

---

**注意**: 使用本工具前建议手动备份重要文件，虽然程序会自动创建备份，但额外的安全措施总是有益的。
