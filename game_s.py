import pygame
import random
import cv2
import mediapipe as mp
import numpy as np
import os


pygame.init()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Gesture Control Racing Game")


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


player_car_images = ["./assets/img/player_car.png", "./assets/img/player_car_2.png", "./assets/img/player_car_3.png"]
obstacle_car_images = ["./assets/img/obstacle_car.png", "./assets/img/obstacle_car_2.png", "./assets/img/obstacle_car_3.png"]
power_up_image = pygame.image.load("./assets/img/power_up.png")
power_up_image = pygame.transform.scale(power_up_image, (50, 50))
background = pygame.image.load("./assets/img/road.png")
background = pygame.transform.scale(background, (screen_width, screen_height))


crash_sound = pygame.mixer.Sound('./assets/sounds/crash.wav')
score_sound = pygame.mixer.Sound('./assets/sounds/score.wav')
power_up_sound = pygame.mixer.Sound('./assets/sounds/power_up.wav')




mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils


cap = cv2.VideoCapture(0)


player_x, player_y = screen_width // 2, screen_height - 120
player_speed = 10
base_obstacle_speed = 5
obstacles = []
power_ups = []
score = 0
game_over = False
acceleration = 0.01
scroll_y = 0
hand_tracking_box_size = 200
level = 1
player_car_choice = 0


font = pygame.font.SysFont(None, 36)
large_font = pygame.font.SysFont(None, 72)


def detect_gesture(landmarks):
    wrist = landmarks[0]
    index_tip = landmarks[8]

    if index_tip.x > wrist.x + 0.1:
        return "right"
    elif index_tip.x < wrist.x - 0.1:
        return "left"
    else:
        return "neutral"


def create_obstacle():
    x = random.randint(50, screen_width - 50)
    y = -100
    obstacle_choice = random.choice(obstacle_car_images)
    obstacle_img = pygame.image.load(obstacle_choice)
    obstacle_img = pygame.transform.scale(obstacle_img, (50, 100))
    return [x, y, obstacle_img]


def create_power_up():
    x = random.randint(50, screen_width - 50)
    y = -100
    return [x, y]


def move_obstacles(obstacles, speed):
    for obs in obstacles:
        obs[1] += speed
    return obstacles


def move_power_ups(power_ups, speed):
    for power in power_ups:
        power[1] += speed
    return power_ups

def draw_hand_tracking_box(frame, gesture):

    frame_height, frame_width = frame.shape[:2]
    roi = cv2.resize(frame, (hand_tracking_box_size, hand_tracking_box_size))
    roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
    roi_rgb = np.rot90(roi_rgb)
    frame_surface = pygame.surfarray.make_surface(roi_rgb)
    screen.blit(frame_surface, (screen_width - hand_tracking_box_size - 10, 10))
    border_thickness = 3
    pygame.draw.rect(screen, RED, (screen_width - hand_tracking_box_size - 10, 10, hand_tracking_box_size, hand_tracking_box_size), border_thickness)
    gesture_text = font.render(gesture.capitalize(), True, RED)
    text_x = screen_width - hand_tracking_box_size - 10 + (hand_tracking_box_size - gesture_text.get_width()) // 2
    text_y = 10 + hand_tracking_box_size + 5
    screen.blit(gesture_text, (text_x, text_y))
    frame_height, frame_width = frame.shape[:2]
    roi = cv2.resize(frame, (hand_tracking_box_size, hand_tracking_box_size))

    roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
    roi_rgb = np.rot90(roi_rgb)
    frame_surface = pygame.surfarray.make_surface(roi_rgb)
    screen.blit(frame_surface, (screen_width - hand_tracking_box_size - 10, 10))

    border_thickness = 3
    pygame.draw.rect(screen, RED, (screen_width - hand_tracking_box_size - 10, 10, hand_tracking_box_size, hand_tracking_box_size), border_thickness)


def start_screen():
    screen.fill(WHITE)
    title_text = large_font.render("Gesture Control Racing Game", True, BLACK)
    instruction_text = font.render("Move your hand left or right to control the car", True, BLACK)
    start_text = font.render("Press any key to start", True, RED)
    car_choice_text = font.render("Choose Your Car: 1, 2, 3", True, GREEN)

    screen.blit(title_text, (screen_width//2 - title_text.get_width()//2, screen_height//2 - 150))
    screen.blit(instruction_text, (screen_width//2 - instruction_text.get_width()//2, screen_height//2 - 50))
    screen.blit(start_text, (screen_width//2 - start_text.get_width()//2, screen_height//2 + 50))
    screen.blit(car_choice_text, (screen_width//2 - car_choice_text.get_width()//2, screen_height//2 + 150))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    global player_car_choice
                    player_car_choice = event.key - pygame.K_1
                waiting = False


def game_over_screen(score, high_score):

    global screen
    screen.fill(WHITE)
    game_over_text = large_font.render("Game Over!", True, BLACK)
    score_text = font.render(f"Your Score: {score}", True, BLACK)
    high_score_text = font.render(f"High Score: {high_score}", True, BLUE)
    restart_text = font.render("Press any key to restart", True, RED)

    screen.blit(game_over_text, (screen_width//2 - game_over_text.get_width()//2, screen_height//2 - 100))
    screen.blit(score_text, (screen_width//2 - score_text.get_width()//2, screen_height//2))
    screen.blit(high_score_text, (screen_width//2 - high_score_text.get_width()//2, screen_height//2 + 50))
    screen.blit(restart_text, (screen_width//2 - restart_text.get_width()//2, screen_height//2 + 150))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                waiting = False


def load_high_score():
    if os.path.exists("highscore.txt"):
        with open("highscore.txt", "r") as file:
            return int(file.read().strip())
    return 0


def save_high_score(score):
    with open("highscore.txt", "w") as file:
        file.write(str(score))


start_screen()


player_car = pygame.image.load(player_car_images[player_car_choice])
player_car = pygame.transform.scale(player_car, (50, 100))


running = True
high_score = load_high_score()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    gesture = "neutral"
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            gesture = detect_gesture(hand_landmarks.landmark)

            if gesture == "right":
                player_x += player_speed
            elif gesture == "left":
                player_x -= player_speed


    player_x = max(0, min(player_x, screen_width - player_car.get_width()))


    if random.randint(1, 50) == 1:
        obstacles.append(create_obstacle())


    if random.randint(1, 100) == 1:
        power_ups.append(create_power_up())

    obstacle_speed = base_obstacle_speed + score * acceleration
    obstacles = move_obstacles(obstacles, obstacle_speed)
    power_ups = move_power_ups(power_ups, obstacle_speed)


    player_rect = pygame.Rect(player_x, player_y, player_car.get_width(), player_car.get_height())
    new_obstacles = []
    for obs in obstacles:
        obstacle_rect = pygame.Rect(obs[0], obs[1], obs[2].get_width(), obs[2].get_height())
        if player_rect.colliderect(obstacle_rect):
            crash_sound.play()
            game_over = True
        elif obs[1] > screen_height:
            score += 1
            score_sound.play()
        else:
            new_obstacles.append(obs)


    new_power_ups = []
    for power in power_ups:
        power_rect = pygame.Rect(power[0], power[1], power_up_image.get_width(), power_up_image.get_height())
        if player_rect.colliderect(power_rect):
            power_up_sound.play()
            score += 5
        elif power[1] > screen_height:
            continue
        else:
            new_power_ups.append(power)

    obstacles = new_obstacles
    power_ups = new_power_ups


    screen.fill(WHITE)
    scroll_y = (scroll_y + obstacle_speed) % screen_height
    screen.blit(background, (0, scroll_y - screen_height))
    screen.blit(background, (0, scroll_y))
    screen.blit(player_car, (player_x, player_y))
    for obs in obstacles:
        screen.blit(obs[2], (obs[0], obs[1]))
    for power in power_ups:
        screen.blit(power_up_image, (power[0], power[1]))


    draw_hand_tracking_box(frame, gesture)


    score_text = font.render(f"Score: {score}", True, BLACK)
    level_text = font.render(f"Level: {level}", True, GREEN)
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (screen_width - 150, 10))


    if score // 10 > level - 1:
        level += 1
        base_obstacle_speed += 1


    pygame.display.flip()


    if game_over:
        if score > high_score:
            high_score = score
            save_high_score(high_score)
        game_over_screen(score, high_score)

        player_x, player_y = screen_width // 2, screen_height - 120
        obstacles.clear()
        power_ups.clear()
        score = 0
        game_over = False
        level = 1
        base_obstacle_speed = 7

cap.release()
cv2.destroyAllWindows()
pygame.quit()
