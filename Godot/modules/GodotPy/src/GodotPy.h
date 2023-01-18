//
// 2023-1-17
//

#pragma once

#include "scene/main/node.h"

//------------------------------------------------------------------------------
//
//------------------------------------------------------------------------------
typedef struct _object PyObject;

class FPyModule : public Node {
	GDCLASS(FPyModule, Node)
private:
	String py_file_path;
	PyObject *py_module;

public:
	FPyModule();
	virtual ~FPyModule();

private:
	void _notification(int p_what);
	void _ready();

	void set_python(const String &file_path);
	String get_python() const {
		return py_file_path;
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


