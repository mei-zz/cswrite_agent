#include "config_8bit.h"
#include "chip_operation.h"

extern const struct chip_operation csu32px10_ops;
extern const struct chip_operation csu38mx10_ops;
extern const struct chip_operation vmodel_repair_8bit_ops;
/* EXTERN_END */

#define OPS_CSU32PX10 (&csu32px10_ops)
#define OPS_CSU38MX10 (&csu38mx10_ops)
#define OPS_VMODEL_REPAIR_8BIT (&vmodel_repair_8bit_ops)
/* OPS_DEFINE_END */

const char *cswrite_chip_list[] = {
    STR_CSU32PX10,
    STR_CSU38MX10,
    STR_VMODEL_REPAIR_8BIT,
/* CHIP_LIST_END */
};

const struct chip_operation *cswrite_chip_ops_list[] = {
    OPS_CSU32PX10,
    OPS_CSU38MX10,
    OPS_VMODEL_REPAIR_8BIT,
/* OPS_LIST_END */
};

