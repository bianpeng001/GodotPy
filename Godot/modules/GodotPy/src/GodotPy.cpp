//
// 2023-1-17
//

#include "GodotPy.h"

// impl
#include "core/os/memory.h"
#include "scene/3d/node_3d.h"

#include <Windows.h>
#define PY_SSIZE_T_CLEAN
#include <Python.h>

//------------------------------------------------------------------------------
//
//------------------------------------------------------------------------------

/// <summary>
/// 用来处理python的callback
/// </summary>
class CallableCustomCallback : public CallableCustomMethodPointerBase {
private:
	struct Data {
		Node *p_node;
		PyObject *py_func;
		PyObject *py_args;
	} data;
public:
	CallableCustomCallback(Node *p_node, PyObject *func, PyObject *args) {
		Py_INCREF(func);
		data.p_node = p_node;
		data.py_func = func;
		data.py_args = args;
		_setup((uint32_t *)&data, sizeof(Data));
	}
	virtual ~CallableCustomCallback() {
		if (data.py_func) {
			Py_DECREF(data.py_func);
			data.py_func = NULL;
		}
		if (data.py_args) {
			Py_DECREF(data.py_args);
			data.py_args = NULL;
		}
	}
	virtual ObjectID get_object() const {
		return data.p_node->get_instance_id();
	}
	virtual void call(const Variant **p_arguments, int p_argcount, Variant &r_return_value, Callable::CallError &r_call_error) const {
		// TODO: 这里要解决一下参数，目前没有穿参数
		//print_line("CallableCustomCallback::call");
		PyObject_Call(data.py_func, data.py_args, NULL);
	};
};

// 常量区域
static const char *c_capsule_name = "py_capsule";
static const char *c_node_name = "node";

/// <summary>
/// 用来存一个PyCapsule指针, 在离开场景时要清空
/// </summary>
class FCapsuleObject : public Object {
public:
	PyObject *p_capsule;

	FCapsuleObject(PyObject *a_capsule) :
			p_capsule(a_capsule) {

	}
	virtual ~FCapsuleObject() {
		auto node = reinterpret_cast<Node *>(PyCapsule_GetPointer(p_capsule, c_node_name));
		print_line(vformat("destroy FCapsuleObject: %s(%d) of %s ",
				node->get_name(),
				(uint64_t)this->get_instance_id(),
				node->get_class_name()));

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

		auto ptr = memnew(FCapsuleObject(p_capsule));
		FCapsuleObject::instance_list.push_back(ptr);

		v = ptr;
		p_node->set(c_capsule_name, v);
	}
	auto obj = static_cast<Object *>(v);
	return static_cast<FCapsuleObject *>(obj)->p_capsule;
}
//------------------------------------------------------------------------------
// module function implementation
//------------------------------------------------------------------------------
static PyObject *f_print_line(PyObject *module, PyObject *args) {
	const char *str;
	if (!PyArg_ParseTuple(args, "s", &str)) {
		Py_RETURN_NONE;
	}
	print_line(str);
	Py_RETURN_NONE;
}
static PyObject *f_set_process_input(PyObject *module, PyObject *args) {
	PyObject *node;
	int value;

	if (!PyArg_ParseTuple(args, "Oi", &node, &value)) {
		Py_RETURN_NONE;
	}

	auto p_node = (Node *)PyCapsule_GetPointer(node, c_node_name);
	p_node->set_process_input(value != 0);

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
static PyObject *f_connect_callback(PyObject *callback) {
	Py_RETURN_NONE;
}
static PyObject *f_connect(PyObject *module, PyObject *args) {
	PyObject *node;
	const char *signal;
	PyObject *func;

	do {
		if (!PyArg_ParseTuple(args, "OsO", &node, &signal, &func)) {
			break;
		}
		Py_INCREF(func);

		auto py_args = PyTuple_New(0);

		auto p_node = reinterpret_cast<Node *>(PyCapsule_GetPointer(node, c_node_name));
		auto ccb = memnew(CallableCustomCallback(p_node, func, py_args));
		p_node->connect(signal, Callable(ccb));

	} while (0);
	
	Py_RETURN_NONE;
}
static PyObject* f_find_node(PyObject* module, PyObject* args) {
	const char *path;
	PyObject *node;

	if (!PyArg_ParseTuple(args, "Os", &node, &path)) {
		goto end;
	}

	auto p_node = (Node *)PyCapsule_GetPointer(node, c_node_name);
	Node *result = p_node->get_node(NodePath(path));
	if (!result) {
		goto end;
	}

	PyObject *capsule = get_or_create_capsule(result);
	return capsule;

end:
	Py_RETURN_NONE;
}
static PyObject *f_set_position(PyObject *module, PyObject *args) {
	PyObject *node;
	float x, y, z;

	do {
		if (!PyArg_ParseTuple(args, "Offf", &node, &x, &y, &z)) {
			break;
		}

		auto p_node = (Node *)PyCapsule_GetPointer(node, c_node_name);
		auto p_node3d = dynamic_cast<Node3D *>(p_node);
		if (!p_node3d) {
			break;
		}

		p_node3d->set_position(Vector3(x, y, z));

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_get_position(PyObject *module, PyObject *args) {
	PyObject *node;

	do {
		if (!PyArg_ParseTuple(args, "O", &node)) {
			break;
		}

		auto p_node = (Node *)PyCapsule_GetPointer(node, c_node_name);
		auto p_node3d = dynamic_cast<Node3D *>(p_node);
		if (!p_node3d) {
			break;
		}

		auto p = p_node3d->get_position();

		auto tuple = PyTuple_New(3);
		PyTuple_SetItem(tuple, 0, Py_BuildValue("f", p.x));
		PyTuple_SetItem(tuple, 1, Py_BuildValue("f", p.y));
		PyTuple_SetItem(tuple, 2, Py_BuildValue("f", p.z));
		return tuple;

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_set_rotation(PyObject *module, PyObject *args) {
	PyObject *node;
	float x, y, z;

	do {
		if (!PyArg_ParseTuple(args, "Offf", &node, &x, &y, &z)) {
			break;
		}

		auto p_node = reinterpret_cast<Node *>(PyCapsule_GetPointer(node, c_node_name));
		auto p_node3d = dynamic_cast<Node3D *>(p_node);
		if (!p_node3d) {
			break;
		}

		p_node3d->set_rotation_degrees(Vector3(x, y, z));

	} while (0);
	
	Py_RETURN_NONE;
}
static PyObject *f_get_rotation(PyObject *module, PyObject *args) {
	PyObject *node;

	do {
		if (!PyArg_ParseTuple(args, "O", &node)) {
			break;
		}

		auto p_node = (Node *)PyCapsule_GetPointer(node, c_node_name);
		auto p_node3d = dynamic_cast<Node3D *>(p_node);
		if (!p_node3d) {
			break;
		}

		auto p = p_node3d->get_rotation();

		auto tuple = PyTuple_New(3);
		PyTuple_SetItem(tuple, 0, Py_BuildValue("f", p.x));
		PyTuple_SetItem(tuple, 1, Py_BuildValue("f", p.y));
		PyTuple_SetItem(tuple, 2, Py_BuildValue("f", p.z));
		return tuple;

	} while (0);

	Py_RETURN_NONE;
}
static PyMethodDef GodotPy_methods[] = {
	{ "print_line", f_print_line, METH_VARARGS, NULL },
	{ "find_node", f_find_node, METH_VARARGS, NULL },
	{ "set_process", f_set_process, METH_VARARGS, NULL },
	{ "set_process_input", f_set_process_input, METH_VARARGS, NULL },
	{ "connect", f_connect, METH_VARARGS, NULL },

	{ "set_position", f_set_position, METH_VARARGS, NULL },
	{ "get_position", f_get_position, METH_VARARGS, NULL },
	{ "set_rotation", f_set_rotation, METH_VARARGS, NULL },
	{ "get_rotation", f_get_rotation, METH_VARARGS, NULL },

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

		// 这里是通过环境变量，把当前目录加到路径里面去，具体的逻辑在
		// Modules/getpath.py
		::SetEnvironmentVariableA("PYTHONPATH", ".");

		PyImport_AppendInittab("GodotPy", &PyInit_GodotPy);
		InitPython();
		//Py_Initialize();
		
		PyRun_SimpleString("from GodotPy import print_line;print_line('hello python')\n");
		print_line("init python ok");
	}
}

void FLibPy::Clean() {
	if (!bInit) {
		Py_FinalizeEx();
		bInit = false;
	}
}
void FPyObject::input(const Ref<InputEvent> &p_event) {
	//print_line(vformat("input: %s", p_event->as_text()));
	Ref<InputEventMouseMotion> mm = p_event;
	if (mm.is_valid()) {
		auto pressure = mm->get_pressure();
		auto pos = mm->get_position();
		//print_line(vformat("MouseMotion: %f,%f", pos.x, pos.y));
		auto ret = PyObject_CallMethod(this->p_object, "on_mouse_move", "ff", pos.x, pos.y);
		if (ret) {
			Py_DECREF(ret);
			ret = NULL;
		}
	}

	Ref<InputEventMouseButton> mb = p_event;
	if (mb.is_valid()) {
		int button_index = (int)mb->get_button_index();
		int pressed = mb->is_pressed();
		auto pos = mb->get_position();
		//print_line(vformat("MouseButton: %d %d", button_index, pressed));
		auto ret = PyObject_CallMethod(this->p_object, "on_mouse_button", "iiff",
			button_index, pressed,
			pos.x, pos.y);
		if (ret) {
			Py_DECREF(ret);
			ret = NULL;
		}
	}

	Ref<InputEventKey> k = p_event;
	if (k.is_valid()) {
		auto code = k->get_keycode();
		int pressed = k->is_pressed();
		//print_line(vformat("Key: %d %d", (int)code, pressed));
		auto ret = PyObject_CallMethod(this->p_object, "on_key_pressed", "ii",
			(int)code, pressed);
		if (ret) {
			Py_DECREF(ret);
			ret = NULL;
		}
	}

	//if (p_event->is_action("LeftButton")) {
	//	print_line("LeftButton111");
	//}
}

//------------------------------------------------------------------------------
//
//------------------------------------------------------------------------------
FPyObject::FPyObject() :
		p_module(nullptr), p_object(nullptr), p_capsule(nullptr) {
}

FPyObject::~FPyObject() {
	//if (p_module) {
	//	Py_DECREF(p_module);
	//	p_module = nullptr;
	//}

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

		case NOTIFICATION_ENTER_TREE:
			break;

		case NOTIFICATION_EXIT_TREE:
			_exit_tree();
			break;
	}
}

void FPyObject::_ready() {
	do {
		if (py_path.is_empty()) {
			break;
		}
		print_line(vformat("load module: %s", py_path));
		auto &path_utf8 = py_path.utf8();

		PyObject *p_path = PyUnicode_FromString(path_utf8.get_data());
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
		
		auto &class_utf8 = py_class.utf8();
		auto p_class_info = PyDict_GetItemString(dict, class_utf8.get_data());
		if (!p_class_info) {
			PyErr_Print();
			break;
		}
		Py_DECREF(dict);
		if (!PyCallable_Check(p_class_info)) {
			Py_DECREF(p_class_info);
			break;
		}

		print_line(vformat("create class: %s", py_class));
		p_object = PyObject_CallObject(p_class_info, NULL);
		if (!p_object) {
			PyErr_Print();
			break;
		}
		Py_DECREF(p_class_info);
		Py_INCREF(p_object);

		p_capsule = get_or_create_capsule(this);
		PyObject_SetAttrString(p_object, c_capsule_name, p_capsule);
		Py_INCREF(p_capsule);

		auto ret = PyObject_CallMethod(p_object, "_create", NULL);
		if (ret) {
			Py_DECREF(ret);
			ret = NULL;
		}
	
	} while (0);
		
}

void FPyObject::_process() {
	do {
		if (!p_object) {
			break;
		}

		auto ret = PyObject_CallMethod(p_object, "_process", NULL);
		if (ret) {
			Py_DECREF(ret);
			ret = NULL;
		}
	} while (0);
}

void FPyObject::_exit_tree() {
	// TODO: 暂时放在这里清空
	auto& list = FCapsuleObject::instance_list;
	if (list.size() > 0) {
		for (auto it : list) {
			memdelete(it);
		}
		list.clear();
	}
}

void FPyObject::_bind_methods() {
	ClassDB::bind_method(D_METHOD("set_python_path", "python_path"), &FPyObject::set_python_path);
	ClassDB::bind_method(D_METHOD("get_python_path"), &FPyObject::get_python_path);
	ADD_PROPERTY(PropertyInfo(Variant::STRING, "python_path"), "set_python_path", "get_python_path");

	ClassDB::bind_method(D_METHOD("set_python_class", "py_class"), &FPyObject::set_python_class);
	ClassDB::bind_method(D_METHOD("get_python_class"), &FPyObject::get_python_class);
	ADD_PROPERTY(PropertyInfo(Variant::STRING, "python_class"), "set_python_class", "get_python_class");
}


