import numpy as np
def hash_mask(string, mask):
    n = len(string)
    vec = np.array([ord(_) for _ in string])
    
    if n < mask.shape[0]:
        vec = np.pad(vec, (0, mask.shape[0]-n), mode='constant', constant_values=0)
    elif n > mask.shape[0]:
        mask = np.pad(mask, ((0, n-mask.shape[0]),(0,0)), mode='constant', constant_values=0)
        print(mask)
    return vec @ mask



mask = np.random.randint(100, size=(10, 10))
print(hash_mask('an_umbrella', mask))
