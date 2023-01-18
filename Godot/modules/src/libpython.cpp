//
// 2023-1-17
//

#include "libpython.h"

#include <Windows.h>
#define PY_SSIZE_T_CLEAN
#include <Python.h>

static PyObject *fio_print(PyObject *module, PyObject *args) {
	const char *str;

	if (!PyArg_ParseTuple(args, "s", &str)) {
		return NULL;
	}
	print_line(str);

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

bool FioLibPython::bInit = false;

void FioLibPython::Init() {
	if (!bInit) {
		bInit = true;
		print_line("begin init python");

		SetEnvironmentVariableA("PYTHONPATH", ".");
		PyImport_AppendInittab("fio", &PyInit_fio);
		InitPython();
		//Py_Initialize();
		
		//PyRun_SimpleString("print('hello python')\n");
		print_line("init python ok");
	}
}

void FioLibPython::Clean() {
	if (!bInit) {
		Py_FinalizeEx();
		bInit = false;
	}
}
//------------------------------------------------------------------------------
//
//------------------------------------------------------------------------------
FioExecPython::FioExecPython() :
		py_file_path(),
		py_obj(nullptr) {
	//this->add_child();
}

FioExecPython::~FioExecPython() {
	if (py_obj) {
		Py_DECREF(py_obj);
		py_obj = nullptr;
	}
}

void FioExecPython::_notification(int p_what) {
	switch (p_what) {
		case NOTIFICATION_READY:
			_ready();
			break;
	}
}

void FioExecPython::_ready() {
	print_line(vformat("load module: %s", py_file_path));
	if (!py_file_path.is_empty()) {
		PyObject *pName = PyUnicode_FromString(py_file_path.utf8().get_data());
		py_obj = PyImport_Import(pName);
		Py_DECREF(pName);

		if (py_obj) {
			print_line("load module ok");
		}
	}
}

void FioExecPython::set_python(const String &a_file_path) {
	py_file_path = a_file_path;
}

void FioExecPython::_bind_methods() {
	ClassDB::bind_method(D_METHOD("set_python", "python"), &FioExecPython::set_python);
	ClassDB::bind_method(D_METHOD("get_python"), &FioExecPython::get_python);
	ADD_PROPERTY(PropertyInfo(Variant::STRING, "python"), "set_python", "get_python");
}


