import pygame
import sys
import random
from random import randint
import numpy as np
import keyboard

class Carro:
    def __init__(self, carril: int, y: int, velocidad: float, ancho: int, alto: int):
        self.carril = carril
        self.y = y
        self.velocidad = velocidad
        self.ancho = ancho
        self.alto = alto
        print("carril: ", self.carril)

    def mover(self, direccion_x):
        pass

class CarroEnemigo(Carro):
    def __init__(self, carril: int, y: int, velocidad: float, type: str, ancho: int, alto: int):
        super().__init__(carril, y, velocidad, ancho, alto)
        self.type = type
        self.imagen_auto = pygame.image.load('ENEMIGO1.png')  # Cambia esta ruta por la imagen del enemigo
        self.imagen_auto = pygame.transform.scale(self.imagen_auto, (ancho, alto))

    def mover(self):
        self.y += self.velocidad
    
    
class CarroJugador(Carro):
    def __init__(self, carril: int, y: int, velocidad: float, ancho: int, alto: int):
        super().__init__(carril, y, velocidad, ancho, alto)
        self.x = carril
        self.cantidadPuntos = 0
        self.riel_player = 1
        self.dir_back1 = 0
        self.dir_back2 = 0
        self.imagen_auto = pygame.image.load('jugador1.png')
        self.imagen_auto = pygame.transform.scale(self.imagen_auto, (ancho, alto))

        
        self.listado_recompensas = []
        self.max_speed = 7
        self.speed = 0
        self.carril_act = 0
        self.ocupado = 0
        self.modo = 0
        
    
    def acumularPuntos(self, puntos: int, choque: bool):
        if choque:
            self.cantidadPuntos = 0
        else:
            self.cantidadPuntos += puntos
        print(f"¡Puntos acumulados! Puntaje actual: {self.cantidadPuntos}")

    def mover(self, direccion_x, direccion_xaut, carril_posiciones):
        if self.dir_back1 != direccion_x:
            self.dir_back1=direccion_x
            self.riel_player += direccion_x

        if self.dir_back2 != direccion_xaut:
            self.dir_back2=direccion_xaut
            self.riel_player += direccion_xaut
        
        if self.riel_player <= 0:
            self.riel_player = 0
        elif self.riel_player >= 2:
            self.riel_player = 2
        print("bef: ", self.dir_back1, self.dir_back2, "act", direccion_x, "act aut", direccion_xaut)
                

        self.x = carril_posiciones[self.riel_player]

class Pista:
    def __init__(self, carriles: int):
        self.carriles = carriles

class Juego:
         
    def __init__(self, jugador: CarroJugador, enemigos: list, pista: Pista):
        self.jugador = jugador
        self.enemigos = enemigos
        self.pista = pista
        self.puntaje = 0
        self.dificultad = 1
        self.imagen_fondo_game_over = pygame.image.load('choque.jpg')
        self.imagen_fondo_game_over = pygame.transform.scale(self.imagen_fondo_game_over, (800, 800))
        pygame.init()
        pygame.mixer.init()
        self.musica_menu = "self.musica_menu.mp3"  # Música de fondo para el menú
        self.musica_juego = "Sfondo.mp3"  # Música de fondo para el juego
        self.sonido_choque = pygame.mixer.Sound("Schoques.mp3")
        
        self.NEGRO = (0, 0, 0)
        self.BLANCO = (255, 255, 255)
        self.VERDE_CLARO = (0, 255, 0)
        self.VERDE_OSCURO = (0, 150, 0)
        self.ROJO_CLARO = (255, 100, 100)
        self.ROJO_OSCURO = (200, 50, 50)
        self.GRIS = (50, 50, 50)
        self.ANCHO = 800
        self.ALTO = 800 
        self.screen = pygame.display.set_mode((self.ANCHO, self.ALTO))
        pygame.display.set_caption("PANAMERICANA CRASH COURSE")
        self.imagen_fondo = pygame.image.load("PanamericanaPeru.jpg")
        self.imagen_fondo = pygame.transform.scale(self.imagen_fondo, (self.ANCHO, self.ALTO))
        self.fuente = pygame.font.SysFont(None, 50)
        self.fuente_botones = pygame.font.SysFont(None, 40)
        self.carril_posiciones = [self.ANCHO // 4 - 55, self.ANCHO // 2 - 55, 3 * self.ANCHO // 4 - 55]
        self.open = self.carril_posiciones
        self.need = []
        self.fondo_inicial = pygame.image.load("PanamericanaPeru.jpg") 
        self.imagen_fondo_juego = pygame.image.load("PISTA.jpeg")  # Cambia esto por la ruta de tu imagen de pista
        self.imagen_fondo_juego = pygame.transform.scale(self.imagen_fondo_juego, (self.ANCHO, self.ALTO))
        self.low = np.array([self.carril_posiciones[0]], dtype=np.float32)
        self.high = np.array([self.carril_posiciones[2]], dtype=np.float32)
        self.estado = 0
        self.state_0 = 0
        self.state =0
        self.qtable = np.random.uniform(low = 0, high = 2, size = [3,3,3])
        self.tasa_aprendizaje = 0.4
        self.factor_descuento = 0.97
        self.episodios = 500
        self.accion= 0
        self.recompensa = 0
        self.modo = 0
        self.train = False

        self.future_q = 0
        self.future_riel = 0
        self.actual_q = 0
        

    
    def iniciarJuego(self):
        pygame.mixer.music.load(self.musica_juego)  # Cargar la música del juego
        pygame.mixer.music.play(-1)  # Reproducir en bucle la música del juego
        clock = pygame.time.Clock()
        clock = pygame.time.Clock()
        dificultad_incremento = [70, 190, 330]
        velocidad_incremento = 1.5
        max_enemigos = 1
        enemigos_rects = []
        running = True
        direccion_x = 0
        direccion_xaut = 0

        for enemigo in self.enemigos:
            enemigo_rect = pygame.Rect(self.carril_posiciones[enemigo.carril], enemigo.y, enemigo.ancho, enemigo.alto)
            enemigos_rects.append(enemigo_rect)

        
        for episodio in range(self.episodios):
            
            recompensa_total = 0
            reward = 0
            self.imagen_fondo = self.imagen_fondo_juego

            while running :
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                

                if self.puntaje in dificultad_incremento:
                    
                    for enemigo in self.enemigos:
                        enemigo.velocidad += velocidad_incremento

                    if len(self.enemigos) < max_enemigos:
                        nuevo_enemigo = CarroEnemigo(
                            carril=random.randint(0, 2),
                            y=-random.randint(100, 400),
                            velocidad=self.enemigos[0].velocidad,
                            type="enemigo_extra",
                            ancho=120,
                            alto=160
                        )
                        self.enemigos.append(nuevo_enemigo)
                        enemigos_rects.append(
                            pygame.Rect(
                                self.carril_posiciones[nuevo_enemigo.carril], nuevo_enemigo.y, nuevo_enemigo.ancho, nuevo_enemigo.alto
                            )
                            
                        )
                        
                    dificultad_incremento.remove(self.puntaje)

                carriles_ocupados = set()

                for i, enemigo in enumerate(self.enemigos):
                    

                    enemigos_rects[i].y += enemigo.velocidad

                    self.accion = np.argmax(self.qtable [self.jugador.riel_player][self.state])

                    if self.accion == 0:
                        self.future_riel = self.jugador.riel_player -1
                    elif self.accion == 1:
                        self.future_riel = self.jugador.riel_player
                    elif self.accion == 2:
                        self.future_riel = self.jugador.riel_player +1

                    if self.future_riel >= 2:
                        self.future_riel = 2
                    elif self.future_riel <=0:
                        self.future_riel = 0


                    if enemigos_rects[i].top > self.ALTO:
                        
                        enemigos_rects[i].y = -random.randint(100, 400)
                        carriles_disponibles = [carril for carril in range(3) if carril not in carriles_ocupados]
                        
                        enemigo.carril = random.choice(carriles_disponibles)
                        enemigos_rects[i].x = self.carril_posiciones[enemigo.carril]
                        self.recompensa = 0
                        self.state= enemigo.carril

                        self.acumularPuntos(1)

                    
                    if keyboard.is_pressed('left'):
                                direccion_x = -1
                    elif keyboard.is_pressed('right'):
                                direccion_x = 1
                    else:
                        direccion_x = 0
                    self.jugador.mover(direccion_x, direccion_xaut,  self.carril_posiciones) 

                    carriles_ocupados.add(enemigos_rects[i].x)
                    non_vis = pygame.Rect(self.jugador.x, 150, self.jugador.ancho, 50)
                    jugador_rect = pygame.Rect(self.jugador.x, self.jugador.y, self.jugador.ancho, self.jugador.alto)
                    
                    if non_vis.colliderect(enemigos_rects[i]) or enemigos_rects[i].top > self.ALTO:
                        #self.gameOver()
                        
                        if self.modo == 1:
                            if self.accion == 0:
                                            direccion_xaut = -1 *self.modo
                            elif self.accion == 2:
                                            direccion_xaut = 1*self.modo
                            else:
                                direccion_xaut = 0

                        self.future_q = np.max(self.qtable[(self.future_riel, self.state)])

                        self.actual_q = self.qtable[(self.jugador.riel_player , self.state, self.accion)]

                        self.nuevo_q = (1 - self.tasa_aprendizaje) * self.actual_q + self.tasa_aprendizaje * (self.recompensa + self.factor_descuento * self.future_q)

                        self.qtable[(self.jugador.riel_player , self.state, self.accion)] = self.nuevo_q

                    
                    if jugador_rect.colliderect(enemigos_rects[i]) :
                        if self.modo == 0:
                            self.gameOver()
                            
                        else: 
                            self.recompensa = -1
                            self.acumularPuntos(-self.puntaje)
                            self.iniciarJuego()
                            running = False

                self.screen.blit(self.imagen_fondo, (0, 0))
                self.screen.blit(self.jugador.imagen_auto, (self.jugador.x, self.jugador.y))

                for i, enemigo in enumerate(self.enemigos):
                    self.screen.blit(enemigo.imagen_auto, (enemigos_rects[i].x, enemigos_rects[i].y))
                    

                puntaje_text = self.fuente.render(f"Puntuación: {self.puntaje}", True, self.BLANCO)
                self.screen.blit(puntaje_text, (10, 10))

                pygame.display.flip()

                clock.tick(160)
        
                
    def gameOver(self):
        pygame.mixer.music.stop()  # Detener la música del juego
        self.sonido_choque.play()
        # Almacena el puntaje obtenido antes del choque
        puntaje_final = self.puntaje
        game_over_active = True

        while game_over_active:
            # Dibuja la imagen de fondo
            self.screen.blit(self.imagen_fondo_game_over, (0, 0))

            # Texto de "Game Over"
            fuente_game_over = pygame.font.SysFont(None, 100)
            texto_game_over = fuente_game_over.render("GAME OVER", True, self.ROJO_CLARO)
            self.screen.blit(texto_game_over, (self.ANCHO // 2 - texto_game_over.get_width() // 2, self.ALTO // 4))

            # Mostrar la puntuación alcanzada antes del choque
            texto_puntuacion = self.fuente.render(f"Puntuación: {puntaje_final}", True, self.BLANCO)
            self.screen.blit(texto_puntuacion, (self.ANCHO // 2 - texto_puntuacion.get_width() // 2, self.ALTO // 2))

            # Botón para jugar de nuevo
            boton_jugar_de_nuevo = pygame.Rect(self.ANCHO // 2 - 140, self.ALTO // 2 + 100, 275, 60)
            self.dibujar_boton("JUGAR DE NUEVO", self.VERDE_OSCURO, self.VERDE_CLARO, boton_jugar_de_nuevo)

            # Botón para volver al inicio
            boton_volver_inicio = pygame.Rect(self.ANCHO // 2 - 140, self.ALTO // 2 + 180, 275, 60)
            self.dibujar_boton("VOLVER AL INICIO", self.ROJO_OSCURO, self.ROJO_CLARO, boton_volver_inicio)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if boton_jugar_de_nuevo.collidepoint(event.pos):
                        # Reinicia el puntaje y empieza de nuevo
                        self.puntaje = 0
                        self.jugador.cantidadPuntos = 0
                        for enemigo in self.enemigos:
                            enemigo.y = -random.randint(100, 400)  # Reinicia la posición de los enemigos
                        game_over_active = False  # Salir del bucle
                        self.iniciarJuego()  # Volver a iniciar el juego
                    elif boton_volver_inicio.collidepoint(event.pos):
                        # Volver a la pantalla de inicio
                        self.puntaje = 0
                        game_over_active = False  # Salir del bucle
                        self.pantalla_inicio()

    def acumularPuntos(self, puntos: int):
            self.puntaje += puntos

    def dibujar_boton(self, texto, color_normal, color_hover, rect, radio_borde=10):
        mouse_pos = pygame.mouse.get_pos()
        color = color_hover if rect.collidepoint(mouse_pos) else color_normal
        pygame.draw.rect(self.screen, color, rect, border_radius=radio_borde)
        sombra = pygame.Rect(rect.x + 3, rect.y + 3, rect.width, rect.height)
        pygame.draw.rect(self.screen, self.GRIS, sombra, border_radius=radio_borde)
        texto_renderizado = self.fuente_botones.render(texto, True, self.BLANCO)
        self.screen.blit(texto_renderizado, (rect.x + (rect.width - texto_renderizado.get_width()) // 2,
                                             rect.y + (rect.height - texto_renderizado.get_height()) // 2))

    def pantalla_inicio(self):
        pygame.mixer.music.load(self.musica_menu)  # Cargar la música del menú
        pygame.mixer.music.play(-1)
        self.imagen_fondo = pygame.image.load("PanamericanaPeru.jpg")  # Asegúrate de que el fondo se cargue aquí
        self.imagen_fondo = pygame.transform.scale(self.imagen_fondo, (self.ANCHO, self.ALTO))
        while True:
            self.screen.blit(self.imagen_fondo, (0, 0))
            fuente_titulo = pygame.font.SysFont(None, 40)
            texto_titulo = fuente_titulo.render("PANAMERICANA CRASH COURSE", True, self.VERDE_CLARO)
            self.screen.blit(texto_titulo, (self.ANCHO // 2 - texto_titulo.get_width() // 2, self.ALTO // 4))
            boton_manual = pygame.Rect(self.ANCHO // 4 - 80, self.ALTO // 2 - 30, 160, 60)
            self.dibujar_boton("CRASH!", self.VERDE_OSCURO, self.VERDE_CLARO, boton_manual)
            
            boton_automatic = pygame.Rect(2 * self.ANCHO // 4 - 80, self.ALTO // 2 - 30, 160, 60)
            self.dibujar_boton("DÍA LIBRE", (0, 0, 200), (0, 0, 255), boton_automatic)
            
            boton_cerrar = pygame.Rect(3 * self.ANCHO // 4 - 80, self.ALTO // 2 - 30, 160, 60)
            self.dibujar_boton("SALIR", self.ROJO_OSCURO, self.ROJO_CLARO, boton_cerrar)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if boton_manual.collidepoint(event.pos):
                        self.modo = 0
                    elif boton_automatic.collidepoint(event.pos):
                        self.modo = 1

                    if boton_manual.collidepoint(event.pos) or boton_automatic.collidepoint(event.pos):
                        self.seleccion_dificultad()
                    elif boton_cerrar.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()

    def seleccion_dificultad(self):
        while True:
            self.screen.blit(self.imagen_fondo, (0, 0))
            fuente_titulo = pygame.font.SysFont(None, 50)
            texto_titulo = fuente_titulo.render("SELECCIONA LA DIFICULTAD", True, self.BLANCO)
            self.screen.blit(texto_titulo, (self.ANCHO // 2 - texto_titulo.get_width() // 2, self.ALTO // 4 - 70))

            ancho_boton = 150
            alto_boton = 60
            espaciado_y = 20
            posicion_inicial_y = self.ALTO // 2 - alto_boton - espaciado_y - 30

            boton_facil = pygame.Rect(self.ANCHO // 2 - ancho_boton // 2, posicion_inicial_y, ancho_boton, alto_boton)
            self.dibujar_boton("FÁCIL", self.VERDE_OSCURO, self.VERDE_CLARO, boton_facil)

            boton_medio = pygame.Rect(self.ANCHO // 2 - ancho_boton // 2, posicion_inicial_y + alto_boton + espaciado_y,
                                      ancho_boton, alto_boton)
            self.dibujar_boton("MEDIO", (0, 0, 200), (0, 0, 255), boton_medio)

            boton_dificil = pygame.Rect(self.ANCHO // 2 - ancho_boton // 2,
                                        posicion_inicial_y + 2 * (alto_boton + espaciado_y), ancho_boton, alto_boton)
            self.dibujar_boton("DIFÍCIL", self.ROJO_OSCURO, self.ROJO_CLARO, boton_dificil)

            boton_volver = pygame.Rect(self.ANCHO // 2 - ancho_boton // 2,
                                       posicion_inicial_y + 3 * (alto_boton + espaciado_y), ancho_boton, alto_boton)
            self.dibujar_boton("VOLVER", self.NEGRO, self.GRIS, boton_volver)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if boton_facil.collidepoint(event.pos):
                        # Modo Fácil: velocidades iniciales
                        self.dificultad = 1
                        self.jugador.velocidad = 5.0
                        for enemigo in self.enemigos:
                            enemigo.velocidad = 7.0
                        print("Modo Fácil seleccionado")
                        self.iniciarJuego()
                    elif boton_medio.collidepoint(event.pos):
                        # Modo Medio: velocidades iniciales
                        self.dificultad = 2
                        self.jugador.velocidad = 7.0
                        for enemigo in self.enemigos:
                            enemigo.velocidad = 10.0
                        print("Modo Medio seleccionado")
                        self.iniciarJuego()
                    elif boton_dificil.collidepoint(event.pos):
                        # Modo Difícil: velocidades iniciales
                        self.dificultad = 3
                        self.jugador.velocidad = 10.0
                        for enemigo in self.enemigos:
                            enemigo.velocidad = 20
                        print("Modo Difícil seleccionado")
                        self.iniciarJuego()
                    elif boton_volver.collidepoint(event.pos):
                        self.pantalla_inicio()


jugador = CarroJugador(carril= random.randint(0, 2), y=620, velocidad=5.0, ancho=120, alto=150)  
enemigos = [CarroEnemigo(carril=random.randint(0, 2), y=-200, velocidad=7.0, type="enemigo1", ancho=120, alto=200)]  
pista = Pista(carriles=3)
juego = Juego(jugador, enemigos, pista)
juego.pantalla_inicio()
