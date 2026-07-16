from colorama import init, Fore

init(autoreset=True)

# ANSI escape codes
RESET = "\033[0m"
STYLES = {
    "DIM": "\033[2m",
    "ITALIC": "\033[3m",
    "UNDERLINE": "\033[4m",
    "BLINK": "\033[5m",
    "REVERSE": "\033[7m",
    "STRIKE": "\033[9m",
}

# Color mapping
COLORS = {
    "BLACK": Fore.BLACK,
    "RED": Fore.RED,
    "GREEN": Fore.GREEN,
    "YELLOW": Fore.YELLOW,
    "BLUE": Fore.BLUE,
    "MAGENTA": Fore.MAGENTA,
    "CYAN": Fore.CYAN,
    "WHITE": Fore.WHITE,
    "LIGHTBLACK_EX": Fore.LIGHTBLACK_EX,
    "LIGHTRED_EX": Fore.LIGHTRED_EX,
    "LIGHTGREEN_EX": Fore.LIGHTGREEN_EX,
    "LIGHTYELLOW_EX": Fore.LIGHTYELLOW_EX,
    "LIGHTBLUE_EX": Fore.LIGHTBLUE_EX,
    "LIGHTMAGENTA_EX": Fore.LIGHTMAGENTA_EX,
    "LIGHTCYAN_EX": Fore.LIGHTCYAN_EX,
    "LIGHTWHITE_EX": Fore.LIGHTWHITE_EX,
    "RESET": Fore.RESET,
}


class Style:
    """ANSI style codes as attributes with validation."""
    
    DIM = STYLES["DIM"]
    ITALIC = STYLES["ITALIC"]
    UNDERLINE = STYLES["UNDERLINE"]
    BLINK = STYLES["BLINK"]
    REVERSE = STYLES["REVERSE"]
    STRIKE = STYLES["STRIKE"]
    
    @classmethod
    def list_styles(cls) -> list:
        """Return list of all available style names."""
        return [attr for attr in dir(cls) if not attr.startswith("_") and attr != "list_styles"]
    
    def __getattr__(self, name):
        """Handle invalid style access."""
        available = ", ".join(Style.list_styles())
        raise AttributeError(
            f"'{name}' is not a valid style. "
            f"Available styles: {available}"
        )


class Color:
    """Color codes as attributes with validation."""
    
    BLACK = "BLACK"
    RED = "RED"
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    BLUE = "BLUE"
    MAGENTA = "MAGENTA"
    CYAN = "CYAN"
    WHITE = "WHITE"
    LIGHTBLACK_EX = "LIGHTBLACK_EX"
    LIGHTRED_EX = "LIGHTRED_EX"
    LIGHTGREEN_EX = "LIGHTGREEN_EX"
    LIGHTYELLOW_EX = "LIGHTYELLOW_EX"
    LIGHTBLUE_EX = "LIGHTBLUE_EX"
    LIGHTMAGENTA_EX = "LIGHTMAGENTA_EX"
    LIGHTCYAN_EX = "LIGHTCYAN_EX"
    LIGHTWHITE_EX = "LIGHTWHITE_EX"
    RESET = "RESET"
    
    @classmethod
    def list_colors(cls) -> list:
        """Return list of all available color names."""
        return [attr for attr in dir(cls) if not attr.startswith("_") and attr != "list_colors"]
    
    def __getattr__(self, name):
        """Handle invalid color access."""
        available = ", ".join(Color.list_colors())
        raise AttributeError(
            f"'{name}' is not a valid color. "
            f"Available colors: {available}"
        )


def _printThis(style: str, message: str, color: str = "WHITE") -> None:
    """
    Print a styled message to the console using ANSI escape codes.
    
    Args:
        style: ANSI style code (Style.DIM, Style.UNDERLINE, etc.)
        message: The text to print
        color: Color name as string (default: "WHITE")
    
    Examples:
        _printThis(style=Style.STRIKE, message="Deprecated", color="RED")
        _printThis(style=Style.UNDERLINE + Style.ITALIC, message="Warning!", color="YELLOW")
    """
    # Get color code from mapping, default to WHITE
    color_code = COLORS.get(color.upper(), Fore.WHITE)
    print(f"{style}{color_code}{message}{RESET}")


# Convenience functions
def print_error(message: str) -> None:
    """Print error message in red."""
    _printThis(style="", message=f"✗ {message}", color="RED")

def print_success(message: str) -> None:
    """Print success message in green."""
    _printThis(style="", message=f"✓ {message}", color="GREEN")

def print_warning(message: str) -> None:
    """Print warning message in yellow."""
    _printThis(style="", message=f"⚠ {message}", color="YELLOW")

def print_info(message: str) -> None:
    """Print info message in cyan."""
    _printThis(style=Style.ITALIC, message=f"ℹ {message}", color="CYAN")
