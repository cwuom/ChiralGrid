from util import logger

# ** 渲染设置 **
# 启用作弊模式：高亮显示手性碳区域
# 如果你不知道什么是手性碳，请把这一项改为 True
cheating = True

# 控制绘制元素符号的圆形区域大小，避免符号与化学键重叠
base_elem_padding = 63

# 控制化学键线条的宽度
base_line_width = 3

# 控制字体大小（会根据图像尺寸动态调整）
base_font_size = 30

# 控制输出图像分辨率（提高清晰度）
dpi = 500

# 控制网格大小，当此项为 0 或小于 0 时则不渲染网格
base_grid_size = 800

# ** 日志与数据持久化设置 **
# 设置日志等级
log_level = logger.LEVEL_DEBUG

# 是否保存网格数据
save_grid = True
