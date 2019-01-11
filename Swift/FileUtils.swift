class FileUtils{

    //缓存路径(这里用的沙盒cache文件，非document，可根据需求更改)
    func getCachePath()->String{
        var cacheDir = NSSearchPathForDirectoriesInDomains(FileManager.SearchPathDirectory.cachesDirectory, .userDomainMask, true).first!
        if(!cacheDir.hasSuffix("/")){
            cacheDir += "/"
        }
        cacheDir += CACHEPATH + "/"
        return cacheDir
    }
    
    //获得NSFileManager
    func getFileManager()->FileManager{
        return FileManager.default
    }
    
    //判断文件夹是否存在
    func dirExists(dir:String)->Bool{
        return getFileManager().fileExists(atPath: dir)
    }
    
    //判断文件是否存在
    func fileExists(path:String)->Bool{
        return dirExists(dir: path)
    }
    
    //判断是否存在,存在则返回文件路径，不存在则返回nil
    func fileExistsWithFileName(fileName:String)->String?{
        let dir = getCachePath()
        if(!dirExists(dir: dir)){
            return nil
        }
        let filePath = dir + fileName
        
        return fileExists(path: filePath) ? filePath : nil
    }
    
    
    //创建文件夹
    func createDir(dir:String)->Bool{
        let fileManager = getFileManager()
        do{
            try fileManager.createDirectory(at: NSURL(fileURLWithPath: dir, isDirectory: true) as URL, withIntermediateDirectories: true, attributes: nil)
        }catch{
            return false
        }
        return true
    }
    
    /// 根据文件名创建路径
    ///
    /// - Parameter fileName: <#fileName description#>
    /// - Returns: <#return value description#>
    func createFilePath(fileName:String)->String?{
        let dir = getCachePath()
        if(!dirExists(dir: dir) && !createDir(dir: dir)){
            return nil
        }
        let filePath = dir + fileName
        if(fileExists(path: filePath)){
            do{
                try getFileManager().removeItem(atPath: filePath)
            }catch{
                return nil
            }
            
        }
        return filePath
    }
    
    
    /// 删除文件 - 根据文件名称
    ///
    /// - Parameter fileName: <#fileName description#>
    /// - Returns: <#return value description#>
    func deleteFileWithName(fileName:String)->Bool{
        guard let filePath = fileExistsWithFileName(fileName: fileName) else{
            return true
        }
        return deleteFile(path: filePath)
    }
    
    
    /// 删除文件 - 根据文件路径
    ///
    /// - Parameter path: <#path description#>
    /// - Returns: <#return value description#>
    func deleteFile(path:String)->Bool{
        if(!fileExists(path: path)){
            return true
        }
        let fileManager = getFileManager()
        do{
            try fileManager.removeItem(atPath: path)
        }catch{
            return false
        }
        
        return true
    }
    
    /**
     清除所有的缓存
     
     - returns: Bool
     */
    func deleteAll()->Bool{
        let dir = getCachePath()
        
        if !dirExists(dir: dir){
            return true
        }
        let manager = getFileManager()
        do{
            try manager.removeItem(atPath: dir)
        }catch{
            return false
        }
        return true
    }
    
    //读取文件 -（根据路径）
    func readFileFromCache(path:String)->NSData?{
        var result:NSData?
        do{
            result = try NSData(contentsOfFile: path, options: NSData.ReadingOptions.uncached)
        }catch{
            return nil
        }
        return result
    }
    
    //读取文件 -（根据文件名）
    func readFile(fileName:String)->NSData?{
        
        guard let filePath = fileExistsWithFileName(fileName: fileName) else{
            return nil
        }
        
        return readFileFromCache(path: filePath)
    }
    

    
    /// 写文件
    ///
    /// - Parameters:
    ///   - fileName: 文件名称
    ///   - data: 数据data
    /// - Returns: <#return value description#>
    func writeFile(fileName:String,data:NSData)->Bool{
        
        guard let filePath = createFilePath(fileName: fileName) else{
            return false
        }
        
        return data.write(toFile: filePath, atomically: true)
    }
    
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
    
    ///把字符串追加写进文件
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
    
}
