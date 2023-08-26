// python
#include <Windows.h>
#define PY_SSIZE_T_CLEAN
#include <Python.h>

template<typename T>
struct TypeLabel {
    static const char *Label;
};
template<> const char *TypeLabel<char*>::Label = "s";
template<> const char *TypeLabel<int>::Label = "i";
template<> const char *TypeLabel<PyObject*>::Label = "o";

//
// parse args tuple
//
template<typename T>
void GetTupleItem(PyObject* arg, T* Result) { }
template<> void GetTupleItem<int>(PyObject *arg, int *Result) {
    long ivalue = PyLong_AsLong(arg);

    *Result = (int)ivalue;
}
typedef const char* cchar_ptr;
template<> void GetTupleItem<cchar_ptr>(PyObject *arg, cchar_ptr *Result) {
    const char *sarg;
    Py_ssize_t len;

    sarg = PyUnicode_AsUTF8AndSize(arg, &len);
    *Result = sarg;
}
template<> void GetTupleItem<PyObject*>(PyObject *arg, PyObject **Result) {
    *Result = arg;
}

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

