## PixApp — Gerador de QR Code Pix (desktop)

Quantas vezes voce já quis gerar um QR Code Pix rapidamente no seu computador desktop Windows, sem depender de apps móveis ou sites online? Pois bem!

Esse é um app para gerar QR Codes do Pix (unitário e em massa) em desktop Windows.
Sem complicações, rápido e fácil de usar!
Roda totalmente offline, sem necessidade de internet após a instalação.
O código é open source e pode ser avaliado e modificado conforme sua necessidade (não esqueça de me atribuir :)
Veja abaixo as instruções para rodar localmente ou gerar um executável.


Principais arquivos
- `main.py` — interface PyQt5 / ponto de entrada
- `pix_utils.py` — lógica para gerar o payload e imagens do QR
- `perfis.json` — perfis de cobrança de exemplo (guarde seus perfis aqui)
- `pix_config.json` — configurações persistentes (ex.: chave, cidade)

Requisitos
- Python 3.8+ (3.9/3.10 recomendados)
- Dependências: veja `requirements.txt` (PyQt5, qrcode, Pillow, ...)

Uso rápido (desenvolvimento)
1. Criar/ativar virtualenv e instalar dependências:

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

2. Executar localmente:

```powershell
python main.py
```

Gerar executável / instalador (Windows)

Opções comuns:

- Usar `build_windows.ps1` (suporta PyInstaller e tenta criar instalador Inno quando disponível). Exemplo:

```powershell
.\\build_windows.ps1
```

- Para um único `.exe` com PyInstaller, edite `build_windows.ps1` e passe `--onefile` para o comando do PyInstaller.

- O template do Inno Setup está em `PixApp.iss` (ou `installer/pix_app.iss`). Para compilar localmente com Inno use o Inno Setup Compiler (ISCC.exe).

Observação sobre releases e binários

Por padrão não é recomendável commitar grandes binários (instaladores) dentro do repositório Git. Boas práticas:

- Subir o código-fonte no repositório (o que já está aqui).
- Publicar instaladores como "Release assets" no GitHub Releases — assim o repositório permanece enxuto.

No repositório atual há um instalador gerado (`installer/PixApp_Setup.exe`) que foi adicionado por conveniência — se preferir, posso remover o binário e gerar um release para você.

Configuração do instalador (Inno Setup)

- Arquivo de exemplo: `PixApp.iss`.
- O script inclui os arquivos: `PixApp.exe`, `perfis.json`, `pix_config.json`, `pix_gerados.json`.

Contribuição

1. Fork
2. Criar branch: `git checkout -b feat/minha-feature`
3. Commit: `git commit -m "Add feature"`
4. Push e abrir Pull Request

Licença

Este projeto está licenciado sob MIT — veja o arquivo `LICENSE`.

Autor / Contato

Cauã Ferreira — https://github.com/caua-ferreira
