# Implementación del Patrón Creacional

## Módulo: Procesamiento de Pagos

**Problema:** La creación y procesamiento de pagos implicaba validar montos, gestionar diferentes métodos de pago y manejar transiciones de estado, todo potencialmente mezclado en la vista.

---

## Solución Arquitectónica

### Arquitectura por Capas

```
┌─────────────────────────────────────────────────────────────────┐
│                     CAPA DE INTERFAZ                            │
│                      (Django Views)                             │
│  Responsabilidad: Capturar request → llamar Service → response │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CAPA DE APLICACIÓN                            │
│                   (PagoService)                                 │
│  Responsabilidad: Orquestar Builder, Factory y lógica          │
└─────────────────────────────────────────────────────────────────┘
                    │                    │
                    ▼                    ▼
┌────────────────────────┐    ┌──────────────────────────────────┐
│   CAPA DE DOMINIO      │    │   CAPA DE INFRAESTRUCTURA       │
│   (domain/)            │    │   (infra/)                       │
│                        │    │                                  │
│   • PagoBuilder        │    │   • ProcesadorPagoFactory        │
│   • Modelo Pago        │    │   • ProcesadorPagoReal           │
│   • State Pattern      │    │   • ProcesadorPagoMock           │
└────────────────────────┘    └──────────────────────────────────┘
```

---

## Diagrama de Clases

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           PagoService                                    │
├─────────────────────────────────────────────────────────────────────────┤
│ - _procesador: ProcesadorPagoBase                                       │
├─────────────────────────────────────────────────────────────────────────┤
│ + __init__(procesador: ProcesadorPagoBase | None)                       │
│ + crear_pago(monto, metodo_pago) → Pago                                 │
│ + procesar_pago(pago: Pago) → dict                                      │
│ + confirmar_pago(pago: Pago) → None                                     │
│ + cancelar_pago(pago: Pago) → None                                      │
└─────────────────────────────────────────────────────────────────────────┘
                │                                    │
                │ usa                                │ usa
                ▼                                    ▼
┌─────────────────────────────┐    ┌─────────────────────────────────────┐
│        PagoBuilder          │    │    «interface»                      │
│        (domain/)            │    │    ProcesadorPagoBase               │
├─────────────────────────────┤    ├─────────────────────────────────────┤
│ - _monto: Decimal           │    │ + procesar(pago: Pago) → dict       │
│ - _metodo_pago: str         │    │ + get_nombre() → str                │
│ - _errors: list             │    └─────────────────────────────────────┘
├─────────────────────────────┤                    △
│ + con_monto(monto) → self   │                    │ implementa
│ + con_metodo_pago(m) → self │         ┌─────────┴─────────┐
│ + build(save) → Pago        │         │                   │
└─────────────────────────────┘         ▼                   ▼
                              ┌──────────────────┐ ┌──────────────────┐
                              │ProcesadorPagoReal│ │ProcesadorPagoMock│
                              │    (infra/)      │ │    (infra/)      │
                              ├──────────────────┤ ├──────────────────┤
                              │+ procesar()      │ │+ procesar()      │
                              │+ get_nombre()    │ │+ get_nombre()    │
                              └──────────────────┘ └──────────────────┘
                                        △                   △
                                        │                   │
                                        └─────────┬─────────┘
                                                  │ crea
                              ┌───────────────────────────────────────┐
                              │       ProcesadorPagoFactory           │
                              ├───────────────────────────────────────┤
                              │ + crear() → ProcesadorPagoBase        │
                              │ + crear_mock() → ProcesadorPagoMock   │
                              │ + crear_real() → ProcesadorPagoReal   │
                              └───────────────────────────────────────┘
```

---

## Patrones Implementados

### 1. Service Layer (SOLID)

**Archivo:** `pagos/services.py`

El `PagoService` actúa como orquestador central, aplicando:
- **Single Responsibility:** Cada clase tiene una única responsabilidad
- **Open/Closed:** Nuevos procesadores se agregan sin modificar código existente
- **Dependency Inversion:** El servicio depende de abstracciones, no implementaciones concretas

### 2. Builder Pattern

**Archivo:** `pagos/domain/builders.py`

`PagoBuilder` permite construir objetos `Pago` de forma:
- **Fluida:** Métodos encadenables (Fluent Interface)
- **Validada:** Verifica datos antes de persistir
- **Expresiva:** Código legible y auto-documentado

```python
# Ejemplo de uso
pago = (
    PagoBuilder()
    .con_monto(150.00)
    .con_metodo_pago('tarjeta')
    .build()
)
```

### 3. Factory Pattern

**Archivo:** `pagos/infra/factories.py`

`ProcesadorPagoFactory` decide qué implementación usar según el entorno:

```python
# Variable de entorno determina el comportamiento
# PAYMENT_PROCESSOR_TYPE=REAL → Usa pasarela real
# PAYMENT_PROCESSOR_TYPE=MOCK → Usa simulador

procesador = ProcesadorPagoFactory.crear()
```

### 4. Inyección de Dependencias

El servicio recibe el procesador como parámetro:

```python
# Uso normal (Factory decide)
service = PagoService()

# Para testing (inyección explícita)
mock = ProcesadorPagoFactory.crear_mock()
service = PagoService(procesador=mock)
```

---

## Justificación de Decisiones

| Decisión | Justificación |
|----------|---------------|
| **Builder en domain/** | La construcción de Pagos es lógica de dominio. El Builder garantiza objetos válidos antes de persistir. |
| **Factory en infra/** | Los procesadores externos (pasarelas de pago) son infraestructura. La Factory abstrae esta complejidad. |
| **Inyección en Service** | Permite testing sin dependencias externas y cambio de comportamiento sin modificar código. |
| **Variable de entorno** | Configuración declarativa: cambiamos `PAYMENT_PROCESSOR_TYPE` sin tocar código. |

---

## Estructura de Archivos

```
pagos/
├── domain/                    # Capa de Dominio
│   ├── __init__.py
│   └── builders.py            # PagoBuilder (Fluent Interface)
│
├── infra/                     # Capa de Infraestructura
│   ├── __init__.py
│   └── factories.py           # Factory + Procesadores MOCK/REAL
│
├── models.py                  # Modelo Pago + State Pattern
├── services.py                # PagoService + Inyección de Dependencias
├── views.py                   # Vistas Django (solo delegan al Service)
└── urls.py
```

---

## Snippet Clave

```python
# services.py
class PagoService:
    def __init__(self, procesador: ProcesadorPagoBase | None = None) -> None:
        # Inyección de Dependencias + Factory
        self._procesador = procesador or ProcesadorPagoFactory.crear()

    def crear_pago(self, monto, metodo_pago='tarjeta') -> Pago:
        # Uso del Builder con Fluent Interface
        pago = (
            PagoBuilder()
            .con_monto(monto)
            .con_metodo_pago(metodo_pago)
            .build()
        )
        return pago

    def procesar_pago(self, pago: Pago) -> dict:
        pago._transicionar(pago.Estado.EN_PROCESO)
        # Delega al procesador inyectado (MOCK o REAL)
        return self._procesador.procesar(pago)
```

---

## Configuración de Entorno

Para cambiar entre procesador MOCK y REAL:

```bash
# Desarrollo (por defecto)
export PAYMENT_PROCESSOR_TYPE=MOCK

# Producción
export PAYMENT_PROCESSOR_TYPE=REAL
```

O en `settings.py`:
```python
import os
os.environ.setdefault('PAYMENT_PROCESSOR_TYPE', 'MOCK')
```

