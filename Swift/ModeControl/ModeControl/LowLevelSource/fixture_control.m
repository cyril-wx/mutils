/*
 Write by leo, update by bruce 2018/08/03
 */
//*********************Fixture Control *****************************//

#import "fixture_control.h"


void fixtureItemInfo(char * item_Info);
int fixtureCmdWR(char * str_Cmd, int time_Out);    //time_Out=1 >> 0.1s
int fixtureCmdWRWithFD(char * str_Cmd, int fd, int time_Out);
void fixtureClose(void);
int fixtureInit(char * fixture_Serial);
int fixtureStart(char *fixture_Serial );
int fixtureEnd(char * fixture_Serial );
int fixtureLEDSet(char * fixture_Serial, char * DUT_slot , char * DUT_state);
//int fixtureRead( int device_fd);
NSString* fixtureRead( int device_fd);
int isFixtureFlag(NSString * read_Result, NSString * fixture_Flag);
int TTfixtureInit(char * fixture_Serial);
int TTfixtureInitReturnFD(char * fixture_Serial);
int TTFixtureStart(char * fixture_Serial );
int TTFixtureEnd(char * fixture_Serial );
int TTFixtureRecovery(char * fixture_Serial);
int TTFixtureRecoveryWithFD(int device_fd);
int TTFixtureDiagsWithFD(int device_fd);
int TTFixtureDiags(char * fixture_Serial);
int TTFixtureDFU(char * fixture_Serial);
int TTFixtureDFUWithFD(int device_fd);


#ifdef FIXTURE_MESSAGE_CALLBACK
char fixture_Message[FIXTURE_MESSAGE_SIZE] = {""};
#endif

NSString * read_Buffer;  //store read info when send command to serial.
int device_fd = 0;

#define TTfixture_Recovery_Cmd_Count 14
char TTfixture_Recovery_Cmd[14][50]= {
    "tt_rst",
    "tt_wbattpwr_ocpset_3000",
    "tt_wvddmainpwr_ocpset_3000",
    "tt_wusbpwr_ocpset_2000",
    "tt_pmu_wake1_on",
    "tt_e75p2mux_uart",
    "tt_appid_on",
    "tt_acc1_sel_hi5",
    "tt_tristar_det_on",
    "tt_bank_sel_on",
    "tt_e75p1mux_dpdn",
    "tt_wbattpwr_stepvset_4.0",
    "tt_wvddmainpwr_vset_3.9",
    "tt_wusbpwr_vset_5"
};


#define TTfixture_Diags_Cmd_Count 14
char TTfixture_Diags_Cmd[14][50]= {
    "tt_rst",
    "tt_wbattpwr_ocpset_3000",
    "tt_wvddmainpwr_ocpset_3000",
    "tt_wusbpwr_ocpset_2000",
    "tt_pmu_wake1_on",
    "tt_e75p2mux_uart",
    "tt_appid_on",
    "tt_acc1_sel_hi5",
    "tt_tristar_det_on",
    "tt_bank_sel_on",
    "tt_e75p1mux_dpdn",
    "tt_wbattpwr_stepvset_4.0",
    "tt_wvddmainpwr_vset_3.9",
    "tt_wusbpwr_vset_5"
};

#define TTfixture_DFU_Cmd_Count 15
char TTfixture_DFU_Cmd[15][50]= {
    "tt_rst",
    "tt_wbattpwr_ocpset_3000",
    "tt_wvddmainpwr_ocpset_3000",
    "tt_wusbpwr_ocpset_2000",
    "tt_pmu_wake1_on",
    "tt_e75p2mux_uart",
    "tt_appid_on",
    "tt_acc1_sel_hi5",
    "tt_tristar_det_on",
    "tt_force_dfu_on",
    "tt_e75p1mux_dpdn",
    "tt_wbattpwr_stepvset_4.0",
    "tt_wvddmainpwr_vset_3.9",
    "tt_wusbpwr_vset_5",
    //"tt_vbus_detect_open", //for pre-dfu
    "tt_vbus_detect_close" //for post-dfu, and finally will became this.
    
};

#define FIXTURE_START_CMD_AMOUNT 8
char fixture_Start_Cmd[FIXTURE_START_CMD_AMOUNT][50]= {
    "Hold In",
    "Probe link",
    "Open iboot",
    "Open E_Detect",
    "Open E_ACC1",
    "MLB Power On",
    "USB Power On",
    "Sim in"};

#define FIXTURE_END_CMD_AMOUNT 5
char fixture_End_Cmd[FIXTURE_END_CMD_AMOUNT][50]= {
    "Close E_Detect",
    "Close E_ACC1",
    "MLB Power Off",
    "USB Power Off",
    "Reset Fixture"};
int test()
{
    for (int i = 0; i<FIXTURE_START_CMD_AMOUNT; i++) {
        NSLog(@"i= %d, command: %s", i, fixture_Start_Cmd[i]);
    }

    return 0;
}

/***********************************************************************
 *  Function: Only use to show item info
 *  Parameters:
 *      Item_Info:
 *  Return: No
 ***********************************************************************/
void fixtureItemInfo(char * item_Info)
{

#ifdef FIXTURE_DEBUG
    NSLog(@"\n===================== Item: %s =====================\n" , item_Info);
#endif
    
#ifdef FIXTURE_MESSAGE_CALLBACK
    char dev[1024] = "===================== Item:";
    strcat(dev,item_Info);
    strcat(dev, " =====================\n");
    strcat(fixture_Message, dev);
#endif

}

/***********************************************************************
 *  Function: Send command to fixture and callback, Judge if is pass.
 *  Parameters:
 *      Item_Info:
 *  Return: No
 ***********************************************************************/

int fixtureCmdWR(char * str_Cmd, int time_Out)
{
    char str_Write[50] = "";
    strcpy(str_Write, str_Cmd);
    strcat(str_Write,"\r\n");
    printf("####wr:device_fd:%d in comwr", device_fd);
    while (1) {
       
        for (int j = 0; j < FIXTURE_CMD_EXECUTE_TIME; j++)
        {
           
            write_serial( device_fd, str_Write, 0 );
            printf("write command:%s\n", str_Write);
            for (int i = 0; i < time_Out; i++) { //Wait for execute the command and judge the callback info.
                read_Buffer = fixtureRead(device_fd);
                
                if (isFixtureFlag(read_Buffer, @"fixture_done") == 0) {    //
                    
                    break;
                }
               
            }
            
            if (isFixtureFlag(read_Buffer, @"fixture_done") == 0) {     // if pass, break j;
                break;
            }
            else
            {
                DELAY(1000000);     // delay 1s,
            }
        }
        
        if (isFixtureFlag(read_Buffer, @"fixture_done") == 0) {
            break;
        }
        printf("*******find me*******");
    }
    
    return 0;
}

int fixtureCmdWRWithFD(char * str_Cmd, int fd, int time_Out)
{
    char str_Write[50] = "";
    int device_fd = fd;
    strcpy(str_Write, str_Cmd);
    strcat(str_Write,"\r\n");
    NSString * read_Buffer = [[NSString alloc]init];
    //printf("**bytest in fixtureCmdWRWithFD , device_fd:%d\n", device_fd);
    while (1) {
        
        for (int j = 0; j < FIXTURE_CMD_EXECUTE_TIME; j++)
        {
            
            write_serial( device_fd, str_Write, 0 );
            printf("write fd:%d , command:%s", device_fd, str_Write );
            for (int i = 0; i < time_Out; i++) { //Wait for execute the command and judge the callback info.
                read_Buffer = fixtureRead(device_fd);
                //printf("read_Buffer in fixtureCmdWRWithFD:%s\n", [read_Buffer cStringUsingEncoding:NSASCIIStringEncoding] );
                if (isFixtureFlag(read_Buffer, @"fixture_done") == 0) {    //
                    
                    break;
                }
                
            }
            
            if (isFixtureFlag(read_Buffer, @"fixture_done") == 0) {     // if pass, break j;
                break;
            }
            else
            {
                DELAY(1000000);     // delay 1s,
            }
        }
        
        if (isFixtureFlag(read_Buffer, @"fixture_done") == 0) {
            break;
        }else{
            printf("write fd:%d , command:%s run fail, continue!", device_fd, str_Write );
            break;
        }
        
    }
    
    return 0;
}


/***********************************************************************
 *  Function: Only use to show item info
 *  Parameters:
 *      Item_Info:
 *  Return: No
 ***********************************************************************/
void fixtureClose()
{
    close_serial(device_fd);
#ifdef FIXTURE_DEBUG
    NSLog(@"\nSerial device have closed.\n");
#endif
    
#ifdef FIXTURE_MESSAGE_CALLBACK
    strcat(fixture_Message, "Serial device have closed.\n");
#endif
    
}

/***********************************************************************
 *  Function: Init the fixture and get fd vaule.
 *  Parameters:
 *      fixture_Serial: serial info of the fixture need to open.
 *  Return: No
***********************************************************************/
int fixtureInit(char * fixture_Serial)
{
    //fixtureItemInfo("Fixture Init");
    
    if ( (device_fd = init_serial( fixture_Serial )) == -1 )
    {
#ifdef FIXTURE_DEBUG
        NSLog(@"\nInit serial: %s Error.\n", fixture_Serial);
#endif
        
#ifdef FIXTURE_MESSAGE_CALLBACK
        char dev[1024] = "Init serial: ";
        strcat(dev,fixture_Serial);
        strcat(dev, " Error.\n");
        strcat(fixture_Message, dev);
#endif
        close_serial(device_fd);
        return -1;
    }
    else
    {
#ifdef FIXTURE_DEBUG
        NSLog(@"\nInit serial: %s Successfully.\n", fixture_Serial);
#endif
        
#ifdef FIXTURE_MESSAGE_CALLBACK
        char dev[1024] = "Init serial: ";
        strcat(dev,fixture_Serial);
        strcat(dev, " Successfully.\n");
        strcat(fixture_Message, dev);
#endif
    }
    
#ifdef FIXTURE_DEBUG
    NSLog(@"\nInit serial device_fd = %d.\n" , device_fd);
#endif
    return 0;
}

int TTfixtureInitReturnFD(char * fixture_Serial)
{
    //fixtureItemInfo("Fixture Init");
    int fd = 0;
    fd = init_serial_with_baudrate( fixture_Serial, 230400 );
    printf("init serial success cable:%s, fd:%d\n", fixture_Serial, device_fd);
    if ( fd == -1 )
    {
#ifdef FIXTURE_DEBUG
        NSLog(@"\nInit serial: %s Error.\n", fixture_Serial);
#endif
        
#ifdef FIXTURE_MESSAGE_CALLBACK
        char dev[1024] = "Init serial: ";
        strcat(dev,fixture_Serial);
        strcat(dev, " Error.\n");
        strcat(fixture_Message, dev);
#endif
        close_serial(fd);
        return -1;
    }
    else
    {
#ifdef FIXTURE_DEBUG
        NSLog(@"\nInit serial: %s Successfully.\n", fixture_Serial);
#endif
        
#ifdef FIXTURE_MESSAGE_CALLBACK
        char dev[1024] = "Init serial: ";
        strcat(dev,fixture_Serial);
        strcat(dev, " Successfully.\n");
        strcat(fixture_Message, dev);
#endif
    }
    
#ifdef FIXTURE_DEBUG
    NSLog(@"\nInit serial device_fd = %d.\n" , fd);
#endif
    return fd;
}

int TTfixtureInit(char * fixture_Serial)
{
    //fixtureItemInfo("Fixture Init");
    device_fd = init_serial_with_baudrate( fixture_Serial, 230400 );
    printf("init serial success cable:%s, fd:%d\n", fixture_Serial, device_fd);
    if ( device_fd == -1 )
    {
#ifdef FIXTURE_DEBUG
        NSLog(@"\nInit serial: %s Error.\n", fixture_Serial);
#endif
        
#ifdef FIXTURE_MESSAGE_CALLBACK
        char dev[1024] = "Init serial: ";
        strcat(dev,fixture_Serial);
        strcat(dev, " Error.\n");
        strcat(fixture_Message, dev);
#endif
        close_serial(device_fd);
        return -1;
    }
    else
    {
#ifdef FIXTURE_DEBUG
        NSLog(@"\nInit serial: %s Successfully.\n", fixture_Serial);
#endif
        
#ifdef FIXTURE_MESSAGE_CALLBACK
        char dev[1024] = "Init serial: ";
        strcat(dev,fixture_Serial);
        strcat(dev, " Successfully.\n");
        strcat(fixture_Message, dev);
#endif
    }
    
#ifdef FIXTURE_DEBUG
    NSLog(@"\nInit serial device_fd = %d.\n" , device_fd);
#endif
    return 0;
}


/***********************************************************************
 *  Function: Fixture start
 *  Parameters:
 *      fixture_Serial: serial info of the fixture need to open.
 *  Return: int
 ***********************************************************************/
int fixtureStart(char *fixture_Serial )
{
#ifdef FIXTURE_MESSAGE_CALLBACK
    strcpy(fixture_Message, "");    // Init fixtre_Message
#endif
    read_Buffer = [[NSString alloc]init];
    
    fixtureItemInfo("Fixture Start");
    if(fixtureInit(fixture_Serial) == -1)
    {
        return -1;
    }
    
    //fixtureCmdWR("", FIXTURE_CMD_TIMEOUT);
    fixtureCmdWR("Hold In", FIXTURE_CMD_TIMEOUT);
    fixtureCmdWR("Probe link", FIXTURE_CMD_TIMEOUT);
    fixtureCmdWR("Open iboot", FIXTURE_CMD_TIMEOUT);
    fixtureCmdWR("Open E_Detect", FIXTURE_CMD_TIMEOUT);
    fixtureCmdWR("Open E_ACC1", FIXTURE_CMD_TIMEOUT);
    fixtureCmdWR("MLB Power On", FIXTURE_CMD_TIMEOUT);
    fixtureCmdWR("USB Power On", FIXTURE_CMD_TIMEOUT);
    fixtureCmdWR("Sim in", FIXTURE_CMD_TIMEOUT);
    
#ifdef FIXTURE_MESSAGE_CALLBACK_DEBUG
    printf("*****************Print fixture message*****************\n%s\n",fixture_Message);
#endif
    //fixtureLEDSet("A", "Running");
    //fixtureLEDSet("B", "Running");
    fixtureClose();
    return 0;
}

/***********************************************************************
 *  Function: Fixture End
 *  Parameters:
 *      fixture_Serial: serial info of the fixture need to open.
 *  Return: int
 ***********************************************************************/
int fixtureEnd(char * fixture_Serial )
{
#ifdef FIXTURE_MESSAGE_CALLBACK
    strcpy(fixture_Message, "");    // Init fixtre_Message
#endif
    read_Buffer = [[NSString alloc]init];
    
    fixtureItemInfo("Fixture End");
    if(fixtureInit(fixture_Serial) == -1)
    {
        return -1;
    }
    
    fixtureCmdWR("Close E_Detect", FIXTURE_CMD_TIMEOUT);
    fixtureCmdWR("Close E_ACC1", FIXTURE_CMD_TIMEOUT);
    fixtureCmdWR("MLB Power Off", FIXTURE_CMD_TIMEOUT);
    fixtureCmdWR("USB Power Off", FIXTURE_CMD_TIMEOUT);
    fixtureCmdWR("Reset Fixture", FIXTURE_CMD_TIMEOUT);
    
#ifdef FIXTURE_MESSAGE_CALLBACK_DEBUG
    printf("*****************Print fixture message*****************\n%s\n",fixture_Message);
#endif
    
    
    fixtureClose();
    return 0;
}

/***********************************************************************
 *  Function: Fixture LED Set
 *  Parameters:
 *      DUT_slot: A/B
 *      DUT_state: Running/PASS/FAIL
 *  Return: int
 ***********************************************************************/
int fixtureLEDSet(char * fixture_Serial, char * DUT_slot , char * DUT_state)
{
#ifdef FIXTURE_MESSAGE_CALLBACK
    strcpy(fixture_Message, "");    // Init fixtre_Message
#endif
    read_Buffer = [[NSString alloc]init];
    
    fixtureItemInfo("Set Fixture LED State");
    
    if(fixtureInit(fixture_Serial) == -1)
    {
        return -1;
    }
    
    char dev[50] = "Test ";
    
    strcat(dev,DUT_state);
    strcat(dev," ");
    strcat(dev,DUT_slot);
    strcat(dev,"\r\n");
    
#ifdef FIXTURE_DEBUG
    printf( "Set fixture LED: %s\n", dev);
#endif
    
    sleep(1);
    write_serial(device_fd, dev,0);
    fixtureRead(device_fd);
    
#ifdef FIXTURE_MESSAGE_CALLBACK_DEBUG
    printf("*****************Print fixture message*****************\n%s\n",fixture_Message);
#endif
    fixtureClose();
    return 0;
}

/***********************************************************************
 *  Function: Read callback result
 *  Parameters:
 device_fd:
 read_Result: To store callback result.
 *  Return: int 0/-1 Pass/Fail
 ***********************************************************************/
NSString* fixtureRead( int device_fd)
{
    int nread;
    char temp[1000] = {0};
    memset( temp, 0, sizeof(temp) );
    NSString* read_Buffer = [[NSString alloc]init];
    //printf("in fixtureRead\n");
    while( 1 )
    {
        //nread = read_serial( device_fd, temp );
        nread = read_serial_for_mode_judge( device_fd, temp, "");
        //printf("**bytest**%s\n",temp);
        if ( nread == 0 )
        {
#ifdef FIXTURE_DEBUG
            NSLog(@"nread = %d", nread);
#endif
            break;
        }
        else if ( nread == -1 )
        {
#ifdef FIXTURE_DEBUG
            perror( "Read error\n" );
#endif
#ifdef FIXTURE_MESSAGE_CALLBACK
            //strcat(fixture_Message, "Read error");
#endif
            read_Buffer = @"Read error" ;
            return [NSString stringWithUTF8String:"-1"];
        }
        
        if (strlen(temp) > 0)
        {
            //printf("***bytest in fixtureRead **%s**",temp);
#ifdef FIXTURE_MESSAGE_CALLBACK
            //strcat(fixture_Message, temp);
#endif
            //printf("***bytest***:%s:\n", temp);
           
            return [NSString stringWithUTF8String:temp];    //char => NSString
            
        }
        DELAY(FIXTURE_READ_TIMEOUT);   // 0.1s
    }
    return [NSString stringWithUTF8String:"0"];
}

/***********************************************************************
 *  Function:Search specified flag from the string.
 *  Parameters:
 read_Result:
 fixture_Flag: diags: "Pass"/"illegal"
 *  Return: int 0/-1 Pass/Fail
 ***********************************************************************/
int isFixtureFlag(NSString * read_Result, NSString * fixture_Flag)
{
#ifdef FIXTURE_DEBUG
    NSLog(@"Search the flag:%@ from read result.",fixture_Flag);
    NSLog(@"%@", read_Result);
    NSLog(@"%@", fixture_Flag);
#endif
    
    if ([read_Result rangeOfString:fixture_Flag].location == NSNotFound) {
#ifdef FIXTURE_DEBUG
        NSLog(@"Read result don't include the flag: %@",fixture_Flag);
#endif
        return -1;
    }
    else
    {
#ifdef DEVICE_MODE_CONTROL_DEBUG
        NSLog(@"Read result include the flag: %@",mode_Flag);
#endif
    }
    
    return 0;
}

int TTFixtureRecovery(char * fixture_Serial){
    int fd = 0;
    if( (fd = TTfixtureInitReturnFD(fixture_Serial)) == -1)
    {
        return -1;
    }
    if (fd > 0) {
        //printf("**bytest in com wr:device_fd:%d", fd);
        for (int i=0; i<TTfixture_Recovery_Cmd_Count; i++) {
            fixtureCmdWRWithFD( TTfixture_Recovery_Cmd[i], fd, FIXTURE_CMD_TIMEOUT);
        }
        return 0;
    }
    return -1;
}


int TTFixtureRecoveryWithFD(int device_fd){
    int fd = device_fd;
    
    if (fd > 0) {
        //printf("**bytest in com wr:device_fd:%d", fd);
        for (int i=0; i<TTfixture_Recovery_Cmd_Count; i++) {
            fixtureCmdWRWithFD( TTfixture_Recovery_Cmd[i], fd, FIXTURE_CMD_TIMEOUT);
        }
        sleep(1);
        return 0;
    }
    return -1;
}

int TTFixtureDiagsWithFD(int device_fd){
    int fd = device_fd;
    
    if (fd > 0) {
        for (int i=0; i<TTfixture_Diags_Cmd_Count; i++) {
            fixtureCmdWRWithFD( TTfixture_Diags_Cmd[i], fd, FIXTURE_CMD_TIMEOUT);
        }
        sleep(1);
        return 0;
    }
    return -1;
}

int TTFixtureDiags(char * fixture_Serial){
    int fd = 0;
    if((fd = TTfixtureInitReturnFD(fixture_Serial)) == -1)
    {
        return -1;
    }
    if (fd > 0) {
        for (int i=0; i<TTfixture_Diags_Cmd_Count; i++) {
            fixtureCmdWRWithFD( TTfixture_Diags_Cmd[i], fd, FIXTURE_CMD_TIMEOUT);
        }
        return 0;
    }
    return -1;
}

int TTFixtureDFUWithFD(int device_fd){
    
    if (device_fd > 0) {
        for (int i=0; i<TTfixture_DFU_Cmd_Count; i++) {
            fixtureCmdWRWithFD( TTfixture_DFU_Cmd[i], device_fd, FIXTURE_CMD_TIMEOUT);
        }
        return 0;
    }
    return -1;
}

int TTFixtureDFU(char * fixture_Serial){
    if(TTfixtureInit(fixture_Serial) == -1)
    {
        return -1;
    }
    if (device_fd > 0) {
        for (int i=0; i<TTfixture_DFU_Cmd_Count; i++) {
            fixtureCmdWR( TTfixture_DFU_Cmd[i], FIXTURE_CMD_TIMEOUT);
        }
        return 0;
    }
    return -1;
}

int TTFixtureStart(char * fixture_Serial )
{
#ifdef FIXTURE_MESSAGE_CALLBACK
    strcpy(fixture_Message, "");    // Init fixtre_Message
#endif
    read_Buffer = [[NSString alloc]init];
    
    fixtureItemInfo("TT Fixture Start");
    if(TTfixtureInit(fixture_Serial) == -1)
    {
        return -1;
    }
    
    //fixtureCmdWR("", FIXTURE_CMD_TIMEOUT);
    fixtureCmdWR("tt_rst", FIXTURE_CMD_TIMEOUT);
   
    fixtureCmdWR("tt_fixture_in", FIXTURE_CMD_TIMEOUT);
    sleep(3);
    fixtureCmdWR("tt_fixture_down", FIXTURE_CMD_TIMEOUT);
    
    
    
#ifdef FIXTURE_MESSAGE_CALLBACK_DEBUG
    printf("*****************Print fixture message*****************\n%s\n",fixture_Message);
#endif
    //fixtureLEDSet("A", "Running");
    //fixtureLEDSet("B", "Running");
    fixtureClose();
    return 0;
    
}

int TTFixtureStartWithFD(int fd)
{
#ifdef FIXTURE_MESSAGE_CALLBACK
    strcpy(fixture_Message, "");    // Init fixtre_Message
#endif
    
    fixtureCmdWRWithFD("tt_rst", fd, FIXTURE_CMD_TIMEOUT);
    
    fixtureCmdWRWithFD("tt_fixture_in", fd, FIXTURE_CMD_TIMEOUT);
    sleep(3);
    fixtureCmdWRWithFD("tt_fixture_down", fd, FIXTURE_CMD_TIMEOUT);
    
    
#ifdef FIXTURE_MESSAGE_CALLBACK_DEBUG
    printf("*****************Print fixture message*****************\n%s\n",fixture_Message);
#endif
    //fixtureLEDSet("A", "Running");
    //fixtureLEDSet("B", "Running");
    return 0;
    
}

int TTFixtureEndWithFD(int fd)
{
#ifdef FIXTURE_MESSAGE_CALLBACK
    strcpy(fixture_Message, "");    // Init fixtre_Message
#endif
    read_Buffer = [[NSString alloc]init];
    
    fixtureItemInfo("TT Fixture End");
 
    //write_serial( device_fd, "nanokdp\r\n", 0 );
    fixtureCmdWRWithFD("tt_rst", fd, FIXTURE_CMD_TIMEOUT);
    fixtureCmdWRWithFD("tt_fixture_up", fd, FIXTURE_CMD_TIMEOUT);
    sleep(3);
    fixtureCmdWRWithFD("tt_fixture_out", fd, FIXTURE_CMD_TIMEOUT);
    
    
#ifdef FIXTURE_MESSAGE_CALLBACK_DEBUG
    printf("*****************Print fixture message*****************\n%s\n",fixture_Message);
#endif
    //close_serial(fd);
    return 0;
    
}

int TTFixtureEnd(char * fixture_Serial )
{
#ifdef FIXTURE_MESSAGE_CALLBACK
    strcpy(fixture_Message, "");    // Init fixtre_Message
#endif
    read_Buffer = [[NSString alloc]init];
    
    fixtureItemInfo("TT Fixture End");
    if(TTfixtureInit(fixture_Serial) == -1)
    {
        return -1;
    }
    //write_serial( device_fd, "nanokdp\r\n", 0 );
    fixtureCmdWR("tt_fixture_up", FIXTURE_CMD_TIMEOUT);
    sleep(3);
    fixtureCmdWR("tt_fixture_out", FIXTURE_CMD_TIMEOUT);
    
    
#ifdef FIXTURE_MESSAGE_CALLBACK_DEBUG
    printf("*****************Print fixture message*****************\n%s\n",fixture_Message);
#endif
    
    
    fixtureClose();
    return 0;
}
