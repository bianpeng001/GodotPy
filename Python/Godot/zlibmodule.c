//
// zlibmodule，使得可以从zip包加载module
// 为了编译方便，为freeze流程，提供一个假的zlibmodule
//

#ifndef Py_BUILD_CORE_BUILTIN
#  define Py_BUILD_CORE_MODULE 1
#endif
#include "Python.h"

static PyMethodDef zlib_methods[] = {
	{ NULL, NULL, 0, NULL }
};
static struct PyModuleDef zlibmodule = {
	PyModuleDef_HEAD_INIT,
	"zlib",
	NULL,
	0,
	zlib_methods,
	NULL,
	NULL,
	NULL,
	NULL,
};
PyMODINIT_FUNC
PyInit_zlib(void) {
    return PyModuleDef_Init(&zlibmodule);
}

