from entity import Molecule, Bond
from util.index_from import index_from


def get_molecule_chiral_carbons(mol: Molecule) -> set:
    ret = set()
    for i in range(1, mol.atom_count() + 1):
        if is_chiral_carbon(mol, i):
            ret.add(i)
    return ret


@index_from(1)
def is_chiral_carbon(mol, index):
    atom = mol.get_atom(index)
    if atom.element != "C":
        return False

    bonds = mol.get_atom_declared_bonds(index)
    for b in bonds:
        if b.type > 1:  # 不是单键
            return False

    hcnt = atom.hydrogen_count
    bondnh = []

    for b in bonds:
        if b.from_atom == index:
            another = b.to
        else:
            another = b.from_atom

        if mol.get_atom(another).element == "H" and len(mol.get_atom_declared_bonds(another)) == 1:
            hcnt += 1
            continue
        bondnh.append(b)

    if len(bondnh) == 4 and hcnt == 0:
        b1, b2, b3, b4 = [mol.get_bond_id(b) for b in bondnh]
        return not (compare_chain(mol, index, b1, b2) or
                    compare_chain(mol, index, b1, b3) or
                    compare_chain(mol, index, b1, b4) or
                    compare_chain(mol, index, b2, b3) or
                    compare_chain(mol, index, b2, b4) or
                    compare_chain(mol, index, b3, b4))
    elif len(bondnh) == 3 and hcnt == 1:
        b1, b2, b3 = [mol.get_bond_id(b) for b in bondnh]
        return not (compare_chain(mol, index, b1, b2) or
                    compare_chain(mol, index, b1, b3) or
                    compare_chain(mol, index, b2, b3))
    else:
        return False


@index_from(1)
def compare_chain(mol, center, chain1, chain2):
    return compare_chain_recursive(mol, center, center, chain1, chain2,
                                   3 + int(mol.atom_count() ** 0.5))


@index_from(1)
def compare_chain_recursive(mol: Molecule, atom1: int, atom2: int, chain1: Bond, chain2: Bond, ttl: int):
    b1 = mol.get_bond(chain1)
    b2 = mol.get_bond(chain2)
    if b1.type != b2.type:
        return False

    another1 = b1.to if b1.from_atom == atom1 else b1.from_atom
    another2 = b2.to if b2.from_atom == atom2 else b2.from_atom
    a1 = mol.get_atom(another1)
    a2 = mol.get_atom(another2)
    if a1.element != a2.element:
        return False
    hcnt1 = a1.hydrogen_count
    hcnt2 = a2.hydrogen_count
    bonds1 = mol.get_atom_declared_bonds(another1)
    bonds2 = mol.get_atom_declared_bonds(another2)
    bondnh1 = []
    bondnh2 = []

    bonds_pairs = [(bonds1, another1), (bonds2, another2)]
    atoms_to_avoid = [atom1, atom2]

    for bonds, another in bonds_pairs:
        hcnt = 0
        bondnh = []
        for b in bonds:
            other_atom_index = b.to if b.from_atom == another else b.from_atom
            if other_atom_index == atoms_to_avoid[bonds_pairs.index((bonds, another))]:
                continue
            atom = mol.get_atom(other_atom_index)
            if atom.element == "H" and len(mol.get_atom_declared_bonds(other_atom_index)) == 1:
                hcnt += 1
            else:
                bondnh.append(b)

        if bonds == bonds1:
            hcnt1 = hcnt
            bondnh1 = bondnh
        else:
            hcnt2 = hcnt
            bondnh2 = bondnh

    if hcnt1 != hcnt2 or len(bondnh1) != len(bondnh2):
        return False
    if ttl < 0:
        return False
    ttl -= 1
    for dchain1 in bondnh1:
        success = False
        for bond in bondnh2:
            if compare_chain_recursive(mol, another1, another2, mol.get_bond_id(dchain1),
                                       mol.get_bond_id(bond), ttl):
                success = True
                break
        if not success:
            return False

    return True
