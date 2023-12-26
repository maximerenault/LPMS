from elements.wire import Wire
from math import sqrt

def intersect(elem1:Wire, elem2:Wire):
    '''
    Returns intersection coordinates
    with special cases for avoiding
    the creation of undesirable nodes
    '''
    x1,y1,x2,y2 = elem1.getcoords()
    x3,y3,x4,y4 = elem2.getcoords()
    denom = (y4-y3)*(x2-x1) - (x4-x3)*(y2-y1)
    if denom == 0: # parallel
        if (y4-y2)*(x2-x1) - (x4-x2)*(y2-y1) == 0 : # colinear
            d13 = distance(x1,y1,x3,y3)
            if d13 == 0 :
                dp = dotprod(x1,y1,x2,y2,x3,y3,x4,y4)
                if dp>0 :
                    return (x1,y1)
                return (x2,y2)
            
            d14 = distance(x1,y1,x4,y4)
            if d14 == 0 :
                dp = dotprod(x1,y1,x2,y2,x3,y3,x4,y4)
                if dp<0 :
                    return (x1,y1)
                return (x2,y2)
            
            d12 = distance(x1,y1,x2,y2)
            if d12<d13 and d12<d14 :
                return (x2,y2)
            if d13<d14 :
                return (x3,y3)
            return (x4,y4)
        return (x2,y2)
    
    ua = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)) / denom
    if ua < 0 or ua > 1: # out of range
        return (x2,y2)
    
    ub = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)) / denom
    if ub < 0 or ub > 1: # out of range
        return (x2,y2)
    
    x = x1 + round(ua * (x2-x1))
    y = y1 + round(ua * (y2-y1))
    if x==x1 and y==y1 :
        return (x2,y2)
    return (x,y)

def distance(x1,y1,x2,y2):
    '''
    Returns the distance between
    (x1,y1) and (x2,y2)
    '''
    return sqrt((x1-x2)**2+(y1-y2)**2)

def dotprod(x1,y1,x2,y2,x3,y3,x4,y4):
    '''
    Returns the dot product of vectors
    (x2-x1,y2-y1) and (x4-x3,y4-y3)
    '''
    return (x2-x1)*(x4-x3)+(y2-y1)*(y4-y3)

def point_on_elem(elem:Wire,x0,y0):
    '''
    Checks if a point (x0,y0) is
    on the line of elem
    '''
    x1,y1,x2,y2 = elem.getcoords()
    if (y1-y0)*(x2-x1) - (x1-x0)*(y2-y1) != 0 :
        return False
    dp1 = dotprod(x1,y1,x0,y0,x1,y1,x2,y2)
    dp2 = dotprod(x2,y2,x0,y0,x2,y2,x1,y1)
    if dp1>0 and dp2>0 :
        return True
    return False