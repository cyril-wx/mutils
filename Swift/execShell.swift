//: Playground - noun: a place where people can play

import Cocoa
import UIKit

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
