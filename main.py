import json
import random
import tkinter as tk
from PIL import Image, ImageTk
import os
from util import mdl_mol_parser, chiral_carbon_helper, logger
from config import *


class ChiralCaptchaApp:
    """
    用于答题或测试的程序
    """

    def __init__(self, mol_res_path="resource/mol", label=None, frame=None, entry=None, img_tk=None,
                 img_var=None, canvas=None, root=None, mol_load_path="", files=None, molecule=None,
                 mol_path_label=None):
        self.callback_label = None
        self.mol_path_label = mol_path_label
        self.label = label
        self.frame = frame
        self.entry = entry
        self.img_tk = img_tk
        self.img_var = img_var
        self.canvas = canvas
        self.root = root
        self.mol_res_path = mol_res_path
        self.mol_load_path = mol_load_path
        self.files = files
        self.molecule = molecule
        self.chiral_carbon_regions = []
        self.logger = logger.Logger(log_level, "ChiralGrid-log.txt")
        self.init_once()

    def init_once(self):
        self.logger.info("Initializing...")
        self.files = self.load_molecule(self.mol_res_path)
        if not self.files:
            raise InitializedError(f"No molecules found in the directory: '{self.mol_res_path}'")

    def load_molecule(self, directory):
        self.logger.info(f"Loading molecules from directory: {directory}")
        return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.endswith('.mol')]

    def random_molecule(self):
        if not self.files:
            raise InitializedError("Molecule files have not been initialized or the directory is empty.")
        self.mol_load_path = f"{self.mol_res_path}/{random.choice(self.files)}"
        self.logger.info(f"Loading molecule from: {self.mol_load_path}")
        string_mol = open(self.mol_load_path, "r", encoding="utf-8").read()
        return mdl_mol_parser.parse_string(string_mol)

    def refresh_image(self):
        self.molecule = self.random_molecule()
        result = self.molecule.render_molecule(base_elem_padding=base_elem_padding,
                                               base_line_width=base_line_width,
                                               base_font_size=base_font_size,
                                               dpi=dpi, base_grid_size=base_grid_size,
                                               cheating=cheating)
        image = result[0]
        cid = self.molecule.cid

        self.chiral_carbon_regions = result[2]

        image.save(f"result/{cid}_molecule.png")

        with open(f"result/data/{cid}_grid_data.json", 'w', encoding='utf-8') as json_file:
            json.dump(result[1], json_file, ensure_ascii=False, indent=4, sort_keys=True)

        if not chiral_carbon_helper.get_molecule_chiral_carbons(self.molecule):
            self.logger.error("No chiral carbon for you! refresh again..")
            self.refresh_image()

        return f"result/{cid}_molecule.png"

    def resize_image(self, event):
        if event is not None:
            new_width = event.width
            new_height = event.height
        else:
            new_width = self.canvas.winfo_width()
            new_height = self.canvas.winfo_height()

        if new_width <= 0 or new_height <= 0:
            self.logger.error("Invalid size!")
            return

        # 保持纵横比
        ratio = min(new_width / self.img_var[0].width, new_height / self.img_var[0].height)
        new_img_width = int(self.img_var[0].width * ratio)
        new_img_height = int(self.img_var[0].height * ratio)

        resized_img = self.img_var[0].resize((new_img_width, new_img_height), Image.LANCZOS)
        self.img_tk = ImageTk.PhotoImage(resized_img)

        # 更新 Label 中的图像
        self.label.config(image=self.img_tk)
        self.label.image = self.img_tk

        # 更新 Canvas 的滚动区域
        self.canvas.config(scrollregion=(0, 0, new_img_width, new_img_height))

    def refresh_tk(self):
        path = self.refresh_image()

        img = Image.open(path)
        self.img_var[0] = img
        self.img_tk = ImageTk.PhotoImage(img)
        self.label.config(image=self.img_tk)
        self.label.image = self.img_tk

        self.mol_path_label.config(text="Molecule: " + self.mol_load_path)

        self.resize_image(None)
        self.frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def submit_answer(self):
        try:
            answer = str(self.entry.get()).split(",")
            self.logger.info(f"User submitted: {answer}")
            self.entry.delete(0, tk.END)
            if sorted(answer) == sorted(self.chiral_carbon_regions):
                self.callback_label.config(text=f"回答正确")
            else:
                self.callback_label.config(text=f"回答错误")
        except Exception as e:
            self.callback_label.config(text=f"回答不符合规范")
            self.logger.error(f"Error in submit_answer: {e}")

    def display_image_in_window(self):
        self.root = tk.Tk()
        self.root.title("Molecule Image Display")

        width, height = self.root.maxsize()
        self.root.geometry(f"{int(width * 0.8)}x{int(height * 0.8)}")

        path = self.refresh_image()

        # 加载图像
        img = Image.open(path)

        self.img_var = [img]
        self.img_tk = ImageTk.PhotoImage(img)

        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 创建滚动条
        vscrollbar = tk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.canvas.yview)
        vscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        hscrollbar = tk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.canvas.xview)
        hscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.configure(yscrollcommand=vscrollbar.set, xscrollcommand=hscrollbar.set)

        # 绑定Event
        self.canvas.bind_all("<MouseWheel>", lambda event: self.canvas.yview_scroll(-(event.delta // 120), "units"))
        self.canvas.bind_all("<Shift-MouseWheel>",
                             lambda event: self.canvas.xview_scroll(-(event.delta // 120), "units"))

        self.frame = tk.Frame(self.canvas)
        self.label = tk.Label(self.frame, image=self.img_tk)
        self.label.pack()
        self.canvas.create_window((0, 0), window=self.frame, anchor='nw')

        def on_resize(event):
            self.resize_image(event)

        self.canvas.bind("<Configure>", on_resize)  # 图像变化自适应

        # Tips
        tk.Label(self.root, text=f"ChiralCaptcha").pack(side=tk.TOP, fill=tk.X, pady=5)
        tk.Label(self.root, text=f"提示:\n看不清请全屏\n回车提交答案").pack(side=tk.TOP, fill=tk.X, pady=5)

        self.mol_path_label = tk.Label(self.root, text=f"Molecule: {self.mol_load_path}")
        self.mol_path_label.pack(side=tk.TOP, fill=tk.X, pady=5)

        # 刷新按钮
        refresh_button = tk.Button(self.root, text="看不清，换一题",
                                   command=lambda: self.refresh_tk())
        refresh_button.pack(side=tk.TOP, fill=tk.X, pady=5)

        # 提交按钮
        submit_button = tk.Button(self.root, text="提交", command=lambda: self.submit_answer())
        submit_button.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        # 输入框
        self.entry = tk.Entry(self.root)
        self.entry.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        # 提示文本
        prompt_label = tk.Label(self.root, text="请输入图中所有包含手性碳的区域，逗号分割(A1,B2,C3):")
        prompt_label.pack(side=tk.BOTTOM, pady=5)

        # 提示文本
        self.callback_label = tk.Label(self.root, text="")
        self.callback_label.pack(side=tk.BOTTOM, pady=5)

        # 绑定回车键
        self.entry.bind("<Return>", lambda event: submit_button.invoke())

        self.root.mainloop()


class InitializedError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


if __name__ == '__main__':
    app = ChiralCaptchaApp()
    app.display_image_in_window()
