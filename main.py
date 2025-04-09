import os
import sys
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, scrolledtext
import json
import re
from pathlib import Path

class ConfigManager:
    """配置管理类，用于保存和加载配置"""
    def __init__(self):
        self.config_dir = Path.home() / ".luogu_testpoint_viewer"
        self.config_file = self.config_dir / "config.json"
        self.open_tabs_file = self.config_dir / "open_tabs.json"
        self.testpoint_paths_file = self.config_dir / "testpoints.json"
        self.ensure_config_dir()
        self.config = self.load_config()
    
    def ensure_config_dir(self):
        """确保配置目录存在"""
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True)
    
    def load_config(self):
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 确保视图模式始终为side_by_side
                    config["view_mode"] = "side_by_side"
                    return config
            except Exception:
                return {"font_size": 10, "view_mode": "side_by_side", "font_family": "Microsoft YaHei UI", "sash_position": 250}
        return {"font_size": 10, "view_mode": "side_by_side", "font_family": "Microsoft YaHei UI", "sash_position": 250}
    
    def save_config(self):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def get_font_size(self):
        """获取字体大小"""
        return self.config.get("font_size", 10)
    
    def set_font_size(self, size):
        """设置字体大小"""
        self.config["font_size"] = size
        self.save_config()
    
    def get_font_family(self):
        """获取字体"""
        return self.config.get("font_family", "Microsoft YaHei UI")
    
    def set_font_family(self, family):
        """设置字体"""
        self.config["font_family"] = family
        self.save_config()
        
    def get_view_mode(self):
        """获取视图模式，始终返回并排视图模式"""
        return "side_by_side"
    
    def set_view_mode(self, mode):
        """设置视图模式，但实际上始终使用并排视图模式"""
        self.config["view_mode"] = "side_by_side"
        self.save_config()
    
    def get_sash_position(self):
        """获取分隔窗口位置"""
        return self.config.get("sash_position", 250)
    
    def set_sash_position(self, position):
        """设置分隔窗口位置"""
        self.config["sash_position"] = position
        self.save_config()
    
    def save_open_tabs(self, open_tabs_data):
        """保存已打开的测试点列表 - 根据需求，不再保存open_tabs.json文件"""
        # 不再保存open_tabs.json文件，只保存config.json文件
        pass
    
    def load_open_tabs(self):
        """加载已打开的测试点列表"""
        if self.open_tabs_file.exists():
            try:
                with open(self.open_tabs_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                pass
        return {}
        
    def save_testpoint_paths(self, testpoint_paths):
        """保存测试点文件路径列表到testpoints.json"""
        try:
            # 确保配置目录存在
            self.ensure_config_dir()
            # 确保testpoint_paths是一个列表
            if not isinstance(testpoint_paths, list):
                testpoint_paths = list(testpoint_paths) if testpoint_paths else []
                
            # 去除重复的测试点路径（相同基本文件名的文件）
            unique_paths = []
            unique_bases = set()
            
            for path in testpoint_paths:
                if os.path.exists(path):  # 确保文件存在
                    base_name = os.path.splitext(os.path.basename(path))[0]
                    if base_name not in unique_bases:
                        unique_bases.add(base_name)
                        unique_paths.append(path)
            
            with open(self.testpoint_paths_file, 'w', encoding='utf-8') as f:
                json.dump(unique_paths, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            return False
    
    def load_testpoint_paths(self):
        """从testpoints.json加载测试点文件路径列表"""
        if self.testpoint_paths_file.exists():
            try:
                with open(self.testpoint_paths_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:  # 处理空文件的情况
                        return []
                    
                    paths = json.loads(content)
                    # 验证路径格式
                    valid_paths = []
                    for path in paths:
                        try:
                            # 尝试规范化路径格式
                            norm_path = os.path.normpath(path)
                            if os.path.exists(norm_path):
                                valid_paths.append(norm_path)
                        except Exception as e:
                            pass
                    
                    return valid_paths
            except json.JSONDecodeError as e:
                return []  # JSON解析错误时返回空列表
            except Exception as e:
                return []  # 其他错误时也返回空列表
        return []

class TestPointViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("洛谷测试点查看器")
        self.geometry("900x600")
        self.minsize(800, 500)
        
        # 设置应用图标
        try:
            self.iconbitmap(default="")
        except:
            pass
        
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        
        # 绑定窗口关闭事件
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 设置样式
        self.style = ttk.Style()
        self.font_family = self.config_manager.get_font_family()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TButton", font=(self.font_family, 10))
        self.style.configure("TLabel", font=(self.font_family, 10), background="#f0f0f0")
        self.style.configure("TLabelframe", background="#f0f0f0")
        self.style.configure("TLabelframe.Label", background="#f0f0f0", font=(self.font_family, 10, "bold"))
        self.style.configure("TNotebook", background="#f0f0f0")
        self.style.configure("TNotebook.Tab", background="#e0e0e0", padding=[10, 2])
        self.style.map("TNotebook.Tab", background=[('selected', '#f0f0f0')])
        
        # 设置全局字体
        self.font_family = self.config_manager.get_font_family()
        default_font = (self.font_family, 10)
        self.option_add("*Font", default_font)
        
        # 创建主框架
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建顶部框架
        self.top_frame = ttk.Frame(self.main_frame)
        self.top_frame.pack(fill=tk.X, pady=5)
        
        # 创建文件选择按钮
        self.select_btn = ttk.Button(self.top_frame, text="选择测试点文件", command=self.select_file)
        self.select_btn.pack(side=tk.LEFT, padx=5)
        
        # 显示当前选择的文件路径
        self.file_path_var = tk.StringVar()
        self.file_path_var.set("未选择文件")
        self.file_path_label = ttk.Label(self.top_frame, textvariable=self.file_path_var)
        self.file_path_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 创建可调整的分隔窗口
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建测试点列表框架
        self.list_frame = ttk.LabelFrame(self.paned_window, text="测试点列表")
        self.paned_window.add(self.list_frame, weight=1)
        
        # 创建测试点列表和滚动条
        self.list_frame_inner = ttk.Frame(self.list_frame)
        self.list_frame_inner.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.testpoint_scrollbar = ttk.Scrollbar(self.list_frame_inner)
        self.testpoint_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.testpoint_listbox = tk.Listbox(self.list_frame_inner, width=25, height=25, 
                                           selectmode=tk.EXTENDED,  # 支持多选
                                           activestyle="none",  # 去除选中项的下划线
                                           bg="#f8f8f8",  # 设置背景色
                                           bd=1,  # 设置边框宽度
                                           relief=tk.SOLID,  # 设置边框样式
                                           highlightthickness=0)  # 去除高亮边框
        self.testpoint_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.testpoint_listbox.bind("<<ListboxSelect>>", self.on_testpoint_select)
        self.testpoint_listbox.bind("<Double-Button-1>", self.on_testpoint_double_click)
        
        # 配置滚动条
        self.testpoint_scrollbar.config(command=self.testpoint_listbox.yview)
        self.testpoint_listbox.config(yscrollcommand=self.testpoint_scrollbar.set)
        
        # 创建测试点操作按钮框架
        self.list_btn_frame = ttk.Frame(self.list_frame)
        self.list_btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 创建打开选中测试点按钮
        self.open_btn = ttk.Button(self.list_btn_frame, text="打开选中", 
                                 command=self.open_selected_testpoints)
        self.open_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # 创建删除选中测试点按钮
        self.delete_btn = ttk.Button(self.list_btn_frame, text="删除选中", 
                                  command=self.delete_selected_testpoints)
        self.delete_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # 创建导出JSON按钮
        self.export_btn = ttk.Button(self.list_btn_frame, text="导出JSON", 
                                   command=self.export_testpoints_to_json)
        self.export_btn.pack(side=tk.RIGHT, padx=2)
        
        # 创建关闭所有标签页按钮
        self.close_all_btn = ttk.Button(self.list_btn_frame, text="关闭所有", 
                                     command=self.close_all_tabs)
        self.close_all_btn.pack(side=tk.RIGHT, padx=2)
        
        # 创建内容显示框架
        self.content_frame = ttk.LabelFrame(self.paned_window, text="测试点内容")
        self.paned_window.add(self.content_frame, weight=3)
        
        # 创建字体大小调节框架
        self.font_frame = ttk.Frame(self.content_frame)
        self.font_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 创建字体大小标签
        ttk.Label(self.font_frame, text="字体大小:").pack(side=tk.LEFT, padx=5)
        
        # 创建减小字体按钮
        self.decrease_btn = ttk.Button(self.font_frame, text="-", width=2, command=self.decrease_font_size)
        self.decrease_btn.pack(side=tk.LEFT, padx=2)
        
        # 创建字体大小输入框
        self.font_size_var = tk.StringVar()
        self.font_size_var.set(str(self.config_manager.get_font_size()))
        self.font_size_entry = tk.Entry(self.font_frame, textvariable=self.font_size_var, 
                                       width=3, justify="center", relief="flat", bg="#f5f5f5",
                                       highlightthickness=1, bd=1)
        self.font_size_entry.pack(side=tk.LEFT, padx=5, pady=2, ipady=1)
        self.font_size_entry.bind("<Return>", self.on_font_size_change)
        
        # 创建增加字体按钮
        self.increase_btn = ttk.Button(self.font_frame, text="+", width=2, command=self.increase_font_size)
        self.increase_btn.pack(side=tk.LEFT, padx=2)
        
        # 创建视图切换按钮
        self.view_mode_var = tk.StringVar()
        self.view_mode_var.set("并排视图")
        self.view_mode_btn = ttk.Button(self.font_frame, textvariable=self.view_mode_var, 
                                      command=self.toggle_view_mode)
        self.view_mode_btn.pack(side=tk.LEFT, padx=10)
        
        # 创建提示标签（初始不可见）
        self.font_tip_var = tk.StringVar()
        self.font_tip_var.set("输入6-30之间的数字")
        self.font_tip_label = ttk.Label(self.font_frame, textvariable=self.font_tip_var, foreground="#666666")
        
        # 绑定鼠标悬停事件
        self.font_size_entry.bind("<Enter>", self.show_font_tip)
        self.font_size_entry.bind("<Leave>", self.hide_font_tip)
        
        # 绑定键盘快捷键
        self.bind("<Control-plus>", lambda e: self.increase_font_size())
        self.bind("<Control-minus>", lambda e: self.decrease_font_size())
        self.bind("<Control-equal>", lambda e: self.increase_font_size())  # 兼容不需要按Shift的情况
        
        # 绑定鼠标滚轮事件
        self.bind_all("<Control-MouseWheel>", self.on_mouse_wheel)
        
        # 创建标签页框架（用于多标签页视图）
        self.multi_tab_notebook = ttk.Notebook(self.content_frame)
        
        # 创建并排显示的框架
        self.side_by_side_frame = ttk.Frame(self.content_frame)
        self.side_by_side_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建左侧输入框架
        self.left_frame = ttk.LabelFrame(self.side_by_side_frame, text="输入数据")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建右侧输出框架
        self.right_frame = ttk.LabelFrame(self.side_by_side_frame, text="输出数据")
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建输入文本框和复制按钮框架（这部分代码已移至左右框架中，此处不再需要）
        # 以下代码已被替换为左右框架中的对应代码
        
        # 创建左侧输入文本框和复制按钮框架（用于并排显示）
        self.left_input_frame = ttk.Frame(self.left_frame)
        self.left_input_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建复制按钮框架
        self.left_btn_frame = ttk.Frame(self.left_input_frame)
        self.left_btn_frame.pack(side=tk.TOP, fill=tk.X, pady=2)
        
        self.left_input_copy_btn = ttk.Button(self.left_btn_frame, text="复制", width=4, command=lambda: self.copy_text(self.left_input_text))
        self.left_input_copy_btn.pack(side=tk.RIGHT, padx=5)
        
        # 创建文本框 - 使用ScrolledText自带的滚动条
        self.left_input_container = ttk.Frame(self.left_input_frame)
        self.left_input_container.pack(fill=tk.BOTH, expand=True)
        
        # ScrolledText已经包含了滚动条，不需要额外添加
        self.left_input_text = scrolledtext.ScrolledText(self.left_input_container, wrap=tk.WORD, bg="#fafafa", relief=tk.FLAT, bd=1)
        self.left_input_text.pack(fill=tk.BOTH, expand=True)
        
        # 创建右侧输出文本框和复制按钮框架（用于并排显示）
        self.right_output_frame = ttk.Frame(self.right_frame)
        self.right_output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建复制按钮框架
        self.right_btn_frame = ttk.Frame(self.right_output_frame)
        self.right_btn_frame.pack(side=tk.TOP, fill=tk.X, pady=2)
        
        self.right_output_copy_btn = ttk.Button(self.right_btn_frame, text="复制", width=4, command=lambda: self.copy_text(self.right_output_text))
        self.right_output_copy_btn.pack(side=tk.RIGHT, padx=5)
        
        # 创建文本框 - 使用ScrolledText自带的滚动条
        self.right_output_container = ttk.Frame(self.right_output_frame)
        self.right_output_container.pack(fill=tk.BOTH, expand=True)
        
        # ScrolledText已经包含了滚动条，不需要额外添加
        self.right_output_text = scrolledtext.ScrolledText(self.right_output_container, wrap=tk.WORD, bg="#fafafa", relief=tk.FLAT, bd=1)
        self.right_output_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # 根据配置设置初始视图模式
        self.current_view_mode = self.config_manager.get_view_mode()
        if self.current_view_mode == "side_by_side":
            self.multi_tab_notebook.pack_forget()
            self.side_by_side_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        else:
            self.side_by_side_frame.pack_forget()
            self.multi_tab_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 初始化数据
        self.testpoint_data = {}
        self.current_file = None
        self.open_tabs = {}  # 存储已打开的标签页 {tab_id: {"name": display_name, "original_name": original_name}}
        
        # 设置文本框字体大小
        self.update_font_size(self.config_manager.get_font_size())
        
        # 加载上次保存的测试点列表
        self.load_saved_testpoints()
        
        # 设置分隔窗口位置
        try:
            saved_position = self.config_manager.get_sash_position()
            if saved_position > 0:
                self.paned_window.sashpos(0, saved_position)
        except Exception as e:
            pass
    
    def select_file(self):
        """选择测试点文件"""
        file_path = filedialog.askopenfilename(
            title="选择测试点文件",
            filetypes=[("所有文件", "*.*"), ("文本文件", "*.txt"), ("JSON文件", "*.json")]
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            self.current_file = file_path
            self.load_testpoints(file_path)
    
    def load_testpoints(self, file_path):
        """加载测试点数据，追加到现有列表中"""
        try:
            # 检查文件是否已经加载过
            testpoint_paths = self.config_manager.load_testpoint_paths()
            
            # 检查文件路径是否已在列表中
            if file_path in testpoint_paths:
                # 如果文件路径已存在，直接提示用户并返回
                messagebox.showinfo("提示", "已加载相同测试点数据")
                return
                
            # 获取当前文件的基本名称（不含扩展名）
            current_file_base = os.path.splitext(os.path.basename(file_path))[0]
            
            # 检查是否已存在相同基本名称的测试点文件
            is_duplicate = False
            for existing_path in testpoint_paths:
                existing_base = os.path.splitext(os.path.basename(existing_path))[0]
                if current_file_base == existing_base:
                    is_duplicate = True
                    break
            
            # 只有当不是重复测试点时才添加到路径列表
            if not is_duplicate:
                testpoint_paths.append(file_path)
                self.config_manager.save_testpoint_paths(testpoint_paths)
            
            # 保存当前测试点数据的副本
            current_data = self.testpoint_data.copy()
            
            # 根据文件类型处理
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == ".json":
                # 处理JSON格式的测试点文件
                self.load_json_testpoints(file_path)
            else:
                # 处理普通文本格式的测试点文件
                self.load_text_testpoints(file_path)
                
            # 尝试查找与当前文件相关的测试点文件（同名不同扩展名）
            self.find_related_testpoints(file_path)
            
            # 获取新添加的测试点
            new_testpoints = {}
            for name, data in self.testpoint_data.items():
                if name not in current_data:
                    new_testpoints[name] = data
            
            # 如果没有新的测试点，提示用户
            if not new_testpoints:
                messagebox.showinfo("提示", "已加载相同测试点数据")
                return
                
            # 更新测试点列表，只添加新的测试点
            for tp_name in sorted(new_testpoints.keys()):
                # 移除文件扩展名显示
                display_name = self.format_testpoint_name(tp_name)
                self.testpoint_listbox.insert(tk.END, display_name)
                
            # 如果有测试点，默认选择第一个新添加的测试点
            if self.testpoint_listbox.size() > 0:
                # 选择第一个新添加的测试点
                new_index = self.testpoint_listbox.size() - len(new_testpoints)
                self.testpoint_listbox.selection_clear(0, tk.END)
                self.testpoint_listbox.selection_set(new_index)
                self.testpoint_listbox.see(new_index)  # 确保新添加的测试点可见
                self.testpoint_listbox.event_generate("<<ListboxSelect>>")
                
            # 更新文件路径显示
            self.file_path_var.set(f"已加载: {file_path} (共 {self.testpoint_listbox.size()} 个测试点)")
            
            # 保存测试点文件路径
            self.save_testpoints_data()
                
        except Exception as e:
            messagebox.showerror("错误", f"加载测试点数据失败: {str(e)}")
    
    def load_json_testpoints(self, file_path):
        """加载JSON格式的测试点文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # 创建临时字典存储新的测试点
            new_testpoints = {}
            
            # 尝试解析不同格式的JSON测试点
            if isinstance(data, dict):
                # 如果是字典格式，可能是洛谷的测试点格式
                if 'testCases' in data:
                    # 洛谷格式
                    for i, test_case in enumerate(data['testCases']):
                        # 使用文件名作为前缀，避免与其他文件的测试点冲突
                        base_name = os.path.basename(file_path)
                        name = f"{base_name}_测试点_{i+1}"
                        new_testpoints[name] = {
                            'input': test_case.get('input', ''),
                            'output': test_case.get('output', '')
                        }
                else:
                    # 其他字典格式，假设键是测试点名称
                    base_name = os.path.basename(file_path)
                    for name, content in data.items():
                        if isinstance(content, dict):
                            # 添加文件名前缀
                            prefixed_name = f"{base_name}_{name}"
                            new_testpoints[prefixed_name] = {
                                'input': content.get('input', ''),
                                'output': content.get('output', '')
                            }
            elif isinstance(data, list):
                # 如果是列表格式
                base_name = os.path.basename(file_path)
                for i, item in enumerate(data):
                    if isinstance(item, dict):
                        item_name = item.get('name', f"测试点_{i+1}")
                        name = f"{base_name}_{item_name}"
                        new_testpoints[name] = {
                            'input': item.get('input', ''),
                            'output': item.get('output', '')
                        }
            
            # 将新的测试点添加到现有测试点数据中
            self.testpoint_data.update(new_testpoints)
    
    def load_text_testpoints(self, file_path):
        """加载文本格式的测试点文件"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            # 创建临时字典存储新的测试点
            new_testpoints = {}
            
            # 尝试识别测试点格式
            # 1. 检查是否是输入文件 (.in) 或输出文件 (.out/.ans)
            base_name = os.path.basename(file_path)
            # 获取不带扩展名的文件名作为测试点标识符的基础
            name_without_ext = os.path.splitext(base_name)[0]
            # 生成唯一的测试点名称，使用目录哈希和不带扩展名的文件名
            dir_hash = str(abs(hash(os.path.dirname(file_path))) % 10000)
            unique_name = f"{dir_hash}_{name_without_ext}"
            
            # 检查是否已经存在这个测试点
            if unique_name in self.testpoint_data:
                # 如果已存在，则更新现有测试点而不是创建新的
                if re.match(r'.*\.(in|input)$', base_name, re.IGNORECASE):
                    # 这是一个输入文件，更新输入内容
                    self.testpoint_data[unique_name]['input'] = content
                elif re.match(r'.*\.(out|ans|output)$', base_name, re.IGNORECASE):
                    # 这是一个输出文件，更新输出内容
                    self.testpoint_data[unique_name]['output'] = content
                else:
                    # 不是标准的测试点文件，更新输入内容
                    self.testpoint_data[unique_name]['input'] = content
                return
            
            if re.match(r'.*\.(in|input)$', base_name, re.IGNORECASE):
                # 这是一个输入文件，尝试查找对应的输出文件
                output_file = re.sub(r'\.(in|input)$', '.out', file_path, flags=re.IGNORECASE)
                if not os.path.exists(output_file):
                    output_file = re.sub(r'\.(in|input)$', '.ans', file_path, flags=re.IGNORECASE)
                
                if os.path.exists(output_file):
                    with open(output_file, 'r', encoding='utf-8', errors='ignore') as out_f:
                        output_content = out_f.read()
                    new_testpoints[unique_name] = {
                        'input': content,
                        'output': output_content
                    }
                else:
                    new_testpoints[unique_name] = {
                        'input': content,
                        'output': '未找到对应的输出文件'
                    }
            elif re.match(r'.*\.(out|ans|output)$', base_name, re.IGNORECASE):
                # 这是一个输出文件，尝试查找对应的输入文件
                input_file = re.sub(r'\.(out|ans|output)$', '.in', file_path, flags=re.IGNORECASE)
                if not os.path.exists(input_file):
                    input_file = re.sub(r'\.(out|ans|output)$', '.input', file_path, flags=re.IGNORECASE)
                
                if os.path.exists(input_file):
                    with open(input_file, 'r', encoding='utf-8', errors='ignore') as in_f:
                        input_content = in_f.read()
                    new_testpoints[unique_name] = {
                        'input': input_content,
                        'output': content
                    }
                else:
                    new_testpoints[unique_name] = {
                        'input': '未找到对应的输入文件',
                        'output': content
                    }
            else:
                # 不是标准的测试点文件，将整个内容作为一个测试点
                new_testpoints[unique_name] = {
                    'input': content,
                    'output': ''
                }
                
            # 将新的测试点添加到现有测试点数据中
            self.testpoint_data.update(new_testpoints)
    
    def find_related_testpoints(self, file_path):
        """查找同目录下的相关测试点文件"""
        dir_path = os.path.dirname(file_path)
        files = os.listdir(dir_path)
        
        # 创建临时字典存储新的测试点
        new_testpoints = {}
        
        # 生成目录的唯一标识符，用于避免不同目录下的同名文件冲突
        # 使用与load_text_testpoints方法相同的哈希生成逻辑
        dir_hash = str(abs(hash(dir_path)) % 10000)
        
        # 获取当前文件的名称（不含扩展名）
        current_file_name = os.path.splitext(os.path.basename(file_path))[0]
        
        # 查找与当前文件相关的测试点文件
        related_files = []
        for f in files:
            name_without_ext = os.path.splitext(f)[0]
            # 只处理与当前文件名相同的文件
            if name_without_ext == current_file_name:
                related_files.append(f)
        
        # 分类相关文件
        input_files = [f for f in related_files if re.match(r'.*\.(in|input)$', f, re.IGNORECASE)]
        output_files = [f for f in related_files if re.match(r'.*\.(out|ans|output)$', f, re.IGNORECASE)]
        
        # 创建输入文件名到文件的映射
        input_map = {}
        for in_file in input_files:
            name_without_ext = os.path.splitext(in_file)[0]
            input_map[name_without_ext] = in_file
        
        # 创建输出文件名到文件的映射
        output_map = {}
        for out_file in output_files:
            name_without_ext = os.path.splitext(out_file)[0]
            output_map[name_without_ext] = out_file
        
        # 处理相关测试点
        processed_names = set()
        
        # 首先处理有输入文件的测试点
        for base_name in input_map.keys():
            # 创建唯一的测试点名称
            unique_name = f"{dir_hash}_{base_name}"
            
            # 检查是否已经存在这个测试点或已处理过
            if unique_name in self.testpoint_data or base_name in processed_names:
                continue
                
            processed_names.add(base_name)
            
            # 读取输入文件内容
            in_path = os.path.join(dir_path, input_map[base_name])
            with open(in_path, 'r', encoding='utf-8', errors='ignore') as f:
                input_content = f.read()
            
            # 查找对应的输出文件
            output_content = '未找到对应的输出文件'
            if base_name in output_map:
                out_path = os.path.join(dir_path, output_map[base_name])
                with open(out_path, 'r', encoding='utf-8', errors='ignore') as f:
                    output_content = f.read()
            
            new_testpoints[unique_name] = {
                'input': input_content,
                'output': output_content
            }
        
        # 处理只有输出文件的测试点
        for base_name in output_map.keys():
            if base_name in processed_names or base_name in input_map:
                continue  # 已处理过或有对应的输入文件
            
            # 创建唯一的测试点名称
            unique_name = f"{dir_hash}_{base_name}"
            
            # 检查是否已经存在这个测试点
            if unique_name in self.testpoint_data:
                continue
            
            # 读取输出文件内容
            out_path = os.path.join(dir_path, output_map[base_name])
            with open(out_path, 'r', encoding='utf-8', errors='ignore') as f:
                output_content = f.read()
            
            new_testpoints[unique_name] = {
                'input': '未找到对应的输入文件',
                'output': output_content
            }
        
        # 将新的测试点添加到现有测试点数据中
        self.testpoint_data.update(new_testpoints)
    

    
    def increase_font_size(self):
        """增加字体大小"""
        try:
            current_size = int(self.font_size_var.get())
            if current_size < 30:  # 限制最大字体大小
                new_size = current_size + 1
                self.update_font_size(new_size)
                self.config_manager.set_font_size(new_size)
        except ValueError:
            pass
    
    def decrease_font_size(self):
        """减小字体大小"""
        try:
            current_size = int(self.font_size_var.get())
            if current_size > 6:  # 限制最小字体大小
                new_size = current_size - 1
                self.update_font_size(new_size)
                self.config_manager.set_font_size(new_size)
        except ValueError:
            pass
    
    def update_font_size(self, size):
        """更新字体大小"""
        self.font_size_var.set(str(size))
        font = (self.font_family, size)
        # 更新所有文本组件的字体
        self.left_input_text.configure(font=font)
        self.right_output_text.configure(font=font)
        
        # 更新已打开标签页中的文本组件字体
        for tab_id, tab_info in self.open_tabs.items():
            tab_frame = tab_info["frame"]
            self._update_font_in_frame(tab_frame, font)
    
    def on_font_size_change(self, event):
        """字体大小输入框变化时的处理函数"""
        try:
            new_size = int(self.font_size_var.get())
            if 6 <= new_size <= 30:  # 限制字体大小范围
                self.update_font_size(new_size)
                self.config_manager.set_font_size(new_size)
            else:
                # 如果超出范围，恢复原来的值
                self.font_size_var.set(str(self.config_manager.get_font_size()))
        except ValueError:
            # 如果输入的不是数字，恢复原来的值
            self.font_size_var.set(str(self.config_manager.get_font_size()))
    
    def show_font_tip(self, event):
        """显示字体大小提示"""
        self.font_tip_label.pack(side=tk.LEFT, padx=5)
    
    def hide_font_tip(self, event):
        """隐藏字体大小提示"""
        self.font_tip_label.pack_forget()
    
    def format_testpoint_name(self, file_name):
        """格式化测试点名称，移除文件扩展名"""
        # 移除文件扩展名
        base_name = os.path.splitext(file_name)[0]
        
        # 尝试匹配P数字格式
        p_match = re.search(r'(P\d+)', base_name)
        if p_match:
            p_num = p_match.group(1)
            # 尝试匹配测试点编号
            test_match = re.search(r'(\d+)$', base_name)
            if test_match:
                return f"{p_num}_第{test_match.group(1)}个测试点"
            return p_num
        
        return base_name
    
    def on_testpoint_select(self, event):
        """选择测试点时的处理函数"""
        selection = self.testpoint_listbox.curselection()
        if not selection:
            return
        
        # 如果只选择了一个测试点，更新当前视图
        if len(selection) == 1:
            index = selection[0]
            display_name = self.testpoint_listbox.get(index)
            
            # 查找对应的原始测试点名称
            original_name = None
            for tp_name in self.testpoint_data.keys():
                if self.format_testpoint_name(tp_name) == display_name:
                    original_name = tp_name
                    break
            
            if original_name and original_name in self.testpoint_data:
                input_data = self.testpoint_data[original_name]['input']
                output_data = self.testpoint_data[original_name]['output']
                
                # 更新并排视图的文本框
                self.left_input_text.delete(1.0, tk.END)
                self.left_input_text.insert(tk.END, input_data)
                self.right_output_text.delete(1.0, tk.END)
                self.right_output_text.insert(tk.END, output_data)
    
    def on_testpoint_double_click(self, event):
        """双击测试点时的处理函数，与单击行为相同"""
        selection = self.testpoint_listbox.curselection()
        if not selection:
            return
        
        # 获取双击的项目索引
        clicked_index = self.testpoint_listbox.nearest(event.y)
        if clicked_index not in selection:
            return
            
        # 触发选择事件，与单击行为相同
        self.testpoint_listbox.selection_clear(0, tk.END)
        self.testpoint_listbox.selection_set(clicked_index)
        self.testpoint_listbox.event_generate("<<ListboxSelect>>")
        
        # 双击时与单击行为相同，不需要额外处理

    def on_mouse_wheel(self, event):
        """鼠标滚轮事件处理函数"""
        # 在Windows上，event.delta为正表示向上滚动，为负表示向下滚动
        # 在macOS上可能相反，需要根据实际情况调整
        if event.delta > 0:
            self.increase_font_size()
        else:
            self.decrease_font_size()
            
    def copy_text(self, text_widget):
        """复制文本框内容到剪贴板"""
        try:
            # 获取文本内容
            content = text_widget.get(1.0, tk.END).strip()
            if content:
                # 清除剪贴板当前内容
                self.clipboard_clear()
                # 设置新的剪贴板内容
                self.clipboard_append(content)
                # 显示提示消息
                messagebox.showinfo("提示", "内容已复制到剪贴板")
            else:
                messagebox.showinfo("提示", "没有内容可复制")
        except Exception as e:
            messagebox.showerror("错误", f"复制失败: {str(e)}")
    
    def create_new_tab(self, display_name, original_name):
        """创建新的测试点标签页"""
        # 创建新的标签页框架
        tab_frame = ttk.Frame(self.multi_tab_notebook)
        tab_id = str(id(tab_frame))  # 使用框架的id作为唯一标识符
        
        # 创建标签页内容
        if self.current_view_mode == "tab":
            # 创建选项卡控件
            tab_notebook = ttk.Notebook(tab_frame)
            tab_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # 创建输入选项卡
            input_frame = ttk.Frame(tab_notebook)
            tab_notebook.add(input_frame, text="输入数据")
            
            # 创建输出选项卡
            output_frame = ttk.Frame(tab_notebook)
            tab_notebook.add(output_frame, text="输出数据")
            
            # 创建输入文本框和复制按钮框架
            input_text_frame = ttk.Frame(input_frame)
            input_text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # 创建复制按钮框架
            input_btn_frame = ttk.Frame(input_text_frame)
            input_btn_frame.pack(side=tk.TOP, fill=tk.X, pady=2)
            
            input_copy_btn = ttk.Button(input_btn_frame, text="复制", width=4, 
                                       command=lambda tf=input_text_frame: self.copy_text(tf.winfo_children()[-1]))
            input_copy_btn.pack(side=tk.RIGHT, padx=5)
            
            # 创建带滚动条的文本框
            input_text_container = ttk.Frame(input_text_frame)
            input_text_container.pack(fill=tk.BOTH, expand=True)
            
            input_scrollbar = ttk.Scrollbar(input_text_container)
            input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            input_text = scrolledtext.ScrolledText(input_text_container, wrap=tk.WORD, 
                                                  font=("TkDefaultFont", self.config_manager.get_font_size()),
                                                  bg="#fafafa", relief=tk.FLAT, bd=1)
            input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            input_text.config(yscrollcommand=input_scrollbar.set)
            input_scrollbar.config(command=input_text.yview)
            
            # 创建输出文本框和复制按钮框架
            output_text_frame = ttk.Frame(output_frame)
            output_text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # 创建复制按钮框架
            output_btn_frame = ttk.Frame(output_text_frame)
            output_btn_frame.pack(side=tk.TOP, fill=tk.X, pady=2)
            
            output_copy_btn = ttk.Button(output_btn_frame, text="复制", width=4, 
                                        command=lambda tf=output_text_frame: self.copy_text(tf.winfo_children()[-1]))
            output_copy_btn.pack(side=tk.RIGHT, padx=5)
            
            # 创建带滚动条的文本框
            output_text_container = ttk.Frame(output_text_frame)
            output_text_container.pack(fill=tk.BOTH, expand=True)
            
            output_scrollbar = ttk.Scrollbar(output_text_container)
            output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            output_text = scrolledtext.ScrolledText(output_text_container, wrap=tk.WORD, 
                                                   font=("TkDefaultFont", self.config_manager.get_font_size()),
                                                   bg="#fafafa", relief=tk.FLAT, bd=1)
            output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            output_text.config(yscrollcommand=output_scrollbar.set)
            output_scrollbar.config(command=output_text.yview)
            
            # 填充数据
            input_data = self.testpoint_data[original_name]['input']
            output_data = self.testpoint_data[original_name]['output']
            
            input_text.insert(tk.END, input_data)
            output_text.insert(tk.END, output_data)
            
        else:  # side_by_side 模式
            # 创建并排显示的框架
            side_frame = ttk.Frame(tab_frame)
            side_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # 创建左侧输入框架
            left_frame = ttk.LabelFrame(side_frame, text="输入数据")
            left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # 创建右侧输出框架
            right_frame = ttk.LabelFrame(side_frame, text="输出数据")
            right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # 创建左侧输入文本框和复制按钮框架
            left_input_frame = ttk.Frame(left_frame)
            left_input_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # 创建复制按钮框架
            left_btn_frame = ttk.Frame(left_input_frame)
            left_btn_frame.pack(side=tk.TOP, fill=tk.X, pady=2)
            
            left_input_copy_btn = ttk.Button(left_btn_frame, text="复制", width=4, 
                                           command=lambda tf=left_input_frame: self.copy_text(tf.winfo_children()[-1]))
            left_input_copy_btn.pack(side=tk.RIGHT, padx=5)
            
            # 创建带滚动条的文本框
            left_input_container = ttk.Frame(left_input_frame)
            left_input_container.pack(fill=tk.BOTH, expand=True)
            
            left_input_scrollbar = ttk.Scrollbar(left_input_container)
            left_input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            left_input_text = scrolledtext.ScrolledText(left_input_container, wrap=tk.WORD, 
                                                      font=("TkDefaultFont", self.config_manager.get_font_size()),
                                                      bg="#fafafa", relief=tk.FLAT, bd=1)
            left_input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            left_input_text.config(yscrollcommand=left_input_scrollbar.set)
            left_input_scrollbar.config(command=left_input_text.yview)
            
            # 创建右侧输出文本框和复制按钮框架
            right_output_frame = ttk.Frame(right_frame)
            right_output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # 创建复制按钮框架
            right_btn_frame = ttk.Frame(right_output_frame)
            right_btn_frame.pack(side=tk.TOP, fill=tk.X, pady=2)
            
            right_output_copy_btn = ttk.Button(right_btn_frame, text="复制", width=4, 
                                             command=lambda tf=right_output_frame: self.copy_text(tf.winfo_children()[-1]))
            right_output_copy_btn.pack(side=tk.RIGHT, padx=5)
            
            # 创建带滚动条的文本框
            right_output_container = ttk.Frame(right_output_frame)
            right_output_container.pack(fill=tk.BOTH, expand=True)
            
            right_output_scrollbar = ttk.Scrollbar(right_output_container)
            right_output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            right_output_text = scrolledtext.ScrolledText(right_output_container, wrap=tk.WORD, 
                                                        font=("TkDefaultFont", self.config_manager.get_font_size()),
                                                        bg="#fafafa", relief=tk.FLAT, bd=1)
            right_output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            right_output_text.config(yscrollcommand=right_output_scrollbar.set)
            right_output_scrollbar.config(command=right_output_text.yview)
            
            # 填充数据
            input_data = self.testpoint_data[original_name]['input']
            output_data = self.testpoint_data[original_name]['output']
            
            # 确保使用统一的字体样式
            font = (self.font_family, self.config_manager.get_font_size())
            left_input_text.configure(font=font)
            right_output_text.configure(font=font)
            
            # 填充数据
            left_input_text.delete(1.0, tk.END)
            left_input_text.insert(tk.END, input_data)
            right_output_text.delete(1.0, tk.END)
            right_output_text.insert(tk.END, output_data)
        
        # 添加标签页 - 显示测试点名称
        self.multi_tab_notebook.add(tab_frame, text=display_name + "  ")
        
        # 创建关闭按钮
        close_button = ttk.Button(self.multi_tab_notebook, text="×", width=2, 
                                 command=lambda tid=tab_id: self.close_tab(tid),
                                 style="Tab.TButton")
        
        # 创建关闭按钮样式
        self.style.configure("Tab.TButton", font=("Arial", 8, "bold"), padding=0)
        
        # 获取标签页索引
        tab_index = self.multi_tab_notebook.index("end") - 1
        
        # 选择新创建的标签页
        self.multi_tab_notebook.select(tab_index)
        
        # 确保关闭按钮可见
        self.after(100, self.update_close_buttons)
        
        # 存储标签页信息
        self.open_tabs[tab_id] = {
            "name": display_name,
            "original_name": original_name,
            "frame": tab_frame,
            "close_button": close_button
        }
        
        # 绑定标签页选择事件，用于显示/隐藏关闭按钮
        self.multi_tab_notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # 显示关闭按钮
        self.update_close_buttons()
        
        # 选择新创建的标签页
        self.multi_tab_notebook.select(tab_index)
    
    def close_tab(self, tab_id):
        """关闭标签页"""
        if tab_id in self.open_tabs:
            tab_info = self.open_tabs[tab_id]
            tab_frame = tab_info["frame"]
            
            # 获取标签页索引
            try:
                tab_index = self.multi_tab_notebook.index(tab_frame)
                # 移除标签页
                self.multi_tab_notebook.forget(tab_index)
                # 移除标签页信息
                del self.open_tabs[tab_id]
                # 更新关闭按钮
                self.update_close_buttons()
            except:
                pass
    
    def on_tab_changed(self, event):
        """标签页切换事件处理函数"""
        self.update_close_buttons()
    
    def update_close_buttons(self):
        """更新所有标签页的关闭按钮"""
        # 获取当前选中的标签页索引
        try:
            current_tab = self.multi_tab_notebook.select()
            
            # 更新所有标签页的关闭按钮
            for tab_id, tab_info in self.open_tabs.items():
                tab_frame = tab_info["frame"]
                close_button = tab_info["close_button"]
                
                try:
                    tab_index = self.multi_tab_notebook.index(tab_frame)
                    
                    # 获取标签页的位置
                    x, y, width, height = self.multi_tab_notebook.bbox(tab_index)
                    
                    if x is not None and width is not None:
                        # 放置关闭按钮
                        close_button.place(x=x+width-20, y=y+2, width=16, height=16)
                        close_button.lift()
                    else:
                        close_button.place_forget()
                except Exception as e:
                    close_button.place_forget()
        except Exception as e:
            pass
            
    def close_all_tabs(self):
        """关闭所有标签页"""
        # 获取所有标签页ID
        tab_ids = list(self.open_tabs.keys())
        
        # 逐个关闭标签页
        for tab_id in tab_ids:
            self.close_tab(tab_id)
            
        # 清空标签页信息
        self.open_tabs = {}
        
        # 如果是并排视图模式，清空文本框
        if self.current_view_mode == "side_by_side":
            self.left_input_text.delete(1.0, tk.END)
            self.right_output_text.delete(1.0, tk.END)
    
    def open_selected_testpoints(self):
        """打开选中的测试点"""
        selection = self.testpoint_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先选择测试点")
            return
        
        # 遍历所有选中的测试点
        for index in selection:
            display_name = self.testpoint_listbox.get(index)
            
            # 查找对应的原始测试点名称
            original_name = None
            for tp_name in self.testpoint_data.keys():
                if self.format_testpoint_name(tp_name) == display_name:
                    original_name = tp_name
                    break
            
            if original_name and original_name in self.testpoint_data:
                # 检查是否已经打开了这个测试点
                already_open = False
                for tab_id, tab_info in self.open_tabs.items():
                    if tab_info["original_name"] == original_name:
                        # 如果已经打开，切换到对应标签页
                        tab_frame = tab_info["frame"]
                        tab_index = self.multi_tab_notebook.index(tab_frame)
                        self.multi_tab_notebook.select(tab_index)
                        already_open = True
                        break
                
                if not already_open:
                    # 创建新标签页
                    self.create_new_tab(display_name, original_name)
    
    def toggle_view_mode(self):
        """切换视图模式"""
        # 由于需求变更，我们始终使用并排视图模式
        self.current_view_mode = "side_by_side"
        self.view_mode_var.set("并排视图")
        
        # 确保并排视图可见
        self.multi_tab_notebook.pack_forget()
        self.side_by_side_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 如果有选中的测试点，更新并排视图的内容
        selection = self.testpoint_listbox.curselection()
        if selection:
            index = selection[0]
            display_name = self.testpoint_listbox.get(index)
            
            # 查找对应的原始测试点名称
            original_name = None
            for tp_name in self.testpoint_data.keys():
                if self.format_testpoint_name(tp_name) == display_name:
                    original_name = tp_name
                    break
            
            if original_name and original_name in self.testpoint_data:
                input_data = self.testpoint_data[original_name]['input']
                output_data = self.testpoint_data[original_name]['output']
                
                # 清空并更新文本框内容
                self.left_input_text.delete(1.0, tk.END)
                self.left_input_text.insert(tk.END, input_data)
                self.right_output_text.delete(1.0, tk.END)
                self.right_output_text.insert(tk.END, output_data)
        
        # 确保复制按钮可见
        self.left_btn_frame.lift()
        self.right_btn_frame.lift()
        
        # 保存视图模式设置
        self.config_manager.set_view_mode(self.current_view_mode)
        
    def update_tab_content(self, tab_frame, original_name):
        """更新标签页内容"""
        if original_name in self.testpoint_data:
            input_data = self.testpoint_data[original_name]['input']
            output_data = self.testpoint_data[original_name]['output']
            
            # 查找标签页中的文本框
            for child in tab_frame.winfo_children():
                if isinstance(child, ttk.Notebook):
                    tab_notebook = child
                    # 获取输入和输出选项卡
                    if len(tab_notebook.winfo_children()) >= 2:
                        input_frame = tab_notebook.winfo_children()[0]
                        output_frame = tab_notebook.winfo_children()[1]
                        
                        # 更新输入文本框
                        self._update_text_widget(input_frame, input_data)
                        
                        # 更新输出文本框
                        self._update_text_widget(output_frame, output_data)
                elif isinstance(child, ttk.Frame):
                    # 处理并排视图
                    for frame in child.winfo_children():
                        if isinstance(frame, ttk.LabelFrame):
                            if "输入" in frame["text"]:
                                # 输入框架
                                self._update_text_widget(frame, input_data)
                            elif "输出" in frame["text"]:
                                # 输出框架
                                self._update_text_widget(frame, output_data)
    
    def _update_text_widget(self, parent_frame, content):
        """递归查找并更新文本框内容"""
        # 递归查找文本框
        for child in parent_frame.winfo_children():
            if isinstance(child, scrolledtext.ScrolledText):
                child.delete(1.0, tk.END)
                child.insert(tk.END, content)
                return True
            elif hasattr(child, 'winfo_children'):
                if self._update_text_widget(child, content):
                    return True
        return False
        
    def _update_font_in_frame(self, parent_frame, font):
        """递归查找并更新文本框字体"""
        # 递归查找文本框
        for child in parent_frame.winfo_children():
            if isinstance(child, scrolledtext.ScrolledText):
                child.configure(font=font)
            elif hasattr(child, 'winfo_children'):
                self._update_font_in_frame(child, font)
        
    def export_testpoints_to_json(self):
        """将测试点数据导出为JSON文件"""
        if not self.testpoint_data:
            messagebox.showinfo("提示", "没有测试点数据可导出")
            return
            
        # 选择保存路径
        file_path = filedialog.asksaveasfilename(
            title="保存测试点数据",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            # 准备导出数据
            export_data = {}
            for name, data in self.testpoint_data.items():
                export_data[name] = {
                    "input": data["input"],
                    "output": data["output"]
                }
                
            # 写入JSON文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
                
            messagebox.showinfo("成功", f"测试点数据已成功导出到:\n{file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"导出测试点数据失败: {str(e)}")
    
    def on_closing(self):
        """窗口关闭事件处理函数"""
        # 保存分隔窗口位置
        try:
            sash_position = self.paned_window.sashpos(0)
            if sash_position > 0:
                self.config_manager.set_sash_position(sash_position)
        except Exception as e:
            pass
            
        # 保存测试点文件路径
        self.save_testpoints_data()
        self.destroy()
    
    def load_saved_testpoints(self):
        """加载已保存的测试点文件路径列表，并从原始文件加载测试点数据"""
        self.testpoint_data = {}
        self.testpoint_listbox.delete(0, tk.END)
        
        # 加载已保存的测试点文件路径列表
        testpoint_paths = self.config_manager.load_testpoint_paths()
        if not testpoint_paths:
            return
        
        # 从原始文件加载测试点数据
        loaded_count = 0
        for file_path in testpoint_paths:
            try:
                if os.path.exists(file_path):
                    self.current_file = file_path
                    # 直接调用加载方法，不通过load_testpoints以避免弹窗
                    self.load_testpoint_without_popup(file_path)
                    loaded_count += 1
            except Exception as e:
                pass
            
        # 如果有测试点，更新文件路径显示
        if self.testpoint_listbox.size() > 0:
            if self.current_file:
                self.file_path_var.set(f"已加载: {self.current_file} (共 {self.testpoint_listbox.size()} 个测试点)")
            
            # 默认选择第一个测试点
            self.testpoint_listbox.selection_clear(0, tk.END)
            self.testpoint_listbox.selection_set(0)
            self.testpoint_listbox.see(0)
            self.testpoint_listbox.event_generate("<<ListboxSelect>>")
        else:
            self.file_path_var.set("未能加载任何测试点")
            
    def load_testpoint_without_popup(self, file_path):
        """加载测试点数据，但不显示弹窗提示，用于程序启动时加载保存的测试点"""
        try:
            # 根据文件类型处理
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == ".json":
                # 处理JSON格式的测试点文件
                self.load_json_testpoints(file_path)
            else:
                # 处理普通文本格式的测试点文件
                self.load_text_testpoints(file_path)
                
            # 尝试查找与当前文件相关的测试点文件（同名不同扩展名）
            self.find_related_testpoints(file_path)
            
            # 更新测试点列表
            for tp_name in sorted(self.testpoint_data.keys()):
                # 检查测试点是否已经在列表中
                display_name = self.format_testpoint_name(tp_name)
                # 检查是否已存在于列表中
                exists = False
                for i in range(self.testpoint_listbox.size()):
                    if self.testpoint_listbox.get(i) == display_name:
                        exists = True
                        break
                # 只添加不存在的测试点
                if not exists:
                    self.testpoint_listbox.insert(tk.END, display_name)
            
        except Exception as e:
            pass
    
    def delete_selected_testpoints(self):
        """删除选中的测试点"""
        selection = self.testpoint_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先选择要删除的测试点")
            return
        
        # 确认是否删除
        if len(selection) == 1:
            confirm = messagebox.askyesno("确认", "确定要删除选中的测试点吗？")
        else:
            confirm = messagebox.askyesno("确认", f"确定要删除选中的 {len(selection)} 个测试点吗？")
            
        if not confirm:
            return
        
        # 获取所有选中的测试点名称
        to_delete = []
        for index in sorted(selection, reverse=True):
            display_name = self.testpoint_listbox.get(index)
            
            # 查找对应的原始测试点名称
            for tp_name in list(self.testpoint_data.keys()):
                if self.format_testpoint_name(tp_name) == display_name:
                    # 检查是否有打开的标签页
                    for tab_id, tab_info in list(self.open_tabs.items()):
                        if tab_info["original_name"] == tp_name:
                            # 关闭对应的标签页
                            self.close_tab(tab_id)
                    
                    # 从测试点数据中删除
                    del self.testpoint_data[tp_name]
                    to_delete.append(index)
                    break
        
        # 从列表中删除
        for index in to_delete:
            self.testpoint_listbox.delete(index)
        
        # 保存测试点数据
        self.save_testpoints_data()
        
        # 清空当前显示
        if self.current_view_mode == "side_by_side":
            self.left_input_text.delete(1.0, tk.END)
            self.right_output_text.delete(1.0, tk.END)
        
        # 更新文件路径显示
        if self.current_file:
            self.file_path_var.set(f"已加载: {self.current_file} (共 {self.testpoint_listbox.size()} 个测试点)")
        
        messagebox.showinfo("成功", "已删除选中的测试点")
    
    def save_testpoints_data(self):
        """保存测试点文件路径到testpoints.json"""
        # 从配置中加载已有的测试点文件路径
        testpoint_paths = self.config_manager.load_testpoint_paths()
        
        # 添加当前文件路径（如果存在且有效）
        if self.current_file and os.path.exists(self.current_file):
            # 检查是否已存在相同路径
            if self.current_file not in testpoint_paths:
                # 获取当前文件的基本名称（不含扩展名）
                current_file_base = os.path.splitext(os.path.basename(self.current_file))[0]
                
                # 检查是否已存在相同基本名称的测试点文件
                is_duplicate = False
                for existing_path in testpoint_paths:
                    existing_base = os.path.splitext(os.path.basename(existing_path))[0]
                    if current_file_base == existing_base:
                        is_duplicate = True
                        break
                
                # 只有当不是重复测试点时才添加到路径列表
                if not is_duplicate:
                    testpoint_paths.append(self.current_file)
        
        # 去除重复的测试点路径
        unique_paths = []
        unique_bases = set()
        
        for path in testpoint_paths:
            if os.path.exists(path):  # 确保文件存在
                base_name = os.path.splitext(os.path.basename(path))[0]
                if base_name not in unique_bases:
                    unique_bases.add(base_name)
                    unique_paths.append(path)
        
        # 保存测试点文件路径列表
        self.config_manager.save_testpoint_paths(unique_paths)

if __name__ == "__main__":
    app = TestPointViewer()
    app.mainloop()