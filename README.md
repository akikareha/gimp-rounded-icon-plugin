# Rounded Iconify (GIMP 3 Python Plug-in)

**Rounded Iconify** is a GIMP 3.0 Python plug-in that creates square icons
with rounded corners.  
It is useful for preparing UI assets or small icons that need a clean look
across both light and dark themes.

![Suzume](suzume.png)
==>>
![Suzume Icon](suzume-icon.png)

## Features

- Adds alpha channel if missing
- Adds a white layer mask
- Applies current selection to the mask (if any)
- Rounds corners based on a ratio of image width
- Clears outside the rounded selection
- Scales down to a target icon size
- Interactive dialog for parameters:
  - **Corner Ratio**: divisor of width (e.g. 6 → radius = width/6)
  - **Icon Size**: final square size in pixels

## Installation

1. Copy the plug-in directory into your GIMP config folder:

   ```bash
   mkdir -p ~/.config/GIMP/3.0/plug-ins/rounded_icon
   cp rounded_icon.py ~/.config/GIMP/3.0/plug-ins/rounded_icon/
   chmod +x ~/.config/GIMP/3.0/plug-ins/rounded_icon/rounded_icon.py
   ```
2. Restart GIMP.

3. The plug-in will appear in the menu:

```
Image -> Python-Fu -> Rounded Iconify
```

## Usage

A typical workflow:

1. Open a square image (e.g. 512×512).
2. Use the **Fuzzy Select (wand) tool** to select the background area.
3. Set the **foreground color** to a neutral gray (e.g. `#c0c0c0`).
    * This color will be used to fill the mask, controlling the
    transparency of the background.
    * By choosing lighter or darker grays, you can adjust the transparency.
4. Run **Rounded Iconify** from the menu.
5. In the dialog:
    * **Corner Ratio**: smaller values -> stronger rounding; larger values
    -> gentler rounding.
    * **Icon Size**: final square size in pixels (default `128`).
6. The image will be transformed into a rounded-corner icon:
    * The background outside the rounded rectangle is cleared.
    * The image is scaled to the target size.
    * The result works well on both light and dark themes.

## Example

* Input: a 512×512 square logo with a white background.
* Workflow: background selected with wand tool, foreground color set to `#c0c0c0`.
* Settings: `Corner Ratio = 6`, `Icon Size = 128`.
* Output: a 128×128 rounded-corner icon with semi-transparent gray edges.

## Requirements

* GIMP >= 3.0
* Python >= 3.10
* GI bindings for GIMP (`python3-gi`, installed with GIMP 3)

## License

MIT License.
