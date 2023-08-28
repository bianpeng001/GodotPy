#pragma once

//
// parse args tuple
//
template<typename T>
inline void GetTupleItem(PyObject* arg, int index, T* Result) { }
template<> inline void GetTupleItem<int>(PyObject *args, int index, int *Result) {
    PyObject *arg = PyTuple_GET_ITEM(args, index);
    long ivalue = PyLong_AsLong(arg);
    *Result = (int)ivalue;
}
typedef const char* const_char_ptr;
template<> inline void GetTupleItem<const_char_ptr>(PyObject *args, int index, const_char_ptr *Result) {
    const char *sarg;
    Py_ssize_t len;
    PyObject *arg = PyTuple_GET_ITEM(args, index);
    sarg = PyUnicode_AsUTF8AndSize(arg, &len);
    *Result = sarg;
}
template<> inline void GetTupleItem<float>(PyObject *args, int index, float *Result) {
    PyObject *arg = PyTuple_GET_ITEM(args, index);
    *Result = (float)PyFloat_AsDouble(arg);
}
typedef PyObject * PyObject_ptr;
template<> inline void GetTupleItem<PyObject_ptr>(PyObject *args, int index, PyObject_ptr *Result) {
    PyObject *arg = PyTuple_GET_ITEM(args, index);
    *Result = arg;
}


