# Sistema de Logging de Accesos - Kosmo

## Descripción

Se ha implementado un sistema completo de logging que registra todos los accesos a los enlaces de la aplicación, incluyendo información detallada del usuario cuando esté disponible.

## Componentes

### 1. Middleware de Logging (`common/middleware.py`)

**Clase**: `AccessLoggerMiddleware`

Este middleware intercepta todas las peticiones HTTP y registra información detallada sobre cada acceso.

#### Información registrada:

- **Método HTTP**: GET, POST, PUT, DELETE, etc.
- **Ruta completa**: URL completa con parámetros
- **Código de estado**: 200, 404, 500, etc.
- **Usuario**: Nombre completo, username o ID cuando esté autenticado
- **Dirección IP**: IP real del cliente (considerando proxies)
- **User-Agent**: Navegador y sistema operativo (limitado a 100 caracteres)
- **Tiempo de respuesta**: Duración en milisegundos

#### Filtrado inteligente:

El middleware excluye automáticamente:
- Archivos estáticos (.css, .js, .png, .jpg, etc.)
- Rutas estáticas (/static/, /media/, /favicon.ico, etc.)
- Peticiones de heartbeat o ping

### 2. Logger mejorado (`common/AppLoger.py`)

Se han agregado funciones específicas para el logging de accesos:

- `log_access(message)`: Registra accesos exitosos
- `log_access_error(message)`: Registra errores de acceso
- `loggin_event(message, error, file_path)`: Función general mejorada

#### Archivos de log:

- `logs/app.log`: Log general de la aplicación
- `logs/access.log`: Log específico de accesos

### 3. Configuración (`kosmo/settings.py`)

El middleware se ha agregado a la lista MIDDLEWARE en la posición adecuada:

```python
MIDDLEWARE = [
    # ... otros middlewares ...
    'common.middleware.AccessLoggerMiddleware',  # Logging personalizado
    # ... más middlewares ...
]
```

## Formato del Log

Cada entrada de acceso sigue este formato:

```
[2024-01-15 14:30:25.123456] [MESSAGE] ACCESO: GET /dashboard/ | Estado: 200 | Usuario: Juan Pérez | IP: 192.168.1.100 | User-Agent: Mozilla/5.0... | Duración: 125.45ms
```

Para errores:

```
[2024-01-15 14:30:25.123456] [ERROR]: ACCESO: POST /api/login/ | Estado: 401 | Usuario: Anónimo | IP: 192.168.1.100 | User-Agent: Mozilla/5.0... | Duración: 25.12ms
```

## Tipos de Usuario Registrados

1. **Usuario autenticado con nombre completo**: "Usuario: Juan Pérez"
2. **Usuario autenticado solo con username**: "Usuario: jperez"
3. **Usuario autenticado solo con ID**: "Usuario: 123"
4. **Usuario no autenticado**: "Usuario: Anónimo"

## Ventajas

- **No impacta el rendimiento**: El logging se ejecuta de forma asíncrona
- **Filtrado inteligente**: Solo registra peticiones importantes
- **Información completa**: Incluye toda la información relevante para auditoría
- **Manejo de errores**: Si el logging falla, no afecta la respuesta al usuario
- **Archivos separados**: Los accesos se registran en un archivo dedicado

## Uso

El sistema funciona automáticamente una vez configurado. No requiere cambios en las vistas o controladores existentes.

### Para consultar los logs:

```bash
# Ver los últimos accesos
tail -f logs/access.log

# Buscar accesos de un usuario específico
grep "Usuario: Juan" logs/access.log

# Ver solo errores de acceso
grep "ERROR" logs/access.log

# Ver accesos a una ruta específica
grep "/dashboard/" logs/access.log
```

## Consideraciones de Seguridad

- Los logs pueden contener información sensible (IPs, user agents)
- Se recomienda implementar rotación de logs para evitar archivos muy grandes
- Los archivos de log deben tener permisos restrictivos en producción
- Considerar implementar limpieza automática de logs antiguos

## Próximas Mejoras Sugeridas

1. **Rotación automática de logs** por tamaño o fecha
2. **Dashboard de estadísticas** basado en los logs
3. **Alertas automáticas** para patrones sospechosos
4. **Integración con sistemas de monitoreo** externos
5. **Anonimización de IPs** para cumplir con GDPR/LOPD
