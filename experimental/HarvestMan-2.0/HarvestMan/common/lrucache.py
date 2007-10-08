"""
lrucache.py - Length-limited O(1) LRU cache implementation

Author: Anand B Pillai <anand at harvestmanontheweb.com>
    
Created Anand B Pillai Jun 26 2007 from ASPN Python Cookbook recipe #252524.

{http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/252524}

Original code courtesy Josiah Carlson.

Copyright (C) 2007, Anand B Pillai.
"""
import copy

class Node(object):
    __slots__ = ['prev', 'next', 'me']
    def __init__(self, prev, me):
        self.prev = prev
        self.me = me
        self.next = None

    def __copy__(self):
        n = Node(self.prev, self.me)
        n.next = self.next

        return n
    
class LRU(object):
    """
    Implementation of a length-limited O(1) LRU queue.
    Built for and used by PyPE:
    http://pype.sourceforge.net
    Copyright 2003 Josiah Carlson.
    """
    def __init__(self, count, pairs=[]):
        self.count = max(count, 1)
        self.d = {}
        self.first = None
        self.last = None
        for key, value in pairs:
            self[key] = value

    def __copy__(self):
        lrucopy = LRU(self.count)
        lrucopy.first = copy.copy(self.first)
        lrucopy.last = copy.copy(self.last)
        lrucopy.d = self.d.copy()
        for key,value in self.iteritems():
            lrucopy[key] = value

        return lrucopy
        
    def __contains__(self, obj):
        return obj in self.d
    def __getitem__(self, obj):
        a = self.d[obj].me
        self[a[0]] = a[1]
        return a[1]
    def __setitem__(self, obj, val):
        if obj in self.d:
            del self[obj]
        nobj = Node(self.last, (obj, val))
        if self.first is None:
            self.first = nobj
        if self.last:
            self.last.next = nobj
        self.last = nobj
        self.d[obj] = nobj
        if len(self.d) > self.count:
            if self.first == self.last:
                self.first = None
                self.last = None
                return
            a = self.first
            a.next.prev = None
            self.first = a.next
            a.next = None
            del self.d[a.me[0]]
            del a
    def __delitem__(self, obj):
        nobj = self.d[obj]
        if nobj.prev:
            nobj.prev.next = nobj.next
        else:
            self.first = nobj.next
        if nobj.next:
            nobj.next.prev = nobj.prev
        else:
            self.last = nobj.prev
        del self.d[obj]
    def __iter__(self):
        cur = self.first
        while cur != None:
            cur2 = cur.next
            yield cur.me[1]
            cur = cur2
    def iteritems(self):
        cur = self.first
        while cur != None:
            cur2 = cur.next
            yield cur.me
            cur = cur2
    def iterkeys(self):
        return iter(self.d)
    def itervalues(self):
        for i,j in self.iteritems():
            yield j
    def keys(self):
        return self.d.keys()
    def clear(self):
        self.d.clear()
    def __len__(self):
        return len(self.d)
    
if __name__=="__main__":
    l = LRU(10)
    for x in range(10):
        l[x] = x
    print l.keys()
    print l[3]
    print l[3]
    print l[9]
    print l[9]
    
    l[12]=11
    l[13]=12
    print l.keys()
    print len(l)
    print copy.copy(l).keys()
