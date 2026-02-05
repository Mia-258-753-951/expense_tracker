# Expense Tracker (CLI)

Expense Tracker es una aplicación de línea de comandos para el registro y análisis de gastos personales.

El objetivo principal del proyecto **no es la funcionalidad en sí**, sino servir como proyecto práctico para consolidar una **arquitectura backend “seria” en Python**, con separación clara de responsabilidades, persistencia intercambiable y tests desde el inicio.

---

## 🎯 Objetivos del proyecto

- Diseñar una arquitectura limpia y extensible en Python
- Aplicar el *Repository Pattern* de forma práctica
- Separar dominio, servicios, infraestructura y CLI
- Implementar persistencia progresiva:
  - memoria
  - JSON
  - SQLite (SQL manual)
- Implementar estadísticas eficientes
- Mantener disciplina de tests, commits y calidad de código

El proyecto está desarrollado por fases, cada una construyendo sobre la anterior sin romper contratos.

---

## 🏗️ Arquitectura

La aplicación sigue una arquitectura en capas bien definida:

### Dominio
Modelos puros (por ejemplo `Expense`) con invariantes y sin dependencias externas.

### Servicios
Contienen la lógica de aplicación y las reglas de negocio.  
No conocen detalles de persistencia ni de la interfaz de entrada.

### Repositorios (Infrastructure)
Implementaciones concretas de persistencia:
- In-memory
- JSON
- SQLite

### Puertos (Protocols)
Contratos explícitos que definen las capacidades requeridas por los servicios
(CRUD, estadísticas, etc.).

### CLI
Implementada con **Typer**.  
Se limita a parsear argumentos y delegar en los servicios.

---

## 📦 Modelo de dominio

Entidad principal: **Expense**

Campos principales:
- `id`
- `date`
- `amount` (en céntimos)
- `category`
- `wallet`
- `note`
- `currency`
- `created_at`
- `updated_at`

El dominio es completamente independiente de la persistencia y de la CLI.

---

## 💾 Persistencia

### Fase 1 — Memoria
Repositorio en memoria utilizado para:
- validar la arquitectura
- desarrollar servicios
- escribir tests iniciales

No persiste entre ejecuciones.

---

### Fase 2 — JSON
Persistencia en fichero JSON con:
- escritura atómica (`.tmp` + replace)
- campo `schema_version` para evolución futura
- tests de *round-trip* (guardar → recargar)

Formato simplificado:

```json
{
  "schema_version": 1,
  "expenses": []
}

### Fase 3 — SQLite

Persistencia en SQLite usando SQL manual.

Características:

- esquema versionado mediante migraciones SQL
- tabla `schema_version`
- índices en campos clave
- estadísticas calculadas directamente en SQL
- uso de `COALESCE` para normalizar agregaciones

Las migraciones se aplican automáticamente al inicializar el repositorio.

---

## 📊 Estadísticas

Las estadísticas se calculan de forma distinta según el backend:

- **Memory / JSON** → cálculo en Python
- **SQLite** → cálculo en SQL (`GROUP BY`, `COUNT`, `SUM`)

Se define un puerto específico (`ExpenseStatsRepository`) para expresar las
capacidades de agregación, independiente del repositorio CRUD.

Estadísticas soportadas:

- resumen por rango de fechas
- agrupación por categoría
- agrupación por wallet
- agrupación por día
- estadísticas mensuales:
  - total gastado
  - número de gastos
  - media
  - *top categories* (por importe)
  - *top wallets* (por importe)

---

## 🖥️ CLI

La interfaz de línea de comandos está implementada con **Typer**.

Ejemplos de uso:

```bash
expenses add --amount 10.50 --category food --wallet personal --date 2026-01-10
expenses list
stats range --from 2026-01-01 --to 2026-01-31 --by category
stats month-stats --month 2026-01

🧪 Tests

 * tests unitarios para servicios
* tests de integración para repositorios (JSON y SQLite)
* smoke tests para la CLI

Los tests de persistencia verifican round-trip real
(datos escritos y recargados desde disco).

🧭 Roadmap / Fases

Fase 1: CLI + repositorio en memoria

Fase 2: Persistencia JSON

Fase 3: Persistencia SQLite + migraciones + estadísticas en SQL

Fase 4 (futuro): FastAPI + autenticación

Fase 5 (futuro): Frontend con HTMX

▶️ Cómo ejecutar
Instalar dependencias (usando uv):
uv sync

Ejecutar la CLI:
python -m expense_tracker


Por defecto, los datos SQLite se almacenan en:

data/expenses.db

📌 Nota final

Este proyecto está pensado como ejercicio de aprendizaje serio y progresivo,
priorizando diseño, claridad y mantenibilidad frente a complejidad innecesaria.