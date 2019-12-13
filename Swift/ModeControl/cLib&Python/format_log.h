#ifndef __FORMAT_LOG__
#define __FORMAT_LOG__
#include <stdio.h>
#include <time.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <dirent.h>
#include <libgen.h>
#include <string.h>

#define DIR_NAME_MAX_NUM 256

int mk_dir( char * dirname );
int mk_dir_with_date( char * path, char * dirname, char * return_dirname, size_t return_dirname_len );
FILE * creat_log_file( const char * filename );
int write_log( FILE * fd_w, char * content );
int close_log( FILE * fd );

#endif
