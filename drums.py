import pygame
from pygame import mixer
pygame.init()

# screen dimensions
WIDTH = 1366
HEIGHT = 695

# some colors we'll use below
black = (0,0,0)
white = (225,225,225)
gray = (96,96,96)
dark_gray = (50,50,50)
light_gray = (130,130,130)
green = (39,145,27)
gold = (212,175,55)
blue = (0, 255, 255)

# window creation and settings
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Electronic Drums')
label_font = pygame.font.Font('freesansbold.ttf', 28)
medium_font = pygame.font.Font('freesansbold.ttf', 22)

fps = 60
timer = pygame.time.Clock()
beats = 8
instruments = 6
boxes = []
clicked = [[-1 for _ in range(beats)] for _ in range(instruments)] # create a 'matrix' of -1 for non-active beats per instrument
bpm = 240
playing = False
active_length = 0
active_beat = 0
beat_changed = True
active_list = [1 for _ in range(instruments)] # create a vector of 1 for active instruments
save_menu = False
load_menu = False
saved_beats = []
file = open('saved_beats.txt', 'r')
for line in file:
    saved_beats.append(line)
beat_name = ''
typing = False
index = 100


# load in sounds
hi_hat = mixer.Sound('sounds/hi hat.WAV')
clap = mixer.Sound('sounds/clap.wav')
snare = mixer.Sound('sounds/snare.WAV')
kick = mixer.Sound('sounds/kick.WAV')
crash = mixer.Sound('sounds/crash.wav')
tom = mixer.Sound('sounds/tom.WAV')
pygame.mixer.set_num_channels(instruments*3)


# plays parts of the drums
def play_notes():
    for i in range(len(clicked)):
        if clicked[i][active_beat] == 1 and active_list[i] == 1:
            if i == 0:
                hi_hat.play()
            if i == 1:
                snare.play()
            if i == 2:
                kick.play()
            if i == 3:
                crash.play()
            if i == 4:
                clap.play()
            if i == 5:
                tom.play()


# subdivisons of the screen
def draw_grid(clicks, beat, actives):
    left_box = pygame.draw.rect(screen, gray, [0,0,200,HEIGHT-210], 5)
    bottom_box = pygame.draw.rect(screen, gray, [0, HEIGHT-215, WIDTH, 215], 5)
    boxes = []
    colors = [gray, white, dark_gray]

    hi_hat_text = label_font.render('Hi Hat', True, colors[actives[0]])
    screen.blit(hi_hat_text, (30,30))
    snare_text = label_font.render('Snare', True, colors[actives[1]])
    screen.blit(snare_text, (30,110))
    kick_text = label_font.render('Bass Drum', True, colors[actives[2]])
    screen.blit(kick_text, (30,190))
    crash_text = label_font.render('Crash', True, colors[actives[3]])
    screen.blit(crash_text, (30,270))
    clap_text = label_font.render('Clap', True, colors[actives[4]])
    screen.blit(clap_text, (30,350))
    tom_text = label_font.render('Floor Tom', True, colors[actives[5]])
    screen.blit(tom_text, (30,430))

    for i in range(instruments):
        pygame.draw.line(screen, gray, (0, (i*80)), (195, (i*80)), 5)

    for i in range(beats):
        for j in range(instruments):
            if clicks[j][i] == -1:
                color = gray
            else:
                if actives[j]==1:
                    color = green
                else:
                    color = dark_gray
            rect = pygame.draw.rect(screen, color, [i*((WIDTH-200)//beats) + 200, j*80, (WIDTH-200)//beats, (HEIGHT-215)//instruments - 5], 0, 3)
            pygame.draw.rect(screen, gold, [i*((WIDTH-200)//beats) + 200, j*80, (WIDTH-200)//beats, (HEIGHT-215)//instruments], 5, 5)
            pygame.draw.rect(screen, black, [i*((WIDTH-200)//beats) + 200, j*80, (WIDTH-200)//beats, (HEIGHT-215)//instruments], 2, 5)
            boxes.append((rect, (i,j)))

        active = pygame.draw.rect(screen, blue, [beat*((WIDTH-200)//beats) + 200, 0, (WIDTH-200)//beats, instruments*80], 5, 3)
    return boxes

# draws the save menu when you hit save button
def draw_save_menu(beat_name, typing):
    pygame.draw.rect(screen, black, [0, 0, WIDTH, HEIGHT])
    menu_text = label_font.render('SAVE MENU: Enter a Name for Curent Beat', True, white)
    saving_btn = pygame.draw.rect(screen, gray, [WIDTH//2 - 200, HEIGHT*0.75, 400, 100], 0, 5)
    saving_txt = label_font.render('Save Beat', True, white)
    screen.blit(saving_txt, (WIDTH//2 - 70, HEIGHT * 0.75 + 30))
    screen.blit(menu_text, (400, 40))
    exit_btn = pygame.draw.rect(screen, gray, [WIDTH-200, HEIGHT-100, 180, 90], 0, 5)
    exit_text = label_font.render('Close', True, white)
    screen.blit(exit_text, (WIDTH-160, HEIGHT-70))
    if typing:
        pygame.draw.rect(screen, dark_gray, [400, 200, 600, 200], 0, 5)
    entry_rect = pygame.draw.rect(screen, gray, [400, 200, 600, 200], 5, 5)
    entry_text = label_font.render(f'{beat_name}', True, white)
    screen.blit(entry_text, (430, 250))
    return exit_btn, saving_btn, entry_rect


# draws the load menu when you hit load button
def draw_load_menu(index):
    loaded_clicked = []
    loaded_beats = 0
    loaded_bpm = 0
    pygame.draw.rect(screen, black, [0, 0, WIDTH, HEIGHT])
    menu_text = label_font.render('LOAD MENU: Select a Beat to Load', True, white)
    loading_btn = pygame.draw.rect(screen, gray, [WIDTH//2 - 200, HEIGHT*0.75, 400, 100], 0, 5)
    loading_txt = label_font.render('Load Beat', True, white)
    screen.blit(loading_txt, (WIDTH//2 - 70, HEIGHT * 0.75 + 30))
    screen.blit(menu_text, (400, 40))
    delete_btn = pygame.draw.rect(screen, gray, [WIDTH//2 - 500, HEIGHT*0.75, 200, 100], 0, 5)
    delete_text = label_font.render('Delete Beat', True, white)
    screen.blit(delete_text, (WIDTH//2 - 485, HEIGHT*0.75 + 30))
    exit_btn = pygame.draw.rect(screen, gray, [WIDTH-200, HEIGHT-100, 180, 90], 0, 5)
    exit_text = label_font.render('Close', True, white)
    screen.blit(exit_text, (WIDTH-160, HEIGHT-70))
    loaded_rectangle = pygame.draw.rect(screen, gray, [190, 90, 1000, 400], 3, 5)
    if 0<= index < len(saved_beats):
        pygame.draw.rect(screen, light_gray, [190, 90 + index*50, 1000, 50], 0, 5)
    for beat in range(len(saved_beats)):
        if beat < 8:
            beat_clicked = []
            row_text = medium_font.render(f'{beat + 1}', True, white)
            screen.blit(row_text, (200, 100 + beat*50))
            name_index_start = saved_beats[beat].index('name: ') + 6
            name_index_end = saved_beats[beat].index(', beats:')
            name_text = medium_font.render(saved_beats[beat][name_index_start:name_index_end], True, white)
            screen.blit(name_text, (240, 100 + beat*50))
        if 0 <= index < len(saved_beats) and beat == index:
            beat_index_end = saved_beats[beat].index(', bpm:')
            loaded_beats = int(saved_beats[beat][name_index_end + 8:beat_index_end])
            bpm_index_end = saved_beats[beat].index(', selected:')
            loaded_bpm = int(saved_beats[beat][beat_index_end + 6: bpm_index_end])
            loaded_clicks_string = saved_beats[beat][bpm_index_end + 14: -3]
            loaded_clicks_rows = list(loaded_clicks_string.split('], ['))
            for row in range(len(loaded_clicks_rows)):
                loaded_row = (loaded_clicks_rows[row].split(', '))
                for item in range(len(loaded_row)):
                    if loaded_row[item] == '1' or loaded_row[item] == '-1':
                        loaded_row[item] = int(loaded_row[item])
                beat_clicked.append(loaded_row)
                loaded_clicked = beat_clicked
    loaded_info = [loaded_beats, loaded_bpm, loaded_clicked]

    return exit_btn, loading_btn, delete_btn, loaded_rectangle, loaded_info


run = True
while run:
    timer.tick(fps)
    screen.fill(black)
    boxes = draw_grid(clicked, active_beat, active_list)

    # Menu Buttons
    # play/pause button
    play_pause = pygame.draw.rect(screen, gray, [50, HEIGHT-150, 200, 100], 0, 5)
    play_text = label_font.render('Play/Pause', True, white)
    screen.blit(play_text, (70, HEIGHT-130))
    if playing:
        play_text2 = medium_font.render('Playing', True, dark_gray)
    else:
        play_text2 = medium_font.render('Paused', True, dark_gray)
    screen.blit(play_text2, (100, HEIGHT-90))
   
    # bpm visualizer
    bpm_rect = pygame.draw.rect(screen, gray, [300, HEIGHT-150, 200, 100], 5, 5)
    bpm_text = medium_font.render('Beats per minute', True, white)
    screen.blit(bpm_text, (310, HEIGHT-130))
    bpm_text2 = label_font.render(f'{bpm}', True, white)
    screen.blit(bpm_text2, (370, HEIGHT-100))
    
    # bpm button
    bpm_add_rect = pygame.draw.rect(screen, gray, [510, HEIGHT-150, 48, 48], 0, 5)
    bpm_sub_rect = pygame.draw.rect(screen, gray, [510, HEIGHT-100, 48, 48], 0, 5)
    add_text = medium_font.render('+5', True, white)
    sub_text = medium_font.render('-5', True, white)
    screen.blit(add_text, (520, HEIGHT-135))
    screen.blit(sub_text, (525, HEIGHT-85))
    
    # beats visualizer
    beats_rect = pygame.draw.rect(screen, gray, [600, HEIGHT-150, 200, 100], 5, 5)
    beats_text = medium_font.render('Beats in loop', True, white)
    screen.blit(beats_text, (630, HEIGHT-130))
    beats_text2 = label_font.render(f'{beats}', True, white)
    screen.blit(beats_text2, (670, HEIGHT-100))
    
    # bpm button
    beats_add_rect = pygame.draw.rect(screen, gray, [810, HEIGHT-150, 48, 48], 0, 5)
    beats_sub_rect = pygame.draw.rect(screen, gray, [810, HEIGHT-100, 48, 48], 0, 5)
    add_text2 = medium_font.render('+1', True, white)
    sub_text2 = medium_font.render('-1', True, white)
    screen.blit(add_text2, (820, HEIGHT-135))
    screen.blit(sub_text2, (825, HEIGHT-85))
    
    # instruments rectangles
    instruments_rect = []
    for i in range(instruments):
        rect = pygame.rect.Rect((0, i*80), (200, 80))
        instruments_rect.append(rect)

    # save/load buttons
    save_button = pygame.draw.rect(screen, gray, [900, HEIGHT-150, 200, 48], 0, 5)
    save_text = label_font.render('Save Beat', True, white)
    screen.blit(save_text, (920, HEIGHT-140))
    load_button = pygame.draw.rect(screen, gray, [900, HEIGHT-100, 200, 48], 0, 5)
    load_text = label_font.render('Load Beat', True, white)
    screen.blit(load_text, (920, HEIGHT-90))

    # clear button
    clear_button = pygame.draw.rect(screen, gray, [1150, HEIGHT-150, 100, 100], 0, 5)
    clear_text = label_font.render('Clear', True, white)
    screen.blit(clear_text, (1160, HEIGHT-120))

    # save/load
    if save_menu:
        exit_button, saving_button, entry_rectangle = draw_save_menu(beat_name, typing)
    if load_menu:
        exit_button, loading_button, delete_button, loaded_rectangle, loaded_info = draw_load_menu(index)

    if beat_changed:
        play_notes()
        beat_changed = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and not save_menu and not load_menu: # choose which buttons are on/off on screen
            for i in range(len(boxes)):
                if boxes[i][0].collidepoint(event.pos):
                    coords = boxes[i][1]
                    # we turn on/off buttons by changing positivity of corresp. item in the matrix 'clicked'
                    clicked[coords[1]][coords[0]] *= -1
        if event.type == pygame.MOUSEBUTTONUP and not save_menu and not load_menu: # choose play or pause
            if play_pause.collidepoint(event.pos):
                if playing:
                    playing = False
                elif not playing:
                    playing = True
            elif bpm_add_rect.collidepoint(event.pos):
                bpm += 5
            elif bpm_sub_rect.collidepoint(event.pos):
                bpm -= 5
            elif beats_add_rect.collidepoint(event.pos):
                beats += 1
                for i in range(len(clicked)):
                    clicked[i].append(-1)
            elif beats_sub_rect.collidepoint(event.pos):
                beats -= 1
                for i in range(len(clicked)):
                    clicked[i].pop(-1)
            elif clear_button.collidepoint(event.pos): # resets clicked matrix to initial config
                clicked = [[-1 for _ in range(beats)] for _ in range(instruments)]
            elif save_button.collidepoint(event.pos):
                save_menu = True
            elif load_button.collidepoint(event.pos):
                load_menu = True

            for i in range(len(instruments_rect)):
                if instruments_rect[i].collidepoint(event.pos):
                    active_list[i] *=  -1
        elif event.type == pygame.MOUSEBUTTONUP:
            if exit_button.collidepoint(event.pos):
                save_menu = False
                load_menu = False
                playing = True
                beat_name = ''
                typing = False
            if load_menu:
                if loaded_rectangle.collidepoint(event.pos):
                    index = (event.pos[1] - 100)//50
                if delete_button.collidepoint(event.pos):
                    if 0<= index < len(saved_beats):
                        saved_beats.pop(index)
                if loading_button.collidepoint(event.pos):
                    if 0 <= index < len(saved_beats):
                        beats = loaded_info[0]
                        bpm = loaded_info[1]
                        clicked = loaded_info[2]
                        index = 100
                        load_menu = False
            if save_menu:
                if entry_rectangle.collidepoint(event.pos):
                    if typing:
                        typing = False
                    elif not typing:
                        typing = True
                if saving_button.collidepoint(event.pos):
                    file = open('saved_beats.txt', 'w')
                    saved_beats.append(f'\nname: {beat_name}, beats: {beats}, bpm: {bpm}, selected: {clicked}')
                    for i in range(len(saved_beats)):
                        file.write(str(saved_beats[i]))
                    file.close()
                    save_menu = False
                    typing = False
                    beat_name = ''
        if event.type == pygame.TEXTINPUT and typing:
            beat_name += event.text
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE and len(beat_name)>0 and typing:
                beat_name = beat_name[:-1]


    beat_length = (fps * 60)//bpm

    # playing the track
    if playing:
        if active_length < beat_length:
            active_length += 1
        else:
            active_length = 0
            if active_beat < beats - 1:
                active_beat += 1
                beat_changed = True
            else:
                active_beat = 0
                beat_changed = True

    pygame.display.flip()

pygame.quit()