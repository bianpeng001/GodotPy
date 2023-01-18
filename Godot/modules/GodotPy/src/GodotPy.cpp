//
// 2023-1-17
//

#include "GodotPy.h"

#include <Windows.h>
#define PY_SSIZE_T_CLEAN
#include <Python.h>

static PyObject *f_print(PyObject *module, PyObject *args) {
	const char *str;

	if (!PyArg_ParseTuple(args, "s", &str)) {
		return NULL;
	}
	print_line(str);

	Py_RETURN_NONE;
}

static PyMethodDef GodotPy_methods[] = {
	{ "print", f_print, METH_VARARGS, NULL },
	{ NULL, NULL, 0, NULL }
};
static struct PyModuleDef GodotPymodule = {
	PyModuleDef_HEAD_INIT,
	"GodotPy",
	NULL,
	0,
	GodotPy_methods,
	NULL,
	NULL,
	NULL,
	NULL,
};
PyMODINIT_FUNC PyInit_GodotPy(void) {
	return PyModuleDef_Init(&GodotPymodule);
}
static int InitPython() {
	const char program[] = "GodotPyGame";
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

bool FLibPy::bInit = false;

void FLibPy::Init() {
	if (!bInit) {
		bInit = true;
		print_line("begin init python");

		SetEnvironmentVariableA("PYTHONPATH", ".");
		PyImport_AppendInittab("GodotPy", &PyInit_GodotPy);
		InitPython();
		//Py_Initialize();
		
		PyRun_SimpleString("import GodotPy;GodotPy.print('hello python')\n");
		print_line("init python ok");
	}
}

void FLibPy::Clean() {
	if (!bInit) {
		Py_FinalizeEx();
		bInit = false;
	}
}
//------------------------------------------------------------------------------
//
//------------------------------------------------------------------------------
FPyModule::FPyModule() :
		py_file_path(),
		py_module(nullptr) {
	//this->add_child();
}

FPyModule::~FPyModule() {
	if (py_module) {
		Py_DECREF(py_module);
		py_module = nullptr;
	}
}

void FPyModule::_notification(int p_what) {
	switch (p_what) {
		case NOTIFICATION_READY:
			_ready();
			break;
	}
}

void FPyModule::_ready() {
	if (!py_file_path.is_empty()) {
		print_line(vformat("load module: %s", py_file_path));

		PyObject *pName = PyUnicode_FromString(py_file_path.utf8().get_data());
		py_module = PyImport_Import(pName);
		Py_DECREF(pName);

		if (py_module) {
			print_line("load module ok");
		}
	}
}

void FPyModule::set_python(const String &a_file_path) {
	py_file_path = a_file_path;
}

void FPyModule::_bind_methods() {
	ClassDB::bind_method(D_METHOD("set_python", "python"), &FPyModule::set_python);
	ClassDB::bind_method(D_METHOD("get_python"), &FPyModule::get_python);
	ADD_PROPERTY(PropertyInfo(Variant::STRING, "python"), "set_python", "get_python");
}


