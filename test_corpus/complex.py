"""High complexity module with issues."""

# TODO: Refactor this mess
def complicated_function(data, config):
    result = []
    seen = set()
    
    for i, item in enumerate(data):
        if item in seen:
            continue
            
        if config.get('filter'):
            if item < 0:
                continue
                
        if config.get('transform'):
            if item % 2 == 0:
                if item > 100:
                    item = item / 2
                else:
                    item = item * 2
            else:
                if item < 50:
                    item = item + 10
                else:
                    item = item - 10
                    
        seen.add(item)
        result.append(item)
        
    return result

def another_complex(a, b, c, d):
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    return a + b + c + d
                return a + b + c
            return a + b
        return a
    return 0
