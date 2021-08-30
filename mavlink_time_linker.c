#include <Python.h>

#include <your_dialect/mavlink.h>

#include <common/mavlink.h> //? e' il dialetto come sopra?

mavlink_system_t mavlink_system = {
    1, // System ID (1-255)
    1  // Component ID (a MAV_COMPONENT value)
};

mavlink_status_t status;
mavlink_message_t msg;
int chan = MAVLINK_COMM_0;

while(serial.bytesAvailable > 0)
{
  uint8_t byte = serial.getNextByte();
  if (mavlink_parse_char(chan, byte, &msg, &status))
    {
    printf("Received message with ID %d, sequence: %d from component %d of system %d\n", msg.msgid, msg.seq, msg.compid, msg.sysid);
    // ... DECODE THE MESSAGE PAYLOAD HERE ...
    }
}