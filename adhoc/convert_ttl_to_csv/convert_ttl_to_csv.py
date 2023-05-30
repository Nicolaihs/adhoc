import csv
import click
import logging
import os
import pickle
from rdflib import Graph, Namespace, Literal, BNode
from tqdm import tqdm

# Define the RDF namespaces
rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
skos = Namespace("http://www.w3.org/2004/02/skos/core#")
lexinfo = lexinfo = Namespace("http://www.lexinfo.net/ontology/3.0/lexinfo#")
ontolex = Namespace("http://www.w3.org/ns/lemon/ontolex#")
dn = Namespace("https://wordnet.dk/dannet/data/")
dns = Namespace("https://wordnet.dk/dannet/schema/")
wn = Namespace("https://globalwordnet.github.io/schemas/wn#")


def load_graph_from_pickle(pickle_file):
    with open(pickle_file, "rb") as file:
        return pickle.load(file)


def save_graph_to_pickle(graph, pickle_file):
    with open(pickle_file, "wb") as file:
        pickle.dump(graph, file)


def get_ontological_type(graph, ontological_type):
    # Assuming `ontological_type` is the value of the dns:ontologicalType property
    if not ontological_type:
        return ""
    bnode_values = []
    bnodes = graph.objects(ontological_type, None)
    for i, bnode in enumerate(bnodes):
        value = str(bnode.strip()).split("/")[-1]
        bnode_values.append(value)

        if i >= 10:
            import ipdb

            ipdb.set_trace()
    if bnode_values:
        bnode_values = bnode_values[1:]
    return "+".join(bnode_values)


def get_word_uris_from_sense_uri(graph, sense_uri):
    word_uris = []
    for word_triple in graph.triples((None, ontolex.sense, sense_uri)):
        word_uris.append(word_triple[0])
    return word_uris


def get_synset_uris_from_sense_uri(graph, sense_uri):
    synset_uris = []
    for synset_triple in graph.triples((None, ontolex.lexicalizedSense, sense_uri)):
        synset_uris.append(synset_triple[0])
    return synset_uris


def create_synset_file(graph, csv_file):
    # Count the number of synsets
    synset_count = len(list(graph.triples((None, rdf.type, ontolex.LexicalConcept))))

    # Log and display the number of synsets
    logging.info(f"Number of synsets: {synset_count}")

    # Open the CSV file for writing
    with open(csv_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Write the CSV header
        writer.writerow(["synset_id", "definition", "ontological_type"])

        # Iterate over all triples in the graph with progress bar
        with tqdm(total=synset_count, desc="Exporting") as pbar:
            for synset_uri, _, _ in graph.triples(
                (None, rdf.type, ontolex.LexicalConcept)
            ):
                synset_id = str(synset_uri.strip()).split("/")[-1]
                # Get the definition
                definition = graph.value(synset_uri, skos.definition)

                # Get the ontological type
                ontological_type_uri = graph.value(synset_uri, dns.ontologicalType)
                ontological_type = get_ontological_type(graph, ontological_type_uri)
                # Write the row to the CSV file
                writer.writerow([synset_id, definition, ontological_type])

                # Update the progress bar
                pbar.update(1)


def create_word_file(graph, csv_file):
    # Count the number of synsets
    word_count = len(list(graph.triples((None, rdf.type, ontolex.Word))))

    # Log and display the number of synsets
    logging.info(f"Number of words: {word_count}")

    # Open the CSV file for writing
    with open(csv_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Write the CSV header
        writer.writerow(["word_id", "word", "pos", "type", "source"])

        # Iterate over all triples in the graph with progress bar
        with tqdm(total=word_count, desc="Exporting") as pbar:
            for word_uri, _, _ in graph.triples((None, rdf.type, ontolex.Word)):
                word_id = str(word_uri.strip()).split("/")[-1]
                source_uri = graph.value(word_uri, dns.source) or ""
                # Get the definition
                written_form = graph.value(
                    word_uri, ontolex.canonicalForm / ontolex.writtenRep
                )

                # Get the part of speech
                part_of_speech = graph.value(word_uri, lexinfo.partOfSpeech)
                if part_of_speech:
                    part_of_speech = str(part_of_speech.strip()).split("#")[-1]

                # Write the row to the CSV file
                writer.writerow(
                    [word_id, written_form, part_of_speech, "Word", source_uri.strip()]
                )

                # Update the progress bar
                pbar.update(1)


def create_sense_file(graph, csv_file):
    # Count the number of synsets
    sense_count = len(list(graph.triples((None, rdf.type, ontolex.LexicalSense))))
    logging.info(f"Number of senses: {sense_count}")

    # Open the CSV file for writing
    with open(csv_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Write the CSV header
        writer.writerow(["sense_id", "word_id", "synset_id", "source", "example"])

        # Iterate over all triples in the graph with progress bar
        with tqdm(total=sense_count, desc="Exporting") as pbar:
            for sense_uri, _, _ in graph.triples(
                (None, rdf.type, ontolex.LexicalSense)
            ):
                sense_id = str(sense_uri.strip()).split("/")[-1]
                source_uri = graph.value(sense_uri, dns.source)
                example_uri = graph.value(sense_uri, lexinfo.senseExample)
                if example_uri is not None:
                    print(example_uri)
                word_uris = get_word_uris_from_sense_uri(graph, sense_uri)
                synset_uris = get_synset_uris_from_sense_uri(graph, sense_uri)
                for word_uri in word_uris:
                    word_id = str(word_uri.strip()).split("/")[-1]
                    for synset_uri in synset_uris:
                        synset_id = str(synset_uri.strip()).split("/")[-1]
                        writer.writerow(
                            [
                                sense_id,
                                word_id,
                                synset_id,
                                source_uri is not None and source_uri.strip() or "",
                                example_uri is not None and example_uri.strip() or "",
                            ]
                        )

                # Update the progress bar
                pbar.update(1)


def get_relations(graph, uri, writer):
    """Return the relations for the given URI."""
    desired_namespaces = [wn, dns]
    for subj, pred, obj in graph.triples((uri, None, None)):
        all_ok = False
        for desired_namespace in desired_namespaces:
            if pred.startswith(desired_namespace):
                all_ok = True
                break

        # Not ok if pred ends with "OnlogicalType"
        if all_ok and pred.endswith("ontologicalType"):
            all_ok = False
        if not all_ok:
            continue

        print(subj, obj, pred)
        if pred.endswith("inherited"):
            pass
            # TODO: How do we match the inherited info to the specific relation, see e.g. inherit-11088-mero_member
        else:
            writer.writerow(
                [
                    str(subj.strip()).split("/")[-1],
                    str(pred.strip()).split("/")[-1],
                    str(obj.strip()).split("/")[-1],
                ]
            )


def create_relation_file(graph, csv_file):
    # Count the number of relations
    synset_count = len(list(graph.triples((None, rdf.type, ontolex.LexicalConcept))))
    logging.info(f"Number of senses: {synset_count}")

    # Open the CSV file for writing
    with open(csv_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Write the CSV header
        writer.writerow(["source", "relation", "target"])

        # Iterate over all triples in the graph with progress bar
        with tqdm(total=synset_count, desc="Exporting") as pbar:
            for synset_uri, _, _ in graph.triples(
                (None, rdf.type, ontolex.LexicalConcept)
            ):
                get_relations(graph, synset_uri, writer)
                # Update the progress bar
                pbar.update(1)


@click.command()
@click.argument("rdf_file", type=click.Path(exists=True))
@click.option("--use-pickle", is_flag=True, help="Use pickled RDF file if available")
def export_synsets_to_csv(rdf_file, use_pickle):
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    # Check if pickled RDF file exists and use it if available
    pickle_file = rdf_file + ".pickle"
    if use_pickle and os.path.exists(pickle_file):
        logging.info("Loading pickled RDF file...")
        graph = load_graph_from_pickle(pickle_file)
    else:
        # Create an RDF graph
        graph = Graph()

        # Log and display the file size
        logging.info(f"Loading RDF file: {rdf_file}")

        # Load the file with progress bar
        graph.parse(rdf_file, format="turtle")

        # Save the parsed RDF graph to a pickle file
        logging.info("Saving pickled RDF file...")
        save_graph_to_pickle(graph, pickle_file)

    create_synset_file(graph, "synsets.csv")
    create_word_file(graph, "words.csv")
    create_sense_file(graph, "senses.csv")
    create_relation_file(graph, "relations.csv")

    click.echo("CSV export completed successfully.")

    import ipdb

    ipdb.set_trace()


if __name__ == "__main__":
    export_synsets_to_csv()
