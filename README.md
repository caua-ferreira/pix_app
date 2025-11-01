# Pix QR Code Desktop
# PixApp — Gerador de QR Code Pix (desktop)

Essa é uma versão genérica do app para gerar QR Codes do Pix (unitário e em massa) em desktop Windows.

Principais arquivos
- `main.py` — interface PyQt5 e ponto de entrada.
- `pix_utils.py` — funções para gerar payload e imagem do QR.
- `perfis.json` — exemplos de perfis (empresa). Salve seus perfis locais aqui.
- `pix_config.json` — configurações persistentes (chave pix, cidade).

Requisitos
- Python 3.8+ (recomendado 3.9/3.10)
- PyQt5, qrcode, pillow (veja `requirements.txt`)

Uso (rápido)
1. Instale dependências (recomendado em virtualenv):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Execute localmente para testar:

```powershell
python main.py
```

Gerando um executável para Windows

Incluí um script PowerShell de ajuda `build_windows.ps1` que:
- cria (opcional) virtualenv
- instala dependências
- executa PyInstaller para gerar a pasta `dist\PixApp\` (ou `dist\PixApp.exe` se usar --onefile)

Como usar o script (PowerShell):

```powershell
.\build_windows.ps1
```

O script também tenta criar um instalador Inno Setup se o compilador do Inno estiver instalado (ISCC.exe).
Um template de script Inno está em `installer\pix_app.iss`.

Dicas de empacotamento
- Para gerar um único .exe (onefile): altere o trecho do PyInstaller no `build_windows.ps1` para `--onefile`.
- Inclua imagens e arquivos (ex.: `perfis.json`, `Logo Oficial.png`) com a opção `--add-data "arquivo;."` do PyInstaller.

Estrutura sugerida

```
pix_app/
  __init__.py
  pix_utils.py
main.py
perfis.json
pix_config.json
Logo Oficial.png
requirements.txt
README.md
build_windows.ps1
installer/pix_app.iss
```

Suporte
- Este projeto é open-source para uso geral. Se quiser adicionar um site de suporte, substitua esta seção por um contato ou repositório Git.

Próximos passos recomendados
- (Opcional) Colocar o código dentro de um package (`pix_app/`) para facilitar distribuição via pip.
- Criar testes unitários para `pix_utils.py`.
- Adicionar ícone e assets ao instalador.
