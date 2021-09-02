//#include <Python.h>

// C library headers
#include <stdio.h>
#include <string.h>

// Linux headers
#include <fcntl.h> // Contains file controls like O_RDWR
#include <errno.h> // Error integer and strerror() function
#include <termios.h> // Contains POSIX terminal control definitions
#include <unistd.h> // write(), read(), close()

#include <common/mavlink.h>

mavlink_status_t status;
mavlink_message_t msg;
int chan = MAVLINK_COMM_0;

int serial = open("/dev/ttyUSB0", O_RDWR);

// Check for errors
if (serial < 0) {
    printf("Error %i from open: %s\n", errno, strerror(errno));
}

while(serial.bytesAvailable > 0)
{
  uint8_t byte = serial.getNextByte();
  if (mavlink_parse_char(chan, byte, &msg, &status))
    {
    printf("Received message with ID %d, sequence: %d from component %d of system %d\n", msg.msgid, msg.seq, msg.compid, msg.sysid);
    // ... DECODE THE MESSAGE PAYLOAD HERE ...
    }
}