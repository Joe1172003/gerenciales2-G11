## 8e. ¿Implementar un chat conversacional de IA afectaría a la empresa para que entregue el análisis de los datos a futuro?

Implementar un chat conversacional de IA, como el agente construido con
Google ADK en esta práctica, afectaría positivamente a la empresa en la
forma en que se entregan los análisis de datos, principalmente porque
elimina la dependencia de que un analista humano esté disponible cada
vez que alguien en la organización necesita una cifra o una tendencia.
En lugar de esperar a que el equipo de datos genere un reporte, cualquier
persona con acceso al chat puede preguntar directamente "¿cuál fue el
mes con más ventas?" o "¿qué navegador usan más nuestros clientes?" y
recibir una respuesta en segundos, con la gráfica correspondiente
incluida. Esto acelera considerablemente la toma de decisiones,
especialmente en una empresa que está por abrir su primera sucursal
física y necesita datos ágiles para decisiones operativas del día a día.

Sin embargo, esta implementación también trae responsabilidades nuevas.
El agente solo es tan confiable como las herramientas (tools) que tiene
conectadas: si el servidor MCP no cubre una pregunta, el chat debe
reconocerlo honestamente en vez de inventar una respuesta, por lo que la
calidad del `instruction` y de las descripciones de cada tool es crítica
para evitar que el modelo "alucine" cifras que no existen. También hay
que considerar los límites de tokens de los modelos gratuitos como
Gemini Flash, la necesidad de mantener actualizada la base de datos en
la nube para que las respuestas no queden desactualizadas, y controlar
quién tiene acceso al chat, ya que expone información sensible de ventas
y clientes. En resumen, el chat no reemplaza al analista humano, pero sí
democratiza el acceso a los datos dentro de la empresa y libera tiempo
del equipo de análisis para enfocarse en preguntas más complejas en vez
de reportes repetitivos.
