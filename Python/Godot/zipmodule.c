#ifndef Py_BUILD_CORE_BUILTIN
#  define Py_BUILD_CORE_MODULE 1
#endif
#include "Python.h"

static PyMethodDef zlib_methods[] = {
	{ NULL, NULL, 0, NULL }
};
static struct PyModuleDef zipmodule = {
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
    return PyModuleDef_Init(&zipmodule);
}

