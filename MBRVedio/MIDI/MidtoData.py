import mido
import os
import sys

acc = 25  # 精度 范围5,25,50,100。精度越高音乐越慢，精度越低速度越快

# 检查文件夹是否存在
if not os.path.exists('input.mid'):
    print("找不到输入音频input.midi|*￣ー￣|")
    sys.exit(1)

# 将MIDI文件转换为mus_freg和mus_time
def midi_to_data(midi_file):
    mus_freg = []
    mus_time = []

    mid = mido.MidiFile(midi_file)
    ticks_per_beat = mid.ticks_per_beat

    for i, track in enumerate(mid.tracks):
        tick_counter = 0
        for msg in track:
            tick_counter += msg.time
            if msg.type == 'note_on':
                if msg.velocity > 0:
                    freq = int(round(1193180.0 / (2**((msg.note - 69)/12.0)*440), 0))
                    mus_freg.append(freq)
                    mus_time.append(int(tick_counter * 100 / ticks_per_beat))
                    tick_counter = 0
                else:
                    mus_freg.append(-1)
                    mus_time.append(int(tick_counter * 100 / ticks_per_beat))
                    tick_counter = 0

    return mus_freg, mus_time

# 将mus_freg和mus_time保存到文件中
def save_data_to_file(mus_freg, mus_time, output_file):
    with open(output_file, 'w') as f:
        f.write("mus_freg dw ")
        f.write(','.join([str(x) for x in mus_freg]))
        f.write("\n")
        f.write("mus_time dw ")
        f.write(','.join([str(round(x/acc)) for x in mus_time]))
        f.write("\n")

    with open("data.bin", "wb") as out:
        for p, d in zip(mus_freg, mus_time):
            d_acc = round(d / acc)
            if d_acc <= 0:
                choice = input(f"发现一个音符的持续时间（d_acc={d_acc}）小于等于0，是否跳过该音符？(Y/N): ")
                if choice.upper() == "Y":
                    continue
                elif choice.upper() == "N":
                    d_acc += 1
                else:
                    print("无效的输入，将跳过该音符。")
                    continue
            out.write(bytes([p & 0xff, (d_acc - 1) << 5 | p >> 8]))


# 主函数
def main():
    midi_file = 'input.mid'  # MIDI文件路径
    output_file = 'data.asm'  # 输出文件路径

    mus_freg, mus_time = midi_to_data(midi_file)
    save_data_to_file(mus_freg, mus_time, output_file)

    print("转换完成，数据已保存到data.txt和data.bin文件中。")

if __name__ == '__main__':
    main()
