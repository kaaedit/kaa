#ifndef __PYX_HAVE___gappedbuf
#define __PYX_HAVE___gappedbuf

struct GappedBufferObj;

/* "_gappedbuf.pxd":2
 * 
 * cdef public class GappedBuffer [object GappedBufferObj, type GappedBufferType]:             # <<<<<<<<<<<<<<
 *     cdef public Py_ssize_t bufsize
 *     cdef public Py_ssize_t numelems
 */
struct GappedBufferObj {
  PyObject_HEAD
  struct __pyx_vtabstruct_10_gappedbuf_GappedBuffer *__pyx_vtab;
  Py_ssize_t bufsize;
  Py_ssize_t numelems;
  Py_ssize_t gap;
  Py_ssize_t gapsize;
  Py_UCS4 *buf;
};

#ifndef __PYX_HAVE_API___gappedbuf

#ifndef __PYX_EXTERN_C
  #ifdef __cplusplus
    #define __PYX_EXTERN_C extern "C"
  #else
    #define __PYX_EXTERN_C extern
  #endif
#endif

__PYX_EXTERN_C DL_IMPORT(PyTypeObject) GappedBufferType;

#endif /* !__PYX_HAVE_API___gappedbuf */

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC init_gappedbuf(void);
#else
PyMODINIT_FUNC PyInit__gappedbuf(void);
#endif

#endif /* !__PYX_HAVE___gappedbuf */
