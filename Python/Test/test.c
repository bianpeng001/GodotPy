#define PY_SSIZE_T_CLEAN
#include <Python.h>

static PyObject *fio_print(PyObject* self, PyObject *args) {
    const char *str;
    if(!PyArg_ParseTuple(args, "s", &str)) {
        return NULL;
    }
    puts(str);
	Py_RETURN_NONE;
}

static PyMethodDef fio_methods[] = {
	{ "print", fio_print, METH_VARARGS, NULL },
	{ NULL, NULL, 0, NULL }
};

static struct PyModuleDef fiomodule = {
	PyModuleDef_HEAD_INIT,
	"fio",
	NULL,
	0,
	fio_methods,
	NULL,
	NULL,
	NULL,
	NULL,
};
PyMODINIT_FUNC PyInit_fio(void) {
	return PyModuleDef_Init(&fiomodule);
}
static int InitPython() {
	const char program[] = "game";
	PyStatus status;
	PyConfig config;
	size_t program_len;

	PyConfig_InitPythonConfig(&config);
	//config.isolated = 1;
	config.program_name = Py_DecodeLocale(program, &program_len);

	//status = PyConfig_SetBytesArgv(&config, argc, argv);
	//if (PyStatus_Exception(status)) {
	//	goto exception;
	//}

	status = Py_InitializeFromConfig(&config);
	if (PyStatus_Exception(status)) {
		goto exception;
	}
	PyConfig_Clear(&config);

	//return Py_RunMain();
	return 0;

exception:
	PyConfig_Clear(&config);
	if (PyStatus_IsExit(status)) {
		return status.exitcode;
	}
	/* Display the error message and exit the process with
	   non-zero exit code */
	Py_ExitStatusException(status);
}

int main() {
	PyObject *pModule, *pName, *Program;

    PyImport_AppendInittab("fio", &PyInit_fio);
	SetEnvironmentVariableA("PYTHONPATH", ".");
	InitPython();
    //Py_Initialize();
	

    PyRun_SimpleString("print('hello python')\n");
    pName = PyUnicode_FromString("start_python");
    pModule = PyImport_Import(pName);
    Py_DECREF(pName);

    if (pModule) {
        // TODO:
    }
	
    Py_FinalizeEx();
	
    return 0;
}

