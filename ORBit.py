import pygame
from pygame.locals import (
    QUIT,
    KEYDOWN,
    K_ESCAPE,
    K_p as K_P,
    K_r as K_R,
    MOUSEBUTTONDOWN,
    MOUSEWHEEL,
    MOUSEMOTION
)
from math import (
    sqrt,
    floor
)
from time import (
    time
)
pygame.init()
global FPS, SCREEN_WIDTH, SCREEN_HEIGHT, Poles
FPS = 10
Running = True
Clock = pygame.time.Clock()
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
class Screen:
    def __init__(self):
        self.SCREEN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.ZoomAmount = 1
        self.Center = [0, 0]
        self.TooltipFont = pygame.font.Font(None, 50)
        self.MousePos = [0, 0]
        self.LastMousePos = [0, 0]
        self.WorldX, self.WorldY = SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2
        self.BlitingXChange = 0
        self.BlitingYChange = 0
    def Add(self, Surface, Coord):
        self.SCREEN.blit(
            Surface,
            ((Coord[0] + (self.Center[0] * -1))* self.ZoomAmount,
            (Coord[1] + (self.Center[1] * -1)) * self.ZoomAmount)
        )
    def Update(self):
        self.SCREEN.blit(
            self.TooltipFont.render(
                str(floor(FPS)) + ' FPS',
                True,
                (255, 255, 255)
            ),
            (10, 10)

            )
        if round(self.ZoomAmount * 100) > 100000:
            self.SCREEN.blit(
                self.TooltipFont.render(
                    '> 100000%',
                    True,
                    (255, 255, 255)
                ),
                (10, 70)
            )
        else:
            if round(self.ZoomAmount * 100, 3) < 0.001:
                self.SCREEN.blit(
                    self.TooltipFont.render(
                        '0%',
                        True,
                        (255, 255, 255)
                    ),
                    (10, 70)
                )
            else:
                self.SCREEN.blit(
                    self.TooltipFont.render(
                        str(round(self.ZoomAmount * 100, 3)) + '%',
                        True,
                        (255, 255, 255)
                    ),
                    (10, 70)
                )
        pygame.display.update()
    def Clear(self):
        self.SCREEN.fill((0, 0, 0))
    def GetMousePos(self, MousePos):
        self.MousePos = MousePos
    def GetLastMousePos(self):
        self.LastMousePos = self.MousePos
    def Zoom(self, ZoomDirection):
        OldZoom = self.ZoomAmount
        if ZoomDirection > 0:
            for x in range(0, ZoomDirection, 1):
                self.ZoomAmount = self.ZoomAmount + (self.ZoomAmount * 0.1)
        elif ZoomDirection < 0:
            for x in range(0, abs(ZoomDirection), 1):
                self.ZoomAmount = self.ZoomAmount - (self.ZoomAmount * 0.1)
        self.Center[0] = (self.MousePos[0] / OldZoom) + self.Center[0] - (self.MousePos[0] / self.ZoomAmount)
        self.Center[1] = (self.MousePos[1] / OldZoom) + self.Center[1] - (self.MousePos[1] / self.ZoomAmount)
        if self.MousePos != self.LastMousePos:
            self.WorldX = (self.MousePos[0] / OldZoom) + self.Center[0]
            self.WorldY = (self.MousePos[1] / OldZoom) + self.Center[1]
    def Pan(self, MousePos):
        PanSpeed = 100 / self.ZoomAmount * 0.3
        if MousePos[0] <= 0:
            self.Center[0] -= PanSpeed
        elif MousePos[0] >= SCREEN_WIDTH - 1:
            self.Center[0] += PanSpeed
        if MousePos[1] <= 0:
            self.Center[1] -= PanSpeed
        elif MousePos[1] >= SCREEN_HEIGHT - 1:
            self.Center[1] += PanSpeed
SCREEN = Screen()
class Pole:
    def __init__(self, Mass, Coord, IsNegative, IsPullable):
        self.Mass = Mass
        self.Coord = Coord
        self.IsNegative = IsNegative
        self.IsPullable = IsPullable
        if IsNegative:
            self.Mass *= -1
        self.AcelerationX = 0
        self.AcelerationY = 0
    def Update(self):
        if not self.IsPullable:
            # Convert world coordinates to screen coordinates
            screen_x = (self.Coord[0] - SCREEN.Center[0]) * SCREEN.ZoomAmount
            screen_y = (self.Coord[1] - SCREEN.Center[1]) * SCREEN.ZoomAmount
            try:
                pygame.draw.circle(
                    SCREEN.SCREEN,
                    (255, 0, 0),
                    (int(screen_x), int(screen_y)),
                    max(int(self.Mass / 100 * SCREEN.ZoomAmount), 1),
                )
            except TypeError:
                pass
    def UpdatePos(self, Number):
        for PoleIndex in Poles:
            dx = PoleIndex.Coord[0] - self.Coord[0]
            dy = PoleIndex.Coord[1] - self.Coord[1]
            Distance = max(sqrt(dx ** 2 + dy ** 2), 0.1)
            GravPow = PoleIndex.Mass / (Distance ** 2)
            self.AcelerationX += GravPow * (dx / Distance)
            self.AcelerationY += GravPow * (dy / Distance)
Poles = []
class Orbiter:
    def __init__(self, StartCoord, Surface):
        self.OrbiterIMG = Surface
        self.OrbiterIMG.fill((255, 255, 255))
        if StartCoord == 'Center':
            self.Coord = [SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2]
        else:
            self.Coord = [StartCoord[0], StartCoord[1]]
        self.XSpeed, self.YSpeed = 0, 0
        self.AcelerationX = 0
        self.AcelerationY = 0
        self.XSpeed = 0
        self.YSpeed = 0
    def GetDisFromPoles(self, Mass, PolePos):
        dx = PolePos[0] - self.Coord[0]
        dy = PolePos[1] - self.Coord[1]
        Distance = max(sqrt(dx ** 2 + dy ** 2), 5)
        GravPow = Mass / (Distance ** 2)
        # Calculate acceleration components
        self.AcelerationX += GravPow * (dx / Distance)
        self.AcelerationY += GravPow * (dy / Distance)
    def Update(self):
        self.XSpeed += self.AcelerationX
        self.YSpeed += self.AcelerationY
        self.Coord[0] += (self.XSpeed * 2) / FPS
        self.Coord[1] += (self.YSpeed * 2) / FPS
        SCREEN.Add(self.OrbiterIMG, self.Coord)
    def PauseUpdate(self):
        SCREEN.Add(self.OrbiterIMG, self.Coord)
    def ClearAcceleration(self):
        self.AcelerationX = 0
        self.AcelerationY = 0
        self.XSpeed = 0
        self.YSpeed = 0
OrbiterIMG = pygame.surface.Surface((1, 1))
Orbiters = []
for x in range(0, 1920, 12):
    for y in range(0, 1080, 12):
        Orbiters.append(Orbiter((x, y), OrbiterIMG))
StartTime = time()
LastLoopStartTime = StartTime
pygame.mouse.set_pos(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
Iteration = 0
MousePos = pygame.mouse.get_pos()
MouseWorldPos = [
    (MousePos[0] / SCREEN.ZoomAmount) + SCREEN.Center[0],
    (MousePos[1] / SCREEN.ZoomAmount) + SCREEN.Center[1]\
]
while Running:
    SCREEN.GetMousePos(MousePos)
    for PoleIndex in Poles:
        if PoleIndex.IsPullable:
            PoleIndex.UpdatePos()
    for Orbit in Orbiters:
        for PoleIndex in Poles:
            Orbit.GetDisFromPoles(PoleIndex.Mass, PoleIndex.Coord)
        try:
            Orbit.Update()
        except AttributeError:
            Orbit.PauseUpdate()
    for PoleIndex in Poles:
        PoleIndex.Update()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                exit()
            elif event.key == K_P:
                PauseLoop = True
                while PauseLoop:
                    SCREEN.GetMousePos(MousePos)
                    MousePos = pygame.mouse.get_pos()
                    MouseWorldPos = [
                        (MousePos[0] / SCREEN.ZoomAmount) + SCREEN.Center[0],
                        (MousePos[1] / SCREEN.ZoomAmount) + SCREEN.Center[1]
                    ]
                    for event in pygame.event.get():
                        if event.type == MOUSEWHEEL:
                            SCREEN.Zoom(event.y)
                        elif event.type == KEYDOWN:
                            if event.key == K_P:
                                PauseLoop = False
                            elif event.key == K_ESCAPE:
                                pygame.quit()
                                exit()
                        elif event.type == QUIT:
                            pygame.quit()
                            exit()
                    for Orbit in Orbiters:
                        Orbit.PauseUpdate()
                    for PoleIndex in Poles:
                        PoleIndex.Update()
                    SCREEN.Pan(MousePos)
                    SCREEN.Update()
                    SCREEN.Clear()
                    ThisTime = time()
                    TimeElapsed = ThisTime - LastLoopStartTime
                    FPS = 1 / TimeElapsed
                    Clock.tick(FPS)
                    LastLoopStartTime = ThisTime
                del PauseLoop
                MousePos = pygame.mouse.get_pos()
                MouseWorldPos = [
                    (MousePos[0] / SCREEN.ZoomAmount) + SCREEN.Center[0],
                    (MousePos[1] / SCREEN.ZoomAmount) + SCREEN.Center[1]
                ]
        elif event.type == MOUSEWHEEL:
            SCREEN.Zoom(event.y)
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                Iteration += 1
                if Iteration < FPS / 0.5:
                    MousePos = pygame.mouse.get_pos()
                    MouseWorldPos = [
                        (MousePos[0] / SCREEN.ZoomAmount) + SCREEN.Center[0],
                        (MousePos[1] / SCREEN.ZoomAmount) + SCREEN.Center[1]
                    ]
                    Poles.append(Pole(500, MouseWorldPos, False, False))
                    Iteration = -1
        elif event.type == MOUSEMOTION:
            MousePos = pygame.mouse.get_pos()
            MouseWorldPos = [
                (MousePos[0] / SCREEN.ZoomAmount) + SCREEN.Center[0],
                (MousePos[1] / SCREEN.ZoomAmount) + SCREEN.Center[1]
            ]
    SCREEN.Pan(MousePos)
    SCREEN.Update()
    SCREEN.Clear()
    SCREEN.GetLastMousePos()
    ThisTime = time()
    TimeElapsed = ThisTime - LastLoopStartTime
    FPS = 1 / TimeElapsed
    #Clock.tick(FPS)
    LastLoopStartTime = ThisTime
exit()