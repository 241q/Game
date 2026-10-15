
import pygame
from client.score_client import submit_score
from game.game import CellSize, Colors, GridCols, GridRows, Game

Width = GridCols * CellSize + 40
Height = GridRows * CellSize + 220
BoardX = 20
BoardY = 190
BoardWidth = GridCols * CellSize
BoardHeight = GridRows * CellSize

ColorButtons = {}
ColorButtonSize = 44
ColorButtonGap = 12
ColorButtonY = 122

Background = (7, 7, 8)
BoardColor = (18, 18, 20)
GridColor = (35, 35, 38)
TextColor = (225, 225, 225)
MutedColor = (125, 125, 128)
AccentColor = (200, 55, 55)
SnakeColor = (65, 125, 80)
SnakeHeadColor = (115, 175, 105)
InputBackground = (27, 27, 30)
InputBorder = (65, 65, 70)


def Text(Screen, TextValue, Font, Color, Position, Center=False):
    Image = Font.render(str(TextValue), True, Color)
    Rect = Image.get_rect()

    if Center:
        Rect.center = Position
    else:
        Rect.topleft = Position

    Screen.blit(Image, Rect)
    return Rect


def GetFonts():
    FontName = "bahnschrift"

    if not pygame.font.match_font(FontName):
        FontName = "segoe ui"

    if not pygame.font.match_font(FontName):
        FontName = "arial"

    return {
        "small": pygame.font.SysFont(FontName, 16),
        "medium": pygame.font.SysFont(FontName, 21),
        "large": pygame.font.SysFont(FontName, 36),
        "challenge": pygame.font.SysFont(FontName, 32),
        "keytarget": pygame.font.SysFont(FontName, 54),
        "title": pygame.font.SysFont(FontName, 46),
    }


def CellRect(Cell, Inset=2):
    X, Y = Cell
    return pygame.Rect(
        BoardX + X * CellSize + Inset,
        BoardY + Y * CellSize + Inset,
        CellSize - Inset * 2,
        CellSize - Inset * 2
    )


def Board(Screen):
    BoardRect = pygame.Rect(BoardX, BoardY, BoardWidth, BoardHeight)
    pygame.draw.rect(Screen, BoardColor, BoardRect)

    for X in range(1, GridCols):
        Px = BoardX + X * CellSize
        pygame.draw.line(
            Screen, GridColor,
            (Px, BoardY), (Px, BoardY + BoardHeight), 1
        )

    for Y in range(1, GridRows):
        Py = BoardY + Y * CellSize
        pygame.draw.line(
            Screen, GridColor,
            (BoardX, Py), (BoardX + BoardWidth, Py), 1
        )


def Header(Screen, GameObj, Fonts):
    Text(
        Screen, str(GameObj.Score).zfill(3), Fonts["large"],
        TextColor, (22, 38)
    )

    Text(
        Screen, f"LVL {GameObj.Level}/5", Fonts["small"],
        MutedColor, (24, 87)
    )

    ColorButtons.clear()

    if GameObj.State == "play" and GameObj.FoodType == "normal":
        Seconds = GameObj.NormalAppleSecondsLeft
        TimerColor = (235, 65, 65) if Seconds <= 5 else TextColor

        Text(
            Screen, f"ĀBOLS: {Seconds:.1f} s", Fonts["medium"],
            TimerColor, (22, 125)
        )

    if GameObj.Challenge:
        PanelX = 300
        PanelWidth = Width - PanelX - 20
        PanelCenter = PanelX + PanelWidth // 2
        Seconds = GameObj.ChallengeSecondsLeft
        TimerColor = (210, 85, 75) if Seconds < 1.5 else AccentColor

        Text(
            Screen, f"{Seconds:.1f} s", Fonts["small"],
            TimerColor, (PanelCenter, 18), Center=True
        )

        ChallengeType = GameObj.Challenge["Type"]

        if ChallengeType == "key":
            Target = GameObj.Challenge["Key"]

            Text(
                Screen, "NOSPIED TAUSTIŅU", Fonts["small"],
                MutedColor, (PanelCenter, 53), Center=True
            )

            Text(
                Screen,
                "SPACE" if Target == "SPACE" else Target,
                Fonts["keytarget"], AccentColor,
                (PanelCenter, 104), Center=True
            )

        elif ChallengeType == "color":
            Target = GameObj.Challenge["Color"]

            Text(
                Screen, "ATRODI KRĀSU", Fonts["medium"],
                TextColor, (PanelCenter, 47), Center=True
            )

            ButtonNames = tuple(Colors.keys())
            TotalWidth = (
                len(ButtonNames) * ColorButtonSize
                + (len(ButtonNames) - 1) * ColorButtonGap
            )
            StartX = PanelCenter - TotalWidth // 2

            for Index, Name in enumerate(ButtonNames):
                Rect = pygame.Rect(
                    StartX + Index * (ColorButtonSize + ColorButtonGap),
                    ColorButtonY,
                    ColorButtonSize,
                    ColorButtonSize
                )
                ColorButtons[Name] = Rect
                pygame.draw.rect(Screen, Colors[Name], Rect)

                if Name == Target:
                    pygame.draw.rect(
                        Screen, (245, 245, 245),
                        (
                            Rect.x - 2, Rect.y - 2,
                            Rect.width + 4, Rect.height + 4
                        ),
                        2
                    )

        elif ChallengeType == "mouse":
            Text(
                Screen, "PELES MĒRĶIS", Fonts["medium"],
                TextColor, (PanelCenter, 55), Center=True
            )
            Text(
                Screen, "PĀRVIETO PELI UZ DZELTENO APLI",
                Fonts["small"], AccentColor,
                (PanelCenter, 105), Center=True
            )


def Objects(Screen, GameObj):
    if GameObj.FoodPos is not None:
        FoodRect = CellRect(GameObj.FoodPos, Inset=4)

        if GameObj.FoodType == "silver":
            pygame.draw.ellipse(Screen, (185, 190, 198), FoodRect)
            pygame.draw.ellipse(
                Screen, (225, 228, 232),
                pygame.Rect(FoodRect.x + 4, FoodRect.y + 3, 4, 4)
            )
        else:
            pygame.draw.ellipse(Screen, (190, 65, 58), FoodRect)
            pygame.draw.line(
                Screen, (90, 135, 75),
                (FoodRect.centerx, FoodRect.top + 2),
                (FoodRect.centerx + 3, FoodRect.top - 2), 2
            )

    for Segment in reversed(GameObj.Snake[1:]):
        pygame.draw.rect(
            Screen, SnakeColor,
            CellRect(Segment, Inset=2)
        )

    HeadRect = CellRect(GameObj.Snake[0], Inset=1)
    pygame.draw.rect(Screen, SnakeHeadColor, HeadRect)

    if GameObj.Challenge and GameObj.Challenge["Type"] == "mouse":
        TargetRect = CellRect(GameObj.Challenge["Target"], Inset=0)
        Center = TargetRect.center
        Radius = 11

        TargetSurface = pygame.Surface(
            (Radius * 2 + 4, Radius * 2 + 4),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            TargetSurface,
            (255, 210, 45, 65),
            (Radius + 2, Radius + 2),
            Radius
        )

        Screen.blit(
            TargetSurface,
            (Center[0] - Radius - 2, Center[1] - Radius - 2)
        )

        pygame.draw.circle(
            Screen,
            (255, 205, 35),
            Center,
            Radius,
            2
        )


def Overlay(Screen, Title, Subtitle, Fonts, TitleColor=AccentColor):
    Layer = pygame.Surface((BoardWidth, BoardHeight), pygame.SRCALPHA)
    Layer.fill((0, 0, 0, 190))
    Screen.blit(Layer, (BoardX, BoardY))

    CenterX = BoardX + BoardWidth // 2
    CenterY = BoardY + BoardHeight // 2

    Text(
        Screen, Title, Fonts["title"], TitleColor,
        (CenterX, CenterY - 30), Center=True
    )
    Text(
        Screen, Subtitle, Fonts["small"], TextColor,
        (CenterX, CenterY + 25), Center=True
    )


def GameScreen(Screen, GameObj, Fonts, PlayerName):
    Screen.fill(Background)
    Header(Screen, GameObj, Fonts)
    Board(Screen)
    Objects(Screen, GameObj)

    if GameObj.State == "menu":
        Layer = pygame.Surface((BoardWidth, BoardHeight), pygame.SRCALPHA)
        Layer.fill((0, 0, 0, 205))
        Screen.blit(Layer, (BoardX, BoardY))

        CenterX = Width // 2
        CenterY = Height // 2

        Text(
            Screen, "Ievadi savu vārdu", Fonts["medium"], TextColor,
            (CenterX, CenterY - 48), Center=True
        )

        InputWidth = min(340, BoardWidth - 40)
        InputHeight = 46
        InputRect = pygame.Rect(
            CenterX - InputWidth // 2,
            CenterY - InputHeight // 2,
            InputWidth,
            InputHeight
        )

        pygame.draw.rect(
            Screen, InputBackground, InputRect, border_radius=5
        )
        pygame.draw.rect(
            Screen, InputBorder, InputRect, width=1, border_radius=5
        )

        DisplayName = PlayerName if PlayerName else "Raksti savu vārdu..."
        NameColor = TextColor if PlayerName else MutedColor

        Text(
            Screen, DisplayName, Fonts["medium"], NameColor,
            InputRect.center, Center=True
        )

        Text(
            Screen, "Nospied ENTER, lai sāktu",
            Fonts["small"], MutedColor,
            (CenterX, CenterY + 55), Center=True
        )

    elif GameObj.State == "pause":
        Overlay(
            Screen, "APTURĒTS",
            "Nospied P, lai turpinātu", Fonts
        )

    elif GameObj.State == "over":
        Overlay(
            Screen, "SPĒLE BEIGUSIES",
            f"{GameObj.GameOverReason}  Punkti: {GameObj.Score}  Nospied R, lai spēlētu vēlreiz",
            Fonts, (190, 75, 68)
        )

    elif (
        GameObj.FeedbackText
        and GameObj.NowMs < GameObj.FeedbackUntilMs
    ):
        Text(
            Screen, GameObj.FeedbackText, Fonts["small"],
            AccentColor, (Width // 2, Height - 25), Center=True
        )

    pygame.display.flip()


def KeyLabel(Key):
    if Key == pygame.K_SPACE:
        return "SPACE"

    return pygame.key.name(Key).upper()


def Main():
    pygame.init()

    Screen = pygame.display.set_mode((Width, Height))
    pygame.display.set_caption("Panic Snake")
    Clock = pygame.time.Clock()
    Fonts = GetFonts()
    GameObj = Game()
    Running = True
    PlayerName = ""
    ScoreSent = False

    pygame.key.start_text_input()

    DirectionKeys = {
        pygame.K_UP: (0, -1),
        pygame.K_DOWN: (0, 1),
        pygame.K_LEFT: (-1, 0),
        pygame.K_RIGHT: (1, 0),
        pygame.K_w: (0, -1),
        pygame.K_s: (0, 1),
        pygame.K_a: (-1, 0),
        pygame.K_d: (1, 0),
    }

    while Running:
        Dt = Clock.tick(60)

        for Event in pygame.event.get():
            if Event.type == pygame.QUIT:
                Running = False

            elif Event.type == pygame.KEYDOWN:
                if Event.key == pygame.K_ESCAPE:
                    Running = False
                    continue

                if GameObj.State == "menu":
                    if Event.key == pygame.K_RETURN:
                        if PlayerName.strip():
                            PlayerName = PlayerName.strip()
                            GameObj.Start()
                            pygame.key.stop_text_input()
                    elif Event.key == pygame.K_BACKSPACE:
                        PlayerName = PlayerName[:-1]
                    continue

                if Event.key == pygame.K_p and GameObj.State in ("play", "pause"):
                    GameObj.TogglePause()
                    continue

                if Event.key == pygame.K_r and GameObj.State == "over":
                    GameObj.Start()
                    continue

                if GameObj.State != "play":
                    continue

                if Event.key in DirectionKeys:
                    GameObj.SetDirection(DirectionKeys[Event.key])
                    continue

                if GameObj.Challenge and GameObj.Challenge["Type"] == "key":
                    GameObj.AnswerKey(KeyLabel(Event.key))

            elif Event.type == pygame.TEXTINPUT:
                if GameObj.State == "menu":
                    NewName = PlayerName + Event.text

                    if len(NewName) <= 20 and Event.text.isprintable():
                        PlayerName = NewName

            elif Event.type == pygame.MOUSEMOTION:
                if (
                    GameObj.State == "play"
                    and GameObj.Challenge
                    and GameObj.Challenge["Type"] == "mouse"
                ):
                    MouseX, MouseY = Event.pos
                    CellX = (MouseX - BoardX) // CellSize
                    CellY = (MouseY - BoardY) // CellSize

                    if 0 <= CellX < GridCols and 0 <= CellY < GridRows:
                        GameObj.AnswerMouseCell((CellX, CellY))

            elif Event.type == pygame.MOUSEBUTTONDOWN and Event.button == 1:
                if (
                    GameObj.State == "play"
                    and GameObj.Challenge
                    and GameObj.Challenge["Type"] == "color"
                ):
                    SelectedColor = None

                    for ColorName, Rect in ColorButtons.items():
                        if Rect.collidepoint(Event.pos):
                            SelectedColor = ColorName
                            break

                    if SelectedColor is None:
                        GameObj.FailColorClick()
                    else:
                        GameObj.AnswerColor(SelectedColor)

        GameObj.Update(Dt)

        if GameObj.State == "over" and not ScoreSent:
            submit_score(PlayerName, GameObj.Score)
            ScoreSent = True
        elif GameObj.State != "over":
            ScoreSent = False

        GameScreen(Screen, GameObj, Fonts, PlayerName)

    pygame.key.stop_text_input()
    pygame.quit()


if __name__ == "__main__":
    Main()