from entity import Atom, Bond
from entity import Molecule

"""
Utility class for parsing MDL MOL files.
Adapted from WebMolKit(https://github.com/aclarkxyz/web_molkit)
"""


class BadMolFormatException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class MdlMolParser:
    @staticmethod
    def parse_string(str_input) -> Molecule:
        """
        将mol字符串解析为Molecule对象
        """

        start = -1
        lines = str_input.replace("\r\n", "\n").replace('\r', '\n').split("\n")
        for i, line in enumerate(lines):
            if len(line) >= 39 and line.startswith("V2000", 34):
                start = i
                break
        if start == -1:
            raise BadMolFormatException("V2000 tag not found at any_line.substring(34, 39)")

        cid = int(lines[0]) if lines[0].isdigit() else 0
        num_atoms = int(lines[start][:3].strip())
        num_bonds = int(lines[start][3:6].strip())

        atoms = [Atom() for _ in range(num_atoms)]
        bonds = [Bond() for _ in range(num_bonds)]

        for i in range(num_atoms):
            atom = atoms[i]
            line = lines[start + 1 + i]
            if len(line) < 39:
                raise BadMolFormatException(f"Invalid MDL MOL: atom line{start + 2 + i}")

            atom.x = float(line[:10].strip())
            atom.y = float(line[10:20].strip())
            atom.z = float(line[20:30].strip())
            atom.element = line[31:34].strip()

            chg2 = int(line[36:39].strip())
            mapnum = int(line[60:63].strip()) if len(line) >= 63 else 0
            rad = 0

            if 1 <= chg2 <= 3:
                chg = 4 - chg2
            elif chg2 == 4:
                chg = 0
                rad = 2
            elif chg2 < 5 or chg2 > 7:
                chg = 0
            else:
                chg = 4 - chg2

            atom.charge = chg
            atom.unpaired = rad
            atom.mapnum = mapnum

        for i in range(num_bonds):
            bond = bonds[i]
            line = lines[start + num_atoms + 1 + i]
            if len(line) < 12:
                raise BadMolFormatException(f"Invalid MDL MOL: bond line{start + num_atoms + 2 + i}")

            from_atom = int(line[:3].strip())
            to = int(line[3:6].strip())
            type = int(line[6:9].strip())
            stereo = int(line[9:12].strip())

            if from_atom == to or from_atom < 1 or from_atom > num_atoms or to < 1 or to > num_atoms:
                raise BadMolFormatException(f"Invalid MDL MOL: bond line{start + num_atoms + 2 + i}")

            order = 1 if type < 1 or type > 3 else type
            style = 0
            if stereo == 1:
                style = 1
            elif stereo == 6:
                style = 2

            bond.from_atom = from_atom
            bond.to = to
            bond.type = order
            bond.stereo_direction = style

        molecule = Molecule(cid, atoms, bonds, str_input)
        for i in range(start + num_atoms + num_bonds + 1, len(lines)):
            line = lines[i]
            if line.startswith("M  END"):
                break

            if line.startswith("M  CHG"):
                type2 = 1
            elif line.startswith("M  RAD"):
                type2 = 2
            elif line.startswith("M  ISO"):
                type2 = 3
            elif line.startswith("M  RGP"):
                type2 = 4
            elif line.startswith("M  HYD"):
                type2 = 5
            elif line.startswith("M  ZCH"):
                type2 = 6
            elif not line.startswith("M  ZBO"):
                anum = int(line[3:6].strip()) if len(line) >= 6 else 0
                if line.startswith("A  ") and len(line) >= 6 and 1 <= anum <= num_atoms:
                    line5 = lines[i + 1]
                    if line5 is None:
                        break
                    molecule.get_atom(anum).element = line5
            else:
                type2 = 7

            if type2 > 0:
                try:
                    len_values = int(line[6:9].strip())
                    for n3 in range(len_values):
                        pos = int(line[(n3 * 8) + 9:(n3 * 8) + 13].strip())
                        val = int(line[(n3 * 8) + 13:(n3 * 8) + 17].strip())
                        if pos < 1:
                            raise BadMolFormatException("Invalid MDL MOL: M-block")

                        if type2 == 1:
                            molecule.get_atom(pos).charge = val
                        elif type2 == 2:
                            molecule.get_atom(pos).unpaired = val
                        elif type2 == 3:
                            molecule.get_atom(pos).isotope = val
                        elif type2 == 4:
                            molecule.get_atom(pos).element = f"R{val}"
                        elif type2 == 5:
                            molecule.get_atom(pos).show_flag = Molecule.SHOW_FLAG_EXPLICIT
                        elif type2 == 6:
                            molecule.get_atom(pos).charge = val
                        elif type2 == 7:
                            molecule.get_bond(pos).stereo_direction = val
                except IndexError:
                    raise BadMolFormatException("Invalid MDL MOL: M-block")

        molecule.init_once()
        return molecule

