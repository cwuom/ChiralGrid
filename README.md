# ChiralGrid

**ChiralGrid** 是一个用于识别和标记分子手性碳区域的 Python 项目。项目实现了一个 GUI 程序，可用来加载分子文件（`.mol` 格式），渲染分子结构，并在网格化图像上标记手性碳区域。项目支持动态调整分子渲染参数、识别手性碳以及交互式提交答案。

----------

## 项目功能🔨

1.  **手性碳识别**：

    -   自动检测分子结构中的手性碳原子
    -   支持通过颜色或网格区域高亮显示手性碳区域（作弊模式）

2.  **分子结构渲染**：
    -   根据分子 `.mol` 文件渲染分子结构
     -   提供动态调整字体、线条宽度、网格大小的选项
     -   输出高分辨率的分子图像，支持 DPI 调整

3.  **交互式答题**：

    -   GUI 程序允许用户观察分子图像并输入手性碳所在的网格区域
    -   自动验证用户输入的答案是否正确

4.  **日志与数据持久化**：

    -   实时记录程序运行的日志
    -   支持保存分子图像与网格数据到本地

----------

## 文件结构📁

项目代码按照功能模块化，主要文件说明如下：

```bash
ChiralGrid/  
│  
├── config.py                    # 配置文件，包含渲染设置、日志设置等参数
├── main.py                      # 主程序入口，负责初始化 GUI 应用
│  
├── entity/                      # 分子实体模块
│   ├── __init__.py              # 分子实体初始化文件
│   ├── molecule.py              # 定义分子、原子、化学键的基本属性与渲染方法
│  
├── util/                        # 工具模块
│   ├── __init__.py              # 工具模块初始化文件
│   ├── chiral_carbon_helper.py  # 手性碳检测工具
│   ├── mdl_mol_parser.py        # MDL MOL 文件解析器
│   ├── logger.py                # 日志工具
│   ├── index_from.py            # 索引装饰器
│  
├── resource/                    # 资源文件
│   ├── mol/[*.mol]              # 存放分子的 `.mol` 文件  
│   ├── font/                    # 字体文件，用于分子渲染  
│  
└── result/                      # 输出目录  
 ├── [{cid}_molecule.png]        # 渲染的分子图像  
 ├── data/[{cid}_grid_data.json] # 包含分子网格信息的 JSON 数据  
```



----------

## 快速开始⚡

### 环境要求

-   **操作系统**：Windows、Linux 或 macOS

-   **Python 版本**：Python 3.7 或更高

-   **依赖库**:

    -   `Pillow`：用于图像处理和渲染。

    -   `tkinter`：用于 GUI 界面。

    -   其他内置库：如 `os`、`json`、`random` 等。

### 安装依赖

在项目目录下，运行以下命令安装依赖：

```bash
pip install -r requirements.txt
```

### 运行程序

执行以下命令启动 GUI 程序：

```bash
python main.py
```


----------

## 使用指南🧭

### 1. GUI 功能说明

-   **加载分子文件**：程序自动从 `resource/mol` 目录加载 `.mol` 文件。

-   **随机切换分子**：点击“看不清，换一题”按钮随机切换分子。

-   **查看网格编号**：在分子图像中找到手性碳区域的网格编号。

-   **提交答案**：在输入框中输入手性碳所在的网格编号，多个编号用逗号分隔（如 `A1,B2,C3`）。

-   **查看答案反馈**：程序会验证输入的网格编号是否正确，并给出“正确”或“错误”的提示。

### 2. 配置调整

可以通过修改 `config.py` 文件调整以下设置：

-   渲染设置：

    -   `cheating`：是否启用作弊模式（高亮手性碳区域）。

    -   `base_elem_padding`：元素符号的圆形区域大小。

    -   `base_line_width`：化学键线条宽度。

    -   `base_font_size`：字体大小。

    -   `dpi`：输出图像的分辨率。

    -   `base_grid_size`：网格大小。

-   日志设置：

    -   `log_level`：设置日志等级（`LEVEL_DEBUG`、`LEVEL_INFO`、`LEVEL_WARNING`、`LEVEL_ERROR`）。

    -   `save_grid`：是否保存网格数据。

### 3. 输出文件说明

-   分子图像：

    -   保存到 `result/` 目录，文件命名格式为 `{CID}_molecule.png`。

-   网格数据：

    -   保存到 `result/data/` 目录，文件命名格式为 `{CID}_grid_data.json`。

----------

## 核心模块功能🪄

### 1. `MdlMolParser`

-   解析 `.mol` 文件，将分子数据转化为 `Molecule` 对象。

-   提供分子原子、化学键的结构化数据。

### 2. `Molecule`

-   定义分子、原子、化学键的属性和行为。

-   提供分子结构渲染功能，包括化学键绘制、元素符号绘制、网格化渲染等。

### 3. `ChiralCaptchaApp`

-   GUI 主程序类，提供分子图像显示、答题、网格区域验证等功能。

-   支持图像缩放、动态布局调整。

### 4. `chiral_carbon_helper`

-   实现手性碳检测逻辑。

-   基于分子的键连接和原子属性，判断某原子是否为手性碳。

### 5. `Logger`

-   提供日志记录功能，支持多线程写日志到控制台和文件。

----------

## 示例✨

运行程序后会出现以下界面：

1. **加载分子图像**：

   显示分子的结构图，并以网格形式标记分子所在区域。

2. **答题区域**：

   用户输入包含手性碳的网格编号，验证答案是否正确。

3. **交互式功能**：

   点击按钮切换题目，或调整窗口大小以适应显示。

----------

### **系统设计和运行原理** *️⃣

#### **1. 分子数据处理：**

系统读取并解析分子文件（`.mol`），提取分子的 **原子** 和 **键** 信息，然后封装到分子对象 `Molecule` 中，作为主要数据结构进行后续的渲染和处理。

**关键模块：**

-   `mdl_mol_parser.py`：

    -   核心功能是解析 `.mol` 文件并生成分子对象（`Molecule`）。

    -   从` .mol`文件中提取的内容包括：

        -   原子（`Atom`）的位置、元素符号、电荷等信息。

        -   化学键（`Bond`）的起点、终点和类型（如单键、双键、三键等）。

    -   文件解析后，分子对象包含所有原子和化学键的结构化数据。

**示例：**

```python
atoms = [Atom() for _ in range(num_atoms)]  # 生成原子列表  
bonds = [Bond() for _ in range(num_bonds)]  # 生成化学键列表  
molecule = Molecule(cid, atoms, bonds, str_input)
```

----------

#### **2. 分子渲染（图像生成）：**

分子渲染的核心是将**原子**和**化学键**绘制为图像，支持高亮**手性碳**，并适配不同分子大小即**动态调整分辨率**。

**核心模块：**

-   `entity/molecule.py`
    -   渲染分子结构的方法是 *render_molecule*，其流程包括：

        -   **坐标缩放**：将分子中的原子坐标适配到图像的分辨率。

        -   **绘制原子(离子)和化学键**：根据解析到的分子结构绘制原子(离子)并留白，绘制元素符号以及离子符号，以及化学键的线条。

        -   **高亮手性碳**：如果启用了“作弊模式”（`cheating=True`），则用特殊颜色标记手性碳区域。

**关键代码：**

```python
# 绘制化学键  
self.draw_bond(atom1, atom2, bond.type, scale, offset_x, offset_y, line_width)  
  
# 绘制原子符号  
self.draw.text((x, y), atom.element, fill="black", font=font, align="center", anchor="mm")
```

----------

#### **3. 手性碳检测：**

**手性碳** 是指连接了四种不同配位基的碳原子，通常具有对称性破缺的特性。检测逻辑封装在 `util/chiral_carbon_helper.py`。

**实现逻辑：**

1.  判断原子是否为碳原子。

2.  检查该原子的化学键，确保它与 4 个不同的原子或基团连接。

3.  验证碳原子的邻近结构是否满足手性要求。

**关键函数：**

-   **`is_chiral_carbon`**：判断某个原子是否为手性碳。

-   **`compare_chain_recursive`**：递归比较手性碳相连的链条，确保所有配位基均不同。

**关键代码：**

```python
if len(bondnh) == 4 and hcnt == 0:  
 # 若无氢原子，检查所有键的独特性  
 return not (compare_chain(mol, index, b1, b2) or compare_chain(mol, index, b1, b3) ...)
```

----------

#### **4. 图形用户界面（GUI）：**

用户界面基于 **Tkinter**，实现了分子结构图像的展示、网格高亮、用户输入验证等功能。

**核心模块：**

-   `main.py`

    -   初始化分子文件目录，随机加载分子。

    -   渲染分子结构图像并在界面中显示。

    -   提供用户交互功能，如输入答案、刷新分子图像、提示手性碳位置等。

**关键功能：**

-   **图片展示**：显示渲染的分子结构图像，并允许用户滚动、缩放。

-   **答案提交**：用户输入手性碳的位置（如 `A1,B2`），程序验证答案的正确性。

-   **图像刷新**：切换至下一个分子并重新渲染。

**界面相关代码：**

```python
self.entry = tk.Entry(self.root)  
submit_button = tk.Button(self.root, text="提交", command=lambda: self.submit_answer())  
refresh_button = tk.Button(self.root, text="看不清，换一题", command=lambda: self.refresh_tk())
```

----------

#### **5. 日志与调试：**

程序通过 **日志系统** 记录运行信息和错误，以便调试和优化。

**核心模块：**

-   `util/logger.py`

    -   支持不同级别的日志输出（`DEBUG`、`INFO`、`WARNING`、`ERROR`）。

    -   将日志信息保存到文件并在控制台输出。

**日志示例：**

```python
self.logger.info(f"Loading molecule from: {self.mol_load_path}")  
self.logger.error("No chiral carbon for you! refresh again..")
```

----------

### **程序运行流程**

1.  **启动程序**：
    -   初始化 `ChiralCaptchaApp` 类，加载分子文件。

    -   使用 Tkinter 创建主窗口，加载分子图像并显示。
2.  **渲染分子图像**：

    -   调用 `random_molecule` 随机选择一个分子。
    -   解析分子结构，调用 `render_molecule` 渲染图像。
        -   手性碳检测(`cheating=True`)：根据解析到的分子结构，调用 `is_chiral_carbon` 检测手性碳并高亮显示。
    -   将图像加载到 Tkinter 界面。
3.  **用户交互**：
    -   用户输入可能的手性碳区域（如 `A1,B2`），程序验证答案。

    -   若输入正确，显示“回答正确”；否则提示“回答错误”。

    -   用户可刷新图像切换到其他分子。

----------

## 贡献⛏️

如果您对本项目有任何建议或改进，请提交 **Pull Request** 或 **Issue**

----------

## 鸣谢💕

- [cinit/NeoAuthBotPlugin](https://github.com/cinit/NeoAuthBotPlugin)
- [PubChem](https://pubchem.ncbi.nlm.nih.gov/)


## 分子数据库🌐

-   Source:  [PubChem Compound Database](https://ftp.ncbi.nlm.nih.gov/pubchem/Compound/CURRENT-Full/SDF)

Over 10,000  `.mol`  files have been added to this database, providing a rich source of molecular structures for generating CAPTCHAs.

## 授权

本项目采用 [MIT License](LICENSE)
