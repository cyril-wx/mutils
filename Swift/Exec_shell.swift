import Foundation

/// 类的方式开启shell 调用
/// - 不执行等待
/// - eg: status = Execution.execute(path: "/bin/ls")
class Exe_Shell{
	/// 等待执行完毕
	/// - parameter launchPath: 必须为完整路径
	/// - parameter arguments (list): 参数列表
	/// - Returns: (状态码，命令执行标准输出)
	class func run_shell(launchPath:String,arguments:[String]? = nil) -> (Int, String) {
		let task = Process();
		task.launchPath = launchPath
		var environment = ProcessInfo.processInfo.environment
		environment["PATH"] = "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
		task.environment = environment
		if arguments != nil {
			task.arguments = arguments!
		}
		
		let pipe = Pipe()
		task.standardOutput = pipe
		task.launch()
		let data = pipe.fileHandleForReading.readDataToEndOfFile()
		let output: String = String(data: data, encoding: String.Encoding.utf8)!
		task.waitUntilExit()
		pipe.fileHandleForReading.closeFile()      
		
		print("DEBUG 24: run_shell finish.")
		return (Int(task.terminationStatus),output)
	}
	/// 不等待执行完毕, 无返回值，调用时需使用try-catch
	/// - parameter launchPath: 必须为完整路径
	/// - parameter arguments (list): 参数列表
	class func run_shell2(launchPath: String, arguments:[String]? = nil) {
		
		var environment = ProcessInfo.processInfo.environment
		environment["PATH"] = "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
		
		let task = Process()
		task.environment = environment
		task.launchPath = launchPath
		if arguments != nil {
			task.arguments = arguments!
		}
		let pipe = Pipe()
		task.standardOutput = pipe
		task.launch()
		
		//let data = pipe.fileHandleForReading.readDataToEndOfFile()
		pipe.fileHandleForReading.closeFile()
		
		//let output: String = String(data: data, encoding: String.Encoding.utf8)!
		print("DEBUG 23: run_shell2 finish.")
		
	}
	/// 命令后台运行(非线程方式)，超时自动销毁退出 
	/// - parameter launchPath: 必须为完整路径
	/// - parameter arguments (list): 参数列表
	/// - Returns: (状态码，命令执行标准输出)
	class func run_shell3(launchPath: String, arguments:[String]? = nil, timeout:Int = 2) {
		var args:[String]
		if arguments == nil {
			args = [launchPath]
		}else {
			args = arguments!
			args.insert(launchPath, at: 0)
		}
		
		run_shell2(launchPath: Rep_runShell, arguments: args)
	}
}