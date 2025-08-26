"""Progress tracking and user interface for AWS Services Reporter.

Provides beautiful progress bars, spinners, and status messages using the Rich library,
with graceful fallback to simple text output when Rich is not available.
"""

from typing import Any, List, Optional, Tuple
from tabulate import tabulate

# Try to import Rich for enhanced progress tracking
try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn, TimeElapsedColumn
    from rich.table import Table
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None


class ProgressTracker:
    """Enhanced progress tracking with Rich library support.
    
    Provides beautiful progress bars, spinners, and status messages using the Rich library,
    with graceful fallback to simple text output when Rich is not available.
    
    Attributes:
        use_rich: Whether to use Rich library features
        quiet: Whether to suppress all output
        console: Rich console instance
        current_progress: Current progress bar state
    """
    
    def __init__(self, use_rich: bool = True, quiet: bool = False) -> None:
        """Initialize progress tracker.
        
        Args:
            use_rich: Enable Rich library features if available
            quiet: Suppress all progress output
        """
        self.use_rich = use_rich and RICH_AVAILABLE and not quiet
        self.quiet = quiet
        self.console = Console() if self.use_rich else None
        self.current_progress = None
    
    def start_operation(self, description: str, total: Optional[int] = None) -> Optional[Tuple[Any, Any]]:
        """Start a new operation with optional progress bar.
        
        Args:
            description: Description of the operation
            total: Total number of items for progress tracking (optional)
            
        Returns:
            Tuple of (progress, task_id) if Rich is available, None otherwise
            None if quiet mode is enabled
        """
        if self.quiet:
            return None
            
        if self.use_rich:
            # Create rich progress bar
            progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn() if total else TextColumn(""),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%") if total else TextColumn(""),
                TimeElapsedColumn(),
                TimeRemainingColumn() if total else TextColumn(""),
                console=self.console,
                transient=False
            )
            progress.start()
            task_id = progress.add_task(description, total=total or 100)
            self.current_progress = (progress, task_id)
            return self.current_progress
        else:
            # Fallback to simple print
            print(f"⏳ {description}...")
            return None
    
    def update_progress(self, advance: int = 1, description: Optional[str] = None) -> None:
        """Update progress bar with advancement and optional description.
        
        Args:
            advance: Number of units to advance (default: 1)
            description: Updated description for the progress bar
        """
        if self.quiet:
            return
            
        if self.use_rich and self.current_progress:
            progress, task_id = self.current_progress
            progress.update(task_id, advance=advance, description=description)
    
    def finish_operation(self, success_message: Optional[str] = None) -> None:
        """Finish current operation and display success message.
        
        Args:
            success_message: Optional success message to display
        """
        if self.quiet:
            return
            
        if self.use_rich and self.current_progress:
            progress, task_id = self.current_progress
            progress.stop()
            self.current_progress = None
            if success_message:
                self.console.print(f"✅ {success_message}", style="green")
        else:
            if success_message:
                print(f"✅ {success_message}")
    
    def print_status(self, message: str, style: Optional[str] = None) -> None:
        """Print status message with optional Rich styling.
        
        Args:
            message: Message to display
            style: Rich style string (e.g., 'green', 'bold red')
        """
        if self.quiet:
            return
            
        if self.use_rich:
            self.console.print(message, style=style)
        else:
            print(message)
    
    def print_table(self, data: List[List[str]], headers: List[str], title: Optional[str] = None) -> None:
        """Print table with Rich formatting if available.
        
        Args:
            data: List of rows, where each row is a list of cell values
            headers: List of column headers
            title: Optional table title
        """
        if self.quiet:
            return
            
        if self.use_rich:
            table = Table(title=title)
            for header in headers:
                table.add_column(header)
            for row in data:
                table.add_row(*[str(cell) for cell in row])
            self.console.print(table)
        else:
            if title:
                print(f"\n{title}")
            print(tabulate(data, headers=headers, tablefmt="grid"))
    
    def print_panel(self, content: str, title: Optional[str] = None) -> None:
        """Print content in a panel if Rich is available.
        
        Args:
            content: Text content to display
            title: Optional panel title
        """
        if self.quiet:
            return
            
        if self.use_rich:
            panel = Panel(content, title=title)
            self.console.print(panel)
        else:
            if title:
                print(f"\n=== {title} ===")
            print(content)