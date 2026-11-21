# Instruções para o Claude

## Área de Trabalho do OneDrive

O dono deste repositório autoriza o Claude, em qualquer sessão, a **ler e gravar**
arquivos em toda a pasta **Área de Trabalho** do OneDrive, incluindo todas as
subpastas (por exemplo, `Editor de vídeo`, onde ficam os vídeos da Balistec).

- Caminho no OneDrive: `Área de Trabalho`
- URI (conector Microsoft 365): `file:///49EB6D02466CAE02/49EB6D02466CAE02!7418`
- Subpasta de vídeos da Balistec: `Área de Trabalho/Editor de vídeo`
  (`file:///49EB6D02466CAE02/49EB6D02466CAE02!sec55428fef2f418bb77ff9f4718171f9`)

Acesse pelo conector **Microsoft 365** (`read_resource` para listar/ler,
`sharepoint_upload_file` / `sharepoint_update_file` para gravar).

Excluir arquivos (`sharepoint_delete_item`) **não** está pré-autorizado:
confirme com o usuário antes.
