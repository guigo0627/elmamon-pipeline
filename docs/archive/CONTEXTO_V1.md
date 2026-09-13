# CONTEXTO DEL PROYECTO - Actualizado 2026-09-09

## 🎯 OBJETIVO DEL PROYECTO
Pipeline 100% automatizado para generar videos de YouTube Shorts:
- **Input:** Guion JSON
- **Output:** Video publicable en minutos
- **Restricciones:** 
  - Inversión mínima (usar $10 USD crédito Replicate)
  - 0 intervención manual por video (después de setup inicial)
  - Pipeline completamente automatizado

---

## 📊 ESTADO ACTUAL

### ✅ COMPLETADO:
1. **Etapa 1:** Guiones (funcionando) ✅
2. **Etapa 2:** Aprobación (funcionando) ✅
3. **Fondos:** Fotos reales cocinas/salas (Flux Schnell - FUNCIONA) ✅
4. **Guiones 001 y 002:** Actualizados gato/perro → humanos ✅
5. **Proyecto limpio:** Archivos temporales eliminados ✅
6. **Video ejemplo analizado:** Identificado animación 2D con rigging + lip sync ✅
7. **Investigación APIs:** Meta + Rhubarb (gratis) vs alternativas comerciales ✅

### 🔄 EN PROGRESO:
- **Usuario creando variaciones manuales** de personajes (2-3 expresiones c/u)

### ⏭️ SIGUIENTE:
- **Desarrollo pipeline animación:** Meta Animated Drawings + Rhubarb Lip Sync

---

## 🎭 PERSONAJES DEL UNIVERSO

### **Humanos (USAR):**
```
Familia:
- mamá
- papá  
- hijo_mayor
- hijo_menor
- hija

Círculo social:
- amigo
- mejor_amigo
- compa
- vecino
```

### **Animales:**
❌ **NO usar por ahora** - Solo humanos para fase de validación

---

## 📋 GUIONES ACTUALIZADOS

### **Video 001:**
- **Personajes:** mamá + hijo_mayor
- **Situación:** Mamá pregunta "¿Cómo te fue hoy?"
- **Humor:** Hijo responde filosóficamente sobre la vida/energía cósmica
- **Remate:** Mamá aclara "en el colegio" → Hijo: "Ah, bien mamá"
- **Estado:** ✅ Aprobado y actualizado

### **Video 002:**
- **Personajes:** mamá + hijo_mayor
- **Situación:** Mamá pregunta "¿Ya comiste?"
- **Humor:** Hijo filosofa sobre el significado de comer
- **Remate:** Mamá aclara "si ya te hiciste el desayuno" → Hijo: "Ah sí má, ahorita voy"
- **Estado:** ✅ Aprobado y actualizado

---

## 🎬 ANÁLISIS VIDEO DE EJEMPLO

### **Tipo de animación identificada:**
- ✅ Animación 2D con rigging (movimiento de partes)
- ✅ Lip sync (boca sincronizada con audio)
- ✅ Cambio de expresiones faciales
- ✅ Movimiento de brazos/cuerpo
- ✅ Zoom/movimiento de cámara
- ✅ Efectos adicionales (lágrimas, etc.)

### **Estilo visual:**
- Líneas negras gruesas
- Colores planos
- Estilo webcomic/meme simple
- Mismo estilo que bases del usuario ✅

---

## 🔧 SOLUCIÓN TÉCNICA ELEGIDA

### **Herramientas de animación:**

**✅ OPCIÓN ELEGIDA: Meta Animated Drawings + Rhubarb Lip Sync**

| Componente | Herramienta | Costo | Función |
|------------|-------------|-------|---------|
| Movimiento corporal | Meta Animated Drawings | $0 | Anima brazos, piernas, cuerpo |
| Lip sync | Rhubarb Lip Sync | $0 | Sincroniza boca con audio (6-9 formas) |
| **TOTAL** | - | **$0** | - |

**Ventajas:**
- ✅ Gratis (open source)
- ✅ Automatizable vía Python/CLI
- ✅ Control total
- ✅ Funciona con PNGs del usuario

**Desventaja:**
- ⚠️ NO cambia expresiones automáticamente
- ⚠️ Requiere variaciones pre-hechas

**Por eso:** Usuario crea variaciones manualmente (mama_feliz, mama_enojada, etc.)

---

## 🗂️ ESTRUCTURA DE ARCHIVOS

### **Personajes (naming convention):**
```
{personaje}_{expresion}.png

Ejemplos:
- mama_base.png
- mama_feliz.png
- mama_enojada.png
- mama_sorprendida.png
- hijo_mayor_base.png
- hijo_mayor_feliz.png
- hijo_mayor_triste.png
```

### **Expresiones estándar:**
- `base` - neutral
- `feliz` - sonriendo
- `enojada/enojado` - cejas fruncidas
- `sorprendida/sorprendido` - ojos grandes, boca "O"
- `triste` - cejas caídas
- `confundida/confundido` - cejas arriba

---

## 🚀 PIPELINE COMPLETO

```
1. Guion JSON (01_guion.py)
   ↓
2. Aprobación humana (02_aprobar.py)
   ↓
3. Generar audio (04_audio.py - ElevenLabs) [TODO]
   ↓
4. Generar fondo (03_imagenes.py - Flux)
   ↓
5. Seleccionar expresión según diálogo
   ↓
6. Animar personaje (04_animacion.py - Meta + Rhubarb) [TODO]
   ↓
7. Compositar: fondo + personaje + texto (05_video_final.py) [TODO]
   ↓
8. Combinar con audio → MP4 final
   ↓
VIDEO LISTO
```

---

## 💰 INVERSIÓN HASTA AHORA

**Gastado:**
- Pruebas Flux para variaciones: ~$0.40 USD
- (Fallaron - no mantuvieron consistencia)

**Crédito restante:** ~$9.60 USD

**Costo estimado por video:**
- Audio (ElevenLabs): ~$0.10
- Fondo (Flux Schnell): $0.003
- Animación (Meta + Rhubarb): $0
- **Total:** ~$0.11 USD/video ✅

**10 videos = ~$1.10 USD** (bien dentro de presupuesto)

---

## 📝 APRENDIZAJES CLAVE

### **Lo que NO funcionó:**
❌ Generar variaciones de personajes con Flux (Schnell o Dev)
- Strength 0.95: Cambia TODO (estilo simple → anime elaborado)
- No respeta estilo ultra-minimalista
- Modelos entrenados para "mejorar" imágenes

### **Lo que SÍ funciona:**
✅ Fondos reales (Flux Schnell)
✅ Cutaways/memes (fotos reales)
✅ Variaciones manuales del usuario
✅ Pipeline automatizado para resto del proceso

---

## 🎯 PRÓXIMOS PASOS

### **AHORA:**
1. **Usuario:** Crea variaciones de personajes en Photoshop/GIMP
   - Prioridad: mama (3 expresiones) + hijo_mayor (3 expresiones)
   - Tiempo estimado: 1-2 horas

2. **Desarrollador (yo):** Prepara pipeline animación
   - Instalar Meta Animated Drawings
   - Instalar Rhubarb Lip Sync
   - Crear scripts 04_animacion.py y 05_video_final.py

### **DESPUÉS:**
3. Probar pipeline completo con Video 001
4. Iterar según resultados
5. Generar videos 002-010 si funciona

---

## 📂 ARCHIVOS IMPORTANTES

### **Guiones aprobados:**
- `output/001-20260904/guion.json` ✅
- `output/002-20260904/guion.json` ✅

### **Personajes base:**
- `assets/personajes_base/mama_base.png` ✅
- `assets/personajes_base/hijo1_base.png` ✅
- `assets/personajes_base/papa_base.png`
- (Usuario agregará variaciones aquí)

### **Scripts principales:**
- `scripts/01_guion.py` - Generación guiones
- `scripts/02_aprobar.py` - Aprobación
- `scripts/03_imagenes.py` - Fondos/cutaways
- `scripts/04_animacion.py` - [TODO] Animación
- `scripts/05_video_final.py` - [TODO] Video final

### **Documentación:**
- `CONTEXTO.md` - Este archivo
- `ESTRUCTURA_PROYECTO.md` - Estructura carpetas
- `docs/specs/style_bible.json` - Especificaciones visuales

---

## ⚠️ RESTRICCIONES CRÍTICAS

**Recordar siempre:**
1. $0 inversión adicional (fase validación con $10 USD)
2. 0 intervención manual por video (después de setup)
3. Pipeline 100% automatizado
4. Generación en minutos, no horas

**Por eso:**
- Variaciones manuales solo UNA VEZ (setup inicial)
- Después todo automatizado
- No contratar diseñadores ($50-100 rechazado)
- No editar cada video manualmente

---

## 📊 DECISIONES PENDIENTES

**Ninguna** - Usuario ya decidió:
- ✅ Crear variaciones manualmente
- ✅ Usar Meta + Rhubarb (gratis)
- ✅ Solo personajes humanos por ahora
- ✅ Probar con videos 001 y 002 primero

---

**Última actualización:** 2026-09-09 19:55  
**Estado:** Proyecto limpio y organizado, esperando variaciones de usuario  
**Próximo hito:** Desarrollo pipeline animación cuando usuario termine variaciones  
**Bloqueadores:** Ninguno - trabajo en paralelo
