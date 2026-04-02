"""Module with long function."""

def very_long_function(data, config, options, context):
    step1 = data.get("input")
    step2 = step1 * 2
    step3 = step2 + 10
    step4 = step3 / 2
    step5 = step4 - 5
    step6 = step5 * config.get("multiplier", 1)
    step7 = step6 + options.get("offset", 0)
    step8 = step7 / context.get("scale", 1)
    step9 = step8 * 2
    step10 = step9 + 100
    step11 = step10 - 50
    step12 = step11 / 2
    return step12
