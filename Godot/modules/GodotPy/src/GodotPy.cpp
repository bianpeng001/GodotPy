//
// 2023年1月17日
//

#include "GodotPy.h"

// core headers
#include "core/os/os.h"
#include "core/os/memory.h"
#include "core/os/time.h"
#include "core/math/plane.h"

#include "main/performance.h"

// scene headers
#include "scene/animation/animation_player.h"
#include "scene/main/viewport.h"

#include "scene/3d/node_3d.h"
#include "scene/3d/camera_3d.h"
#include "scene/3d/label_3d.h"

#include "scene/2d/node_2d.h"
#include "scene/gui/control.h"
#include "scene/gui/label.h"

#include "scene/resources/packed_scene.h"

// server headers
#include "servers/display_server.h"

// python headers
#include <Windows.h>
#define PY_SSIZE_T_CLEAN
#include <Python.h>

#define GP_DECREF(X) Py_DECREF(X); \
	X = NULL

//------------------------------------------------------------------------------
// 定义一个object的容器，用来表示object，应该是一个弱引用
//------------------------------------------------------------------------------
typedef struct {
	PyObject_HEAD Object *obj;
	ObjectID instance_id;
	// 在python那边实际使用的python对象
	PyObject *wrapped_object;
} PyGDObj;

namespace gdobj {

bool Is_PyGDObj(PyObject *o);
PyGDObj *Cast_PyGDObj(PyObject *o);

template <typename T>
static T *GDObjGetPtr(PyObject *a_obj) {
	ERR_FAIL_COND_V(!Is_PyGDObj(a_obj), NULL);

	auto obj = (PyGDObj *)a_obj;
	return Object::cast_to<T>(obj->obj);
}

static void PyGDObj_dealloc(PyObject *o) {
	ERR_FAIL_COND(!Is_PyGDObj(o));

	// TODO: 这里要清空数据
	print_line("destroy PyGDObj");

	PyObject_Free(o);
}
static PyObject *f_get_type(PyObject *a_self, PyObject *args) {
	int type = 0;

	do {
		PyGDObj *self;
		Object *obj;

		self = (PyGDObj *)a_self;
		if (!self->obj) {
			break;
		}

		if (!ObjectDB::get_instance(self->instance_id)) {
			self->obj = NULL;
			break;
		}

		obj = self->obj;
		auto &class_name = obj->get_class_name();
		print_line(vformat("class_name=%s", class_name));

		static Dictionary ClassTypeDict;
		if (ClassTypeDict.size() == 0) {
			ClassTypeDict[StringName("Label")] = 1;
		}

		auto &value = ClassTypeDict.get(class_name, Variant(0));
		type = (int)value;

	} while (false);

	return PyLong_FromLong((long)type);
}
static PyObject *f_get_wrapped_object(PyObject *a_self, PyObject *args) {
	do {
		PyGDObj *self;

		self = Cast_PyGDObj(a_self);
		if (!self || !self->wrapped_object) {
			break;
		}

		auto obj = self->wrapped_object;
		Py_INCREF(obj);
		return obj;

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_set_wrapped_object(PyObject *a_self, PyObject *args) {
	do {
		PyGDObj *self;
		PyObject *wrapped_object;

		self = Cast_PyGDObj(a_self);
		if (!self) {
			break;
		}
		if (!PyArg_ParseTuple(args, "O", &wrapped_object)) {
			break;
		}

		if (self->wrapped_object) {
			GP_DECREF(self->wrapped_object);
		}

		self->wrapped_object = wrapped_object;
		Py_INCREF(self->wrapped_object);

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_is_valid(PyObject *a_self, PyObject *args) {
	do {
		PyGDObj *self;

		if (!Is_PyGDObj(a_self)) {
			break;
		}

		self = (PyGDObj *)a_self;
		auto obj = ObjectDB::get_instance(self->instance_id);

		if (obj) {
			Py_RETURN_TRUE;
		} else {
			Py_RETURN_FALSE;
		}

	} while (0);

	Py_RETURN_NONE;
}


static PyObject *PyGDObj_repr(PyGDObj *o) {
	auto str = vformat("<GDObj id=%x>", (int64_t)o->instance_id);
	return PyUnicode_FromString(str.utf8());
}
static PyMethodDef PyGDObj_methods[] = {
	{ "get_type", &gdobj::f_get_type, METH_VARARGS, NULL },
	{ "get_wrapped_object", &gdobj::f_get_wrapped_object, METH_VARARGS, NULL },
	{ "set_wrapped_object", &gdobj::f_set_wrapped_object, METH_VARARGS, NULL },
	{ "is_valid", &gdobj::f_is_valid, METH_VARARGS, NULL },
	{ NULL, NULL } /* sentinel */
};

PyTypeObject PyGDObj_Type = {
	PyVarObject_HEAD_INIT(&PyType_Type, 0) "GDObj", /*tp_name*/
	sizeof(PyGDObj), /*tp_basicsize*/
	0, /*tp_itemsize*/
	/* methods */
	&gdobj::PyGDObj_dealloc, /*tp_dealloc*/
	0, /*tp_vectorcall_offset*/
	0, /*tp_getattr*/
	0, /*tp_setattr*/
	0, /*tp_as_async*/
	(reprfunc)&gdobj::PyGDObj_repr, /*tp_repr*/
	0, /*tp_as_number*/
	0, /*tp_as_sequence*/
	0, /*tp_as_mapping*/
	0, /*tp_hash*/
	0, /*tp_call*/
	0, /*tp_str*/
	0, /*tp_getattro*/
	0, /*tp_setattro*/
	0, /*tp_as_buffer*/
	0, /*tp_flags*/
	NULL, /*tp_doc*/

	NULL, /* tp_traverse */
	0, /* tp_clear */
	NULL, /* tp_richcompare */
	0, /* tp_weaklistoffset */
	NULL, /* tp_iter */
	0, /* tp_iternext */
	gdobj::PyGDObj_methods, /* tp_methods */
	NULL, /* tp_members */
};
// 创建一个对obj的弱引用，在python side持有，如果obj在godot里面已经销毁
// 则需要在python这边有能力安全的判断是否 is_null, is_valid, has_data啥的
PyObject *PyGDObj_New(Object *a_obj) {
	PyGDObj *obj;

	obj = PyObject_New(PyGDObj, &PyGDObj_Type);
	if (obj == NULL) {
		return NULL;
	}

	obj->obj = a_obj;
	obj->instance_id = a_obj->get_instance_id();
	obj->wrapped_object = NULL;

	return (PyObject *)obj;
}
static bool Is_PyGDObj(PyObject *o) {
	return Py_IS_TYPE(o, &PyGDObj_Type);
}
static PyGDObj* Cast_PyGDObj(PyObject *o) {
	if (!Py_IS_TYPE(o, &PyGDObj_Type)) {
		return NULL;
	}
	return reinterpret_cast<PyGDObj *>(o);
}
} //namespace gdobj

//------------------------------------------------------------------------------
//
//------------------------------------------------------------------------------

/// <summary>
/// 用来处理python的callback, 这个算是一个扩展点
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
		auto ret = PyObject_Call(data.py_func, args, NULL);

		if (ret) {
			GP_DECREF(ret);
		} else {
			PyErr_Print();
		}
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
	PyObject *py_capsule;

	FCapsuleObject(PyObject *a_capsule) :
			py_capsule(a_capsule) {
		
	}
	virtual ~FCapsuleObject() {
#ifdef XXX
		auto node = reinterpret_cast<Node *>(PyCapsule_GetPointer(py_capsule, c_node_name));
		print_line(vformat("destroy FCapsuleObject: %s(%d) of %s",
				node->get_name(),
				(uint64_t)this->get_instance_id(),
				node->get_class_name()));

		const int refcount = py_capsule->ob_refcnt;
		print_line(vformat("refcount=%d", refcount));
#endif

		if (py_capsule) {
			GP_DECREF(py_capsule);
		}
	}
	PyObject* GetPyObject() {
		return py_capsule;
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
		PyObject *py_capsule = PyCapsule_New(a_node, c_node_name, NULL);

		auto ptr = memnew(FCapsuleObject(py_capsule));
		FCapsuleObject::instance_list.push_back(ptr);

		v = ptr;
		a_node->set(c_capsule_name, v);
	}
	auto obj = static_cast<Object *>(v);
	return static_cast<FCapsuleObject *>(obj)->GetPyObject();
}
// 作为属性，存在对象上面
class FPyGDObjSlot : public Object {
private:
	PyObject *gd_obj;
public:
	FPyGDObjSlot() :
			gd_obj(NULL) {
	}
	virtual ~FPyGDObjSlot() {
		if (gd_obj) {
			GP_DECREF(gd_obj);
		}
	}
public:
	// 记录在字典里面, 缓存object_od -> slot，出场景需要清空
	static Dictionary object_id2gd_obj_dict;
	static PyObject *GetPyGDObj(Object *a_obj) {
		auto v = object_id2gd_obj_dict.get(a_obj->get_instance_id(), Variant());
		if (v.is_null()) {
			auto prop = memnew(FPyGDObjSlot);
			prop->gd_obj = gdobj::PyGDObj_New(a_obj);
			v = prop;
			object_id2gd_obj_dict[a_obj->get_instance_id()] = v;
		}
		return Object::cast_to<FPyGDObjSlot>(v.operator Object *())->gd_obj;
	}
};
Dictionary FPyGDObjSlot::object_id2gd_obj_dict;

//------------------------------------------------------------------------------
// module function implementation
//------------------------------------------------------------------------------
static PyObject *f_print_line(PyObject *module, PyObject *args) {
	const char *s;
	if (!PyArg_ParseTuple(args, "s", &s)) {
		Py_RETURN_NONE;
	}
	//OS::get_singleton()->print("%s", str);
	auto str = String::utf8(s);
	print_line(str);

	Py_RETURN_NONE;
}
static PyObject *f_set_window_size(PyObject *module, PyObject *args) {
	int width, height;
	int x, y;
	if (!PyArg_ParseTuple(args, "iiii", &width, &height, &x, &y)) {
		Py_RETURN_NONE;
	}

	auto server = DisplayServer::get_singleton();
	if (server) {
		server->window_set_size(Size2(width, height));
		server->window_set_position(Point2i(x, y));
	}

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
static PyObject *f_set_physics_process(PyObject *module, PyObject *args) {
	PyObject *a_node;
	int value;

	if (!PyArg_ParseTuple(args, "Oi", &a_node, &value)) {
		Py_RETURN_NONE;
	}

	auto node = (Node *)PyCapsule_GetPointer(a_node, c_node_name);
	node->set_physics_process(value != 0);

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
		const char *a_signal;
		PyObject *callback;

		if (!PyArg_ParseTuple(args, "OsO", &a_node, &a_signal, &callback)) {
			break;
		}

		auto node = GetCapsulePointer<Node>(a_node);
		auto ccb = memnew(CallableCustomCallback(node, callback, NULL));
		node->connect(String::utf8(a_signal), Callable(ccb));

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

		auto obj = get_or_create_capsule(parent_node);
		Py_INCREF(obj);
		return obj;

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_reparent(PyObject *module, PyObject *args) {
	do {
		PyObject *a_node;
		PyObject *a_new_parent;

		if (!PyArg_ParseTuple(args, "OO", &a_node, &a_new_parent)) {
			break;
		}

		auto node = GetCapsulePointer<Node>(a_node);
		auto new_parent = GetCapsulePointer<Node>(a_new_parent);

		if (!node || !new_parent) {
			break;
		}
		node->reparent(new_parent);

		auto node3d = Object::cast_to<Node3D>(node);
		if (!node3d) {
			break;
		}
		node3d->set_position(Vector3(0, 0, 0));
		node3d->set_rotation(Vector3(0, 0, 0));

		//Transform3D tr;
		//node3d->set_transform(tr);

	} while (0);

	Py_RETURN_NONE;
}
// 切场景
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
// 销毁节点
static PyObject *f_destroy(PyObject *module, PyObject *args) {
	do {
		PyObject *a_node;

		if (!PyArg_ParseTuple(args, "O", &a_node)) {
			break;
		}

		auto node = GetCapsulePointer<Node>(a_node);
		if (!node) {
			break;
		}
		node->queue_free();

	} while (0);

	Py_RETURN_NONE;
}
static PyObject* f_find_node(PyObject* module, PyObject* args) {
	do {
		const char *a_path;
		PyObject *a_node;

		if (!PyArg_ParseTuple(args, "Os", &a_node, &a_path)) {
			break;
		}

		Node *node = GetCapsulePointer<Node>(a_node);
		if (!node) {
			break;
		}

		auto result_node = node->get_node(NodePath(String::utf8(a_path)));
		if (!result_node) {
			break;
		}

		PyObject *obj = get_or_create_capsule(result_node);
		Py_INCREF(obj);
		return obj;
	} while (0);
	
	Py_RETURN_NONE;
}
// 这个版本是返回我需要的东西，是版本的升级，
// 原先的只是简单把Capsule返回
static PyObject *f_find_node2(PyObject *module, PyObject *args) {
	do {
		const char *a_path;
		PyObject *a_node;

		if (!PyArg_ParseTuple(args, "Os", &a_node, &a_path)) {
			break;
		}

		Node *node = GetCapsulePointer<Node>(a_node);
		if (!node) {
			break;
		}

		auto result_node = node->get_node(NodePath(String::utf8(a_path)));
		if (!result_node) {
			break;
		}

		PyObject *obj = FPyGDObjSlot::GetPyGDObj(result_node);
		Py_INCREF(obj);
		return obj;

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_get_child_count(PyObject *module, PyObject *args) {
	do
	{
		PyObject *a_node;

		if (!PyArg_ParseTuple(args, "O", &a_node)) {
			break;
		}

		Node *node = GetCapsulePointer<Node>(a_node);
		if (!node) {
			break;
		}

		int child_count = node->get_child_count();
		return Py_BuildValue("i", child_count);

	} while (false);

	Py_RETURN_NONE;
}
static PyObject *f_get_child_at(PyObject *module, PyObject *args) {
	do {
		PyObject *a_node;
		int a_index;

		if (!PyArg_ParseTuple(args, "Oi", &a_node, &a_index)) {
			break;
		}

		Node *node = GetCapsulePointer<Node>(a_node);
		if (!node) {
			break;
		}

		if (a_index >= node->get_child_count()) {
			break;
		}

		auto child_node = node->get_child(a_index);

		PyObject *obj = get_or_create_capsule(child_node);
		Py_INCREF(obj);
		return obj;

	} while (0);

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
static PyObject *f_look_at(PyObject *module, PyObject *args) {
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
static PyObject *f_world_to_local(PyObject *module, PyObject *args) {
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

		auto p = node->to_local(Vector3(x, y, z));
		return Py_BuildValue("(fff)", p.x, p.y, p.z);

	} while (0);

	Py_RETURN_NONE;
}

static PyObject *f_local_to_world(PyObject *module, PyObject *args) {
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

		auto p = node->to_global(Vector3(x, y, z));
		return Py_BuildValue("(fff)", p.x, p.y, p.z);

	} while (0);

	Py_RETURN_NONE;
}
// animation play
static PyObject *f_animation_player_play(PyObject *module, PyObject *args) {
	do {
		PyObject *a_node;
		const char *a_anim_name;

		if (!PyArg_ParseTuple(args, "Os", &a_node, &a_anim_name)) {
			break;
		}

		auto anim_player = GetCapsulePointer<AnimationPlayer>(a_node);
		if (!anim_player) {
			break;
		}
		
		StringName anim_name(String::utf8(a_anim_name));
		anim_player->play(anim_name);

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_animation_player_stop(PyObject *module, PyObject *args) {
	do {
		PyObject *a_node;
		int a_keep_state;

		if (!PyArg_ParseTuple(args, "Os", &a_node, &a_keep_state)) {
			break;
		}

		auto player = GetCapsulePointer<AnimationPlayer>(a_node);
		if (!player) {
			break;
		}
		
		player->stop(a_keep_state != 0);

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_animation_player_set_speed_scale(PyObject *module, PyObject *args) {
	do {
		PyObject *a_node;
		float a_speed;

		if (!PyArg_ParseTuple(args, "Of", &a_node, &a_speed)) {
			break;
		}

		auto anim_player = GetCapsulePointer<AnimationPlayer>(a_node);
		if (!anim_player) {
			break;
		}

		anim_player->set_speed_scale(a_speed);

	} while (0);

	Py_RETURN_NONE;
}
// 屏幕点，投影到地面上的交点，的世界坐标
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
static PyObject *f_world_to_screen(PyObject *module, PyObject *args) {
	do {
		PyObject *a_node;
		float x, y, z;

		if (!PyArg_ParseTuple(args, "Offf", &a_node, &x, &y, &z)) {
			break;
		}

		auto camera = GetCapsulePointer<Camera3D>(a_node);
		if (!camera) {
			break;
		}
		const Vector3 world_pos(x, y, z);
		const auto screen_pos = camera->unproject_position(world_pos);
		
		return Py_BuildValue("(ff)", screen_pos.x, screen_pos.y);

	} while (0);

	Py_RETURN_NONE;
}
static PyObject* f_set_visible_2d(PyObject* module, PyObject* args) {
	do {
		PyObject *a_node;
		int v;

		if (!PyArg_ParseTuple(args, "Oi", &a_node, &v)) {
			break;
		}

		auto node = GetCapsulePointer<CanvasItem>(a_node);
		if (!node) {
			break;
		}

		node->set_visible(v != 0);

	} while (0);
	Py_RETURN_NONE;
}
static PyObject *f_find_control(PyObject *module, PyObject *args) {
	do {
		PyObject *a_node;
		float x, y;

		if (!PyArg_ParseTuple(args, "Off", &a_node, &x, &y)) {
			break;
		}

		auto node = GetCapsulePointer<Node>(a_node);
		if (!node) {
			break;
		}
		auto control = node->get_viewport()->gui_find_control(Point2(x, y));
		if (!control) {
			break;
		}

		auto obj = get_or_create_capsule(control);
		Py_INCREF(obj);
		return obj;

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_set_position_2d(PyObject *module, PyObject *args) {
	do {
		PyObject *a_node;
		float x, y;

		if (!PyArg_ParseTuple(args, "Off", &a_node,
					&x, &y)) {
			break;
		}

		auto node = GetCapsulePointer<Node2D>(a_node);
		if (!node) {
			break;
		}

		node->set_position(Point2(x, y));

	} while (0);
	Py_RETURN_NONE;
}
// raycast一个物体
static PyObject *f_raycast_shape(PyObject *module, PyObject *args) {
	do {
		PyObject *a_node;
		float x, y, z;

		if (!PyArg_ParseTuple(args, "Offf", &a_node,
					&x, &y, &z)) {
			break;
		}

		auto camera = GetCapsulePointer<Camera3D>(a_node);
		Ref<World3D> world = camera->get_world_3d();
		auto space_state = world->get_direct_space_state();

		PhysicsDirectSpaceState3D::RayParameters rp;
		rp.from = camera->get_position();
		rp.to = Vector3(x, y, z);
		rp.exclude.insert(camera->get_pyramid_shape_rid());
		rp.collide_with_areas = true;
		rp.collide_with_bodies = true;
		rp.pick_ray = true;
		rp.collision_mask = 1;

		// TODO: 这个的用法可能有点特殊姿势
		PhysicsDirectSpaceState3D::RayResult rr;
		if (space_state->intersect_ray(rp, rr)) {
			print_line(vformat("hit shape:%d", rr.shape));
		} else {
			print_line("hit nothing");
		}

		// TODO: 还有一个shapecast3d，是用一个shape去碰撞别人
		// space_state->intersect_shape
		
		// 这里的raycast，使用ray去碰撞，能被碰撞的有,area和body
		// (space_state->intersect_ray
		
	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_instantiate(PyObject *module, PyObject *args) {
	do {
		const char *a_path;

		if (!PyArg_ParseTuple(args, "s", &a_path)) {
			break;
		}
		const String &path = String::utf8(a_path);
		Ref<PackedScene> res = ResourceLoader::load(path);
		if (res.is_null()) {
			break;
		}
		auto node = Object::cast_to<Node3D>(res->instantiate(PackedScene::GEN_EDIT_STATE_DISABLED));
			
		auto st = SceneTree::get_singleton();
		auto scene = st->get_current_scene();
		scene->add_child(node);

		PyObject *obj = get_or_create_capsule(node);
		Py_INCREF(obj);
		return obj;

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
// FPyObject节点，获得对应的PyObject对象
static PyObject *f_get_py_object(PyObject *module, PyObject *args) {
	do {
		PyObject *a_node;
		if (!PyArg_ParseTuple(args, "O", &a_node)) {
			break;
		}

		auto node = GetCapsulePointer<FPyObject>(a_node);
		if (!node) {
			break;
		}

		auto obj = node->get_py_object();
		// 这里需要返回，所以得+1
		Py_INCREF(obj);
		return obj;
		
	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_label3d_set_text(PyObject *module, PyObject *args) {
	do {
		PyObject *a_node;
		const char *s;
		if (!PyArg_ParseTuple(args, "Os", &a_node, &s)) {
			break;
		}

		auto label = GetCapsulePointer<Label3D>(a_node);
		if (!label) {
			break;
		}

		auto text = String::utf8(s);
		label->set_text(text);
		
	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_label_set_text(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		const char *s;
		if (!PyArg_ParseTuple(args, "Os", &a_obj, &s)) {
			break;
		}

		if (!gdobj::Is_PyGDObj(a_obj)) {
			break;
		}

		auto label = gdobj::GDObjGetPtr<Label>(a_obj);
		if (!label) {
			break;
		}

		auto text = String::utf8(s);
		label->set_text(text);

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_material_set_albedo_color(PyObject *module, PyObject *args) {
	do {
		PyObject *a_node;
		int surface;
		float r, g, b;

		if (!PyArg_ParseTuple(args, "Oifff", &a_node, &surface, &r, &g, &b)) {
			break;
		}

		auto mesh_instance = GetCapsulePointer<MeshInstance3D>(a_node);
		if (!mesh_instance) {
			break;
		}

		int count = mesh_instance->get_surface_override_material_count();
		//print_line(vformat("material count=%d", count));

		if (surface >= count) {
			break;
		}
		Ref<StandardMaterial3D> mat0 = mesh_instance->get_surface_override_material(surface);
		if (mat0.is_null()) {
			break;
		}

		//mat0->set_albedo(Color(r, g, b));
		Ref<Material> mat = ResourceLoader::load(String("res://models/Flag02FlagGreenMat.tres"));
		mesh_instance->set_surface_override_material(surface, mat);
		
		//Ref<StandardMaterial3D> mat(memnew(StandardMaterial3D));
		//mat->set_albedo(Color(r, g, b));
		//mat->set_transparency(StandardMaterial3D::TRANSPARENCY_DISABLED);
		//mesh_instance->set_surface_override_material(index, mat);
		
	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_mesh_instance3d_load_material(PyObject *module, PyObject *args) {
	do {
		PyObject *a_node;
		int surface;
		const char *a_path;

		if (!PyArg_ParseTuple(args, "Ois", &a_node, &surface, &a_path)) {
			break;
		}

		auto mesh_instance = GetCapsulePointer<MeshInstance3D>(a_node);
		if (!mesh_instance) {
			break;
		}

		int count = mesh_instance->get_surface_override_material_count();
		//print_line(vformat("material count=%d", count));

		if (surface >= count) {
			break;
		}

		String path(a_path);
		Ref<Material> mat = ResourceLoader::load(path);
		mesh_instance->set_surface_override_material(surface, mat);

	} while (0);

	Py_RETURN_NONE;
}

static PyObject *f_debug_get_monitor(PyObject *module, PyObject *args) {
	do {
		int a_monitor;
		if (!PyArg_ParseTuple(args, "i", &a_monitor)) {
			break;
		}

		auto monitor = (Performance::Monitor)a_monitor;
		auto pf = Performance::get_singleton();
		float value = pf->get_monitor(monitor);

		return PyFloat_FromDouble(value);

	} while (0);

	Py_RETURN_NONE;
}
// define godot api
static PyMethodDef GodotPy_methods[] = {
	// os
	{ "print_line", f_print_line, METH_VARARGS, NULL },
	{ "get_time", f_get_time, METH_VARARGS, NULL },
	{ "get_delta_time", f_get_delta_time, METH_VARARGS, NULL },
	{ "set_window_size", f_set_window_size, METH_VARARGS, NULL },

	// node
	{ "find_node", f_find_node, METH_VARARGS, NULL },
	{ "find_node2", f_find_node2, METH_VARARGS, NULL },
	{ "get_child_count", f_get_child_count, METH_VARARGS, NULL },
	{ "get_child_at", f_get_child_at, METH_VARARGS, NULL },
	{ "set_process", f_set_process, METH_VARARGS, NULL },
	{ "set_process_input", f_set_process_input, METH_VARARGS, NULL },
	{ "set_physics_process", f_set_physics_process, METH_VARARGS, NULL },
	{ "connect", f_connect, METH_VARARGS, NULL },
	{ "get_parent", f_get_parent, METH_VARARGS, NULL },
	{ "reparent", f_reparent, METH_VARARGS, NULL },
	{ "load_scene", f_load_scene, METH_VARARGS, NULL },
	{ "destroy", f_destroy, METH_VARARGS, NULL },

	// node3d
	{ "set_position", f_set_position, METH_VARARGS, NULL },
	{ "get_position", f_get_position, METH_VARARGS, NULL },
	{ "set_rotation", f_set_rotation, METH_VARARGS, NULL },
	{ "look_at", f_look_at, METH_VARARGS, NULL },
	{ "get_rotation", f_get_rotation, METH_VARARGS, NULL },
	{ "set_scale", f_set_scale, METH_VARARGS, NULL },
	{ "local_to_world", f_local_to_world, METH_VARARGS, NULL },
	{ "world_to_local", f_world_to_local, METH_VARARGS, NULL },

	// animation player
	{ "animation_player_play", f_animation_player_play, METH_VARARGS, NULL },
	{ "animation_player_stop", f_animation_player_stop, METH_VARARGS, NULL },
	{ "animation_player_set_speed_scale", f_animation_player_set_speed_scale, METH_VARARGS, NULL },

	// node2d
	{ "set_position_2d", f_set_position_2d, METH_VARARGS, NULL },
	{ "set_visible_2d", f_set_visible_2d, METH_VARARGS, NULL },
	{ "find_control", f_find_control, METH_VARARGS, NULL },

	// camera3d
	{ "screen_to_world", f_screen_to_world, METH_VARARGS, NULL },
	{ "world_to_screen", f_world_to_screen, METH_VARARGS, NULL },

	// physics
	{ "raycast_shape", f_raycast_shape, METH_VARARGS, NULL },

	// label3d
	{ "label3d_set_text", f_label3d_set_text, METH_VARARGS, NULL },

	// label
	{ "label_set_text", f_label_set_text, METH_VARARGS, NULL },

	// debug
	{ "debug_get_monitor", f_debug_get_monitor, METH_VARARGS, NULL },

	// mesh instance

	// material
	{ "material_set_albedo_color", f_material_set_albedo_color, METH_VARARGS, NULL },

	// resource
	{ "instantiate", f_instantiate, METH_VARARGS, NULL },
	{ "mesh_instance3d_load_material", f_mesh_instance3d_load_material, METH_VARARGS, NULL }, 

	// godotpy
	{ "get_py_object", f_get_py_object, METH_VARARGS, NULL },

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
		//print_line(vformat("MouseMotion: %d %f,%f", (int)(this->p_object != 0), pos.x, pos.y));
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
		p_module(nullptr),
		p_object(nullptr),
		error_last_process (false) {

}
FPyObject::~FPyObject() {
	if (p_module) {
		GP_DECREF(p_module);
	}

	if (p_object) {
		GP_DECREF(p_object);
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

		case NOTIFICATION_PHYSICS_PROCESS:
			_physics_process();
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

		auto capsule = get_or_create_capsule(this);
		PyObject_SetAttrString(p_object, c_capsule_name, capsule);

		// post create object
		auto ret = PyObject_CallMethod(p_object, "_create", NULL);
		if (ret) {
			GP_DECREF(ret);
		} else {
			PyErr_Print();
		}
		print_line(vformat("create %s ok", py_class));

	} while (0);
}
void FPyObject::_physics_process() {
	do {
		if (!p_object) {
			break;
		}
		if (error_last_process) {
			break;
		}

		auto ret = PyObject_CallMethod(p_object, "_physics_process", NULL);
		if (ret) {
			GP_DECREF(ret);
		} else {
			error_last_process = true;
			PyErr_Print();
			
		}

	} while (0);
}
void FPyObject::_process() {
	do {
		if (!p_object) {
			break;
		}
		if (error_last_process) {
			break;
		}

		auto ret = PyObject_CallMethod(p_object, "_process", NULL);
		if (ret) {
			GP_DECREF(ret);
		} else {
			error_last_process = true;
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


