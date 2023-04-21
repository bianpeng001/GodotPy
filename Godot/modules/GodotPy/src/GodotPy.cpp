//
// 2023年1月17日
//

// TODO: 还要处理Resource继承下来的对象，是资源，而不是Object

// TODO：最佳的释放的机会在, SceneTree::_flush_delete_queue
// 这是真正调用memdelete(obj)的地方，因为全部扫描，肯定是不合适的
// 还有一个机会就是queue_delete的地方

#include "GodotPy.h"

// core headers
#include "core/os/os.h"
#include "core/os/memory.h"
#include "core/os/time.h"
#include "core/input/input.h"
#include "core/math/plane.h"
#include "core/math/transform_3d.h"

#include "main/performance.h"

// scene headers
#include "scene/animation/animation_player.h"
#include "scene/main/viewport.h"

#include "scene/3d/node_3d.h"
#include "scene/3d/camera_3d.h"
#include "scene/3d/label_3d.h"
#include "scene/3d/cpu_particles_3d.h"

#include "scene/2d/node_2d.h"

#include "scene/gui/control.h"
#include "scene/gui/base_button.h"
#include "scene/gui/button.h"
#include "scene/gui/label.h"
#include "scene/gui/rich_text_label.h"
#include "scene/gui/tab_bar.h"
#include "scene/gui/check_box.h"
#include "scene/gui/slider.h"
#include "scene/gui/color_rect.h"
#include "scene/gui/texture_rect.h"
#include "scene/gui/text_edit.h"

#include "scene/resources/packed_scene.h"
#include "scene/resources/surface_tool.h"
#include "scene/resources/material.h"
#include "scene/resources/mesh.h"
#include "scene/resources/primitive_meshes.h"
#include "scene/resources/immediate_mesh.h"

// server headers
#include "servers/display_server.h"


//#define MEM_LOG

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

bool Is_GDObj(PyObject *o);
PyGDObj *Cast_PyGDObj(PyObject *o);

template <typename T>
static T *PyGDObj_GetPtr(PyObject *a_obj) {
	ERR_FAIL_COND_V(!Is_GDObj(a_obj), NULL);

	auto obj = (PyGDObj *)a_obj;
	return Object::cast_to<T>(obj->obj);
}
static void PyGDObj_dealloc(PyObject *o) {
	ERR_FAIL_COND(!Is_GDObj(o));

	// TODO: 这里要清空数据
	//print_line("destroy PyGDObj");

	PyObject_Free(o);
}
// 获取映射后的类型, 用于在python端, 支持一下不同类型下面的不同方法
static PyObject *f_get_type(PyObject *a_self, PyObject *args) {
	int type = 0;
	static Dictionary ClassTypeDict;
	static int next_type_id = 0;

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
		//print_line(vformat("class_name=%s", class_name));

		// 命中,说明类型id分配过了
		type = (int)ClassTypeDict.get(class_name, Variant(0));
		if (type != 0) {
			break;
		}

		// 改成在python里面去自行映射,这里指记录一个 class_name -> type_id
		PyObject *reg_type_cb;
		if (!PyArg_ParseTuple(args, "O", &reg_type_cb)) {
			break;
		}

		type = ++next_type_id;
		ClassTypeDict[class_name] = type;

		do {
			auto args = PyTuple_New(2);
			PyTuple_SetItem(args, 0, PyUnicode_FromString(class_name.operator String().utf8()));
			PyTuple_SetItem(args, 1, PyLong_FromLong(type));
			auto ret = PyObject_Call(reg_type_cb, args, NULL);
			if (ret) {
				GP_DECREF(ret);
			} else {
				PyErr_Print();
			}
			GP_DECREF(args);

		} while (0);

	} while (false);

	return PyLong_FromLong((long)type);
}
static PyObject *f_get_type_name(PyObject *a_self, PyObject *args) {
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
		const auto &class_name = obj->get_class_name();

		return PyUnicode_FromString(class_name.operator String().utf8());

	} while (0);

	Py_RETURN_NONE;
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

		if (!Is_GDObj(a_self)) {
			break;
		}

		self = (PyGDObj *)a_self;
		
		Object *obj = NULL;
		if (self->instance_id.is_valid()) {
			obj = ObjectDB::get_instance(self->instance_id);	
		}
		return PyBool_FromLong(obj != NULL);

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *PyGDObj_repr(PyGDObj *o) {
	auto str = vformat("<GDObj id=%x>", (int64_t)o->instance_id);
	return PyUnicode_FromString(str.utf8());
}
static PyMethodDef PyGDObj_methods[] = {
	{ "get_type", &gdobj::f_get_type, METH_VARARGS, NULL },
	{ "get_type_name", &f_get_type_name, METH_VARARGS, NULL },
	{ "get_wrapped_object", &gdobj::f_get_wrapped_object, METH_VARARGS, NULL },
	{ "set_wrapped_object", &gdobj::f_set_wrapped_object, METH_VARARGS, NULL },
	{ "is_valid", &f_is_valid, METH_VARARGS, NULL },

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

	//print_line("new PyGDObj");

	obj->obj = a_obj;
	obj->instance_id = a_obj->get_instance_id();
	obj->wrapped_object = NULL;

	return (PyObject *)obj;
}
static bool Is_GDObj(PyObject *o) {
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

// 常量区域
static const char *c_gdobj_name = "_gdobj";

// 这是一个兼容的写法
template<typename T>
inline T *GetObjPtr(PyObject *o) {
	if (gdobj::Is_GDObj(o)) {
		return gdobj::PyGDObj_GetPtr<T>(o);
	}

	//print_line("GetObjPtr: input obj is not supported, %s");
	print_line(vformat("GetObjPtr: %s not supported", o->ob_type->tp_name));
	return nullptr;
}
//------------------------------------------------------------------------------
// 作为属性，存在对象上面。
// TODO: 后面改成std的dict，这里是因为原本想存在Object::set,get里面，只支持Variant，
// 所以做了一个Slot来接数据
//------------------------------------------------------------------------------
class FGDObjSlot : public Object {
private:
	PyObject *gd_obj;
public:
	FGDObjSlot() :
			gd_obj(NULL) {
	}
	virtual ~FGDObjSlot() {
		if (gd_obj) {
			// 把wrapped_object释放掉，这样wrapped_object对gd_obj的引用就解开了
			auto o = gdobj::Cast_PyGDObj(gd_obj);
			if (o->wrapped_object) {
#ifdef MEM_LOG
				// 超过1说明被持有，1的话说明是一个临时变量
				if (o->wrapped_object->ob_refcnt > 1 || gd_obj->ob_refcnt > 2) {
					print_line(vformat("FGDObjSlot: wrapped_obj refcnt=%d type=%s, gd_obj refcnt=%d",
							o->wrapped_object->ob_refcnt,
							o->wrapped_object->ob_type->tp_name,
							gd_obj->ob_refcnt
						));

					// 打印一下节点的路径，确认下是否需要持有
					auto p_node = Object::cast_to<Node>(o->obj);
					if (p_node) {
						// 这时候已经从scene_tree中删除，得不到路径了
						//auto& path = p_node->get_path();

						print_line(vformat("FGDObjSlot: node_obj name=%s", p_node->get_name()));
					}
				}
#endif

				
				GP_DECREF(o->wrapped_object);
			}

#ifdef MEM_LOG
			// gd_obj->ob_type->tp_name 都是GDObj
			if (gd_obj->ob_refcnt > 1) {
				print_line(vformat("FGDObjSlot: gd_obj refcnt=%d", gd_obj->ob_refcnt));
			}
#endif

			o->obj = NULL;
			o->instance_id = ObjectID();

			GP_DECREF(gd_obj);
		}
	}
public:
	// 记录在字典里面, 缓存object_od -> slot，出场景需要清空
	static Dictionary object_id2gd_obj_dict;
	static PyObject *GetGDObj(Object *a_obj) {
		auto v = object_id2gd_obj_dict.get(a_obj->get_instance_id(), Variant());
		if (v.is_null()) {
			auto prop = memnew(FGDObjSlot);
			prop->gd_obj = gdobj::PyGDObj_New(a_obj);
			v = prop;
			object_id2gd_obj_dict[a_obj->get_instance_id()] = v;
		}
		return Object::cast_to<FGDObjSlot>(v.operator Object *())->gd_obj;
	}
	static void DelGDObj(Object *a_obj) {
		const auto& instance_id = a_obj->get_instance_id();
		if (object_id2gd_obj_dict.has(instance_id)) {
			auto v = object_id2gd_obj_dict.get(instance_id, Variant());
			object_id2gd_obj_dict.erase(instance_id);
			if (!v.is_null()) {
				auto slot = Object::cast_to<FGDObjSlot>(v.operator Object *());
				memdelete(slot);
			}
#ifdef MEM_LOG
			// 根据这个日志表明，至少这里是清空了的
			int slot_count = object_id2gd_obj_dict.size();
			if (slot_count < 10) {
				print_line(vformat("gdobj slot_count=%d", slot_count));
			}
#endif
		}
	}
	static void Clear() {
		if (object_id2gd_obj_dict.size() > 0) {
			auto &values = object_id2gd_obj_dict.values();
			for (int i = 0; i < values.size(); ++i) {
				auto v = values[i];
				auto slot = Object::cast_to<FGDObjSlot>((Object *)v);
				memdelete(slot);
			}
			object_id2gd_obj_dict.clear();
		}
	}
};
Dictionary FGDObjSlot::object_id2gd_obj_dict;

// 在node.cpp里面调用
void delete_gdobj(Node* p_node) {
	FGDObjSlot::DelGDObj(p_node);
}

//------------------------------------------------------------------------------
// 有些数据做一个类型没必要，仍旧放到capsule里面，挺方便的
//------------------------------------------------------------------------------
static const char c_Transform3D[] = "Transform3D";
static const char c_Quaternion[] = "Quaternion";
static const char c_InputEvent[] = "InputEvent";
static const char c_Resource[] = "Resource";
static const char c_SurfaceTool[] = "SurfaceTool";

template <const char* pointer_name, typename T>
void _capsule_delete_pointer(PyObject *obj) {
	//print_line(vformat("delete %s", String(pointer_name)));
	//auto ptr = reinterpret_cast<T *>(PyCapsule_GetPointer(obj, pointer_name));
	auto ptr = _capsule_get_pointer<pointer_name, T>(obj);
	memdelete<T>(ptr);
}
template <const char* pointer_name, typename T>
inline T* _capsule_get_pointer(PyObject* obj) {
	auto ptr = reinterpret_cast<T *>(PyCapsule_GetPointer(obj, pointer_name));
	return ptr;
}

//------------------------------------------------------------------------------
// 用来处理python的callback, 这个算是一个扩展点
//------------------------------------------------------------------------------
class CallableCustomCallback : public CallableCustomMethodPointerBase {
private:
	struct Data {
		Node *p_node;
		PyObject *py_func;
		PyObject *py_args;
	} data;
	static PyObject *InitArguments(const Variant **p_arguments, int p_argcount) {
		//return PyTuple_New(0);

		// 这里要把参数，填进去
		PyObject *obj = PyTuple_New(p_argcount);
		for (int i = 0; i < p_argcount; ++i) {
			auto &arg = *p_arguments[i];
			PyObject *value = NULL;
			switch (arg.get_type()) {
				case Variant::BOOL:
					value = PyBool_FromLong((bool)arg);
					break;
				case Variant::INT:
					value = PyLong_FromLong((int)arg);
					break;
				case Variant::FLOAT:
					value = PyFloat_FromDouble((double)arg);
					break;
				case Variant::STRING:
					do {
						auto &s = (String)arg;
						value = PyUnicode_FromString(s.utf8());

					} while (0);
					break;
				case Variant::VECTOR3:
					do {
						PyObject *f;

						auto v = (Vector3)arg;
						value = PyTuple_New(3);

						f = PyFloat_FromDouble(v.x);
						PyTuple_SetItem(value, 0, f);

						f = PyFloat_FromDouble(v.y);
						PyTuple_SetItem(value, 1, f);

						f = PyFloat_FromDouble(v.z);
						PyTuple_SetItem(value, 2, f);

					} while (0);
					break;
				case Variant::COLOR:
					do {
						PyObject *f;

						auto v = (Color)arg;
						value = PyTuple_New(3);

						f = PyFloat_FromDouble(v.r);
						PyTuple_SetItem(value, 0, f);

						f = PyFloat_FromDouble(v.g);
						PyTuple_SetItem(value, 1, f);

						f = PyFloat_FromDouble(v.b);
						PyTuple_SetItem(value, 2, f);

					} while (0);
					break;
				case Variant::TRANSFORM3D:
					do {
						auto p_transform = memnew(Transform3D((Transform3D)arg));

						value = PyCapsule_New(p_transform, c_Transform3D,
								&_capsule_delete_pointer<c_Transform3D, Transform3D>);
					} while (0);

					break;
				case Variant::QUATERNION:
					do {
						auto p_quat = memnew(Quaternion((Quaternion)arg));

						value = PyCapsule_New(p_quat, c_Quaternion,
								&_capsule_delete_pointer<c_Quaternion, Quaternion>);
					} while (0);

					break;
				case Variant::OBJECT: {
					auto obj = (Object *)arg;
					do {
						// TODO: InputEvent以后应该还有更多的数据要放出来
						auto input_event = Object::cast_to<InputEvent>(obj);
						if (input_event) {
							value = PyBool_FromLong(input_event->is_pressed());
							break;
						}

						// TODO:

						auto node = Object::cast_to<Node>(obj);
						if (node) {
							value = FGDObjSlot::GetGDObj(node);
							Py_INCREF(value);
							break;
						}

					} while (0);

					break;
				}
			}
			if (!value) {
				value = Py_NewRef(Py_None);
			}
			PyTuple_SetItem(obj, i, value);
			//GP_DECREF(value);
		}
		return obj;
	}

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

		auto args = InitArguments(p_arguments, p_argcount);
		auto ret = PyObject_Call(data.py_func, args, NULL);

		if (ret) {
			GP_DECREF(ret);
		} else {
			PyErr_Print();
		}
		GP_DECREF(args);
	};
};

// 记录一下资源的类型
enum class EResType {
	None,
	Material,
	Texture,
};
//
// 一个存Res的包装, 后面得改善下这个接口, 用么也不是不能用...
//
struct ResCapsule {
	int type;
	Ref<Resource> res;

	template <typename T>
	Ref<T> As() {
		return Res<T>(this->res);
	}
};
static inline ResCapsule *GetResCapsule(PyObject *obj) {
	//return reinterpret_cast<ResCapsule *>(PyCapsule_GetPointer(capsule, c_Resource));
	return _capsule_get_pointer<c_Resource, ResCapsule>(obj);
}

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
static PyObject *f_set_window_rect(PyObject *module, PyObject *args) {
	int x, y;
	int width, height;

	if (!PyArg_ParseTuple(args, "iiii", &x, &y, &width, &height)) {
		Py_RETURN_NONE;
	}

	auto server = DisplayServer::get_singleton();
	if (server) {
		server->window_set_position(Point2i(x, y));
		server->window_set_size(Size2(width, height));
	}

	Py_RETURN_NONE;
}
static PyObject *f_get_window_size(PyObject *module, PyObject *args) {
	auto server = DisplayServer::get_singleton();
	if (server) {
		auto size = server->window_get_size();
		return Py_BuildValue("(ii)", size.width, size.height);
	}

	Py_RETURN_NONE;
}
static PyObject *f_window_set_title(PyObject *module, PyObject *args) {
	do {
		const char *a_title;
		if (!PyArg_ParseTuple(args, "s", &a_title)) {
			break;
		}
		auto server = DisplayServer::get_singleton();
		if (server) {
			auto title = String::utf8(a_title);
			server->window_set_title(title);
		}

	} while (0);
	
	Py_RETURN_NONE;
}
static PyObject *f_viewport_get_size(PyObject *module, PyObject *args) {
	do {
		auto st = SceneTree::get_singleton();
		auto root = st->get_current_scene();
		auto viewport = root->get_viewport();
		auto rect = viewport->get_visible_rect();
		return Py_BuildValue("(ff)", rect.size.width, rect.size.height);

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_get_scene_root(PyObject *module, PyObject *args) {
	do {
		auto st = SceneTree::get_singleton();
		auto root = st->get_current_scene();

		PyObject *root_obj = FGDObjSlot::GetGDObj(root);
		Py_INCREF(root_obj);
		return root_obj;

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_is_editor_hint(PyObject *module, PyObject *args) {
	auto value = Engine::get_singleton()->is_editor_hint();
	return PyBool_FromLong(value);
}
static PyObject *f_set_custom_mouse_cursor(PyObject *module, PyObject *args) {
	do {
		PyObject *p_cursor;
		int shape, x, y;
		if (!PyArg_ParseTuple(args, "Oiii", &p_cursor,&shape,&x,&y)) {
			break;
		}
		const auto input = Input::get_singleton();
		if (Py_IsNone(p_cursor)) {
			input->set_custom_mouse_cursor(Ref<Resource>(), (Input::CursorShape)shape, Vector2(x, y));
		} else {
			auto p_res = GetResCapsule(p_cursor);
			input->set_custom_mouse_cursor(p_res->res, (Input::CursorShape)shape, Vector2(x, y));
		}
		

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_set_process_input(PyObject *module, PyObject *args) {
	PyObject *a_obj;
	int value;

	if (!PyArg_ParseTuple(args, "Oi", &a_obj, &value)) {
		Py_RETURN_NONE;
	}

	auto node = GetObjPtr<Node>(a_obj);
	if (!node) {
		goto end;
	}
	node->set_process_input(value != 0);

end:
	Py_RETURN_NONE;
}
static PyObject *f_set_physics_process(PyObject *module, PyObject *args) {
	PyObject *a_obj;
	int value;

	if (!PyArg_ParseTuple(args, "Oi", &a_obj, &value)) {
		Py_RETURN_NONE;
	}

	auto node = GetObjPtr<Node>(a_obj);
	if (!node) {
		goto end;
	}
	node->set_physics_process(value != 0);

end:
	Py_RETURN_NONE;
}
static PyObject *f_set_process(PyObject *module, PyObject *args) {
	PyObject *a_obj;
	int value;

	if (!PyArg_ParseTuple(args, "Oi", &a_obj, &value)) {
		Py_RETURN_NONE;
	}

	auto node = GetObjPtr<Node>(a_obj);
	node->set_process(value != 0);

	Py_RETURN_NONE;
}
static PyObject *f_node_connect(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		const char *a_signal;
		PyObject *callback;

		if (!PyArg_ParseTuple(args, "OsO", &a_obj, &a_signal, &callback)) {
			break;
		}

		auto node = GetObjPtr<Node>(a_obj);
		auto ccb = memnew(CallableCustomCallback(node, callback, NULL));
		node->connect(String::utf8(a_signal), Callable(ccb));

	} while (0);
	
	Py_RETURN_NONE;
}
static PyObject *f_node_disconnect(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		const char *a_signal;
		PyObject *callback;

		if (!PyArg_ParseTuple(args, "OsO", &a_obj, &a_signal, &callback)) {
			break;
		}

		auto node = GetObjPtr<Node>(a_obj);
		//auto ccb = memnew(CallableCustomCallback(node, callback, NULL));
		//node->connect(String::utf8(a_signal), Callable(ccb));

		// TODO:
		//node->disconnect(String::utf8(a_signal), );

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_node_clear_connection(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		const char *a_signal;

		if (!PyArg_ParseTuple(args, "Os", &a_obj, &a_signal)) {
			break;
		}

		auto node = GetObjPtr<Node>(a_obj);

		StringName signal(a_signal);
		List<Object::Connection> conn_list;
		node->get_signal_connection_list(signal, &conn_list);
		for (int i = 0; i < conn_list.size(); ++i) {
			auto conn = conn_list[i];
			auto c = conn.callable;

			node->disconnect(signal, c);
		}

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_node_set_name(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		const char *a_name;

		if (!PyArg_ParseTuple(args, "Os", &a_obj, &a_name)) {
			break;
		}

		auto node = GetObjPtr<Node>(a_obj);
		node->set_name(String::utf8(a_name));
	} while (0);

	Py_RETURN_NONE;
}
//
static PyObject *f_get_parent(PyObject *module, PyObject *args) {
	do {
		PyObject *a_node;

		if (!PyArg_ParseTuple(args, "O", &a_node)) {
			break;
		}

		auto node = GetObjPtr<Node>(a_node);
		auto parent_node = node->get_parent();
		if (!parent_node) {
			break;
		}

		PyObject *obj = FGDObjSlot::GetGDObj(parent_node);
		Py_INCREF(obj);
		return obj;

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_reparent(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		PyObject *a_new_parent;

		if (!PyArg_ParseTuple(args, "OO", &a_obj, &a_new_parent)) {
			break;
		}

		Node *obj = GetObjPtr<Node>(a_obj);
		Node *new_parent = GetObjPtr<Node>(a_new_parent);
		
		if (!obj || !new_parent) {
			break;
		}
		obj->reparent(new_parent);

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_node_set_last(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;

		if (!PyArg_ParseTuple(args, "O", &a_obj)) {
			break;
		}

		Node *obj = GetObjPtr<Node>(a_obj);
		if (!obj) {
			break;
		}
		auto p = obj->get_parent();
		if (p) {
			p->move_child(obj, p->get_child_count() - 1);
		}

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_node_dup(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;

		if (!PyArg_ParseTuple(args, "O", &a_obj)) {
			break;
		}

		Node *obj = GetObjPtr<Node>(a_obj);

		if (!obj) {
			break;
		}

		auto dup = obj->duplicate();
		//obj->add_sibling(dup);
		auto parent = obj->get_parent();
		parent->add_child(dup);

		PyObject *dup_obj = FGDObjSlot::GetGDObj(dup);
		Py_INCREF(dup_obj);
		return dup_obj;

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
// 这里是主动调用destroy，则主动在python端解开对gdobj的引用
static PyObject *f_destroy(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;

		if (!PyArg_ParseTuple(args, "O", &a_obj)) {
			break;
		}

		Node *node = GetObjPtr<Node>(a_obj);
		if (!node) {
			break;
		}

		// 移到 predelete_handler(Object *p_object) 里面，保证每一个Node删除的时候，都会走这里
		//notify_delete_gdobj_if_exists(node);
		node->queue_free();

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_node3d_set_visible(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		int a_value;

		if (!PyArg_ParseTuple(args, "Oi", &a_obj, &a_value)) {
			break;
		}

		Node3D *node = GetObjPtr<Node3D>(a_obj);
		if (!node) {
			break;
		}
		node->set_visible(a_value != 0);

	} while (0);

	Py_RETURN_NONE;
}

// 这个版本是返回我需要的东西，是版本的升级，
// 原先的只是简单把Capsule返回
static PyObject *f_find_node(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		const char *a_path;

		if (!PyArg_ParseTuple(args, "Os", &a_obj, &a_path)) {
			break;
		}

		Node *node = GetObjPtr<Node>(a_obj);
		if (!node) {
			break;
		}

		auto result_node = node->get_node(NodePath(String::utf8(a_path)));
		if (!result_node) {
			break;
		}

		PyObject *obj = FGDObjSlot::GetGDObj(result_node);
		Py_INCREF(obj);
		return obj;

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_get_child_count(PyObject *module, PyObject *args) {
	do
	{
		PyObject *a_obj;

		if (!PyArg_ParseTuple(args, "O", &a_obj)) {
			break;
		}

		Node *node = GetObjPtr<Node>(a_obj);
		if (!node) {
			break;
		}

		int child_count = node->get_child_count();
		//return Py_BuildValue("i", child_count);
		return PyLong_FromLong(child_count);

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

		Node *node = GetObjPtr<Node>(a_node);
		if (!node) {
			break;
		}

		if (a_index >= node->get_child_count()) {
			break;
		}

		auto child_node = node->get_child(a_index);
		if (!child_node) {
			break;
		}

		PyObject *obj = FGDObjSlot::GetGDObj(child_node);
		Py_INCREF(obj);
		return obj;

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_set_position(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		float x, y, z;

		if (!PyArg_ParseTuple(args, "Offf", &a_obj, &x, &y, &z)) {
			break;
		}

		Node3D *node = GetObjPtr<Node3D>(a_obj);
		if (!node) {
			break;
		}

		node->set_position(Vector3(x, y, z));

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_get_position(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;

		if (!PyArg_ParseTuple(args, "O", &a_obj)) {
			break;
		}

		Node3D *node = GetObjPtr<Node3D>(a_obj);
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
		PyObject *a_obj;
		float x, y, z;

		if (!PyArg_ParseTuple(args, "Offf", &a_obj, &x, &y, &z)) {
			break;
		}

		Node3D *node = GetObjPtr<Node3D>(a_obj);
		if (!node) {
			break;
		}

		node->set_rotation_degrees(Vector3(x, y, z));

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_look_at(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		float x, y, z;

		if (!PyArg_ParseTuple(args, "Offf", &a_obj, &x, &y, &z)) {
			break;
		}

		Node3D *node = GetObjPtr<Node3D>(a_obj);
		if (!node) {
			break;
		}
		node->look_at(Vector3(x, y, z), Vector3(0, 1, 0));

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_local_look_at(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		float x, y, z;

		if (!PyArg_ParseTuple(args, "Offf", &a_obj, &x, &y, &z)) {
			break;
		}

		Node3D *node = GetObjPtr<Node3D>(a_obj);
		if (!node) {
			break;
		}
		//auto transform = node->get_transform();
		Transform3D transform;
		// TODO:
		//transform.set_look_at();
		node->set_transform(transform);

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_get_forward(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;

		if (!PyArg_ParseTuple(args, "O", &a_obj)) {
			break;
		}

		Node3D *node = GetObjPtr<Node3D>(a_obj);
		if (!node) {
			break;
		}
		auto p = node->get_global_transform().xform(Vector3(0, 0, -1));
		p -= node->get_position();
		return Py_BuildValue("(fff)", p.x, p.y, p.z);

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_get_rotation(PyObject *module, PyObject *args) {
	
	do {
		PyObject *a_obj;

		if (!PyArg_ParseTuple(args, "O", &a_obj)) {
			break;
		}

		Node3D *node = GetObjPtr<Node3D>(a_obj);
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
		PyObject *a_obj;
		float x, y, z;

		if (!PyArg_ParseTuple(args, "Offf", &a_obj, &x, &y, &z)) {
			break;
		}

		Node3D *node = GetObjPtr<Node3D>(a_obj);
		if (!node) {
			break;
		}

		node->set_scale(Vector3(x, y, z));

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_world_to_local(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		float x, y, z;

		if (!PyArg_ParseTuple(args, "Offf", &a_obj, &x, &y, &z)) {
			break;
		}

		Node3D *node = GetObjPtr<Node3D>(a_obj);
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
		PyObject *a_obj;
		float x, y, z;

		if (!PyArg_ParseTuple(args, "Offf", &a_obj, &x, &y, &z)) {
			break;
		}

		Node3D *node = GetObjPtr<Node3D>(a_obj);
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
		PyObject *a_obj;
		const char *a_anim_name;

		if (!PyArg_ParseTuple(args, "Os", &a_obj, &a_anim_name)) {
			break;
		}

		AnimationPlayer *anim_player = GetObjPtr<AnimationPlayer>(a_obj);
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
		PyObject *a_obj;
		int a_keep_state;

		if (!PyArg_ParseTuple(args, "Os", &a_obj, &a_keep_state)) {
			break;
		}

		AnimationPlayer *anim_player = GetObjPtr<AnimationPlayer>(a_obj);
		if (!anim_player) {
			break;
		}
		
		anim_player->stop(a_keep_state != 0);

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_animation_player_set_speed_scale(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		float a_speed;

		if (!PyArg_ParseTuple(args, "Of", &a_obj, &a_speed)) {
			break;
		}

		AnimationPlayer *anim_player = GetObjPtr<AnimationPlayer>(a_obj);
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
		PyObject *a_obj;
		float x, y;

		if (!PyArg_ParseTuple(args, "Off", &a_obj, &x, &y)) {
			break;
		}

		Camera3D *camera = GetObjPtr<Camera3D>(a_obj);
		if (!camera) {
			break;
		}

		const Vector2 screen_pos(x, y);
		auto ray_origin = camera->project_ray_origin(screen_pos);
		auto ray_normal = camera->project_ray_normal(screen_pos);
		ray_normal.normalize();

		const Vector3 plane_normal(0, 1, 0);
		const Vector3 plane_p0(0, 0, 0);

		real_t den = ray_normal.dot(plane_normal);
		if (Math::is_zero_approx(den)) {
			// 没有交点,法线垂直, 说明直线跟平面平行
			return Py_BuildValue("(fff)", 0,0,0);
		}

		// 这个公式的几何意义, ray_origin到p0的向量, ray_normal在plane_normal上的投影, 形成的相似三角形
		real_t d = (plane_p0 - ray_origin).dot(plane_normal) / den;

		Vector3 p(ray_origin + d * ray_normal);
		return Py_BuildValue("(fff)", p.x, p.y, p.z);
		
	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_world_to_screen(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		float x, y, z;

		if (!PyArg_ParseTuple(args, "Offf", &a_obj, &x, &y, &z)) {
			break;
		}

		Camera3D *camera = GetObjPtr<Camera3D>(a_obj);
		if (!camera) {
			break;
		}
		const Vector3 world_pos(x, y, z);
		const auto screen_pos = camera->unproject_position(world_pos);
		
		return Py_BuildValue("(ff)", screen_pos.x, screen_pos.y);

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_canvas_item_set_visible(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		int v;

		if (!PyArg_ParseTuple(args, "Oi", &a_obj, &v)) {
			break;
		}

		CanvasItem *canvas_item = GetObjPtr<CanvasItem>(a_obj);
		if (!canvas_item) {
			break;
		}

		canvas_item->set_visible(v != 0);

	} while (0);
	Py_RETURN_NONE;
}
static PyObject *f_canvas_item_set_modulate(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		float r, g, b;

		if (!PyArg_ParseTuple(args, "Offf", &a_obj, &r,&g, &b)) {
			break;
		}

		CanvasItem *canvas_item = GetObjPtr<CanvasItem>(a_obj);
		if (!canvas_item) {
			break;
		}

		canvas_item->set_modulate(Color(r, g, b));

	} while (0);
	Py_RETURN_NONE;
}
static PyObject *f_canvas_item_set_self_modulate(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		float r, g, b;

		if (!PyArg_ParseTuple(args, "Offf", &a_obj, &r, &g, &b)) {
			break;
		}

		CanvasItem *canvas_item = GetObjPtr<CanvasItem>(a_obj);
		if (!canvas_item) {
			break;
		}

		canvas_item->set_self_modulate(Color(r, g, b));

	} while (0);
	Py_RETURN_NONE;
}

static PyObject *f_find_control(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		float x, y;

		if (!PyArg_ParseTuple(args, "Off", &a_obj, &x, &y)) {
			break;
		}

		Node *node = GetObjPtr<Node>(a_obj);
		if (!node) {
			break;
		}
		auto control = node->get_viewport()->gui_find_control(Point2(x, y));
		if (!control) {
			break;
		}

		PyObject *obj = FGDObjSlot::GetGDObj(control);
		Py_INCREF(obj);
		return obj;

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_node2d_set_position(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		float x, y;

		if (!PyArg_ParseTuple(args, "Off", &a_obj,
					&x, &y)) {
			break;
		}

		Node2D *node = GetObjPtr<Node2D>(a_obj);
		if (!node) {
			break;
		}

		node->set_position(Point2(x, y));

	} while (0);
	Py_RETURN_NONE;
}
static PyObject *f_control_set_position(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		float x, y;

		if (!PyArg_ParseTuple(args, "Off", &a_obj,
					&x, &y)) {
			break;
		}

		auto control = GetObjPtr<Control>(a_obj);
		if (!control) {
			break;
		}

		control->set_position(Point2(x, y));

	} while (0);
	Py_RETURN_NONE;
}
static PyObject *f_control_set_size(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		float w, h;

		if (!PyArg_ParseTuple(args, "Off", &a_obj, &w, &h)) {
			break;
		}

		Control *canvas_item = GetObjPtr<Control>(a_obj);
		if (!canvas_item) {
			break;
		}

		//canvas_item->set_self_modulate(Color(r, g, b));
		canvas_item->set_size(Size2(w, h));

	} while (0);
	Py_RETURN_NONE;
}
static PyObject *f_control_get_rect(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;

		if (!PyArg_ParseTuple(args, "O", &a_obj)) {
			break;
		}

		auto control = GetObjPtr<Control>(a_obj);
		if (!control) {
			break;
		}

		auto rect = control->get_rect();
		return Py_BuildValue("(ffff)", rect.position.x, rect.position.y,
			rect.size.width, rect.size.height);

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

		Camera3D *camera = NULL;
		//auto camera = GetCapsulePointer<Camera3D>(a_node);
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
		auto node = Object::cast_to<Node>(res->instantiate(PackedScene::GEN_EDIT_STATE_DISABLED));

		// 添加到场景的根节点下面
		auto st = SceneTree::get_singleton();
		auto scene = st->get_current_scene();
		scene->add_child(node);

		// 返回
		PyObject *obj = FGDObjSlot::GetGDObj(node);
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
//static PyObject *f_get_py_object(PyObject *module, PyObject *args) {
//	do {
//		PyObject *a_node;
//		if (!PyArg_ParseTuple(args, "O", &a_node)) {
//			break;
//		}
//
//		auto node = GetCapsulePointer<FPyObject>(a_node);
//		if (!node) {
//			break;
//		}
//
//		auto obj = node->get_py_object();
//		// 这里需要返回，所以得+1
//		Py_INCREF(obj);
//		return obj;
//		
//	} while (0);
//
//	Py_RETURN_NONE;
//}
static PyObject *f_label3d_set_text(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		const char *s;
		if (!PyArg_ParseTuple(args, "Os", &a_obj, &s)) {
			break;
		}
		Label3D *label = GetObjPtr<Label3D>(a_obj);
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

		auto label = GetObjPtr<Label>(a_obj);
		if (!label) {
			break;
		}

		auto text = String::utf8(s);
		label->set_text(text);

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_rich_text_label_set_text(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		const char *s;
		if (!PyArg_ParseTuple(args, "Os", &a_obj, &s)) {
			break;
		}

		auto label = GetObjPtr<RichTextLabel>(a_obj);
		if (!label) {
			break;
		}

		auto text = String::utf8(s);
		label->set_text(text);

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_texture_rect_load_texture(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		const char *s;
		if (!PyArg_ParseTuple(args, "Os", &a_obj, &s)) {
			break;
		}

		auto rect = GetObjPtr<TextureRect>(a_obj);
		if (!rect) {
			break;
		}

		Ref<Resource> res = ResourceLoader::load(s);
		Ref<Texture> tex = res;
		if (tex.is_valid()) {
			rect->set_texture(tex);
		}

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_texture_rect_set_texture(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		PyObject *a_tex;
		if (!PyArg_ParseTuple(args, "OO", &a_obj, &a_tex)) {
			break;
		}

		auto rect = GetObjPtr<TextureRect>(a_obj);
		if (!rect) {
			break;
		}
		auto p_res = GetResCapsule(a_tex);
		if (!p_res) {
			break;
		}

		Ref<Texture> tex = p_res->res;
		if (!tex.is_valid()) {
			break;
		}

		rect->set_texture(tex);

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_text_edit_set_text(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		const char *s;

		if (!PyArg_ParseTuple(args, "Os", &a_obj, &s)) {
			break;
		}

		auto edit = GetObjPtr<TextEdit>(a_obj);
		if (!edit) {
			break;
		}
		edit->set_text(String::utf8(s));

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_text_edit_get_text(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;

		if (!PyArg_ParseTuple(args, "O", &a_obj)) {
			break;
		}

		auto edit = GetObjPtr<TextEdit>(a_obj);
		if (!edit) {
			break;
		}
		auto s = edit->get_text();

		return PyUnicode_FromString(s.utf8());

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_color_rect_set_color(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		float r,g,b;

		if (!PyArg_ParseTuple(args, "Os", &a_obj, &r,&g,&b)) {
			break;
		}

		auto rect = GetObjPtr<ColorRect>(a_obj);
		if (!rect) {
			break;
		}
		rect->set_color(Color(r,g,b));

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_label_set_minimum_size(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		float w, h;

		if (!PyArg_ParseTuple(args, "Off", &a_obj, &w, &h)) {
			break;
		}

		auto label = GetObjPtr<Label>(a_obj);
		if (!label) {
			break;
		}

		label->set_custom_minimum_size(Size2(w, h));

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_tab_bar_get_current_tab(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;

		if (!PyArg_ParseTuple(args, "O", &a_obj)) {
			break;
		}

		auto tab_bar = GetObjPtr<TabBar>(a_obj);
		if (!tab_bar) {
			break;
		}

		int idx = tab_bar->get_current_tab();

		return PyLong_FromLong((long)idx);

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_tab_bar_set_current_tab(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		int a_index;

		if (!PyArg_ParseTuple(args, "Oi", &a_obj, &a_index)) {
			break;
		}

		auto tab_bar = GetObjPtr<TabBar>(a_obj);
		if (!tab_bar) {
			break;
		}

		if (a_index >= tab_bar->get_tab_count()) {
			break;
		}

		tab_bar->set_current_tab(a_index);

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_base_button_set_disabled(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		int a_value;

		if (!PyArg_ParseTuple(args, "Oi", &a_obj, &a_value)) {
			break;
		}

		auto btn = GetObjPtr<BaseButton>(a_obj);
		if (!btn) {
			break;
		}

		btn->set_disabled(a_value != 0);

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_base_button_is_pressed(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;

		if (!PyArg_ParseTuple(args, "O", &a_obj)) {
			break;
		}

		auto btn = GetObjPtr<BaseButton>(a_obj);
		if (!btn) {
			break;
		}

		bool pressed = btn->is_pressed();
		
		return PyBool_FromLong(pressed);

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_base_button_set_pressed(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		int a_value;

		if (!PyArg_ParseTuple(args, "Oi", &a_obj, &a_value)) {
			break;
		}

		auto btn = GetObjPtr<BaseButton>(a_obj);
		if (!btn) {
			break;
		}

		btn->set_pressed(a_value);

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_button_set_text(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		const char *a_str;

		if (!PyArg_ParseTuple(args, "Os", &a_obj, &a_str)) {
			break;
		}

		auto btn = GetObjPtr<Button>(a_obj);
		if (!btn) {
			break;
		}

		btn->set_text(String::utf8(a_str));

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_slider_get_value(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;

		if (!PyArg_ParseTuple(args, "O", &a_obj)) {
			break;
		}

		auto slider = GetObjPtr<Slider>(a_obj);
		if (!slider) {
			break;
		}

		auto value = slider->get_value();

		return PyFloat_FromDouble(value);

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_slider_set_value(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		float a_value;

		if (!PyArg_ParseTuple(args, "Of", &a_obj, &a_value)) {
			break;
		}

		auto slider = GetObjPtr<Slider>(a_obj);
		if (!slider) {
			break;
		}

		slider->set_value(a_value);

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_mesh_instance3d_set_albedo_color(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		int surface;
		float r, g, b;

		if (!PyArg_ParseTuple(args, "Oifff", &a_obj, &surface, &r, &g, &b)) {
			break;
		}

		auto mesh_instance = GetObjPtr<MeshInstance3D>(a_obj);
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
static PyObject *f_mesh_instance3d_load_albedo_tex(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		int surface;
		const char *a_path;

		if (!PyArg_ParseTuple(args, "Ois", &a_obj, &surface, &a_path)) {
			break;
		}

		auto mesh_instance = GetObjPtr<MeshInstance3D>(a_obj);
		if (!mesh_instance) {
			break;
		}

		// TODO:....

	} while (0);

	Py_RETURN_NONE;
}
// 加载资源接口, 可以是任何资源
static PyObject *f_load_resource(PyObject *module, PyObject *args) {
	do {
		const char *a_path;
		
		if (!PyArg_ParseTuple(args, "s", &a_path)) {
			break;
		}

		ResCapsule *p_res = memnew(ResCapsule);
		p_res->type = 0;
		p_res->res = ResourceLoader::load(String::utf8(a_path));

		auto obj = PyCapsule_New(p_res, c_Resource,
				&_capsule_delete_pointer<c_Resource, ResCapsule>);

		return obj;

	} while (0);

	Py_RETURN_NONE;
}
// f_resource_duplicate 资源复制
static PyObject *f_resource_duplicate(PyObject *module, PyObject *args) {
	do {
		PyObject *a_src_obj;

		if (!PyArg_ParseTuple(args, "O", &a_src_obj)) {
			break;
		}

		auto p_src_obj = GetResCapsule(a_src_obj);
		ResCapsule *p_res = memnew(ResCapsule);
		p_res->type = 0;
		p_res->res = p_src_obj->res->duplicate();

		auto dst_obj = PyCapsule_New(p_res, c_Resource,
				&_capsule_delete_pointer<c_Resource, ResCapsule>);

		return dst_obj;

	} while (0);

	Py_RETURN_NONE;
}
// f_material_set_color, 设置材质属性
static PyObject *f_material_set_color(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		const char *a_str;
		float a, r, g, b;

		if (!PyArg_ParseTuple(args, "Osffff", &a_obj, &a_str, &r, &g, &b, &a)) {
			break;
		}

		auto p_res = GetResCapsule(a_obj);
		Ref<ShaderMaterial> mat = p_res->res;
		if (mat.is_valid()) {
			mat->set_shader_parameter(String::utf8(a_str), Color(r, g, b, a));
		}

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_mesh_instance3d_load_material(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		int surface;
		const char *a_path;

		if (!PyArg_ParseTuple(args, "Ois", &a_obj, &surface, &a_path)) {
			break;
		}

		MeshInstance3D *mesh_instance = GetObjPtr<MeshInstance3D>(a_obj);
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

		//mesh_instance->set_surface_override_material(surface, mat);
		// 这个issure, 有人给了一个解决方案, 换成下面这个override
		// 如果用了 surface_material_override, 需要unset, 在销毁这个mesh_instance3d之前.
		// https://github.com/godotengine/godot/issues/59912
		mesh_instance->set_material_override(mat);

		// 这个不能用啊
		//mesh_instance->set_surface_override_material(surface, mat);

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_mesh_instance3d_set_surface_material(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		int a_surface;
		PyObject *a_mat;

		if (!PyArg_ParseTuple(args, "OiO", &a_obj, &a_surface, &a_mat)) {
			break;
		}

		MeshInstance3D *mesh_instance = GetObjPtr<MeshInstance3D>(a_obj);
		if (!mesh_instance) {
			break;
		}

		int count = mesh_instance->get_surface_override_material_count();
		if (a_surface >= count) {
			break;
		}
		if (Py_IsNone(a_mat)) {
			mesh_instance->set_surface_override_material(a_surface, nullptr);
		} else {
			auto p_res = GetResCapsule(a_mat);
			mesh_instance->set_surface_override_material(a_surface, p_res->res);
		}

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_cpu_particle_set_emitting(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		int a_value;

		if (!PyArg_ParseTuple(args, "Oi", &a_obj, &a_value)) {
			break;
		}

		auto ps = GetObjPtr<CPUParticles3D>(a_obj);
		if (!ps) {
			break;
		}
		ps->set_emitting(a_value != 0);

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
// surface tool
struct SurfaceToolCapsule {
	Ref<SurfaceTool> st;
};
static inline SurfaceToolCapsule* GetSurfaceToolCapsule(PyObject* capsule) {
	//return reinterpret_cast<SurfaceToolCapsule *>(PyCapsule_GetPointer(capsule, c_SurfaceTool));
	return _capsule_get_pointer<c_SurfaceTool, SurfaceToolCapsule>(capsule);
}
static PyObject *f_surface_tool_new(PyObject *module, PyObject *args) {
	do {

		SurfaceToolCapsule *p_res = memnew(SurfaceToolCapsule);
		p_res->st = Ref<SurfaceTool>(memnew(SurfaceTool));
		p_res->st->begin(Mesh::PRIMITIVE_TRIANGLES);
		p_res->st->set_color(Color(1.0f, 1.0f, 1.0f));
		p_res->st->set_normal(Vector3(0.0f, 1.0f, 0.0f));
		p_res->st->set_uv(Vector2(0.0, 0.0f));
		p_res->st->index();

		auto obj = PyCapsule_New(p_res, c_SurfaceTool,
				&_capsule_delete_pointer<c_SurfaceTool, SurfaceToolCapsule>);
		return obj;

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_surface_tool_set_color(PyObject *module, PyObject *args) {
	do {
		PyObject *p_obj;
		float r, g, b, a;

		if (!PyArg_ParseTuple(args, "Offff", &p_obj, &r, &g, &b, &a)) {
			break;
		}

		auto p_res = GetSurfaceToolCapsule(p_obj);
		if (!p_res) {
			break;
		}

		p_res->st->set_color(Color(r, g, b, a));

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_surface_tool_set_uv(PyObject *module, PyObject *args) {
	do {
		PyObject *p_obj;
		float x, y;

		if (!PyArg_ParseTuple(args, "Off", &p_obj, &x, &y)) {
			break;
		}

		auto p_res = GetSurfaceToolCapsule(p_obj);
		if (!p_res) {
			break;
		}

		p_res->st->set_uv(Vector2(x, y));

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_surface_tool_set_uv2(PyObject *module, PyObject *args) {
	do {
		PyObject *p_obj;
		float x, y;

		if (!PyArg_ParseTuple(args, "Off", &p_obj, &x, &y)) {
			break;
		}

		auto p_res = GetSurfaceToolCapsule(p_obj);
		if (!p_res) {
			break;
		}

		p_res->st->set_uv2(Vector2(x, y));

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_surface_tool_add_vertex(PyObject *module, PyObject *args) {
	do {
		PyObject *p_obj;
		float x, y, z;

		if (!PyArg_ParseTuple(args, "Offf", &p_obj, &x, &y, &z)) {
			break;
		}

		auto p_res = GetSurfaceToolCapsule(p_obj);
		if (!p_res) {
			break;
		}

		p_res->st->add_vertex(Vector3(x, y, z));

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_surface_tool_add_index(PyObject *module, PyObject *args) {
	do {
		PyObject *p_obj;
		int i;

		if (!PyArg_ParseTuple(args, "Oi", &p_obj, &i)) {
			break;
		}

		auto p_res = GetSurfaceToolCapsule(p_obj);
		if (!p_res) {
			break;
		}

		p_res->st->add_index(i);

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_surface_tool_set_normal(PyObject *module, PyObject *args) {
	do {
		PyObject *p_obj;
		float x, y, z;

		if (!PyArg_ParseTuple(args, "Offf", &p_obj, &x, &y, &z)) {
			break;
		}

		auto p_res = GetSurfaceToolCapsule(p_obj);
		if (!p_res) {
			break;
		}

		p_res->st->set_normal(Vector3(x,y,z));

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_surface_tool_set_custom(PyObject *module, PyObject *args) {
	do {
		PyObject *p_obj;
		int channel_index;
		float a, r, g, b;

		if (!PyArg_ParseTuple(args, "Oiffff", &p_obj, &channel_index, &r, &g, &b, &a)) {
			break;
		}

		auto p_res = GetSurfaceToolCapsule(p_obj);
		if (!p_res) {
			break;
		}

		p_res->st->set_custom(channel_index, Color(r, g, b, a));

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_surface_tool_commit(PyObject *module, PyObject *args) {
	do {
		PyObject *p_obj;
		PyObject *mi_obj;

		if (!PyArg_ParseTuple(args, "OO", &p_obj, &mi_obj)) {
			break;
		}

		auto p_res = GetSurfaceToolCapsule(p_obj);
		
		auto mi = GetObjPtr<MeshInstance3D>(mi_obj);
		if (!mi || !p_res) {
			break;
		}

		Ref<ArrayMesh> mesh = p_res->st->commit();
		mi->set_mesh(mesh);

	} while (0);

	Py_RETURN_NONE;
}
static PyObject *f_viewport_set_update_mode(PyObject *module, PyObject *args) {
	do {
		PyObject *a_obj;
		int mode;

		if (!PyArg_ParseTuple(args, "Oi", &a_obj, &mode)) {
			break;
		}

		auto p_viewport = GetObjPtr<SubViewport>(a_obj);
		if (!p_viewport) {
			break;
		}

		p_viewport->set_update_mode((SubViewport::UpdateMode)mode);

	} while (0);

	Py_RETURN_NONE;
}

// define godot api
static PyMethodDef GodotPy_methods[] = {
	// os
	{ "print_line", f_print_line, METH_VARARGS, NULL },
	{ "get_time", f_get_time, METH_VARARGS, NULL },
	{ "get_delta_time", f_get_delta_time, METH_VARARGS, NULL },
	{ "set_window_rect", f_set_window_rect, METH_VARARGS, NULL },
	{ "get_window_size", f_get_window_size, METH_VARARGS, NULL },
	{ "window_set_title", f_window_set_title, METH_VARARGS, NULL },
	{ "viewport_get_size", f_viewport_get_size, METH_VARARGS, NULL },
	{ "get_scene_root", f_get_scene_root, METH_VARARGS, NULL },
	{ "is_editor_hint", f_is_editor_hint, METH_VARARGS, NULL },
	{ "set_custom_mouse_cursor", f_set_custom_mouse_cursor, METH_VARARGS, NULL },

	// node
	{ "set_process", f_set_process, METH_VARARGS, NULL },
	{ "set_process_input", f_set_process_input, METH_VARARGS, NULL },
	{ "set_physics_process", f_set_physics_process, METH_VARARGS, NULL },
	{ "destroy", f_destroy, METH_VARARGS, NULL },

	{ "find_node", f_find_node, METH_VARARGS, NULL },
	{ "get_child_count", f_get_child_count, METH_VARARGS, NULL },
	{ "get_child_at", f_get_child_at, METH_VARARGS, NULL },
	{ "get_parent", f_get_parent, METH_VARARGS, NULL },
	{ "reparent", f_reparent, METH_VARARGS, NULL },
	{ "node_set_last", f_node_set_last, METH_VARARGS, NULL },
	{ "node_dup", f_node_dup, METH_VARARGS, NULL },

	{ "node_connect", f_node_connect, METH_VARARGS, NULL },
	{ "node_disconnect", f_node_disconnect, METH_VARARGS, NULL },
	{ "node_clear_connection", f_node_clear_connection, METH_VARARGS, NULL },
	{ "node_set_name", f_node_set_name, METH_VARARGS, NULL },
	
	// node3d
	{ "set_position", f_set_position, METH_VARARGS, NULL },
	{ "get_position", f_get_position, METH_VARARGS, NULL },
	{ "set_rotation", f_set_rotation, METH_VARARGS, NULL },
	{ "get_rotation", f_get_rotation, METH_VARARGS, NULL },
	{ "set_scale", f_set_scale, METH_VARARGS, NULL },
	{ "look_at", f_look_at, METH_VARARGS, NULL },
	{ "local_look_at", f_local_look_at, METH_VARARGS, NULL },
	{ "get_forward", f_get_forward, METH_VARARGS, NULL },
	{ "local_to_world", f_local_to_world, METH_VARARGS, NULL },
	{ "world_to_local", f_world_to_local, METH_VARARGS, NULL },
	{ "node3d_set_visible", f_node3d_set_visible, METH_VARARGS, NULL },

	// animation player
	{ "animation_player_play", f_animation_player_play, METH_VARARGS, NULL },
	{ "animation_player_stop", f_animation_player_stop, METH_VARARGS, NULL },
	{ "animation_player_set_speed_scale", f_animation_player_set_speed_scale, METH_VARARGS, NULL },

	// 2d
	{ "node2d_set_position", f_node2d_set_position, METH_VARARGS, NULL },

	// camera3d
	{ "screen_to_world", f_screen_to_world, METH_VARARGS, NULL },
	{ "world_to_screen", f_world_to_screen, METH_VARARGS, NULL },

	// physics
	{ "raycast_shape", f_raycast_shape, METH_VARARGS, NULL },

	// label3d
	{ "label3d_set_text", f_label3d_set_text, METH_VARARGS, NULL },

	// gui
	{ "control_set_position", f_control_set_position, METH_VARARGS, NULL },
	{ "control_set_size", f_control_set_size, METH_VARARGS, NULL },
	{ "control_get_rect", f_control_get_rect, METH_VARARGS, NULL },

	{ "canvas_item_set_visible", f_canvas_item_set_visible, METH_VARARGS, NULL },
	{ "canvas_item_set_modulate", f_canvas_item_set_modulate, METH_VARARGS, NULL },
	{ "canvas_item_set_self_modulate", f_canvas_item_set_self_modulate, METH_VARARGS, NULL },

	{ "find_control", f_find_control, METH_VARARGS, NULL },
	{ "base_button_set_disabled", f_base_button_set_disabled, METH_VARARGS, NULL },
	{ "base_button_is_pressed", f_base_button_is_pressed, METH_VARARGS, NULL },
	{ "base_button_set_pressed", f_base_button_set_pressed, METH_VARARGS, NULL },
	{ "button_set_text", f_button_set_text, METH_VARARGS, NULL },
	{ "slider_get_value", f_slider_get_value, METH_VARARGS, NULL },
	{ "slider_set_value", f_slider_set_value, METH_VARARGS, NULL },

	// label
	{ "label_set_text", f_label_set_text, METH_VARARGS, NULL },
	{ "label_set_minimum_size", f_label_set_minimum_size, METH_VARARGS, NULL },

	// texture rect
	{ "texture_rect_load_texture", f_texture_rect_load_texture, METH_VARARGS, NULL },
	{ "texture_rect_set_texture", f_texture_rect_set_texture, METH_VARARGS, NULL },
	{ "color_rect_set_color", f_color_rect_set_color, METH_VARARGS, NULL },

	// text edit
	{ "text_edit_set_text", f_text_edit_set_text, METH_VARARGS, NULL },
	{ "text_edit_get_text", f_text_edit_get_text, METH_VARARGS, NULL },
	
	// rich_text_label_set_text
	{ "rich_text_label_set_text", f_rich_text_label_set_text, METH_VARARGS, NULL },

	// tabbar
	{ "tab_bar_get_current_tab", f_tab_bar_get_current_tab, METH_VARARGS, NULL },
	{ "tab_bar_set_current_tab", f_tab_bar_set_current_tab, METH_VARARGS, NULL },

	// particle
	{ "cpu_particle_set_emitting", f_cpu_particle_set_emitting, METH_VARARGS, NULL },

	// debug
	{ "debug_get_monitor", f_debug_get_monitor, METH_VARARGS, NULL },

	// mesh instance
	{ "mesh_instance3d_load_material", f_mesh_instance3d_load_material, METH_VARARGS, NULL },
	{ "mesh_instance3d_set_surface_material", f_mesh_instance3d_set_surface_material, METH_VARARGS, NULL },
	{ "mesh_instance3d_set_albedo_color", f_mesh_instance3d_set_albedo_color, METH_VARARGS, NULL },
	{ "mesh_instance3d_load_albedo_tex", f_mesh_instance3d_load_albedo_tex, METH_VARARGS, NULL },

	// resource
	{ "instantiate", f_instantiate, METH_VARARGS, NULL },
	{ "load_scene", f_load_scene, METH_VARARGS, NULL },
	{ "load_resource", f_load_resource, METH_VARARGS, NULL },
	{ "resource_duplicate", f_resource_duplicate, METH_VARARGS, NULL },
	{ "material_set_color", f_material_set_color, METH_VARARGS, NULL },

	// surface tool
	{ "surface_tool_new", f_surface_tool_new, METH_VARARGS, NULL },
	{ "surface_tool_set_color", f_surface_tool_set_color, METH_VARARGS, NULL },
	{ "surface_tool_set_uv", f_surface_tool_set_uv, METH_VARARGS, NULL },
	{ "surface_tool_set_uv2", f_surface_tool_set_uv2, METH_VARARGS, NULL },
	{ "surface_tool_set_normal", f_surface_tool_set_normal, METH_VARARGS, NULL }, 
	{ "surface_tool_add_vertex", f_surface_tool_add_vertex, METH_VARARGS, NULL },
	{ "surface_tool_add_index", f_surface_tool_add_index, METH_VARARGS, NULL },
	{ "surface_tool_set_custom", f_surface_tool_set_custom, METH_VARARGS, NULL },
	{ "surface_tool_commit", f_surface_tool_commit, METH_VARARGS, NULL },

	// viewport
	{ "viewport_set_update_mode", f_viewport_set_update_mode, METH_VARARGS, NULL },

	// godotpy
	//{ "get_py_object", f_get_py_object, METH_VARARGS, NULL },

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
		} else {
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

		auto gdobj = FGDObjSlot::GetGDObj(this);
		PyObject_SetAttrString(p_object, c_gdobj_name, gdobj);

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
	// TODO:
	//FGDObjSlot::Clear();
	//Py_FinalizeEx();
}
void FPyObject::_bind_methods() {
	ClassDB::bind_method(D_METHOD("set_python_path", "python_module"), &FPyObject::set_python_path);
	ClassDB::bind_method(D_METHOD("get_python_path"), &FPyObject::get_python_path);
	ADD_PROPERTY(PropertyInfo(Variant::STRING, "python_module"), "set_python_path", "get_python_path");

	ClassDB::bind_method(D_METHOD("set_python_class", "py_class"), &FPyObject::set_python_class);
	ClassDB::bind_method(D_METHOD("get_python_class"), &FPyObject::get_python_class);
	ADD_PROPERTY(PropertyInfo(Variant::STRING, "python_class"), "set_python_class", "get_python_class");

	ClassDB::bind_static_method("FPyObject", D_METHOD("call_python_func", "module", "func"), &FPyObject::call_python_func);
}

void FPyObject::call_python_func(const String &module, const String &func) {
	print_line(vformat("call python func: %s.%s", module, func));

	do
	{
		PyObject *p_path = PyUnicode_FromString(module.utf8().get_data());
		auto p_module = PyImport_Import(p_path);
		if (!p_module) {
			break;
		}
		GP_DECREF(p_path);

		auto dict = PyModule_GetDict(p_module);
		if (!dict) {
			GP_DECREF(p_module);
			PyErr_Print();
			break;
		}
		GP_DECREF(p_module);

		auto p_func = PyDict_GetItemString(dict, func.utf8().get_data());
		if (!p_func) {
			PyErr_Print();
			break;
		}

		if (!PyCallable_Check(p_func)) {
			break;
		}

		//auto args = PyTuple_New(0);
		auto ret = PyObject_CallObject(p_func, NULL);
		//GP_DECREF(args);

		if (!ret) {
			PyErr_Print();
			break;
		}
		GP_DECREF(ret);
		 
	} while (0);
	
}


