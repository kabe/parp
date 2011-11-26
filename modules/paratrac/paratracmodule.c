#include <Python.h>
#include <paratrac_part.h>

static PyObject* str_hash(PyObject* self, PyObject* str) {
    const char* s;
    if(!PyArg_ParseTuple(str, "s", &s)) {
        return NULL;
    }
    unsigned int hashval = util_str_hash(s);
    return Py_BuildValue("i", hashval);
}

static PyMethodDef ParatracMethods[] = {
    {"str_hash", str_hash, METH_VARARGS, "get a hash value from a path string"},
    {NULL, NULL, 0, NULL}    /* sentinel */
};

PyMODINIT_FUNC initparatrac(void) {
    (void) Py_InitModule("paratrac", ParatracMethods);
}

