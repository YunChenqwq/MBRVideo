#include <windows.h>
#include <winioctl.h>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <TlHelp32.h>
using namespace std;

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
// 将镜像文件写入指定驱动器
bool WriteImageToDrive(const string& drivePath, const string& imagePath) {
    // 以读写方式打开物理驱动器
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

    // 打开镜像文件
    ifstream imageFile(imagePath, ios::binary | ios::ate);
    if (!imageFile.is_open()) {
        cerr << "无法打开镜像文件 " << imagePath << endl;
        CloseHandle(hDrive);
        return false;
    }

    // 获取镜像文件大小
    streamsize imageSize = imageFile.tellg();
    imageFile.seekg(0, ios::beg);

    // 读取镜像文件内容
    char* buffer = new char[imageSize];
    if (!imageFile.read(buffer, imageSize)) {
        cerr << "读取镜像文件失败" << endl;
        delete[] buffer;
        imageFile.close();
        CloseHandle(hDrive);
        return false;
    }
    imageFile.close();

    // 写入驱动器
    DWORD bytesWritten;
    if (!WriteFile(hDrive, buffer, (DWORD)imageSize, &bytesWritten, NULL)) {
        cerr << "写入驱动器失败。错误代码: " << GetLastError() << endl;
        delete[] buffer;
        CloseHandle(hDrive);
        return false;
    }

    cout << "成功写入 " << bytesWritten << " 字节到 " << drivePath << endl;

    delete[] buffer;
    CloseHandle(hDrive);
    return true;
}
void GetPrivileges()
{
    HANDLE hProcess;
    HANDLE hTokenHandle;
    TOKEN_PRIVILEGES tp;
    hProcess = GetCurrentProcess();
    OpenProcessToken(hProcess, TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, &hTokenHandle);
    tp.PrivilegeCount = 1;
    LookupPrivilegeValue(NULL, SE_DEBUG_NAME, &tp.Privileges[0].Luid);
    tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;
    AdjustTokenPrivileges(hTokenHandle, FALSE, &tp, sizeof(tp), NULL, NULL);
    CloseHandle(hTokenHandle);
    CloseHandle(hProcess);
}
int main() {
    GetPrivileges();//古法提权
    cout << "物理驱动器写入工具" << endl;
    cout << "------------------" << endl;

    // 获取可用物理驱动器列表
    vector<string> drives = GetPhysicalDrives();

    if (drives.empty()) {
        cerr << "未找到可用的物理驱动器，请使用管理员权限运行本程序" << endl;
        return 0;
    }

    // 显示可用驱动器
    cout << "可用的物理驱动器:" << endl;
    for (size_t i = 0; i < drives.size(); i++) {
        cout << "[" << i << "] " << drives[i] << endl;
    }

    // 获取用户选择
    int choice;
    cout << "\n请输入要写入的驱动器编号 (0-" << drives.size() - 1 << "): ";
    cin >> choice;

    if (choice < 0 || choice >= (int)drives.size()) {
        cerr << "无效的选择" << endl;
        return 0;
    }

    string imagePath = "yourimg.img";

    // 检查镜像文件是否存在
    ifstream testFile(imagePath);
    if (!testFile.good()) {
        cerr << "错误: 找不到镜像文件 " << imagePath << endl;
        return 0;
    }
    testFile.close();

    // 确认操作
    cout << "\n警告: 这将完全覆盖 " << drives[choice] << " 上的所有数据!" << endl;
    cout << "你确定要继续吗? (y/n): ";
    char confirm;
    cin >> confirm;

    if (tolower(confirm) != 'y') {
        cout << "操作已取消" << endl;
        return 0;
    }

    // 执行写入操作
    cout << "开始写入..." << endl;
    if (WriteImageToDrive(drives[choice], imagePath)) {
        cout << "写入完成!" << endl;
    }
    else {
        cerr << "写入过程中发生错误" << endl;
    }
    return 0;
}