// python
#include <Windows.h>
#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "Binding.h"

template<typename T>
struct TypeLabel {
    static const char *Label;
};
template<> const char *TypeLabel<char*>::Label = "s";
template<> const char *TypeLabel<int>::Label = "i";
template<> const char *TypeLabel<PyObject*>::Label = "o";

template<typename T>
struct Arg {
    typedef T Type;
    typedef TypeLabel<T> TypeLabel;
};

#define MAKE_FUNC_BEGIN(NAME) \
    static PyObject * f_ ## NAME(PyObject *module, PyObject *args) { \
    do { \
    } while(0);
    

#define MAKE_FUNC_END() \
    Py_RETURN_NONE; }

MAKE_FUNC_BEGIN(hello)
MAKE_FUNC_END()

