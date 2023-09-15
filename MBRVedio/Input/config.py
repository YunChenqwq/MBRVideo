EvilLock_config = {
  "循环次数": 10,  #需要循环播放动画的次数，指的是动画循环次数，和音乐因素无关。最大值 65535，循环播放 -1
  "音乐速度": 5,#音乐的速度 最大值10
  "是否加载自己程序": False, #//是 True 否 False
  "导出形式": "e_base64"#默认e_base64 就是加密后的base64 被evillock支持 十六进制：HEX 10进制DEC 
  "程序代码": " "	#在此添加你的代码
}
def check_config(config):
    if "循环次数" in config:
        loop_count = config["循环次数"]
        if not isinstance(loop_count, int) or loop_count < -1 or loop_count > 65535:
            return "循环次数值错误"

    if "音乐速度" in config:
        music_speed = config["音乐速度"]
        if not isinstance(music_speed, int) or music_speed < 1 or music_speed > 10:
            return "音乐速度值错误"

    if "是否加载自己程序" in config:
        load_program = config["是否加载自己程序"]
        if not isinstance(load_program, bool):
            return "是否加载自己程序值错误"
            
    if "导出形式" in config:
    export_format = config["导出形式"]
    if export_format not in ["e_base64", "HEX", "DEC"]:
        return "导出形式值错误"

    return None

result = check_config(EvilLock_config)
if result:
    print(result)
    exit(1)
else:
print("所有配置全部正确~o(〃＾▽＾〃)o")