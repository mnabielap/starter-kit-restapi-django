# Helper to pick fields from a dictionary (similar to lodash.pick or utils/pick.js)
def pick(dictionary, keys):
    return {k: v for k, v in dictionary.items() if k in keys}