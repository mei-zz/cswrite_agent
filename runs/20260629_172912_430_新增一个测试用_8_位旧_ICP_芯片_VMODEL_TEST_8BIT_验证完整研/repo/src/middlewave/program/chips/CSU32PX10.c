#include "io_icsp.h"
#include "chip_operation.h"

static int csu32px10_read_id(void) { return io_icsp_read_id(); }
static int csu32px10_erase(void) { return io_icsp_chip_erase(); }
static int csu32px10_program(void) { return io_icsp_program(); }

const struct chip_operation csu32px10_ops = {
    .read_id = csu32px10_read_id,
    .erase = csu32px10_erase,
    .program = csu32px10_program,
};

