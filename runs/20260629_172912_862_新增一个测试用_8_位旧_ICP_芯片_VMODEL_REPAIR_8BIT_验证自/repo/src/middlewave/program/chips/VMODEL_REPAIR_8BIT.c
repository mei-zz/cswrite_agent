#include "io_icsp.h"
#include "chip_operation.h"

static int vmodel_repair_8bit_read_id(void) { return io_icsp_read_id(); }
static int vmodel_repair_8bit_erase(void) { return io_icsp_chip_erase(); }
static int vmodel_repair_8bit_program(void) { return io_icsp_program(); }

const struct chip_operation vmodel_repair_8bit_ops = {
    .read_id = vmodel_repair_8bit_read_id,
    .erase = vmodel_repair_8bit_erase,
    .program = vmodel_repair_8bit_program,
};
