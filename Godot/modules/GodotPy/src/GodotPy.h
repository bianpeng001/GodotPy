//
// 2023-1-17
//

#pragma once

#include "scene/main/node.h"

//------------------------------------------------------------------------------
//
//------------------------------------------------------------------------------
typedef struct _object PyObject;

/// <summary>
/// Python脚本的执行入口，放一个节点
/// </summary>
class FPyObject : public Node {
	GDCLASS(FPyObject, Node)
private:
	String py_path;
	String py_class;

	PyObject *p_module;
	PyObject *p_object;

protected:
	virtual void input(const Ref<InputEvent> &p_event) override;

public:
	FPyObject();
	virtual ~FPyObject();

	PyObject* get_py_object() {
		return p_object;
	}

private:
	void _notification(int p_what);
	void _ready();
	void _physics_process();
	void _process();
	void _exit_tree();

	void set_python_path(const String& a_file_path) {
		py_path = a_file_path;
	}
	const String &get_python_path() const {
		return py_path;
	}
	void set_python_class(const String& a_py_class) {
		py_class = a_py_class;
	}
	const String &get_python_class() const {
		return py_class;
	}
	static void _bind_methods();
};

/// <summary>
///
/// </summary>
class FLibPy {
private:
	static bool bInit;

public:
	static void Init();
	static void Clean();
};


