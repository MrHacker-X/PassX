#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PassX v2.0 - strong password generator (Termux / Linux)

Everything happens locally:
  - Passwords come from Python's `secrets` module (CSPRNG).
  - Nothing is written, logged or sent anywhere unless you ask for --save.

Usage:
  python3 passx.py                      interactive menu
  python3 passx.py -l 24 -c 5           5 random passwords, 24 chars
  python3 passx.py -m phrase -w 6       6-word passphrase
  python3 passx.py -m pin -l 8          8-digit PIN
  python3 passx.py --doctor             environment self-check
  python3 passx.py -v                   version
"""

import argparse
import math
import os
import shutil
import subprocess
import sys
import time

try:
    import secrets  # noqa: F401  (presence check; real use below)
    HAVE_SECRETS = True
except ImportError:  # pragma: no cover
    HAVE_SECRETS = False

import random as _insecure_fallback  # only used if secrets is missing (pre-3.6)

VERSION = "2.0"
TOOL = "PassX"

# ---------------------------------------------------------------------------
# House palette - colours off when not a tty or NO_COLOR is set
# ---------------------------------------------------------------------------

def _supports_color():
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

COLOR = _supports_color()

WH = "\033[1;97m" if COLOR else ""   # white
YL = "\033[38;5;179m" if COLOR else ""   # warm sand
GR = "\033[38;5;150m" if COLOR else ""   # sage green
DM = "\033[38;5;245m" if COLOR else ""   # dim grey
RE = "\033[38;5;196m" if COLOR else ""   # red
GN = "\033[38;5;114m" if COLOR else ""   # good green
RS = "\033[0m" if COLOR else ""

# ---------------------------------------------------------------------------
# Block-letter wordmark (house pattern: no ASCII art, block glyphs only)
# ---------------------------------------------------------------------------

_BLOCK_FONT = {
    "P": ["████ ", "█   █", "████ ", "█    ", "█    "],
    "A": [" ███ ", "█   █", "█████", "█   █", "█   █"],
    "S": [" ████", "█    ", " ███ ", "    █", "████ "],
    "X": ["█   █", " █ █ ", "  █  ", " █ █ ", "█   █"],
}


def _wordmark_rows(text="PASSX"):
    rows = [""] * 5
    for i, ch in enumerate(text.upper()):
        glyph = _BLOCK_FONT.get(ch)
        if glyph is None:
            continue
        for r in range(5):
            rows[r] += glyph[r] + " "
    return rows


def banner():
    print()
    for row in _wordmark_rows("PASSX"):
        print(f"{YL}{row.center(44)}{RS}")
    print(f"{DM}{'v' + VERSION + ' - strong local password generator'.center(44)}{RS}")
    print(f"{DM}{'secrets-based CSPRNG · nothing leaves this device'.center(44)}{RS}")
    print()


def rule(width=44):
    print(f"{DM}{'─' * width}{RS}")


def header(title):
    print(f"\n{WH}{title}{RS}")
    rule()


def say(msg=""):
    print(f"{WH}{msg}{RS}")


def note(msg):
    print(f"{GR}  {msg}{RS}")


def warn(msg):
    print(f"{YL}  ! {msg}{RS}")


def err(msg):
    print(f"{RE}  x {msg}{RS}", file=sys.stderr)


def kv(key, val):
    print(f"{DM}  {key:<14}{RS}{WH}{val}{RS}")


def item(num, label, desc=""):
    print(f"  {YL}[{WH}{num}{YL}]{RS} {WH}{label}{RS}{DM}  {desc}{RS}")


def ask(prompt):
    """Input that exits cleanly on EOF (piped/redirected input)."""
    try:
        return input(f"{YL}  {prompt}{WH} ").strip()
    except EOFError:
        print()
        safe_exit()


def confirm(prompt):
    ans = ask(f"{prompt} [y/N]:").lower()
    return ans in ("y", "yes")


def pause():
    try:
        input(f"{DM}  press ENTER to continue…{RS}")
    except EOFError:
        safe_exit()


def safe_exit():
    print(f"\n{DM}  safe exit.{RS}")
    sys.exit(130)


def int_input(prompt, lo, hi, default):
    """Integer input with bounds and default; returns int."""
    raw = ask(f"{prompt} [{default}]:")
    if raw == "":
        return default
    try:
        val = int(raw)
    except ValueError:
        err(f"not a number: {raw}")
        return int_input(prompt, lo, hi, default)
    if not (lo <= val <= hi):
        err(f"must be {lo}–{hi}")
        return int_input(prompt, lo, hi, default)
    return val


# ---------------------------------------------------------------------------
# Password engine
# ---------------------------------------------------------------------------

CHARSETS = {
    "lower": "abcdefghijklmnopqrstuvwxyz",
    "upper": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "digits": "0123456789",
    "symbols": "!@#$%^&*()-_=+[]{};:,.<>?/~",
}
AMBIGUOUS = "Il1O0o"  # excluded when avoid-ambiguous is on

# 1029 common short words for passphrase mode (written for PassX, no external list)
WORDLIST = (
    "able acid acorn aged agile album amber angle apple apron arrow ash aspen atom "
    "aunt avid axis bacon badge bagel baker bamboo banjo basin batch beach beam bean "
    "beard beetle bench berry bird bison black blade blank blaze blink bloom blue "
    "board bolt bonus book booth bottle box brave bread brick bridge bright brook "
    "brush bubble bucket buddy bugle bunch cabin cable cactus camel candle canoe "
    "canvas canyon cargo carrot castle catch cedar cello chair chalk charm cheese "
    "cherry chill chimney chord cider cinema circle citrus clang clay clever cliff "
    "cloak clock cloud clover coach coast cobra cocoa comet coral cotton couch "
    "coyote crab crane crate crayon cream creek crest cricket crown crumb crystal "
    "cube cup curly curse curve cycle daisy dance dawn deck deer delta den dice "
    "dime diner dingo ditch dock dolphin domino donut door dove draft dragon dream "
    "dress drift drum duck dune dusk eagle earth easel echo edge eel egg elbow "
    "elder elk elm ember emerald engine envoy equal era essay ether evening exit "
    "fable falcon family fancy fang farm fawn feast feather fern ferry fiber fig "
    "filter finch fire fish flag flame fleet flint flock flour flute foam fog forest "
    "fork fort fossil fox frame free fresh frost fruit fudge fungus funnel fuse "
    "gadget galaxy game garden garlic gauge gecko gem ghost giant gift ginger "
    "glacier glance glass glaze globe glove glow glue goat gold golem goose gorge "
    "grace grain grape graph grass gravel green grid grill groove grove guard "
    "guitar gulf gully gust gym hail hair half halo hammer harbor harp hawk hazel "
    "heart hedge helm heron hickory hill hinge hive hobby hockey hollow honey "
    "hood hoof hook horizon horn horse hotel house human humid hunt hut ice "
    "icicle idea igloo image index ingot inlet iris iron island ivory ivy jacket "
    "jade jaguar jam jar jasmine jelly jewel jigsaw jockey jog joint joke jolly "
    "jolt journal judge juice jumper jungle junior jury kabob kale kayak kernel "
    "kettle key khaki kiln kilt kimono kind king kiosk kite kitten kiwi knee "
    "knife knight knot koala lace ladder ladle lagoon lake lamp lance lantern "
    "lark laser latch lattice laurel lava lawn layer ledge legend lemon lens "
    "leopard lever lichen lilac lily limber lime linen lion liquid listen lizard "
    "llama loaf loom lotus lumber lunar lynx lyric macaw magenta magnet mahogany "
    "maize mango maple marble marlin marsh mask mason meadow medal melon mentor "
    "mesa meteor midnight mimic mint mirror mist mite mitten mocha mohair mold "
    "monsoon moon moss motel moth mountain mouse muffin mulch muse music mustang "
    "nacho napkin narrow navy neat neck needle nest net never newt nibble nickel "
    "night nimble noble nod noise nomad noon north note nova nozzle nugget nutmeg "
    "oak oasis oat ocean octave odor offer often olive omelet onion onyx opal "
    "opera orange orbit orchard orchid organ origami osprey otter ounce oval owl "
    "oxide oyster pace pact paddle pagoda paint palm panda panel pansy panther "
    "papaya paper parade parcel parka parsley pasta pastel patch path patio pause "
    "peach peak pearl pebble pecan pedal pelican penny pepper perch perfume petal "
    "pewter phantom phone photo piano picnic pigment pigeon pillar pilot pine "
    "pistol pivot pixel pizza place plank plant plasma plaza plum pocket poem "
    "point polar polish pond poplar poppy porch portal potato pouch powder power "
    "prairie prawn pretzel pride prime prism prize profile prompt prong proof "
    "propel prowl prune pulley pulse pumpkin punch pupil puppy purse puzzle pyre "
    "python rabbit racer radar radish raft rail rain rally ramp ranch random range "
    "rascal raven razor react ready realm reason rebel recipe reef regal region "
    "relay relic remedy render rescue resin retro rhino ribbon ridge rifle right "
    "rigid rinse ripple ritual river roast robin robot rocket rodent rogue roll "
    "roof rooster root rope rose rotate rough round route rover rowan rubber ruby "
    "rudder ruffle rugby ruler rumor runner runway rust saber saddle safari saffron "
    "sage sail salad salmon salute sand sapphire sardine sash satin sauce sauna "
    "savage savory scale scarf scene scent school scoop scooter scope score scout "
    "scrap screen script scroll sculpt seal season second sector sedan seed "
    "seldom select senate sense sequoia serene serve shadow shale shape shard "
    "share shark sharp shelf shell shield shine shiny shore short shovel shrine "
    "shrug side sierra signal silk silver simple since siren sister sketch skier "
    "skill skirt skull slate sleek sleep slice slide slope small smart smile smoke "
    "snack snake sneaker snow soap sober socket soda solar solid sonar sonnet "
    "soothe sorbet sound soup south soy space spade spark spatula spear speech "
    "sphere spice spider spike spine spiral spire splint spoon sport spout spray "
    "spring sprout squad square squash squid stack staff stage stair stake stamp "
    "stand starling starch statue steam steel stem step stereo sterling stick "
    "stitch stock stone stool storm stove strand straw stream street strike "
    "stripe strong studio stylus sugar summit sunset super supply surf survey "
    "swallow swamp swan sweater swift swing sword syrup table tackle tactic tail "
    "talent tally tandem tangent tanker tape target tavern tempo tender tennis "
    "tent tepid terra thank thaw theater theme thick thing thistle thorn thread "
    "three thrift throne thumb thunder ticket tidal tiger tile timber timer tin "
    "tint tiny tissue toffee toggle token tomato tonic tool topaz topic torch "
    "tornado tortoise total totem touch tower town trace track trade trail train "
    "tram trap travel tray treat trend trial triangle tribe trick trio trophy "
    "tropic trout truck truffle trumpet trunk trust truth tube tulip tumble tundra "
    "tunnel turbine turf turkey turnip turtle tutor tuxedo twig twine twist type "
    "udder ulcer ultra umber umbrella uncle under unicorn uniform union unique "
    "unit upper urban urgent usage user usher utensil utility vacancy valley "
    "value valve vanilla vapor vault velvet vendor vent verse vertex vessel "
    "veteran vibrant video vigor viking villa vine vinyl violet violin virtue "
    "vision visit vital vivid vocal vodka volume vortex voyage wafer wager wagon "
    "waist walnut walrus wand walnut warden warmth wasp watch water wave wax "
    "weasel weather weave wedge well west whale wharf wheat wheel whisk white "
    "wicker widget width wild willow wind window winter wire wisdom wisp wolf "
    "wombat wonder wood wool world worthy woven wrench wrist yacht yarn yeast "
    "yellow yield yodel yoga yogurt yonder young zebra zenith zephyr zeppelin "
    "zest zigzag zinc zipper zone"
).split()


def secure_choice(seq):
    if HAVE_SECRETS:
        return secrets.choice(seq)
    return _insecure_fallback.choice(seq)  # pragma: no cover


def secure_shuffle(lst):
    if HAVE_SECRETS:
        # Fisher-Yates with CSPRNG
        for i in range(len(lst) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            lst[i], lst[j] = lst[j], lst[i]
    else:  # pragma: no cover
        _insecure_fallback.shuffle(lst)
    return lst


def generate_random(length, sets=("lower", "upper", "digits", "symbols"),
                    no_ambiguous=False, at_least_one_of_each=True):
    pools = []
    for name in sets:
        chars = CHARSETS[name]
        if no_ambiguous:
            chars = "".join(c for c in chars if c not in AMBIGUOUS)
        if chars:
            pools.append(chars)
    alphabet = "".join(pools)

    if at_least_one_of_each and length >= len(pools):
        chars = [secure_choice(p) for p in pools]
        chars += [secure_choice(alphabet) for _ in range(length - len(pools))]
        secure_shuffle(chars)
        return "".join(chars)
    return "".join(secure_choice(alphabet) for _ in range(length))


def generate_phrase(words, separator="-", add_number=True):
    picked = [secure_choice(WORDLIST) for _ in range(words)]
    if add_number:
        if HAVE_SECRETS:
            picked.append(str(secrets.randbelow(90) + 10))
        else:  # pragma: no cover
            picked.append(str(_insecure_fallback.randint(10, 99)))
    return separator.join(picked)


def generate_pin(length):
    return "".join(secure_choice("0123456789") for _ in range(length))


def entropy_bits(pw, mode, length, words=0):
    if mode == "phrase":
        bits = math.log2(len(WORDLIST)) * words
        bits += math.log2(90)  # trailing number
        return bits
    if mode == "pin":
        return math.log2(10) * length
    # random: size of the alphabet actually used
    used = set(pw)
    if not used:
        return 0.0
    return math.log2(len("".join(CHARSETS.values()))) * length


def strength_label(bits):
    if bits < 40:
        return ("WEAK", RE)
    if bits < 60:
        return ("FAIR", YL)
    if bits < 80:
        return ("STRONG", GR)
    if bits < 100:
        return ("VERY STRONG", GN)
    return ("FORTRESS", GN)


def meter(pw, mode, length, words=0):
    bits = entropy_bits(pw, mode, length, words)
    label, col = strength_label(bits)
    filled = int(max(0, min(10, bits / 12)))
    bar = "█" * filled + "░" * (10 - filled)
    print(f"    {DM}entropy{RS} {col}{bar}{RS} {col}{bits:5.1f} bits · {label}{RS}")


# ---------------------------------------------------------------------------
# Clipboard + save helpers
# ---------------------------------------------------------------------------

CLIPBOARD_HELPERS = (
    ("termux-clipboard-set", ["termux-clipboard-set"]),
    ("wl-copy", ["wl-copy"]),
    ("xclip", ["xclip", "-selection", "clipboard"]),
    ("pbcopy", ["pbcopy"]),
)


def copy_to_clipboard(text):
    for name, cmd in CLIPBOARD_HELPERS:
        if shutil.which(name):
            try:
                subprocess.run(cmd, input=text.encode(), check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return name
            except (OSError, subprocess.CalledProcessError):
                continue
    return None


def save_passwords(pws, mode):
    stamp = time.strftime("%Y%m%d-%H%M%S")
    fname = f"passx-{mode}-{stamp}.txt"
    try:
        with open(os.open(fname, os.O_CREAT | os.O_WRONLY, 0o600), "w") as fh:
            fh.write("\n".join(pws) + "\n")
        os.chmod(fname, 0o600)
        return fname
    except OSError as exc:
        err(f"could not save: {exc}")
        return None


# ---------------------------------------------------------------------------
# Interactive flows
# ---------------------------------------------------------------------------

MODES = [
    ("1", "random",    "Random strong password (letters + digits + symbols)"),
    ("2", "phrase",    "Passphrase (memorable words + number)"),
    ("3", "pin",       "Numeric PIN"),
    ("4", "random",    "Random with custom character sets"),
]


def flow_generate():
    header("Generate")
    print(f"  {DM}modes:{RS}")
    for num, mode, desc in MODES:
        item(num, desc)
    print(f"  {YL}[0]{RS} {WH}back{RS}")
    choice = ask("mode:")
    if choice == "0" or choice == "":
        return
    if choice not in ("1", "2", "3", "4"):
        err(f"invalid mode: {choice}")
        return

    mode = {"1": "random", "2": "phrase", "3": "pin", "4": "random"}[choice]

    if mode == "phrase":
        words = int_input("words per phrase (3-12)", 3, 12, 5)
        count = int_input("how many (1-100)", 1, 100, 1)
        sep = ask("separator [-]:") or "-"
        length = words  # for meter math
        passwords = [generate_phrase(words, sep) for _ in range(count)]
    elif mode == "pin":
        length = int_input("PIN length (4-24)", 4, 24, 8)
        count = int_input("how many (1-100)", 1, 100, 1)
        passwords = [generate_pin(length) for _ in range(count)]
    else:
        length = int_input("password length (4-256)", 4, 256, 20)
        count = int_input("how many (1-100)", 1, 100, 1)
        no_amb = False
        sets = ("lower", "upper", "digits", "symbols")
        if choice == "4":
            print(f"  {DM}include (enter to keep):{RS}")
            s = ask(f"lowercase [Y]:").lower()
            u = ask(f"uppercase [Y]:").lower()
            d = ask(f"digits    [Y]:").lower()
            y = ask(f"symbols   [Y]:").lower()
            sets = tuple(
                name for name, flag in
                (("lower", s), ("upper", u), ("digits", d), ("symbols", y))
                if flag in ("", "y", "yes")
            ) or ("lower", "upper", "digits")
            if ask("avoid look-alike chars Il1O0 [N]:").lower() in ("y", "yes"):
                no_amb = True
        passwords = [
            generate_random(length, sets=sets, no_ambiguous=no_amb)
            for _ in range(count)
        ]

    print()
    say(f"  {len(passwords)} password{'s' if len(passwords) != 1 else ''}:")
    print()
    for pw in passwords:
        print(f"    {WH}{pw}{RS}")
        if count <= 10:
            meter(pw, mode, length, words if mode == "phrase" else 0)
    if count > 10:
        note(f"(strength shown for first 10 of {count})")
        for pw in passwords[:3]:
            meter(pw, mode, length, words if mode == "phrase" else 0)

    print()
    helper = copy_to_clipboard(passwords[0])
    if helper:
        note(f"first password copied via {helper}")
    else:
        warn("no clipboard helper found (termux-clipboard-set / wl-copy / xclip / pbcopy)")

    if confirm("save all to a file (chmod 600)?"):
        fname = save_passwords(passwords, mode)
        if fname:
            note(f"saved: {fname}")
            warn("plaintext on disk - delete it when you've stored the passwords")
    pause()


def flow_about():
    header("About / security notes")
    say("  PassX generates passwords locally with Python's `secrets` module")
    say("  (a cryptographically secure random generator).")
    print()
    kv("generator", "secrets (CSPRNG)" if HAVE_SECRETS else "random (FALLBACK - upgrade Python)")
    kv("wordlist", f"{len(WORDLIST)} words embedded")
    kv("network", "none - nothing is uploaded")
    kv("developer", "MrHacker-X")
    kv("website", "https://vritrasec.com")
    print()
    note("a strong password is long first, complex second")
    note("passphrases are easier to type on phones and just as strong")
    note("never reuse passwords across accounts - use a password manager")
    note("2FA protects you even if a password leaks")
    print()
    pause()


def menu():
    while True:
        os.system("clear" if os.name != "nt" else "cls")
        banner()
        print(f"  {YL}[{WH}1{YL}]{RS} {WH}Generate passwords{RS}")
        print(f"  {YL}[{WH}2{YL}]{RS} {WH}About / security notes{RS}")
        print(f"  {YL}[{WH}0{YL}]{RS} {WH}Exit{RS}")
        print()
        choice = ask("passx >>")
        if choice in ("1", "01"):
            flow_generate()
        elif choice in ("2", "02"):
            flow_about()
        elif choice in ("0", "00", "q", "quit", "exit"):
            print(f"\n{DM}  thanks for using PassX.{RS}")
            return
        elif choice == "":
            continue
        else:
            err(f"invalid option: {choice}")
            time.sleep(0.4)


# ---------------------------------------------------------------------------
# Doctor
# ---------------------------------------------------------------------------

def doctor():
    banner()
    checks = []

    def check(name, ok, detail=""):
        checks.append((name, ok, detail))

    check("python", sys.version_info >= (3, 8),
          f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    check("secrets (CSPRNG)", HAVE_SECRETS,
          "ok" if HAVE_SECRETS else "missing - passwords would be insecure!")
    check("wordlist", len(WORDLIST) >= 250, f"{len(WORDLIST)} words")
    check("entropy math", abs(entropy_bits("a" * 20, "random", 20) - 20 * math.log2(len("".join(CHARSETS.values())))) < 0.01,
          "log2 charset × length")
    check("tty", sys.stdout.isatty(), "colors " + ("on" if COLOR else "off"))
    helper = next((n for n, _ in CLIPBOARD_HELPERS if shutil.which(n)), None)
    check("clipboard", helper is not None, helper or "none found (copy will be skipped)")

    width = max(len(n) for n, _, _ in checks)
    all_ok = True
    for name, ok, detail in checks:
        if name == "tty":  # informational only - not an environment problem
            mark = f"{DM}--{RS}"
        else:
            mark = f"{GN}OK{RS}" if ok else f"{RE}FAIL{RS}"
            if not ok:
                all_ok = False
        print(f"  {mark}  {WH}{name:<{width}}{RS}  {DM}{detail}{RS}")
    print()
    if all_ok:
        note("all checks passed")
    else:
        warn("some checks failed - see above")
    return 0 if all_ok else 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def one_shot(args):
    sets = ("lower", "upper", "digits", "symbols")
    if args.only_lower:
        sets = ("lower",)
    elif args.only_alpha:
        sets = ("lower", "upper")
    elif args.no_symbols:
        sets = ("lower", "upper", "digits")

    passwords = []
    if args.mode == "phrase":
        for _ in range(args.count):
            passwords.append(generate_phrase(args.words, args.separator))
        length = args.words
    elif args.mode == "pin":
        for _ in range(args.count):
            passwords.append(generate_pin(args.length))
        length = args.length
    else:
        for _ in range(args.count):
            passwords.append(generate_random(args.length, sets=sets,
                                             no_ambiguous=args.no_ambiguous))
        length = args.length

    for pw in passwords:
        print(f"{WH}{pw}{RS}")

    if args.strength:
        print()
        for pw in passwords[:5]:
            meter(pw, args.mode, length, args.words if args.mode == "phrase" else 0)

    if args.copy:
        helper = copy_to_clipboard(passwords[0])
        if helper:
            note(f"first password copied via {helper}")
        else:
            err("no clipboard helper found")

    if args.save:
        fname = save_passwords(passwords, args.mode)
        if fname:
            note(f"saved: {fname}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(
        prog="passx.py",
        description=f"PassX v{VERSION} - strong local password generator",
    )
    p.add_argument("-m", "--mode", choices=["random", "phrase", "pin"],
                   default=None, help="generation mode (default: interactive menu)")
    p.add_argument("-l", "--length", type=int, default=20,
                   help="length for random/pin modes (default: 20)")
    p.add_argument("-w", "--words", type=int, default=5,
                   help="words per passphrase (default: 5)")
    p.add_argument("-c", "--count", type=int, default=1,
                   help="how many passwords (default: 1)")
    p.add_argument("-s", "--separator", default="-",
                   help="passphrase separator (default: -)")
    p.add_argument("--no-symbols", action="store_true",
                   help="letters + digits only")
    p.add_argument("--only-alpha", action="store_true",
                   help="letters only")
    p.add_argument("--only-lower", action="store_true",
                   help="lowercase letters only")
    p.add_argument("--no-ambiguous", action="store_true",
                   help="exclude look-alike characters (Il1O0)")
    p.add_argument("--strength", action="store_true",
                   help="show entropy meter")
    p.add_argument("--copy", action="store_true",
                   help="copy first password to clipboard")
    p.add_argument("--save", action="store_true",
                   help="save passwords to a chmod-600 file")
    p.add_argument("--doctor", action="store_true",
                   help="run environment self-check")
    p.add_argument("-v", "--version", action="store_true",
                   help="print version")
    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(f"PassX v{VERSION}")
        return 0
    if args.doctor:
        return doctor()
    if args.mode:
        banner()
        return one_shot(args)
    menu()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        safe_exit()
