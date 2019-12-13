#include "format_log.h"

int mk_dir( char * dir_name )
{

		//char directer_name[512];
		//strncpy( directer_name, dirname( dir_name ), sizeof(directer_name) );
		//puts( directer_name );
		if(	access( dir_name, F_OK ) )
		{
				//perror( "access dir name" );
				if (mkdir( dir_name, 0755 ))
				{
						perror( "creat dir" );
						return -1;
				}
		}

		return 0;
}

int mk_dir_with_date( char* path, char * tempdir, char * return_dirname, size_t return_dirname_len )
{
		char local_dir_name[DIR_NAME_MAX_NUM];
		time_t now = time(NULL);
		struct tm* p = localtime(&now);
		char time_buf[20];
		strftime( time_buf, sizeof(time_buf), "%F", p );
		snprintf( local_dir_name, sizeof(local_dir_name), "%s/%s_%s", path, time_buf, tempdir );
		if ( NULL == strncpy( return_dirname, local_dir_name, return_dirname_len ) )
			perror( "mk_dir_with_date" );

		mk_dir( local_dir_name );
		return 0;
}


FILE * creat_log_file( const char * filename )
{
		FILE * fd = fopen( filename, "a+" );
		if ( fd == NULL )
		{
				perror( "open log file failed!" );
				return fd;
		}
		return fd;
}

int write_log( FILE * fd_w, char * content )
{
		time_t now = time(NULL);
		struct tm* p = localtime(&now);
		char time_buf[25];
		strftime( time_buf, sizeof(time_buf), "%F:%T", p );
		int ret=0;

		//fd_w = creat_log_file( filename );
		if ( !fd_w )
				perror( "write log failed!" );

		ret = fprintf( fd_w, "[%s]%s\n", time_buf, content );
		return ret;
}

int close_log( FILE * fd )
{
		return fclose( fd );
}



