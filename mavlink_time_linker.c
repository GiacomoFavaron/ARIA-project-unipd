#include <errno.h>
#include <fcntl.h> 
#include <inttypes.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <termios.h>
#include <time.h>
#include <unistd.h>

#include <common/mavlink.h>
#include <common/mavlink_msg_system_time.h>
#include <common/mavlink_msg_timesync.h>
#include <common/mavlink_msg_global_position_int.h>

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

        // structs to store the received messages
        mavlink_system_time_t time_message;
        mavlink_timesync_t timesync_message;
        mavlink_global_position_int_t global_message;

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

        uint8_t byte = 0;
        uint64_t mavlink_unix_time = 0;
        uint64_t time_since_boot = 0;

        // Print output file headers
        FILE* output = fopen("mavlink_output.csv", "w");
        if(output == NULL) {
                fprintf(stderr, "Error opening mavlink_output.csv!\n");
                exit(1);
        }
        fprintf(output, "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n", "UNIX time mavlink", "time since system boot mavlink", "lat", "lon", "alt", "relative_alt", "vx", "vy", "vz", "hdg");
        fclose(output);

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
                                        // printf("Raspberry Unix time = %u\n", (unsigned)time(NULL));
                                        // printf("UNIX epoch time = %" PRIu64 "\n", time_message.time_unix_usec);
                                        // printf("time since system boot = %" PRIu32 "\n", time_message.time_boot_ms);
                                        mavlink_unix_time = time_message.time_unix_usec;
                                        time_since_boot = time_message.time_boot_ms;
                                }
                                // case MAVLINK_MSG_ID_TIMESYNC: {
                                //         mavlink_msg_timesync_decode(&msg, &timesync_message);
                                //         printf("Timesync tc1 = %" PRId64 "\n", timesync_message.tc1); // it's the unix epoch time
                                //         printf("Timesync ts1 = %" PRId64 "\n", timesync_message.ts1); // it's the time since system boot
                                //         output = fopen("mavlink_output.csv", "a");
                                //         if(output == NULL) {
                                //                 fprintf(stderr, "Error opening mavlink_output.csv!\n");
                                //                 exit(1);
                                //         }
                                //         fprintf(output, "%" PRId64 ",", timesync_message.tc1);
                                //         //fprintf(output, "%" PRId64 ",", timesync_message.ts1);
                                //         fclose(output);
                                //         //return 0;
                                // }
                                case MAVLINK_MSG_ID_GLOBAL_POSITION_INT: {
                                        // if(mavlink_unix_time == 0) {
                                        //         continue;
                                        // }
                                        mavlink_msg_global_position_int_decode(&msg, &global_message);
                                        output = fopen("mavlink_output.csv", "a");
                                        if(output == NULL) {
                                                fprintf(stderr, "Error opening mavlink_output.csv!\n");
                                                exit(1);
                                        }
                                        fprintf(output, "%" PRIu64 ",", mavlink_unix_time);
                                        fprintf(output, "%" PRIu32 ",", time_since_boot);
                                        fprintf(output, "%" PRId32 ",", global_message.lat);
                                        fprintf(output, "%" PRId32 ",", global_message.lon);
                                        fprintf(output, "%" PRId32 ",", global_message.alt);
                                        fprintf(output, "%" PRId32 ",", global_message.relative_alt);
                                        fprintf(output, "%" PRId16 ",", global_message.vx);
                                        fprintf(output, "%" PRId16 ",", global_message.vy);
                                        fprintf(output, "%" PRId16 ",", global_message.vz);
                                        fprintf(output, "%" PRIu16 "\n", global_message.hdg);
                                        fclose(output);
                                        return 0;
                                }
                        }
                }
        }

}
