# ESTRUCTURA DEL PROYECTO - ElMamón Pipeline

## 📁 ESTRUCTURA LIMPIA (2026-09-09)

```
elmamon-pipeline/
├── assets/                          # 🎨 ASSETS PERMANENTES
│   └── personajes_base/            # ✅ Personajes base (MANTENER)
│       ├── mama_base.png
│       ├── mama_feliz.png
│       ├── mama_enojada.png
│       ├── hijo_mayor_base.png
│       ├── hijo_mayor_feliz.png
│       └── ... (agregar más según necesidad)
│
├── assets_temp/                     # 📦 REFERENCIAS Y TEMPORAL
│   ├── guiones/                    # Guiones generados con timestamps
│   ├── personajes_referencia.png   # Imágenes de referencia usuario
│   └── gato_referencia.png
│
├── scripts/                         # 🔧 SCRIPTS DEL PIPELINE
│   ├── 01_guion.py                 # Generación de guiones (LLM)
│   ├── 02_aprobar.py               # Aprobación humana
│   ├── 03_imagenes.py              # Generación de fondos/cutaways
│   ├── 03_imagenes_base.py         # [deprecated] Intentos generación personajes
│   ├── 03_variaciones.py           # [deprecated] Intentos variaciones
│   ├── 04_audio.py                 # [TODO] Audio con ElevenLabs
│   ├── 04_animacion.py             # [TODO] Meta + Rhubarb
│   ├── 05_video_final.py           # [TODO] Composición final
│   └── utils.py                    # Utilidades comunes
│
├── output/                          # 📤 OUTPUT DE VIDEOS
│   ├── 001-20260904/               # Video 001
│   │   ├── guion.json              # ✅ Guión aprobado (mamá + hijo_mayor)
│   │   ├── APROBADO.txt
│   │   ├── audio/                  # (vacío - pendiente)
│   │   ├── animaciones/            # (vacío - pendiente)
│   │   ├── fondo/                  # Fondos generados
│   │   ├── cutaways/               # Cutaways generados
│   │   └── personajes/             # (vacío)
│   │
│   ├── 002-20260904/               # Video 002
│   │   ├── guion.json              # ✅ Guión aprobado (mamá + hijo_mayor)
│   │   ├── APROBADO.txt
│   │   └── ... (misma estructura)
│   │
│   ├── video_analisis/             # Frames del video de ejemplo
│   │   └── frame_*.png
│   │
│   └── variaciones_prueba/         # [deprecated] Intentos Flux variaciones
│
├── docs/                            # 📚 DOCUMENTACIÓN
│   ├── specs/
│   │   └── style_bible.json
│   ├── prompts/
│   ├── guides/
│   └── research/
│
├── config/                          # ⚙️ CONFIGURACIÓN
│   └── video_config.json
│
├── logs/                            # 📝 LOGS
│
├── .env                             # 🔐 API KEYS
├── CONTEXTO.md                      # 📋 Estado del proyecto
├── ESTRUCTURA_PROYECTO.md           # 📁 Este archivo
└── README.md                        # 📖 README principal
```

---

## 🧹 LIMPIEZA REALIZADA

### **Archivos eliminados:**
- ❌ `output/001-20260904/*validacion*.json` (10 archivos)
- ❌ `output/002-20260904/*validacion*.json` (3 archivos)
- ❌ `assets_temp/guiones/*intento*.json` (4 archivos)

### **Archivos actualizados:**
- ✅ `output/001-20260904/guion.json` - gato → hijo_mayor
- ✅ `output/002-20260904/guion.json` - gato → hijo_mayor, perro → desayuno

---

## 📋 GUIONES ACTUALIZADOS

### **Video 001:**
```json
Personajes: mamá + hijo_mayor
Situación: Mamá pregunta "¿Cómo te fue hoy?"
Humor: Hijo responde filosóficamente sobre la vida
Remate: Mamá aclara "en el colegio" → Hijo dice "bien mamá"
Estado: ✅ Aprobado, actualizado a humanos
```

### **Video 002:**
```json
Personajes: mamá + hijo_mayor
Situación: Mamá pregunta "¿Ya comiste?"
Humor: Hijo filosofa sobre el significado de comer
Remate: Mamá aclara "si ya te hiciste el desayuno" → Hijo dice "ahorita voy"
Estado: ✅ Aprobado, actualizado a humanos
```

---

## 🎭 PERSONAJES DEL UNIVERSO

### **Humanos disponibles:**
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
❌ **NO usar por ahora** (gato, perro, loro)

---

## 📝 NAMING CONVENTION

### **Archivos de personajes:**
```
{personaje}_{expresion}.png

Ejemplos:
- mama_base.png
- mama_feliz.png
- mama_enojada.png
- hijo_mayor_base.png
- hijo_mayor_feliz.png
- papa_sorprendido.png
```

### **Expresiones estándar:**
```
- base (neutral)
- feliz (sonriendo)
- enojada/enojado
- sorprendida/sorprendido
- triste
- confundida/confundido
- burlón/burlona
```

---

## 🚀 PRÓXIMOS PASOS

### **1. Usuario crea personajes:**
```
Prioridad alta:
- mama_base.png ✅ (ya existe)
- mama_feliz.png
- mama_enojada.png
- hijo_mayor_base.png ✅ (ya existe)
- hijo_mayor_feliz.png
- hijo_mayor_triste.png
```

### **2. Desarrollar pipeline animación:**
```
- Instalar Meta Animated Drawings
- Instalar Rhubarb Lip Sync
- Crear 04_animacion.py
- Crear 05_video_final.py
- Integrar todo el pipeline
```

### **3. Probar con Video 001:**
```
Guion → Audio → Fondo → Animación → Video final
```

---

## ⚠️ NOTAS IMPORTANTES

1. **NO TOCAR:** `assets/personajes_base/` - Son las bases del usuario
2. **Guiones válidos:** Solo 001 y 002 (actualizados a humanos)
3. **Animales:** Descartados por ahora, enfoque en humanos
4. **Variaciones Flux:** Fallaron, usuario las crea manualmente

---

**Última actualización:** 2026-09-09 19:55
**Estado:** Proyecto limpio y organizado, listo para desarrollo de animación
