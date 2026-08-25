# Laboratorio Sistemas Organizacionales y Gerenciales 2

## Integrantes

| Nombre                           | Carné     |
| -------------------------------- | --------- |
| Sergio Joel Rodas Valdez         | 202200271 |
| Ariel Josué López Gálvez         | 202200185 |
| Joel Alexander Guzaro Tzunun     | 202201395 |
| Elian Angel Fernando Reyes Yac   | 202044192 |
| Katherin Alejandra Gálvez Chiroy | 202006633 |

## Cómo probar el Servidor MCP

Para verificar que las herramientas de análisis del Servidor MCP funcionan correctamente antes de conectarlas a un Agente de IA, se puede usar el Inspector Oficial de MCP.

### Requisitos Previos

1. Activa el entorno virtual:
   ```bash
   source venv/bin/activate
   ```
2. Verifica que las dependencias estén instaladas:
   ```bash
   pip install -r requirements.txt
   pip install fastmcp
   ```

### Ejecutar el Inspector

Con el entorno activado y las dependencias instaladas, ejecuta el siguiente comando utilizando Node.js (`npx`):

```bash
npx @modelcontextprotocol/inspector@latest ./venv/bin/python src/mcp_server.py
```

Al ejecutarse, la terminal mostrará un enlace local para abrir el Inspector en el navegador.
