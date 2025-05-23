"""
配置文件，存储应用程序的基本设置
"""

# 文件名规则的正则表达式
FILENAME_PATTERN = r'20\d{2}_\d{2}_\d{2}_\d{6}'

# 文件完整性检查所需的最小文件数量
FILES_PER_TEST = 4

# 界面设置
WINDOW_TITLE = "文件名检查工具"
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400

# 结果窗口设置
RESULT_WINDOW_TITLE = "对比结果"
RESULT_WINDOW_WIDTH = 600
RESULT_WINDOW_HEIGHT = 400 