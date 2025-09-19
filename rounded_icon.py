#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gimp", "3.0")
gi.require_version("GimpUi", "3.0")
from gi.repository import Gimp, GimpUi, GObject, GLib
import sys


def run_proc(name, **kwargs):
    """Utility wrapper for running PDB procedures in GIMP 3."""
    proc = Gimp.get_pdb().lookup_procedure(name)
    if not proc:
        raise RuntimeError(f"Procedure {name} not found")
    config = proc.create_config()
    for k, v in kwargs.items():
        config.set_property(k.replace("_", "-"), v)
    return proc.run(config)


def rounded_icon_run(procedure, run_mode, image, drawables, config, data):
    if len(drawables) < 1:
        return procedure.new_return_values(
            Gimp.PDBStatusType.CALLING_ERROR,
            GLib.Error("Needs at least one drawable (layer)")
        )

    drawable = drawables[0]
    width = image.get_width()

    # --- Show dialog if interactive ---
    if run_mode == Gimp.RunMode.INTERACTIVE:
        GimpUi.init("rounded-icon")
        dialog = GimpUi.ProcedureDialog.new(procedure, config, "Rounded Iconify")
        dialog.fill(["corner-ratio", "icon-size"])
        if not dialog.run():
            dialog.destroy()
            return procedure.new_return_values(Gimp.PDBStatusType.CANCEL, None)
        dialog.destroy()

    # --- Get values from config ---
    corner_ratio = config.get_property("corner-ratio")  # e.g. 6
    icon_size = config.get_property("icon-size")        # e.g. 128 px
    radius = max(1, width // corner_ratio)

    # --- Apply operations ---
    image.undo_group_start()

    # 1. Ensure alpha channel
    run_proc("gimp-layer-add-alpha", layer=drawable)

    # 2. Add a white layer mask
    proc = Gimp.get_pdb().lookup_procedure("gimp-layer-create-mask")
    mask_cfg = proc.create_config()
    mask_cfg.set_property("layer", drawable)
    mask_cfg.set_property("mask-type", Gimp.AddMaskType.WHITE)
    result = proc.run(mask_cfg)
    mask = result.index(1)
    run_proc("gimp-layer-add-mask", layer=drawable, mask=mask)

    # 3. Fill mask with current selection if any
    if not run_proc("gimp-selection-is-empty", image=image).index(1):
        run_proc("gimp-drawable-edit-fill",
                 drawable=mask,
                 fill_type=Gimp.FillType.FOREGROUND)

    # 4. Apply mask to the layer
    run_proc("gimp-layer-remove-mask", layer=drawable, mode=0)  # 0 = apply

    # 5. Rounded rectangle selection
    proc = Gimp.get_pdb().lookup_procedure("gimp-image-select-round-rectangle")
    sel_cfg = proc.create_config()
    sel_cfg.set_property("image", image)
    sel_cfg.set_property("operation", Gimp.ChannelOps.REPLACE)
    sel_cfg.set_property("x", 0)
    sel_cfg.set_property("y", 0)
    sel_cfg.set_property("width", width)
    sel_cfg.set_property("height", width)
    sel_cfg.set_property("corner-radius-x", radius)
    sel_cfg.set_property("corner-radius-y", radius)
    proc.run(sel_cfg)

    # 6. Clear outside
    run_proc("gimp-selection-invert", image=image)
    run_proc("gimp-drawable-edit-clear", drawable=drawable)

    # 7. Scale to icon size
    run_proc("gimp-image-scale", image=image,
             new_width=icon_size, new_height=icon_size)

    image.undo_group_end()
    Gimp.displays_flush()

    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)


class RoundedIcon(Gimp.PlugIn):
    def do_query_procedures(self):
        return ["python-fu-rounded-icon"]

    def do_create_procedure(self, name):
        if name == "python-fu-rounded-icon":
            procedure = Gimp.ImageProcedure.new(
                self, name, Gimp.PDBProcType.PLUGIN,
                rounded_icon_run, None
            )
            procedure.set_image_types("*")
            procedure.set_sensitivity_mask(Gimp.ProcedureSensitivityMask.DRAWABLE)
            procedure.set_menu_label("Rounded Iconify")
            procedure.add_menu_path("<Image>/Python-Fu")
            procedure.set_attribution("Aki Kareha", "Kareha Lab", "2025")
            procedure.set_documentation(
                "Make a rounded-corner square icon",
                "Adds alpha, applies mask, rounds corners, "
                "clears outside and scales to icon size.",
                None
            )

            # --- Arguments (dialog inputs) ---
            procedure.add_int_argument(
                "corner-ratio",
                "Corner Ratio",
                "Corner radius as divisor of width (e.g. 6 = width/6)",
                1, 50, 6,
                GObject.ParamFlags.READWRITE
            )
            procedure.add_int_argument(
                "icon-size",
                "Icon Size",
                "Final square icon size (px)",
                16, 2048, 128,
                GObject.ParamFlags.READWRITE
            )

            return procedure


Gimp.main(RoundedIcon.__gtype__, sys.argv)
