//
//  MyScanf.c
//  ModeControl
//
//  Created by coreos on 2/23/19.
//  Copyright © 2019 coreos. All rights reserved.
//

// MyScanf.c

#include "MyScanf.h"
#include<string.h>
#include<stdlib.h>

#define READ_BUF_SIZE 1024

char *MyScanf(void) {
    // 从命令行读取用户输入
    char * str;
    str=(char*)malloc(100*sizeof(char));
    scanf("%s",&str);
    printf("Input: %s", str);
    return str;
}

char *readbuffer(void)
{
    char *buftemp;
    int size= 20,buf_totalcount,every_count; //每次从键盘读取的长度，最后的总长度，每次实际读取的字符数
    buftemp = (char*)malloc(sizeof(char)*size);//每次分配20个字符大小缓冲区
    printf("input：\n");
    buftemp = fgets(buftemp,size,stdin);//从键盘读取字符
    every_count = strlen(buftemp); //每次实际接收的数据长度
    buf_totalcount = every_count;//总长度变化
//    *buffer = (char*)malloc(sizeof(char)*(buf_totalcount+1));//为了最后保存结束符，多分配一位
//    strcpy(*buffer,buftemp);
    while(buftemp[every_count-1]!='\n')//输入回车键即为输入结束
    {
        buftemp =fgets(buftemp,size,stdin);//从键盘读取字符
        every_count = strlen(buftemp); //每次实际接收的数据长度
        buf_totalcount +=every_count;//总长度变化
 //       *buffer = (char*)realloc(*buffer,sizeof(char)*(buf_totalcount+1));//重新分配缓冲区
 //       strcpy((*buffer)+buf_totalcount-every_count,buftemp); //拷贝本次结束的字符串
    }
    buftemp[buf_totalcount-1]='\0'; //填充结束符
    printf("output: %s", buftemp);
//    free(buftemp);//释放
//    buffer[buf_totalcount-1]='\0'; //填充结束符
//    printf("c: %s", &buffer);
    //return buf_totalcount-1;//返回实际字符串的长度
    return buftemp;
}
