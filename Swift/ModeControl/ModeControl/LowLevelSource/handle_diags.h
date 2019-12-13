#ifndef __HANDLE_DIAGS__
#define __HANDLE_DIAGS__
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct response_info 
{
	char test_item[30]; 
	char  test_value[256]; 
	int  test_result;   //0: fail;  1:pass
};


extern char * diags_cmd_rwt( int device_fd, const char * str_cmd, int timeout );
extern int diags_cmd_wt( int device_fd, const char * str_cmd, int timeout );
extern int is_alive( int fd );

extern struct response_info * parse_diags_result( const char * diags_return, const char * test_item_keyword, char * search_keywords );

extern void output_parse_result( struct response_info * ri_m_ptr );

#endif
