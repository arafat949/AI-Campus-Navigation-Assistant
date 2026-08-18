"""
Minimax + Alpha-Beta Pruning - implemented as a playable Tic-Tac-Toe AI.

Framed in the project as a small "Beat the Campus AI" mini-game: the student
(HUMAN, "X") plays against the AI (AI, "O"). The AI always plays optimally
because Minimax explores the full game tree (Tic-Tac-Toe's tree is small
enough to search completely), and Alpha-Beta pruning cuts off branches that
can't possibly change the final decision - so the AI reaches the same optimal
move while exploring far fewer nodes. The node count returned to the frontend
demonstrates that saving.
"""

HUMAN, AI, EMPTY = "X", "O", ""

WIN_LINES = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],   # rows
    [0, 3, 6], [1, 4, 7], [2, 5, 8],   # columns
    [0, 4, 8], [2, 4, 6],              # diagonals
]


def winner(board):
    for a, b, c in WIN_LINES:
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return board[a]
    return None


def is_full(board):
    return all(cell != EMPTY for cell in board)


def minimax(board, depth, alpha, beta, maximizing, stats):
    stats["nodes"] += 1
    win = winner(board)
    if win == AI:
        return 10 - depth
    if win == HUMAN:
        return depth - 10
    if is_full(board):
        return 0

    if maximizing:
        best = -1000
        for i in range(9):
            if board[i] == EMPTY:
                board[i] = AI
                best = max(best, minimax(board, depth + 1, alpha, beta, False, stats))
                board[i] = EMPTY
                alpha = max(alpha, best)
                if beta <= alpha:
                    break  # alpha-beta cut-off
        return best
    else:
        best = 1000
        for i in range(9):
            if board[i] == EMPTY:
                board[i] = HUMAN
                best = min(best, minimax(board, depth + 1, alpha, beta, True, stats))
                board[i] = EMPTY
                beta = min(beta, best)
                if beta <= alpha:
                    break  # alpha-beta cut-off
        return best


def best_move(board):
    """Given the current board (list of 9 cells), return the AI's optimal move."""
    stats = {"nodes": 0}
    best_score = -1000
    move = -1
    for i in range(9):
        if board[i] == EMPTY:
            board[i] = AI
            score = minimax(board, 0, -1000, 1000, False, stats)
            board[i] = EMPTY
            if score > best_score:
                best_score = score
                move = i

    result_board = list(board)
    game_over = False
    result_text = None
    if move != -1:
        result_board[move] = AI
        w = winner(result_board)
        if w == AI:
            game_over, result_text = True, "AI wins"
        elif is_full(result_board):
            game_over, result_text = True, "Draw"

    return {
        "move": move,
        "score": best_score,
        "nodes_explored": stats["nodes"],
        "board": result_board,
        "game_over": game_over,
        "result": result_text,
    }
