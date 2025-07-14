import mido
import math
import sys
import argparse

def note_to_freq(note):
    """将MIDI音符编号转换为频率(Hz)"""
    return 440.0 * (2.0 ** ((note - 69) / 12.0))

def process_midi(midi_file, tempo_factor=1.0, pitch_shift=0):
    """
    处理MIDI文件并生成频率-时长对
    
    参数:
        midi_file: MIDI文件路径
        tempo_factor: 速度系数(0.1-10.0)，1.0为原速，大于1加快，小于1减慢
        pitch_shift: 音高偏移(半音数)，正数升高，负数降低
    """
    # 参数验证
    if not 0.1 <= tempo_factor <= 10.0:
        raise ValueError("速度系数应在0.1到10.0之间")
    if not -24 <= pitch_shift <= 24:
        raise ValueError("音高偏移应在-24到24半音之间")
    
    mid = mido.MidiFile(midi_file)
    
    # 检测多轨MIDI文件
    if len(mid.tracks) > 1:
        print("警告：检测到多轨MIDI文件，仅处理第一轨")
    
    track = mid.tracks[0]
    notes = []  # 存储音符数据（频率,时长）
    current_time = 0  # 当前时间(ticks)
    active_notes = {}  # 当前活跃的音符 {note: start_time}

    for msg in track:
        current_time += msg.time
        
        # 音符开始事件
        if msg.type == 'note_on' and msg.velocity > 0:
            active_notes[msg.note] = current_time
            
        # 音符结束事件
        elif (msg.type == 'note_off' or 
              (msg.type == 'note_on' and msg.velocity == 0)):
            if msg.note in active_notes:
                duration = current_time - active_notes[msg.note]
                duration_ms = mido.tick2second(duration, mid.ticks_per_beat, 500000) * 1000
                
                # 应用速度系数调整时长
                adjusted_duration = max(10, round(duration_ms / tempo_factor))  # 最小10ms
                
                # 应用音高偏移
                note_with_shift = msg.note + pitch_shift
                freq = round(note_to_freq(note_with_shift))
                
                notes.append((freq, adjusted_duration))
                del active_notes[msg.note]

    # 添加结束标记
    notes.append((-1, -1))
    return notes

def generate_asm(notes, output_file="middata.asm"):
    """生成汇编格式的音乐数据"""
    with open(output_file, 'w') as f:
        f.write("; 自动生成的音乐数据\n")
        f.write("; 格式: 频率(Hz), 时长(ms)\n")
        f.write("music_data:\n")
        
        # 处理音符序列，在相同频率的音符间插入休止符
        processed_notes = []
        for i in range(len(notes)):
            processed_notes.append(notes[i])
            # 检查当前音符和下一个音符是否相同且不是结束标记
            if i < len(notes)-1 and notes[i][0] == notes[i+1][0] and notes[i][0] != -1:
                processed_notes.append((0, 8))  # 插入4ms的休止符
        
        # 每行写入5个音符（10个值）
        for i in range(0, len(processed_notes), 5):
            batch = processed_notes[i:i+5]
            line = "    dw " + ", ".join(f"{freq}, {duration}" for freq, duration in batch)
            f.write(line + "\n")

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='MIDI到ASM转换器')
    parser.add_argument('input_file', help='输入的MIDI文件')
    parser.add_argument('-s', '--speed', type=float, default=1.0,
                       help='播放速度系数 (0.1-10.0, 默认1.0)')
    parser.add_argument('-p', '--pitch', type=int, default=0,
                       help='音高偏移 (半音数, -24到24, 默认0)')
    parser.add_argument('-o', '--output', default='middata.asm',
                       help='输出文件名 (默认middata.asm)')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    try:
        notes = process_midi(args.input_file, args.speed, args.pitch)
        generate_asm(notes, args.output)
        print(f"转换完成：{args.input_file} -> {args.output}")
        print(f"速度系数: {args.speed}x, 音高偏移: {args.pitch}半音")
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)