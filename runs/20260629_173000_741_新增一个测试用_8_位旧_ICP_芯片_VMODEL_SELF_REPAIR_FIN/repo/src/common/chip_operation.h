#ifndef CHIP_OPERATION_H
#define CHIP_OPERATION_H

struct chip_operation {
    int (*read_id)(void);
    int (*erase)(void);
    int (*program)(void);
};

#endif

