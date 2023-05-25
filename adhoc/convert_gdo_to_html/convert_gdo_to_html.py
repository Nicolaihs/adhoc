import click
from lxml import etree
from tools3.xmlutilities import objectify, stringify

@click.command()
@click.option('--input-file', type=str)
@click.option('--output-file', type=str)
@click.option('--xslt-file', type=click.File('r'))
@click.option('--css-file', type=click.File('r'))
@click.option('--root-tag-name', type=str, default='Artikel')
def main(input_file, output_file, xslt_file, css_file, root_tag_name):
    # Load xslt file
    xslt_tree = etree.parse(xslt_file)
    transformator = etree.XSLT(xslt_tree)

    # Load css file
    css = css_file.read()

    content = ''
    with open(input_file, 'r') as f:
        for line in f:
            if line[:len(root_tag_name)+1] != f'<{root_tag_name}':
                continue
            xml = objectify(line)
            transformed = transformator(xml)
            content += stringify(transformed)
            content += '\n<hr>\n'


    with open(output_file, 'w') as f:
        f.write(f'<html><head><meta http-equiv="content-type" content="text-html; charset=utf-8"><style>{css}</style></head><body>{content}</body></html>')


if '__main__' == __name__:
    main()