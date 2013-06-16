
cdef extern from "Python.h":
    ctypedef unsigned char Py_UCS1
    ctypedef unsigned short Py_UCS2

    Py_UCS4* PyUnicode_AsUCS4Copy(object u) except NULL
    Py_UCS4* PyUnicode_AsUCS4(object u, Py_UCS4 *buffer, 
            Py_ssize_t buflen, int copy_null) except NULL
    object PyUnicode_New(Py_ssize_t size, Py_UCS4 maxchar)
    void* PyUnicode_DATA(object o) except NULL
    int PyUnicode_KIND(object o) except 0

    int PySlice_GetIndicesEx(object slice, Py_ssize_t length,
            Py_ssize_t *start, Py_ssize_t *stop, Py_ssize_t *step, 
            Py_ssize_t *slicelength) except -1
    int PySlice_Check(object)

