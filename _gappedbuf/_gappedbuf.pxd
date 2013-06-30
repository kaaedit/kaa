
cdef public class GappedBuffer [object GappedBufferObj, type GappedBufferType]:
    cdef public Py_ssize_t bufsize
    cdef public Py_ssize_t numelems 
    cdef public Py_ssize_t gap
    cdef public Py_ssize_t gapsize
    cdef Py_UCS4 *buf

#    cdef inline _conv_slice(self, Py_ssize_t pos) nogil:
#        if pos < 0:
#
#        return self.numelems

    cdef void _resize_buf(self, Py_ssize_t size)
    cdef void _expand_gap(self, Py_ssize_t size)
    cdef void _shrink_gap(self)
    cdef void _move_gap(self, Py_ssize_t index)

    cdef Py_UCS4 _get_max(self, Py_ssize_t begin, Py_ssize_t end) nogil
    cdef void _copy_chars1(self, void *dest, Py_ssize_t begin, 
            Py_ssize_t end) nogil
    cdef void _copy_chars2(self, void *dest, Py_ssize_t begin, 
            Py_ssize_t end) nogil 
    cdef void _copy_chars4(self, void *dest, Py_ssize_t begin, 
            Py_ssize_t end) nogil
          
    cdef int _get_slice(self, object obj, 
            Py_ssize_t *f, Py_ssize_t *t) except *

    cdef _insert(self, Py_ssize_t index, unicode s)
    cpdef insert(self, Py_ssize_t index, unicode s)
    cpdef append(self, unicode s)
    cdef _delete(self, Py_ssize_t begin, Py_ssize_t end)
    cpdef delete(self, Py_ssize_t begin, Py_ssize_t end)
    cpdef replace(self, Py_ssize_t begin, Py_ssize_t end, unicode s)
    cpdef get(self, Py_ssize_t begin, Py_ssize_t end)

    cdef int _get_slice(self, object obj,
            Py_ssize_t *f, Py_ssize_t *t) except *
    cpdef getint(self, Py_ssize_t pos)
    cpdef getints(self, Py_ssize_t begin, Py_ssize_t end)
    cdef _insertints(self, Py_ssize_t index, object s)
    cpdef insertints(self, Py_ssize_t index, object s)
    cpdef appendints(self, object s)
    cpdef replaceints(self, Py_ssize_t begin, Py_ssize_t end, object s)
    cpdef setints(self, Py_ssize_t begin, Py_ssize_t end, unsigned long v)



