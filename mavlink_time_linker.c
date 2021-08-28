#include <Python.h>

#include <your_dialect/mavlink.h>

mavlink_system_t mavlink_system = {
    1, // System ID (1-255)
    1  // Component ID (a MAV_COMPONENT value)
};