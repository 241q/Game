
import math
from pathlib import Path

import pygame
from client.score_client import submit_score
from game.game import (
    CellSize, ChallengeDuration, Colors, GridCols, GridRows, Game
)

Width = GridCols * CellSize + 40
Height = GridRows * CellSize + 220
BoardX = 20
BoardY = 190
BoardWidth = GridCols * CellSize
BoardHeight = GridRows * CellSize

ColorButtons = {}
ColorButtonSize = 44
ColorButtonGap = 12
ColorButtonY = 74

Background = (7, 7, 8)
BoardColor = (18, 18, 20)
GridColor = (29, 30, 35)
TextColor = (225, 225, 225)
MutedColor = (125, 125, 128)
AccentColor = (200, 55, 55)
SnakeColor = (65, 125, 80)
SnakeHeadColor = (115, 175, 105)
InputBackground = (27, 27, 30)
InputBorder = (65, 65, 70)
FrameColor = (38, 43, 62)

BackgroundFile = "background.jpg"
ImageHorizonY = 250


def LoadBackground():
    Folder = Path(__file__).resolve().parent
    Candidates = (
        Folder.parent / "assets" / BackgroundFile,
        Folder / "assets" / BackgroundFile,
    )

    FilePath = next((Path_ for Path_ in Candidates if Path_.exists()), None)

    if FilePath is None:
        print("Background image not found. Looked in:")
        for Path_ in Candidates:
            print("  ", Path_)

        Fallback = pygame.Surface((Width, Height))
        Fallback.fill(Background)
        return Fallback

    Picture = pygame.image.load(str(FilePath)).convert()
    PicW, PicH = Picture.get_size()

    Scale = max(
        Width / PicW,
        Height / PicH,
        (Height - BoardY) / (PicH - ImageHorizonY)
    )
    NewW = math.ceil(PicW * Scale)
    NewH = math.ceil(PicH * Scale)
    Picture = pygame.transform.smoothscale(Picture, (NewW, NewH))

    OffsetX = (Width - NewW) // 2
    OffsetY = BoardY - round(ImageHorizonY * Scale)
    OffsetY = min(0, max(OffsetY, Height - NewH))

    Result = pygame.Surface((Width, Height))
    Result.blit(Picture, (OffsetX, OffsetY))
    return Result


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
    pygame.draw.rect(
        Screen, FrameColor,
        (BoardX - 1, BoardY - 1, BoardWidth + 2, BoardHeight + 2), 1
    )

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


Cream = (232, 230, 204)
Amber = (240, 175, 60)
Ink = (4, 6, 12)
Navy = (10, 14, 28)
Stone = (90, 100, 140)
Urgent = (225, 70, 60)

SignRect = pygame.Rect(300, 12, 560, 154)
PixelFont = None

ApplePattern = (
    "....g...",
    "...g....",
    ".rrrrrr.",
    "rhrrrrrr",
    "rrrrrrrr",
    "rrrrrrrr",
    ".rrrrrr.",
    "..rr.rr.",
)
AppleColors = {
    "r": (190, 65, 58),
    "h": (230, 120, 110),
    "g": (90, 135, 75),
}
ArrowPattern = (
    "xxxxx",
    ".xxx.",
    "..x..",
)


def PixelText(Screen, Value, Scale, Color, Position, Center=False, Shadow=True):
    """Chunky text: drawn small with no smoothing, then scaled up."""
    global PixelFont

    if PixelFont is None:
        PixelFont = pygame.font.Font(None, 16)

    def Build(TextColor):
        Small = PixelFont.render(str(Value), False, TextColor).convert_alpha()
        return pygame.transform.scale(
            Small, (Small.get_width() * Scale, Small.get_height() * Scale)
        )

    Image = Build(Color)
    Rect = Image.get_rect()

    if Center:
        Rect.center = Position
    else:
        Rect.topleft = Position

    if Shadow:
        Screen.blit(Build(Ink), Rect.move(Scale, Scale))

    Screen.blit(Image, Rect)
    return Rect


def PixelArt(Screen, Pattern, Colors_, X, Y, Unit):
    for RowIndex, Row in enumerate(Pattern):
        for ColIndex, Char in enumerate(Row):
            if Char in Colors_:
                pygame.draw.rect(
                    Screen, Colors_[Char],
                    (X + ColIndex * Unit, Y + RowIndex * Unit, Unit, Unit)
                )


def NotchedRect(Screen, Color, Rect, Unit):
    pygame.draw.rect(
        Screen, Color,
        (Rect.x + Unit, Rect.y, Rect.width - 2 * Unit, Rect.height)
    )
    pygame.draw.rect(
        Screen, Color,
        (Rect.x, Rect.y + Unit, Rect.width, Rect.height - 2 * Unit)
    )


def PixelBox(Screen, Rect, Border, Fill, Unit=4):
    NotchedRect(Screen, Ink, Rect, Unit)
    NotchedRect(Screen, Border, Rect.inflate(-2 * Unit, -2 * Unit), Unit)
    NotchedRect(Screen, Fill, Rect.inflate(-4 * Unit, -4 * Unit), Unit)


def Header(Screen, GameObj, Fonts):
    PixelText(Screen, "PUNKTI", 2, Stone, (26, 12))
    PixelText(Screen, str(GameObj.Score).zfill(3), 4, Cream, (26, 34))

    PixelText(Screen, "LĪMENIS", 2, Stone, (26, 84))

    for Index in range(5):
        Pip = pygame.Rect(26 + Index * 24, 114, 18, 18)
        pygame.draw.rect(Screen, Ink, Pip.inflate(4, 4))

        if Index < GameObj.Level:
            pygame.draw.rect(Screen, Amber, Pip)
            pygame.draw.rect(Screen, Cream, (Pip.x, Pip.y, Pip.width, 4))
        else:
            pygame.draw.rect(Screen, (28, 34, 56), Pip)

    ColorButtons.clear()

    if GameObj.State == "play" and GameObj.FoodType == "normal":
        Seconds = GameObj.NormalAppleSecondsLeft
        Low = Seconds <= 5
        Blink = Low and (pygame.time.get_ticks() // 250) % 2 == 0

        PixelArt(Screen, ApplePattern, AppleColors, 26, 146, 3)
        PixelText(
            Screen, f"{Seconds:.1f}", 3,
            Urgent if Blink else Cream, (62, 146)
        )

    if not GameObj.Challenge:
        return

    Seconds = GameObj.ChallengeSecondsLeft
    Hurry = Seconds < 1.5
    Blink = Hurry and (pygame.time.get_ticks() // 120) % 2 == 0

    PixelBox(Screen, SignRect, Urgent if Blink else Stone, Navy)

    CenterX = SignRect.centerx
    ChallengeType = GameObj.Challenge["Type"]

    Titles = {
        "key": "NOSPIED TAUSTIŅU",
        "color": "ATRODI KRĀSU",
        "mouse": "PELES MĒRĶIS",
    }

    PixelText(
        Screen, Titles[ChallengeType], 2, Cream, (CenterX, 38), Center=True
    )
    PixelText(
        Screen, f"{Seconds:.1f}", 3, Urgent if Hurry else Amber,
        (SignRect.right - 70, 38), Center=True
    )

    Blocks = 20
    BlockWidth = 22
    BlockGap = 4
    BarWidth = Blocks * BlockWidth + (Blocks - 1) * BlockGap
    BarX = CenterX - BarWidth // 2
    Fraction = max(0.0, min(1.0, Seconds * 1000 / ChallengeDuration))
    Lit = math.ceil(Fraction * Blocks)

    for Index in range(Blocks):
        if Index < Lit:
            LitColor = Urgent if Hurry else Amber
            if Blink:
                LitColor = Cream
        else:
            LitColor = (28, 34, 56)

        pygame.draw.rect(
            Screen, LitColor,
            (BarX + Index * (BlockWidth + BlockGap), 132, BlockWidth, 12)
        )

    if ChallengeType == "key":
        Target = GameObj.Challenge["Key"]
        IsSpace = Target == "SPACE"

        Face = pygame.Rect(0, 0, 230 if IsSpace else 64, 64)
        Face.center = (CenterX, 84)

        pygame.draw.rect(Screen, Ink, Face.inflate(8, 8).move(0, 3))
        pygame.draw.rect(Screen, (150, 146, 120), Face.move(0, 6))
        pygame.draw.rect(Screen, Cream, Face)

        PixelText(
            Screen, Target, 3 if IsSpace else 4, (20, 24, 44),
            Face.center, Center=True, Shadow=False
        )

    elif ChallengeType == "color":
        Target = GameObj.Challenge["Color"]

        ButtonNames = tuple(Colors.keys())
        TotalWidth = (
            len(ButtonNames) * ColorButtonSize
            + (len(ButtonNames) - 1) * ColorButtonGap
        )
        StartX = CenterX - TotalWidth // 2

        for Index, Name in enumerate(ButtonNames):
            Rect = pygame.Rect(
                StartX + Index * (ColorButtonSize + ColorButtonGap),
                ColorButtonY,
                ColorButtonSize,
                ColorButtonSize
            )
            ColorButtons[Name] = Rect

            pygame.draw.rect(
                Screen, Cream if Name == Target else Ink, Rect.inflate(8, 8)
            )
            pygame.draw.rect(Screen, Colors[Name], Rect)

            if Name == Target:
                PixelArt(
                    Screen, ArrowPattern, {"x": Cream},
                    Rect.centerx - 10, Rect.y - 22, 4
                )

    elif ChallengeType == "mouse":
        pygame.draw.circle(Screen, Amber, (CenterX, 76), 16, 3)
        pygame.draw.circle(Screen, Amber, (CenterX, 76), 3)

        PixelText(
            Screen, "PĀRVIETO PELI UZ DZELTENO APLI", 2, Amber,
            (CenterX, 106), Center=True
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


def GameScreen(Screen, GameObj, Fonts, PlayerName, BackgroundImage):
    Screen.blit(BackgroundImage, (0, 0))
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
    BackgroundImage = LoadBackground()
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

        GameScreen(
            Screen, GameObj, Fonts, PlayerName, BackgroundImage
        )

    pygame.key.stop_text_input()
    pygame.quit()


if __name__ == "__main__":
    Main()
