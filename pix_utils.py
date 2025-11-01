# Shim: importe as funções do pacote `pix_app` (módulo reorganizado)
try:
    from pix_app.pix_utils import *
except Exception as e:
    # Fallback: raise informative error if package is not available
    raise ImportError("Módulo reorganizado: use 'pix_app.pix_utils' ou instale o pacote corretamente. Erro: " + str(e))
