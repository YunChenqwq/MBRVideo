import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import subprocess
import shutil
import binascii
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageTk
import io
import requests

class MBRvideoBuilder:
    def __init__(self, root):
        self.root = root
        self.root.title("MBRvideo Builder Tool v2.0")
        
        # 设置窗口大小和最小尺寸
        self.root.geometry("700x800")
        self.root.minsize(650, 750)
        
        # 初始化变量
        self.video_input = tk.StringVar(value=os.path.abspath("input.mp4"))
        self.video_output = tk.StringVar(value="output_video.bin")
        self.video_mode = tk.StringVar(value="stretch")
        self.use_cuda = tk.BooleanVar(value=False)
        
        self.midi_input = tk.StringVar(value="")  # Initial empty, not required
        self.midi_speed = tk.DoubleVar(value=1.0)  # Float type, 1.0 means original speed
        self.midi_pitch = tk.IntVar(value=0)  # Pitch adjustment parameter
        self.midi_output = tk.StringVar(value="middata.asm")
        
        self.loader_type = tk.StringVar(value="loop")  # Bootloader type
        self.loader_binary = tk.StringVar(value="loader.bin")
        self.img_output = tk.StringVar(value="yourimg.img")
        
        self.build_in_progress = False
        self.setup_ui()
        
        # 加载作者头像
        self.load_author_avatar()
    
    def load_author_avatar(self):
        """加载作者头像/Load author avatar"""
        try:
            response = requests.get("https://i1.hdslb.com/bfs/face/6a76de57b2606e893eae08935e711d7884cec380.jpg")
            image = Image.open(io.BytesIO(response.content))
            image = image.resize((50, 50), Image.Resampling.LANCZOS)
            self.avatar_img = ImageTk.PhotoImage(image)
            
            # 创建作者信息标签
            author_frame = ttk.Frame(self.root)
            author_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
            
            # 头像
            avatar_label = ttk.Label(author_frame, image=self.avatar_img)
            avatar_label.pack(side=tk.LEFT, padx=5)
            
            # 作者信息
            author_info = ttk.Label(author_frame, 
                                  text="Author: YunChen\nGitHub: https://github.com/YunChenqwq",
                                  justify=tk.LEFT)
            author_info.pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            print(f"Failed to load avatar: {e}")
    
    def setup_ui(self):
        """Initialize user interface/初始化用户界面"""
        # Main frame/主框架
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Video settings/视频设置
        video_frame = ttk.LabelFrame(main_frame, 
                                   text="Video/GIF Settings/视频/GIF设置", 
                                   padding=10)
        video_frame.pack(fill=tk.X, pady=5)
        
        # 修改文件类型为支持视频和GIF
        self.create_file_row(video_frame, 
                           "Video/GIF Input/视频/GIF输入:", 
                           self.video_input, 
                           [("Video Files/视频文件", "*.mp4 *.avi"), ("GIF Files/GIF文件", "*.gif")])
        
        self.create_entry_row(video_frame, 
                            "Video Output/视频输出:", 
                            self.video_output)
        
        # Video mode with bilingual description
        ttk.Label(video_frame, 
                 text="Video Mode/视频模式:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        
        video_modes = [
            ("stretch - 拉伸", "stretch"),
            ("keep_aspect - 保持宽高比", "keep_aspect")
        ]
        
        mode_display = [mode[0] for mode in video_modes]
        mode_values = [mode[1] for mode in video_modes]
        
        self.video_mode_combobox = ttk.Combobox(
            video_frame,
            textvariable=self.video_mode,
            values=mode_display,
            width=40,
            state="readonly"
        )
        self.video_mode_combobox.grid(row=2, column=1, sticky=tk.W)
        self.video_mode_combobox.current(0)
        
        ttk.Checkbutton(video_frame, 
                       text="Enable CUDA Acceleration/启用CUDA加速", 
                       variable=self.use_cuda).grid(row=3, column=1, sticky=tk.W)
        
        # MIDI settings (optional)/MIDI设置(可选)
        midi_frame = ttk.LabelFrame(main_frame, 
                                  text="MIDI Audio Settings (Optional)/MIDI音频设置(可选)", 
                                  padding=10)
        midi_frame.pack(fill=tk.X, pady=5)
        
        # MIDI file selection
        self.create_file_row(midi_frame, 
                           "MIDI Input File/MIDI输入文件:", 
                           self.midi_input, 
                           [("MIDI Files/MIDI文件", "*.mid *.midi")])
        
        self.create_entry_row(midi_frame, 
                            "ASM Output File/ASM输出文件:", 
                            self.midi_output)
        
        # Speed control
        speed_frame = ttk.Frame(midi_frame)
        speed_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        ttk.Label(speed_frame, 
                 text="Playback Speed/播放速度:").pack(side=tk.LEFT, padx=5)
        
        ttk.Scale(speed_frame, 
                 from_=0.5, 
                 to=3.0, 
                 variable=self.midi_speed, 
                 orient=tk.HORIZONTAL, 
                 length=150).pack(side=tk.LEFT)
        
        self.speed_display = ttk.Label(speed_frame, text="1.0x", width=5)
        self.speed_display.pack(side=tk.LEFT, padx=5)
        
        # Pitch control
        pitch_frame = ttk.Frame(midi_frame)
        pitch_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        ttk.Label(pitch_frame, 
                 text="Pitch Adjustment/移调:").pack(side=tk.LEFT, padx=5)
        
        ttk.Scale(pitch_frame, 
                 from_=-12, 
                 to=12, 
                 variable=self.midi_pitch,
                 orient=tk.HORIZONTAL, 
                 length=150).pack(side=tk.LEFT)
        
        self.pitch_display = ttk.Label(pitch_frame, text="±0", width=5)
        self.pitch_display.pack(side=tk.LEFT, padx=5)
        
        # Bind variable change events
        self.midi_speed.trace_add("write", self.update_speed_display)
        self.midi_pitch.trace_add("write", self.update_pitch_display)
        
        # Bootloader settings/引导程序设置
        loader_frame = ttk.LabelFrame(main_frame, 
                                    text="Bootloader Settings/引导程序设置", 
                                    padding=10)
        loader_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(loader_frame, 
                 text="Bootloader Type/引导程序类型:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        
        ttk.Radiobutton(loader_frame, 
                       text="Loop Mode循环模式", 
                       variable=self.loader_type, 
                       value="loop").grid(row=0, column=1, sticky=tk.W)
        
        ttk.Radiobutton(loader_frame, 
                       text="Jump Mode/跳转模式", 
                       variable=self.loader_type, 
                       value="jump").grid(row=1, column=1, sticky=tk.W)
        
        self.create_entry_row(loader_frame, 
                            "Bootloader Binary/引导程序输出bin:", 
                            self.loader_binary)
        
        # Output settings/输出设置
        output_frame = ttk.LabelFrame(main_frame, 
                                    text="Output Settings/输出设置", 
                                    padding=10)
        output_frame.pack(fill=tk.X, pady=5)
        
        self.create_entry_row(output_frame, 
                            "Image Output File/镜像输出文件:", 
                            self.img_output)
        
        # Build and view buttons/构建和查看按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        self.build_btn = ttk.Button(btn_frame, 
                                  text="Start Build/开始", 
                                  command=self.start_build, 
                                  width=15)
        self.build_btn.pack(side=tk.LEFT, padx=5)
        
        # Add HEX export button
        ttk.Button(btn_frame, 
                  text="Export HEX/导出HEX", 
                  command=self.export_hex, 
                  width=15).pack(side=tk.LEFT, padx=5)
        
        # Log output/日志输出
        log_frame = ttk.LabelFrame(main_frame, 
                                 text="Build Log/日志", 
                                 padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_frame, height=15, state=tk.DISABLED, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        scrollbar = ttk.Scrollbar(self.log_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
    
    def export_hex(self):
        """Export binary file as HEX format/将二进制文件导出为HEX格式"""
        file_path = filedialog.askopenfilename(
            initialdir=os.path.join(os.getcwd(), "build"),
            title="Select file to export/选择要导出的文件",
            filetypes=[("Binary Files/二进制文件", "*.bin *.img"), ("All Files/所有文件", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Convert to HEX format (0x0E, 0x00 style)
            hex_str = ", ".join(f"0X{byte:02X}" for byte in content)
            
            # Write to hdx.txt
            output_path = os.path.join(os.path.dirname(file_path), "hdx.txt")
            with open(output_path, 'w') as f:
                f.write(hex_str)
            
            # Open the file with default text editor
            if os.name == 'nt':  # Windows
                os.startfile(output_path)
            elif os.name == 'posix':  # macOS and Linux
                subprocess.run(['open', output_path] if sys.platform == 'darwin' else ['xdg-open', output_path])
            
            self.log(f"\nHEX data exported to/HEX数据已导出到: {output_path}")
            
        except Exception as e:
            messagebox.showerror("Error/错误", f"Failed to export HEX/导出HEX失败: {str(e)}")
            self.log(f"\n!!! HEX export failed/HEX导出失败: {str(e)}")
    
    def update_speed_display(self, *args):
        """Update speed display/更新速度显示"""
        speed = round(self.midi_speed.get(), 1)
        self.speed_display.config(text=f"{speed}x")
    
    def update_pitch_display(self, *args):
        """Update pitch display/更新音高显示"""
        pitch = self.midi_pitch.get()
        self.pitch_display.config(text=f"{pitch:+d}")
    
    def create_file_row(self, parent, label, var, filetypes):
        """Create file selection row/创建文件选择行"""
        row = parent.grid_size()[1]
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(parent, textvariable=var, width=50).grid(row=row, column=1, sticky=tk.EW)
        ttk.Button(parent, text="Browse.../浏览...", command=lambda: self.browse_file(var, filetypes)).grid(row=row, column=2)
        
    def create_entry_row(self, parent, label, var):
        """Create input row/创建输入行"""
        row = parent.grid_size()[1]
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(parent, textvariable=var, width=50).grid(row=row, column=1, columnspan=2, sticky=tk.EW)
        
    def browse_file(self, var, filetypes):
        """File browse dialog/文件浏览对话框"""
        initial_file = var.get()
        initial_dir = os.path.dirname(initial_file) if os.path.exists(initial_file) else os.getcwd()
        
        filename = filedialog.askopenfilename(
            initialdir=initial_dir,
            initialfile=os.path.basename(initial_file),
            filetypes=filetypes
        )
        
        if filename:
            var.set(os.path.abspath(filename))
    
    def log(self, message):
        """Log output/日志输出"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()
    
    def clear_log(self):
        """Clear log/清空日志"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def start_build(self):
        """Start build process/开始构建过程"""
        if self.build_in_progress:
            return
            
        self.build_in_progress = True
        self.build_btn.config(state=tk.DISABLED)
        self.clear_log()
        
        # Run build process in background thread
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.executor.submit(self.run_build)
    
    def run_build(self):
        """Execute build process/执行构建过程"""
        try:
            self.log("=== Start Build Process ===/=== 开始构建过程 ===")
            
            # Create necessary directories
            self.create_directories()
            
            # Process video or GIF
            self.process_media()
            
            # Process MIDI (with new parameters)
            self.process_midi()
            
            # Compile bootloader
            self.compile_loader()
            
            # Create final image
            self.create_image()
            
            self.log("\n=== Build Successful ===/=== 构建成功 ===")
            self.log(f"Output File/输出文件: build/{self.img_output.get()}")
            
        except Exception as e:
            self.log(f"\n!!! Build Failed/构建失败: {str(e)}")
        finally:
            self.build_in_progress = False
            self.root.after(0, lambda: self.build_btn.config(state=tk.NORMAL))
    
    def create_directories(self):
        """Create necessary directories/创建必要的目录"""
        self.log("Creating directory structure.../创建目录结构...")
        os.makedirs("build", exist_ok=True)
        os.makedirs("asm", exist_ok=True)
    
    def process_media(self):
        """Process video or GIF file/处理视频或GIF文件"""
        input_file = self.video_input.get()
        video_output = f"build/{self.video_output.get()}"
        
        # 获取文件扩展名
        file_ext = os.path.splitext(input_file)[1].lower()
        
        # Get actual mode value (remove description)
        raw_mode = self.video_mode.get().split(" - ")[0] if " - " in self.video_mode.get() else self.video_mode.get()
        use_cuda = self.use_cuda.get()
        
        self.log(f"\nProcessing Media/处理媒体文件: {os.path.basename(input_file)}")
        self.log(f"Output File/输出文件: {video_output}")
        self.log(f"Mode/模式: {raw_mode}, CUDA: {'Yes/是' if use_cuda else 'No/否'}")
        
        # 根据文件类型选择处理脚本
        if file_ext == '.gif':
            script = "gif2bin.py"
            cmd = [
                "python", script,
                input_file,
                "-o", video_output,
                "-m", raw_mode
            ]
        else:  # 默认为视频处理
            script = "video2bin_cuda.py" if use_cuda else "video2bin.py"
            cmd = [
                "python", script,
                input_file,
                "-o", video_output,
                "-m", raw_mode  # Pass pure mode parameter
            ]
        
        self.run_command(cmd, "Media Processing/媒体处理")
    
    def process_midi(self):
        """Process MIDI file/处理MIDI文件"""
        midi_input = self.midi_input.get()
        
        if not midi_input or not os.path.exists(midi_input):
            self.log("\nNo MIDI file specified, generating empty music data/未指定MIDI文件，生成空音乐数据")
            midi_output = f"asm/{self.midi_output.get()}"
            
            # Generate MIDI data with only end marker
            with open(midi_output, 'w') as f:
                f.write("music_data:\n")
                f.write("    dw 0,  0\n")
                f.write("    dw -1, -1\n")
            return
        
        midi_speed = str(round(self.midi_speed.get(), 2))  # Keep 2 decimal places
        midi_pitch = str(self.midi_pitch.get())
        midi_output = f"asm/{self.midi_output.get()}"
        
        self.log(f"\nProcessing MIDI/处理MIDI: {os.path.basename(midi_input)}")
        self.log(f"Speed/速度: x{midi_speed}, Pitch/音高: {midi_pitch} semitones/半音, Output/输出: {midi_output}")
        
        cmd = [
            "python", "mid2data.py",
            midi_input,
            "-s", midi_speed,
            "-p", midi_pitch,
            "-o", midi_output
        ]
        
        self.run_command(cmd, "MIDI Processing/MIDI处理")
    
    def compile_loader(self):
        """Compile bootloader/编译引导程序"""
        loader_type = self.loader_type.get()
        loader_source = f"asm/loader{'_jmp' if loader_type == 'jump' else ''}.asm"
        loader_binary = f"build/{self.loader_binary.get()}"
        
        if not os.path.exists(loader_source):
            raise FileNotFoundError(f"Bootloader source file not found/引导程序源文件不存在: {loader_source}")
        
        self.log(f"\nCompiling Bootloader/编译引导程序: {os.path.basename(loader_source)}")
        self.log(f"Output File/输出文件: {loader_binary}")
        
        current_dir = os.getcwd()
        cmd = [
            "nasm", "-f", "bin",
            "-i", f"{current_dir}/asm/",  # 添加包含路径
            loader_source,
            "-o", loader_binary
        ]
        
        self.run_command(cmd, "Bootloader Compilation/引导程序编译")
    
    def create_image(self):
        """Create final image/生成最终镜像"""
        loader_binary = f"build/{self.loader_binary.get()}"
        video_output = f"build/{self.video_output.get()}"
        img_output = f"build/{self.img_output.get()}"
        
        self.log(f"\nCreating Final Image/生成最终镜像: {img_output}")
        
        try:
            with open(img_output, 'wb') as outfile:
                # Merge bootloader and video data
                with open(loader_binary, 'rb') as infile:
                    outfile.write(infile.read())
                with open(video_output, 'rb') as infile:
                    outfile.write(infile.read())
        except Exception as e:
            raise Exception(f"Failed to create image/生成镜像失败: {str(e)}")
    
    def run_command(self, cmd, process_name):
        """Execute external command/执行外部命令"""
        self.log(f"Executing Command/执行命令: {' '.join(cmd)}")
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log(output.strip())
            
            if process.returncode != 0:
                raise Exception(f"{process_name} failed/失败 (Exit Code/退出码: {process.returncode})")
                
        except Exception as e:
            raise Exception(f"{process_name} execution error/执行错误: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MBRvideoBuilder(root)
    root.mainloop()