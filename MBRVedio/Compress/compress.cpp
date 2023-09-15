#include <iostream>
#include <fstream>
#include <vector>

#define BLOCK_SIZE 32768 // 逐块处理的块大小
#define LMIN 4 // 最小匹配长度
#define LMAX 255 // 最大匹配长度

void compressBlock(const std::vector<unsigned char>& block, std::ofstream& outfile) {
    std::vector<unsigned char> bytes(block.size());
    int bi = 0;
    int pos = 0;

    while (pos < block.size()) {
        unsigned char l = 0, ml = 0; // 当前匹配长度、最大匹配长度
        short p = 0, mp = 0; // 当前匹配位置、最大匹配位置

        // 在当前位置之前查找最大匹配
        for (; p < pos; p++) {
            if (l >= LMAX)
                break;

            if (block[p] == block[pos + l]) {
                l++;
            } else {
                if (l >= ml) {
                    ml = l;
                    mp = p;
                }

                p -= l;
                l = 0;
            }
        }

        if (l >= ml) {
            ml = l;
            mp = p;
        }

        if (ml >= LMIN) {
            int bs = 0;
            while (bi > 0) {
                int bx = bi;
                if (bx > 128) bx = 128;

                unsigned char b = (1 << 7) | (bx - 1); // 标记字节

                outfile.write(reinterpret_cast<char*>(&b), 1);
                outfile.write(reinterpret_cast<char*>(bytes.data() + bs), bx);

                bi -= bx;
                bs += bx;
            }

            mp = (mp - ml);
            mp = (mp >> 8) | (mp << 8); // 以小端格式写入最大匹配位置
            outfile.write(reinterpret_cast<char*>(&mp), 2);
            outfile.write(reinterpret_cast<char*>(&ml), 1); // 写入最大匹配长度

            pos += ml;
        } else {
            bytes[bi++] = block[pos++];
        }
    }

    int bs = 0;
    while (bi > 0) {
        int bx = bi;
        if (bx > 128) bx = 128;

        char b = (1 << 7) | (bx - 1);
        outfile.write(&b, 1);
        outfile.write(reinterpret_cast<char*>(bytes.data() + bs), bx);

        bi -= 128;
        bs += 128;
    }
}

int main(int argc, char **argv) {
    if (argc != 3) {
        std::cerr << "错误的传参，正确传参： [输入文件] [输出文件]" << std::endl;
        return 1;
    }

    std::ifstream infile(argv[1], std::ios::binary);
    if (!infile) {
        std::cerr << "无法打开输入文件进行读取。" << std::endl;
        return 2;
    }

    std::ofstream outfile(argv[2], std::ios::binary);
    if (!outfile) {
        std::cerr << "无法打开输出文件进行写入。" << std::endl;
        return 2;
    }

    std::vector<unsigned char> block(BLOCK_SIZE);
    while (!infile.eof()) {
        infile.read(reinterpret_cast<char*>(block.data()), BLOCK_SIZE);
        std::streamsize bytesRead = infile.gcount();

        if (bytesRead > 0) {
            block.resize(bytesRead);
            compressBlock(block, outfile);
        }
    }

    infile.close();
    outfile.close();
    
    return 0;
}

