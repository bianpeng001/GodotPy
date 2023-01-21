//
// 2023-1-17
//

#include "GodotPy.h"

#include <Windows.h>
#define PY_SSIZE_T_CLEAN
#include <Python.h>

static const char *c_capsule_name = "py_capsule";
static const char *c_node_name = "node";

/// <summary>
/// 用来存一个PyCapsule指针
/// </summary>
class FCapsuleObject : public Object {
public:
	PyObject *p_capsule;

	FCapsuleObject(PyObject *a_capsule) :
			p_capsule(a_capsule) {

	}
	virtual ~FCapsuleObject() {
		print_line("desctroy FCapsuleObject");
		if (p_capsule) {
			Py_DECREF(p_capsule);
			p_capsule = nullptr;
		}
	}
	static List<FCapsuleObject *> instance_list;
};
List<FCapsuleObject *> FCapsuleObject::instance_list;

static PyObject* get_or_create_capsule(Node* p_node) {
	auto v = p_node->get(c_capsule_name);
	
	if (!v) {
		PyObject *p_capsule = PyCapsule_New(p_node, c_node_name, NULL);

		auto ptr = new FCapsuleObject(p_capsule);
		FCapsuleObject::instance_list.push_back(ptr);

		v = ptr;
		p_node->set(c_capsule_name, v);
	}
	auto obj = static_cast<Object*>(v);
	return static_cast<FCapsuleObject *>(obj)->p_capsule;
}

static PyObject *f_print_line(PyObject *module, PyObject *args) {
	const char *str;
	if (!PyArg_ParseTuple(args, "s", &str)) {
		Py_RETURN_NONE;
	}
	print_line(str);
	/*
	PyObject *p_obj, *p_str;

	if (!PyArg_ParseTuple(args, "O", &p_obj)) {
		return NULL;
	}

	p_str = PyObject_Str(p_obj);
	*/
	Py_RETURN_NONE;
}
static PyObject *f_set_process(PyObject *module, PyObject *args) {
	PyObject *node;
	int value;

	if (!PyArg_ParseTuple(args, "Oi", &node, &value)) {
		Py_RETURN_NONE;
	}

	auto p_node = (Node *)PyCapsule_GetPointer(node, c_node_name);
	p_node->set_process(value != 0);

	Py_RETURN_NONE;
}
static PyObject *f_connect(PyObject *module, PyObject *args) {
	const char *signal;
	PyObject *callback;

	if (!PyArg_ParseTuple(args, "sO", &signal, &callback)) {
		Py_RETURN_NONE;
	}

	Py_RETURN_NONE;
}
static PyObject* f_find_node(PyObject* module, PyObject* args) {
	const char *path;
	PyObject *node;

	if (!PyArg_ParseTuple(args, "Os", &node, &path)) {
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

	auto p_node = (Node *)PyCapsule_GetPointer(node, c_node_name);
	Node *p_get = p_node->get_node(NodePath(path));

	if (!p_get) {
		goto end;
	}

	auto capsule = get_or_create_capsule(p_get);
	return capsule;

end:
	Py_RETURN_NONE;
}
static PyMethodDef GodotPy_methods[] = {
	{ "print_line", f_print_line, METH_VARARGS, NULL },
	{ "find_node", f_find_node, METH_VARARGS, NULL },
	{ "set_process", f_set_process, METH_VARARGS, NULL },
	{ "connect", f_connect, METH_VARARGS, NULL },
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
	// 一般来说嵌入， 需要 isolated=1, 会无视一些参数，包括环境变量
	// 但是我目前的当前目录加到sys.path，这个步骤需要依赖环境变量，
	// 所以目前还没有想到更好的办法，保持isolated = 0
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
		p_module(nullptr), p_object(nullptr), p_capsule(nullptr) {
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

	if (p_capsule) {
		Py_DECREF(p_capsule);
		p_capsule = nullptr;
	}
}

void FPyObject::_notification(int p_what) {
	if (Engine::get_singleton()->is_editor_hint()) {
		return;
	}

	switch (p_what) {
		case NOTIFICATION_READY:
			_ready();
			break;

		case NOTIFICATION_PROCESS:
			_process();
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
			p_capsule = get_or_create_capsule(this);
			PyObject_SetAttrString(p_object, c_capsule_name, p_capsule);

			PyObject_CallMethod(p_object, "post_create", NULL);

			//print_line("create object ok");
			Py_DECREF(p_class_info);
		} else {
			Py_DECREF(p_class_info);
			break;
		}

		//this->set_process(true);
		//auto ret = PyObject_CallMethod(p_object, "hello", NULL);
		//if (ret) {
		//	Py_DECREF(ret);
		//}
			
	} while (0);
		
}

void FPyObject::_process() {
	do {
		if (!p_object) {
			break;
		}

		auto ret = PyObject_CallMethod(p_object, "process", NULL);
		if (ret) {
			Py_DECREF(ret);
			ret = NULL;
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


