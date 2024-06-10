import argparse
from dataclasses import dataclass
from math import floor
from pathlib import Path

import qrcode

from solid2 import cube, cylinder, hull, text, set_global_fn, union


@dataclass
class Args:
    start_index: int = 1
    end_index: int = 1
    output_dir: Path = Path("output")
    token_width: float = 50.0
    token_height: float = 60.0
    token_depth: float = 3.0
    token_corner_radius: float = 4.0
    token_fillet_radius: float = 1.0
    qr_border: float = 3.0
    colored_print_depth: float = 0.6
    text_font: str = "Helvetica"
    text_size: float = 7.0
    text_border: float = 3.0
    hole_radius: float = 3.0
    hole_offset: float = 3.0
    build_plate_width: float = 254.0
    build_plate_height: float = 254.0
    build_plate_spacing: float = 1.0


def qr_code_to_3d_model(data: str, qr_width: int, depth: float) -> cube:
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, version=1, border=0)
    qr.add_data(data)
    # noinspection PyArgumentEqualDefault
    qr.make()
    matrix = qr.get_matrix()
    num_cells = len(matrix)

    pixel_size = qr_width / num_cells

    model = union()
    for y, row in enumerate(matrix):
        for x, cell in enumerate(row):
            if cell:
                model += cube(pixel_size, pixel_size, depth).right(x * pixel_size).forward(y * pixel_size)

    return model.color("black")


def create_keychain_body(
    width: float,
    height: float,
    depth: float,
    radius: float,
    hole_radius: float,
    hole_offset: float,
):
    main_core = cube([width - 2 * radius, height - 2 * radius, depth]).right(radius).forward(radius)
    corner_cylinder = cylinder(r=radius, h=depth)

    corners = [
        corner_cylinder.right(radius).forward(radius),
        corner_cylinder.right(width - radius).forward(radius),
        corner_cylinder.right(width - radius).forward(height - radius),
        corner_cylinder.right(radius).forward(height - radius),
    ]

    rounded_edges = [
        hull()(corners[0], corners[1]),
        hull()(corners[1], corners[2]),
        hull()(corners[2], corners[3]),
        hull()(corners[3], corners[0]),
    ]

    combined_shape = main_core
    for shape in rounded_edges:
        combined_shape += shape

    keychain_hole = (
        cylinder(r=hole_radius, h=depth + 2)
        .right(width - hole_offset - hole_radius)
        .forward(height - hole_offset - (hole_radius * 2))
        .back(-1)
    )
    combined_shape -= keychain_hole

    return combined_shape.color("white")


def add_text(data: str, size: float, depth):
    return (
        text(data, size=size, halign="center", valign="top", font="Helvetica")
        .linear_extrude(height=depth)
        .color("black")
    )


def parse_args() -> Args:
    parser = argparse.ArgumentParser(description="Create keychain models")
    parser.add_argument("--start-index", type=int, default=Args.start_index, help="Starting index for keychain tags")
    parser.add_argument("--end-index", type=int, default=Args.end_index, help="Ending index for keychain tags")
    parser.add_argument("--output-dir", type=Path, default=Args.output_dir, help="Output directory for 3mf files")
    parser.add_argument("--token-width", type=float, default=Args.token_width, help="Width of the keychain token")
    parser.add_argument("--token-height", type=float, default=Args.token_height, help="Height of the keychain token")
    parser.add_argument("--token-depth", type=float, default=Args.token_depth, help="Depth of the keychain token")
    parser.add_argument(
        "--token-corner-radius",
        type=float,
        default=Args.token_corner_radius,
        help="Corner radius of the keychain token",
    )
    parser.add_argument(
        "--token-fillet-radius", type=float, default=Args.token_fillet_radius, help="Filet radius of the keychain token"
    )
    parser.add_argument("--qr-border", type=float, default=Args.qr_border, help="Border width around the QR code")
    parser.add_argument(
        "--colored-print-depth", type=float, default=Args.colored_print_depth, help="Depth of colored print"
    )
    parser.add_argument("--text-font", type=str, default=Args.text_font, help="Font for the text")
    parser.add_argument("--text-size", type=float, default=Args.text_size, help="Size of the text")
    parser.add_argument("--text-border", type=float, default=Args.text_border, help="Border around the text")
    parser.add_argument("--hole-radius", type=float, default=Args.hole_radius, help="Radius of the keychain hole")
    parser.add_argument("--hole-offset", type=float, default=Args.hole_offset, help="Offset of the keychain hole")
    return Args(**vars(parser.parse_args()))


def prepare_output_directory(output_dir: Path) -> None:
    for file in output_dir.glob("*"):
        file.unlink()
    output_dir.mkdir(parents=True, exist_ok=True)


def main() -> None:
    args = parse_args()
    prepare_output_directory(args.output_dir)
    set_global_fn(100)

    num_per_row = int(args.build_plate_width / (args.token_width + args.build_plate_spacing))
    num_per_column = int(args.build_plate_height / (args.token_height + args.build_plate_spacing))
    tokens_per_plate = num_per_row * num_per_column

    current_plate_index = 0
    build_plate_body = union()
    build_plate_colored = union()
    for i in range(args.start_index, args.end_index + 1):
        if (i - args.start_index) % tokens_per_plate == 0:
            if current_plate_index > 0:
                build_plate_body.save_as_stl(args.output_dir / f"build_plate_body_{current_plate_index}.stl")
                build_plate_colored.save_as_stl(args.output_dir / f"build_plate_colored_{current_plate_index}.stl")

            build_plate_body = union()
            build_plate_colored = union()
            current_plate_index += 1

        tag_text = f"T-{i}"
        qr_model = qr_code_to_3d_model(
            tag_text, qr_width=floor(args.token_width - (args.qr_border * 2)), depth=args.colored_print_depth
        )
        text_model = add_text(tag_text, args.text_size, args.colored_print_depth)

        position_index = (i - args.start_index) % tokens_per_plate
        row = position_index // num_per_row
        col = position_index % num_per_row
        x_offset = col * (args.token_width + args.build_plate_spacing)
        y_offset = row * (args.token_height + args.build_plate_spacing)

        colored = assemble_colored_components(
            qr_model, text_model, args, (args.token_width - args.hole_radius - args.text_border) / 2
        )
        body = create_keychain_body(
            args.token_width,
            args.token_height,
            args.token_depth - 0.00001,
            args.token_corner_radius,
            args.hole_radius,
            args.hole_offset,
        )
        body -= colored

        positioned_body = body.translate([x_offset, y_offset, 0])
        positioned_colored = colored.translate([x_offset, y_offset, 0])

        build_plate_body += positioned_body
        build_plate_colored += positioned_colored

    if current_plate_index > 0:
        build_plate_body.save_as_stl(args.output_dir / f"build_plate_body_{current_plate_index}.stl")
        build_plate_colored.save_as_stl(args.output_dir / f"build_plate_colored_{current_plate_index}.stl")

    for file in args.output_dir.glob("*.scad"):
        file.unlink()


def assemble_colored_components(qr_model: cube, text_model: union, args: Args, text_offset: float) -> union:
    front_colored = qr_model.right(args.qr_border).forward(args.qr_border).up(
        args.token_depth - args.colored_print_depth
    ) + text_model.right(text_offset).forward(args.token_height - args.text_border).up(
        args.token_depth - args.colored_print_depth
    )

    back_colored = (
        qr_model.left(args.token_width - args.qr_border).forward(args.qr_border).mirrorX()
        + text_model.left(text_offset).forward(args.token_height - args.text_border).mirrorX()
    )

    return front_colored + back_colored


def save_models(body: union, colored: union, index: int, output_dir: Path) -> None:
    body -= colored
    body.save_as_stl(output_dir / f"keychain_{index}.stl")
    colored.save_as_stl(output_dir / f"keychain_{index}_colored.stl")


if __name__ == "__main__":
    main()
