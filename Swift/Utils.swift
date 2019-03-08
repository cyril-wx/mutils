//
//  Utils.swift
//  AutoPanic
//
//  Created by Cyril on 3/7/19.
//  Copyright © 2019 coreos. All rights reserved.
//

import Foundation


/// 工具库，包含各种通用工具模版  --- Cyril
public class Utils{
    
    /// 读取plist文件 -- Cyril
    /// * filePath: plist文件路径
    /// plist文件默认放在 NSHomeDirectory()+"/Anole/Config/" 目录下
    /// 数据类型为 NSDictionary<String, NSDictionary>
    func readPlist(filePath: String) -> NSDictionary? {
        if dirExists(path: filePath){
            //判断对象类型
            //let name = type(of: data); print(name);
            let data: NSDictionary? =  NSDictionary(contentsOfFile: filePath)
            if data == nil{
                print("readPlist Failed: [DataNilError] Please check content of file: ", filePath)
            }
            ///let name = type(of: data); print(name); //判断对象类型
            return data
        }else{
            print("readPlist Failed: [FileNotFoundError] Please check file path: ", filePath)
            return nil
        }
        
        /* 异常处理
         /// 1. try?        //如果解析成功，则返回值，否则返回nil
         /// 2. try!        //如果解析成功，则返回值，否则直接崩溃
         /// 3. try catch   //处理异常，能接收错误，并输出错误
         } // */
    }
    
    /// NSDictionary写入plist文件(覆盖写入) -- Cyril
    /// * filePath: plist文件路径
    /// * data: 待写入数据
    func writePlist_NSDictionary(filePath: String, data: NSDictionary) -> Bool{
        createFileAuto(filePath: filePath)
        return data.write(toFile: filePath, atomically: true)
    }
    /// NSArray写入plist文件(覆盖写入) -- Cyril
    /// * filePath: plist文件路径
    /// * data: 待写入数据
    func writePlist_NSArray(filePath: String, data: NSArray) -> Bool{
        createFileAuto(filePath: filePath)
        //在使用writeToFile的时候，data对象类型必须是NSString，NSData，NSDate，NSNumber,NSArray,NSDictionary
        return data.write(toFile: filePath, atomically: true)
    }
    
    ///把字符串追加写进文件,文件保存在沙盒中Documents路径中
    func writeStrToFile(receivedString: String, filePath: String){
        let str = receivedString + "\n"
        let wr = NSMutableData()
        wr.append(str.data(using:String.Encoding(rawValue: String.Encoding.utf8.rawValue))!)
        
        if !createFileAuto(filePath: filePath){
            print("writeStrToFile Failed: [CreateFileError] Please check file path access: ", filePath)
            //  return false
        }
        
        let url: URL = NSURL(fileURLWithPath: filePath) as URL
        let writeHandler = try? FileHandle(forWritingTo: url)
        if writeHandler != nil {
            writeHandler!.seekToEndOfFile()
            writeHandler?.write(wr as Data)
            //   return true
        }else{
            print("WriteFileFailed : ", url)
        }
        //  return false
    }
    
    //判断文件是否存在 --- Cyril
    func dirExists(path:String)->Bool{
        return FileManager.default.fileExists(atPath: path)
    }
    
    /// 如果文件不存在将自动创建文件
    /// * fileParentDir: 文件父目录路径
    /// * fileName: 文件名
    /// * return: true:文件创建成功或已存在，false:文件不存在且创建失败
    func createFileAuto(filePath:String) -> Bool{
        /// 去掉文件名的文件路径
        let dir = getFileDirByPath(filePath: filePath)
        if !dirExists(path: filePath){
            
            let  fileManager = FileManager.default
            do{
                // 创建文件夹   1，路径 2 是否补全中间的路径 3 属性
                try fileManager.createDirectory(atPath: dir, withIntermediateDirectories: true, attributes: nil)
                //创建文件    1 路径  2 内容 3 属性
                try fileManager.createFile(atPath: filePath, contents: nil, attributes: nil)
                if !dirExists(path: filePath){
                    return false
                }
            } catch{
                return false
            }
        }
        return true
    }
    
    /** Swift 调用任意参数个数Shell脚本, 一般不直接调用此函数
     *  arg0 : scriptPath // 第一个参数是脚本路径 （必须是完整路径）
     *  arg1 : ${1}     // 第二个参数是脚本参数1
     *  ...
     *  argn : ${n}    // 第N个参数是脚本参数N
     *  返回值： shell 命令执行返回值
     */
    func execShellCMD(_ members: String...) -> String{
        // 脚本文件路径
        var scriptPath:String=String("")
        var args:Array = [String]()
        scriptPath = members[0]
        // 尝试在系统中获取CMD真实路径
        /* if !scriptPath.contains("/") {  //如果命令不包含执行路径，则尝试查找该命令是否存在于系统路径
         var res = execShell("/usr/bin/which", scriptPath)  //将命令替换为带路径的string值
         if res == ""{
         print(scriptPath, " 命令不存在。" )
         return ""
         }
         scriptPath = res as String
         } */
        //print("scriptPath -> ", scriptPath)
        
        if members.endIndex >= 1{
            for index in 1...(members.endIndex-1){
                args.append(members[index])
            }
        } //如果<1则说明传入的member不包含命令执行参数
        //print("args ->", args)
        
        let task = Process()
        task.launchPath = scriptPath
        task.arguments = args
        let pipe = Pipe()
        task.standardOutput = pipe
        task.launch()
        let data = pipe.fileHandleForReading.readDataToEndOfFile()
        let output: String = String(data: data, encoding: String.Encoding.utf8)!
        
        return output
    }
    
    // curl "http://172.25.3.167/fatpma" -d "c=QUERY_RECORD&sn=C39XH00RL892&p=mpn&p=region_code"
    func getValueFromSFC(sfc_url: String, sn: String) -> Array<Substring>{
        //let res = execShell("/usr/bin/curl","http://172.25.3.167/fatpma","-d","c=QUERY_RECORD&sn=C39XH00RL892&p=mpn&p=region_code")
        let res = execShellCMD("/usr/bin/curl", sfc_url, "-d", "c=QUERY_RECORD&sn=\(sn)&p=mpn&p=region_code").split(separator: "\n")
        /**
         0 SFC_OK
         mpn=993-34313
         region_code=LL/A
         */
        //print(type(of: res)); print("res=",res);
        return res
    }
    
    /// 切割完整文件路径，获取文件目录 --- Cyril
    /// * filePath: 完整文件路径
    /// * return: 获取文件目录路径
    func getFileDirByPath(filePath:String) -> String {
        let ss = filePath.components(separatedBy: "/")
        // print("ss= ", ss)
        var dir:String = "" // dir 为去掉文件名的文件路径
        for index in 0...ss.endIndex-2{
            dir = dir + "/\(ss[index])"
        }
        
        return dir
    }
    
    /// 打包Log文件夹    -- Cyril
    /// * return true: 文件打包成功
    /// * return false: 文件打包失败
    func packageLogs(logPath: String, logName: String) -> Bool{
        if dirExists(path: logPath){
            /// 不包含文件名的文件父目录路径
            let logDir = getFileDirByPath(filePath: logPath)
            let sh_cmd = execShellCMD("/usr/bin/zip", "-r", "\(logDir)/\(logName)", "\(logDir)")
            //print("sh_cmd ", sh_cmd)
            if sh_cmd.contains("adding:"){
                return true
            }
        }else{
            print("Logs File Folder is not exists: \(logPath)")
        }
        return false
    }
    
    /// 删除指定文件/文件夹（慎用此函数）
    /// * path: 要删除的文件路径
    /// * return true: 删除成功
    /// * return false: 删除失败
    func deleteFileFid(path: String) -> Bool{
        if dirExists(path: path){
            let sh_cmd = execShellCMD("/bin/rm", "-rf", "\(path)")
            if sh_cmd != ""{
                return false
            }
        }
        return true
    }
    
    /// 获取格式化 diags命令返回值结果 （字符串处理函数）
    /// * str: diags命令执行结果返回的原始string
    /// * return: diags命令执行结果
    func getFormatDiagsResultStr(str: String) -> String{
        let str_tmp:String = str.trimmingCharacters(in: .whitespacesAndNewlines)
        let str_tmp2: Array = str_tmp.split(separator: "\n")
        if (str_tmp2.endIndex > 2){
            return String(str_tmp2[1]).trimmingCharacters(in: .whitespacesAndNewlines)
        }else{
            return ""
        }
    }
    
    func myThread(result: Int, dwi: DispatchWorkItem){
        
        // 开一条全局队列异步执行任务
        DispatchQueue.global().async {
            
            /*  Group的用法
             *  1. notify(依赖任务), 必须和 enter/leave在同一队列才会执行
             *  2. wait(任务等待)
             *  3. enter/leave 手动管理group计数,enter和leave必须配对, 可以不需要wait()
             */
            let group = DispatchGroup()
            var subTask: [DispatchQueue] = [DispatchQueue]()
            
            /* // 主线程
             DispatchQueue.main.async {  //通知ui刷新
             print("Main 刷新 UI: Begin")
             group.wait()
             Thread.sleep(forTimeInterval: 1)   //停止1秒
             print("Main 刷新 UI: End")
             }   // */
            
            //初始化8个子线程
            for i in 0...7{
                subTask.append(DispatchQueue(label: "subTask\(i)", attributes: .concurrent))
            }
            //启动8个子线程任务
            for item in subTask{
                group.enter()   //把该任务添加到组队列中执行, enter和leave必须配对
                item.async(group: group) {
                    Thread.sleep(forTimeInterval: 1)   //停止1秒
                    print("\(Date().description) subTask.label = \(item.label)")
                    group.leave()   //执行完之后从组队列中移除
                }
                group.notify(queue: item){ // 对应的子线程完成后，扫尾任务
                    DispatchQueue.main.async(group: group, execute: dwi)     // 通知主线程刷新UI
                    print("\(item.label) finished，do something more")
                    // *** 此处可添加 对应的子线程完成后的扫尾任务
                    sleep(10)
                }
            }
            print("Waitting all test done.")
            group.wait()    // 等待所有子线程完成
            print("All test done.")
        }
    }
    // 字符串数组转字符串（给python使用，python需将字符串转回字符串数组）
    func arr_to_str(arr: [String]) -> String{
        var res = ""
        for i in 0...arr.count-2{
            res = "\(res)\(arr[i]),"
        }
        res = "\(res)\(arr[arr.count-1])"
        return res
    }
    func arr_to_str2(arr: [String]) -> String{
        var res = "\""
        for i in 0...arr.count-2{
            res = "\(res)\(arr[i]),"
        }
        res = "\(res)\(arr[arr.count-1])\""
        return res
    }
    
    func str_to_arr(str: String) -> [String]{
        
        
        return []
    }

    
}




