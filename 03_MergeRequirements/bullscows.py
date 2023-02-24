from collections import defaultdict




def bullscows(guess: str, secret: str) -> (int, int):
    bulls, cows = 0, 0
    for a, b in zip(guess, secret):
        if a == b:
            bulls += 1

    g_dict = defaultdict(int)
    s_dict = defaultdict(int)
    for a in guess:
        g_dict[a] += 1
    for a in secret:
        s_dict[a] += 1
    for a, n in s_dict.items():
        cows += min(n, g_dict[a])
    cows -= bulls

    return bulls, cows



if __name__ == "__main__":
    print(bullscows('мама', 'папа'))
    print(bullscows('человек', 'ччччччч'))
    print(bullscows('привет', 'тевирп'))

