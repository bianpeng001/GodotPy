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
template<typename T1, typename T2, typename T3, typename T4> struct Args4 {
    T1 arg1;
    T2 arg2;
    T3 arg3;
    T4 arg4;

    Args4(PyObject * args) {
        GetTupleItem(args, 0, &arg1);
        GetTupleItem(args, 1, &arg2);
        GetTupleItem(args, 2, &arg3);
        GetTupleItem(args, 3, &arg4);
    }
};
template<typename T1, typename T2, typename T3, typename T4, typename T5> struct Args5 {
    T1 arg1;
    T2 arg2;
    T3 arg3;
    T4 arg4;
    T5 arg5;

    Args5(PyObject * args) {
        GetTupleItem(args, 0, &arg1);
        GetTupleItem(args, 1, &arg2);
        GetTupleItem(args, 2, &arg3);
        GetTupleItem(args, 3, &arg4);
        GetTupleItem(args, 4, &arg5);
    }
};
template<typename T, typename TResult> struct Call0 {
    typedef TResult (T::*func_ptr)();
    func_ptr fun;
    Call0(func_ptr a_fun) : fun(a_fun) {

    }
    TResult Exec(PyObject * args) {
        Args1<PyObject *> arguments(args);
        auto obj = GetObjPtr<T>(arguments.arg1);
        if (obj) {
            (obj->*fun)();
        }
    }
    TResult operator()(PyObject * args) {
        return this->Exec(args);
    }
};
template<typename T, typename TResult, typename T1> struct Call1 {
    typedef TResult (T::*func_ptr)(T1);
    func_ptr fun;
    Call1(func_ptr a_fun) : fun(a_fun) {

    }
    TResult Exec(PyObject * args) {
        Args2<PyObject *,T1> arguments(args);
        auto obj = GetObjPtr<T>(arguments.arg1);
        if (obj) {
            (obj->*fun)(arguments.arg2);
        }
    }
    TResult operator()(PyObject * args) {
        return this->Exec(args);
    }
};
template<typename T, typename TResult, typename T1, typename T2> struct Call2 {
    typedef TResult (T::*func_ptr)(T1,T2);
    func_ptr fun;
    Call2(func_ptr a_fun) : fun(a_fun) {

    }
    TResult Exec(PyObject * args) {
        Args3<PyObject *,T1,T2> arguments(args);
        auto obj = GetObjPtr<T>(arguments.arg1);
        if (obj) {
            (obj->*fun)(arguments.arg2, arguments.arg3);
        }
    }
    TResult operator()(PyObject * args) {
        return this->Exec(args);
    }
};


