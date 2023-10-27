class GameState:

    def __init__(self):
        self.board = [['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
                      ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
                      ['--', '--', '--', '--', '--', '--', '--', '--'],
                      ['--', '--', '--', '--', '--', '--', '--', '--'],
                      ['--', '--', '--', '--', '--', '--', '--', '--'],
                      ['--', '--', '--', '--', '--', '--', '--', '--'],
                      ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
                      ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]

        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'K': self.getKingMoves,
                              'Q': self.getQueenMoves, 'N': self.getKnightMoves, 'B': self.getBishopMoves}
        self.whiteToMove = True
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = ()
        self.moveLog = []
        # self.redoMoveLog = []
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [
            CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.wqs, self.currentCastlingRight.bks,
                         self.currentCastlingRight.bqs)]

    def makeMove(self, move):
        """
        Takes a move as a parameter and executes it (this will not work for castling, pawn promotion, and en-passant)
        :param move:
        :return:
        """
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)  # log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove  # swap players
        # update King's position
        if move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        # pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"
        # enpassant move
        # if move.isEnpassantMove:
        #     print("here")
        #     self.board[move.startRow][move.endCol] = '--'  # capturing the pawn
        # if self.isEnpassantMove:
        # print(move.moveID, move.startRow, move.startCol, move.pieceCaptured, move.pieceMoved, move.isEnpassantMove,
        #       move.isCastleMove)

        # update enpassantPossible variable
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.endCol)
        else:
            self.enpassantPossible = ()
        # if en passant move, must update the board to capture the pawn
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"

        # castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # king side castle move
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = '--'
            else:  # queen side castle move
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = '--'

        # if castle move, must update the board to move the Rook and king
        self.updateCastleRights(move)
        self.castleRightsLog.append(
            CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.wqs, self.currentCastlingRight.bks,
                         self.currentCastlingRight.bqs))

    def undoMove(self):
        """
        Un-do's the last move
        :param :
        :return:
        """
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            # if flag:
            #     self.redoMoveLog.append(move)
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            # update King's position
            if move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            # undo enpassant move
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'  # leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured  # puts the pawn back on the correct square
                self.enpassantPossible = (move.endRow, move.endCol)  # allow an enpassant to happen on the next move
            # undo a 2 square pawn advance
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()
            # undo castling rights
            self.castleRightsLog.pop()
            self.currentCastlingRight = self.castleRightsLog[-1]
            # undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # king side castle move
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = "--"
                else:  # queen side castle move
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = "--"
            self.checkMate = False
            self.staleMate = False

    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bqs = False
            self.currentCastlingRight.bks = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.wks = False

    # def redoMove(self):
    #     """
    #     Re-do's the last undo move
    #     :return:
    #     """
    #     if self.redoMoveLog:
    #         move = self.redoMoveLog.pop()
    #         self.moveLog.append(move)
    #         self.board[move.startRow][move.startCol] = move.pieceCaptured
    #         self.board[move.endRow][move.endCol] = move.pieceMoved
    #         self.whiteToMove = not self.whiteToMove
    #         # update King's position
    #         if move.pieceMoved == "bK":
    #             self.blackKingLocation = (move.endRow, move.endCol)
    #         elif move.pieceMoved == "wK":
    #             self.whiteKingLocation = (move.endRow, move.endCol)

    def getValidMoves(self):
        """
        All moves considering checks
        :return:
        """
        # # 1. generate all possible moves
        # # 5. if they do attack your king, not a valid move
        # moves = self.getAllPossibleMoves()
        # # 2. for each move, make the move
        # for i in range(len(moves) - 1, -1, -1):
        #     self.makeMove(moves[i])
        #     # 3. generate all opponent's moves
        #     # 4. for each of your opponent's moves, see if they attack your king
        #     self.whiteToMove = not self.whiteToMove
        #     if self.inCheck():
        #         # 5. if they do attack your king, not a valid move
        #         moves.remove(moves[i])
        #     self.whiteToMove = not self.whiteToMove
        #     self.undoMove()

        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1:  # can either block check or move King
                moves = self.getAllPossibleMoves()
                # To block a check you must move a piece into one of the squares between the enemy piece and king
                check = self.checks[0]  # check information
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]  # enemy piece causing the check
                validSquares = []  # squares that pieces can move to
                # if knight, must capture knight or move king, other pieces can be blocked
                if pieceChecking[1] == "N":
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)  # check[2] and check[3) are the
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:  # once you get to piece end check
                            # directions
                            break
                # get rid of any moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != "K":
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else:  # double check only king has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else:
            moves = self.getAllPossibleMoves()
            self.getCastleMoves(kingRow, kingCol, moves)
        if len(moves) == 0:  # can be either checkmate or stalemate
            if self.inCheck:
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.staleMate = False
            self.checkMate = False
        return moves

    def checkForPinsAndChecks(self):
        pins = []  # squares where the allied pinned piece is and direction pinned from
        checks = []  # squares where enemy is applying a check
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        # check outward from king for pins and checks, keep track of pins
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()  # reset possible pins
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != "K":
                        if possiblePin == ():  # 1st allied piece could pe pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break
                    elif endPiece[0] == enemyColor:
                        typeOfPiece = endPiece[1]
                        # Five possibilities here in this complex conditional statement
                        # 1. Orthogonally away from king and piece is a rook
                        # 2. Diagonally away from king and piece is a bishop
                        # 3. 1 square  diagonally away from king and piece is a pawn
                        # 5. Any direction 1 square away and piece is a king (this is necessary to prevent a king move
                        # to a square that controlled by another king)
                        if (0 <= j <= 3 and typeOfPiece == "R") or (4 <= j <= 7 and typeOfPiece == "B") \
                                or (i == 1 and typeOfPiece == "p" and (
                                (enemyColor == "w" and 6 <= j <= 7) or (enemyColor == "b" and 4 <= j <= 5))) \
                                or (typeOfPiece == "Q") or (i == 1 and typeOfPiece == "K"):
                            if possiblePin == ():  # No piece blocking, so check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else:  # enemy piece not applying check
                            break
                else:  # off board
                    break
        # check for knight checks
        knightMoves = [(-2, -1), (-2, 1), (2, -1), (2, 1), (1, -2), (1, 2), (-1, -2), (-1, 2)]
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == "N":  # enemy knight attacking king
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks

    # def inCheck(self):
    #     """
    #     Determine if the current player is in check
    #     :return:
    #     """
    #     if self.whiteToMove:
    #         return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
    #     else:
    #         return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def squareUnderAttack(self, r, c):
        """
        Determine if the enemy can attack the square r, c
        :param r:
        :param c:
        :return:
        """
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    def getAllPossibleMoves(self):
        """
        All moves without considering checks
        :return:
        """
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)
        return moves

    def getPawnMoves(self, r, c, moves):
        """
        Get all the pawn moves for the pawn located at row, col and add these moves to the list
        :param r:
        :param c:
        :param moves:
        :return:
        """
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        if self.whiteToMove:  # white pawn moves
            if self.board[r - 1][c] == '--':  # 1 square pawn advance
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((r, c), (r - 1, c), self.board))
                    if r == 6 and self.board[r - 2][c] == "--":  # 2 square pawn advance
                        moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:  # captures to the left
                if self.board[r - 1][c - 1][0] == 'b':  # enemy piece to capture
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.enpassantPossible:
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantPossible=True))

            if c + 1 <= 7:  # captures to the right
                if self.board[r - 1][c + 1][0] == 'b':  # enemy piece to capture
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enpassantPossible:
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantPossible=True))

        else:  # black pawn moves
            if self.board[r + 1][c] == '--':  # 1 square pawn advance
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    if r == 1 and self.board[r + 2][c] == "--":  # 2 square pawn advance
                        moves.append(Move((r, c), (r + 2, c), self.board))

            if c - 1 >= 0:  # captures to the left
                if self.board[r + 1][c - 1][0] == 'w':  # enemy piece to capture
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enpassantPossible:
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantPossible=True))
            if c + 1 <= 7:  # captures to the right
                if self.board[r + 1][c + 1][0] == 'w':  # enemy piece to capture
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enpassantPossible:
                    if not piecePinned or pinDirection == (1, 0):
                        moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantPossible=True))

    def getRookMoves(self, r, c, moves):
        """
        Get all the Rook moves for the pawn located at row, col and add these moves to the list
        :param r:
        :param c:
        :param moves:
        :return:
        """
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != "Q":  # can't remove queen from pin on rook moves, only remove it on bishop
                    # moves
                    self.pins.remove(self.pins[i])
                break
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        enemy = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                row = r + d[0] * i
                col = c + d[1] * i
                if 0 <= row < 8 and 0 <= col < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        if self.board[row][col] == "--":
                            moves.append(Move((r, c), (row, col), self.board))
                        elif self.board[row][col][0] == enemy:
                            moves.append(Move((r, c), (row, col), self.board))
                            break
                        else:
                            break
                else:
                    break

    def getKnightMoves(self, r, c, moves):
        """
                Get all the Knight moves for the pawn located at row, col and add these moves to the list
                :param r:
                :param c:
                :param moves:
                :return:
        """
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        directions = [(-2, -1), (-2, 1), (2, -1), (2, 1), (1, -2), (1, 2), (-1, -2), (-1, 2)]
        notEnemy = "w" if self.whiteToMove else "b"
        for d in directions:
            row = r + d[0]
            col = c + d[1]
            if 0 <= row < 8 and 0 <= col < 8:
                if not piecePinned:
                    if self.board[row][col][0] != notEnemy:
                        moves.append(Move((r, c), (row, col), self.board))

    def getBishopMoves(self, r, c, moves):
        """
                Get all the Bishop moves for the pawn located at row, col and add these moves to the list
                :param r:
                :param c:
                :param moves:
                :return:
        """
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
        enemy = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                row = r + d[0] * i
                col = c + d[1] * i
                if 0 <= row < 8 and 0 <= col < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        if self.board[row][col] == "--":
                            moves.append(Move((r, c), (row, col), self.board))
                        elif self.board[row][col][0] == enemy:
                            moves.append(Move((r, c), (row, col), self.board))
                            break
                        else:
                            break
                else:
                    break

    def getKingMoves(self, r, c, moves):
        """
                Get all the King moves for the pawn located at row, col and add these moves to the list
                :param r:
                :param c:
                :param moves:
                :return:
        """
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]
        notEnemy = "w" if self.whiteToMove else "b"
        for d in directions:
            row = r + d[0]
            col = c + d[1]
            if 0 <= row < 8 and 0 <= col < 8:
                endPiece = self.board[row][col]
                if endPiece[0] != notEnemy:
                    # place king on end square and check for checks
                    if notEnemy == "w":
                        self.whiteKingLocation = (row, col)
                    else:
                        self.blackKingLocation = (row, col)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r, c), (row, col), self.board))
                    if notEnemy == "w":
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)

    def getCastleMoves(self, r, c, moves):
        if self.inCheck:
            return
        if (self.whiteToMove and self.currentCastlingRight.wks) or (
                not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingSideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (
                not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueenSideCastleMoves(r, c, moves)

    def getKingSideCastleMoves(self, r, c, moves):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastle=True))

    def getQueenSideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--':
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastle=True))

    def getQueenMoves(self, r, c, moves):
        """
                Get all the Queen moves for the pawn located at row, col and add these moves to the list
                :param r:
                :param c:
                :param moves:
                :return:
        """
        self.getBishopMoves(r, c, moves)
        self.getRookMoves(r, c, moves)


class CastleRights:
    def __init__(self, wks, wqs, bks, bqs):
        self.wks = wks
        self.wqs = wqs
        self.bks = bks
        self.bqs = bqs


class Move:
    # maps keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantPossible=False, isCastle=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # pawn promotion
        self.isPawnPromotion = (self.endRow == 0 and self.pieceMoved == 'wp') or \
                               (self.endRow == 7 and self.pieceMoved == 'bp')
        # Enpassant
        self.isEnpassantMove = isEnpassantPossible
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        # Castling
        self.isCastleMove = isCastle
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        # if self.isCastleMove:
        #           self.isCastleMove)

    def __eq__(self, other):
        """
        Overriding the equals method
        :param other:
        :return:
        """
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
