import os

def is_hidden(filepath):
  (path, file) = os.path.split(filepath)
  
  if file and file.startswith('.'):
    return True
  
  try:
    import ctypes
    attrs = ctypes.windll.kernel32.GetFileAttributesW(unicode(filepath))
    return bool(attrs & 2)
  except Exception:
    pass
    
  return False