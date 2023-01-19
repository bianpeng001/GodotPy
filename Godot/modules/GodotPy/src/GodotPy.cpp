//
// 2023-1-17
//

#include "GodotPy.h"

#include <Windows.h>
#define PY_SSIZE_T_CLEAN
#include <Python.h>

static void f_destroy_capsule(PyObject* p_capsule) {
	auto name = PyCapsule_GetName(p_capsule);

	print_line(vformat("capsule free: %s", name));
}

static PyObject *f_print(PyObject *module, PyObject *args) {
	const char *str;

	if (!PyArg_ParseTuple(args, "s", &str)) {
		return NULL;
	}
	print_line(str);

	Py_RETURN_NONE;
}

static PyObject* f_find_node(PyObject* module, PyObject* args) {
	const char *path;
	//const char *node_name;

	if (!PyArg_ParseTuple(args, "s", &path)) {
		goto end;
	}

	/*
	auto scene = SceneTree::get_singleton()->get_current_scene();
	auto node = scene->get_node(NodePath(path));
	if (!node) {
		goto end;
	}

	node_name = static_cast<String>(node->get_name()).utf8();
	return PyCapsule_New(node, node_name, &f_destroy_capsule);
	*/

end:
	Py_RETURN_NONE;
}

static PyMethodDef GodotPy_methods[] = {
	{ "print", f_print, METH_VARARGS, NULL },
	{ "find_node", f_find_node, METH_VARARGS, NULL },
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
FPyObject::FPyObject() :
		p_module(nullptr), p_object(nullptr) {
}

FPyObject::~FPyObject() {
	if (p_module) {
		Py_DECREF(p_module);
		p_module = nullptr;
	}

	if (p_object) {
		Py_DECREF(p_object);
		p_object = nullptr;
	}
}

void FPyObject::_notification(int p_what) {
	switch (p_what) {
		case NOTIFICATION_READY:
			_ready();
			break;
	}
}

void FPyObject::_ready() {
	do {
		if (py_path.is_empty()) {
			break;
		}
		print_line(vformat("load module: %s", py_path));
		PyObject *p_path = PyUnicode_FromString(py_path.utf8().get_data());
		p_module = PyImport_Import(p_path);
		if (!p_module) {
			PyErr_Print();
			break;
		}
		Py_DECREF(p_path);

		if (py_class.is_empty()) {
			break;
		}

		auto dict = PyModule_GetDict(p_module);
		if (!dict) {
			PyErr_Print();
			break;
		}

		auto s_class = py_class.utf8().get_data();
		auto p_class_info = PyDict_GetItemString(dict, s_class);
		if (!p_class_info) {
			PyErr_Print();
			break;
		}
		Py_DECREF(dict);

		if (PyCallable_Check(p_class_info)) {
			p_object = PyObject_CallObject(p_class_info, NULL);
			if (!p_object) {
				PyErr_Print();
				break;
			}
			//print_line("create object ok");
			Py_DECREF(p_class_info);
		} else {
			Py_DECREF(p_class_info);
			break;
		}

		auto ret = PyObject_CallMethod(p_object, "hello", NULL);
		if (ret) {
			Py_DECREF(ret);
		}
			
	} while (0);
		
}

void FPyObject::_bind_methods() {
	ClassDB::bind_method(D_METHOD("set_python_path", "python_path"), &FPyObject::set_python_path);
	ClassDB::bind_method(D_METHOD("get_python_path"), &FPyObject::get_python_path);
	ADD_PROPERTY(PropertyInfo(Variant::STRING, "python_path"), "set_python_path", "get_python_path");

	ClassDB::bind_method(D_METHOD("set_python_class", "py_class"), &FPyObject::set_python_class);
	ClassDB::bind_method(D_METHOD("get_python_class"), &FPyObject::get_python_class);
	ADD_PROPERTY(PropertyInfo(Variant::STRING, "python_class"), "set_python_class", "get_python_class");
}


