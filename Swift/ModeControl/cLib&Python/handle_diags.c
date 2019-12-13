#include "serial_control.h"
#include "handle_diags.h"
/*
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
*/

#define READ_BUF_SIZE 1024


struct memory_struct 
{
	char * memory_content;
	size_t size;
};
//when yor
static struct memory_struct * diags_read( int child_fd )
{
		static struct memory_struct ms;
		//int fd, len=0,
        int nread=0;
		char temp[1024] = {0};
		ms.memory_content  = (char *)malloc( READ_BUF_SIZE );
		ms.size = 0;
        char * backup = ms.memory_content;
/*
	Need to change ret to malloc format, because return value may be more then 2048
*/
		memset( ms.memory_content, 0, READ_BUF_SIZE );
		memset( temp, 0, sizeof(temp) );
		while( 1 )
		{
				nread = read_serial( child_fd, temp );
				if ( nread == 0 )
						break;
				else if ( nread == -1 )
						perror( "read error\n" );

				if ( nread > 0 )
				{
					ms.size += nread;
					if ( ms.size >= 1000 )
					{
                        printf("######################%ld########################\n", ms.size);
                        backup = realloc( ms.memory_content, READ_BUF_SIZE + ms.size + 1);
                        if (backup != NULL) {
                            strcpy(backup, ms.memory_content);
                            strcat(backup, temp);
                            ms.memory_content = backup;
                            printf("######################%ld########################\n", ms.size);
                            printf("%s", temp);
                            continue;
                        }
                        
						if( backup == NULL)
						{	
							printf("not enough memory (realloc returned NULL)\n");
                            free(ms.memory_content);
						}
						//memset( ms.memory_content, 0, (READ_BUF_SIZE + READ_BUF_SIZE) );
					}
					strcat( ms.memory_content, temp );
					printf("%s", temp);
				}
				
		}
		//printf( "***in print_read function***%lu\n", ms.size );
		//puts( ms.memory_content );
		return &ms;
}

//For command reset or reboot, you need set enough timeout time.
extern char * diags_cmd_rwt( int device_fd, const char * str_cmd, int timeout )
{
			
		struct memory_struct * ms;
		unsigned long cmd_len = (strlen( str_cmd ) + 2);
		char test_cmd[cmd_len];
		snprintf( test_cmd, sizeof(test_cmd), "%s\r", str_cmd );
        write_serial( device_fd, test_cmd, timeout );
		ms = diags_read( device_fd );
		return ms->memory_content;
}

extern int diags_cmd_wt( int device_fd, const char * str_cmd, int timeout )
{
    
    //struct memory_struct * ms;
    unsigned long cmd_len = (strlen( str_cmd ) + 2);
    char test_cmd[cmd_len];
    snprintf( test_cmd, sizeof(test_cmd), "%s\r", str_cmd );
    int rev = write_serial( device_fd, test_cmd, timeout );
    //ms = diags_read( device_fd );
    //printf("%s", ms->memory_content);
    return rev;
}

extern int is_alive( int fd )
{
		struct memory_struct * ms;
		write_serial( fd, "\r", 0 );
		write_serial( fd, "\r", 0 );
		ms = diags_read( fd );
		if ( ms->size > 1 )
			return 0;
		else	
			return -1;
}

extern struct response_info * parse_diags_result( const char * diags_return, const char * test_item_keyword, char * search_keywords )
{
	static struct response_info r;
	struct response_info * ri_ptr = &r;
	char *error_ptr = NULL;
	char *fail_ptr = NULL;
	char *keyword_ptr = NULL;

	strncpy( ri_ptr->test_item, test_item_keyword, sizeof(ri_ptr->test_item) );	
	keyword_ptr = strcasestr( diags_return, search_keywords );
	if ( keyword_ptr != NULL )
	{
		error_ptr = strcasestr( diags_return, "error" );
		fail_ptr = strcasestr( diags_return, "fail" );
		if ( error_ptr || fail_ptr )
		{
			ri_ptr->test_result = 0;
			snprintf( ri_ptr->test_value, sizeof(ri_ptr->test_value), "%s", (error_ptr != NULL) ? error_ptr : fail_ptr );	
		}
		else
		{
			ri_ptr->test_result = 1;
			strncpy( ri_ptr->test_value, "PASS", sizeof(ri_ptr->test_value) );	
		}
	}
	else
	{
		ri_ptr->test_result = 0;
		snprintf( ri_ptr->test_value, sizeof(ri_ptr->test_value), "%s:key not found!", test_item_keyword );	
	}

	return ri_ptr;
}

void output_parse_result( struct response_info * ri_m_ptr )
{
	if ( ri_m_ptr->test_result )	
	{
		fprintf( stdout, "\n%s : %s\n", ri_m_ptr->test_item, ri_m_ptr->test_value );
	}
	else
		fprintf( stdout, "\n%s : fail\n", ri_m_ptr->test_item );
}



