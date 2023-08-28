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

template<typename T1> struct Args1 {
    T1 arg1;

    Args1(PyObject * args) {
        GetTupleItem(args, 0, &arg1);
    }
};
template<typename T1, typename T2> struct Args2 {
    T1 arg1;
    T2 arg2;

    Args2(PyObject * args) {
        GetTupleItem(args, 0, &arg1);
        GetTupleItem(args, 1, &arg2);
    }
};
template<typename T1, typename T2, typename T3> struct Args3 {
    T1 arg1;
    T2 arg2;
    T3 arg3;

    Args3(PyObject * args) {
        GetTupleItem(args, 0, &arg1);
        GetTupleItem(args, 1, &arg2);
        GetTupleItem(args, 2, &arg3);
    }
};

template<typename T, typename TResult, typename T1, typename T2> struct Call2 {
    typedef TResult (T::*func)(T1, T2);
    TResult operator()(PyObject * args) {
        Args2<T1,T2> arguments(args);
    }
};

