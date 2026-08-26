# Guion de demo — Agente ADK (10 preguntas)


| # | Pregunta a escribirle al agente | Tool que debería usar | Qué debe mencionar la respuesta |
|---|---|---|---|
| 1 | "Dame un resumen de las estadísticas básicas: edad, venta total y monto por compra." | `estadisticas_basicas` | Media, mediana y moda de al menos edad y monto_compra |
| 2 | "¿En qué mes se vendió más y en cuál se vendió menos durante 2021?" | `ventas_por_mes` | Nombre del mes (no el número) y el monto en cada caso |
| 3 | "¿Cuál navegador usan más los clientes y cuál es el menos popular?" | `ranking_navegadores` | Navegador más y menos usado, mención de Tienda Física si aplica |
| 4 | "¿Qué porcentaje de las ventas se pagaron en efectivo o contra entrega?" | `ventas_por_metodo_pago` | Porcentaje de efectivo y método más usado en general |
| 5 | "¿Qué rango de edad es el que más gasta en promedio?" | `segmentacion_por_edad` | Rango de edad ganador y su venta promedio |
| 6 | "¿Hay diferencias notables en el comportamiento de compra entre hombres y mujeres?" | `comparativa_generos` | Género que más gasta y método de pago preferido por cada uno |
| 7 | "¿En qué meses se usaron más boletines y más vales?" | `uso_boletin_vale` | Mes de boletín y mes de vale (pueden ser distintos) |
| 8 | "¿Los clientes que usan boletín Y vale gastan más que los que no usan ninguno?" | `patrones_boletin_vale` | Comparación entre el grupo "con boletín/con vale" y "sin boletín/sin vale" |
| 9 | "¿Existe relación entre la edad del cliente y cuánto gasta en total?" | `correlaciones` | Coeficiente de Pearson e interpretación en palabras (débil/moderada/fuerte) |
| 10 | "Necesito un resumen ejecutivo: estadísticas generales, el mes más fuerte en ventas y el navegador más usado." | Combinada: `estadisticas_basicas` + `ventas_por_mes` + `ranking_navegadores` | Que el agente llame las tres tools y las una en una sola respuesta coherente, no tres respuestas separadas |

