/*
#include     <stdio.h>      
#include     <stdlib.h>     
#include     <unistd.h>     
#include     <sys/types.h>   
#include     <sys/stat.h>    
#include   	 <sys/uio.h>
#include     <string.h> 
#include     <fcntl.h>      
#include     <termios.h>    
#include     <errno.h>      
*/
#include 	 "serial_control.h"

//static char rbuff[SIZE];
//static char wbuff[SIZE];

static int speed_arr[] = { B230400, B115200, B57600, B38400, B19200, B9600, B4800, B2400, B1200, B300, B38400, B19200, B9600, B4800, B2400, B1200, B300, }; 
static int name_arr[] = { 230400, 115200, 57600, 38400, 19200, 9600, 4800, 2400, 1200, 300, 38400, 19200, 9600, 4800, 2400, 1200, 300, }; 
//static struct termios options;  

extern int init_serial( char * dev );
extern int init_serial_with_baudrate( char* dev, int baud );
extern int read_serial( int fd , char * rbuff );
extern int write_serial( int fd , const char * strcmd, int timeout );
extern void close_serial( int fd );
extern int read_serial_for_mode_judge( int fd, char * buff, char * filename );

/*********************************************************************/ 
static int open_dev( char *Dev ) 
{ 
		int fd = open( Dev, O_RDWR |  O_NOCTTY );  //| O_NOCTTY , open a terminal device without changing your controlling terminal, O_NONBLOCK      
		if ( fd == -1 )    
		{
            puts(Dev);
				printf("Can't Open %s Port*\n", Dev);
				return -1;       
		}    
		//fcntl( fd, F_SETFL, 0 );
		return fd; 
} 



/** 
 *@brief  设置串口通信速率 
 *@param  fd     类型 int  打开串口的文件句柄 
 *@param  speed  类型 int  串口速度 
 *@return  success:0   fail: 非0
 */ 
static int set_speed( int fd, int speed ) 
{ 
		int i, status;  
		struct termios Opt; 
		tcgetattr( fd, &Opt );  
		for ( i= 0; i < sizeof(speed_arr) / sizeof(int); i++ )
		{  
				//printf( "speed=%d == %d\n", speed, name_arr[i] );
				if ( speed == name_arr[i] ) 
				{      
						tcflush( fd, TCIOFLUSH );     // TCIOFLUSH: Flush both data received but not read and data written but not transmitted 
						cfsetispeed( &Opt, speed_arr[i] );   
						cfsetospeed( &Opt, speed_arr[i] );    
						status = tcsetattr( fd, TCSANOW, &Opt );  //TCSANOW: The change occurs immediately. 
						if ( status != 0 ) {         
								perror( "tcsetattr fd when set speed\n" );   
								return -1;      
						}     
						tcflush( fd, TCIOFLUSH );    
						return 0;
				}   
		} 
		fprintf( stderr, "This speed[%d] not be support!\n", speed );
		return -1;
} 

/**
  set the time of read,  
 *@param  time   1/10 s
 **/
static int set_timeout( int fd, int time )
{

		struct termios timeout_time;  
		if ( tcgetattr( fd, &timeout_time )  !=  0 ) 
		{  
				perror( "Set timeout time error!\n" );      
				return -1;   
		}

		timeout_time.c_cc[VTIME] = time; /* 设置超时 1/10 seconds*/    
		timeout_time.c_cc[VMIN] = 0; /* the least receive byte */ 

		if ( tcsetattr( fd, TCSANOW, &timeout_time) != 0 )    
		{  
				perror( "Set timeout time error!\n" );      
				return -1;   
		}  

		return 0;   
}

/** 
 *brief   设置串口数据位，停止位和效验位
 *param  fd     类型  int  打开的串口文件句柄
 *param  databits 类型  int 数据位   取值 为 7 或者8
 *param  stopbits 类型  int 停止位   取值为 1 或者2
 *param  parity  类型  int  效验类型 取值为N,E,O,,S
 *return 
 */ 
static int set_parity( int fd, int databits, int stopbits, int parity ) 
{  
		struct termios options;  
		options.c_lflag  &= ~(ICANON | ECHOE | ISIG);  /*Input*/ 
		options.c_oflag  &= ~OPOST;   /*Output*/ 
		if ( tcgetattr( fd, &options )  !=  0 ) 
		{  
				perror( "Setup Serial parity error!\n" );      
				return -1;   
		} 
		options.c_cflag &= ~CSIZE;  

		switch ( databits ) /*设置数据位数*/ 
		{    
				case 7:      
						options.c_cflag |= CS7;  
						break; 
				case 8:      
						options.c_cflag |= CS8; 
						break;    
				default:     
						fprintf( stderr, "Unsupported data size[%d]\n", databits ); 
						return -1;   
		} 
		switch ( parity )  
		{    
				case 'n': 
				case 'N':     
						options.c_cflag &= ~PARENB;   /* Clear parity enable */ 
						options.c_iflag &= ~INPCK;     /* Enable parity checking */  
						break;   
				case 'o':    
				case 'O':      
						options.c_cflag |= (PARODD | PARENB); /* 设置为奇效验*/   
						options.c_iflag |= INPCK;             /* Disnable parity checking */  
						break;   
				case 'e':   
				case 'E':    
						options.c_cflag |= PARENB;     /* Enable parity */     
						options.c_cflag &= ~PARODD;   /* 转换为偶效验*/      
						options.c_iflag |= INPCK;       /* Disnable parity checking */ 
						break; 
				case 'S':  
				case 's':  /*as no parity*/    
						options.c_cflag &= ~PARENB; 
						options.c_cflag &= ~CSTOPB;
						break ;   
				default:    
						fprintf( stderr, "Unsupported parity[%d]\n", parity );     
						return -1;   
		}   
		/* 设置停止位*/   
		switch ( stopbits ) 
		{    
				case 1:     
						options.c_cflag &= ~CSTOPB;   
						break;   
				case 2:     
						options.c_cflag |= CSTOPB;   
						break; 
				default:  
						fprintf( stderr, "Unsupported stop bits[%d]\n", stopbits );   
						return -1;  
		}  
		/* Set input parity option */  
		if ( parity != 'n' )    
				options.c_iflag |= INPCK;  

		tcflush( fd, TCIFLUSH ); 
		set_timeout( fd, 1 );

		return 0;   
} 

//int read_serial( int fd , char * buff ) {
//
//        size_t iRead=0;
//        memset( rbuff, 0, sizeof(rbuff) );
//        if ( (iRead = read( fd, rbuff, (int)sizeof(rbuff) )) > 0 )
//        {
//                //printf("\nRead***%d****\n", iRead );
//                strcpy( buff, rbuff );
//                printf("%s", buff);
//                return (int)iRead;
//        }
//        else if ( iRead == -1 )
//        {
//                perror( "read error!" );
//                return -1;
//        }
//        else
//        {
//                //printf("\nRead***%d****\n", iRead );
//                return 0;
//        }
//}

int read_serial( int fd, char * buff ) {
        
        size_t iRead = 0;
        size_t num = 0;
        char rbuff[SIZE];
        memset( &rbuff[0], 0, sizeof(rbuff) );
        do {
            if ( (num = read( fd, rbuff, (int)sizeof(rbuff)-1 )) > 0 )
            {
                //printf("\nRead***%d****\n", iRead );
                //printf("%s", rbuff);
                strcat( buff, rbuff );
                //printf("%s", rbuff);
                iRead += num;
                //printf("\nRead***%d****\n", iRead );
               
                //return (int)iRead;
            }
            else if ( num == -1 )
            {
                perror( "read error!" );
                return -1;
            }

                //printf("\nRead***%d****\n", iRead );
            
        }while (num > 0);
        return (int)iRead;
}

int read_serial_to_file( int fd, char * buff, char * filename ) {
    
    size_t iRead = 0;
    size_t num = 0;
    char rbuff[SIZE];
    memset( &rbuff[0], 0, sizeof(rbuff) );
    FILE * file_f = creat_log_file(filename);
    do {
        if ( (num = read( fd, rbuff, (int)sizeof(rbuff)-1 )) > 0 )
        {
            //printf("\nRead***%d****\n", iRead );
            //printf("%s", rbuff);
            strcat( buff, rbuff );
            write_log(file_f, rbuff);
            //printf("%s", rbuff);
            iRead += num;
            //printf("\nRead***%d****\n", iRead );
            
            //return (int)iRead;
        }
        else if ( num == -1 )
        {
            perror( "read error!" );
            close_log(file_f);
            return -1;
        }
        
        //printf("\nRead***%d****\n", iRead );
        
    }while (num > 0);
    close_log(file_f);
    return (int)iRead;
}

int read_serial_for_mode_judge( int fd, char * buff, char * filename ) {
    
    size_t iRead = 0;
    size_t num = 0;
    //char rbuff[SIZE];
    FILE * file_f;
    if (strcmp(filename, "") != 0){
        file_f = creat_log_file(filename);
    }else{
        file_f = creat_log_file("/dev/null");
    }
    //memset( &rbuff[0], 0, sizeof(rbuff) );
    do {
        //printf("in read_serial_for_mode_judge\n");
        num = read( fd, buff, 1000 );
        //printf("\nRead***%lu****\n", num );
        if ( (num) > 0 )
        {
            
            //printf("%s", buff);
            //strncpy( buff, rbuff, strlen(rbuff) );
            write_log(file_f, buff);
            //printf("%s", rbuff);
            iRead += num;
            //buff += num;
            //printf("\nRead***%d****\n", iRead );
            fflush(stdout);
            //return (int)iRead;
        }
        else if ( num == -1 )
        {
            perror( "read error!" );
            close_log(file_f);
            return -1;
        }
        else{
            strcat(buff, "\0");
            buff += 1;
        }
        
        //printf("\nRead***%d****\n", iRead );
        
    }while (num > 0);
    close_log(file_f);
    return (int)iRead;
    /*
     char response[1024];
     memset(response, '\0', sizeof response);
     
     do {
     n = read( USB, &buf, 1 );
     sprintf( &response[spot], "%c", buf );
     spot += n;
     } while( buf != '\r' && n > 0);
     
     if (n < 0) {
     std::cout << "Error reading: " << strerror(errno) << std::endl;
     }
     else if (n == 0) {
     std::cout << "Read nothing!" << std::endl;
     }
     else {
     std::cout << "Response: " << response << std::endl;
     }
     */
}


//int read_serial_for_mode_judge( int fd, char * buff, char * filename ) {
//
//    size_t iRead = 0;
//    size_t num = 0;
//    char rbuff[SIZE];
//    FILE * file_f;
//    if (strcmp(filename, "") != 0){
//        file_f = creat_log_file(filename);
//    }else{
//        file_f = creat_log_file("/dev/null");
//    }
//    memset( &rbuff[0], 0, sizeof(rbuff) );
//    do {
//        //printf("in read_serial_for_mode_judge\n");
//        num = read( fd, rbuff, (int)sizeof(rbuff)-1 );
//        //printf("\nRead***%lu****\n", num );
//        if ( (num) > 0 )
//        {
//
//            //printf("%s", rbuff);
//            strncpy( buff, rbuff, strlen(rbuff) );
//            write_log(file_f, rbuff);
//            //printf("%s", rbuff);
//            iRead += num;
//            //printf("\nRead***%d****\n", iRead );
//            fflush(stdout);
//            //return (int)iRead;
//        }
//        else if ( num == -1 )
//        {
//            perror( "read error!" );
//            close_log(file_f);
//            return -1;
//        }
//        else{
//            strcat(buff, "\0");
//        }
//
//        //printf("\nRead***%d****\n", iRead );
//
//    }while (num > 0);
//    close_log(file_f);
//    return (int)iRead;
//    /*
//     char response[1024];
//     memset(response, '\0', sizeof response);
//
//     do {
//     n = read( USB, &buf, 1 );
//     sprintf( &response[spot], "%c", buf );
//     spot += n;
//     } while( buf != '\r' && n > 0);
//
//     if (n < 0) {
//     std::cout << "Error reading: " << strerror(errno) << std::endl;
//     }
//     else if (n == 0) {
//     std::cout << "Read nothing!" << std::endl;
//     }
//     else {
//     std::cout << "Response: " << response << std::endl;
//     }
//     */
//}

int readToFile( int fd, char * buff ) {
    
    size_t iRead = 0;
    size_t num = 0;
    char rbuff[SIZE];
    memset( &rbuff[0], 0, sizeof(rbuff) );
    do {
        if ( (num = read( fd, rbuff, (int)sizeof(rbuff)-1 )) > 0 )
        {
            //printf("\nRead***%d****\n", iRead );
            //printf("%s", rbuff);
            strcpy( buff, rbuff );
            //printf("%s", rbuff);
            iRead += num;
            //printf("\nRead***%d****\n", iRead );
            
            //return (int)iRead;
        }
        else if ( num == -1 )
        {
            perror( "read error!" );
            return -1;
        }
        
        //printf("\nRead***%d****\n", iRead );
        
    }while (num > 0);
    return (int)iRead;
}

int write_serial( int fd , const char * strcmd, int timeout )
{
    size_t nread=0;
    int iwrite=0;
    char wbuff[SIZE];
		memset( wbuff, 0, sizeof(wbuff) );
		if ( (iwrite=(int)strlen(strcmd))  >= 0 ) 
		{ 

						strcpy( wbuff, strcmd );
						nread = write( fd, wbuff, strlen(wbuff) ); 

						if ( nread == -1 ) 
						{
								perror( "Wirte buff error.\n" ); 
								return -1; 
						} 
						sleep( timeout );
		} 
		return (int)nread;

}
//#define DEFAULT_BAUDRATE 230400
int init_serial_with_baudrate( char * dev, int baud )
{
    int fd;
    fd = open_dev( dev );
    
    if( fd == -1 )
    {
        printf( "Open serial %s error!\n", dev );
        return -1;
    }
    
    if( set_speed( fd, baud ) )
    {
        close( fd );
        perror( "Set Baud Rate Error\n" );
        return -1;
    }
    
    if ( set_parity( fd, DEFAULT_DATABITS, DEFAULT_STOPBITS, DEFAULT_PARITY ) )
    {
        close( fd );
        perror( "Set Parity Error\n" );
        return -1;
    }
    
    printf("init serial:%s\n", dev);
    return fd;
}

int init_serial( char * dev )
{		
		int fd;
		fd = open_dev( dev );
		if( fd == -1 )
		{ 	
				printf( "Open serial %s error!\n", dev );
				return -1;
		}

		if( set_speed( fd, DEFAULT_BAUDRATE ) )	
		{	
				close( fd );
				perror( "Set Baud Rate Error\n" ); 
				return -1;  
		}

		if ( set_parity( fd, DEFAULT_DATABITS, DEFAULT_STOPBITS, DEFAULT_PARITY ) )   
		{ 
				close( fd );
				perror( "Set Parity Error\n" ); 
				return -1; 
		} 
		return fd;
}

void close_serial( int fd )
{
    printf("!!!Close serial %d\n", fd);
    close( fd );
}

