"""complex_recursion.py - High complexity module."""

def complicated_processor(data, config, callbacks=None):
    """Complex data processor with many branches."""
    results = {}
    errors = []
    
    if not data:
        return None
    
    if config.get("validate"):
        for key, value in data.items():
            if key.startswith("_"):
                continue
            
            if isinstance(value, dict):
                if config.get("recursive"):
                    sub_result = complicated_processor(value, config, callbacks)
                    if sub_result:
                        results[key] = sub_result
            elif isinstance(value, list):
                processed = []
                for idx, item in enumerate(value):
                    if config.get("filter_nulls") and item is None:
                        continue
                    if config.get("transform"):
                        if isinstance(item, str):
                            processed.append(item.strip().lower())
                        elif isinstance(item, (int, float)):
                            processed.append(item * config.get("multiplier", 1))
                        else:
                            processed.append(item)
                    else:
                        processed.append(item)
                results[key] = processed
            else:
                results[key] = value
    
    if callbacks and "on_complete" in callbacks:
        try:
            callbacks["on_complete"](results)
        except Exception as e:
            errors.append(str(e))
    
    return results if not errors else None
