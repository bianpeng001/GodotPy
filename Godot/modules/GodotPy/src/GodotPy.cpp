//
// 2023-1-17
//

#include "GodotPy.h"

// godot
#include "core/os/os.h"
#include "core/os/memory.h"
#include "core/os/time.h"

#include "core/math/plane.h"

#include "scene/3d/node_3d.h"
#include "scene/3d/camera_3d.h"

#include "scene/resources/packed_scene.h"

// python
#include <Windows.h>
#define PY_SSIZE_T_CLEAN
#include <Python.h>

#define GP_DECREF(X) Py_DECREF(X); \
	X = NULL

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

		if (func) {
			Py_INCREF(func);
		}
		if (args) {
			Py_INCREF(args);
		}
		_setup((uint32_t *)&data, sizeof(Data));
	}
	virtual ~CallableCustomCallback() {
		if (data.py_func) {
			GP_DECREF(data.py_func);
		}
		if (data.py_args) {
			GP_DECREF(data.py_args);
		}
	}
	virtual ObjectID get_object() const override {
		return data.p_node->get_instance_id();
	}
	virtual void call(const Variant **p_arguments, int p_argcount, Variant &r_return_value, Callable::CallError &r_call_error) const override {
		// TODO: 这里要解决一下参数，目前没有传入参数
		auto args = PyTuple_New(0);
		PyObject_Call(data.py_func, args, NULL);
		GP_DECREF(args);
	};
};

// 常量区域
static const char *c_capsule_name = "node_capsule";
static const char *c_node_name = "node";

// 从capsule里面取数据
template <typename T>
static T *GetCapsulePointer(PyObject *capsule) {
	auto node = reinterpret_cast<Node *>(PyCapsule_GetPointer(capsule, c_node_name));
	return Object::cast_to<T>(node);
}

/// <summary>
/// 用来存一个PyCapsule指针, 在离开场景时要清空
/// </summary>
class FCapsuleObject : public Object {
public:
	PyObject *p_node_capsule;

	FCapsuleObject(PyObject *a_capsule) :
			p_node_capsule(a_capsule) {
		
	}
	virtual ~FCapsuleObject() {
		//auto node = reinterpret_cast<Node *>(PyCapsule_GetPointer(p_capsule, c_node_name));
		//print_line(vformat("destroy FCapsuleObject: %s(%d) of %s ",
		//		node->get_name(),
		//		(uint64_t)this->get_instance_id(),
		//		node->get_class_name()));

		if (p_node_capsule) {
			GP_DECREF(p_node_capsule);
		}
	}
	static List<FCapsuleObject *> instance_list;
};
List<FCapsuleObject *> FCapsuleObject::instance_list;

// 创建一个FCapsuleObject，用来存放PyCapsule*，记录了Node，对应的PyObject
// 并存在Node里面，以供后用，
// TODO: 记得销毁
static PyObject* get_or_create_capsule(Node* a_node) {
	auto v = a_node->get(c_capsule_name);
	
	if (v.is_null()) {
		PyObject *node_capsule = PyCapsule_New(a_node, c_node_name, NULL);

		auto ptr = memnew(FCapsuleObject(node_capsule));
		FCapsuleObject::instance_list.push_back(ptr);

		v = ptr;
		a_node->set(c_capsule_name, v);
	}
	auto obj = static_cast<Object *>(v);
	return static_cast<FCapsuleObject *>(obj)->p_node_capsule;
}
//------------------------------------------------------------------------------
// module function implementation
//------------------------------------------------------------------------------
static PyObject *f_print_line(PyObject *module, PyObject *args) {
	const char *str;
	if (!PyArg_ParseTuple(args, "s", &str)) {
		Py_RETURN_NONE;
	}
	//OS::get_singleton()->print("%s", str);
	print_line(str);

	Py_RETURN_NONE;
}
static PyObject *f_set_process_input(PyObject *module, PyObject *args) {
	PyObject *a_node;
	int value;

	if (!PyArg_ParseTuple(args, "Oi", &a_node, &value)) {
		Py_RETURN_NONE;
	}

	auto node = (Node *)PyCapsule_GetPointer(a_node, c_node_name);
	node->set_process_input(value != 0);

	Py_RETURN_NONE;
}
static PyObject *f_set_process(PyObject *module, PyObject *args) {
	PyObject *a_node;
	int value;

	if (!PyArg_ParseTuple(args, "Oi", &a_node, &value)) {
		Py_RETURN_NONE;
	}

	//auto p_node = (Node *)PyCapsule_GetPointer(node, c_node_name);
	auto node = GetCapsulePointer<Node>(a_node);
	node->set_process(value != 0);

	Py_RETURN_NONE;
}
static PyObject *f_connect(PyObject *module, PyObject *args) {
	do {
		PyObject *a_node;
		const char *signal;
		PyObject *callback;

		if (!PyArg_ParseTuple(args, "OsO", &a_node, &signal, &callback)) {
			break;
		}

		auto node = GetCapsulePointer<Node>(a_node);
		auto ccb = memnew(CallableCustomCallback(node, callback, NULL));
		node->connect(signal, Callable(ccb));

	} while (0);
	
	Py_RETURN_NONE;
}
static PyObject *f_get_parent(PyObject *module, PyObject *args) {
	do {
		PyObject *a_node;

		if (!PyArg_ParseTuple(args, "O", &a_node)) {
			break;
		}

		auto node = GetCapsulePointer<Node>(a_node);
		auto parent_node = node->get_parent();
		if (!parent_node) {
			break;
		}

		return get_or_create_capsule(parent_node);

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_load_scene(PyObject *module, PyObject *args) {
	do {
		char *a_path;

		if (!PyArg_ParseTuple(args, "s", &a_path)) {
			break;
		}

		String path(a_path);
		auto st = SceneTree::get_singleton();
		st->change_scene_to_file(path);

	} while (0);

	Py_RETURN_NONE;
}

static PyObject* f_find_node(PyObject* module, PyObject* args) {
	const char *path;
	PyObject *node;

	if (!PyArg_ParseTuple(args, "Os", &node, &path)) {
		goto end;
	}

	Node *result = GetCapsulePointer<Node>(node)->get_node(NodePath(path));
	if (!result) {
		goto end;
	}

	PyObject *capsule = get_or_create_capsule(result);
	return capsule;

end:
	Py_RETURN_NONE;
}
static PyObject *f_set_position(PyObject *module, PyObject *args) {
	
	do {
		PyObject *a_node;
		float x, y, z;

		if (!PyArg_ParseTuple(args, "Offf", &a_node, &x, &y, &z)) {
			break;
		}

		auto node = GetCapsulePointer<Node3D>(a_node);
		if (!node) {
			break;
		}

		node->set_position(Vector3(x, y, z));

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_get_position(PyObject *module, PyObject *args) {
	
	do {
		PyObject *a_node;

		if (!PyArg_ParseTuple(args, "O", &a_node)) {
			break;
		}

		auto node = GetCapsulePointer<Node3D>(a_node);
		if (!node) {
			break;
		}

		auto p = node->get_position();

		//auto tuple = PyTuple_New(3);
		//PyTuple_SetItem(tuple, 0, Py_BuildValue("f", p.x));
		//PyTuple_SetItem(tuple, 1, Py_BuildValue("f", p.y));
		//PyTuple_SetItem(tuple, 2, Py_BuildValue("f", p.z));
		//return tuple;
		return Py_BuildValue("(fff)", p.x, p.y, p.z);

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_set_rotation(PyObject *module, PyObject *args) {
	
	do {
		PyObject *a_node;
		float x, y, z;

		if (!PyArg_ParseTuple(args, "Offf", &a_node, &x, &y, &z)) {
			break;
		}

		auto node = GetCapsulePointer<Node3D>(a_node);
		if (!node) {
			break;
		}

		node->set_rotation_degrees(Vector3(x, y, z));

	} while (0);
	
	Py_RETURN_NONE;
}
static PyObject *f_lookat(PyObject *module, PyObject *args) {
	do {
		PyObject *a_node;
		float x, y, z;

		if (!PyArg_ParseTuple(args, "Offf", &a_node, &x, &y, &z)) {
			break;
		}

		auto node = GetCapsulePointer<Node3D>(a_node);
		if (!node) {
			break;
		}

		//node->set_rotation_degrees(Vector3(x, y, z));
		node->look_at(Vector3(x, y, z), Vector3(0, 1, 0));

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_get_rotation(PyObject *module, PyObject *args) {
	
	do {
		PyObject *a_node;

		if (!PyArg_ParseTuple(args, "O", &a_node)) {
			break;
		}

		auto node = GetCapsulePointer<Node3D>(a_node);
		if (!node) {
			break;
		}

		auto p = node->get_rotation();
		return Py_BuildValue("(fff)", p.x, p.y, p.z);

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_set_scale(PyObject *module, PyObject *args) {
	do {
		PyObject *a_node;
		float x, y, z;

		if (!PyArg_ParseTuple(args, "Offf", &a_node, &x, &y, &z)) {
			break;
		}

		auto node = GetCapsulePointer<Node3D>(a_node);
		if (!node) {
			break;
		}

		node->set_scale(Vector3(x, y, z));

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_screen_to_world(PyObject *module, PyObject *args) {
	do {
		PyObject *a_node;
		float x, y;

		if (!PyArg_ParseTuple(args, "Off", &a_node, &x, &y)) {
			break;
		}

		auto camera = GetCapsulePointer<Camera3D>(a_node);
		if (!camera) {
			break;
		}

		const Vector2 screen_pos(x, y);
		auto ray_origin = camera->project_ray_origin(screen_pos);
		auto ray_normal = camera->project_ray_normal(screen_pos);

		const Plane plane(Vector3(0, 1, 0), 0);
		Vector3 p;
		if (plane.intersects_ray(ray_origin, ray_normal, &p)) {
			return Py_BuildValue("(fff)", p.x, p.y, p.z);
		}
		
	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_instantiate(PyObject *module, PyObject *args) {
	do {
		const char *a_path;

		if (!PyArg_ParseTuple(args, "s", &a_path)) {
			break;
		}
		const String path(a_path);
		Ref<PackedScene> res = ResourceLoader::load(path);
		if (!res.is_null()) {
			auto node = Object::cast_to<Node3D>(res->instantiate(PackedScene::GEN_EDIT_STATE_DISABLED));
			
			auto st = SceneTree::get_singleton();
			auto scene = st->get_current_scene();
			scene->add_child(node);

			PyObject *obj = get_or_create_capsule(node);
			return obj;
		}

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_get_time(PyObject *module, PyObject *args) {
	auto time = (int)Time::get_singleton()->get_ticks_msec();
	return Py_BuildValue("i", time);
}
static PyObject *f_get_delta_time(PyObject *module, PyObject *args) {
	float delta = (float)SceneTree::get_singleton()->get_process_time();
	return Py_BuildValue("f", delta);
}
static PyMethodDef GodotPy_methods[] = {
	// os
	{ "print_line", f_print_line, METH_VARARGS, NULL },
	{ "get_time", f_get_time, METH_VARARGS, NULL },
	{ "get_delta_time", f_get_delta_time, METH_VARARGS, NULL },

	// node
	{ "find_node", f_find_node, METH_VARARGS, NULL },
	{ "set_process", f_set_process, METH_VARARGS, NULL },
	{ "set_process_input", f_set_process_input, METH_VARARGS, NULL },
	{ "connect", f_connect, METH_VARARGS, NULL },
	{ "get_parent", f_get_parent, METH_VARARGS, NULL },
	{ "load_scene", f_load_scene, METH_VARARGS, NULL },

	// node3d
	{ "set_position", f_set_position, METH_VARARGS, NULL },
	{ "get_position", f_get_position, METH_VARARGS, NULL },
	{ "set_rotation", f_set_rotation, METH_VARARGS, NULL },
	{ "lookat", f_lookat, METH_VARARGS, NULL },
	{ "get_rotation", f_get_rotation, METH_VARARGS, NULL },
	{ "set_scale", f_set_scale, METH_VARARGS, NULL },

	// camera3d
	{ "screen_to_world", f_screen_to_world, METH_VARARGS, NULL },
	{ "world_to_screen", f_screen_to_world, METH_VARARGS, NULL },

	// resource
	{ "instantiate", f_instantiate, METH_VARARGS, NULL },

	// over
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
		print_line("init python");

		// 这里是通过环境变量，把当前目录加到路径里面去，具体的逻辑在
		// Modules/getpath.py
		::SetEnvironmentVariableA("PYTHONPATH", ".");

		PyImport_AppendInittab("GodotPy", &PyInit_GodotPy);
		InitPython();
		//Py_Initialize();
		
		PyRun_SimpleString("import game.boot;print('hello godot')\n");
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
			GP_DECREF(ret);
		}
		else {
			PyErr_Print();
		}
		return;
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
			GP_DECREF(ret);
		}
		else {
			PyErr_Print();
		}
		return;
	}

	Ref<InputEventKey> k = p_event;
	if (k.is_valid()) {
		auto code = k->get_keycode();
		int pressed = k->is_pressed();
		//print_line(vformat("Key: %d %d", (int)code, pressed));
		auto ret = PyObject_CallMethod(this->p_object, "on_key_pressed", "ii",
			(int)code, pressed);
		if (ret) {
			GP_DECREF(ret);
		}
		else {
			PyErr_Print();
		}
		return;
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
	if (p_module) {
		GP_DECREF(p_module);
	}

	if (p_object) {
		GP_DECREF(p_object);
	}

	if (p_capsule) {
		GP_DECREF(p_capsule);
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
		const auto &path_utf8 = py_path.utf8();

		PyObject *p_path = PyUnicode_FromString(path_utf8.get_data());
		p_module = PyImport_Import(p_path);
		if (!p_module) {
			PyErr_Print();
			break;
		}
		GP_DECREF(p_path);

		if (py_class.is_empty()) {
			break;
		}

		auto dict = PyModule_GetDict(p_module);
		if (!dict) {
			PyErr_Print();
			break;
		}
		
		const auto &class_utf8 = py_class.utf8();
		auto p_class_info = PyDict_GetItemString(dict, class_utf8.get_data());
		if (!p_class_info) {
			PyErr_Print();
			break;
		}
		if (!PyCallable_Check(p_class_info)) {
			break;
		}

		print_line(vformat("create class: %s", py_class));
		p_object = PyObject_CallObject(p_class_info, NULL);
		if (!p_object) {
			PyErr_Print();
			break;
		}

		p_capsule = get_or_create_capsule(this);
		PyObject_SetAttrString(p_object, c_capsule_name, p_capsule);

		// post create object
		auto ret = PyObject_CallMethod(p_object, "_create", NULL);
		if (ret) {
			GP_DECREF(ret);
		}
		else {
			PyErr_Print();
		}
		print_line(vformat("create %s ok", py_class));

	} while (0);
		
}
void FPyObject::_process() {
	do {
		if (!p_object) {
			break;
		}

		auto ret = PyObject_CallMethod(p_object, "_process", NULL);
		if (ret) {
			GP_DECREF(ret);
		}
		else {
			PyErr_Print();
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
	ClassDB::bind_method(D_METHOD("set_python_path", "python_module"), &FPyObject::set_python_path);
	ClassDB::bind_method(D_METHOD("get_python_path"), &FPyObject::get_python_path);
	ADD_PROPERTY(PropertyInfo(Variant::STRING, "python_module"), "set_python_path", "get_python_path");

	ClassDB::bind_method(D_METHOD("set_python_class", "py_class"), &FPyObject::set_python_class);
	ClassDB::bind_method(D_METHOD("get_python_class"), &FPyObject::get_python_class);
	ADD_PROPERTY(PropertyInfo(Variant::STRING, "python_class"), "set_python_class", "get_python_class");
}


