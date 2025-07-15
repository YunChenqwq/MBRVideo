import mido
from mido import MidiFile, merge_tracks

def merge_midi_tracks(input_file, output_file):
    """
    将多轨 MIDI 文件合并为单轨

    参数:
        input_file: 输入 MIDI 文件路径
        output_file: 输出单轨 MIDI 文件路径
    """
    try:
        # 读取 MIDI 文件
        mid = MidiFile(input_file)

        print(f"\n原始 MIDI 文件信息:")
        print(f"  类型: {mid.type}")
        print(f"  轨道数: {len(mid.tracks)}")
        print(f"  总时长: {mid.length:.2f} 秒")

        if len(mid.tracks) <= 1:
            print("文件已经是单轨 MIDI，无需处理。")
            return

        # 合并所有轨道
        merged_track = merge_tracks(mid.tracks)

        # 创建新 MIDI 文件
        new_mid = MidiFile(ticks_per_beat=mid.ticks_per_beat)
        new_mid.tracks.append(merged_track)

        # 保存合并后的 MIDI 文件
        new_mid.save(output_file)

        print(f"\n成功合并为单轨 MIDI 文件:")
        print(f"  保存路径: {output_file}")
        print(f"  新轨道数: {len(new_mid.tracks)}")

    except Exception as e:
        print(f"\n处理过程中出错: {str(e)}")

def main():
    print("MIDI 合并工具（多轨 → 单轨）")
    input_file = input("请输入输入 MIDI 文件路径: ").strip()
    output_file = input("请输入输出 MIDI 文件路径: ").strip()

    merge_midi_tracks(input_file, output_file)

if __name__ == "__main__":
    main()
