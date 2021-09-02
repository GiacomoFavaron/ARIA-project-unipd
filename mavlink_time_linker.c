//#include <Python.h>

// C library headers
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Linux headers
#include <fcntl.h> // Contains file controls like O_RDWR
#include <errno.h> // Error integer and strerror() function
//#include <termios.h> // Contains POSIX terminal control definitions
//#include <unistd.h> // write(), read(), close()

#include <common/mavlink.h>
#include <common/mavlink_msg_system_time.h>

int main() {
	
	mavlink_status_t status;
	mavlink_message_t msg;
	int chan = MAVLINK_COMM_0;

	FILE *serial = fopen("/dev/ttyS2","r"); // Open Serial communication through TELEM 2

	// Check for errors
	if (serial < 0) {
		printf("Error %i from open: %s\n", errno, strerror(errno));
	}

	mavlink_system_time_t time_message;

	while(1) {
	uint8_t byte = serial.getNextByte();
	if (mavlink_parse_char(chan, byte, &msg, &status)) {
			printf("Received message with ID %d, sequence: %d from component %d of system %d\n", msg.msgid, msg.seq, msg.compid, msg.sysid);
			switch(msg.msgid) {
				case MAVLINK_MSG_ID_SYSTEM_TIME: {
					mavlink_msg_system_time_decode(&msg, &time_message);
					char string[20];
					itoa(time_message.time_unix_usec,string,10);
					printf("Unix Pixhawk time = %s\n", string);
				}
			}
		}
	}

}