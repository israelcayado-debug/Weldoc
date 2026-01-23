# Especificacion funcional de el sistema

Este documento integra, de forma coherente y reutilizable, la informacion de las
fuentes "el sistema Features", "Creating Welder Qualifications with el sistema"
y "Welding Project Software - el sistema". Su proposito es definir una
especificacion funcional completa del software para gestion de soldadura
industrial, con el mismo nivel de detalle que los documentos originales.

## 1. Vision general del sistema

el sistema es un software integral de gestion de soldadura orientado a empresas
de fabricacion, caldereria, tuberia y EPC, valido tanto para pequenos talleres
como para grandes proyectos industriales. Funciona como un ERP especializado
en soldadura y cubre todo el ciclo de vida del proyecto: desde la definicion de
procedimientos de soldeo (WPS/PQR), la cualificacion y continuidad de soldadores,
hasta la planificacion, ejecucion, inspeccion, ensayos y generacion del dossier
final del proyecto.

El sistema cumple con los principales codigos y normas internacionales de
soldadura, integrando reglas automaticas que evitan errores y aseguran la
conformidad normativa.

## 2. Modulo de procedimientos de soldadura (WPS / PQR)

Este modulo permite la creacion, gestion y aprobacion de procedimientos de
soldadura y registros de cualificacion de procedimientos de forma guiada.

Funcionalidades principales:
- Creacion de WPS y PQR mediante formularios paso a paso, orientados al usuario.
- Validacion automatica de reglas de codigo para evitar combinaciones no
  conformes.
- Base de datos de materiales base con mas de 5.000 materiales.
- Base de datos de materiales de aporte con mas de 4.000 referencias.
- Tablas de dimensiones de tuberia en sistema metrico e imperial.
- Seleccion grafica de tipos de junta y secuencia de pases.
- Visualizacion dinamica de requisitos de ensayo obligatorios y opcionales.
- Calculo y visualizacion en tiempo real de los rangos de aprobacion.
- Soporte de hasta tres procesos de soldeo por procedimiento.
- Posibilidad de redactar WPS en borrador, generar PQR y aprobar WPS.
- Creacion de WPS a partir de uno o varios PQR.
- Importacion y gestion de WPS y PQR existentes creados fuera del sistema, sin
  limitaciones de numero ni costes adicionales.

Codigos soportados:
- ASME IX
- AWS D1.1
- AWS D1.2
- AWS D1.5
- AWS D1.6
- API 1104
- ISO 15614-1

## 3. Modulo de cualificacion y continuidad de soldadores (WPQ / WQTR)

Este modulo permite gestionar de forma centralizada todas las cualificaciones
de soldadores, tanto propias como de subcontratistas o clientes.

Funcionalidades principales:
- Generacion de WPQ/WQTR conformes a codigo en pocos minutos.
- Reglas de codigo integradas y seleccion guiada mediante listas desplegables.
- Visualizacion permanente del rango de cualificacion durante la creacion.
- Soporte de hasta tres procesos de soldeo por cualificacion.
- Flujo de aprobacion con firma y sello automaticos por usuario.
- Adjuntar informes de ensayo a cada cualificacion.
- Clonacion de cualificaciones existentes.
- Importacion de cualificaciones externas sin coste adicional.
- Gestion automatica de la continuidad del soldador.
- Registro detallado de todos los cordones realizados por cada soldador
  (log de soldador).
- Bloqueo automatico de soldadores con cualificaciones caducadas o fuera de
  continuidad.
- Envio automatico de correos de aviso por caducidad (normalmente un mes antes).
- Cuadros de mando con indicadores tipo "semaforo" para control de vencimientos.
- Informes detallados de rendimiento y productividad por soldador.

Normas soportadas:
- ASME IX
- AWS D1.1
- AWS D1.2
- AWS D1.5
- AWS D1.6
- API 1104
- ISO 9606-1
- ISO 9606-4

## 4. Gestion de proyectos de soldadura

El modulo de proyectos es el nucleo operativo del sistema y permite gestionar
desde unos pocos cordones hasta decenas de miles dentro de un mismo proyecto.

Capacidades generales:
- Creacion ilimitada de proyectos o trabajos.
- Configuracion del proyecto segun especificaciones del cliente o del codigo
  aplicable.
- Asignacion de usuarios por proyecto con control de roles y permisos.
- Gestion documental con control de revisiones.
- Historicos completos de cambios para auditorias.

## 5. Gestion de planos, isometricos y weld mapping

el sistema incorpora una herramienta grafica de marcado de soldaduras
directamente sobre planos.

Funcionalidades:
- Carga de planos con control de versiones.
- Marcado grafico de soldaduras mediante herramientas de dibujo.
- Numeracion automatica y secuencial de soldaduras.
- Asignacion de atributos a cada soldadura (tipo, tamano, junta, etc.).
- Creacion automatica de soldaduras en el sistema a partir del marcado en plano.
- Navegacion directa desde el plano a cada soldadura.
- Transferencia automatica de marcados cuando un plano se revisa.
- Registro de dimensiones y generacion de planos "as-built".
- Impresion de mapas de soldadura de alta calidad.

## 6. Repositorios de datos del proyecto

Cada proyecto dispone de repositorios estructurados y controlados por permisos.

Repositorios especificos:
- Tags o items fabricados.
- Planos y revisiones.
- Materiales y numeros de colada (heat numbers).
- Certificados de materiales (MTCs).
- Consumibles de soldadura y certificados asociados.
- Documentos del proyecto.
- Informes de inspeccion visual y END.

Repositorios centrales reutilizables:
- WPS y PQR.
- Soldadores.
- Operarios de montaje (fitters).
- Maquinas y equipos.

Carga de datos:
- Formularios individuales.
- Interfaces tipo hoja Excel para cargas masivas.
- Importacion de ficheros con emparejamiento inteligente.
- Carga masiva de adjuntos vinculados automaticamente a los registros.

## 7. Flujo de trabajo de soldadura (weld lifecycle)

El sistema integra un flujo completo desde la planificacion hasta la
finalizacion.

Etapas:
- Planificacion de soldaduras.
- Asignacion de WPS y soldadores.
- Control de trazabilidad de materiales.
- Ejecucion de soldadura.
- Inspeccion visual por etapas (fit-up, durante soldadura, post-soldadura).
- Solicitud y gestion de END.
- Gestion automatica de reparaciones.
- Ensayos de presion y tratamientos termicos (PWHT).

Supervision e inspeccion:
- Supervisores asignan soldadores y controlan el avance.
- Inspectores registran resultados y defectos por etapa.
- Registro de parametros de soldadura frente a WPS.

## 8. Inspeccion, END y control de calidad

El modulo de calidad permite un control exhaustivo conforme a codigos como
ASME B31.3.

Funcionalidades:
- Definicion de requisitos de END por proyecto, plano, tag o soldadura.
- Algoritmos automaticos de muestreo, penalizacion y trazadores.
- Gestion de solicitudes de END.
- Registro de resultados y defectos.
- Control de reparaciones y reinspecciones.
- Informes de cumplimiento de END.
- Registro de inspecciones visuales por etapa.

## 9. Work packs, travelers y documentacion de taller

- Agrupacion de soldaduras en work packs.
- Generacion de travelers, hojas de control y job cards.
- Emision en PDF.
- Etiquetas QR para soldaduras.
- Acceso a datos mediante app movil para soldadores, supervisores e inspectores.

## 10. Gestion del proyecto y seguimiento

- Calendario del proyecto.
- Diagramas de Gantt.
- Barras de progreso y estados.
- Cuadros de mando.
- Alertas y notificaciones.
- Mensajeria instantanea entre miembros del equipo.

## 11. Informes, analitica y exportacion de datos

- Informes de productividad de soldadores.
- Informes de avance del proyecto.
- Exportacion de datos a Excel.
- Generacion de PDFs para END, PWHT y pruebas de presion.
- Informes historicos de cambios para auditorias.

## 12. Dossier final y turnover pack

El sistema permite generar automaticamente el libro final del proyecto
(MDR / data book).

Caracteristicas:
- Seleccion flexible de contenidos.
- Tablas con enlaces a documentos.
- Indice y separadores de seccion.
- Encabezados y pies personalizables.
- Inclusion de adjuntos.
- Generacion de un unico PDF completamente estructurado.
- Regeneracion rapida ante cambios o entregas parciales.

## 13. Seguridad y control de accesos

- Control de acceso basado en roles.
- Permisos de lectura, alta, edicion o sin acceso.
- Trazabilidad completa de quien hizo que y cuando.

## 14. Conclusion

el sistema se concibe como una solucion integral y especializada para la
gestion de soldadura industrial, integrando en una unica plataforma los
requisitos tecnicos, normativos, operativos y documentales necesarios para
ejecutar y auditar proyectos de soldadura de cualquier escala.
