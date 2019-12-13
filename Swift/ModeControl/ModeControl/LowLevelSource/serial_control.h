#ifndef __SERIAL_CONTROL__
#define __SERIAL_CONTROL__

#define DEFAULT_BAUDRATE 115200
#define DEFAULT_DATABITS 8
#define DEFAULT_STOPBITS 1
#define DEFAULT_PARITY 'N'
#define SIZE 1024
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
#include     "format_log.h"

extern int init_serial( char * dev );
extern int init_serial_with_baudrate( char* dev, int baud);
extern int read_serial( int fd , char * rbuff );
extern int write_serial( int fd , const char * strcmd, int timeout );
extern void close_serial( int fd );
extern int read_serial_for_mode_judge( int fd, char * buff, char * filename );


#endif

