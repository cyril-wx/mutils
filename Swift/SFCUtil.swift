//
//  SFCUtil.swift
//  Anole
//
//  Created by admin on 7/28/18.
//  Copyright © 2018 gdadmin. All rights reserved.
//

import Foundation

//goto:把url维护成一个配置文件
//getValueFromSFC(url: "http://172.25.3.167/mlbd33", sn: c39asedasdf, data: "p=mpn")
func getValueFromSFC(url: String, sn: String, data: String) -> String {
    
    var argcVal = [String]()
    argcVal.append("-S")
    argcVal.append("-s")
    argcVal.append(url)
    argcVal.append("-d")
    let queryData = "sn=\(sn)&c=QUERY_RECORD&"
    argcVal.append("\(queryData)\(data)")
    //print(argcVal)
    let result_string = DeviceDetect().runCommand(launchPath: "/usr/bin/curl", arguments: argcVal, retry: 3).1
    if !result_string.isEmpty{
        
        //print("rev=\(result_string)")
        if result_string.contains("="){
            var index = result_string.index(of: "=")
            index = result_string.index(index!, offsetBy: 1)
            let temp = result_string.suffix(from: index!)
            return String(temp)
//            if result_string.contains("mpn"){
//                let mpn = temp
//                //print("my mpn=\(sbuild)")
//                return mpn
//            }
        }
        
    }
    return "null"
}
