import math
from typing import List, Optional

from config import log_level
from util import logger

from PIL import Image, ImageDraw, ImageFont

from util import chiral_carbon_helper

logger = logger.Logger(log_level, "ChiralGrid-log.txt")


def convert_ion(text):
    normal_chars = "0123456789+-"
    superscript_chars = "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻"

    mapping = str.maketrans(normal_chars, superscript_chars)
    converted_text = text.translate(mapping)
    return converted_text


class Atom:
    """
    定义原子的基本属性
    """

    def __init__(self, charge: int = 0, element: str = "", show_flag: int = 0,
                 hydrogen_count: int = 0, spare_space: int = 0, isotope: int = 0,
                 mapnum: int = 0, unpaired: int = 0, x: float = 0.0, y: float = 0.0,
                 z: float = 0.0, extra: Optional[List[str]] = None):
        self.charge = charge  # 净电荷
        self.element = element  # 元素符号 ("C", "H", "O")
        self.show_flag = show_flag  # 标志位, 默认为 0(SHOW_FLAG_DEFAULT)
        self.hydrogen_count = hydrogen_count  # 连接的氢原子数
        self.spare_space = spare_space  # 保留空间，用于标记方向
        self.isotope = isotope  # 同位素编号
        self.mapnum = mapnum  # 映射编号, 在合成路线追踪中有用
        self.unpaired = unpaired  # 未配对的电子数

        # 原子坐标
        self.x = x
        self.y = y
        self.z = z

        # 额外信息 默认为空
        self.extra = extra if extra is not None else []


class Bond:
    """
    定义化学键的基本属性
    """

    def __init__(self, from_atom: int = 0, to: int = 0, type_: int = 0,
                 stereo_direction: int = 0, extra: Optional[List[str]] = None):
        self.from_atom = from_atom  # 起始端点
        self.to = to  # 结束端点
        self.type = type_  # 类型 （单键、双键、三键..）

        # 键的方向 默认为 0(DIRECTION_UNSPECIFIED)
        self.stereo_direction = stereo_direction
        self.extra = extra if extra is not None else []


class Molecule:
    """
    定义分子的基本属性
    """

    SHOW_FLAG_DEFAULT = 0
    SHOW_FLAG_EXPLICIT = 1

    # 键的立体方向
    DIRECTION_UNSPECIFIED = 0  # 未指定
    DIRECTION_TOP = 1  # 指向上方
    DIRECTION_BOTTOM = 2  # 指向下方
    DIRECTION_LEFT = 4  # 指向左边
    DIRECTION_RIGHT = 8  # 指向右边

    def __init__(self, cid: int, atoms: List[Atom], bonds: List[Bond], mdl_mol_str: str):
        self.draw = None
        self.cid = cid
        self.atoms = atoms
        self.bonds = bonds
        self.mdl_mol_str = mdl_mol_str

        # 坐标范围
        self.max_x = 0.0
        self.max_y = 0.0
        self.min_x = 0.0
        self.min_y = 0.0

        self.inval_min_max = True  # 坐标范围无效
        self.avg_bond_length = 0.0  # 平均键长

    def determine_min_max(self):
        """
        确定分子中所有原子的最大和最小坐标值
        """

        self.inval_min_max = False  # 坐标范围有效
        if not self.atoms:
            self.max_y = self.min_y = self.max_x = self.min_x = 0.0
            return
        atom_x = self.atom_x(1)
        self.max_x = self.min_x = atom_x
        atom_y = self.atom_y(1)
        self.max_y = self.min_y = atom_y
        for n in range(2, len(self.atoms) + 1):
            x = self.atom_x(n)
            y = self.atom_y(n)
            self.min_x = min(self.min_x, x)
            self.max_x = max(self.max_x, x)
            self.min_y = min(self.min_y, y)
            self.max_y = max(self.max_y, y)

    def get_atom(self, n):
        """
        获取指定索引的原子对象
        :param n:
        :return: Atom
        """

        if n < 1 or n > len(self.atoms):
            raise IndexError(f"Atoms: get {n}, numAtoms={len(self.atoms)}")
        return self.atoms[n - 1]

    def get_bond(self, n: int) -> Bond:
        """
        获取指定索引的化学键对象
        :param n:
        :return: Bond
        """

        if 1 <= n <= len(self.bonds):
            return self.bonds[n - 1]
        raise IndexError(f"Bonds: get {n}, numBonds={len(self.bonds)}")

    def get_atom_index_near(self, x: float, y: float, tolerance: float) -> int:
        """
        查找距离给定坐标最近的原子索引
        :param x: x
        :param y: y
        :param tolerance: 容差
        :return: 最近原子的索引，如果没有找到符合条件的原子，则返回 -1
        """

        if not self.atoms:
            return -1
        closest_index = 1
        min_distance = float("inf")
        for i, atom in enumerate(self.atoms):
            dist = (atom.x - x) ** 2 + (atom.y - y) ** 2
            if dist < min_distance:
                closest_index = i + 1
                min_distance = dist
        return closest_index if min_distance < tolerance ** 2 else -1

    def atom_count(self) -> int:
        """
        获取分子中的原子数
        """

        return len(self.atoms)

    def bond_count(self) -> int:
        """
        获取分子中的化学键数
        """

        return len(self.bonds)

    # ------------------- 获取指定原子的坐标值 -------------------
    def atom_x(self, index):
        return self.atoms[index - 1].x

    def atom_y(self, index):
        return self.atoms[index - 1].y

    def atom_z(self, n: int) -> float:
        return self.get_atom(n).z

    # ------------------- 获取分子在 X 轴和 Y 轴上的跨度 -------------------
    def range_x(self) -> float:
        return self.max_x - self.min_x

    def range_y(self) -> float:
        return self.max_y - self.min_y

    # ------------------- 返回分子的最大最小坐标值 -------------------
    def min_x(self) -> float:
        if self.inval_min_max:
            self.determine_min_max()
        return self.min_x

    def max_x(self) -> float:
        if self.inval_min_max:
            self.determine_min_max()
        return self.max_x

    def min_y(self) -> float:
        if self.inval_min_max:
            self.determine_min_max()
        return self.min_y

    def max_y(self) -> float:
        if self.inval_min_max:
            self.determine_min_max()
        return self.max_y

    # ------------------- 获取原子或化学键在列表中的索引 -------------------

    def get_atom_id(self, atom: Atom) -> int:
        for i, a in enumerate(self.atoms):
            if atom == a:
                return i + 1
        return -1

    def get_bond_id(self, bond: Bond) -> int:
        for i, b in enumerate(self.bonds):
            if bond == b:
                return i + 1
        return -1

    # --------------------------------------------------

    def get_atom_declared_bonds(self, atom_index: int) -> List[Bond]:
        """
        获取指定原子所关联的所有键（bonds）

        @param atom_index: 指定要查找其关联键的原子的索引号

        @return:
        List[Bond]: 一个包含与指定原子关联的所有键的列表。
        """

        if atom_index < 1 or atom_index > len(self.atoms):
            raise IndexError(f"Invalid atom index: {atom_index}. Must be between test and {len(self.atoms)}")

        ret = []
        for b in self.bonds:
            if b.from_atom == atom_index or b.to == atom_index:
                ret.append(b)

        return ret

    def get_average_bond_length(self) -> float:
        """
        返回分子的平均键长
        """
        return self.avg_bond_length

    def draw_bond(self, atom1, atom2, bond_type, scale, offset_x, offset_y, line_width):
        """
        绘制化学键

        :param atom1: 起始原子
        :param atom2: 终止原子
        :param bond_type: 键的类型
        :param scale: 缩放比例
        :param offset_x: x轴偏移量
        :param offset_y: y轴偏移量
        :param line_width: 线条宽度
        """

        start_x = int(atom1.x * scale + offset_x)
        start_y = int(atom1.y * scale + offset_y)
        end_x = int(atom2.x * scale + offset_x)
        end_y = int(atom2.y * scale + offset_y)

        rad = math.atan2(end_y - start_y, end_x - start_x)
        delta = line_width / 6
        dx = math.sin(rad) * delta * 10
        dy = math.cos(rad) * delta * 10

        w1 = int(line_width * 0.8)

        if bond_type == 1:  # 单键
            self.draw.line((start_x, start_y, end_x, end_y), fill="black", width=line_width)
        elif bond_type == 2:  # 双键
            self.draw.line((start_x + dx / 2, start_y - dy / 2, end_x + dx / 2, end_y - dy / 2), fill="black",
                           width=w1)
            self.draw.line((start_x - dx / 2, start_y + dy / 2, end_x - dx / 2, end_y + dy / 2), fill="black",
                           width=w1)
        elif bond_type == 3:  # 三键
            self.draw.line((start_x, start_y, end_x, end_y), fill="black", width=w1)
            self.draw.line((start_x + dx, start_y - dy, end_x + dx, end_y - dy), fill="black", width=w1)
            self.draw.line((start_x - dx, start_y + dy, end_x - dx, end_y + dy), fill="black", width=w1)
        else:
            raise ValueError("Unknown bond type:", bond_type)

    def init_once(self):
        """
        初始化分子的一些属性
        """

        logger.info("Initializing molecular properties...")

        # 确定原子的氢原子数
        for i, atom in enumerate(self.atoms):
            bonds = self.get_atom_declared_bonds(i + 1)
            bond_type_sum = sum(b.type for b in bonds)
            logger.debug(f"bond_type_sum: {bond_type_sum}")
            if atom.hydrogen_count == 0:
                if atom.element == "C":
                    atom.hydrogen_count = max(0, 4 - atom.unpaired - abs(atom.charge) - bond_type_sum)
                elif atom.element in {"O", "S"}:
                    atom.hydrogen_count = max(0, 2 - atom.unpaired + atom.charge - bond_type_sum)
                elif atom.element in {"N", "P"}:
                    atom.hydrogen_count = max(0, 3 - atom.unpaired + atom.charge - bond_type_sum)
                elif atom.element in {"F", "Cl", "Br", "I"}:
                    atom.hydrogen_count = max(0, 1 - atom.unpaired - abs(atom.charge) - bond_type_sum)

            # 设置碳原子的显式标志
            if atom.element == "C":
                if len(bonds) == 2:  # 双键
                    t1 = math.atan2(self.atom_y(bonds[0].from_atom) - self.atom_y(bonds[0].to),
                                    self.atom_x(bonds[0].from_atom) - self.atom_x(bonds[0].to))
                    t2 = math.atan2(self.atom_y(bonds[1].from_atom) - self.atom_y(bonds[1].to),
                                    self.atom_x(bonds[1].from_atom) - self.atom_x(bonds[1].to))
                    if t1 < 0:
                        t1 += math.pi
                    if t2 < 0:
                        t2 += math.pi
                    if abs(t1 - t2) < 10 / 360 * 2 * math.pi:  # 方向相同
                        logger.debug(f"{atom} is a linear carbon")
                        atom.show_flag |= Molecule.SHOW_FLAG_EXPLICIT

            # 确定原子的 spare_space 方向标志
            top = bottom = left = right = 2 * math.pi
            for b in bonds:
                x1, y1 = self.atom_x(i + 1), self.atom_y(i + 1)
                x2, y2 = (self.atom_x(b.to), self.atom_y(b.to)) if b.from_atom == i + 1 else \
                    (self.atom_x(b.from_atom), self.atom_y(b.from_atom))
                dt = math.atan2(y2 - y1, x2 - x1)
                tmp = abs(dt - 0) % (2 * math.pi)
                right = min(right, tmp)
                tmp = min(abs(dt - math.pi), abs(dt + math.pi)) % (2 * math.pi)
                left = min(left, tmp)
                tmp = abs(dt - math.pi / 2) % (2 * math.pi)
                top = min(top, tmp)
                tmp = abs(dt + math.pi / 2) % (2 * math.pi)
                bottom = min(bottom, tmp)
            if right > 1.0:
                atom.spare_space = Molecule.DIRECTION_RIGHT
            elif left > 1.4:
                atom.spare_space = Molecule.DIRECTION_LEFT
            elif bottom > 1.0:
                atom.spare_space = Molecule.DIRECTION_BOTTOM
            else:
                atom.spare_space = Molecule.DIRECTION_UNSPECIFIED

        # 计算分子的平均键长
        total_length = sum(math.hypot(self.atom_x(b.from_atom) - self.atom_x(b.to),
                                      self.atom_y(b.from_atom) - self.atom_y(b.to))
                           for b in self.bonds)
        self.avg_bond_length = total_length / len(self.bonds) if self.bonds else 0.0

    def to_mdl_mol_string(self) -> str:
        """
        返回 MDL 分子字符串
        """

        return self.mdl_mol_str

    def render_molecule(self, base_elem_padding: int = 50, base_line_width: int = 5, base_font_size: int = 30,
                        dpi: int = 300, base_grid_size=700, cheating=False):
        """
        渲染分子模型

        :param cheating: 是否使用作弊模式，即直接高亮手性碳区域
        :param base_grid_size: 基础网格大小
        :param base_font_size: 基础字体大小
        :param base_line_width: 基础线条宽度
        :param base_elem_padding: 基础圆的长宽，用于留白，避免元素符号和线条重合
        :param dpi: 每英寸点数，用于控制输出图像的分辨率
        :return: Image Object
        """

        logger.info(f"Rendering molecule... cid={self.cid}")

        # 计算坐标
        self.determine_min_max()

        # 原始w, h，用于resize
        width = int(self.range_x() * 100 * 1.8)
        height = int(self.range_y() * 100 * 1.8)

        # 提高分辨率, 用于绘制，有利于抗锯齿
        high_res_width = int(width * 2.5)
        high_res_height = int(height * 2.5)

        logger.debug(f"base_w, base_h = ({high_res_width}, {high_res_height})")
        logger.debug(f"high_res_w, high_res_h = ({high_res_width}, {high_res_height})")

        image = Image.new("RGBA", (high_res_width, high_res_height), (255, 255, 255))
        self.draw = ImageDraw.Draw(image)

        # 计算缩放比例
        scale_x = high_res_width / self.range_x() if self.range_x() > 0 else 1
        scale_y = high_res_height / self.range_y() if self.range_y() > 0 else 1
        scale = min(scale_x, scale_y) * 0.8  # 留出一些边距

        # 计算坐标的偏移量以居中
        offset_x = (high_res_width - (self.max_x - self.min_x) * scale) / 2 - (self.min_x * scale)
        offset_y = (high_res_height - (self.max_y - self.min_y) * scale) / 2 - (self.min_y * scale)

        # 动态计算字体大小和线条宽度
        font_size = int(base_font_size * (min(width, height) / 500))

        logger.debug(f"font_size = {font_size}")
        base_grid_size = base_grid_size * (1 + font_size / 100)

        # 动态计算线条宽度
        line_width = int(base_line_width * (min(width, height) / 500))

        elem_padding = int(int(base_elem_padding * (min(width, height) / 1500)) * 0.8)

        # 防止元素符号重叠
        for i, atom_i in enumerate(self.atoms):
            for atom_j in self.atoms[i + 1:]:
                xi = int(atom_i.x * scale + offset_x)
                yi = int(atom_i.y * scale + offset_y)
                xj = int(atom_j.x * scale + offset_x)
                yj = int(atom_j.y * scale + offset_y)

                if abs(xi - xj) < base_elem_padding and abs(yi - yj) < base_elem_padding:
                    logger.warning(
                        f"Element symbols are too close: Atom {atom_i.element} at ({atom_i.x}, {atom_i.y}) and Atom {atom_j.element} at ({atom_j.x}, {atom_j.y}). "
                        f"Adjusting positions..")

                    dx = (base_elem_padding - abs(xi - xj)) // 2
                    dy = (base_elem_padding - abs(yi - yj)) // 2

                    if xi < xj:
                        atom_i.x -= dx / scale
                        atom_j.x += dx / scale
                    else:
                        atom_i.x += dx / scale
                        atom_j.x -= dx / scale

                    if yi < yj:
                        atom_i.y -= dy / scale
                        atom_j.y += dy / scale
                    else:
                        atom_i.y += dy / scale
                        atom_j.y -= dy / scale

                    logger.info(
                        f"Adjusted over: Atom {atom_i.element} at ({atom_i.x}, {atom_i.y}) and Atom {atom_j.element} at ({atom_i.x}, {atom_i.y}). ")

        logger.info(f"Drawing grid...")

        grid_display_flag = True

        # 绘制网格
        if base_grid_size <= 0:
            logger.warning("base_grid_size is less than or equal to 0, skipping grid drawing.")
            grid_display_flag = False

        grid_data = {}
        font = ImageFont.truetype("resource/font/MiSans-Medium.ttf", int(font_size * 1.2))  # 替换为实际字体路径

        if grid_display_flag:
            rows = math.ceil(high_res_height / base_grid_size)
            cols = math.ceil(high_res_width / base_grid_size)

            for row in range(rows):
                for col in range(cols):
                    grid_id = f"{chr(65 + row)}{col + 1}"
                    x0, y0 = col * base_grid_size, row * base_grid_size
                    x1, y1 = x0 + base_grid_size, y0 + base_grid_size

                    bg_color = "white"
                    if (row + col) % 2 == 1:
                        bg_color = "lightgray"
                        self.draw.rectangle([x0, y0, x1, y1], fill=bg_color)

                    grid_data[f"{grid_id}.elems"] = []
                    grid_data[grid_id] = {
                        "x0": x0,
                        "y0": y0,
                        "x1": x1,
                        "y1": y1,
                        "bg": bg_color,
                    }

        logger.info(f"Drawing bonds...")

        # 绘制化学键
        for bond in self.bonds:
            atom1 = self.atoms[bond.from_atom - 1]
            atom2 = self.atoms[bond.to - 1]
            self.draw_bond(atom1, atom2, bond.type, scale, offset_x, offset_y, line_width)

        logger.info(f"Drawing atoms...")
        chiral_carbon_regions = []
        # 绘制元素
        atom_index = 1
        for atom in self.atoms:
            x = int(atom.x * scale + offset_x)
            y = int(atom.y * scale + offset_y)
            circle_x0 = x - elem_padding
            circle_y0 = y - elem_padding
            circle_x1 = x + elem_padding
            circle_y1 = y + elem_padding

            # 转换离子符号
            charge_symbol = ""
            if atom.charge != 0:
                logger.info(f"Found ion with charge {atom.charge} for atom {atom.element} at ({x}, {y}).")
                charge_symbol = str(abs(atom.charge))
                if charge_symbol == "1":
                    charge_symbol = "+" if atom.charge > 0 else "-"
                else:
                    charge_symbol += "+" if atom.charge > 0 else "-"

                charge_symbol = convert_ion(charge_symbol)

            # 获取网格信息
            x0 = None
            y0 = None
            grid_bg = "white"
            grid_id = None
            if grid_display_flag:
                for grid_id, grid in grid_data.items():
                    try:
                        if (grid['x0'] <= x < grid['x1']) and (grid['y0'] <= y < grid['y1']):
                            grid_bg = grid["bg"]
                            x0 = grid['x0']
                            y0 = grid['y0']
                            grid_id = grid_id
                            break
                    except TypeError:
                        pass

            # 绘制元素符号，并留白
            if (atom.element != "C" or (atom.element == "C" and
                                        not ((atom.show_flag & Molecule.SHOW_FLAG_EXPLICIT) == 0))):
                logger.info(f"Drawing atom {atom.element} at ({x}, {y})")

                # 根据网格背景颜色来填充元素符号的留白区域
                self.draw.ellipse([circle_x0, circle_y0, circle_x1, circle_y1], fill=grid_bg)
                self.draw.text((x, y), atom.element + charge_symbol, fill="black", font=font, align="center",
                               anchor="mm")

            # 绘制氢原子
            if atom.hydrogen_count > 0:
                logger.info(f"Drawing hydrogen atoms for {atom.element} at ({x}, {y})")
                for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]:
                    self.draw.text((x + dx, y - 15 + dy), "H", fill=(200, 200, 200, 255), font=font, anchor="mm")
                self.draw.text((x, y - 15), "H", fill="black", font=font, anchor="mm")

            is_chiral_carbon = False
            if chiral_carbon_helper.is_chiral_carbon(self, atom_index):
                logger.info(f"chiral carbon -> @{atom_index}")
                if grid_display_flag:
                    if grid_id not in chiral_carbon_regions:
                        chiral_carbon_regions.append(grid_id)
                    if cheating:
                        self.draw.text((x0 + 10, y0 + 10), grid_id, fill="red", font=font)
                is_chiral_carbon = True

            if grid_id:
                if grid_display_flag:
                    # 绘制编号
                    self.draw.text((x0 + 5, y0 + 5), grid_id, fill="black", font=font)

                    grid_data[f"{grid_id}.elems"].append(
                        (x, y, atom.element, atom.hydrogen_count, atom.charge, atom_index, is_chiral_carbon))

            atom_index += 1

        image = image.resize((width, height), Image.LANCZOS)
        image.info["dpi"] = (dpi, dpi)

        logger.info(f"Render completely! cid={self.cid}")
        logger.info(f"grid_data -> {grid_data}")
        return image, grid_data, chiral_carbon_regions
