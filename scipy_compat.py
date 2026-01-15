"""
SciPy 兼容性補丁
修復 librosa 與新版 scipy 的兼容性問題
"""

import scipy.signal
import scipy.signal.windows

# 如果 scipy.signal 沒有 hann 屬性，添加它
if not hasattr(scipy.signal, 'hann'):
    scipy.signal.hann = scipy.signal.windows.hann
    print("已應用 scipy.signal.hann 兼容性補丁")

# 同時修復其他可能的窗函數
window_functions = ['hamming', 'blackman', 'bartlett', 'kaiser']
for func_name in window_functions:
    if not hasattr(scipy.signal, func_name):
        setattr(scipy.signal, func_name, getattr(scipy.signal.windows, func_name))
