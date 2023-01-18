/* Implements the getpath API for compiling with no functionality */

#include "Python.h"
#include "pycore_pathconfig.h"
#include "pycore_fileutils.h"
#include "pycore_initconfig.h"
#include "pycore_pymem.h"

PyStatus
_PyConfig_InitPathConfig(PyConfig *config, int compute_path_config)
{
    return _PyStatus_OK();
    //return PyStatus_Error("not support frozen module");
}


