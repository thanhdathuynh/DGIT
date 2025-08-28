GENE_MAPPING = {
    "SLC6A4": ["Solute Carrier Family 6 Member 4", "SERT"],
    "BDNF": ["Brain-Derived Neurotrophic Factor"],
    "HTR2A": ["5-Hydroxytryptamine Receptor 2A", "Serotonin Receptor 2A"],
    "COMT": ["Catechol-O-Methyltransferase"],
    "TPH2": ["Tryptophan Hydroxylase 2"]
}

def map_to_symbol(query):
    """Return the gene symbol for a given alias or symbol."""
    query_lower = query.lower().strip()
    for symbol, aliases in GENE_MAPPING.items():
        if query_lower == symbol.lower():
            return symbol
        if query_lower in [a.lower() for a in aliases]:
            return symbol
    return None
