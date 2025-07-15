#include <windows.h>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <TlHelp32.h>

using namespace std;

#define BLOCK_SIZE (1024 * 1024) // 1MB 每块，嫌慢可以搞到更大，但是不建议

// 获取可用的物理驱动器列表
vector<string> GetPhysicalDrives() {
    vector<string> drives;
    char driveName[32];

    for (int i = 0; i < 16; i++) {
        sprintf_s(driveName, "\\\\.\\PhysicalDrive%d", i);

        HANDLE hDevice = CreateFileA(
            driveName,
            GENERIC_READ,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            NULL,
            OPEN_EXISTING,
            0,
            NULL
        );

        if (hDevice != INVALID_HANDLE_VALUE) {
            drives.push_back(driveName);
            CloseHandle(hDevice);
        }
    }

    return drives;
}

// 将镜像文件分块写入指定驱动器
bool WriteImageToDrive(const string& drivePath, const string& imagePath) {
    HANDLE hDrive = CreateFileA(
        drivePath.c_str(),
        GENERIC_WRITE | GENERIC_READ,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        NULL,
        OPEN_EXISTING,
        0,
        NULL
    );

    if (hDrive == INVALID_HANDLE_VALUE) {
        cerr << "无法打开驱动器 " << drivePath << "。错误代码: " << GetLastError() << endl;
        return false;
    }

    ifstream imageFile(imagePath, ios::binary);
    if (!imageFile.is_open()) {
        cerr << "无法打开镜像文件 " << imagePath << endl;
        CloseHandle(hDrive);
        return false;
    }

    vector<char> buffer(BLOCK_SIZE);
    DWORD bytesWritten = 0;
    ULONGLONG totalWritten = 0;
    int blockCount = 0;

    while (!imageFile.eof()) {
        imageFile.read(buffer.data(), BLOCK_SIZE);
        streamsize bytesRead = imageFile.gcount();

        if (bytesRead == 0) break;

        if (!WriteFile(hDrive, buffer.data(), (DWORD)bytesRead, &bytesWritten, NULL)) {
            cerr << "\n写入驱动器失败。错误代码: " << GetLastError() << endl;
            imageFile.close();
            CloseHandle(hDrive);
            return false;
        }

        totalWritten += bytesWritten;
        blockCount++;

        cout << "\r已写入: " << (totalWritten / 1024 / 1024) << " MB (" << blockCount << " blocks)" << flush;
    }

    cout << "\n 成功写入 " << totalWritten << " 字节到 " << drivePath << endl;

    imageFile.close();
    CloseHandle(hDrive);
    return true;
}

// 提权以访问物理驱动器
void GetPrivileges() {
    HANDLE hProcess = GetCurrentProcess();
    HANDLE hTokenHandle;
    TOKEN_PRIVILEGES tp;

    OpenProcessToken(hProcess, TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, &hTokenHandle);
    tp.PrivilegeCount = 1;
    LookupPrivilegeValue(NULL, SE_DEBUG_NAME, &tp.Privileges[0].Luid);
    tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;
    AdjustTokenPrivileges(hTokenHandle, FALSE, &tp, sizeof(tp), NULL, NULL);

    CloseHandle(hTokenHandle);
    CloseHandle(hProcess);
}

int main() {
    GetPrivileges();
    cout << "物理驱动器写入工具" << endl;
    cout << "------------------" << endl;

    // 获取可用物理驱动器
    vector<string> drives = GetPhysicalDrives();
    if (drives.empty()) {
        cerr << "未找到可用的物理驱动器，请使用管理员权限运行本程序" << endl;
        return 0;
    }

    // 列出驱动器
    cout << "可用的物理驱动器:" << endl;
    for (size_t i = 0; i < drives.size(); i++) {
        cout << "[" << i << "] " << drives[i] << endl;
    }

    // 用户选择驱动器
    int choice;
    cout << "\n请输入要写入的驱动器编号 (0-" << drives.size() - 1 << "): ";
    cin >> choice;

    if (choice < 0 || choice >= (int)drives.size()) {
        cerr << "无效的选择" << endl;
        return 0;
    }

    string imagePath;
    cout << "请输入要写入的镜像文件路径: ";
    cin >> ws;
    getline(cin, imagePath);

    // 检查镜像文件是否存在
    ifstream testFile(imagePath);
    if (!testFile.good()) {
        cerr << "错误: 找不到镜像文件 " << imagePath << endl;
        return 0;
    }
    testFile.close();

    cout << "\n 警告: 这将完全覆盖 " << drives[choice] << " 上的所有数据!" << endl;
    cout << "你确定要继续吗? (y/n): ";
    char confirm;
    cin >> confirm;

    if (tolower(confirm) != 'y') {
        cout << "操作已取消" << endl;
        return 0;
    }

    // 执行写入
    cout << "开始写入..." << endl;
    if (WriteImageToDrive(drives[choice], imagePath)) {
        cout << " 写入完成!" << endl;
    }
    else {
        cerr << "写入过程中发生错误" << endl;
    }

    return 0;
}
