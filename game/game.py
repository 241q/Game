import random

CellSize = 20
GridCols = 48
GridRows = 28

BaseMoveInterval = 150
MinMoveInterval = 65
SpeedIncrease = 5
LevelScoreStep = 50

NormalAppleLimit = 20000

SilverAppleChance = 0.04
SilverAppleDuration = 5000
SilverSlowDuration = 5000
SilverSlowExtra = 75

ChallengeMinDelay = 7000
ChallengeMaxDelay = 13000
ChallengeDuration = 4500

ReactionKeys = {
    "Q": "q",
    "E": "e",
    "F": "f",
    "SPACE": "space",
}

Colors = {
    "SARKANA": (235, 75, 75),
    "ZILA": (65, 145, 255),
    "DZELTENA": (250, 210, 65),
    "VIOLETA": (185, 100, 245),
}


class Game:
    def __init__(self):
        self.Reset()

    def Reset(self):
        CenterX = GridCols // 2
        CenterY = GridRows // 2

        self.Snake = [
            (CenterX, CenterY),
            (CenterX - 1, CenterY),
            (CenterX - 2, CenterY),
            (CenterX - 3, CenterY),
        ]

        self.Direction = (1, 0)
        self.NextDirection = (1, 0)

        self.Score = 0
        self.Level = 1
        self.Lives = 1
        self.SpeedIncrease = 0
        self.State = "menu"
        self.GameOverReason = ""

        self.NowMs = 0
        self.NextMoveAt = BaseMoveInterval
        self.SlowUntilMs = 0

        self.FoodPos = None
        self.FoodType = "normal"
        self.SilverAppleExpiresAt = 0
        self.NormalAppleDeadline = NormalAppleLimit
        self.SpawnFood()

        self.Challenge = None
        self.NextChallengeAt = random.randint(
            ChallengeMinDelay,
            ChallengeMaxDelay
        )
        self.ChallengesCompleted = 0

        self.FeedbackText = ""
        self.FeedbackUntilMs = 0

    def Start(self):
        self.Reset()
        self.State = "play"

    @property
    def MoveIntervalMs(self):
        Interval = max(
            MinMoveInterval,
            BaseMoveInterval - self.SpeedIncrease
        )

        if self.NowMs < self.SlowUntilMs:
            Interval += SilverSlowExtra

        return Interval

    @property
    def ChallengeSecondsLeft(self):
        if self.Challenge is None:
            return 0.0

        return max(
            0.0,
            (self.Challenge["Deadline"] - self.NowMs) / 1000
        )

    @property
    def NormalAppleSecondsLeft(self):
        if self.FoodType != "normal":
            return 0.0

        return max(
            0.0,
            (self.NormalAppleDeadline - self.NowMs) / 1000
        )

    @property
    def SilverSlowActive(self):
        return self.NowMs < self.SlowUntilMs

    def SetDirection(self, Direction):
        if self.State != "play":
            return

        Dx, Dy = Direction
        CurrentDx, CurrentDy = self.Direction

        if (Dx, Dy) == (-CurrentDx, -CurrentDy):
            return

        self.NextDirection = (Dx, Dy)

    def TogglePause(self):
        if self.State == "play":
            self.State = "pause"
        elif self.State == "pause":
            self.State = "play"

    def Update(self, DtMs):
        if self.State != "play":
            return

        DtMs = max(0, min(int(DtMs), 100))
        self.NowMs += DtMs

        if (
            self.FoodType == "normal"
            and self.NowMs >= self.NormalAppleDeadline
        ):
            self.EndGame("Tu 20 sekunžu laikā neapēdi parasto ābolu!")
            return

        if (
            self.FoodType == "silver"
            and self.NowMs >= self.SilverAppleExpiresAt
        ):
            self.SpawnNormalFood()

        if self.Challenge is not None:
            if self.NowMs >= self.Challenge["Deadline"]:
                self.FailChallenge("Nokavēts reakcijas uzdevums!")
                return
        elif self.NowMs >= self.NextChallengeAt:
            self.StartChallenge()

        MovementSteps = 0

        while (
            self.State == "play"
            and self.NowMs >= self.NextMoveAt
            and MovementSteps < 3
        ):
            self.MoveSnake()
            self.NextMoveAt += self.MoveIntervalMs
            MovementSteps += 1

    def MoveSnake(self):
        self.Direction = self.NextDirection

        HeadX, HeadY = self.Snake[0]
        Dx, Dy = self.Direction
        NewHead = (HeadX + Dx, HeadY + Dy)
        X, Y = NewHead

        if X < 0 or X >= GridCols or Y < 0 or Y >= GridRows:
            self.EndGame("Čūska ietriecās sienā!")
            return

        WillEat = NewHead == self.FoodPos
        BodyToCheck = self.Snake if WillEat else self.Snake[:-1]

        if NewHead in BodyToCheck:
            self.EndGame("Čūska ietriecās sevī!")
            return

        self.Snake.insert(0, NewHead)

        if WillEat:
            EatenFoodType = self.FoodType
            self.Score += 10

            if EatenFoodType == "silver":
                self.SpeedIncrease = 0
                self.SlowUntilMs = self.NowMs + SilverSlowDuration
                self.FeedbackText = "Sudraba ābols! Ātrums atiestatīts."
                self.FeedbackUntilMs = self.NowMs + 2200
            else:
                self.SpeedIncrease = min(
                    BaseMoveInterval - MinMoveInterval,
                    self.SpeedIncrease + SpeedIncrease
                )
                self.FeedbackText = "+10 punkti"
                self.FeedbackUntilMs = self.NowMs + 1200

            self.UpdateLevel()
            self.SpawnFood()
        else:
            self.Snake.pop()

    def UpdateLevel(self):
        self.Level = min(5, (self.Score // LevelScoreStep) + 1)

    def SpawnFood(self):
        Occupied = set(self.Snake)
        FreeCells = [
            (X, Y)
            for X in range(GridCols)
            for Y in range(GridRows)
            if (X, Y) not in Occupied
        ]

        if not FreeCells:
            self.EndGame("Tu aizpildīji visu laukumu — uzvara!")
            return

        self.FoodPos = random.choice(FreeCells)
        self.FoodType = (
            "silver"
            if random.random() < SilverAppleChance
            else "normal"
        )

        if self.FoodType == "silver":
            self.SilverAppleExpiresAt = (
                self.NowMs + SilverAppleDuration
            )
            self.NormalAppleDeadline = 0
        else:
            self.SilverAppleExpiresAt = 0
            self.NormalAppleDeadline = self.NowMs + NormalAppleLimit

    def SpawnNormalFood(self):
        Occupied = set(self.Snake)
        FreeCells = [
            (X, Y)
            for X in range(GridCols)
            for Y in range(GridRows)
            if (X, Y) not in Occupied
        ]

        if not FreeCells:
            self.EndGame("Tu aizpildīji visu laukumu — uzvara!")
            return

        self.FoodPos = random.choice(FreeCells)
        self.FoodType = "normal"
        self.SilverAppleExpiresAt = 0
        self.NormalAppleDeadline = self.NowMs + NormalAppleLimit

    def StartChallenge(self):
        ChallengeType = random.choice(("key", "color", "mouse"))
        Deadline = self.NowMs + ChallengeDuration

        if ChallengeType == "key":
            KeyLabel = random.choice(tuple(ReactionKeys.keys()))
            self.Challenge = {
                "Type": "key",
                "Key": KeyLabel,
                "Deadline": Deadline,
            }

        elif ChallengeType == "color":
            ColorName = random.choice(tuple(Colors.keys()))
            self.Challenge = {
                "Type": "color",
                "Color": ColorName,
                "Deadline": Deadline,
            }

        else:
            Occupied = set(self.Snake)
            Occupied.add(self.FoodPos)

            FreeCells = [
                (X, Y)
                for X in range(2, GridCols - 2)
                for Y in range(2, GridRows - 2)
                if (X, Y) not in Occupied
            ]

            Target = (
                random.choice(FreeCells)
                if FreeCells
                else (GridCols // 2, GridRows // 2)
            )

            self.Challenge = {
                "Type": "mouse",
                "Target": Target,
                "Deadline": Deadline,
            }

    def AnswerKey(self, KeyLabel):
        if self.State != "play" or not self.Challenge:
            return

        if self.Challenge["Type"] != "key":
            return

        if KeyLabel.upper() == self.Challenge["Key"]:
            self.CompleteChallenge()
        else:
            self.FailChallenge("Nepareizs taustiņš!")

    def AnswerColor(self, ColorName):
        if self.State != "play" or not self.Challenge:
            return

        if self.Challenge["Type"] != "color":
            return

        if ColorName == self.Challenge["Color"]:
            self.CompleteChallenge()
        else:
            self.FailChallenge("Nepareizā krāsa!")

    def AnswerMouseCell(self, Cell):
        if self.State != "play" or not self.Challenge:
            return

        if self.Challenge["Type"] != "mouse":
            return

        TargetX, TargetY = self.Challenge["Target"]
        MouseX, MouseY = Cell

        if (
            abs(MouseX - TargetX) <= 1
            and abs(MouseY - TargetY) <= 1
        ):
            self.CompleteChallenge()

    def FailColorClick(self):
        if self.State == "play" and self.Challenge:
            if self.Challenge["Type"] == "color":
                self.FailChallenge("Klikšķini uz pareizās krāsas!")

    def CompleteChallenge(self):
        self.Challenge = None
        self.ChallengesCompleted += 1
        self.Score += 5
        self.UpdateLevel()
        self.FeedbackText = "+5 punkti"
        self.FeedbackUntilMs = self.NowMs + 1500
        self.NextChallengeAt = (
            self.NowMs
            + random.randint(ChallengeMinDelay, ChallengeMaxDelay)
        )

    def FailChallenge(self, Reason):
        self.Challenge = None
        self.EndGame(Reason)

    def EndGame(self, Reason):
        self.State = "over"
        self.GameOverReason = Reason
        self.Challenge = None