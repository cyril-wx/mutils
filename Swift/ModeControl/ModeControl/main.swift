//
//  main.swift
//  ModeControl
//
//  Created by coreos on 2/23/19.
//  Copyright © 2019 coreos. All rights reserved.
//

//
//  ModeControl.swift
//  Anole
//
//  Created by Cyril on 12/28/18.
//  Modified by Cyril on 01/09/19.
//  Copyright © 2018 coreos. All rights reserved.
//

import Foundation
/// 模式控制
/// * cableName: cable Name（治具或cable线）,such as "cu.kanzi-30F465"
/// * connType: 连接方式（Kanzi/DCSD/TTFixture），默认DCSD
/// * ⚠️每个Unit/MLB 都需单独实例化此类, 并且要特别注意在治具连接时，使用ModeControl前第一次需要手动调用治具init，治具测试完后手动调用治具退出
class ModeControl{
    /// fd=-1说明Cable已断开， 需要重新初始化
    var fd: Int32! = -1
    private let cableName: String!
    private var rbuffer: String = ""
    private var wbuffer: String = ""
    private var connType: CONN_TYPE!
    private var timeout_skip_iboot: UInt32 = 10
    //   public static var MCs: [ModeControl] = []   // 用于管理所有已初始化的ModeControl实例, 全局变量
    
    /// ModeControl初始化函数
    /// * cableName: cable Name（治具或cable线）,such as "cu.kanzi-30F465"
    /// * connType: 连接方式（Kanzi/DCSD/TTFixture），默认TT
    init(cableName: String, connType: CONN_TYPE = CONN_TYPE.TTFixture){
        self.cableName = cableName
        self.connType = connType
        self.fd = self.getFD(cableStr: cableName)
        
        /*
         if self.fd != -1{
         print("Cable \(self.cableName) already inited.")
         return
         }   //  */
        if self.fd == -1{
            print("Init cable:/dev/\(cableName) error, ModeControl exit.")
            close(fd)
            return
        }
        
        if connType == CONN_TYPE.TTFixture{     // TT 治具连接方式 初始化
            /*    if ModeControl.MCs.count == 0{  // TT 治具首次进板需要上电操作
             TTFixtureStart(UnsafeMutablePointer<Int8>(mutating: (cableName as NSString).utf8String))
             }   // */
            let rev_in = TTFixtureStartWithFD(self.fd)
            if Int(rev_in) == 0 {
                print("Fixture start, ModeControl for cable \(cableName) initializing....")
                print("Enter to iBoot.")
                TTFixtureRecoveryWithFD(self.fd)
                //    ModeControl.append(mc: self)   // TT 治具连接成功，则将此ModeControl实例加入管理队列
            }
        }else{                              // 非TT治具
            // ModeControl.append(mc: self)
            print("ModeControl for cable \(cableName) initializing.")
        }
    }
    deinit {
        /*   if connType == CONN_TYPE.TTFixture{
         TTFixtureEndWithFD(self.fd)
         ModeControl.delete(mc: self)
         print("Fixture end...")
         if ModeControl.MCs.count == 0{
         fixtureEnd(UnsafeMutablePointer<Int8>(mutating: ("fixture_Serial" as NSString).utf8String))
         }
         }else{
         
         ModeControl.delete(mc: self)
         }   //  */
        close_serial(fd)
        print("ModeControl for cable \(cableName!) deinit.")
    }
    
    /*
     static func append(mc: ModeControl) -> Int32{
     for i in MCs{
     if i.cableName == mc.cableName{
     return mc.fd        // 如果管理队列已存在mc，则跳过append操作
     }
     }
     MCs.append(mc)
     return mc.fd           // 如果传进函数的参数mc没有在队列中存在，fd=0
     }
     static func  delete(mc: ModeControl){
     for i in 0...MCs.count{
     if MCs[i].cableName == mc.cableName{
     MCs.remove(at: i)
     }
     }
     
     }   // */
    
    /// Any mode to targetMode
    /// * targetMode: Unit/MLB 目标模式，使用（enum）Mode
    /// * timeout: ios模式切换超时时间 默认10s
    /// * 不保证模式切换一定成功
    /// * 在模式切换后 请使用deviceModeJudge()获取当前模式，用它确保模式切换成功
    func modeChange(targetMode: String, timeout: Int = 10) -> Bool{
        
        var result: Bool = false
        let cmode = self.deviceModeJudge()
        if cmode == targetMode{
            return true
        }
        switch targetMode {
        case MODE.iBoot.rawValue:
            if cmode == MODE.Diags.rawValue{
                result = iBoot_to_diags(iBoot_to_diags: false)
            }else if cmode == MODE.iOS.rawValue{
                result = iBoot_to_iOS(iBoot_to_iOS: false, timeout: timeout)
            }else if cmode == MODE.iOS_Unlogin.rawValue{
                result = iBoot_to_iOS(iBoot_to_iOS: false, timeout: timeout)
            }
            break
        case MODE.Diags.rawValue:
            if cmode == MODE.iBoot.rawValue{
                result = iBoot_to_diags(iBoot_to_diags: true)
            }else if cmode == MODE.iOS.rawValue{
                result = diags_to_iOS(diags_to_iOS: false, timeout: timeout)
            }else if cmode == MODE.iOS_Unlogin.rawValue{
                result = diags_to_iOS(diags_to_iOS: false, timeout: timeout)
            }
            break
        case MODE.iOS.rawValue:
            if cmode == MODE.iBoot.rawValue{
                result = iBoot_to_iOS(iBoot_to_iOS: true, timeout: timeout)
            }else if cmode == MODE.Diags.rawValue{
                result = diags_to_iOS(diags_to_iOS: true, timeout: timeout)
            }else if cmode == MODE.iOS_Unlogin.rawValue{
                loginToiOS()
            }
            break
        default:
            print("模式跳转错误：modeChange() -> 未知的跳转模式")
            break
        }
        return result
    }
    /// 模式判断
    /// * retryTimes: 重试次数，默认20次
    /// * return: 返回 当前模式 字符串
    func deviceModeJudge(retryTimes: Int = 20) -> MODE.RawValue {
        
        var mode_flag = ""
        for _ in 0..<retryTimes {
            self.deviceWrite(cmdStr: "\r\n")
            self.rbuffer = self.deviceRead()
            print("!#\(self.cableName!):\(rbuffer)#!")
            if !rbuffer.isEmpty {
                mode_flag = rbuffer
                if mode_flag.lengthOfBytes(using: .utf8) < 20 { // String.contain方式不适合判断iBoot模式
                    if (mode_flag.range(of: "]") != nil) {
                        return MODE.iBoot.rawValue
                    }
                }else if mode_flag.contains(":-)") {
                    return MODE.Diags.rawValue
                }else if mode_flag.contains("root#"){
                    return MODE.iOS.rawValue
                }else if mode_flag.contains("login:") || mode_flag.contains("Password:"){
                    return MODE.iOS_Unlogin.rawValue
                }else{
                    //print("deviceModeJudge(): 无法判断当前连接Cable:\(cableName) 的设备模式， 重试中...")
                    continue    // 重试判断
                }
            }
        }
        print("deviceModeJudge(): 无法判断当前连接Cable:\(cableName) 的设备模式, 设备可能已断开连接")
        return MODE.Unknown.rawValue
    }
    /// 适用于iBoot命令行/Diag模式的命令写入与读取
    /// * 请不要使用此函数在os/iboot非命令行模式下，否则程序崩溃。
    /// * 注意此函数返回的数据，需要根据不同模式进行不同格式化处理
    func deviceReadAndWrite( cmdStr: String, timeout: Int32 = 1) -> String {
        if fd == -1{
            print("deviceWrite: Cable连接已断开，写入失败。")
        }
        let res:String? = String(cString: diags_cmd_rwt(fd, cmdStr + "\n", timeout))
        if res == nil{
            return ""
        }
        return res!
    }
    
    /// ⚠️警告：deviceReadAndWriteOniOS coding 未完成
    func deviceReadAndWriteOniOS() -> String{
        /*    let retv = DeviceDetect().runCommand(launchPath: "/usr/local/bin/FactoryServicesHost", arguments: argc, retry: 1).1
         if !retv.isEmpty{
         print(retv)
         }*/
        var result:String = ""
        print("⚠️警告：deviceReadAndWriteOniOS coding 未完成")
        return result
    }
    
    /// 适用于iBoot/Diag/OS模式的命令写入
    /// * 注意不要将多条命令合并写入
    func deviceWrite( cmdStr: String, timeout: Int32 = 1) -> Int32 {
        if fd != -1{
            //return diags_cmd_wt(fd, cmdStr + "\n", timeout)   // 这个不适用于治具？
            return write_serial(fd, cmdStr + "\n", timeout)
        }else{
            print("deviceWrite: Cable连接已断开，写入失败。")
            return -1
        }
        
    }
    
    /// 适用于iBoot/Diag/OS模式的读入
    /// * return: 串口的输出数据
    /// * 注意此函数返回的数据，需要根据不同模式进行不同格式化处理
    func deviceRead() -> String {
        var read_num: Int32 = 0
        let tempBuf = [CChar](repeating: 0, count: 1024)
        while true {
            read_num = read_serial_for_mode_judge(fd, UnsafeMutablePointer<Int8>(mutating: tempBuf), UnsafeMutablePointer<Int8>(mutating: ""))
            if read_num == 0 {
                break
            }
            if read_num == -1 {
                print("Read device \(self.cableName): \(self.fd) error!")
                break
            }
            
            if tempBuf[0] == 0 {
                continue
            }else{
                let temp = String.init(utf8String: tempBuf)
                if temp != nil {
                    //因为是模式判断不需要考虑是否有丢数据，只拿最后的数据。
                    self.rbuffer = temp!
                }else{
                    continue
                }
                return self.rbuffer
            }
        }
        return self.rbuffer
    }
    
    /// iboot_to_diags 或 diags_to_iboot
    /// * iBoot_to_diags: true:iBoot_to_diags, false: diags_to_iBoot
    /// * timeout: 模式切换超时时间 默认5s
    /// * 不保证模式切换一定成功，可使用getCMode()获取当前模式
    private func iBoot_to_diags(iBoot_to_diags: Bool, timeout:Int = 5) -> Bool{
        let cmode = self.deviceModeJudge()
        if iBoot_to_diags{
            if cmode == MODE.iBoot.rawValue{
                self.deviceWrite(cmdStr: "diags")
                for _ in 0..<timeout {
                    if deviceModeJudge() == MODE.Diags.rawValue {
                        return true        // 成功进入Diags模式
                    }
                    sleep(1)
                }
            }else{
                print("iBoot_to_diags(): 模式跳转错误, 当前非iBoot模式")
            }
        }else{  // diags_to_iBoot
            if cmode == MODE.Diags.rawValue{
                self.deviceWrite(cmdStr: "nvram --set auto-boot false")
                self.deviceWrite(cmdStr: "nvram --save")
                self.deviceWrite(cmdStr: "res")
                for _ in 0..<timeout {
                    if deviceModeJudge() == MODE.iBoot.rawValue {
                        return true        // 成功进入iBoot模式
                    }
                    sleep(1)
                }
            }else{
                print("diags_to_iBoot(): 模式跳转错误, 当前非diags模式")
            }
        }
        print("模式跳转失败：iBoot_to_diags(\(iBoot_to_diags))")
        return false
    }
    
    /// iBoot_to_iOS 或 iBoot_to_iOS
    /// * iBoot_to_iOS: true:iBoot_to_iOS, false: iOS_to_iBoot
    /// * timeout: 模式切换超时时间 默认15s
    private func iBoot_to_iOS(iBoot_to_iOS: Bool, timeout: Int = 15) -> Bool{
        let cmode = self.deviceModeJudge()
        if iBoot_to_iOS{
            if cmode == MODE.iBoot.rawValue{
                self.deviceWrite(cmdStr: "setenv auto-boot true")
                self.deviceWrite(cmdStr: "setenv boot-command fsboot")
                self.deviceWrite(cmdStr: "saveenv")
                self.deviceWrite(cmdStr: "fsboot")
                for _ in 0..<timeout {
                    if deviceModeJudge() == MODE.iOS.rawValue || deviceModeJudge() == MODE.iOS_Unlogin.rawValue{
                        self.loginToiOS()   //自动登录iOS
                        return true         // 不管是否成功登录iOS，此时已进入iOS模式，返回true
                    }
                    sleep(1)
                }
            }else{
                print("iBoot_to_iOS(): 模式跳转错误, 当前非iBoot模式")
            }
        }else{  // iOS_to_iBoot
            if cmode == MODE.iOS.rawValue || cmode == MODE.iOS_Unlogin.rawValue{
                self.loginToiOS()
                self.deviceWrite(cmdStr: "\n nvram auto-boot=false")    // 这里必须要有“\n”，否则执行不成功，测试和iOS模式有关
                self.deviceWrite(cmdStr: "\n nvram boot-command=''")
                self.deviceWrite(cmdStr: "\n reboot")
                for _ in 0..<timeout {
                    if deviceModeJudge() == MODE.iBoot.rawValue{
                        return true         // 成功进入iBoot
                    }
                    sleep(1)
                }
            }else{
                print("iOS_to_iBoot(): 模式跳转错误, 当前非iOS模式")
            }
        }
        print("模式跳转失败：iBoot_to_iOS(\(iBoot_to_iOS))")
        return false
    }
    
    /// diags_to_iOS 或 iOS_to_diags
    /// * diags_to_iOS: true:diags_to_iOS, false: iOS_to_diags
    /// * timeout: 模式切换超时时间 默认10s, 若手动设定值请不要小于10s,否则设定无效
    private func diags_to_iOS(diags_to_iOS: Bool, timeout: Int = 15) -> Bool{
        let cmode = self.deviceModeJudge()
        if diags_to_iOS{
            if cmode == MODE.Diags.rawValue{
                /*
                 self.deviceWrite(cmdStr: "\n nvram --set auto-boot true")
                 self.deviceWrite(cmdStr: "\n nvram --set boot-command fsboot")
                 self.deviceWrite(cmdStr: "\n nvram --save")
                 self.deviceWrite(cmdStr: "\n res")
                 */
                iBoot_to_diags(iBoot_to_diags: false)
                iBoot_to_iOS(iBoot_to_iOS: true)
                //sleep(timeout_skip_iboot)
                for _ in 0..<timeout {
                    if deviceModeJudge() == MODE.iOS.rawValue || deviceModeJudge() == MODE.iOS_Unlogin.rawValue{
                        self.loginToiOS()   //自动登录iOS
                        return true         // 不管是否成功登录iOS，此时已进入iOS模式，返回true
                    }
                    sleep(1)
                }
            }else{
                print("diags_to_iOS(): 模式跳转错误, 当前非diags模式")
            }
        }else{  // iOS_to_diags
            if cmode == MODE.iOS.rawValue || cmode == MODE.iOS_Unlogin.rawValue{
                /*
                 self.loginToiOS()
                 self.deviceWrite(cmdStr: "\n nvram auto-boot=true")
                 self.deviceWrite(cmdStr: "\n nvram boot-command=diags")
                 self.deviceWrite(cmdStr: "\n reboot")
                 //sleep(timeout_skip_iboot)
                 */
                iBoot_to_iOS(iBoot_to_iOS: false)
                iBoot_to_diags(iBoot_to_diags: true)
                for i in 0..<timeout {
                    if deviceModeJudge() == MODE.Diags.rawValue {
                        return true          // 成功进入Diags模式
                    }
                    sleep(1)
                }
            }else{
                print("iOS_to_diags(): 模式跳转错误, 当前非iOS模式")
            }
        }
        print("模式跳转失败：diags_to_iOS(\(diags_to_iOS))")
        return false
    }
    
    /// 登陆ios
    /// * return: true: 登陆成功  false: 登陆失败
    private func loginToiOS(retryTimes: Int = 10) -> Bool{
        for _ in 0..<retryTimes {
            let current_mode = self.deviceModeJudge()
            if(current_mode == MODE.iOS_Unlogin.rawValue){
                print("loginToiOS(): 开始执行登陆iOS ...")
                self.deviceWrite(cmdStr: "root")
                self.deviceWrite(cmdStr: "alpine")
                let tmp = self.deviceRead()
                if(tmp.contains("root#")){
                    return true
                }
            }else if(current_mode == MODE.iOS.rawValue){
                return true
            }else{
                print("loginToiOS(): 当前不是iOS模式, 自动登录停止.")
            }
        }
        print("loginToiOS(): 未能登陆iOS.")
        return false
    }
    /// 获取fd用于串口通信, 适用于非治具连接
    /// * cableStr: cable name, 如 cu.kanzi-30F465
    /// * runEnv: 连接方式（enum）CONN_TYPE，包含治具、DCSD、Kanzi等连接方式
    /// * timeout: 获取fd 的超时时间，默认为10s
    /// * return: fd（int32）
    private func getFD(cableStr: String, timeout:Int = 10) -> Int32{
        var fd: Int32 = -1
        var times = 0
        /*      for i in ModeControl.MCs{
         if i.cableName == cableStr{
         if i.fd != -1{
         return i.fd     // 如果fd已存在则直接返回
         }
         }
         }   */
        if connType == CONN_TYPE.DCSD_CABLE || connType == CONN_TYPE.KANZI_CABLE{
            for i in 0...timeout{
                // 115200 是针对于非治具连接
                // 230400 是针对治具连接
                // fd = init_serial_with_baudrate(UnsafeMutablePointer<Int8>(mutating: ("/dev/\(cableStr)" as NSString).utf8String), 115200)
                fd = init_serial(UnsafeMutablePointer<Int8>(mutating: ("/dev/\(cableStr)" as NSString).utf8String))
                sleep(1)
                if (fd != -1){
                    print("init serial in father, cable:/dev/\(cableStr), fd:\(fd)")
                    return fd
                }
            }
        }else if connType == CONN_TYPE.TTFixture{
            for i in 0...timeout{
                // 115200 是针对于非治具连接
                // 230400 是针对治具连接
                //TTfixtureInitReturnFD
                fd = init_serial_with_baudrate(UnsafeMutablePointer<Int8>(mutating: ("/dev/\(cableStr)" as NSString).utf8String), BAUD_RATE.TTFixture.rawValue)
                sleep(1)
                if (fd != -1){
                    print("init serial in father, cable:/dev/\(cableStr), fd:\(fd)")
                    return fd
                }
                
            }
        }
        close(fd)
        print("Init serial for cable:/dev/\(cableStr) error, maybe no cable connected.")
        return -1
    }
}

print("===快速连接机台&执行命令工具===")
print("#-- Author: Cyril --------#")
print("#-- Create: 190615 -------#")
print("#-- Dep: NPI-SW-CoreOS ---#")
print("===========================")
print("请输入cableName（参照格式：cu.kanzi-30EE63）：")
let cable_name:String = String(cString: readbuffer())
print("请输入机台待执行命令：")
let cmd:String = String(cString: readbuffer())
let mc = ModeControl.init(cableName: cable_name,connType: CONN_TYPE.DCSD_CABLE)
print("执行结果：")
mc.deviceWrite(cmdStr: cmd)
print(mc.deviceRead())




