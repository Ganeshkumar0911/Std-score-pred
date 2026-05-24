FILES = "abcdefgh"

available_keys = ["pawn", "rook", "knight", "bishop", "queen", "king"]


def is_valid_position(pos):
    pos = pos.lower().strip()
    return len(pos) == 2 and pos[0] in FILES and pos[1] in "12345678"


def inside_board(file_index, rank):
    return 0 <= file_index < 8 and 1 <= rank <= 8


def to_position(file_index, rank):
    return FILES[file_index] + str(rank)


def get_index_rank(position):
    position = position.lower().strip()
    file_index = FILES.index(position[0])
    rank = int(position[1])
    return file_index, rank


def pawn_moves(file_index, rank, color):
    moves = []

    if color == "white":
        direction = 1
        starting_rank = 2
    else:
        direction = -1
        starting_rank = 7

    one_step = rank + direction
    if inside_board(file_index, one_step):
        moves.append(to_position(file_index, one_step))

    two_step = rank + 2 * direction
    if rank == starting_rank and inside_board(file_index, two_step):
        moves.append(to_position(file_index, two_step))

    return moves


def rook_moves(file_index, rank):
    moves = []
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for df, dr in directions:
        new_file = file_index + df
        new_rank = rank + dr

        while inside_board(new_file, new_rank):
            moves.append(to_position(new_file, new_rank))
            new_file += df
            new_rank += dr

    return moves


def bishop_moves(file_index, rank):
    moves = []
    directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

    for df, dr in directions:
        new_file = file_index + df
        new_rank = rank + dr

        while inside_board(new_file, new_rank):
            moves.append(to_position(new_file, new_rank))
            new_file += df
            new_rank += dr

    return moves


def queen_moves(file_index, rank):
    return rook_moves(file_index, rank) + bishop_moves(file_index, rank)


def knight_moves(file_index, rank):
    moves = []
    directions = [
        (1, 2), (2, 1),
        (2, -1), (1, -2),
        (-1, -2), (-2, -1),
        (-2, 1), (-1, 2)
    ]

    for df, dr in directions:
        new_file = file_index + df
        new_rank = rank + dr

        if inside_board(new_file, new_rank):
            moves.append(to_position(new_file, new_rank))

    return moves


def king_moves(file_index, rank):
    moves = []
    directions = [
        (1, 0), (-1, 0),
        (0, 1), (0, -1),
        (1, 1), (1, -1),
        (-1, 1), (-1, -1)
    ]

    for df, dr in directions:
        new_file = file_index + df
        new_rank = rank + dr

        if inside_board(new_file, new_rank):
            moves.append(to_position(new_file, new_rank))

    return moves


def possible_moves(piece, position, color):
    file_index, rank = get_index_rank(position)

    if piece == "pawn":
        return pawn_moves(file_index, rank, color)
    elif piece == "rook":
        return rook_moves(file_index, rank)
    elif piece == "bishop":
        return bishop_moves(file_index, rank)
    elif piece == "queen":
        return queen_moves(file_index, rank)
    elif piece == "knight":
        return knight_moves(file_index, rank)
    elif piece == "king":
        return king_moves(file_index, rank)


while True:
    print("\n--- Chess Possible Move Finder ---")
    print("Available chess keys/pieces:")

    for i, key in enumerate(available_keys, start=1):
        print(f"{i}. {key}")

    print("0. exit")

    choice = input("\nChoose a key number from the above list: ").strip()

    if choice == "0":
        print("Program stopped.")
        break

    if not choice.isdigit():
        print("Invalid choice. Enter number only.")
        continue

    choice = int(choice)

    if choice < 1 or choice > len(available_keys):
        print("Invalid choice. Choose from the given list.")
        continue

    selected_key = available_keys[choice - 1]

    print(f"\nYou selected: {selected_key}")

    color = input("Enter color white/black: ").lower().strip()

    if color not in ["white", "black"]:
        print("Invalid color. Enter white or black.")
        continue

    position = input("Enter position like a2, e4, h7: ").lower().strip()

    if not is_valid_position(position):
        print("Invalid position. Example: a2, e4, h7")
        continue

    moves = possible_moves(selected_key, position, color)

    print(f"\nPossible moves for {color} {selected_key} at {position}:")
    print(moves)