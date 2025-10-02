# Proyecto de Lectura de Imágenes con Cámara OAK-4W

Este proyecto contiene diferentes programas Python para trabajar con la cámara OAK-4W de Luxonis.

## Requisitos

- Python 3.7 o superior
- Cámara OAK-4W conectada vía USB
- Windows/Linux/macOS

## Instalación

1. Clona o descarga este repositorio
2. Navega al directorio del proyecto:
   ```bash
   cd leer_image
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Programas Disponibles

### 1. `captura_basica.py`
Programa básico que muestra la imagen en tiempo real de la cámara.

**Características:**
- Vista previa en tiempo real (640x480)
- Interfaz simple
- Presiona 'q' para salir

**Uso:**
```bash
python captura_basica.py
```

### 2. `vista_previa.py`
Programa avanzado con vista previa mejorada y función de captura.

**Características:**
- Vista previa en alta resolución (1280x720)
- Contador de FPS en tiempo real
- Información de resolución
- Captura de imágenes con 's'
- Interfaz mejorada

**Controles:**
- `q`: Salir
- `s`: Capturar imagen

**Uso:**
```bash
python vista_previa.py
```

### 3. `capturar_guardar.py`
Programa completo para capturar y guardar imágenes con múltiples modos.

**Características:**
- Resolución Full HD (1920x1080)
- Múltiples modos de captura
- Guardado automático en carpeta 'capturas'
- Calidad JPEG 95%

**Controles:**
- `ESPACIO`: Capturar imagen individual
- `c`: Activar/desactivar modo continuo (cada 2 segundos)
- `s`: Capturar serie de 5 imágenes
- `q`: Salir

**Uso:**
```bash
python capturar_guardar.py
```

## Estructura de Archivos

```
leer_image/
├── requirements.txt          # Dependencias del proyecto
├── captura_basica.py        # Programa básico
├── vista_previa.py          # Vista previa avanzada
├── capturar_guardar.py      # Captura y guardado completo
├── README.md                # Este archivo
└── capturas/                # Directorio de imágenes (se crea automáticamente)
```

## Solución de Problemas

### Error de conexión con la cámara:
1. Verifica que la cámara OAK-4W esté conectada correctamente vía USB
2. Asegúrate de que no haya otros programas usando la cámara
3. Reinicia la conexión USB
4. Verifica que las librerías estén instaladas correctamente

### Error de importación de módulos:
```bash
pip install --upgrade depthai opencv-python numpy
```

### Problemas de rendimiento:
- Cierra otros programas que puedan consumir recursos
- Reduce la resolución en el código si es necesario
- Verifica que tu sistema cumpla con los requisitos mínimos

## Especificaciones Técnicas

- **Resolución máxima**: 1920x1080 (Full HD)
- **FPS máximo**: 30 fps (dependiendo de la resolución)
- **Formato de salida**: JPEG con calidad 95%
- **Conectividad**: USB 3.0 recomendado

## Contribuciones

Para contribuir al proyecto:
1. Haz un fork del repositorio
2. Crea una rama para tu feature
3. Haz commit de tus cambios
4. Push a la rama
5. Abre un Pull Request

## Licencia

Este proyecto está bajo licencia MIT. Ver archivo LICENSE para detalles.

## Contacto

Para soporte técnico o preguntas, abre un issue en el repositorio.