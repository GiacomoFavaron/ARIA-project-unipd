#include <errno.h>
#include <fcntl.h> 
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <termios.h>
#include <unistd.h>

#include <common/mavlink.h>
#include <common/mavlink_msg_system_time.h>
#include <common/mavlink_msg_timesync.h>

int
set_interface_attribs (int fd, int speed, int parity)
{
        struct termios tty;
        if (tcgetattr (fd, &tty) != 0)
        {
                fprintf (stderr, "error %d from tcgetattr", errno);
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
                fprintf (stderr, "error %d from tcsetattr", errno);
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
                fprintf (stderr, "error %d from tggetattr", errno);
                return;
        }

        tty.c_cc[VMIN]  = should_block ? 1 : 0;
        tty.c_cc[VTIME] = 5;            // 0.5 seconds read timeout

        if (tcsetattr (fd, TCSANOW, &tty) != 0)
                fprintf (stderr, "error %d setting term attributes", errno);
}

//--------------------

int main() {

        mavlink_system_t mavlink_system = {
                1, // System ID
                1  // Component ID
        };

        mavlink_status_t status;
        mavlink_message_t msg;
        int chan = MAVLINK_COMM_0;
        mavlink_system_time_t time_message;
        mavlink_timesync_t timesync_message;

        char *portname = "/dev/ttyS0";   // telem2 port

        int fd = open (portname, O_RDWR | O_NOCTTY | O_SYNC);
        if (fd < 0)
        {
                fprintf (stderr, "error %d opening %s: %s", errno, portname, strerror (errno));
                return 1;
        }

        set_interface_attribs (fd, B9600, 0);  // set speed to 9600 bps, 8n1 (no parity)
        set_blocking (fd, 0);                // set no blocking

        //write (fd, "hello!\n", 7);           // send 7 character greeting

        //usleep ((7 + 25) * 100);             // sleep enough to transmit the 7 plus
                                        // receive 25:  approx 100 uS per char transmit
        //int n = read (fd, buf, sizeof buf);  // read up to 100 characters if ready to read

        FILE* output = open("pixhawk_time.txt", 'w');

        uint8_t byte = 0;

        while(1) {
                int n = read (fd, &byte, 1);
                //printf("read returns: %d\n", n);
                //printf("The read byte is: %d\n", byte);
                if(n == -1) {
                        fprintf (stderr, "error %d on read: %s", errno, portname, strerror (errno));
                        return 1;
                }
                if (mavlink_parse_char(chan, byte, &msg, &status)) {
                        printf("Received message with ID %d, sequence: %d from component %d of system %d\n", msg.msgid, msg.seq, msg.compid, msg.sysid);
                        switch(msg.msgid) {
                                case MAVLINK_MSG_ID_SYSTEM_TIME: {
                                        mavlink_msg_system_time_decode(&msg, &time_message);
                                        printf("Unix Pixhawk time = %d\n", time_message.time_unix_usec);
                                        fprintf(output, "%d,\n", time_message.time_unix_usec);
                                }
                                case MAVLINK_MSG_ID_TIMESYNC: {
                                        mavlink_msg_timesync_decode(&msg, &timesync_message);
                                        printf("Timesync t1 = %d\n", timesync_message.tc1);
                                }
                        }
                }
        }

}
