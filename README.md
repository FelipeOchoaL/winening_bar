# Winening Bar - Sistema de Pagos

Sistema de procesamiento de pagos con arquitectura limpia y patrones de diseño.

## 🏗️ Arquitectura

Este proyecto implementa una arquitectura por capas siguiendo los principios **SOLID** y patrones de diseño creacionales:

```
pagos/
├── domain/              # Capa de Dominio
│   └── builders.py      # PagoBuilder (Builder Pattern)
│
├── infra/               # Capa de Infraestructura
│   └── factories.py     # ProcesadorPagoFactory (Factory Pattern)
│
├── models.py            # Modelo Pago (State Pattern)
├── services.py          # PagoService (Service Layer + DI)
└── views.py             # Vistas Django
```

## 🎯 Patrones Implementados

### 1. Builder Pattern (`domain/builders.py`)
Construcción fluida de objetos Pago con validación:

```python
pago = (
    PagoBuilder()
    .con_monto(150.00)
    .con_metodo_pago('tarjeta')
    .build()
)
```

### 2. Factory Pattern (`infra/factories.py`)
Creación de procesadores según el entorno:

```python
# Cambia comportamiento con variable de entorno
# PAYMENT_PROCESSOR_TYPE=REAL → Producción
# PAYMENT_PROCESSOR_TYPE=MOCK → Desarrollo

procesador = ProcesadorPagoFactory.crear()
```

### 3. Service Layer con Inyección de Dependencias (`services.py`)

```python
# Uso normal
service = PagoService()

# Para testing
mock_procesador = ProcesadorPagoFactory.crear_mock()
service = PagoService(procesador=mock_procesador)
```

### 4. State Pattern (`models.py`)
Transiciones de estado controladas para el ciclo de vida del pago.

## ⚙️ Configuración

### Variables de Entorno

| Variable | Valores | Descripción |
|----------|---------|-------------|
| `PAYMENT_PROCESSOR_TYPE` | `MOCK` / `REAL` | Tipo de procesador de pagos |

### Instalación

```bash
# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones
python manage.py migrate

# Iniciar servidor
python manage.py runserver
```

## 📚 Documentación

Ver documentación completa de la arquitectura en:
- [Wiki: Implementación del Patrón Creacional](docs/WIKI_PATRON_CREACIONAL.md)

## 👥 Equipo

- Arquitectura de Software 2026
- Prof. Nicolás Ramírez Vélez
