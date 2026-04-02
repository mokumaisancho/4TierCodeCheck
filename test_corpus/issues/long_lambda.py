
process = lambda data: [item for item in data if item.active and item.score > 50 and item.category in ['A', 'B']]
