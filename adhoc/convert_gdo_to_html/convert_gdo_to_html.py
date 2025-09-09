import argparse
from lxml import etree


# Copied from tools3
def stringify(tree, pretty_print=False):
    """Return xml tree as string."""
    return etree.tostring(tree, pretty_print=pretty_print, encoding="unicode")


# Copied from tools3
def objectify(text, verbose=True):
    """Return text as an xml object"""
    try:
        xml = etree.fromstring(text.encode("utf8"))
    except etree.ParseError as err:
        if verbose:
            sys.stderr.write("%s\n" % text)
            sys.stderr.write("----\n%s\n----\n" % err.msg)
        #            import ipdb; ipdb.set_trace()
        raise
        sys.exit()
    return xml


def main(input_file, output_file, xslt_file, css_file, root_tag_name):
    # Load xslt file
    xslt_tree = etree.parse(xslt_file)
    transformator = etree.XSLT(xslt_tree)

    # Load css file
    css = css_file.read()

    content = ""
    with open(input_file, "r") as f:
        for line in f:
            if line[: len(root_tag_name) + 1] != f"<{root_tag_name}":
                continue
            xml = objectify(line)
            transformed = transformator(xml)
            content += stringify(transformed)
            content += "\n<hr>\n"

    with open(output_file, "w") as f:
        f.write(
            f'<html><head><meta http-equiv="content-type" content="text-html; charset=utf-8"><style>{css}</style></head><body>{content}</body></html>'
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert GDO XML to HTML using XSLT and CSS."
    )
    parser.add_argument("--input-file", type=str, required=True, help="Input XML file")
    parser.add_argument(
        "--output-file", type=str, required=True, help="Output HTML file"
    )
    parser.add_argument(
        "--xslt-file", type=argparse.FileType("r"), required=True, help="XSLT file"
    )
    parser.add_argument(
        "--css-file", type=argparse.FileType("r"), required=True, help="CSS file"
    )
    parser.add_argument(
        "--root-tag-name",
        type=str,
        default="Artikel",
        help="Root tag name to filter XML lines",
    )

    args = parser.parse_args()
    main(
        args.input_file,
        args.output_file,
        args.xslt_file,
        args.css_file,
        args.root_tag_name,
    )
