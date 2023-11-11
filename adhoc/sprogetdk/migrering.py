import click
import json
import logging
import os
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def find_matching_files(input_path, content_path, content_type, output_file):
    referenced_images = []
    articles_with_no_images = []
    no_of_pages = 0
    with open(output_file, "w") as out_file:
        for root, dirs, files in os.walk(input_path):
            logger.info(f"Searching in {root}")
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    with open(file_path) as f:
                        data = json.load(f)
                        if not data.get("_type") == content_type:
                            continue
                        if data.get("_path", "").startswith(content_path):
                            body = data.get("text", "")
                            # Get all images sources in body using regex
                            images = re.findall(r'<img.*?src="(.+?)".*?>', body)
                            if images:
                                referenced_images += images

                            publication_date = data.get("effectiveDate") or data.get(
                                "creation_date"
                            )
                            item = {
                                "id": data.get("id"),
                                "uid": data.get("_uid"),
                                "text": data.get("text"),
                                "path": data.get("_path"),
                                "title": data.get("title"),
                                "creators": data.get("creators"),
                                "publication_date": publication_date,
                                "creation_date": data.get("creation_date"),
                                "modification_date": data.get("modification_date"),
                                "type": data.get("_type"),
                                "description": data.get("description"),
                                "categories": data.get("categories"),
                            }

                            if data.get("effective_date"):
                                item["effective_date"] = data.get("effective_date")
                            if data.get("effectiveDate"):
                                item["effective_date"] = data.get("effectiveDate")
                            if data.get("_datafield_image"):
                                item["datafield_image"] = data.get("_datafield_image")

                            if None in item.values():
                                logger.warning(
                                    f"None value found in item: path: {file_path}, title: {data.get('title')}"
                                )

                            if not images and not item.get("datafield_image"):
                                articles_with_no_images.append(item)

                            json.dump(
                                item,
                                out_file,
                            )
                            out_file.write("\n")
                            no_of_pages += 1

    logger.info(f"Found {len(referenced_images)} referenced images")
    logger.info(f"Found {len(articles_with_no_images)} articles with no images")
    logger.info(f"Found {no_of_pages} pages")


@click.command()
@click.option("--input-path", required=True)
@click.option("--content-path", required=True)
@click.option("--content-type", required=True)
@click.option("--output-file", required=True)
def main(input_path, content_path, content_type, output_file):
    find_matching_files(input_path, content_path, content_type, output_file)


if __name__ == "__main__":
    main()
