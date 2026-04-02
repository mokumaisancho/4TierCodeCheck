
def process(data):
    for item in data:
        if item.active:
            for sub in item.children:
                if sub.valid:
                    process(sub)
