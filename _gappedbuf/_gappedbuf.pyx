from libc.stdlib cimport malloc, free, realloc
from libc.string cimport memmove, memcpy
from cpython cimport unicode, mem, ref
from cpython.list cimport PyList_New, PyList_SET_ITEM
from cpython.long cimport PyLong_FromUnsignedLong

cimport rtdef

cdef extern from "_gappedbufre.h":
    object PyInit__gappedbufre()



def init_gappedbufre():
    import sys
    sys.modules['_gappedbufre'] = PyInit__gappedbufre()

cdef class GappedBuffer:
    def __cinit__(self):
        DEF BUFSIZE = 4096

        self.buf = <Py_UCS4*>malloc(BUFSIZE * sizeof(Py_UCS4))
        if not self.buf:
            raise MemoryError()

        self.bufsize = BUFSIZE
        self.numelems = 0
        self.gap = 0
        self.gapsize = BUFSIZE

    def __dealloc__(self):
        if self.buf:
            free(self.buf)
            self.buf = NULL
    
    cdef void _resize_buf(self, Py_ssize_t size):
        cdef Py_UCS4 *buf = <Py_UCS4*>realloc(
                self.buf, size * sizeof(Py_UCS4))

        if not buf:
            raise MemoryError()
        self.buf = buf
        self.bufsize = size

    cdef void _expand_gap(self, Py_ssize_t size):
        if size <= self.gapsize:
            return
        self._resize_buf(self.numelems+size)

        if self.gap < self.numelems:
            # resize gap
            memmove(self.buf+self.gap+size, self.buf+self.gap+self.gapsize,
                    (self.numelems-self.gap) * sizeof(Py_UCS4))
    
        self.gapsize = size

    cdef void _shrink_gap(self):
        DEF MAX_GAPSIZE = 4096
        if self.numelems + MAX_GAPSIZE > self.bufsize:
            return
        memmove(self.buf+self.gap+MAX_GAPSIZE,
                self.buf+self.gap+self.gapsize,
                (self.numelems-self.gap) * sizeof(Py_UCS4))

        self.gapsize = MAX_GAPSIZE
        self._resize_buf(self.numelems+MAX_GAPSIZE)

    cdef void _move_gap(self, Py_ssize_t index):
        assert index <= self.bufsize
        if self.gap == index:
            return
        if self.gapsize:
            if index < self.gap:
                memmove(self.buf+index+self.gapsize, self.buf+index,
                        (self.gap - index)*sizeof(Py_UCS4))
            else:
                memmove(self.buf+self.gap, self.buf+self.gap+self.gapsize,
                        (index - self.gap)*sizeof(Py_UCS4))
        self.gap = index
    
    cdef _insert(self, Py_ssize_t index, unicode s):
        cdef Py_ssize_t size = len(s)
        if not (0 <= index <= self.numelems):
            raise ValueError('Invalid index value: %d, %d' % (
                                index, self.numelems))

        if size:
            self._move_gap(index)
            if self.gapsize < size:
                self._expand_gap(max(1024, size*2))
            rtdef.PyUnicode_AsUCS4(s, self.buf+index, size, False)
            
            self.numelems += size
            self.gap += size
            self.gapsize -= size

    cpdef insert(self, Py_ssize_t index, unicode s):
        self._insert(index, s)

    cpdef append(self, unicode s):
        self.insert(self.numelems, s)

    cdef _delete(self, Py_ssize_t begin, Py_ssize_t end):
        if not (0 <= begin <= end <= self.numelems):
            raise ValueError('Invalid range: %d, %d, %d' % (
                                begin, end, self.numelems))
        
        cdef Py_ssize_t size = end-begin
        if not size:
            return

        self._move_gap(begin)
        self.gapsize += size
        self.numelems -= size
        self._shrink_gap()

    cpdef delete(self, Py_ssize_t begin, Py_ssize_t end):
        self._delete(begin, end)

    cpdef replace(self, Py_ssize_t begin, Py_ssize_t end, unicode s):
        self._delete(begin, end)
        self._insert(begin, s)

    cdef Py_UCS4 _get_max(self, Py_ssize_t begin, Py_ssize_t end) nogil:
        cdef Py_UCS4 maxchar = 0
        cdef Py_ssize_t b, e

        e = min(end, self.gap)

        cdef Py_ssize_t p
        for p from begin <= p < e:
            maxchar = max(maxchar, self.buf[p])
        b = max(begin, self.gap) 
        for p from b <= p < end:
            maxchar = max(maxchar, self.buf[p+self.gapsize])
        return maxchar

    cdef void _copy_chars1(self, void *dest, Py_ssize_t begin, 
            Py_ssize_t end) nogil:
        cdef rtdef.Py_UCS1 *buf = <rtdef.Py_UCS1 *>dest
        cdef Py_ssize_t b, e

        # copy before gap
        e = min(end, self.gap)
        cdef Py_ssize_t p
        for p from begin <= p < e:
            buf[0] = self.buf[p]
            buf += 1

        # copy after gap
        b = max(begin, self.gap) + self.gapsize
        for p from b <= p < end+self.gapsize:
            buf[0] = self.buf[p]
            buf += 1
        
    cdef void _copy_chars2(self, void *dest, Py_ssize_t begin, 
            Py_ssize_t end) nogil:
        cdef rtdef.Py_UCS2 *buf = <rtdef.Py_UCS2 *>dest
        cdef Py_ssize_t b, e

        # copy before gap
        e = min(end, self.gap)
        cdef Py_ssize_t p
        for p from begin <= p < e:
            buf[0] = self.buf[p]
            buf += 1

        # copy after gap
        b = max(begin, self.gap) + self.gapsize
        for p from b <= p < end+self.gapsize:
            buf[0] = self.buf[p]
            buf += 1

    cdef void _copy_chars4(self, void *dest, Py_ssize_t begin, 
            Py_ssize_t end) nogil:
        cdef Py_ssize_t n = end - begin
        cdef Py_ssize_t former

        if self.gap < begin:
            memcpy(dest, self.buf+begin+self.gapsize, n*sizeof(Py_UCS4))
        elif end <= self.gap:
            memcpy(dest, self.buf+begin, n*sizeof(Py_UCS4))
        else:
            former = self.gap - begin
            memcpy(dest, self.buf+begin, former*sizeof(Py_UCS4))
            memcpy(dest+former*sizeof(Py_UCS4), self.buf+self.gap+self.gapsize, 
                    (n-former)*sizeof(Py_UCS4))

    cpdef get(self, Py_ssize_t begin, Py_ssize_t end):
        if not (0 <= begin <= end <= self.numelems):
            raise IndexError('Invalid range: %d, %d, %d' % (
                                begin, end, self.numelems))

        cdef Py_ssize_t n = end - begin
        cdef Py_UCS4 maxchar = self._get_max(begin, end)
        cdef unicode ret = rtdef.PyUnicode_New(n, maxchar)
        cdef void *buf = rtdef.PyUnicode_DATA(ret)
        cdef nbytes = rtdef.PyUnicode_KIND(ret)

        if nbytes == 1:
            self._copy_chars1(buf, begin, end)
        elif nbytes == 2:
            self._copy_chars2(buf, begin, end)
        elif nbytes == 4:
            self._copy_chars4(buf, begin, end)
        else:
            raise RuntimeError()

        return ret
    
    def __len__(self):
        return self.numelems
    
    cdef int _get_slice(self, object obj, 
            Py_ssize_t *f, Py_ssize_t *t) except *:
        cdef Py_ssize_t step, slicelength

        if rtdef.PySlice_Check(obj):
            rtdef.PySlice_GetIndicesEx(obj, self.numelems, f, t, 
                     &step, &slicelength)
            if step != 1:
                raise ValueError('step is not supported')
            return 1
        else: 
            f[0] = obj
            if f[0] < 0:
                f[0] += self.numelems
            if not (0 <= f[0] < self.numelems):
                raise IndexError('Invalid index value: %d, %d' % (
                                    f[0], self.numelems))
            return 0

    def __getitem__(self, object item):
        cdef Py_ssize_t start, stop
        
        if self._get_slice(item, &start, &stop):
            return self.get(start, stop)
        else:
            return self.buf[start+(0 if start < self.gap else self.gapsize)]

    def __setitem__(self, object item, unicode value):
        cdef Py_ssize_t start, stop
        
        if self._get_slice(item, &start, &stop):
            self.replace(start, stop, value)
        else:
            if len(value) != 1:
                raise ValueError('Invalid string length: %d' % len(value))
            
            start = start+(0 if start < self.gap else self.gapsize)
            self.buf[start] = <Py_UCS4>value

    def __delitem__(self, object item):
        cdef Py_ssize_t start, stop
        
        if self._get_slice(item, &start, &stop):
            self.delete(start, stop)
        else: 
            self.delete(start, start+1)

    def findchr(self, unicode c, Py_ssize_t begin, Py_ssize_t end):
        cdef Py_UCS4 *chars
        cdef Py_ssize_t size, b, e, p

        if not (0 <= begin <= end <= self.numelems):
            raise ValueError('Invalid range: %d, %d, %d' % (
                                begin, end, self.numelems))
        
        chars = rtdef.PyUnicode_AsUCS4Copy(c)
        try:
            size = len(c)
            # search before gap
            e = min(end, self.gap)
            for p from begin <= p < e:
                for q from 0 <= q < size:
                    if self.buf[p] == chars[q]:
                        return p

            # search after gap
            b = max(begin, self.gap) + self.gapsize
            for p from b <= p < end+self.gapsize:
                for q from 0 <= q < size:
                    if self.buf[p] == chars[q]:
                        return p-self.gapsize
        finally:
            mem.PyMem_Free(chars)

        return -1

    def rfindchr(self, unicode c, Py_ssize_t begin, Py_ssize_t end):
        cdef Py_UCS4 *chars
        cdef Py_ssize_t size, b, e, p

        if not (0 <= begin <= end <= self.numelems):
            raise ValueError('Invalid range: %d, %d, %d' % (
                                begin, end, self.numelems))
        
        chars = rtdef.PyUnicode_AsUCS4Copy(c)
        try:
            size = len(c)
            # search after gap
            b = max(begin, self.gap) + self.gapsize
            for p from (end+self.gapsize) > p >= b:
                for q from 0 <= q < size:
                    if self.buf[p] == chars[q]:
                        return p-self.gapsize

            # search before gap
            e = min(end, self.gap)
            for p from e > p >= begin:
                for q from 0 <= q < size:
                    if self.buf[p] == chars[q]:
                        return p
        finally:
            mem.PyMem_Free(chars)

        return -1
    
    cpdef getint(self, Py_ssize_t pos):
        if not (0 <= pos < self.numelems):
            raise ValueError('Invalid index value: %d, %d' % (
                                pos, self.numelems))
        if pos < self.gap:
            return <unsigned long>self.buf[pos]
        else:
            return <unsigned long>self.buf[self.gapsize+pos]

    cpdef getints(self, Py_ssize_t begin, Py_ssize_t end):

        cdef Py_ssize_t b, e, p, n
        cdef list ret
        cdef object v

        if not (0 <= begin <= end <= self.numelems):
            raise ValueError('Invalid range: %d, %d, %d' % (
                                begin, end, self.numelems))
        
        ret = PyList_New(end-begin)
        n = 0 
        # read before gap
        e = min(end, self.gap)
        for p from begin <= p < e:
            v = <unsigned long>self.buf[p]
            PyList_SET_ITEM(ret, n, v)
            ref.Py_INCREF(v)
            n += 1

        # read after gap
        b = max(begin, self.gap) + self.gapsize
        for p from b <= p < end+self.gapsize:
            v = <unsigned long>self.buf[p]
            PyList_SET_ITEM(ret, n, v)
            ref.Py_INCREF(v)
            n += 1

        return ret

    cdef _insertints(self, Py_ssize_t index, object s):

        cdef Py_ssize_t size = len(s)
        if not (0 <= index <= self.numelems):
            raise ValueError('Invalid index value: %d, %d' % (
                                index, self.numelems))

        if size:
            self._move_gap(index)
            if self.gapsize < size:
                self._expand_gap(max(1024, size*2))

            for value in s:
                self.buf[self.gap] = <unsigned long>value
                self.gap += 1

            self.numelems += size
            self.gapsize -= size

    cpdef insertints(self, Py_ssize_t index, object s):

        self._insertints(index, s)

    cpdef appendints(self, object s):
        self.insertints(self.numelems, s)

    cpdef replaceints(self, Py_ssize_t begin, Py_ssize_t end, object s):
        self._delete(begin, end)
        self._insertints(begin, s)

    cpdef setints(self, Py_ssize_t begin, Py_ssize_t end, unsigned long v):
        cdef Py_ssize_t b, e, p

        if not (0 <= begin <= end <= self.numelems):
            raise ValueError('Invalid range: %d, %d, %d' % (
                                begin, end, self.numelems))

        n = 0
        # replace before gap
        e = min(end, self.gap)
        for p from begin <= p < e:
            self.buf[p] = v

        # replace after gap
        b = max(begin, self.gap) + self.gapsize
        for p from b <= p < end+self.gapsize:
            self.buf[p] = v

    def findint(self, object nums, Py_ssize_t begin, Py_ssize_t end,
                int comp_ne):
        cdef unsigned long *longs
        cdef Py_ssize_t size, b, e, p

        if not (0 <= begin <= end <= self.numelems):
            raise ValueError('Invalid range: %d, %d, %d' % (
                                begin, end, self.numelems))

        size = len(nums)
        longs = <unsigned long *>mem.PyMem_Malloc(
                                    size * sizeof(unsigned long))
        if not longs:
            raise MemoryError()

        try:
            for i from 0 <= i < size:
                longs[i] = nums[i]

            # search before gap
            e = min(end, self.gap)
            for p from begin <= p < e:
                if not comp_ne:
                    for q from 0 <= q < size:
                        if self.buf[p] == longs[q]:
                            return p
                else:
                    for q from 0 <= q < size:
                        if self.buf[p] == longs[q]:
                            break
                    else:
                        return p

            # search after gap
            b = max(begin, self.gap) + self.gapsize
            for p from b <= p < end+self.gapsize:
                if not comp_ne:
                    for q from 0 <= q < size:
                        if self.buf[p] == longs[q]:
                            return p-self.gapsize
                else:
                    for q from 0 <= q < size:
                        if self.buf[p] == longs[q]:
                            break
                    else:
                        return p-self.gapsize
        finally:
            mem.PyMem_Free(longs)

        return -1

    def rfindint(self, object nums, Py_ssize_t begin, Py_ssize_t end,
                 int comp_ne):

        cdef unsigned long *longs
        cdef Py_ssize_t size, b, e, p

        if not (0 <= begin <= end <= self.numelems):
            raise ValueError('Invalid range: %d, %d, %d' % (
                                begin, end, self.numelems))

        size = len(nums)
        longs = <unsigned long *>mem.PyMem_Malloc(
                                    size * sizeof(unsigned long))
        if not longs:
            raise MemoryError()
        try:
            for i from 0 <= i < size:
                longs[i] = nums[i]

            # search after gap
            b = max(begin, self.gap) + self.gapsize
            for p from (end+self.gapsize) > p >= b:
                if not comp_ne:
                    for q from 0 <= q < size:
                        if self.buf[p] == longs[q]:
                            return p-self.gapsize
                else:
                    for q from 0 <= q < size:
                        if self.buf[p] == longs[q]:
                            break
                    else:
                        return p-self.gapsize

            # search before gap
            e = min(end, self.gap)
            for p from e > p >= begin:
                if not comp_ne:
                    for q from 0 <= q < size:
                        if self.buf[p] == longs[q]:
                            return p
                else:
                    for q from 0 <= q < size:
                        if self.buf[p] == longs[q]:
                            break
                    else:
                        return p
        finally:
            mem.PyMem_Free(longs)

        return -1
