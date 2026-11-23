from lxml import etree

tree = etree.parse("/Users/princessatosi/Desktop/fuel-prices-platform/data/bronze/date=2026-11-20/PrixCarburants_instantane.xml")
root = tree.getroot()

# Keep the original XML structure
sample_root = etree.Element(root.tag, attrib=root.attrib)

for element in list(root)[:20]:
    sample_root.append(element)

tree_sample = etree.ElementTree(sample_root)
tree_sample.write(
    "sample.xml",
    encoding="utf-8",
    xml_declaration=True,
    pretty_print=True
)