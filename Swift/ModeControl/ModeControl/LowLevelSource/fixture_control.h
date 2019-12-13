#ifndef FIXTURE_CONTROL_H
#define FIXTURE_CONTROL_H

#import <Foundation/Foundation.h>
#import "serial_control.h"

#define FIXTURE_READ_TIMEOUT 100000   // 0.1s
#define FIXTURE_CMD_TIMEOUT 10        //50*0.1s = 5s wait for execute command and feedback info.
#define FIXTURE_CMD_EXECUTE_TIME 3    // if this command is illegal, have a try the command (5 times)
#define DFUTTFIXTURE

//#define FIXTURE_DEBUG
//#define FIXTURE_MESSAGE_CALLBACK_DEBUG
#define FIXTURE_MESSAGE_CALLBACK

#ifdef FIXTURE_MESSAGE_CALLBACK
#define FIXTURE_MESSAGE_SIZE 1024
extern char fixture_Message[FIXTURE_MESSAGE_SIZE];      //Callback all fixture message
#endif


extern int test(void);
extern int fixtureStart(char * fixture_Serial );
extern int fixtureEnd(char * fixture_Serial );
extern int fixtureLEDSet(char * fixture_Serial, char * DUT_slot , char * DUT_state);

//#define DFUTTFIXTURE
#ifdef DFUTTFIXTURE

#define DFU_TT_FIXTURE_DEBUG
extern int TTFixtureRecovery(char * fixture_Serial);
extern int TTFixtureDiags(char * fixture_Serial);
extern int TTFixtureDFU(char * fixture_Serial);
extern int TTfixtureInit(char * fixture_Serial);
extern int TTfixtureInitReturnFD(char * fixture_Serial);
extern int TTFixtureStart(char * fixture_Serial );
extern int TTFixtureStartWithFD(int fd);
extern int TTFixtureEnd(char * fixture_Serial );
extern int TTFixtureEndWithFD(int fd);
extern int TTFixtureRecoveryWithFD(int device_fd);
extern int TTFixtureDiagsWithFD(int device_fd);
extern int TTFixtureDFUWithFD(int device_fd);
#endif

#endif
