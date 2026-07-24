# QuantInvest Tool - UI Design System

## Design System Overview

A professional, cohesive design system for the QuantInvest Tool that ensures visual consistency, accessibility, and usability across all tabs and dialogs.

---

## Color Palette

### Primary Colors

**Dark Theme (Default)**
```
Brand Blue:        #0D47A1  (RGB: 13, 71, 161)   - Buttons, accents
Dark Background:   #1E1E1E  (RGB: 30, 30, 30)    - Window background
Dark Surface:      #2D2D2D  (RGB: 45, 45, 45)    - Input fields, panels
Dark Border:       #3D3D3D  (RGB: 61, 61, 61)    - Borders, dividers
Primary Text:      #FFFFFF  (RGB: 255, 255, 255) - Main text
Secondary Text:    #B0B0B0  (RGB: 176, 176, 176)- Help text, labels
```

**Light Theme (Alternative)**
```
Brand Blue:        #1976D2  (RGB: 25, 118, 210)
Light Background:  #FAFAFA  (RGB: 250, 250, 250)
Light Surface:     #FFFFFF  (RGB: 255, 255, 255)
Light Border:      #E0E0E0  (RGB: 224, 224, 224)
Primary Text:      #212121  (RGB: 33, 33, 33)
Secondary Text:    #757575  (RGB: 117, 117, 117)
```

### Semantic Colors

**Status & Feedback**
```
Success:    #4CAF50  (RGB: 76, 175, 80)    - Green checkmarks, success states
Warning:    #FF9800  (RGB: 255, 152, 0)    - Orange warnings, cautions
Error:      #F44336  (RGB: 244, 67, 54)    - Red errors, critical alerts
Info:       #2196F3  (RGB: 33, 150, 243)   - Blue information, hints
Disabled:   #9E9E9E  (RGB: 158, 158, 158)  - Gray disabled states
```

**Chart Colors**
```
Strategy Line:    #0D47A1  (Blue)       - Strategy cumulative returns
Benchmark Line:   #F44336  (Red)        - Buy & hold returns
Winning Trades:   #4CAF50  (Green)      - Profitable trades
Losing Trades:    #F44336  (Red)        - Unprofitable trades
Drawdown:         #FF9800  (Orange)     - Maximum drawdown area
Price Line:       #2196F3  (Light Blue) - Price chart
Volume:           #9C27B0  (Purple)     - Volume indicator
```

---

## Typography

### Font Family
- **Primary**: "Segoe UI" (Windows), "SF Pro Display" (macOS), "Ubuntu" (Linux)
- **Monospace**: "Courier New", "Consolas" (for numbers, code, parameters)
- **Fallback**: Sans-serif

### Font Sizes & Weights

| Element | Size | Weight | Usage |
|---------|------|--------|-------|
| Window Title | 14pt | Bold (700) | Main window title |
| Tab Label | 11pt | Normal (400) | Tab names |
| Section Header | 12pt | Bold (700) | "Stock Configuration", "Strategy Parameters" |
| Label/Input Label | 10pt | Normal (400) | Form labels |
| Body Text | 10pt | Normal (400) | Regular text, descriptions |
| Help Text/Tooltip | 9pt | Normal (400) | Helper text, gray color |
| Status Bar | 10pt | Normal (400) | Status messages |
| Metric Value | 14pt | Bold (700) | Large metric numbers (38%, 1.46, etc.) |
| Metric Label | 9pt | Normal (400) | Metric names (CAGR, Sharpe Ratio) |

### Line Height
- Body text: 1.5x font size
- Labels: 1.2x font size
- Titles: 1.2x font size

---

## Spacing & Layout

### Spacing Scale
```
xs: 2px   (borders, minimal gaps)
sm: 4px   (tight spacing)
md: 8px   (standard spacing)
lg: 16px  (section spacing)
xl: 24px  (major section spacing)
xxl: 32px (window padding)
```

### Layout Guidelines

**Margins & Padding**
```
Window padding:         24px (all edges)
Section padding:        16px
Widget padding:         8px
Form field spacing:     8px (horizontal), 12px (vertical)
Button padding:         6px vertical, 12px horizontal
Tab content margin:     16px
Dialog padding:         20px
```

**Minimum Sizes**
```
Window width:     800px
Window height:    600px
Input field width: 200px
Button width:     120px
Button height:    36px
Table row height: 24px
```

---

## Component Specifications

### Buttons

**Standard Button**
```
States:
- Normal:     Background: #0D47A1, Text: #FFFFFF
- Hover:      Background: #1565C0 (lighter blue)
- Pressed:    Background: #0A3D91 (darker blue)
- Disabled:   Background: #9E9E9E, Opacity: 50%

Size: 36px height, 120px+ width
Padding: 6px top/bottom, 12px left/right
Border Radius: 3px
Font: Segoe UI, 10pt, Bold
Cursor: Pointer (hand)
```

**Secondary Button**
```
Background: Transparent
Border: 1px solid #3D3D3D
Text: #B0B0B0
Hover: Border #0D47A1, Text: #0D47A1
```

**Icon Button**
```
Size: 32x32 pixels
Background: Transparent
Hover: Background: #3D3D3D (subtle highlight)
```

### Input Fields

**Text Input / LineEdit**
```
Background: #2D2D2D
Text Color: #FFFFFF
Border: 1px solid #3D3D3D
Border Radius: 3px
Padding: 5px (all edges)
Height: 28px
Placeholder: #9E9E9E (grayed out)
Focus: Border color #0D47A1, 2px thick
```

**Date/Time Input**
```
Same as text input with calendar dropdown button
Dropdown button width: 24px
```

**Numeric Input (Spin Box)**
```
Same as text input
Up/Down buttons on right side
Button width: 18px each
```

**Slider**
```
Height: 6px
Track color: #3D3D3D
Handle: 16px circle, #0D47A1
Range color: #0D47A1
```

### Checkboxes & Radio Buttons

**Checkbox**
```
Size: 16x16 pixels
Unchecked: Border 1px #3D3D3D, transparent inside
Checked: Background #0D47A1, white checkmark
Hover: Border #0D47A1
Label: Left or right, 4px spacing
```

### Dropdown/Combo Box

```
Height: 28px
Padding: 5px left/right
Background: #2D2D2D
Border: 1px solid #3D3D3D
Text: #FFFFFF
Dropdown arrow: Right side
Dropdown menu: Dark background, hover highlight
```

### Progress Bar

```
Height: 8px
Background: #3D3D3D (unfilled)
Filled: Linear gradient from #0D47A1 to #1565C0
Border Radius: 4px
Text: Optional % in center
Indeterminate: Animated gradient
```

### Table Widget

```
Row height: 24px
Header height: 28px
Header background: #1E1E1E
Header text: #FFFFFF, Bold
Body background: #2D2D2D
Body text: #FFFFFF
Border: 1px solid #3D3D3D
Alternating rows: Every other row slightly darker (#252525)
Selection: Highlight background #0D47A1
```

### Dialog Windows

```
Title bar: 32px height, bold title
Content padding: 20px
Button area padding: 20px, top border 1px #3D3D3D
Min width: 400px
Min height: 300px
Modal: Dark overlay (70% opacity) behind dialog
```

---

## Responsive Design

### Breakpoints
```
Small:    < 600px   (Very small windows, mobile-like)
Medium:   600-1024px (Laptop/desktop standard)
Large:    > 1024px  (Wide desktop)
```

### Responsive Behavior

**Small Screens (< 600px)**
- Stack tabs horizontally → vertically scrollable
- Reduce padding to 12px
- Metrics table becomes horizontal scroll
- Charts scale to fit width
- Buttons: full width

**Medium Screens (600-1024px)**
- Standard layout
- Two columns where applicable
- Normal padding

**Large Screens (> 1024px)**
- Multi-column layouts
- Expanded spacing
- Larger charts and tables

### Minimum Viable Window Size
- Width: 800px (hard minimum)
- Height: 600px (hard minimum)
- Below minimum: Show scroll bars, disable certain features

---

## Icons & Visual Elements

### Icon Set
- Use: Font Awesome (free) or Material Design Icons
- Size: 16px (small), 24px (standard), 32px (large)
- Color: Inherit from context (text color, accent color)

### Common Icons
```
📥 Download/Import
📤 Export/Save
⚙️  Settings
❌ Close/Cancel
✓  Confirm/OK
⏹  Stop/Cancel (operation)
🔄 Refresh/Reload
🗑️  Delete/Clear
📋 Copy
📊 Chart/Analytics
💾 Save
📁 Folder/Directory
🔍 Search
ℹ️  Information/Help
⚠️  Warning
❗ Error
```

---

## Tooltips & Help Text

### Tooltip Style
```
Background: #252525 (darker than surface)
Text: #FFFFFF
Border: 1px solid #3D3D3D
Padding: 8px
Border Radius: 3px
Font: 9pt, sans-serif
Max width: 300px
Delay: 500ms before show
Duration: 5 seconds or until mouse leaves

Example: "Momentum Period: Number of days for momentum calculation (3-30)"
```

### Help Icons
```
Placement: Right of label with small (ⓘ) icon
Color: #0D47A1 (when hovered)
Cursor: Help/question mark
On hover: Show tooltip
```

---

## Dark Mode Implementation

### CSS Variables (Qt Stylesheet)

```css
:root {
  /* Colors */
  --color-primary: #0D47A1;
  --color-primary-hover: #1565C0;
  --color-primary-active: #0A3D91;
  
  --color-background: #1E1E1E;
  --color-surface: #2D2D2D;
  --color-border: #3D3D3D;
  
  --color-text-primary: #FFFFFF;
  --color-text-secondary: #B0B0B0;
  --color-text-disabled: #9E9E9E;
  
  --color-success: #4CAF50;
  --color-warning: #FF9800;
  --color-error: #F44336;
  --color-info: #2196F3;
  
  /* Spacing */
  --space-xs: 2px;
  --space-sm: 4px;
  --space-md: 8px;
  --space-lg: 16px;
  --space-xl: 24px;
  
  /* Fonts */
  --font-family: "Segoe UI", sans-serif;
  --font-family-mono: "Courier New", monospace;
  --font-size-base: 10pt;
  --font-size-label: 9pt;
  --font-size-title: 12pt;
}
```

### Light Mode Override

```css
[data-theme="light"] {
  --color-background: #FAFAFA;
  --color-surface: #FFFFFF;
  --color-border: #E0E0E0;
  --color-text-primary: #212121;
  --color-text-secondary: #757575;
}
```

---

## Accessibility (A11y)

### Keyboard Navigation

**Tab Order**
1. Menu bar
2. Toolbar (if present)
3. Tab widget (left to right)
4. Tab content (top to bottom)
5. Status bar

**Keyboard Shortcuts**
```
Ctrl+Q             Exit
Ctrl+S             Save Session
Ctrl+O             Open Session
Ctrl+E             Export Results
Ctrl+R             Run Backtest
Ctrl+F             Find (if search available)
Alt+H              Help
Tab                Navigate forward
Shift+Tab           Navigate backward
Enter              Activate button/input
Space              Toggle checkbox/button
Arrow Keys         Scroll/change spinner
```

### Screen Reader Support
- All buttons have descriptive labels
- Input fields have associated labels
- Images have alt text
- Tables have header rows marked
- Error messages are announced

### Color Contrast
- Text: Minimum 4.5:1 contrast ratio (WCAG AA)
- Disabled elements: Minimum 3:1 contrast
- UI components: Minimum 3:1 contrast ratio

### Focus Indicators
```
Focus outline: 2px solid #0D47A1
Offset: 2px from element
```

---

## Dialog Designs

### Error Dialog
```
┌─────────────────────────────────┐
│ Error                        [X] │
├─────────────────────────────────┤
│ ❌                              │
│ Unable to download AAPL data    │
│                                 │
│ The ticker "AAPL" is invalid.   │
│ Please check and try again.     │
│                                 │
│ (Error code: INVALID_TICKER)    │
│                                 │
│ [OK]                    [Retry] │
└─────────────────────────────────┘
```

### Confirmation Dialog
```
┌──────────────────────────────────┐
│ Confirm                       [X] │
├──────────────────────────────────┤
│ Clear cache?                     │
│                                  │
│ This will delete cached stock    │
│ data. Downloaded data will need  │
│ to be re-fetched.               │
│                                  │
│ ☑ Don't show this again          │
│                                  │
│ [Cancel]          [Clear Cache]  │
└──────────────────────────────────┘
```

### Progress Dialog (During Long Operation)
```
┌──────────────────────────────────┐
│ Running Parameter Optimization   │
├──────────────────────────────────┤
│                                  │
│ Processing combinations...       │
│ ████████░░░░░░░░░░░░  47%       │
│                                  │
│ 235 / 500 combinations          │
│ Elapsed: 2m 34s                 │
│ Estimated remaining: 2m 45s     │
│                                  │
│ Best found: 467% return          │
│ Parameters: p=9, mfi=45, sl=0.06 │
│                                  │
│                        [Cancel]  │
└──────────────────────────────────┘
```

### Parameter Range Dialog
```
┌──────────────────────────────────┐
│ Set Optimization Ranges      [X] │
├──────────────────────────────────┤
│ Momentum Period                  │
│ From: [8    ] To: [20   ] Step 1  │
│ Estimated values: 13             │
│                                  │
│ MFI Level                        │
│ From: [40   ] To: [60   ] Step 5  │
│ Estimated values: 5              │
│                                  │
│ Stop Loss                        │
│ From: [3%   ] To: [10%  ] Step 1% │
│ Estimated values: 8              │
│                                  │
│ Total combinations: 13 × 5 × 8   │
│                     = 520        │
│                                  │
│ [Reset] [Cancel]      [Apply]   │
└──────────────────────────────────┘
```

---

## Animation & Transitions

### Tab Switching
- Duration: 200ms (fade)
- Easing: Ease-in-out

### Button Interactions
- Hover: 100ms color transition
- Click: Immediate
- Release: 100ms color transition

### Progress Updates
- Linear progress bar animation
- Smooth value updates (no jumps)
- Percentage text updates: integer rounding

### Chart Rendering
- Initial load: 500ms fade-in
- Data updates: 300ms animation (for line movements)

---

## Printing & Export

### PDF Report Layout
```
┌─────────────────────────────────┐
│        QuantInvest Tool         │
│    Backtest Analysis Report     │
├─────────────────────────────────┤
│                                 │
│ Stock: AAPL                     │
│ Period: 2023-01-01 to 2024-01-01│
│ Strategy: Momentum              │
│ Generated: 2026-07-24           │
│                                 │
├─────────────────────────────────┤
│ Performance Metrics             │
│                                 │
│ CAGR            38.37%          │
│ Sharpe Ratio    1.46            │
│ Max Drawdown    -32.87%         │
│ Win Rate        50.00%          │
│ P/L Ratio       4.92            │
│                                 │
├─────────────────────────────────┤
│ Cumulative Returns Chart        │
│ (Embedded chart image)          │
│                                 │
├─────────────────────────────────┤
│ Trade Summary                   │
│ Total Trades: 20                │
│ Winning: 10 (50.00%)           │
│ Losing: 10 (50.00%)            │
│                                 │
└─────────────────────────────────┘
```

### CSV Export Format
```
QuantInvest_AAPL_20230101-20240101.csv

Date,Close,Signal,Position,Portfolio_Value,Cumulative_Return
2023-01-01,150.50,0,0,10000.00,1.0
2023-01-02,151.20,0,0,10000.00,1.0
...
2024-01-01,192.35,0,0,13985.00,1.3985
```

---

## Performance Optimization

### Lazy Loading
- Charts only rendered when tab selected
- Large tables paginated (20 rows per page)
- Cache UI state to avoid re-rendering

### Rendering
- Use Qt's double buffering
- Minimize redraws of unchanged elements
- Use QGraphicsView for complex charts

### Memory
- Limit chart history to 500 points (downsample if needed)
- Clear worker thread signals after completion
- Cache matrix calculations

---

## Branding

### Logo & Icon
- Create 256x256 PNG with QuantInvest brand
- Rounded square design
- Colors: Brand Blue (#0D47A1) on light gray
- Icon variations: 16x16, 32x32, 64x64, 128x128, 256x256

### Window Title
```
"QuantInvest Tool v1.0 - [Current Stock] [Current Strategy]"
Example: "QuantInvest Tool v1.0 - AAPL (Momentum)"
```

### Splash Screen
```
┌─────────────────────────────────┐
│                                 │
│         QuantInvest Tool        │
│           Loading...            │
│                                 │
│  ████████░░░░░░░░░░  40%       │
│                                 │
│  Version 1.0                    │
│  © 2026 Development Team        │
│                                 │
└─────────────────────────────────┘
```

---

**This design system ensures consistent, professional, and accessible UI across all components of the QuantInvest Tool.**
