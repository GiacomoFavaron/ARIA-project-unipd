#include <errno.h>
#include <fcntl.h> 
#include <string.h>
#include <termios.h>
#include <unistd.h>

#include <common/mavlink.h>
#include <common/mavlink_msg_system_time.h>

int
set_interface_attribs (int fd, int speed, int parity)
{
        struct termios tty;
        if (tcgetattr (fd, &tty) != 0)
        {
                error_message ("error %d from tcgetattr", errno);
                return -1;
        }

        cfsetospeed (&tty, speed);
        cfsetispeed (&tty, speed);

        tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8;     // 8-bit chars
        // disable IGNBRK for mismatched speed tests; otherwise receive break
        // as \000 chars
        tty.c_iflag &= ~IGNBRK;         // disable break processing
        tty.c_lflag = 0;                // no signaling chars, no echo,
                                        // no canonical processing
        tty.c_oflag = 0;                // no remapping, no delays
        tty.c_cc[VMIN]  = 0;            // read doesn't block
        tty.c_cc[VTIME] = 5;            // 0.5 seconds read timeout

        tty.c_iflag &= ~(IXON | IXOFF | IXANY); // shut off xon/xoff ctrl

        tty.c_cflag |= (CLOCAL | CREAD);// ignore modem controls,
                                        // enable reading
        tty.c_cflag &= ~(PARENB | PARODD);      // shut off parity
        tty.c_cflag |= parity;
        tty.c_cflag &= ~CSTOPB;
        tty.c_cflag &= ~CRTSCTS;

        if (tcsetattr (fd, TCSANOW, &tty) != 0)
        {
                error_message ("error %d from tcsetattr", errno);
                return -1;
        }
        return 0;
}

void
set_blocking (int fd, int should_block)
{
        struct termios tty;
        memset (&tty, 0, sizeof tty);
        if (tcgetattr (fd, &tty) != 0)
        {
                error_message ("error %d from tggetattr", errno);
                return;
        }

        tty.c_cc[VMIN]  = should_block ? 1 : 0;
        tty.c_cc[VTIME] = 5;            // 0.5 seconds read timeout

        if (tcsetattr (fd, TCSANOW, &tty) != 0)
                error_message ("error %d setting term attributes", errno);
}

//--------------------

mavlink_status_t status;
mavlink_message_t msg;
int chan = MAVLINK_COMM_0;
mavlink_system_time_t time_message;

char *portname = "/dev/ttyS2"   // telem2 port

int fd = open (portname, O_RDWR | O_NOCTTY | O_SYNC);
if (fd < 0)
{
        error_message ("error %d opening %s: %s", errno, portname, strerror (errno));
        return;
}

set_interface_attribs (fd, B9600, 0);  // set speed to 9600 bps, 8n1 (no parity)
set_blocking (fd, 0);                // set no blocking

//write (fd, "hello!\n", 7);           // send 7 character greeting

//usleep ((7 + 25) * 100);             // sleep enough to transmit the 7 plus
                                     // receive 25:  approx 100 uS per char transmit
uint8_t byte = 0;
//int n = read (fd, buf, sizeof buf);  // read up to 100 characters if ready to read

while(1) {
    int n = read (fd, &byte, sizeof buf);
    if(n == -1) {
        error_message ("error %d on read: %s", errno, portname, strerror (errno));
        return;
    }
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