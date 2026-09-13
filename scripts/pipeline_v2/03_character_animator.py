#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO 3: Character Animator
Sistema de animación de personajes stick con PIL/Pillow
Input:  animation_plan.json
Output: Frames animados de personajes
"""

import sys
import os
from pathlib import Path
import json
import math

# Fix encoding UTF-8
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import setup_logger

logger = setup_logger('animator')

try:
    from PIL import Image, ImageDraw
    import math
    import random
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.error("❌ PIL no disponible")

# ========== FUNCIONES PARA DIBUJO "MANO ALZADA" ==========

def draw_hand_drawn_ellipse(draw, bbox, fill=None, outline=None, width=1):
    """
    Dibuja una elipse con aspecto de mano alzada (irregular)
    Usa seed basada en posición para consistencia entre frames

    Args:
        draw: ImageDraw object
        bbox: [x1, y1, x2, y2] bounding box
        fill: Color de relleno
        outline: Color de borde
        width: Ancho del borde
    """
    x1, y1, x2, y2 = bbox
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    radius_x = (x2 - x1) / 2
    radius_y = (y2 - y1) / 2

    # SEED FIJA basada en posición para evitar temblor entre frames
    seed_value = int(center_x * 1000 + center_y * 1000 + radius_x * 100)
    random.seed(seed_value)

    # Generar puntos de la elipse con pequeñas variaciones
    points = []
    num_points = 32  # Más puntos = más suave

    for i in range(num_points):
        angle = (2 * math.pi * i) / num_points

        # Variación pequeña para simular mano alzada (±3%)
        variation_x = random.uniform(0.97, 1.03)
        variation_y = random.uniform(0.97, 1.03)

        x = center_x + radius_x * math.cos(angle) * variation_x
        y = center_y + radius_y * math.sin(angle) * variation_y

        points.append((x, y))

    # Dibujar polígono
    if fill:
        draw.polygon(points, fill=fill)
    if outline:
        draw.line(points + [points[0]], fill=outline, width=width)

def add_slight_jitter(value, max_jitter=2):
    """Agrega pequeña variación a un valor para simular trazo manual"""
    return value + random.randint(-max_jitter, max_jitter)

def draw_hand_drawn_line(draw, start, end, fill='black', width=1, curve_amount=0.15):
    """
    Dibuja una línea CURVA con aspecto de mano alzada (irregular)
    Usa seed basada en posición para consistencia entre frames

    Args:
        draw: ImageDraw object
        start: (x1, y1) punto inicial
        end: (x2, y2) punto final
        fill: Color de la línea
        width: Ancho de la línea
        curve_amount: Cantidad de curvatura (0.0-1.0)
    """
    x1, y1 = start
    x2, y2 = end

    # SEED FIJA basada en posición para evitar temblor entre frames
    seed_value = int(x1 * 1000 + y1 * 1000 + x2 * 100 + y2 * 100)
    random.seed(seed_value)

    # Número de segmentos para la línea curva (más segmentos = más suave)
    num_segments = 12

    # Calcular punto de control para curva cuadrática (curva natural)
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2

    # Offset perpendicular para crear curvatura
    dx = x2 - x1
    dy = y2 - y1
    length = (dx**2 + dy**2) ** 0.5

    if length > 0:
        # Perpendicular normalizado
        perp_x = -dy / length
        perp_y = dx / length

        # Punto de control desplazado (crea la curva)
        curve_offset = length * curve_amount
        control_x = mid_x + perp_x * curve_offset
        control_y = mid_y + perp_y * curve_offset
    else:
        control_x = mid_x
        control_y = mid_y

    # Generar puntos de curva cuadrática de Bézier con variaciones
    points = []

    for i in range(num_segments + 1):
        t = i / num_segments

        # Curva cuadrática de Bézier: P = (1-t)²P0 + 2(1-t)tP1 + t²P2
        x = (1-t)**2 * x1 + 2*(1-t)*t * control_x + t**2 * x2
        y = (1-t)**2 * y1 + 2*(1-t)*t * control_y + t**2 * y2

        # Pequeña variación para aspecto "mano alzada"
        x += random.uniform(-2, 2)
        y += random.uniform(-2, 2)

        points.append((x, y))

    # Dibujar la línea curva
    draw.line(points, fill=fill, width=width, joint='curve')


class StickFigure:
    """Personaje stick figure animable"""

    def __init__(self, gender='neutral', position=(540, 960), scale=1.0):
        """
        Args:
            gender: 'male', 'female', 'neutral'
            position: (x, y) centro del personaje
            scale: Escala del personaje (1.0 = normal)
        """
        self.gender = gender
        self.position = position
        self.scale = scale

        # PROPORCIONES ESTILO CARTOON (cabeza ENORME, cuerpo pequeño)
        self.head_radius = int(90 * scale)  # CABEZA MUY GRANDE
        self.body_height = int(130 * scale)  # Cuerpo MÁS ALARGADO hacia abajo
        self.body_width = int(75 * scale)  # Cuerpo ancho ovalado
        self.arm_length = int(120 * scale)  # Brazos largos pero proporcionales
        self.arm_width = int(4 * scale)  # Grosor CORRECTO (sin cambiar)
        self.leg_length = int(65 * scale)  # Piernas cortas
        self.leg_width = int(8 * scale)  # Piernas FLACAS (líneas delgadas)
        self.hand_size = int(24 * scale)
        self.foot_size = int(30 * scale)

        # OJOS GRANDES estilo cartoon (40% de la cara)
        self.eye_radius = int(18 * scale)
        self.pupil_radius = int(10 * scale)
        self.eye_separation = int(30 * scale)

        # Estado actual
        self.expression = 'neutral'
        self.gesture = 'idle'
        self.mouth_state = 'closed'

        # Colores CARTOON (planos, vibrantes)
        self.line_color = 'black'
        self.line_width = 6  # Outline moderado
        self.skin_color = 'white'  # Piel BLANCA

        # Colores por género
        if gender == 'female':
            self.has_dress = True
            self.body_color = 'white'  # Ropa BLANCA
            self.has_hair = True
            self.hair_color = '#2C1810'  # Café oscuro
        else:
            self.has_dress = False
            self.body_color = 'white'  # Ropa BLANCA
            self.has_hair = False

    def set_expression(self, expression):
        """Cambia expresión facial"""
        self.expression = expression

    def set_gesture(self, gesture):
        """Cambia gesto corporal"""
        self.gesture = gesture

    def set_mouth_state(self, state):
        """Cambia estado de boca (para lip sync)"""
        self.mouth_state = state  # 'closed', 'semi', 'open'

    def _draw_heart_shaped_head(self, draw, x, head_center_y):
        """Dibuja cabeza femenina en forma de CORAZÓN con mejillas definidas"""
        import math

        # Parámetros de la forma
        top_y = head_center_y - self.head_radius
        bottom_y = head_center_y + self.head_radius

        # Generar puntos para forma de corazón con mejillas
        points = []
        num_points = 40  # Suficientes puntos para forma suave

        for i in range(num_points):
            # Ángulo de 0 a 2*pi
            angle = (2 * math.pi * i) / num_points

            # Forma de corazón: ancha arriba, se estrecha abajo con mejillas
            if angle < math.pi / 2 or angle > 3 * math.pi / 2:  # Parte superior
                # Ancho completo arriba (frente amplia)
                radius = self.head_radius
            elif angle < math.pi:  # Lado izquierdo bajando
                # Se estrecha con curva de mejilla
                t = (angle - math.pi/2) / (math.pi/2)  # 0 a 1
                # Curva que va de radio completo a 60% (mejilla)
                radius = self.head_radius * (1.0 - 0.25 * math.sin(t * math.pi))
            else:  # Lado derecho bajando
                # Simétrico
                t = (angle - math.pi) / (math.pi/2)
                radius = self.head_radius * (1.0 - 0.25 * math.sin(t * math.pi))

            # Mentón puntiagudo (parte inferior)
            if 0.4 * math.pi < angle < 0.6 * math.pi or 1.4 * math.pi < angle < 1.6 * math.pi:
                # Estrechar más en la parte del mentón
                radius *= 0.7

            # Calcular posición con variación irregular
            variation = random.uniform(0.97, 1.03)
            px = x + radius * math.cos(angle) * variation
            py = head_center_y + radius * math.sin(angle) * variation

            points.append((px, py))

        # Dibujar forma de corazón
        draw.polygon(points, fill=self.skin_color)
        draw.line(points + [points[0]], fill=self.line_color, width=self.line_width, joint='curve')

    def draw(self, draw_obj, blink=False):
        """
        Dibuja el personaje en un objeto ImageDraw

        Args:
            draw_obj: PIL.ImageDraw objeto
            blink: Si True, dibuja ojos cerrados (parpadeo)
        """
        x, y = self.position

        # Cabeza
        self._draw_head(draw_obj, x, y, blink=blink)

        # Cuerpo
        self._draw_body(draw_obj, x, y)

        # Brazos (según gesture)
        self._draw_arms(draw_obj, x, y)

        # Piernas
        self._draw_legs(draw_obj, x, y)

    def _draw_head(self, draw, x, y, blink=False):
        """Dibuja cabeza ESTILO CARTOON con ojos GRANDES

        Args:
            blink: Si True, dibuja ojos cerrados (parpadeo)
        """
        head_center_y = y - self.body_height - self.head_radius

        # CABELLO PRIMERO (si aplica)
        if self.has_hair:
            self._draw_female_hair(draw, x, head_center_y)

        # CABEZA: circular para todos (cara de corazón rechazada)
        head_box = [
            x - self.head_radius,
            y - self.body_height - self.head_radius * 2,
            x + self.head_radius,
            y - self.body_height
        ]
        draw_hand_drawn_ellipse(draw, head_box, fill=self.skin_color, outline=self.line_color, width=self.line_width)

        # OJOS GRANDES ESTILO CARTOON (40% de la cara)
        eye_y = y - self.body_height - int(self.head_radius * 1.2)
        left_eye_x = x - self.eye_separation // 2
        right_eye_x = x + self.eye_separation // 2

        if blink:
            # OJOS CERRADOS (parpadeo) - líneas curvas horizontales
            draw_hand_drawn_line(draw,
                (left_eye_x - self.eye_radius, eye_y),
                (left_eye_x + self.eye_radius, eye_y),
                fill=self.line_color, width=4, curve_amount=0.08)
            draw_hand_drawn_line(draw,
                (right_eye_x - self.eye_radius, eye_y),
                (right_eye_x + self.eye_radius, eye_y),
                fill=self.line_color, width=4, curve_amount=0.08)
        else:
            # OJOS ABIERTOS (normal)
            # Ojo izquierdo - Blanco del ojo (irregular)
            draw_hand_drawn_ellipse(draw, [
                left_eye_x - self.eye_radius, eye_y - self.eye_radius,
                left_eye_x + self.eye_radius, eye_y + self.eye_radius
            ], fill='white', outline=self.line_color, width=4)

            # Pupila
            pupil_offset_x = 0
            pupil_offset_y = 2  # Mirando ligeramente abajo por defecto

            if self.expression in ['sumiso', 'serio_sumiso', 'regañado']:
                pupil_offset_y = 6  # Mirar más abajo

            draw_hand_drawn_ellipse(draw, [
                left_eye_x - self.pupil_radius + pupil_offset_x,
                eye_y - self.pupil_radius + pupil_offset_y,
                left_eye_x + self.pupil_radius + pupil_offset_x,
                eye_y + self.pupil_radius + pupil_offset_y
            ], fill='black')

            # Brillo en pupila (punto blanco)
            shine_size = 5
            draw_hand_drawn_ellipse(draw, [
                left_eye_x - 4 + pupil_offset_x, eye_y - 4 + pupil_offset_y,
                left_eye_x - 4 + shine_size + pupil_offset_x, eye_y - 4 + shine_size + pupil_offset_y
            ], fill='white')

            # Ojo derecho
            draw_hand_drawn_ellipse(draw, [
                right_eye_x - self.eye_radius, eye_y - self.eye_radius,
                right_eye_x + self.eye_radius, eye_y + self.eye_radius
            ], fill='white', outline=self.line_color, width=4)

            draw_hand_drawn_ellipse(draw, [
                right_eye_x - self.pupil_radius + pupil_offset_x,
                eye_y - self.pupil_radius + pupil_offset_y,
                right_eye_x + self.pupil_radius + pupil_offset_x,
                eye_y + self.pupil_radius + pupil_offset_y
            ], fill='black')

            draw_hand_drawn_ellipse(draw, [
                right_eye_x + 4 + pupil_offset_x, eye_y - 4 + pupil_offset_y,
                right_eye_x + 4 + shine_size + pupil_offset_x, eye_y - 4 + shine_size + pupil_offset_y
            ], fill='white')

        # CEJAS según expresión
        brow_y = eye_y - self.eye_radius - 8

        if self.expression in ['enojado', 'enojada', 'defensiva']:
            # Cejas fruncidas hacia abajo
            draw.line([left_eye_x - 20, brow_y - 5, left_eye_x + 5, brow_y + 5],
                     fill=self.line_color, width=5)
            draw.line([right_eye_x - 5, brow_y + 5, right_eye_x + 20, brow_y - 5],
                     fill=self.line_color, width=5)

        elif self.expression in ['triste', 'arrepentida', 'disculpa']:
            # Cejas levantadas (triste)
            draw.arc([left_eye_x - 20, brow_y - 8, left_eye_x + 5, brow_y + 2],
                    180, 360, fill=self.line_color, width=4)
            draw.arc([right_eye_x - 5, brow_y - 8, right_eye_x + 20, brow_y + 2],
                    180, 360, fill=self.line_color, width=4)

        elif self.expression in ['sorprendido', 'sorprendida']:
            # Cejas levantadas (sorpresa)
            draw.line([left_eye_x - 20, brow_y, left_eye_x + 5, brow_y - 8],
                     fill=self.line_color, width=4)
            draw.line([right_eye_x - 5, brow_y - 8, right_eye_x + 20, brow_y],
                     fill=self.line_color, width=4)

        # BOCA según lip sync
        mouth_y = y - self.body_height - int(self.head_radius * 0.4)

        if self.mouth_state == 'closed':
            # Sonrisa simple
            draw.line([x - 20, mouth_y, x + 20, mouth_y], fill=self.line_color, width=4)

        elif self.mouth_state == 'semi':
            # Círculo pequeño (irregular)
            draw_hand_drawn_ellipse(draw, [x - 10, mouth_y - 8, x + 10, mouth_y + 8],
                        fill='#8B4513', outline=self.line_color, width=3)

        elif self.mouth_state == 'open':
            # Círculo grande / O (irregular)
            draw_hand_drawn_ellipse(draw, [x - 16, mouth_y - 12, x + 16, mouth_y + 12],
                        fill='#8B4513', outline=self.line_color, width=3)

    def _draw_body(self, draw, x, y):
        """Dibuja cuerpo como ÓVALO IRREGULAR (mano alzada)"""
        body_top = y - self.body_height
        body_bottom = y - 5
        body_center_y = (body_top + body_bottom) // 2

        # CUERPO COMO ÓVALO IRREGULAR (igual estilo que la cabeza)
        # Ancho y alto del óvalo del cuerpo
        oval_width = self.body_width // 2
        oval_height = (body_bottom - body_top) // 2

        body_oval_box = [
            x - oval_width,
            body_center_y - oval_height,
            x + oval_width,
            body_center_y + oval_height
        ]

        draw_hand_drawn_ellipse(draw, body_oval_box,
                               fill=self.body_color,
                               outline=self.line_color,
                               width=self.line_width)

    def _draw_arms(self, draw, x, y):
        """Dibuja brazos CURVOS desde el BORDE del óvalo del cuerpo (hombros reales)"""
        # Calcular geometría del óvalo del cuerpo
        body_top = y - self.body_height
        body_bottom = y - 5
        body_center_y = (body_top + body_bottom) // 2

        # Punto de inicio de brazos: 30% desde arriba del óvalo
        shoulder_y_relative = 0.3  # 30% desde arriba
        shoulder_y = body_top + int((body_bottom - body_top) * shoulder_y_relative)

        # Radio horizontal del óvalo (para calcular borde)
        oval_width = self.body_width // 2
        oval_height = (body_bottom - body_top) // 2

        # Calcular punto en el BORDE del óvalo (ecuación de elipse)
        # x = cx ± a * sqrt(1 - (y - cy)²/b²)
        y_offset_from_center = shoulder_y - body_center_y

        if oval_height > 0:
            ratio = 1 - (y_offset_from_center ** 2) / (oval_height ** 2)
            if ratio > 0:
                x_offset = int(oval_width * (ratio ** 0.5))
            else:
                x_offset = 0
        else:
            x_offset = oval_width

        # Puntos de inicio en el BORDE del óvalo
        shoulder_x_left = x - x_offset
        shoulder_x_right = x + x_offset

        if self.gesture in ['idle', 'quieto_escuchando']:
            # Brazos a los lados
            # Brazo izquierdo
            draw.line([x, shoulder_y, x - self.arm_length, shoulder_y + 40],
                     fill=self.line_color, width=self.line_width)
            # Brazo derecho
            draw.line([x, shoulder_y, x + self.arm_length, shoulder_y + 40],
                     fill=self.line_color, width=self.line_width)

        elif self.gesture in ['hands_together_apologetic', 'hands_apologetic']:
            # Manos juntas al frente - brazos desde BORDE del óvalo
            draw_hand_drawn_line(draw, (shoulder_x_left, shoulder_y), (x - 15, shoulder_y + self.arm_length),
                     fill=self.line_color, width=self.arm_width)
            draw_hand_drawn_line(draw, (shoulder_x_right, shoulder_y), (x + 15, shoulder_y + self.arm_length),
                     fill=self.line_color, width=self.arm_width)
            # Manos juntas (irregular)
            draw_hand_drawn_ellipse(draw, [x - 10, shoulder_y + self.arm_length, x + 10, shoulder_y + self.arm_length + 10],
                        fill='#FFE4B5', outline=self.line_color, width=2)

        elif self.gesture in ['hand_gestures_explanatory', 'gestos_con_manos']:
            # Brazos gesticulando más gruesos
            draw.line([x, shoulder_y, x - 40, shoulder_y - 20],
                     fill=self.line_color, width=self.arm_width)
            draw.line([x, shoulder_y, x + 50, shoulder_y + 10],
                     fill=self.line_color, width=self.arm_width)

        elif self.gesture in ['pointing_finger_soft']:
            # Brazo señalando suavemente, más grueso
            draw.line([x, shoulder_y, x - self.arm_length, shoulder_y + 40],
                     fill=self.line_color, width=self.arm_width)
            draw.line([x, shoulder_y, x + 40, shoulder_y + 10],
                     fill=self.line_color, width=self.arm_width)
            draw.line([x + 40, shoulder_y + 10, x + 60, shoulder_y + 5],
                     fill=self.line_color, width=3)  # Dedo

        elif self.gesture in ['hands_up_defensive']:
            # Manos arriba defensivas, brazos gruesos
            draw.line([x, shoulder_y, x - 30, shoulder_y - 40],
                     fill=self.line_color, width=self.arm_width)
            draw.line([x, shoulder_y, x + 30, shoulder_y - 40],
                     fill=self.line_color, width=self.arm_width)
            # Palmas (irregulares)
            draw_hand_drawn_ellipse(draw, [x - 35, shoulder_y - 50, x - 25, shoulder_y - 40],
                        fill='#FFE4B5', outline=self.line_color, width=2)
            draw_hand_drawn_ellipse(draw, [x + 25, shoulder_y - 50, x + 35, shoulder_y - 40],
                        fill='#FFE4B5', outline=self.line_color, width=2)

        elif self.gesture in ['arms_at_sides', 'brazos_a_los_lados']:
            # Brazos pegados al cuerpo, más gruesos
            draw.line([x, shoulder_y, x - 10, y - 20],
                     fill=self.line_color, width=self.arm_width)
            draw.line([x, shoulder_y, x + 10, y - 20],
                     fill=self.line_color, width=self.arm_width)

        elif self.gesture in ['arms_crossed', 'brazos_cruzados']:
            # Brazos cruzados - desde BORDE del óvalo, largos y curvos
            draw_hand_drawn_line(draw, (shoulder_x_left, shoulder_y), (x + int(self.arm_length * 0.3), shoulder_y + int(self.arm_length * 0.9)),
                     fill=self.line_color, width=self.arm_width)
            draw_hand_drawn_line(draw, (shoulder_x_right, shoulder_y), (x - int(self.arm_length * 0.3), shoulder_y + int(self.arm_length * 0.9)),
                     fill=self.line_color, width=self.arm_width)

        elif self.gesture in ['phone_call', 'celular', 'llamada']:
            # Hablando por celular - brazo derecho levantado a la oreja
            # Brazo izquierdo: a un lado relajado
            draw_hand_drawn_line(draw, (shoulder_x_left, shoulder_y),
                               (shoulder_x_left - int(self.arm_length * 0.3), shoulder_y + int(self.arm_length * 0.8)),
                               fill=self.line_color, width=self.arm_width)

            # Brazo derecho: levantado hacia la oreja (lado de la cabeza)
            head_side_x = x + int(self.head_radius * 0.7)  # Lado derecho de la cabeza
            head_ear_y = shoulder_y - int(self.body_height * 0.4)  # Altura de la oreja

            # Brazo derecho curvado hacia la oreja
            draw_hand_drawn_line(draw, (shoulder_x_right, shoulder_y),
                               (head_side_x + 10, head_ear_y),
                               fill=self.line_color, width=self.arm_width)

            # Celular (DOBLE DE GRANDE - más visible)
            phone_w = 36  # Doble: 18 → 36
            phone_h = 60  # Doble: 30 → 60
            phone_x = head_side_x + 5
            phone_y_top = head_ear_y - phone_h//2
            phone_y_bot = head_ear_y + phone_h//2

            # Rectángulo del celular (más grueso)
            draw.rectangle([phone_x, phone_y_top, phone_x + phone_w, phone_y_bot],
                          fill='#2C2C2C', outline=self.line_color, width=4)

            # Pantalla del celular (azul más grande)
            draw.rectangle([phone_x + 5, phone_y_top + 8, phone_x + phone_w - 5, phone_y_bot - 8],
                          fill='#4A90E2', outline='#333333', width=2)

        else:
            # Default: brazos normales desde BORDE del óvalo
            draw_hand_drawn_line(draw, (shoulder_x_left, shoulder_y), (shoulder_x_left - int(self.arm_length * 0.5), shoulder_y + self.arm_length),
                     fill=self.line_color, width=self.arm_width)
            draw_hand_drawn_line(draw, (shoulder_x_right, shoulder_y), (shoulder_x_right + int(self.arm_length * 0.5), shoulder_y + self.arm_length),
                     fill=self.line_color, width=self.arm_width)

    def _draw_legs(self, draw, x, y):
        """Dibuja piernas FLACAS blancas con borde negro (líneas con efecto de borde)"""
        leg_bottom_y = y + self.leg_length

        # Posiciones de piernas
        leg_x_left = x - 30
        leg_x_right = x + 30

        # Pierna izquierda: línea negra gruesa + línea blanca delgada encima
        draw.line([x, y, leg_x_left, leg_bottom_y],
                 fill=self.line_color, width=self.leg_width + 4)  # Borde negro
        draw.line([x, y, leg_x_left, leg_bottom_y],
                 fill='white', width=self.leg_width)  # Línea blanca

        # Pierna derecha: línea negra gruesa + línea blanca delgada encima
        draw.line([x, y, leg_x_right, leg_bottom_y],
                 fill=self.line_color, width=self.leg_width + 4)  # Borde negro
        draw.line([x, y, leg_x_right, leg_bottom_y],
                 fill='white', width=self.leg_width)  # Línea blanca

        # Pies MÁS GRANDES (óvalos horizontales irregulares)
        foot_w = self.foot_size
        foot_h = int(self.foot_size * 0.6)

        # Pie izquierdo (irregular) - ZAPATOS NEGROS
        draw_hand_drawn_ellipse(draw, [leg_x_left - foot_w, leg_bottom_y - foot_h//2,
                     leg_x_left + foot_w//2, leg_bottom_y + foot_h//2],
                    fill='black', outline=self.line_color, width=3)

        # Pie derecho (irregular) - ZAPATOS NEGROS
        draw_hand_drawn_ellipse(draw, [leg_x_right - foot_w//2, leg_bottom_y - foot_h//2,
                     leg_x_right + foot_w, leg_bottom_y + foot_h//2],
                    fill='black', outline=self.line_color, width=3)

    def _draw_female_hair(self, draw, x, head_center_y):
        """Dibuja cabello femenino - líneas SEPARADAS que nacen arriba y caen a los lados"""
        # Punto de inicio del cabello (ARRIBA de la cabeza)
        hair_top_y = head_center_y - self.head_radius - 20

        # CABELLO CON 5 LÍNEAS POR LADO (más separadas, menos densas)
        # Todas las líneas NACEN en hair_top_y y CAEN hacia los lados

        # LADO IZQUIERDO - 5 líneas separadas cayendo hacia la izquierda
        # Formato: (x_inicio, x_final, y_final, grosor)
        left_positions = [
            (-30, -self.head_radius - 30, head_center_y + 15, 7),  # Línea 1 (más externa)
            (-20, -self.head_radius - 20, head_center_y + 5, 6),   # Línea 2
            (-10, -self.head_radius - 12, head_center_y - 5, 6),   # Línea 3
            (0, -self.head_radius - 5, head_center_y - 12, 5),     # Línea 4
            (10, -self.head_radius, head_center_y - 18, 5),        # Línea 5 (más interna)
        ]

        for x_start, x_final, y_final, grosor in left_positions:
            draw_hand_drawn_line(
                draw,
                (x + x_start, hair_top_y),  # Nace arriba
                (x + x_final, y_final),     # Cae hacia oreja izquierda
                fill=self.hair_color,
                width=grosor,
                curve_amount=0.3
            )

        # LADO DERECHO - 5 líneas separadas cayendo hacia la derecha (SIMÉTRICAS)
        right_positions = [
            (30, self.head_radius + 30, head_center_y + 15, 7),   # Línea 1 (más externa)
            (20, self.head_radius + 20, head_center_y + 5, 6),    # Línea 2
            (10, self.head_radius + 12, head_center_y - 5, 6),    # Línea 3
            (0, self.head_radius + 5, head_center_y - 12, 5),     # Línea 4
            (-10, self.head_radius, head_center_y - 18, 5),       # Línea 5 (más interna)
        ]

        for x_start, x_final, y_final, grosor in right_positions:
            draw_hand_drawn_line(
                draw,
                (x + x_start, hair_top_y),  # Nace arriba
                (x + x_final, y_final),     # Cae hacia oreja derecha
                fill=self.hair_color,
                width=grosor,
                curve_amount=0.3
            )

        # FLEQUILLO central - 3 líneas al frente (reducidas)
        for x_offset in [-10, 0, 10]:
            draw_hand_drawn_line(
                draw,
                (x + x_offset, hair_top_y - 5),
                (x + x_offset, head_center_y - self.head_radius + 8),
                fill=self.hair_color,
                width=5,
                curve_amount=0.05
            )

    def _draw_male_hair(self, draw, x, head_center_y):
        """Dibuja 3 pelitos de hombre calvo"""
        top_y = head_center_y - self.head_radius
        hair_length = 15

        # Pelito central
        draw.line([x, top_y, x, top_y - hair_length],
                 fill=self.line_color, width=3)

        # Pelito izquierdo (inclinado)
        draw.line([x - 12, top_y + 5, x - 15, top_y - hair_length + 5],
                 fill=self.line_color, width=3)

        # Pelito derecho (inclinado)
        draw.line([x + 12, top_y + 5, x + 15, top_y - hair_length + 5],
                 fill=self.line_color, width=3)


def create_character_frame(character_data, expression, gesture, mouth_state,
                           width=1080, height=1920, transparent_bg=True, blink=False):
    """
    Crea un frame con un personaje

    Args:
        character_data: Dict con info del personaje
        expression: Expresión facial
        gesture: Gesto corporal
        mouth_state: Estado de boca para lip sync
        width, height: Dimensiones del frame
        transparent_bg: Si True, fondo transparente para composición
        blink: Si True, dibuja ojos cerrados (parpadeo)

    Returns:
        PIL.Image: Frame generado con canal alpha
    """
    # Crear canvas con fondo transparente para composición
    if transparent_bg:
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    else:
        img = Image.new('RGB', (width, height), '#F5F5DC')
    draw = ImageDraw.Draw(img)

    # Crear personaje
    gender = 'female' if character_data['type'] in ['mujer', 'mama', 'esposa', 'hija'] else 'male'

    # Posición según layout (Y más abajo para dar espacio al cabello arriba)
    if character_data['position'] == 'left':
        position = (width // 3, int(height * 0.70))  # 70% abajo para espacio arriba
    elif character_data['position'] == 'right':
        position = (2 * width // 3, int(height * 0.70))
    else:
        position = (width // 2, int(height * 0.70))

    # Crear y dibujar personaje
    character = StickFigure(gender=gender, position=position, scale=1.5)
    character.set_expression(expression)
    character.set_gesture(gesture)
    character.set_mouth_state(mouth_state)

    character.draw(draw, blink=blink)

    return img


def test_characters():
    """Prueba de personajes"""
    logger.info("🎨 Test de personajes stick animados\n")

    output_dir = Path(__file__).parent.parent.parent / "output" / "001-20260910" / "test_characters"
    output_dir.mkdir(exist_ok=True, parents=True)

    # Test mujer
    char_data = {
        'type': 'mujer',
        'position': 'left'
    }

    expressions = ['neutral', 'feliz', 'enojada', 'sorprendida', 'triste', 'disculpa', 'defensiva']
    gestures = ['idle', 'hands_together_apologetic', 'hand_gestures_explanatory',
                'pointing_finger_soft', 'hands_up_defensive']
    mouth_states = ['closed', 'semi', 'open']

    logger.info("Generando expresiones...")
    for expr in expressions:
        img = create_character_frame(char_data, expr, 'idle', 'closed')
        img.save(output_dir / f"mujer_expr_{expr}.png")
        logger.info(f"  ✅ {expr}")

    logger.info("\nGenerando gestos...")
    for gest in gestures:
        img = create_character_frame(char_data, 'neutral', gest, 'closed')
        img.save(output_dir / f"mujer_gesture_{gest}.png")
        logger.info(f"  ✅ {gest}")

    logger.info("\nGenerando mouth states...")
    for mouth in mouth_states:
        img = create_character_frame(char_data, 'neutral', 'idle', mouth)
        img.save(output_dir / f"mujer_mouth_{mouth}.png")
        logger.info(f"  ✅ {mouth}")

    # Test hombre
    char_data_m = {
        'type': 'hombre',
        'position': 'right'
    }

    logger.info("\nGenerando hombre sumiso...")
    img = create_character_frame(char_data_m, 'sumiso', 'arms_crossed', 'closed')
    img.save(output_dir / f"hombre_sumiso_crossed.png")
    logger.info("  ✅ hombre sumiso")

    logger.info(f"\n✅ Frames guardados en: {output_dir}")
    logger.info(f"   Total: {len(list(output_dir.glob('*.png')))} imágenes")

    return True


if __name__ == '__main__':
    if not PIL_AVAILABLE:
        logger.error("❌ PIL no disponible")
        sys.exit(1)

    success = test_characters()
    sys.exit(0 if success else 1)
