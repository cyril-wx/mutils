//
//  Constants.swift
//  Anole
//
//  Created by coreos on 1/14/19.
//  Copyright © 2019 gdadmin. All rights reserved.
//  Constants 类是用于定义所有类/方法中需要使用到的常量

import Foundation


/// 运行模式
public enum RUN_WHERE: String {
    case iOS = "iOS"
    case Diags = "Diags"
    case iBoot = "iBoot"
    case Host = "Host"
}
/// 连接方式
public enum CONN_TYPE: String{
    case KANZI_CABLE = "KANZI_CABLE"
    case DCSD_CABLE = "DCSD_CABLE"
    case TTFixture = "TTFixture"
}

/// Unit/MLB 设备模式
public enum MODE:String{
    case iOS = "iOS"
    case iOS_Unlogin = "iOS_Unlogin"
    case Diags = "diags"
    case iBoot = "iBoot"
    case Unknown = "Unknown"
}

/// 串口读取波特率
/// * 115200 是针对于Cable连接
/// * 230400 是针对治具连接
public enum BAUD_RATE: Int32{
    case TTFixture = 230400
    case Cable = 115200
}


