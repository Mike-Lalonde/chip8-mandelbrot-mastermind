import asyncio
import random
import sys
import pygame

NREG = 16
NMEM = 4096
USERMEM = 512
SCREEN_X = 64
SCREEN_Y = 32
STACK_SIZE = 16


def XCOORD(xc):
    return xc % SCREEN_X


def YCOORD(yc):
    return yc % SCREEN_Y


fontset = [
    0xF0, 0x90, 0x90, 0x90, 0xF0,
    0x20, 0x60, 0x20, 0x20, 0x70,
    0xF0, 0x10, 0xF0, 0x80, 0xF0,
    0xF0, 0x10, 0xF0, 0x10, 0xF0,
    0x90, 0x90, 0xF0, 0x10, 0x10,
    0xF0, 0x80, 0xF0, 0x10, 0xF0,
    0xF0, 0x80, 0xF0, 0x90, 0xF0,
    0xF0, 0x10, 0x20, 0x40, 0x40,
    0xF0, 0x90, 0xF0, 0x90, 0xF0,
    0xF0, 0x90, 0xF0, 0x10, 0xF0,
    0xF0, 0x90, 0xF0, 0x90, 0x90,
    0xE0, 0x90, 0xE0, 0x90, 0xE0,
    0xF0, 0x80, 0x80, 0x80, 0xF0,
    0xE0, 0x90, 0x90, 0x90, 0xE0,
    0xF0, 0x80, 0xF0, 0x80, 0xF0,
    0xF0, 0x80, 0xF0, 0x80, 0x80]


async def main(argv):
    chip8 = Chip8()
    chip8.init()
    chip8.load_game(argv)
    try:
        while True:
            await chip8.emulate_cycle()
            if chip8.DrawFlag:
                drawGraphics(chip8.gfx)
                chip8.DrawFlag = False
            setKeys(chip8.key)
    except Exception as e:
        print(e)
        print("Error")
        print("exiting...")
    return 0


async def drawGraphics(gfx):
    print("\x1b[2J\x1b[H")
    for y in range(SCREEN_Y):
        for x in range(SCREEN_X):
            if gfx[y * SCREEN_X + x] == 1:
                sys.stdout.write(chr(0x2588))
            else:
                sys.stdout.write(" ")
        sys.stdout.write("\n")
    sys.stdout.flush()
    await asyncio.sleep(0.05)


def clearScreen():
    for y in range(SCREEN_Y):
        sys.stdout.write("\n")
    sys.stdout.flush()


def setupGraphics():
    sys.stdout.write("\x1b[2J\x1b[H")
    sys.stdout.flush()


def setKeys(keys):
    get = "e"
    for i in range(16):
        keys[i] = 0
    match get:
        case "1":
            keys[0x1] = 1
        case "2":
            keys[0x2] = 1
        case "3":
            keys[0x3] = 1
        case "4":
            keys[0xC] = 1
        case "q":
            keys[0x4] = 1
        case "w":
            keys[0x5] = 1
        case "e":
            keys[0x6] = 1
        case "r":
            keys[0xD] = 1
        case "a":
            keys[0x7] = 1
        case "s":
            keys[0x8] = 1
        case "d":
            keys[0x9] = 1
        case "f":
            keys[0xE] = 1
        case "z":
            keys[0xA] = 1
        case "x":
            keys[0x0] = 1
        case "c":
            keys[0xB] = 1
        case "v":
            keys[0xF] = 1
        case _:
            pass


class Chip8:
    opcode = 0
    V = [0 for x in range(NREG)]
    memory = [0 for x in range(NMEM)]
    gfx = [0 for x in range(SCREEN_X * SCREEN_Y)]
    I = 0
    pc = 0
    delay_timer = 0
    sound_timer = 0
    stack = [0 for x in range(STACK_SIZE)]
    sp = 0
    key = [0 for x in range(16)]

    DrawFlag = False

    def init(self):
        self.pc = 0x200
        self.opcode = 0
        self.I = 0
        self.sp = 0
        self.delay_timer = 0
        self.sound_timer = 0
        self.gfx = [0 for x in range(SCREEN_X * SCREEN_Y)]
        self.stack = [0 for x in range(STACK_SIZE)]
        self.key = [0 for x in range(16)]
        self.V = [0 for x in range(NREG)]
        self.memory = [0 for x in range(NMEM)]
        self.DrawFlag = True
        self.load_fontset()

    def load_fontset(self):
        for i in range(80):
            self.memory[i] = fontset[i]

    def load_game(self, filename):
        try:
            with open(filename, "rb") as f:
                game = f.read()
                for i in range(len(game)):
                    self.memory[USERMEM + i] = game[i]
        except Exception as e:
            print(e)
            print("Error")
            print("exiting...")
            sys.exit(1)

    async def emulate_cycle(self):
        self.opcode = self.memory[self.pc] << 8 | self.memory[self.pc + 1]
        match self.opcode & 0xF000:
            case 0x0000:
                match self.opcode & 0x000F:
                    case 0x0000:
                        clearScreen()
                        self.pc += 2
                    case 0x000E:
                        self.sp -= 1
                        self.pc = self.stack[self.sp]
                        self.pc += 2
                    case _:
                        print("Unknown opcode [0x0000]: 0x%X" % self.opcode)
                        self.pc += 2
            case 0x1000:
                self.pc = self.opcode & 0x0FFF
            case 0x2000:
                self.stack[self.sp] = self.pc
                self.sp += 1
                self.pc = self.opcode & 0x0FFF
            case 0x3000:
                if self.V[(self.opcode & 0x0F00) >> 8] == (self.opcode & 0x00FF):
                    self.pc += 4
                else:
                    self.pc += 2
            case 0x4000:
                if self.V[(self.opcode & 0x0F00) >> 8] != (self.opcode & 0x00FF):
                    self.pc += 4
                else:
                    self.pc += 2
            case 0x5000:
                if self.V[(self.opcode & 0x0F00) >> 8] == self.V[(self.opcode & 0x00F0) >> 4]:
                    self.pc += 4
                else:
                    self.pc += 2
            case 0x6000:
                self.V[(self.opcode & 0x0F00) >> 8] = self.opcode & 0x00FF
                self.pc += 2
            case 0x7000:
                self.V[(self.opcode & 0x0F00) >> 8] += self.opcode & 0x00FF
                self.pc += 2
            case 0x8000:
                match self.opcode & 0x000F:
                    case 0x0000:
                        self.V[(self.opcode & 0x0F00) >> 8] = self.V[(
                            self.opcode & 0x00F0) >> 4]
                        self.pc += 2
                    case 0x0001:
                        self.V[(self.opcode & 0x0F00) >> 8] |= self.V[(
                            self.opcode & 0x00F0) >> 4]
                        self.pc += 2
                    case 0x0002:
                        self.V[(self.opcode & 0x0F00) >> 8] &= self.V[(
                            self.opcode & 0x00F0) >> 4]
                        self.pc += 2
                    case 0x0003:
                        self.V[(self.opcode & 0x0F00) >> 8] ^= self.V[(
                            self.opcode & 0x00F0) >> 4]
                        self.pc += 2
                    case 0x0004:
                        if self.V[(self.opcode & 0x00F0) >> 4] > (0xFF - self.V[(self.opcode & 0x0F00) >> 8]):
                            self.V[0xF] = 1
                        else:
                            self.V[0xF] = 0
                        self.V[(self.opcode & 0x0F00) >>
                               8] += self.V[(self.opcode & 0x00F0) >> 4]
                        self.pc += 2
                    case 0x0005:
                        if self.V[(self.opcode & 0x00F0) >> 4] > self.V[(self.opcode & 0x0F00) >> 8]:
                            self.V[0xF] = 0
                        else:
                            self.V[0xF] = 1
                        self.V[(self.opcode & 0x0F00) >>
                               8] -= self.V[(self.opcode & 0x00F0) >> 4]
                        self.pc += 2
                    case 0x0006:
                        self.V[0xF] = self.V[(self.opcode & 0x0F00) >> 8] & 0
                        self.V[(self.opcode & 0x0F00) >> 8] >>= 1
                        self.pc += 2
                    case 0x0007:
                        if self.V[(self.opcode & 0x0F00) >> 8] > self.V[(self.opcode & 0x00F0) >> 4]:
                            self.V[0xF] = 0
                        else:
                            self.V[0xF] = 1
                        self.V[(self.opcode & 0x0F00) >> 8] = self.V[(
                            self.opcode & 0x00F0) >> 4] - self.V[(self.opcode & 0x0F00) >> 8]
                        self.pc += 2
                    case 0x000E:
                        self.V[0xF] = self.V[(self.opcode & 0x0F00) >> 8] >> 7
                        self.V[(self.opcode & 0x0F00) >> 8] <<= 1
                        self.pc += 2
                    case _:
                        print("Unknown opcode [0x8000]: 0x%X" % self.opcode)
                        self.pc += 2
            case 0x9000:
                if self.V[(self.opcode & 0x0F00) >> 8] != self.V[(self.opcode & 0x00F0) >> 4]:
                    self.pc += 4
                else:
                    self.pc += 2
            case 0xA000:
                self.I = self.opcode & 0x0FFF
                self.pc += 2
            case 0xB000:
                self.pc = (self.opcode & 0x0FFF) + self.V[0]
            case 0xC000:
                self.V[(self.opcode & 0x0F00) >> 8] = random.randint(
                    0, 255) & (self.opcode & 0x00FF)
                self.pc += 2
            case 0xD000:
                await drawSprite(self.opcode, self.V, self.memory, self.I, self.gfx)
                self.drawFlag = True
                self.pc += 2
            case 0xE000:
                match self.opcode & 0x00FF:
                    case 0x009E:
                        if self.key[self.V[(self.opcode & 0x0F00) >> 8]] != 0:
                            self.pc += 4
                        else:
                            self.pc += 2
                    case 0x00A1:
                        if self.key[self.V[(self.opcode & 0x0F00) >> 8]] == 0:
                            self.pc += 4
                        else:
                            self.pc += 2
                    case _:
                        print("Unknown opcode [0xE000]: 0x%X" % self.opcode)
                        self.pc += 2
            case 0xF000:
                match self.opcode & 0x00FF:
                    case 0x0007:
                        self.V[(self.opcode & 0x0F00) >> 8] = self.delay_timer
                        self.pc += 2
                    case 0x000A:
                        keyPress = False
                        for i in range(16):
                            if self.key[i] != 0:
                                self.V[(self.opcode & 0x0F00) >> 8] = i
                                keyPress = True
                        if not keyPress:
                            return
                        self.pc += 2
                    case 0x0015:
                        self.delay_timer = self.V[(self.opcode & 0x0F00) >> 8]
                        self.pc += 2
                    case 0x0018:
                        self.sound_timer = self.V[(self.opcode & 0x0F00) >> 8]
                        self.pc += 2
                    case 0x001E:
                        if self.I + self.V[(self.opcode & 0x0F00) >> 8] > 0xFFF:
                            self.V[0xF] = 1
                        else:
                            self.V[0xF] = 0
                        self.I += self.V[(self.opcode & 0x0F00) >> 8]
                        self.pc += 2
                    case 0x0029:
                        self.I = self.V[(self.opcode & 0x0F00) >> 8] * 0x5
                        self.pc += 2
                    case 0x0033:
                        self.memory[self.I] = self.V[(
                            self.opcode & 0x0F00) >> 8] / 100
                        self.memory[self.I +
                                    1] = (self.V[(self.opcode & 0x0F00) >> 8] / 10) % 10
                        self.memory[self.I +
                                    2] = (self.V[(self.opcode & 0x0F00) >> 8] % 100) % 10
                        self.pc += 2
                    case 0x0055:
                        for i in range((self.opcode & 0x0F00) >> 8):
                            self.memory[self.I + i] = self.V[i]
                        self.I += ((self.opcode & 0x0F00) >> 8) + 1
                        self.pc += 2
                    case 0x0065:
                        for i in range((self.opcode & 0x0F00) >> 8):
                            self.V[i] = self.memory[self.I + i]
                        self.I += ((self.opcode & 0x0F00) >> 8) + 1
                        self.pc += 2
                    case _:
                        print("Unknown opcode [0xF000]: 0x%X" % self.opcode)
                        self.pc += 2
            case _:
                print("Unknown opcode: 0x%X" % self.opcode)
                self.pc += 2
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            if self.sound_timer == 1:
                sys.stdout.write('\a')
            self.sound_timer -= 1


async def drawSprite(opcode, V, memory, I, gfx):
    x = XCOORD(V[(opcode & 0x0F00) >> 8])
    y = YCOORD(V[(opcode & 0x00F0) >> 4])
    height = opcode & 0x000F
    V[0xF] = 0
    for yline in range(height):
        pixel = memory[I + yline]
        for xline in range(8):
            if (pixel & (0x80 >> xline)) != 0:
                if gfx[(XCOORD(x + xline) + (YCOORD(y + yline) * 64))] == 1:
                    V[0xF] = 1
                gfx[XCOORD(x + xline) + (YCOORD(y + yline) * 64)] ^= 1
    await drawGraphics(gfx)

if __name__ == "__main__":
    name = sys.argv[1]
    asyncio.run(main(name))
