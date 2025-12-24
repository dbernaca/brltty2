"""
From libbrlapi's brlapi_keycodes.h:

Key codes are unsigned 64-bit integers. This 64-bit space is split into 3 parts:

- Bits 63-32 (KEY_FLAGS_MASK): Flags (e.g., shift, control, meta, etc.).
- Bits 31-29 (KEY_TYPE_MASK): Key type (either KEY_TYPE_CMD for braille commands or KEY_TYPE_SYM for standard X keysyms).
- bits 28-0 (KEY_CODE_MASK), key code: for braille commands, see
KEY_CMD_* ; for standard X keysyms, this is the keysym value, see
X11 documentation, a complete list is probably available on your system in
/usr/include/X11/keysymdef.h

The second and third part are thus mandatory to tell the type of keycode and
the value of the keycode, and the first part contains optional flags.

The third part is itself split into two parts: a command number and a command
value. The relative sizes of these parts vary according to the key type.

For a braille command, bits 28-16 (KEY_CMD_BLK_MASK) hold the braille
command number, while bits 15-0 (KEY_CMD_ARG_MASK) hold the command value.

The expandKeyCode() function may be used for splitting key codes into these parts.

For a X keysym, if it is a unicode keysym (0x1uvwxyz), then the command
number part is 0x1000000 and the value part is 0xuvwxyz. Else, the command
part is held by bits 28-8 and the value part is held by bits 7-0. This
permits to easily handle usual cases like 0x00xy (latin1), 0x01xy (latin2),
XK_Backspace (0xff08, backspace), XK_Tab (0xff09, tab), ...

For instance, if key == 0x0000000020010008,
- (key & KEY_TYPE_MASK) == KEY_TYPE_CMD, so it's a braille command
- (key & KEY_CMD_BLK_MASK) == KEY_CMD_ROUTE, so it's the braille route command.
- (key & KEY_CMD_ARG_MASK) == 8, so the highlighted cell is the 9th one (cells are numbered from 0)
- (key & KEY_FLAGS_MASK) == 0, so no modifier key was pressed during the command, and no particular flag applies to the command.

if key == 0x000000010000FF09,
- (key & KEY_TYPE_MASK) == KEY_TYPE_SYM, so it's a keysym
- (key & KEY_CODE_MASK) == XK_Tab, so it's the tab key.
KEY_SYM_TAB can also be used here, as well as a few other KEY_SYM_* constants which are provided
- (key & KEY_FLAGS_MASK) == KEY_FLG_SHIFT, so the shift modifier was pressed during the command.

in the X11 standard some keysyms are directly unicode, for instance if
key == 0x0000000001001EA0,
- (key & KEY_TYPE_MASK) == KEY_TYPE_SYM, so it's a keysym
- (key & KEY_SYM_UNICODE) != 0 so it's a unicode keysym, whose value
is key & (KEY_SYM_UNICODE-1). Of course, one can also consider
(key & KEY_CODE_MASK) == XK_Abelowdot
- (key & KEY_FLAGS_MASK) == 0, so no modifier key was pressed during
the command, and no particular flag applies to the command.
"""

# keyCode's biggest value
KEY_MAX = 0xFFFFFFFFFFFFFFFF

# Mask for flags of a keyCode
KEY_FLAGS_MASK = 0xFFFFFFFF00000000
# Shift for flags
KEY_FLAGS_SHIFT = 32

# Standard X modifiers
KEY_FLG_MOD1 = (0x00000008 << KEY_FLAGS_SHIFT)  # Mod1 (AKA meta)
KEY_FLG_MOD2 = (0x00000010 << KEY_FLAGS_SHIFT)  # Mod2 (usually numlock)
KEY_FLG_MOD3 = (0x00000020 << KEY_FLAGS_SHIFT)  # Mod3 modifier
KEY_FLG_MOD4 = (0x00000040 << KEY_FLAGS_SHIFT)  # Mod4 modifier
KEY_FLG_MOD5 = (0x00000080 << KEY_FLAGS_SHIFT)  # Mod5 (usually Alt-Gr)

# Mask and shift for key type
KEY_TYPE_MASK = 0x00000000E0000000
KEY_TYPE_SHIFT = 29
KEY_TYPE_CMD = 0x0000000020000000  # Braille command
KEY_TYPE_SYM = 0x0000000000000000  # X Keysym

# Mask and shift for key code
KEY_CODE_MASK = 0x000000001FFFFFFF
KEY_CODE_SHIFT = 0

# Mask and shift for braille command type
KEY_CMD_BLK_MASK = 0x1FFF0000
KEY_CMD_BLK_SHIFT = 16
KEY_CMD_ARG_MASK = 0x0000FFFF
KEY_CMD_ARG_SHIFT = 0

# Standard X keysyms
KEY_SYM_BACKSPACE = 0x0000FF08
KEY_SYM_TAB = 0x0000FF09
KEY_SYM_LINEFEED = 0x0000FF0D
KEY_SYM_ESCAPE = 0x0000FF1B
KEY_SYM_HOME = 0x0000FF50
KEY_SYM_LEFT = 0x0000FF51
KEY_SYM_UP = 0x0000FF52
KEY_SYM_RIGHT = 0x0000FF53
KEY_SYM_DOWN = 0x0000FF54
KEY_SYM_PAGE_UP = 0x0000FF55
KEY_SYM_PAGE_DOWN = 0x0000FF56
KEY_SYM_END = 0x0000FF57
KEY_SYM_INSERT = 0x0000FF63
KEY_SYM_FUNCTION = 0x0000FFBE
KEY_SYM_DELETE = 0x0000FFFF
KEY_SYM_UNICODE = 0x01000000

# Driver-specific key codes
DRV_KEY_PRESS = 0x8000000000000000

# Key number and group shifts/masks
DRV_KEY_NUMBER_SHIFT = 0
DRV_KEY_NUMBER_MASK = 0xFF
DRV_KEY_GROUP_SHIFT = 8
DRV_KEY_GROUP_MASK = 0xFF00
DRV_KEY_VALUE_MASK = DRV_KEY_GROUP_MASK | DRV_KEY_NUMBER_MASK

# Key number representing any key in the group
DRV_KEY_NUMBER_ANY = 0xFF

# --- Command constants ---

# do nothing 
KEY_CMD_NOOP = ((0 << KEY_CMD_BLK_SHIFT) + 0)
# go up one line 
KEY_CMD_LNUP = ((0 << KEY_CMD_BLK_SHIFT) + 1)
# go down one line 
KEY_CMD_LNDN = ((0 << KEY_CMD_BLK_SHIFT) + 2)
# go up several lines 
KEY_CMD_WINUP = ((0 << KEY_CMD_BLK_SHIFT) + 3)
# go down several lines 
KEY_CMD_WINDN = ((0 << KEY_CMD_BLK_SHIFT) + 4)
# go up to nearest line with different content 
KEY_CMD_PRDIFLN = ((0 << KEY_CMD_BLK_SHIFT) + 5)
# go down to nearest line with different content 
KEY_CMD_NXDIFLN = ((0 << KEY_CMD_BLK_SHIFT) + 6)
# go up to nearest line with different highlighting 
KEY_CMD_ATTRUP = ((0 << KEY_CMD_BLK_SHIFT) + 7)
# go down to nearest line with different highlighting 
KEY_CMD_ATTRDN = ((0 << KEY_CMD_BLK_SHIFT) + 8)
# go to top line 
KEY_CMD_TOP = ((0 << KEY_CMD_BLK_SHIFT) + 9)
# go to bottom line 
KEY_CMD_BOT = ((0 << KEY_CMD_BLK_SHIFT) + 10)
# go to beginning of top line 
KEY_CMD_TOP_LEFT = ((0 << KEY_CMD_BLK_SHIFT) + 11)
# go to beginning of bottom line 
KEY_CMD_BOT_LEFT = ((0 << KEY_CMD_BLK_SHIFT) + 12)
# go up to first line of paragraph 
KEY_CMD_PRPGRPH = ((0 << KEY_CMD_BLK_SHIFT) + 13)
# go down to first line of next paragraph 
KEY_CMD_NXPGRPH = ((0 << KEY_CMD_BLK_SHIFT) + 14)
# go up to previous command prompt 
KEY_CMD_PRPROMPT = ((0 << KEY_CMD_BLK_SHIFT) + 15)
# go down to next command prompt 
KEY_CMD_NXPROMPT = ((0 << KEY_CMD_BLK_SHIFT) + 16)
# search backward for clipboard text 
KEY_CMD_PRSEARCH = ((0 << KEY_CMD_BLK_SHIFT) + 17)
# search forward for clipboard text 
KEY_CMD_NXSEARCH = ((0 << KEY_CMD_BLK_SHIFT) + 18)
# go left one character 
KEY_CMD_CHRLT = ((0 << KEY_CMD_BLK_SHIFT) + 19)
# go right one character 
KEY_CMD_CHRRT = ((0 << KEY_CMD_BLK_SHIFT) + 20)
# go left half a braille window 
KEY_CMD_HWINLT = ((0 << KEY_CMD_BLK_SHIFT) + 21)
# go right half a braille window 
KEY_CMD_HWINRT = ((0 << KEY_CMD_BLK_SHIFT) + 22)
# go backward one braille window 
KEY_CMD_FWINLT = ((0 << KEY_CMD_BLK_SHIFT) + 23)
# go forward one braille window 
KEY_CMD_FWINRT = ((0 << KEY_CMD_BLK_SHIFT) + 24)
# go backward skipping blank braille windows 
KEY_CMD_FWINLTSKIP = ((0 << KEY_CMD_BLK_SHIFT) + 25)
# go forward skipping blank braille windows 
KEY_CMD_FWINRTSKIP = ((0 << KEY_CMD_BLK_SHIFT) + 26)
# go to beginning of line 
KEY_CMD_LNBEG = ((0 << KEY_CMD_BLK_SHIFT) + 27)
# go to end of line 
KEY_CMD_LNEND = ((0 << KEY_CMD_BLK_SHIFT) + 28)
# go to screen cursor 
KEY_CMD_HOME = ((0 << KEY_CMD_BLK_SHIFT) + 29)
# go back after cursor tracking 
KEY_CMD_BACK = ((0 << KEY_CMD_BLK_SHIFT) + 30)
# go to screen cursor or go back after cursor tracking 
KEY_CMD_RETURN = ((0 << KEY_CMD_BLK_SHIFT) + 31)
# set screen image frozen/unfrozen 
KEY_CMD_FREEZE = ((0 << KEY_CMD_BLK_SHIFT) + 32)
# set display mode attributes/text 
KEY_CMD_DISPMD = ((0 << KEY_CMD_BLK_SHIFT) + 33)
# set text style 6-dot/8-dot 
KEY_CMD_SIXDOTS = ((0 << KEY_CMD_BLK_SHIFT) + 34)
# set sliding braille window on/off 
KEY_CMD_SLIDEWIN = ((0 << KEY_CMD_BLK_SHIFT) + 35)
# set skipping of lines with identical content on/off 
KEY_CMD_SKPIDLNS = ((0 << KEY_CMD_BLK_SHIFT) + 36)
# set skipping of blank braille windows on/off 
KEY_CMD_SKPBLNKWINS = ((0 << KEY_CMD_BLK_SHIFT) + 37)
# set screen cursor visibility on/off 
KEY_CMD_CSRVIS = ((0 << KEY_CMD_BLK_SHIFT) + 38)
# set hidden screen cursor on/off 
KEY_CMD_CSRHIDE = ((0 << KEY_CMD_BLK_SHIFT) + 39)
# set track screen cursor on/off 
KEY_CMD_CSRTRK = ((0 << KEY_CMD_BLK_SHIFT) + 40)
# set screen cursor style block/underline 
KEY_CMD_CSRSIZE = ((0 << KEY_CMD_BLK_SHIFT) + 41)
# set screen cursor blinking on/off 
KEY_CMD_CSRBLINK = ((0 << KEY_CMD_BLK_SHIFT) + 42)
# set attribute underlining on/off 
KEY_CMD_ATTRVIS = ((0 << KEY_CMD_BLK_SHIFT) + 43)
# set attribute blinking on/off 
KEY_CMD_ATTRBLINK = ((0 << KEY_CMD_BLK_SHIFT) + 44)
# set capital letter blinking on/off 
KEY_CMD_CAPBLINK = ((0 << KEY_CMD_BLK_SHIFT) + 45)
# set alert tunes on/off 
KEY_CMD_TUNES = ((0 << KEY_CMD_BLK_SHIFT) + 46)
# set autorepeat on/off 
KEY_CMD_AUTOREPEAT = ((0 << KEY_CMD_BLK_SHIFT) + 47)
# set autospeak on/off 
KEY_CMD_AUTOSPEAK = ((0 << KEY_CMD_BLK_SHIFT) + 48)
# enter/leave help display 
KEY_CMD_HELP = ((0 << KEY_CMD_BLK_SHIFT) + 49)
# enter/leave status display 
KEY_CMD_INFO = ((0 << KEY_CMD_BLK_SHIFT) + 50)
# enter/leave command learn mode 
KEY_CMD_LEARN = ((0 << KEY_CMD_BLK_SHIFT) + 51)
# enter/leave preferences menu 
KEY_CMD_PREFMENU = ((0 << KEY_CMD_BLK_SHIFT) + 52)
# save preferences to disk 
KEY_CMD_PREFSAVE = ((0 << KEY_CMD_BLK_SHIFT) + 53)
# restore preferences from disk 
KEY_CMD_PREFLOAD = ((0 << KEY_CMD_BLK_SHIFT) + 54)
# go up to first item 
KEY_CMD_MENU_FIRST_ITEM = ((0 << KEY_CMD_BLK_SHIFT) + 55)
# go down to last item 
KEY_CMD_MENU_LAST_ITEM = ((0 << KEY_CMD_BLK_SHIFT) + 56)
# go up to previous item 
KEY_CMD_MENU_PREV_ITEM = ((0 << KEY_CMD_BLK_SHIFT) + 57)
# go down to next item 
KEY_CMD_MENU_NEXT_ITEM = ((0 << KEY_CMD_BLK_SHIFT) + 58)
# select previous choice 
KEY_CMD_MENU_PREV_SETTING = ((0 << KEY_CMD_BLK_SHIFT) + 59)
# select next choice 
KEY_CMD_MENU_NEXT_SETTING = ((0 << KEY_CMD_BLK_SHIFT) + 60)
# stop speaking 
KEY_CMD_MUTE = ((0 << KEY_CMD_BLK_SHIFT) + 61)
# go to current speaking position 
KEY_CMD_SPKHOME = ((0 << KEY_CMD_BLK_SHIFT) + 62)
# speak current line 
KEY_CMD_SAY_LINE = ((0 << KEY_CMD_BLK_SHIFT) + 63)
# speak from top of screen through current line 
KEY_CMD_SAY_ABOVE = ((0 << KEY_CMD_BLK_SHIFT) + 64)
# speak from current line through bottom of screen 
KEY_CMD_SAY_BELOW = ((0 << KEY_CMD_BLK_SHIFT) + 65)
# decrease speaking rate 
KEY_CMD_SAY_SLOWER = ((0 << KEY_CMD_BLK_SHIFT) + 66)
# increase speaking rate 
KEY_CMD_SAY_FASTER = ((0 << KEY_CMD_BLK_SHIFT) + 67)
# decrease speaking volume 
KEY_CMD_SAY_SOFTER = ((0 << KEY_CMD_BLK_SHIFT) + 68)
# increase speaking volume 
KEY_CMD_SAY_LOUDER = ((0 << KEY_CMD_BLK_SHIFT) + 69)
# switch to the previous virtual terminal 
KEY_CMD_SWITCHVT_PREV = ((0 << KEY_CMD_BLK_SHIFT) + 70)
# switch to the next virtual terminal 
KEY_CMD_SWITCHVT_NEXT = ((0 << KEY_CMD_BLK_SHIFT) + 71)
# bring screen cursor to current line 
KEY_CMD_CSRJMP_VERT = ((0 << KEY_CMD_BLK_SHIFT) + 72)
# insert clipboard text after screen cursor 
KEY_CMD_PASTE = ((0 << KEY_CMD_BLK_SHIFT) + 73)
# restart braille driver 
KEY_CMD_RESTARTBRL = ((0 << KEY_CMD_BLK_SHIFT) + 74)
# restart speech driver 
KEY_CMD_RESTARTSPEECH = ((0 << KEY_CMD_BLK_SHIFT) + 75)
# braille display temporarily unavailable 
KEY_CMD_OFFLINE = ((0 << KEY_CMD_BLK_SHIFT) + 76)
# cycle the Shift sticky input modifier (next, on, off) 
KEY_CMD_SHIFT = ((0 << KEY_CMD_BLK_SHIFT) + 77)
# cycle the Upper sticky input modifier (next, on, off) 
KEY_CMD_UPPER = ((0 << KEY_CMD_BLK_SHIFT) + 78)
# cycle the Control sticky input modifier (next, on, off) 
KEY_CMD_CONTROL = ((0 << KEY_CMD_BLK_SHIFT) + 79)
# cycle the Meta (Left Alt) sticky input modifier (next, on, off) 
KEY_CMD_META = ((0 << KEY_CMD_BLK_SHIFT) + 80)
# show current date and time 
KEY_CMD_TIME = ((0 << KEY_CMD_BLK_SHIFT) + 81)
# go to previous menu level 
KEY_CMD_MENU_PREV_LEVEL = ((0 << KEY_CMD_BLK_SHIFT) + 82)
# set autospeak selected line on/off 
KEY_CMD_ASPK_SEL_LINE = ((0 << KEY_CMD_BLK_SHIFT) + 83)
# set autospeak selected character on/off 
KEY_CMD_ASPK_SEL_CHAR = ((0 << KEY_CMD_BLK_SHIFT) + 84)
# set autospeak inserted characters on/off 
KEY_CMD_ASPK_INS_CHARS = ((0 << KEY_CMD_BLK_SHIFT) + 85)
# set autospeak deleted characters on/off 
KEY_CMD_ASPK_DEL_CHARS = ((0 << KEY_CMD_BLK_SHIFT) + 86)
# set autospeak replaced characters on/off 
KEY_CMD_ASPK_REP_CHARS = ((0 << KEY_CMD_BLK_SHIFT) + 87)
# set autospeak completed words on/off 
KEY_CMD_ASPK_CMP_WORDS = ((0 << KEY_CMD_BLK_SHIFT) + 88)
# speak current character 
KEY_CMD_SPEAK_CURR_CHAR = ((0 << KEY_CMD_BLK_SHIFT) + 89)
# go to and speak previous character 
KEY_CMD_SPEAK_PREV_CHAR = ((0 << KEY_CMD_BLK_SHIFT) + 90)
# go to and speak next character 
KEY_CMD_SPEAK_NEXT_CHAR = ((0 << KEY_CMD_BLK_SHIFT) + 91)
# speak current word 
KEY_CMD_SPEAK_CURR_WORD = ((0 << KEY_CMD_BLK_SHIFT) + 92)
# go to and speak previous word 
KEY_CMD_SPEAK_PREV_WORD = ((0 << KEY_CMD_BLK_SHIFT) + 93)
# go to and speak next word 
KEY_CMD_SPEAK_NEXT_WORD = ((0 << KEY_CMD_BLK_SHIFT) + 94)
# speak current line 
KEY_CMD_SPEAK_CURR_LINE = ((0 << KEY_CMD_BLK_SHIFT) + 95)
# go to and speak previous line 
KEY_CMD_SPEAK_PREV_LINE = ((0 << KEY_CMD_BLK_SHIFT) + 96)
# go to and speak next line 
KEY_CMD_SPEAK_NEXT_LINE = ((0 << KEY_CMD_BLK_SHIFT) + 97)
# go to and speak first non-blank character on line 
KEY_CMD_SPEAK_FRST_CHAR = ((0 << KEY_CMD_BLK_SHIFT) + 98)
# go to and speak last non-blank character on line 
KEY_CMD_SPEAK_LAST_CHAR = ((0 << KEY_CMD_BLK_SHIFT) + 99)
# go to and speak first non-blank line on screen 
KEY_CMD_SPEAK_FRST_LINE = ((0 << KEY_CMD_BLK_SHIFT) + 100)
# go to and speak last non-blank line on screen 
KEY_CMD_SPEAK_LAST_LINE = ((0 << KEY_CMD_BLK_SHIFT) + 101)
# describe current character 
KEY_CMD_DESC_CURR_CHAR = ((0 << KEY_CMD_BLK_SHIFT) + 102)
# spell current word 
KEY_CMD_SPELL_CURR_WORD = ((0 << KEY_CMD_BLK_SHIFT) + 103)
# bring screen cursor to speech cursor 
KEY_CMD_ROUTE_CURR_LOCN = ((0 << KEY_CMD_BLK_SHIFT) + 104)
# speak speech cursor location 
KEY_CMD_SPEAK_CURR_LOCN = ((0 << KEY_CMD_BLK_SHIFT) + 105)
# set speech cursor visibility on/off 
KEY_CMD_SHOW_CURR_LOCN = ((0 << KEY_CMD_BLK_SHIFT) + 106)
# save clipboard to disk 
KEY_CMD_CLIP_SAVE = ((0 << KEY_CMD_BLK_SHIFT) + 107)
# restore clipboard from disk 
KEY_CMD_CLIP_RESTORE = ((0 << KEY_CMD_BLK_SHIFT) + 108)
# set braille typing mode dots/text 
KEY_CMD_BRLUCDOTS = ((0 << KEY_CMD_BLK_SHIFT) + 109)
# set braille keyboard enabled/disabled 
KEY_CMD_BRLKBD = ((0 << KEY_CMD_BLK_SHIFT) + 110)
# clear all sticky input modifiers 
KEY_CMD_UNSTICK = ((0 << KEY_CMD_BLK_SHIFT) + 111)
# cycle the AltGr (Right Alt) sticky input modifier (next, on, off) 
KEY_CMD_ALTGR = ((0 << KEY_CMD_BLK_SHIFT) + 112)
# cycle the GUI (Windows) sticky input modifier (next, on, off) 
KEY_CMD_GUI = ((0 << KEY_CMD_BLK_SHIFT) + 113)
# stop the braille driver 
KEY_CMD_BRL_STOP = ((0 << KEY_CMD_BLK_SHIFT) + 114)
# start the braille driver 
KEY_CMD_BRL_START = ((0 << KEY_CMD_BLK_SHIFT) + 115)
# stop the speech driver 
KEY_CMD_SPK_STOP = ((0 << KEY_CMD_BLK_SHIFT) + 116)
# start the speech driver 
KEY_CMD_SPK_START = ((0 << KEY_CMD_BLK_SHIFT) + 117)
# stop the screen driver 
KEY_CMD_SCR_STOP = ((0 << KEY_CMD_BLK_SHIFT) + 118)
# start the screen driver 
KEY_CMD_SCR_START = ((0 << KEY_CMD_BLK_SHIFT) + 119)
# bind to the previous virtual terminal 
KEY_CMD_SELECTVT_PREV = ((0 << KEY_CMD_BLK_SHIFT) + 120)
# bind to the next virtual terminal 
KEY_CMD_SELECTVT_NEXT = ((0 << KEY_CMD_BLK_SHIFT) + 121)
# go backward to nearest non-blank braille window 
KEY_CMD_PRNBWIN = ((0 << KEY_CMD_BLK_SHIFT) + 122)
# go forward to nearest non-blank braille window 
KEY_CMD_NXNBWIN = ((0 << KEY_CMD_BLK_SHIFT) + 123)
# set touch navigation on/off 
KEY_CMD_TOUCH_NAV = ((0 << KEY_CMD_BLK_SHIFT) + 124)
# speak indent of current line 
KEY_CMD_SPEAK_INDENT = ((0 << KEY_CMD_BLK_SHIFT) + 125)
# set autospeak indent of current line on/off 
KEY_CMD_ASPK_INDENT = ((0 << KEY_CMD_BLK_SHIFT) + 126)
# refresh braille display 
KEY_CMD_REFRESH = ((0 << KEY_CMD_BLK_SHIFT) + 127)
# show various device status indicators 
KEY_CMD_INDICATORS = ((0 << KEY_CMD_BLK_SHIFT) + 128)
# clear the text selection 
KEY_CMD_TXTSEL_CLEAR = ((0 << KEY_CMD_BLK_SHIFT) + 129)
# select all of the text 
KEY_CMD_TXTSEL_ALL = ((0 << KEY_CMD_BLK_SHIFT) + 130)
# copy selected text to host clipboard 
KEY_CMD_HOST_COPY = ((0 << KEY_CMD_BLK_SHIFT) + 131)
# cut selected text to host clipboard 
KEY_CMD_HOST_CUT = ((0 << KEY_CMD_BLK_SHIFT) + 132)
# insert host clipboard text after screen cursor 
KEY_CMD_HOST_PASTE = ((0 << KEY_CMD_BLK_SHIFT) + 133)
# show the window title 
KEY_CMD_GUI_TITLE = ((0 << KEY_CMD_BLK_SHIFT) + 134)
# open the braille actions window 
KEY_CMD_GUI_BRL_ACTIONS = ((0 << KEY_CMD_BLK_SHIFT) + 135)
# go to the home screen 
KEY_CMD_GUI_HOME = ((0 << KEY_CMD_BLK_SHIFT) + 136)
# go back to the previous screen 
KEY_CMD_GUI_BACK = ((0 << KEY_CMD_BLK_SHIFT) + 137)
# open the device settings window 
KEY_CMD_GUI_DEV_SETTINGS = ((0 << KEY_CMD_BLK_SHIFT) + 138)
# open the device options window 
KEY_CMD_GUI_DEV_OPTIONS = ((0 << KEY_CMD_BLK_SHIFT) + 139)
# open the application list window 
KEY_CMD_GUI_APP_LIST = ((0 << KEY_CMD_BLK_SHIFT) + 140)
# open the application-specific menu 
KEY_CMD_GUI_APP_MENU = ((0 << KEY_CMD_BLK_SHIFT) + 141)
# open the application alerts window 
KEY_CMD_GUI_APP_ALERTS = ((0 << KEY_CMD_BLK_SHIFT) + 142)
# return to the active screen area 
KEY_CMD_GUI_AREA_ACTV = ((0 << KEY_CMD_BLK_SHIFT) + 143)
# switch to the previous screen area 
KEY_CMD_GUI_AREA_PREV = ((0 << KEY_CMD_BLK_SHIFT) + 144)
# switch to the next screen area 
KEY_CMD_GUI_AREA_NEXT = ((0 << KEY_CMD_BLK_SHIFT) + 145)
# move to the first item in the screen area 
KEY_CMD_GUI_ITEM_FRST = ((0 << KEY_CMD_BLK_SHIFT) + 146)
# move to the previous item in the screen area 
KEY_CMD_GUI_ITEM_PREV = ((0 << KEY_CMD_BLK_SHIFT) + 147)
# move to the next item in the screen area 
KEY_CMD_GUI_ITEM_NEXT = ((0 << KEY_CMD_BLK_SHIFT) + 148)
# move to the last item in the screen area 
KEY_CMD_GUI_ITEM_LAST = ((0 << KEY_CMD_BLK_SHIFT) + 149)
# decrease speaking pitch 
KEY_CMD_SAY_LOWER = ((0 << KEY_CMD_BLK_SHIFT) + 150)
# increase speaking pitch 
KEY_CMD_SAY_HIGHER = ((0 << KEY_CMD_BLK_SHIFT) + 151)
# speak from top of screen through bottom of screen 
KEY_CMD_SAY_ALL = ((0 << KEY_CMD_BLK_SHIFT) + 152)
# set contracted/computer braille 
KEY_CMD_CONTRACTED = ((0 << KEY_CMD_BLK_SHIFT) + 153)
# set six/eight dot computer braille 
KEY_CMD_COMPBRL6 = ((0 << KEY_CMD_BLK_SHIFT) + 154)
# reset preferences to defaults 
KEY_CMD_PREFRESET = ((0 << KEY_CMD_BLK_SHIFT) + 155)
# set autospeak empty line on/off 
KEY_CMD_ASPK_EMP_LINE = ((0 << KEY_CMD_BLK_SHIFT) + 156)
# cycle speech punctuation level 
KEY_CMD_SPK_PUNCT_LEVEL = ((0 << KEY_CMD_BLK_SHIFT) + 157)

# Special command definitions using different base values:
KEY_CMD_ROUTE = (1 << KEY_CMD_BLK_SHIFT)
KEY_CMD_CLIP_NEW = (2 << KEY_CMD_BLK_SHIFT)
KEY_CMD_CUTBEGIN = (2 << KEY_CMD_BLK_SHIFT)
KEY_CMD_CLIP_ADD = (3 << KEY_CMD_BLK_SHIFT)
KEY_CMD_CUTAPPEND = (3 << KEY_CMD_BLK_SHIFT)
KEY_CMD_COPY_RECT = (4 << KEY_CMD_BLK_SHIFT)
KEY_CMD_CUTRECT = (4 << KEY_CMD_BLK_SHIFT)
KEY_CMD_COPY_LINE = (5 << KEY_CMD_BLK_SHIFT)
KEY_CMD_CUTLINE = (5 << KEY_CMD_BLK_SHIFT)
KEY_CMD_SWITCHVT = (6 << KEY_CMD_BLK_SHIFT)
KEY_CMD_PRINDENT = (7 << KEY_CMD_BLK_SHIFT)
KEY_CMD_NXINDENT = (8 << KEY_CMD_BLK_SHIFT)
KEY_CMD_DESCCHAR = (9 << KEY_CMD_BLK_SHIFT)
KEY_CMD_SETLEFT = (10 << KEY_CMD_BLK_SHIFT)
KEY_CMD_SETMARK = (11 << KEY_CMD_BLK_SHIFT)
KEY_CMD_GOTOMARK = (12 << KEY_CMD_BLK_SHIFT)
KEY_CMD_GOTOLINE = (13 << KEY_CMD_BLK_SHIFT)
KEY_CMD_PRDIFCHAR = (14 << KEY_CMD_BLK_SHIFT)
KEY_CMD_NXDIFCHAR = (15 << KEY_CMD_BLK_SHIFT)
KEY_CMD_CLIP_COPY = (16 << KEY_CMD_BLK_SHIFT)
# Deprecated, use KEY_CMD_CLIP_COPY instead of:
KEY_CMD_COPYCHARS = (16 << KEY_CMD_BLK_SHIFT)
KEY_CMD_CLIP_APPEND = (17 << KEY_CMD_BLK_SHIFT)
# Deprecated, use KEY_CMD_CLIP_APPEND instead of:
KEY_CMD_APNDCHARS = (17 << KEY_CMD_BLK_SHIFT)
KEY_CMD_PASTE_HISTORY = (18 << KEY_CMD_BLK_SHIFT)
KEY_CMD_SET_TEXT_TABLE = (19 << KEY_CMD_BLK_SHIFT)
KEY_CMD_SET_ATTRIBUTES_TABLE = (20 << KEY_CMD_BLK_SHIFT)
KEY_CMD_SET_CONTRACTION_TABLE = (21 << KEY_CMD_BLK_SHIFT)
KEY_CMD_SET_KEYBOARD_TABLE = (22 << KEY_CMD_BLK_SHIFT)
KEY_CMD_SET_LANGUAGE_PROFILE = (23 << KEY_CMD_BLK_SHIFT)
KEY_CMD_ROUTE_LINE = (24 << KEY_CMD_BLK_SHIFT)
KEY_CMD_REFRESH_LINE = (25 << KEY_CMD_BLK_SHIFT)
KEY_CMD_TXTSEL_START = (26 << KEY_CMD_BLK_SHIFT)
KEY_CMD_TXTSEL_SET = (27 << KEY_CMD_BLK_SHIFT)
KEY_CMD_ROUTE_SPEECH = (28 << KEY_CMD_BLK_SHIFT)
KEY_CMD_SELECTVT = (30 << KEY_CMD_BLK_SHIFT)
KEY_CMD_ALERT = (31 << KEY_CMD_BLK_SHIFT)
KEY_CMD_PASSDOTS = (34 << KEY_CMD_BLK_SHIFT)
KEY_CMD_PASSAT = (35 << KEY_CMD_BLK_SHIFT)
KEY_CMD_PASSXT = (36 << KEY_CMD_BLK_SHIFT)
KEY_CMD_PASSPS2 = (37 << KEY_CMD_BLK_SHIFT)
KEY_CMD_CONTEXT = (38 << KEY_CMD_BLK_SHIFT)
KEY_CMD_TOUCH_AT = (39 << KEY_CMD_BLK_SHIFT)
KEY_CMD_MACRO = (40 << KEY_CMD_BLK_SHIFT)
KEY_CMD_HOSTCMD = (41 << KEY_CMD_BLK_SHIFT)

# --- Flag constants ---
# enable feature
KEY_FLG_TOGGLE_ON = (0x0100 << KEY_FLAGS_SHIFT)
# disable feature
KEY_FLG_TOGGLE_OFF = (0x0200 << KEY_FLAGS_SHIFT)
# mask for all toggle flags 
KEY_FLG_TOGGLE_MASK = (KEY_FLG_TOGGLE_ON | KEY_FLG_TOGGLE_OFF)
# bring screen cursor into braille window after function 
KEY_FLG_MOTION_ROUTE = (0x0400 << KEY_FLAGS_SHIFT)
# scale arg=0X00-0XFF to screen height 
KEY_FLG_MOTION_SCALED = (0x0800 << KEY_FLAGS_SHIFT)
# go to beginning of line 
KEY_FLG_MOTION_TOLEFT = (0x1000 << KEY_FLAGS_SHIFT)
# shift key pressed 
KEY_FLG_SHIFT = (0x01 << KEY_FLAGS_SHIFT)
# convert to uppercase 
KEY_FLG_UPPER = (0x02 << KEY_FLAGS_SHIFT)
# control key pressed 
KEY_FLG_CONTROL = (0x04 << KEY_FLAGS_SHIFT)
# meta (left alt) key pressed 
KEY_FLG_META = (0x08 << KEY_FLAGS_SHIFT)
# altgr (right alt) key pressed 
KEY_FLG_ALTGR = (0x10 << KEY_FLAGS_SHIFT)
# gui (windows) key pressed 
KEY_FLG_GUI = (0x20 << KEY_FLAGS_SHIFT)
# prefix with escape 
KEY_FLG_ESCAPED = (0x40 << KEY_FLAGS_SHIFT)
# capslock key pressed 
KEY_FLG_CAPSLOCK = (0x80 << KEY_FLAGS_SHIFT)
# it is a release scan code 
KEY_FLG_KBD_RELEASE = (0x0100 << KEY_FLAGS_SHIFT)
# it is an emulation 0 scan code 
KEY_FLG_KBD_EMUL0 = (0x0200 << KEY_FLAGS_SHIFT)
# it is an emulation 1 scan code 
KEY_FLG_KBD_EMUL1 = (0x0400 << KEY_FLAGS_SHIFT)

# --- Braille cell dot definitions ---
# upper-left dot of standard braille cell 
DOT1 = 1
# middle-left dot of standard braille cell 
DOT2 = 2
# lower-left dot of standard braille cell 
DOT3 = 4
# upper-right dot of standard braille cell 
DOT4 = 8
# middle-right dot of standard braille cell 
DOT5 = 16
# lower-right dot of standard braille cell 
DOT6 = 32
# lower-left dot of computer braille cell 
DOT7 = 64
# lower-right dot of computer braille cell 
DOT8 = 128
# chord (space bar on braille keyboard) 
DOTC = 256

def DOTS (dot1=0, dot2=0, dot3=0, dot4=0, dot5=0, dot6=0, dot7=0, dot8=0):
    """
    Helper function to easily produce braille patterns.
    
    Returns an integer composed of the following:
      - if dot1 is truthy, include DOT1, else 0,
      - if dot2 is truthy, include DOT2, else 0,
      - ... and so on for all eight dots.
    """
    return ((DOT1 if dot1 else 0) |
            (DOT2 if dot2 else 0) |
            (DOT3 if dot3 else 0) |
            (DOT4 if dot4 else 0) |
            (DOT5 if dot5 else 0) |
            (DOT6 if dot6 else 0) |
            (DOT7 if dot7 else 0) |
            (DOT8 if dot8 else 0))

# space key 
DOT_CHORD = 256

def getArgumentWidth (keyCode):
    """
    As mentioned in the module __docstring__ key command's width in bits may vary.
    This is a function that calculates the bit width of the command argument.
    """
    # For braille commands, assume argument width is 16 bits.
    if (keyCode & KEY_TYPE_MASK) == KEY_TYPE_CMD:
        return 16
    # For X keysyms:
    elif (keyCode & KEY_TYPE_MASK) == KEY_TYPE_SYM:
        # If it's a Unicode keysym, the argument (value) is 24 bits; otherwise, 8 bits.
        if keyCode & KEY_SYM_UNICODE:
            return 24
        else:
            return 8
    return -1

def expandKeyCode (keyCode):
    """
    Translates a keyCode into its expanded components:
      - type:      the key type bits (e.g., CMD or SYM)
      - command:   the command part of the key code (with the argument bits masked out)
      - argument:  the argument part of the key code
      - flags:     the flags portion (shifted down)
    
    Returns a dictionary with these keys.
    """
    argumentWidth = getArgumentWidth(keyCode)
    if argumentWidth == -1:
        return None  
    argumentMask = (1 << argumentWidth) - 1
    type_val = keyCode & KEY_TYPE_MASK
    code = keyCode & KEY_CODE_MASK

    ekc = {
        "type": type_val,
        "command": code & ~argumentMask,
        "argument": code & argumentMask,
        "flags": (keyCode & KEY_FLAGS_MASK) >> KEY_FLAGS_SHIFT,
    }
    return ekc

KEY_TABLE = {
    (KEY_TYPE_CMD | KEY_CMD_NOOP): "NOOP",
    (KEY_TYPE_CMD | KEY_CMD_LNUP): "LNUP",
    (KEY_TYPE_CMD | KEY_CMD_LNDN): "LNDN",
    (KEY_TYPE_CMD | KEY_CMD_WINUP): "WINUP",
    (KEY_TYPE_CMD | KEY_CMD_WINDN): "WINDN",
    (KEY_TYPE_CMD | KEY_CMD_PRDIFLN): "PRDIFLN",
    (KEY_TYPE_CMD | KEY_CMD_NXDIFLN): "NXDIFLN",
    (KEY_TYPE_CMD | KEY_CMD_ATTRUP): "ATTRUP",
    (KEY_TYPE_CMD | KEY_CMD_ATTRDN): "ATTRDN",
    (KEY_TYPE_CMD | KEY_CMD_TOP): "TOP",
    (KEY_TYPE_CMD | KEY_CMD_BOT): "BOT",
    (KEY_TYPE_CMD | KEY_CMD_TOP_LEFT): "TOP_LEFT",
    (KEY_TYPE_CMD | KEY_CMD_BOT_LEFT): "BOT_LEFT",
    (KEY_TYPE_CMD | KEY_CMD_PRPGRPH): "PRPGRPH",
    (KEY_TYPE_CMD | KEY_CMD_NXPGRPH): "NXPGRPH",
    (KEY_TYPE_CMD | KEY_CMD_PRPROMPT): "PRPROMPT",
    (KEY_TYPE_CMD | KEY_CMD_NXPROMPT): "NXPROMPT",
    (KEY_TYPE_CMD | KEY_CMD_PRSEARCH): "PRSEARCH",
    (KEY_TYPE_CMD | KEY_CMD_NXSEARCH): "NXSEARCH",
    (KEY_TYPE_CMD | KEY_CMD_CHRLT): "CHRLT",
    (KEY_TYPE_CMD | KEY_CMD_CHRRT): "CHRRT",
    (KEY_TYPE_CMD | KEY_CMD_HWINLT): "HWINLT",
    (KEY_TYPE_CMD | KEY_CMD_HWINRT): "HWINRT",
    (KEY_TYPE_CMD | KEY_CMD_FWINLT): "FWINLT",
    (KEY_TYPE_CMD | KEY_CMD_FWINRT): "FWINRT",
    (KEY_TYPE_CMD | KEY_CMD_FWINLTSKIP): "FWINLTSKIP",
    (KEY_TYPE_CMD | KEY_CMD_FWINRTSKIP): "FWINRTSKIP",
    (KEY_TYPE_CMD | KEY_CMD_LNBEG): "LNBEG",
    (KEY_TYPE_CMD | KEY_CMD_LNEND): "LNEND",
    (KEY_TYPE_CMD | KEY_CMD_HOME): "HOME",
    (KEY_TYPE_CMD | KEY_CMD_BACK): "BACK",
    (KEY_TYPE_CMD | KEY_CMD_RETURN): "RETURN",
    (KEY_TYPE_CMD | KEY_CMD_FREEZE): "FREEZE",
    (KEY_TYPE_CMD | KEY_CMD_DISPMD): "DISPMD",
    (KEY_TYPE_CMD | KEY_CMD_SIXDOTS): "SIXDOTS",
    (KEY_TYPE_CMD | KEY_CMD_SLIDEWIN): "SLIDEWIN",
    (KEY_TYPE_CMD | KEY_CMD_SKPIDLNS): "SKPIDLNS",
    (KEY_TYPE_CMD | KEY_CMD_SKPBLNKWINS): "SKPBLNKWINS",
    (KEY_TYPE_CMD | KEY_CMD_CSRVIS): "CSRVIS",
    (KEY_TYPE_CMD | KEY_CMD_CSRHIDE): "CSRHIDE",
    (KEY_TYPE_CMD | KEY_CMD_CSRTRK): "CSRTRK",
    (KEY_TYPE_CMD | KEY_CMD_CSRSIZE): "CSRSIZE",
    (KEY_TYPE_CMD | KEY_CMD_CSRBLINK): "CSRBLINK",
    (KEY_TYPE_CMD | KEY_CMD_ATTRVIS): "ATTRVIS",
    (KEY_TYPE_CMD | KEY_CMD_ATTRBLINK): "ATTRBLINK",
    (KEY_TYPE_CMD | KEY_CMD_CAPBLINK): "CAPBLINK",
    (KEY_TYPE_CMD | KEY_CMD_TUNES): "TUNES",
    (KEY_TYPE_CMD | KEY_CMD_AUTOREPEAT): "AUTOREPEAT",
    (KEY_TYPE_CMD | KEY_CMD_AUTOSPEAK): "AUTOSPEAK",
    (KEY_TYPE_CMD | KEY_CMD_HELP): "HELP",
    (KEY_TYPE_CMD | KEY_CMD_INFO): "INFO",
    (KEY_TYPE_CMD | KEY_CMD_LEARN): "LEARN",
    (KEY_TYPE_CMD | KEY_CMD_PREFMENU): "PREFMENU",
    (KEY_TYPE_CMD | KEY_CMD_PREFSAVE): "PREFSAVE",
    (KEY_TYPE_CMD | KEY_CMD_PREFLOAD): "PREFLOAD",
    (KEY_TYPE_CMD | KEY_CMD_MENU_FIRST_ITEM): "MENU_FIRST_ITEM",
    (KEY_TYPE_CMD | KEY_CMD_MENU_LAST_ITEM): "MENU_LAST_ITEM",
    (KEY_TYPE_CMD | KEY_CMD_MENU_PREV_ITEM): "MENU_PREV_ITEM",
    (KEY_TYPE_CMD | KEY_CMD_MENU_NEXT_ITEM): "MENU_NEXT_ITEM",
    (KEY_TYPE_CMD | KEY_CMD_MENU_PREV_SETTING): "MENU_PREV_SETTING",
    (KEY_TYPE_CMD | KEY_CMD_MENU_NEXT_SETTING): "MENU_NEXT_SETTING",
    (KEY_TYPE_CMD | KEY_CMD_MUTE): "MUTE",
    (KEY_TYPE_CMD | KEY_CMD_SPKHOME): "SPKHOME",
    (KEY_TYPE_CMD | KEY_CMD_SAY_LINE): "SAY_LINE",
    (KEY_TYPE_CMD | KEY_CMD_SAY_ABOVE): "SAY_ABOVE",
    (KEY_TYPE_CMD | KEY_CMD_SAY_BELOW): "SAY_BELOW",
    (KEY_TYPE_CMD | KEY_CMD_SAY_SLOWER): "SAY_SLOWER",
    (KEY_TYPE_CMD | KEY_CMD_SAY_FASTER): "SAY_FASTER",
    (KEY_TYPE_CMD | KEY_CMD_SAY_SOFTER): "SAY_SOFTER",
    (KEY_TYPE_CMD | KEY_CMD_SAY_LOUDER): "SAY_LOUDER",
    (KEY_TYPE_CMD | KEY_CMD_SWITCHVT_PREV): "SWITCHVT_PREV",
    (KEY_TYPE_CMD | KEY_CMD_SWITCHVT_NEXT): "SWITCHVT_NEXT",
    (KEY_TYPE_CMD | KEY_CMD_CSRJMP_VERT): "CSRJMP_VERT",
    (KEY_TYPE_CMD | KEY_CMD_PASTE): "PASTE",
    (KEY_TYPE_CMD | KEY_CMD_RESTARTBRL): "RESTARTBRL",
    (KEY_TYPE_CMD | KEY_CMD_RESTARTSPEECH): "RESTARTSPEECH",
    (KEY_TYPE_CMD | KEY_CMD_OFFLINE): "OFFLINE",
    (KEY_TYPE_CMD | KEY_CMD_SHIFT): "SHIFT",
    (KEY_TYPE_CMD | KEY_CMD_UPPER): "UPPER",
    (KEY_TYPE_CMD | KEY_CMD_CONTROL): "CONTROL",
    (KEY_TYPE_CMD | KEY_CMD_META): "META",
    (KEY_TYPE_CMD | KEY_CMD_TIME): "TIME",
    (KEY_TYPE_CMD | KEY_CMD_MENU_PREV_LEVEL): "MENU_PREV_LEVEL",
    (KEY_TYPE_CMD | KEY_CMD_ASPK_SEL_LINE): "ASPK_SEL_LINE",
    (KEY_TYPE_CMD | KEY_CMD_ASPK_SEL_CHAR): "ASPK_SEL_CHAR",
    (KEY_TYPE_CMD | KEY_CMD_ASPK_INS_CHARS): "ASPK_INS_CHARS",
    (KEY_TYPE_CMD | KEY_CMD_ASPK_DEL_CHARS): "ASPK_DEL_CHARS",
    (KEY_TYPE_CMD | KEY_CMD_ASPK_REP_CHARS): "ASPK_REP_CHARS",
    (KEY_TYPE_CMD | KEY_CMD_ASPK_CMP_WORDS): "ASPK_CMP_WORDS",
    (KEY_TYPE_CMD | KEY_CMD_SPEAK_CURR_CHAR): "SPEAK_CURR_CHAR",
    (KEY_TYPE_CMD | KEY_CMD_SPEAK_PREV_CHAR): "SPEAK_PREV_CHAR",
    (KEY_TYPE_CMD | KEY_CMD_SPEAK_NEXT_CHAR): "SPEAK_NEXT_CHAR",
    (KEY_TYPE_CMD | KEY_CMD_SPEAK_CURR_WORD): "SPEAK_CURR_WORD",
    (KEY_TYPE_CMD | KEY_CMD_SPEAK_PREV_WORD): "SPEAK_PREV_WORD",
    (KEY_TYPE_CMD | KEY_CMD_SPEAK_NEXT_WORD): "SPEAK_NEXT_WORD",
    (KEY_TYPE_CMD | KEY_CMD_SPEAK_CURR_LINE): "SPEAK_CURR_LINE",
    (KEY_TYPE_CMD | KEY_CMD_SPEAK_PREV_LINE): "SPEAK_PREV_LINE",
    (KEY_TYPE_CMD | KEY_CMD_SPEAK_NEXT_LINE): "SPEAK_NEXT_LINE",
    (KEY_TYPE_CMD | KEY_CMD_SPEAK_FRST_CHAR): "SPEAK_FRST_CHAR",
    (KEY_TYPE_CMD | KEY_CMD_SPEAK_LAST_CHAR): "SPEAK_LAST_CHAR",
    (KEY_TYPE_CMD | KEY_CMD_SPEAK_FRST_LINE): "SPEAK_FRST_LINE",
    (KEY_TYPE_CMD | KEY_CMD_SPEAK_LAST_LINE): "SPEAK_LAST_LINE",
    (KEY_TYPE_CMD | KEY_CMD_DESC_CURR_CHAR): "DESC_CURR_CHAR",
    (KEY_TYPE_CMD | KEY_CMD_SPELL_CURR_WORD): "SPELL_CURR_WORD",
    (KEY_TYPE_CMD | KEY_CMD_ROUTE_CURR_LOCN): "ROUTE_CURR_LOCN",
    (KEY_TYPE_CMD | KEY_CMD_SPEAK_CURR_LOCN): "SPEAK_CURR_LOCN",
    (KEY_TYPE_CMD | KEY_CMD_SHOW_CURR_LOCN): "SHOW_CURR_LOCN",
    (KEY_TYPE_CMD | KEY_CMD_CLIP_SAVE): "CLIP_SAVE",
    (KEY_TYPE_CMD | KEY_CMD_CLIP_RESTORE): "CLIP_RESTORE",
    (KEY_TYPE_CMD | KEY_CMD_BRLUCDOTS): "BRLUCDOTS",
    (KEY_TYPE_CMD | KEY_CMD_BRLKBD): "BRLKBD",
    (KEY_TYPE_CMD | KEY_CMD_UNSTICK): "UNSTICK",
    (KEY_TYPE_CMD | KEY_CMD_ALTGR): "ALTGR",
    (KEY_TYPE_CMD | KEY_CMD_GUI): "GUI",
    (KEY_TYPE_CMD | KEY_CMD_BRL_STOP): "BRL_STOP",
    (KEY_TYPE_CMD | KEY_CMD_BRL_START): "BRL_START",
    (KEY_TYPE_CMD | KEY_CMD_SPK_STOP): "SPK_STOP",
    (KEY_TYPE_CMD | KEY_CMD_SPK_START): "SPK_START",
    (KEY_TYPE_CMD | KEY_CMD_SCR_STOP): "SCR_STOP",
    (KEY_TYPE_CMD | KEY_CMD_SCR_START): "SCR_START",
    (KEY_TYPE_CMD | KEY_CMD_SELECTVT_PREV): "SELECTVT_PREV",
    (KEY_TYPE_CMD | KEY_CMD_SELECTVT_NEXT): "SELECTVT_NEXT",
    (KEY_TYPE_CMD | KEY_CMD_PRNBWIN): "PRNBWIN",
    (KEY_TYPE_CMD | KEY_CMD_NXNBWIN): "NXNBWIN",
    (KEY_TYPE_CMD | KEY_CMD_TOUCH_NAV): "TOUCH_NAV",
    (KEY_TYPE_CMD | KEY_CMD_SPEAK_INDENT): "SPEAK_INDENT",
    (KEY_TYPE_CMD | KEY_CMD_ASPK_INDENT): "ASPK_INDENT",
    (KEY_TYPE_CMD | KEY_CMD_REFRESH): "REFRESH",
    (KEY_TYPE_CMD | KEY_CMD_INDICATORS): "INDICATORS",
    (KEY_TYPE_CMD | KEY_CMD_TXTSEL_CLEAR): "TXTSEL_CLEAR",
    (KEY_TYPE_CMD | KEY_CMD_TXTSEL_ALL): "TXTSEL_ALL",
    (KEY_TYPE_CMD | KEY_CMD_HOST_COPY): "HOST_COPY",
    (KEY_TYPE_CMD | KEY_CMD_HOST_CUT): "HOST_CUT",
    (KEY_TYPE_CMD | KEY_CMD_HOST_PASTE): "HOST_PASTE",
    (KEY_TYPE_CMD | KEY_CMD_GUI_TITLE): "GUI_TITLE",
    (KEY_TYPE_CMD | KEY_CMD_GUI_BRL_ACTIONS): "GUI_BRL_ACTIONS",
    (KEY_TYPE_CMD | KEY_CMD_GUI_HOME): "GUI_HOME",
    (KEY_TYPE_CMD | KEY_CMD_GUI_BACK): "GUI_BACK",
    (KEY_TYPE_CMD | KEY_CMD_GUI_DEV_SETTINGS): "GUI_DEV_SETTINGS",
    (KEY_TYPE_CMD | KEY_CMD_GUI_DEV_OPTIONS): "GUI_DEV_OPTIONS",
    (KEY_TYPE_CMD | KEY_CMD_GUI_APP_LIST): "GUI_APP_LIST",
    (KEY_TYPE_CMD | KEY_CMD_GUI_APP_MENU): "GUI_APP_MENU",
    (KEY_TYPE_CMD | KEY_CMD_GUI_APP_ALERTS): "GUI_APP_ALERTS",
    (KEY_TYPE_CMD | KEY_CMD_GUI_AREA_ACTV): "GUI_AREA_ACTV",
    (KEY_TYPE_CMD | KEY_CMD_GUI_AREA_PREV): "GUI_AREA_PREV",
    (KEY_TYPE_CMD | KEY_CMD_GUI_AREA_NEXT): "GUI_AREA_NEXT",
    (KEY_TYPE_CMD | KEY_CMD_GUI_ITEM_FRST): "GUI_ITEM_FRST",
    (KEY_TYPE_CMD | KEY_CMD_GUI_ITEM_PREV): "GUI_ITEM_PREV",
    (KEY_TYPE_CMD | KEY_CMD_GUI_ITEM_NEXT): "GUI_ITEM_NEXT",
    (KEY_TYPE_CMD | KEY_CMD_GUI_ITEM_LAST): "GUI_ITEM_LAST",
    (KEY_TYPE_CMD | KEY_CMD_SAY_LOWER): "SAY_LOWER",
    (KEY_TYPE_CMD | KEY_CMD_SAY_HIGHER): "SAY_HIGHER",
    (KEY_TYPE_CMD | KEY_CMD_SAY_ALL): "SAY_ALL",
    (KEY_TYPE_CMD | KEY_CMD_CONTRACTED): "CONTRACTED",
    (KEY_TYPE_CMD | KEY_CMD_COMPBRL6): "COMPBRL6",
    (KEY_TYPE_CMD | KEY_CMD_PREFRESET): "PREFRESET",
    (KEY_TYPE_CMD | KEY_CMD_ASPK_EMP_LINE): "ASPK_EMP_LINE",
    (KEY_TYPE_CMD | KEY_CMD_SPK_PUNCT_LEVEL): "SPK_PUNCT_LEVEL",
    (KEY_TYPE_CMD | KEY_CMD_ROUTE): "ROUTE",
    (KEY_TYPE_CMD | KEY_CMD_CLIP_NEW): "CLIP_NEW",
    (KEY_TYPE_CMD | KEY_CMD_CUTBEGIN): "CUTBEGIN",
    (KEY_TYPE_CMD | KEY_CMD_CLIP_ADD): "CLIP_ADD",
    (KEY_TYPE_CMD | KEY_CMD_CUTAPPEND): "CUTAPPEND",
    (KEY_TYPE_CMD | KEY_CMD_COPY_RECT): "COPY_RECT",
    (KEY_TYPE_CMD | KEY_CMD_CUTRECT): "CUTRECT",
    (KEY_TYPE_CMD | KEY_CMD_COPY_LINE): "COPY_LINE",
    (KEY_TYPE_CMD | KEY_CMD_CUTLINE): "CUTLINE",
    (KEY_TYPE_CMD | KEY_CMD_SWITCHVT): "SWITCHVT",
    (KEY_TYPE_CMD | KEY_CMD_PRINDENT): "PRINDENT",
    (KEY_TYPE_CMD | KEY_CMD_NXINDENT): "NXINDENT",
    (KEY_TYPE_CMD | KEY_CMD_DESCCHAR): "DESCCHAR",
    (KEY_TYPE_CMD | KEY_CMD_SETLEFT): "SETLEFT",
    (KEY_TYPE_CMD | KEY_CMD_SETMARK): "SETMARK",
    (KEY_TYPE_CMD | KEY_CMD_GOTOMARK): "GOTOMARK",
    (KEY_TYPE_CMD | KEY_CMD_GOTOLINE): "GOTOLINE",
    (KEY_TYPE_CMD | KEY_CMD_PRDIFCHAR): "PRDIFCHAR",
    (KEY_TYPE_CMD | KEY_CMD_NXDIFCHAR): "NXDIFCHAR",
    (KEY_TYPE_CMD | KEY_CMD_CLIP_COPY): "CLIP_COPY",
    # The KEY_CMD_COPYCHARS command is deprecated and same as KEY_CMD_CLIP_COPY
    #(KEY_TYPE_CMD | KEY_CMD_COPYCHARS): "COPYCHARS",
    (KEY_TYPE_CMD | KEY_CMD_CLIP_APPEND): "CLIP_APPEND",
    # The KEY_CMD_APNCHARS is deprecated and same as KEY_CMD_CLIP_APPEND
    #(KEY_TYPE_CMD | KEY_CMD_APNDCHARS): "APNDCHARS",
    (KEY_TYPE_CMD | KEY_CMD_PASTE_HISTORY): "PASTE_HISTORY",
    (KEY_TYPE_CMD | KEY_CMD_SET_TEXT_TABLE): "SET_TEXT_TABLE",
    (KEY_TYPE_CMD | KEY_CMD_SET_ATTRIBUTES_TABLE): "SET_ATTRIBUTES_TABLE",
    (KEY_TYPE_CMD | KEY_CMD_SET_CONTRACTION_TABLE): "SET_CONTRACTION_TABLE",
    (KEY_TYPE_CMD | KEY_CMD_SET_KEYBOARD_TABLE): "SET_KEYBOARD_TABLE",
    (KEY_TYPE_CMD | KEY_CMD_SET_LANGUAGE_PROFILE): "SET_LANGUAGE_PROFILE",
    (KEY_TYPE_CMD | KEY_CMD_ROUTE_LINE): "ROUTE_LINE",
    (KEY_TYPE_CMD | KEY_CMD_REFRESH_LINE): "REFRESH_LINE",
    (KEY_TYPE_CMD | KEY_CMD_TXTSEL_START): "TXTSEL_START",
    (KEY_TYPE_CMD | KEY_CMD_TXTSEL_SET): "TXTSEL_SET",
    (KEY_TYPE_CMD | KEY_CMD_ROUTE_SPEECH): "ROUTE_SPEECH",
    (KEY_TYPE_CMD | KEY_CMD_SELECTVT): "SELECTVT",
    (KEY_TYPE_CMD | KEY_CMD_ALERT): "ALERT",
    (KEY_TYPE_CMD | KEY_CMD_PASSDOTS): "PASSDOTS",
    (KEY_TYPE_CMD | KEY_CMD_PASSAT): "PASSAT",
    (KEY_TYPE_CMD | KEY_CMD_PASSXT): "PASSXT",
    (KEY_TYPE_CMD | KEY_CMD_PASSPS2): "PASSPS2",
    (KEY_TYPE_CMD | KEY_CMD_CONTEXT): "CONTEXT",
    (KEY_TYPE_CMD | KEY_CMD_TOUCH_AT): "TOUCH_AT",
    (KEY_TYPE_CMD | KEY_CMD_MACRO): "MACRO",
    (KEY_TYPE_CMD | KEY_CMD_HOSTCMD): "HOSTCMD",
    (KEY_TYPE_SYM | KEY_SYM_LINEFEED): "LINEFEED",
    (KEY_TYPE_SYM | KEY_SYM_TAB): "TAB",
    (KEY_TYPE_SYM | KEY_SYM_BACKSPACE): "BACKSPACE",
    (KEY_TYPE_SYM | KEY_SYM_ESCAPE): "ESCAPE",
    (KEY_TYPE_SYM | KEY_SYM_LEFT): "LEFT",
    (KEY_TYPE_SYM | KEY_SYM_RIGHT): "RIGHT",
    (KEY_TYPE_SYM | KEY_SYM_UP): "UP",
    (KEY_TYPE_SYM | KEY_SYM_DOWN): "DOWN",
    (KEY_TYPE_SYM | KEY_SYM_PAGE_UP): "PAGE_UP",
    (KEY_TYPE_SYM | KEY_SYM_PAGE_DOWN): "PAGE_DOWN",
    (KEY_TYPE_SYM | KEY_SYM_HOME): "HOME",
    (KEY_TYPE_SYM | KEY_SYM_END): "END",
    (KEY_TYPE_SYM | KEY_SYM_INSERT): "INSERT",
    (KEY_TYPE_SYM | KEY_SYM_DELETE): "DELETE",
    KEY_SYM_FUNCTION + 0: "F1",
    KEY_SYM_FUNCTION + 1: "F2",
    KEY_SYM_FUNCTION + 2: "F3",
    KEY_SYM_FUNCTION + 3: "F4",
    KEY_SYM_FUNCTION + 4: "F5",
    KEY_SYM_FUNCTION + 5: "F6",
    KEY_SYM_FUNCTION + 6: "F7",
    KEY_SYM_FUNCTION + 7: "F8",
    KEY_SYM_FUNCTION + 8: "F9",
    KEY_SYM_FUNCTION + 9: "F10",
    KEY_SYM_FUNCTION + 10: "F11",
    KEY_SYM_FUNCTION + 11: "F12",
    KEY_SYM_FUNCTION + 12: "F13",
    KEY_SYM_FUNCTION + 13: "F14",
    KEY_SYM_FUNCTION + 14: "F15",
    KEY_SYM_FUNCTION + 15: "F16",
    KEY_SYM_FUNCTION + 16: "F17",
    KEY_SYM_FUNCTION + 17: "F18",
    KEY_SYM_FUNCTION + 18: "F19",
    KEY_SYM_FUNCTION + 19: "F20",
    KEY_SYM_FUNCTION + 20: "F21",
    KEY_SYM_FUNCTION + 21: "F22",
    KEY_SYM_FUNCTION + 22: "F23",
    KEY_SYM_FUNCTION + 23: "F24",
    KEY_SYM_FUNCTION + 24: "F25",
    KEY_SYM_FUNCTION + 25: "F26",
    KEY_SYM_FUNCTION + 26: "F27",
    KEY_SYM_FUNCTION + 27: "F28",
    KEY_SYM_FUNCTION + 28: "F29",
    KEY_SYM_FUNCTION + 29: "F30",
    KEY_SYM_FUNCTION + 30: "F31",
    KEY_SYM_FUNCTION + 31: "F32",
    KEY_SYM_FUNCTION + 32: "F33",
    KEY_SYM_FUNCTION + 33: "F34",
    KEY_SYM_FUNCTION + 34: "F35",
    }


def describeKeyCode (keyCode):
    """
    Produces a description of the key code. The returned dictionary (dkc) includes:
      - command: the string name found in the key table
      - argument: any residual argument value
      - values: the expanded key code dictionary (from expand_key_code)
      - type: one of "SYM", "CMD", or "UNKNOWN"
      - flag: a list of flag names that are set.
    
    Raises a ValueError if the key code cannot be parsed.
    Works but needs a little optimization and refinements.
    """
    ekc = expandKeyCode(keyCode)
    if ekc is None:
        raise ValueError("Invalid parameter: unable to determine argument width.")
    # Compute a version of the key code with and without the argument.
    argument = ekc["argument"]
    codeWithoutArgument = ekc["type"] | ekc["command"]
    codeWithArgument = codeWithoutArgument | argument
    entry = KEY_TABLE.get(codeWithArgument, None)
    if entry is not None:
        argument = 0
    else:
        entry = KEY_TABLE.get(codeWithoutArgument, None)
    if entry is None:
        if ekc["type"]==KEY_TYPE_SYM and keyCode & KEY_SYM_UNICODE != 0:
            entry = "UNICODE"
            argument = keyCode & (KEY_SYM_UNICODE-1)
        else:
            entry = "Unknown"
            argument = 0
    # Build the described key code dictionary.
    dkc = {}
    dkc["keyCode"] = keyCode
    dkc["command"]  = entry
    dkc["argument"] = argument
    dkc["values"]   = ekc
    if ekc["type"] == KEY_TYPE_SYM:
        dkc["type"] = "SYM"
    elif ekc["type"] == KEY_TYPE_CMD:
        dkc["type"] = "CMD"
    else:
        dkc["type"] = "UNKNOWN"
    # Process flags.
    flag_list = []
    def check_flag(flag_const, name_str):
        if keyCode & flag_const:
            flag_list.append(name_str)

    # Standard modifier flags.
    check_flag(KEY_FLG_SHIFT, "SHIFT")
    check_flag(KEY_FLG_UPPER, "UPPER")
    check_flag(KEY_FLG_CONTROL, "CONTROL")
    check_flag(KEY_FLG_META, "META")
    check_flag(KEY_FLG_ALTGR, "ALTGR")
    check_flag(KEY_FLG_GUI, "GUI")
    # Additional flags for CMD key type.
    if ekc["type"] == KEY_TYPE_CMD:
        blk = ekc["command"] & KEY_CMD_BLK_MASK
        if blk == KEY_CMD_PASSDOTS:
            pass
        elif blk in (KEY_CMD_PASSXT, KEY_CMD_PASSAT, KEY_CMD_PASSPS2):
            check_flag(KEY_FLG_KBD_RELEASE, "KBD_RELEASE")
            check_flag(KEY_FLG_KBD_EMUL0, "KBD_EMUL0")
            check_flag(KEY_FLG_KBD_EMUL1, "KBD_EMUL1")
        else:
            check_flag(KEY_FLG_TOGGLE_ON, "TOGGLE_ON")
            check_flag(KEY_FLG_TOGGLE_OFF, "TOGGLE_OFF")
            check_flag(KEY_FLG_MOTION_ROUTE, "MOTION_ROUTE")
            check_flag(KEY_FLG_MOTION_SCALED, "MOTION_SCALED")
            check_flag(KEY_FLG_MOTION_TOLEFT, "MOTION_TOLEFT")
    dkc["flags"] = flag_list
    return dkc
